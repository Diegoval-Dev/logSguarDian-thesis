"""Size-matched random control, Wilson 95% intervals and payload_full breakdown.

Code reference is origin/develop (dc380e3). Reuses the LOSO helpers from
loso_rf_v11.py, which read FEATURE_NAMES from CODE_REF.
test.parquet is never opened.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loso_rf_v11 as base  # noqa: E402

base.CODE_REF = "origin/develop"
OUT = Path("/tmp/lsg-audit/v4/run2")
CONTROL_SOURCES = [
    "capec", "modsec_learn", "payload_full", "payloads_csv",
    "xss_dataset", "owasp_logs", "seclists_cmdi", "command_injection",
]
CONTROL_SEEDS = [1, 2, 3, 4, 5]
WILSON_Z = 1.959964
SMALL_N = 200
MIDDLEWARE_RULE_LINES = "71p;235,238p"


def wilson(successes: int, n: int) -> dict:
    if n == 0:
        return {"k": 0, "n": 0, "p": None, "lo": None, "hi": None}
    p = successes / n
    z2 = WILSON_Z ** 2
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    half = WILSON_Z * np.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return {"k": int(successes), "n": int(n), "p": p,
            "lo": float(max(0.0, center - half)), "hi": float(min(1.0, center + half))}


def check_rule_on_code_ref() -> str:
    source = base.git_show("packages/core/src/middleware.ts").splitlines()
    assert "RF_THRESHOLD = 0.35" in source[70], source[70]
    assert "threshold = userThreshold ?? RF_THRESHOLD" in source[237], source[237]
    assert "is_attack = predicted_class !== \"benign\"" in source[234], source[234]
    return MIDDLEWARE_RULE_LINES


def class_metrics(labels: np.ndarray, probs: np.ndarray) -> dict:
    argmax, blocked = base.block_mask(probs)
    truth = np.array([base.CLASSES.index(lbl) for lbl in labels])
    attack = truth != base.BENIGN_IDX
    benign = ~attack
    recall = {}
    for cls in base.CLASSES:
        idx = base.CLASSES.index(cls)
        mask = truth == idx
        if mask.any():
            recall[cls] = wilson(int((argmax[mask] == idx).sum()), int(mask.sum()))
    return {
        "n": int(len(labels)),
        "n_attack": int(attack.sum()),
        "n_benign": int(benign.sum()),
        "block_attack": wilson(int(blocked[attack].sum()), int(attack.sum())),
        "fp_benign": wilson(int(blocked[benign].sum()), int(benign.sum())),
        "recall": recall,
    }


def fit_rf(rows: pd.DataFrame, contract: list[str]) -> RandomForestClassifier:
    model = RandomForestClassifier(**base.RF_PARAMS)
    model.fit(rows[contract].to_numpy(dtype=np.float32), rows["label"].to_numpy())
    return model


def rf_onnx_probs(frame: pd.DataFrame, contract: list[str]) -> np.ndarray:
    session = ort.InferenceSession(str(base.RF_ONNX), providers=["CPUExecutionProvider"])
    name = session.get_inputs()[0].name
    return np.asarray(session.run(None, {name: frame[contract].to_numpy(dtype=np.float32)})[1],
                      dtype=np.float64)


def control_rows(train: pd.DataFrame, n_remove: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    drop = rng.choice(len(train), size=n_remove, replace=False)
    keep = np.ones(len(train), dtype=bool)
    keep[drop] = False
    return train[keep]


def audit_source(source: str, train: pd.DataFrame, val: pd.DataFrame, full: pd.DataFrame,
                 contract: list[str], onnx_val: np.ndarray) -> dict:
    s_train = int((train["_source"] == source).sum())
    val_mask = (val["_source"] == source).to_numpy()
    val_labels = val["label"].to_numpy()[val_mask]
    result = {"source": source, "n_train": s_train, "n_val": int(val_mask.sum())}

    result["a_rf_onnx"] = class_metrics(val_labels, onnx_val[val_mask])

    seeds = {}
    if source in CONTROL_SOURCES:
        for seed in CONTROL_SEEDS:
            started = time.perf_counter()
            model = fit_rf(control_rows(train, s_train, seed), contract)
            probs = base.to_full_probs(model, val.loc[val_mask, contract].to_numpy(dtype=np.float32))
            seeds[seed] = {**class_metrics(val_labels, probs),
                           "seconds": round(time.perf_counter() - started, 2)}
    result["b_control_seeds"] = seeds

    eval_rows = full[full["_source"] == source]
    model = fit_rf(train[train["_source"] != source], contract)
    all_probs = base.to_full_probs(model, eval_rows[contract].to_numpy(dtype=np.float32))
    is_val = eval_rows["split"].to_numpy() == "val"
    result["c_loso_val"] = class_metrics(val_labels, all_probs[is_val])
    result["c_loso_all_train_val"] = class_metrics(eval_rows["label"].to_numpy(), all_probs)

    if source == "payload_full":
        result["payload_full_sqli_breakdown"] = sqli_breakdown(eval_rows, all_probs)
    return result


def sqli_breakdown(eval_rows: pd.DataFrame, probs: np.ndarray) -> dict:
    labels = eval_rows["label"].to_numpy()
    sqli_mask = labels == "sqli"
    sqli_probs = probs[sqli_mask]
    argmax, blocked = base.block_mask(sqli_probs)
    total = int(sqli_mask.sum())
    per_pred = {}
    for idx, cls in enumerate(base.CLASSES):
        predicted = argmax == idx
        count = int(predicted.sum())
        per_pred[cls] = {
            "predicted_count": count,
            "share_of_sqli": wilson(count, total),
            "blocked_given_predicted": wilson(int(blocked[predicted].sum()), count),
        }
    return {"n_sqli": total, "by_predicted_class": per_pred}


def table_row(name: str, metrics: dict) -> str:
    def cell(d):
        if d["p"] is None:
            return "—"
        return f"{d['p']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}]"
    recall = " ".join(f"{c}={cell(r)}" for c, r in metrics["recall"].items()) or "—"
    flag = " (n<200)" if metrics["n"] < SMALL_N else ""
    return (f"| {name} | {metrics['n']}{flag} | {metrics['n_attack']} | {cell(metrics['block_attack'])} "
            f"| {metrics['n_benign']} | {cell(metrics['fp_benign'])} | {recall} |")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rule_lines = check_rule_on_code_ref()
    contract = base.load_feature_contract()
    train, val = base.load_frames(contract)
    train = train.assign(split="train")
    val = val.assign(split="val")
    full = pd.concat([train, val], ignore_index=True)
    onnx_val = rf_onnx_probs(val, contract)
    sources = base.sources_to_audit(train, val)

    results = {
        "code_ref": "origin/develop",
        "code_commit": subprocess.run(
            ["git", "-C", str(base.REPO), "rev-parse", "origin/develop"],
            check=True, capture_output=True, text=True).stdout.strip(),
        "middleware_rule_lines": rule_lines,
        "rf_params": base.RF_PARAMS,
        "control_seeds": CONTROL_SEEDS,
        "wilson_z": WILSON_Z,
        "sources": [],
    }
    for source in sources:
        results["sources"].append(audit_source(source, train, val, full, contract, onnx_val))
        (OUT / "results_partial.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"{source} done", flush=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print("done", flush=True)


if __name__ == "__main__":
    main()
