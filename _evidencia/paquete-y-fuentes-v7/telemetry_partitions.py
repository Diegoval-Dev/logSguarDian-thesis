import json
import sqlite3
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

REPO = Path("/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian")
CURATED = REPO / "training" / "data_clean" / "telemetry_curated_2026-08-29.jsonl"
REPORT = REPO / "packages" / "mlops" / "data" / "cluster_report_20260829_192057.json"
DB = REPO / "packages" / "mlops" / "data" / "mlops-telemetry.db"

rows = [json.loads(l) for l in CURATED.open(encoding="utf-8") if l.strip()]
print("curated lines:", len(rows), "unique _row_hash:", len({r["_row_hash"] for r in rows}))
print("curated label counts:", dict(Counter(r["label"] for r in rows)))

for split in ("train", "val", "test"):
    table = pq.read_table(REPO / "training" / "splits" / f"{split}.parquet", columns=["_source"])
    print(f"{split} mlops_telemetry_curated:", Counter(table.column("_source").to_pylist())["mlops_telemetry_curated"])

report = json.loads(REPORT.read_text(encoding="utf-8"))
print("report total_events:", report["total_events"], "anomalous_events:", report["anomalous_events"], "clusters:", len(report["clusters"]))
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
print("db telemetry_events:", con.execute("select count(*) from telemetry_events").fetchone()[0])
print("db source_id:", dict(con.execute("select source_id, count(*) from telemetry_events group by source_id").fetchall()))
