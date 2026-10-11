"""Leave-one-source-out audit of the rf_v11 contract (69 features).

For every source S with >= MIN_ROWS rows in train+val:
  - LOSO model: RandomForest fit on train rows whose _source != S.
    Evaluated on all S rows in train+val (none of them seen in training).
  - Baseline: production rf.onnx (trained on all of train) evaluated on
    the S rows in val only (the only held-out rows for that model).
  - Also the LOSO model on S rows in val only, so the difference against
    the baseline is computed on identical rows.

test.parquet is never opened.
"""
import json
import re
import subprocess
import time
from collections import Counter
from pathlib import Path

import numpy as np
import onnxruntime as ort
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

REPO = Path("/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian")
SPLITS = REPO / "training" / "splits"
RF_ONNX = REPO / "training" / "models" / "rf.onnx"
LOSO_REFERENCE = REPO / "training" / "models" / "loso_results.json"
OUT = Path("/tmp/lsg-audit/v4")
CODE_REF = "develop"
EXTRACTOR_PATH = "packages/extractor/src/index.ts"

CLASSES = ["benign", "cmdi", "path_traversal", "sqli", "xss"]
BENIGN_IDX = CLASSES.index("benign")
BLOCK_THRESHOLD = 0.35
MIN_ROWS = 30
META_COLS = ["sample_id", "label", "timestamp", "_source", "_row_hash"]
WORKER_EXCLUDED = {
    "status_code", "req_count_1s", "req_count_5s", "req_count_60s",
    "error_rate_4xx_60s", "endpoint_diversity_60s", "non_json_quote_count",
}
RF_PARAMS = dict(
    n_estimators=30, max_depth=25, class_weight="balanced_subsample",
    random_state=42, n_jobs=-1,
)
EXPECTED_FEATURES = 69


def git_show(ref_path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), "show", f"{CODE_REF}:{ref_path}"],
        check=True, capture_output=True, text=True,
    ).stdout


def load_feature_contract() -> list[str]:
    source = git_show(EXTRACTOR_PATH)
    block = re.search(r"FEATURE_NAMES: readonly string\[\] = \[(.*?)\];", source, re.S).group(1)
    all_names = re.findall(r'"([a-z0-9_]+)"', block)
    contract = [n for n in all_names if n not in WORKER_EXCLUDED]
    assert len(all_names) == 76, len(all_names)
    assert len(contract) == EXPECTED_FEATURES, len(contract)
    return contract


