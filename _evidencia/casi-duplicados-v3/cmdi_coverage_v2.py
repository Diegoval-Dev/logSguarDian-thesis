"""cmdi coverage, Ronda 5, denominator = all 200 cmdi payloads.

Timeouts / errors / HTTP 5xx count as NOT blocked. Read-only.
"""
import json
from pathlib import Path

import numpy as np

SIM = Path("/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian-vulnerable-project/attack-sim")
FILES = {"tarball-20261009": SIM / "results_config2-develop-tarball-20261009.json",
         "config2": SIM / "results_config2.json"}
MAXJAC = Path("/tmp/lsg-audit/v2/out/round5_maxjac.npz")
OUT = Path("/tmp/lsg-audit/v3/out")


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main():
    m = np.load(MAXJAC)
    mask = m["labels"] == "cmdi"
    ids, best = m["ids"][mask].tolist(), m["any"][mask]
    excl = {"J>=0.8": set(np.asarray(ids)[best >= 0.8].tolist()),
            "J>=0.9": set(np.asarray(ids)[best >= 0.9].tolist())}
    lines, out = [], {"excluded_ids": {k: sorted(v) for k, v in excl.items()}, "files": {}}
    lines.append(f"Excluidos J>=0.8 ({len(excl['J>=0.8'])}): {sorted(excl['J>=0.8'])}")
    lines.append(f"Excluidos J>=0.9 ({len(excl['J>=0.9'])}): {sorted(excl['J>=0.9'])}")
    lines.append(f"J>=0.9 subset of J>=0.8: {excl['J>=0.9'] <= excl['J>=0.8']}\n")
    lines.append("| Archivo | Subconjunto | blocked/n | cobertura | IC95 |")
    lines.append("|---|---|--:|--:|--|")
    for label, path in FILES.items():
        entries = [e for e in json.loads(path.read_text(encoding="utf-8")) if e["category"] == "cmdi"]
        assert len(entries) == 200
        out["files"][label] = {}
        for sub, ex in (("todos", set()), ("excl J>=0.8", excl["J>=0.8"]), ("excl J>=0.9", excl["J>=0.9"])):
            scope = [e for e in entries if e["id"] not in ex]
            k = sum(1 for e in scope if e.get("blocked") is True)
            n = len(scope)
            lo, hi = wilson(k, n)
            out["files"][label][sub] = {"blocked": k, "n": n, "ci95": [lo, hi]}
            lines.append(f"| {label} | {sub} | {k}/{n} | {k/n:.4f} | [{lo:.3f}, {hi:.3f}] |")
        nb = [e["id"] for e in entries if e.get("blocked") is not True]
        out["files"][label]["not_blocked_ids"] = nb
        lines.append(f"\n{label} no bloqueados ({len(nb)}): {nb}")
    text = "\n".join(lines)
    (OUT / "cmdi_coverage_v2.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "cmdi_coverage_v2.md").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
