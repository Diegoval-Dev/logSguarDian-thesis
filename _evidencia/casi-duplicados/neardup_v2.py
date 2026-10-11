"""Near-duplicate audit v2: MinHash LSH (datasketch, num_perm=128, params=(8,16))
with exact Jaccard verification of LSH candidates over char 3-gram shingles.

Read-only on the logSguarDian repo. From splits only label and _row_hash are
read; texts come from unified.jsonl. Test rows are compared as request text
(path | query | body), never scored.
"""
import hashlib
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import unquote_plus

import numpy as np
import pyarrow.parquet as pq
from datasketch import MinHash, MinHashLSH
from scipy import sparse

REPO = Path("/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian")
UNIFIED = REPO / "training/data_clean/unified.jsonl"
SPLITS = REPO / "training/splits"
ROUND5 = Path("/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian-vulnerable-project/attack-sim/large_corpus_requests.json")
OUT = Path("/tmp/lsg-audit/v2/out")

SHINGLE_K = 3
NUM_PERM = 128
LSH_PARAMS = (8, 16)
THRESHOLDS = (0.8, 0.9)
CLASSES = ("benign", "sqli", "xss", "path_traversal", "cmdi")
ROUND5_CLASSES = ("sqli", "path_traversal", "cmdi")
RECALL_SAMPLE = 2000
RECALL_SEED = 42


def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", file=sys.stderr, flush=True)


def normalize(text):
    return re.sub(r"\s+", " ", unquote_plus(text or "")).lower().strip()


def request_text(path, query, body):
    return " | ".join(normalize(part) for part in (path, query, body))


def shingle_set(text):
    if len(text) < SHINGLE_K:
        return {text}
    return {text[i:i + SHINGLE_K] for i in range(len(text) - SHINGLE_K + 1)}


def make_minhash(shingles):
    mh = MinHash(num_perm=NUM_PERM)
    mh.update_batch([s.encode("utf8") for s in shingles])
    return mh


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_split_keys(name):
    table = pq.read_table(SPLITS / f"{name}.parquet", columns=["label", "_row_hash"])
    return table.column("_row_hash").to_pylist(), table.column("label").to_pylist()