def load_frames(contract: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    columns = META_COLS + contract
    train = pd.read_parquet(SPLITS / "train.parquet", columns=columns)
    val = pd.read_parquet(SPLITS / "val.parquet", columns=columns)
    for name, frame in (("train", train), ("val", val)):
        assert "_source" in frame.columns, f"{name} lacks _source"
        assert frame[contract].isna().sum().sum() == 0, f"{name} has NaN features"
    return train, val


def to_full_probs(model: RandomForestClassifier, X: np.ndarray) -> np.ndarray:
    raw = model.predict_proba(X)
    full = np.zeros((X.shape[0], len(CLASSES)), dtype=np.float64)
    for col, cls in enumerate(model.classes_):
        full[:, CLASSES.index(cls)] = raw[:, col]
    return full


def block_mask(probs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    argmax = probs.argmax(axis=1)
    confidence = probs.max(axis=1)
    return argmax, (argmax != BENIGN_IDX) & (confidence >= BLOCK_THRESHOLD)


def metrics_for(labels: np.ndarray, probs: np.ndarray) -> dict:
    argmax, blocked = block_mask(probs)
    truth = np.array([CLASSES.index(lbl) for lbl in labels])
    counts = Counter(labels.tolist())
    per_class_recall, per_class_block = {}, {}
    for cls in CLASSES:
        idx = CLASSES.index(cls)
        mask = truth == idx
        if mask.any():
            per_class_recall[cls] = float((argmax[mask] == idx).mean())
            per_class_block[cls] = float(blocked[mask].mean())
    attack_rows = truth != BENIGN_IDX
    benign_rows = truth == BENIGN_IDX
    present = sorted(set(truth.tolist()))
    macro_f1 = None
    if len(present) >= 2:
        macro_f1 = float(f1_score(truth, argmax, labels=present, average="macro", zero_division=0))
    return {
        "n": int(len(labels)),
        "class_counts": dict(counts),
        "recall_by_argmax": per_class_recall,
        "block_rate_by_class": per_class_block,
        "attack_block_rate": float(blocked[attack_rows].mean()) if attack_rows.any() else None,
        "benign_block_rate_fp": float(blocked[benign_rows].mean()) if benign_rows.any() else None,
        "macro_f1": macro_f1,
    }


def loso_fold(source: str, train: pd.DataFrame, full: pd.DataFrame, contract: list[str]) -> dict:
    fit_rows = train[train["_source"] != source]
    eval_rows = full[full["_source"] == source]
    started = time.perf_counter()
    model = RandomForestClassifier(**RF_PARAMS)
    model.fit(fit_rows[contract].to_numpy(dtype=np.float32), fit_rows["label"].to_numpy())
    all_probs = to_full_probs(model, eval_rows[contract].to_numpy(dtype=np.float32))
    val_mask = eval_rows["split"].to_numpy() == "val"
    elapsed = time.perf_counter() - started

    train_classes = set(fit_rows["label"].unique())
    missing = [c for c in CLASSES if c not in train_classes]
    labels = eval_rows["label"].to_numpy()
    return {
        "held_out_source": source,
        "fit_rows": int(len(fit_rows)),
        "fold_seconds": round(elapsed, 2),
        "classes_missing_in_training": missing,
        "all_train_val": metrics_for(labels, all_probs),
        "val_only": metrics_for(labels[val_mask], all_probs[val_mask]),
    }


def baseline_by_source(val: pd.DataFrame, contract: list[str]) -> dict:
    session = ort.InferenceSession(str(RF_ONNX), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    assert session.get_inputs()[0].shape[1] == EXPECTED_FEATURES
    X = val[contract].to_numpy(dtype=np.float32)
    probs = np.asarray(session.run(None, {input_name: X})[1], dtype=np.float64)
    result = {}
    for source in val["_source"].unique():
        mask = (val["_source"] == source).to_numpy()
        result[source] = metrics_for(val["label"].to_numpy()[mask], probs[mask])
    return result


def sources_to_audit(train: pd.DataFrame, val: pd.DataFrame) -> list[str]:
    combined = pd.concat([train["_source"], val["_source"]]).value_counts()
    return [src for src, n in combined.items() if n >= MIN_ROWS]


def write_partial(payload: dict, name: str) -> None:
    (OUT / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    contract = load_feature_contract()
    train, val = load_frames(contract)
    train = train.assign(split="train")
    val = val.assign(split="val")
    full = pd.concat([train, val], ignore_index=True)
    sources = sources_to_audit(train, val)

    meta = {
        "code_ref": CODE_REF,
        "code_commit": subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", CODE_REF],
            check=True, capture_output=True, text=True).stdout.strip(),
        "rf_params": RF_PARAMS,
        "block_threshold": BLOCK_THRESHOLD,
        "min_rows": MIN_ROWS,
        "n_features": len(contract),
        "feature_contract": contract,
        "train_rows": int(len(train)),
        "val_rows": int(len(val)),
        "sources": sources,
    }
    write_partial({"meta": meta, "baseline_rf_onnx": None, "loso": []}, "results_partial.json")

    baseline = baseline_by_source(val, contract)
    results = []
    for source in sources:
        fold = loso_fold(source, train, full, contract)
        fold["baseline_rf_onnx_val_only"] = baseline.get(source)
        results.append(fold)
        print(f"{source}: n={fold['all_train_val']['n']} fold={fold['fold_seconds']}s", flush=True)
        write_partial({"meta": meta, "loso": results}, "results_partial.json")

    final = {"meta": meta, "loso": results, "baseline_rf_onnx_all_val": baseline}
    (OUT / "results.json").write_text(json.dumps(final, indent=2, ensure_ascii=False))
    print("done", flush=True)


if __name__ == "__main__":
    main()
