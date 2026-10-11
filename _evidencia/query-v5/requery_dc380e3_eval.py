"""Compares RF decisions for Round 5 query derivations: prior reference, old middleware, dc380e3."""
import json
from collections import Counter
from pathlib import Path

import numpy as np
import onnxruntime as ort

V5 = Path("/tmp/lsg-audit/v5")
OUT = Path("/tmp/lsg-audit/out")
RF_PATH = "/tmp/lsg-audit/rf_develop.onnx"
RF_CLASSES = ["benign", "cmdi", "path_traversal", "sqli", "xss"]
RF_THRESHOLD = 0.35
EXCLUDED = {
    "status_code", "req_count_1s", "req_count_5s", "req_count_60s",
    "error_rate_4xx_60s", "endpoint_diversity_60s", "non_json_quote_count",
}
FEATURE_NAMES = json.loads((OUT / "feature_names.txt").read_text().split("feature_names ", 1)[1])
RF_INDICES = [i for i, name in enumerate(FEATURE_NAMES) if name not in EXCLUDED]
assert len(RF_INDICES) == 69


def rf_probs(session, vectors):
    matrix = np.asarray([[v[i] for i in RF_INDICES] for v in vectors], dtype=np.float32)
    output_name = session.get_outputs()[1].name
    return np.asarray(session.run([output_name], {"float_input": matrix})[0], dtype=np.float64)


def decide(probs):
    classes = [RF_CLASSES[i] for i in probs.argmax(axis=1)]
    confidence = probs.max(axis=1)
    blocked = [c != "benign" and conf >= RF_THRESHOLD for c, conf in zip(classes, confidence)]
    return classes, blocked


def feature_diff_names(a, b):
    return [FEATURE_NAMES[i] for i in range(len(a)) if abs(a[i] - b[i]) > 1e-9]


def compare(session, rows, left, right):
    lv = [r["vectors"][left] for r in rows]
    rv = [r["vectors"][right] for r in rows]
    lc, lb = decide(rf_probs(session, lv))
    rc, rb = decide(rf_probs(session, rv))
    diff_counter = Counter()
    rows_with_diff = 0
    rows_rf_diff = 0
    for a, b in zip(lv, rv):
        names = feature_diff_names(a, b)
        diff_counter.update(names)
        rows_with_diff += bool(names)
        rows_rf_diff += any(n not in EXCLUDED for n in names)
    return {
        "n": len(rows),
        "rows_with_any_feature_difference": rows_with_diff,
        "rows_with_rf69_feature_difference": rows_rf_diff,
        "rf_argmax_class_changed": sum(a != b for a, b in zip(lc, rc)),
        "rf_block_decision_changed_T035": sum(a != b for a, b in zip(lb, rb)),
        "block_left": sum(lb),
        "block_right": sum(rb),
        "feature_difference_counts": dict(diff_counter.most_common()),
    }


def main():
    rows = [json.loads(line) for line in open(V5 / "round5_wire_vectors.jsonl", encoding="utf-8")]
    session = ort.InferenceSession(RF_PATH, providers=["CPUExecutionProvider"])
    report = {
        "query_strings": {
            "rows_old_differs_from_wire": sum(r["old_query"] != r["wire_query"] for r in rows),
            "rows_new_differs_from_wire": sum(r["new_query"] != r["wire_query"] for r in rows),
            "rows_old_equals_new": sum(r["old_query"] == r["new_query"] for r in rows),
            "rows_prior_reference_equals_wire": sum(r["prior_reference_query"] == r["wire_query"] for r in rows),
        },
        "new_vs_old": compare(session, rows, "old", "new"),
        "new_vs_prior_reference": compare(session, rows, "prior_reference", "new"),
        "old_vs_prior_reference": compare(session, rows, "prior_reference", "old"),
    }
    report["new_vs_old"]["by_label_decision_changed"] = {}
    for label in ("sqli", "path_traversal", "cmdi"):
        subset = [r for r in rows if r["label"] == label]
        report["new_vs_old"]["by_label_decision_changed"][label] = compare(session, subset, "old", "new")["rf_block_decision_changed_T035"]
    print(json.dumps(report, indent=2, ensure_ascii=False, default=int))
    (V5 / "round5_wire_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=int), encoding="utf-8")


if __name__ == "__main__":
    main()
