"""Exact numerators for the VAL block-gap table (recall per class, benign block rate).

Reuses the setup in block_gap_val.py. Read-only; val only.
"""
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
import pyarrow.parquet as pq

import block_gap_val as bg

OUT = Path("/tmp/lsg-audit/v3/out")


def cell(k, n):
    lo, hi = bg.wilson(k, n)
    return {"k": k, "n": n, "rate": k / n if n else float("nan"), "ci95": [lo, hi]}


def main():
    names = bg.load_feature_names()
    table = pq.read_table(bg.VAL, columns=["_row_hash", "label"] + names)
    hashes = table.column("_row_hash").to_pylist()
    labels_all = np.asarray(table.column("label").to_pylist())
    feats = np.column_stack([table.column(c).to_numpy(zero_copy_only=False) for c in names]).astype(np.float32)
    present = bg.textual_hashes()
    kept = np.asarray([h in present for h in hashes])
    labels = labels_all[kept]
    mj = np.load(bg.MAXJAC)
    assert np.array_equal(labels, mj["labels"])
    has_nb = mj["any"] >= bg.NEIGHBOR_THRESHOLD
    probs = ort.InferenceSession(str(bg.RF_ONNX), providers=["CPUExecutionProvider"]).run(
        ["probabilities"], {"float_input": feats[kept]})[0]
    idx = probs.argmax(1)
    blocked = (idx != 0) & (probs.max(1) >= bg.BLOCK_THRESHOLD)
    res = {}
    for gname, gmask in (("con_vecino_J>=0.8", has_nb), ("sin_vecino_J>=0.8", ~has_nb)):
        res[gname] = {}
        for cls in bg.RF_CLASSES:
            sel = gmask & (labels == cls)
            k = int(blocked[sel].sum())
            res[gname][cls] = cell(k, int(sel.sum()))
    res["rf_sha_check"] = bg.sha256_of(bg.RF_ONNX)
    (OUT / "block_gap_counts.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["| Grupo | Clase | Bloqueados/n | Tasa | IC95 Wilson |", "|---|---|--:|--:|--|"]
    for g in ("con_vecino_J>=0.8", "sin_vecino_J>=0.8"):
        for cls in bg.RF_CLASSES:
            c = res[g][cls]
            label = "tasa bloqueo (FP)" if cls == "benign" else "recall"
            lines.append(f"| {g} | {cls} ({label}) | {c['k']}/{c['n']} | {c['rate']:.4f} | [{c['ci95'][0]:.4f}, {c['ci95'][1]:.4f}] |")
    text = "\n".join(lines)
    (OUT / "block_gap_counts.md").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