def load_texts(needed):
    texts = {}
    with open(UNIFIED, encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            key = record.get("_row_hash")
            if key in needed and key not in texts:
                texts[key] = request_text(record.get("path"), record.get("query"), record.get("body"))
    return texts


def round5_rows():
    rows = []
    for item in json.loads(ROUND5.read_text(encoding="utf-8")):
        if item["category"] not in ROUND5_CLASSES:
            continue
        pair = f'{item["param"]}={item["payload"]}'
        if item["method"] == "GET":
            text = request_text(item["path"], pair, "")
        else:
            text = request_text(item["path"], "", pair)
        rows.append({"id": item["id"], "label": item["category"], "text": text})
    return rows


class Index:
    """Train index: LSH over MinHash plus a sparse shingle matrix for exact Jaccard."""

    def __init__(self, texts, labels):
        self.labels = np.asarray(labels)
        self.vocab = {}
        self.lsh = MinHashLSH(num_perm=NUM_PERM, params=LSH_PARAMS)
        self.sizes = []
        rows, cols = [], []
        for idx, text in enumerate(texts):
            shingles = shingle_set(text)
            self.lsh.insert(str(idx), make_minhash(shingles))
            self.sizes.append(len(shingles))
            for shingle in shingles:
                rows.append(idx)
                cols.append(self.vocab.setdefault(shingle, len(self.vocab)))
        self.sizes = np.asarray(self.sizes, dtype=np.int64)
        self.matrix = sparse.csr_matrix(
            (np.ones(len(rows), dtype=np.int32), (rows, cols)),
            shape=(len(self.sizes), len(self.vocab)),
        )

    def encode(self, text):
        shingles = shingle_set(text)
        ids = [self.vocab[s] for s in shingles if s in self.vocab]
        vector = sparse.csr_matrix(
            (np.ones(len(ids), dtype=np.int32), ([0] * len(ids), ids)),
            shape=(1, len(self.vocab)),
        )
        return vector, len(shingles), make_minhash(shingles)

    def candidates(self, minhash):
        return np.fromiter((int(key) for key in self.lsh.query(minhash)), dtype=np.int64)

    def best_jaccards(self, text, query_label, exclude=None):
        vector, size, minhash = self.encode(text)
        cands = self.candidates(minhash)
        if exclude is not None:
            cands = cands[cands != exclude]
        if cands.size == 0:
            return 0.0, 0.0, 0
        inter = (self.matrix[cands] @ vector.T).toarray().ravel()
        jac = inter / (self.sizes[cands] + size - inter)
        same_mask = self.labels[cands] == query_label
        best_same = float(jac[same_mask].max()) if same_mask.any() else 0.0
        return float(jac.max()), best_same, int(cands.size)

    def exact_best(self, text):
        vector, size, _ = self.encode(text)
        inter = (self.matrix @ vector.T).toarray().ravel()
        return float((inter / (self.sizes + size - inter)).max())


def summarize(label_list, any_values, same_values):
    labels = np.asarray(label_list)
    any_values = np.asarray(any_values)
    same_values = np.asarray(same_values)
    table = {}
    for cls in CLASSES + ("ALL",):
        mask = np.ones(len(labels), dtype=bool) if cls == "ALL" else labels == cls
        n = int(mask.sum())
        entry = {"n": n}
        for t in THRESHOLDS:
            entry[f"any_ge_{t}"] = int((any_values[mask] >= t).sum())
            entry[f"same_ge_{t}"] = int((same_values[mask] >= t).sum())
        table[cls] = entry
    return table


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log(f"config num_perm={NUM_PERM} params={LSH_PARAMS} k={SHINGLE_K} norm=unquote_plus+lower+ws")
    keys, labels = {}, {}
    for name in ("train", "val", "test"):
        keys[name], labels[name] = load_split_keys(name)
    needed = set(keys["train"]) | set(keys["val"]) | set(keys["test"])
    texts = load_texts(needed)
    log("texts loaded")

    kept = {}
    missing = {}
    for name in ("train", "val", "test"):
        pairs = [(texts[k], lab) for k, lab in zip(keys[name], labels[name]) if k in texts]
        kept[name] = pairs
        missing[name] = len(keys[name]) - len(pairs)
    log(f"rows without raw text: {missing}")

    train_texts, train_labels = zip(*kept["train"])
    index = Index(train_texts, train_labels)
    log(f"train index built: {len(train_texts)} rows, vocab={len(index.vocab)}")

    results = {"config": {
        "num_perm": NUM_PERM, "lsh_params_bands_rows": LSH_PARAMS, "shingle_k": SHINGLE_K,
        "normalization": "unquote_plus, lowercase, collapse whitespace, per field; joined as path | query | body",
        "verification": "exact Jaccard over 3-char shingle sets on LSH candidates",
        "round5_text": "GET: query='param=payload'; POST: body='param=payload'",
        "round5_classes": ROUND5_CLASSES,
    }, "rows_without_raw_text": missing, "input_sha256": {
        "train.parquet": sha256_of(SPLITS / "train.parquet"),
        "val.parquet": sha256_of(SPLITS / "val.parquet"),
        "test.parquet": sha256_of(SPLITS / "test.parquet"),
        "unified.jsonl": sha256_of(UNIFIED),
        "large_corpus_requests.json": sha256_of(ROUND5),
    }}

    for name in ("val", "test"):
        any_vals, same_vals, cand_counts = [], [], []
        for text, lab in kept[name]:
            best_any, best_same, n_cand = index.best_jaccards(text, lab)
            any_vals.append(best_any)
            same_vals.append(best_same)
            cand_counts.append(n_cand)
        labels_split = [lab for _, lab in kept[name]]
        results[name] = summarize(labels_split, any_vals, same_vals)
        results[name]["mean_lsh_candidates"] = float(np.mean(cand_counts))
        np.savez(OUT / f"{name}_maxjac.npz", labels=np.asarray(labels_split), any=np.asarray(any_vals), same=np.asarray(same_vals))
        log(f"{name} done")

    any_vals, same_vals = [], []
    for i, (text, lab) in enumerate(kept["train"]):
        best_any, best_same, _ = index.best_jaccards(text, lab, exclude=i)
        any_vals.append(best_any)
        same_vals.append(best_same)
        if i % 50000 == 0:
            log(f"train self {i}")
    results["train_self"] = summarize([lab for _, lab in kept["train"]], any_vals, same_vals)
    np.savez(OUT / "train_self_maxjac.npz", labels=np.asarray([lab for _, lab in kept["train"]]), any=np.asarray(any_vals), same=np.asarray(same_vals))
    log("train self done")

    r5 = round5_rows()
    r5_any, r5_same = [], []
    for row in r5:
        best_any, best_same, _ = index.best_jaccards(row["text"], row["label"])
        r5_any.append(best_any)
        r5_same.append(best_same)
    results["round5"] = summarize([row["label"] for row in r5], r5_any, r5_same)
    results["round5"]["ids_per_class"] = dict(Counter(row["label"] for row in r5))
    np.savez(OUT / "round5_maxjac.npz", labels=np.asarray([row["label"] for row in r5]), ids=np.asarray([row["id"] for row in r5]), any=np.asarray(r5_any), same=np.asarray(r5_same))
    log("round5 done")

    rng = np.random.default_rng(RECALL_SEED)
    sample_idx = rng.choice(len(kept["val"]), size=min(RECALL_SAMPLE, len(kept["val"])), replace=False)
    exact_hits = {t: 0 for t in THRESHOLDS}
    lsh_hits = {t: 0 for t in THRESHOLDS}
    val_any = np.load(OUT / "val_maxjac.npz")["any"]
    for i in sample_idx:
        exact = index.exact_best(kept["val"][i][0])
        for t in THRESHOLDS:
            if exact >= t:
                exact_hits[t] += 1
                lsh_hits[t] += int(val_any[i] >= t)
    results["lsh_recall_check_val_sample"] = {
        "sample_size": int(len(sample_idx)),
        "exact_ge": {str(t): exact_hits[t] for t in THRESHOLDS},
        "lsh_found_among_exact_ge": {str(t): lsh_hits[t] for t in THRESHOLDS},
    }
    log("recall check done")

    (OUT / "neardup_v2_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"written {OUT / 'neardup_v2_results.json'}")


if __name__ == "__main__":
    main()
