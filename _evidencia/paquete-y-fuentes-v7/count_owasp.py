import sys
import json
import importlib.util
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

REPO = Path("/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian")
DATA_CLEAN = REPO / "training" / "data_clean"
SOURCE = "owasp_logs"

spec = importlib.util.spec_from_file_location("unify_mod", REPO / "training" / "unify.py")
unify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unify)

def source_count(path, column="_source"):
    table = pq.read_table(path, columns=[column])
    return Counter(table.column(column).to_pylist())

raw_rows = []
with open(DATA_CLEAN / f"{SOURCE}.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            raw_rows.append(json.loads(line))
print("owasp_logs.jsonl rows:", len(raw_rows))
print("owasp label counts:", dict(Counter(r.get("label") for r in raw_rows)))

records = [(SOURCE, r) for r in raw_rows]
kept, dups = unify.deduplicate_exact(records)
print("after deduplicate_exact (owasp only):", len(kept), "dups:", dict(dups))
print("owasp label counts after dedup:", dict(Counter(r.get("label") for _, r in kept)))

unified = [json.loads(l) for l in open(DATA_CLEAN / "unified.jsonl", encoding="utf-8") if l.strip()]
print("unified.jsonl _source counts:", dict(Counter(r.get("_source") for r in unified)))

features_counts = source_count(REPO / "training" / "features.parquet") if False else source_count(DATA_CLEAN / "features.parquet")
print("features.parquet _source counts:", dict(features_counts))

for split in ("train", "val", "test"):
    counts = source_count(REPO / "training" / "splits" / f"{split}.parquet")
    print(f"{split}.parquet _source counts:", dict(counts))
