"""Regenerates the User-Agent breakdown of Isolation Forest flags on the validation split.

Regeneration: the script that produced ua_check.txt is not preserved. This script
recomputes the same quantities from logSguarDian's validation split and if.onnx.
It reads validation only; it never opens the test split.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
import pyarrow.parquet as pq

DEFAULT_LOGSGUARDIAN = Path(__file__).resolve().parents[3] / "logSguarDian"
META_COLUMNS = {"sample_id", "label", "timestamp", "_source", "_row_hash"}
RF_EXCLUDED = {"status_code", "req_count_1s", "req_count_5s", "req_count_60s",
               "error_rate_4xx_60s", "endpoint_diversity_60s", "non_json_quote_count"}
IF_EXTRA_EXCLUDED = {"dotdot_encoded_count", "authorization_length", "unusual_headers_count",
                     "null_byte_count", "os_path_indicator", "sensitive_file_target"}
UA_PRESENT = "ua_present"
UA_LENGTH = "ua_length"
BENIGN = "benign"
EXPECTED_IF_FEATURES = 63


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--logsguardian", type=Path, default=DEFAULT_LOGSGUARDIAN,
                        help="Path to the logSguarDian repository (validation split and models).")
    return parser.parse_args()


def if_feature_names(table):
    names = [c for c in table.schema.names if c not in META_COLUMNS]
    return [c for c in names if c not in RF_EXCLUDED and c not in IF_EXTRA_EXCLUDED]


def if_scores(session, table, names):
    matrix = np.stack(
        [np.asarray(table.column(n).to_numpy(zero_copy_only=False), dtype=np.float32) for n in names],
        axis=1,
    )
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[1].name
    return np.asarray(session.run([output_name], {input_name: matrix})[0], dtype=np.float32).reshape(-1)


def flag_rate_by_ua_presence(flags, ua_present, benign_mask):
    lines = []
    for value in (0, 1):
        group = benign_mask & (ua_present == value)
        count = int(group.sum())
        share = count / benign_mask.sum() * 100
        flagged = int((flags & group).sum())
        rate = flags[group].mean() * 100
        lines.append(f"benign ua_present={value:2d} n={count:6d} pct={share:.2f} "
                     f"flag={rate:.3f}% flagged={flagged}")
    return lines


def main():
    args = parse_args()
    models_dir = args.logsguardian / "training" / "models"
    table = pq.read_table(args.logsguardian / "training" / "splits" / "val.parquet")

    threshold = json.loads((models_dir / "if_v10_metadata.json").read_text())["threshold"]
    names = if_feature_names(table)
    assert len(names) == EXPECTED_IF_FEATURES, len(names)

    session = ort.InferenceSession(str(models_dir / "if.onnx"), providers=["CPUExecutionProvider"])
    flags = if_scores(session, table, names) < threshold

    labels = np.array(table.column("label").to_pylist())
    benign_mask = labels == BENIGN
    ua_present = np.asarray(table.column(UA_PRESENT).to_numpy(zero_copy_only=False))
    ua_length = np.asarray(table.column(UA_LENGTH).to_numpy(zero_copy_only=False), dtype=np.float64)

    for line in flag_rate_by_ua_presence(flags, ua_present, benign_mask):
        print(line)
    print(f"benign flagged total: {int((flags & benign_mask).sum())} of {int(benign_mask.sum())}")
    benign_length = ua_length[benign_mask]
    print(f"benign ua_length median {np.median(benign_length):.1f} "
          f"p90 {np.percentile(benign_length, 90):.1f} p99 {np.percentile(benign_length, 99):.1f}")


if __name__ == "__main__":
    main()
