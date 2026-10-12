import json
import math
import sys
from collections import OrderedDict

import pyarrow.parquet as pq

REPO = "/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian"
SPLITS = OrderedDict([
    ("train", f"{REPO}/training/splits/train.parquet"),
    ("val", f"{REPO}/training/splits/val.parquet"),
])
CLASSES = ["benign", "sqli", "xss", "path_traversal", "cmdi"]
UA_LONG_THRESHOLD = 40
UA_PRESENT_THRESHOLD = 0
Z_95 = 1.959963984540054
COLUMNS = ["label", "ua_length", "ua_present"]


def wilson_interval(successes, total):
    if total == 0:
        return (0.0, 0.0)
    proportion = successes / total
    z2 = Z_95 ** 2
    denominator = 1 + z2 / total
    center = (proportion + z2 / (2 * total)) / denominator
    half = Z_95 * math.sqrt(proportion * (1 - proportion) / total + z2 / (4 * total ** 2)) / denominator
    return (max(0.0, center - half), min(1.0, center + half))


def load_partition(path):
    table = pq.read_table(path, columns=COLUMNS)
    return table.to_pydict()


def tally(rows):
    stats = OrderedDict()
    for label, ua_length, ua_present in rows:
        entry = stats.setdefault(label, {"n": 0, "long": 0, "present": 0})
        entry["n"] += 1
        entry["long"] += ua_length > UA_LONG_THRESHOLD
        entry["present"] += ua_present > UA_PRESENT_THRESHOLD
    return stats


def row_iter(data):
    return zip(data["label"], data["ua_length"], data["ua_present"])


def summarize(partition_stats):
    result = OrderedDict()
    for cls in CLASSES:
        entry = partition_stats.get(cls, {"n": 0, "long": 0, "present": 0})
        low, high = wilson_interval(entry["long"], entry["n"])
        result[cls] = {
            "n": entry["n"],
            "long": entry["long"],
            "pct_long": 100 * entry["long"] / entry["n"] if entry["n"] else 0.0,
            "wilson_low": 100 * low,
            "wilson_high": 100 * high,
            "present": entry["present"],
            "pct_present": 100 * entry["present"] / entry["n"] if entry["n"] else 0.0,
        }
    return result


def main():
    results = OrderedDict()
    combined_rows = []
    for name, path in SPLITS.items():
        data = load_partition(path)
        rows = list(row_iter(data))
        combined_rows.extend(rows)
        results[name] = summarize(tally(rows))
        unknown = set(data["label"]) - set(CLASSES)
        if unknown:
            print(f"WARNING {name}: unexpected labels {sorted(unknown)}", file=sys.stderr)
    results["train+val"] = summarize(tally(combined_rows))
    json.dump(results, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
