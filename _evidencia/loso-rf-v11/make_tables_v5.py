import json
from pathlib import Path

OUT = Path("/tmp/lsg-audit/v4/run2")
data = json.loads((OUT / "results.json").read_text())
prev = {r["held_out_source"]: r for r in json.loads(Path("/tmp/lsg-audit/v4/results.json").read_text())["loso"]}
CLASSES = ["cmdi", "path_traversal", "sqli", "xss"]


def cell(d):
    if d["p"] is None:
        return "—"
    return f"{d['p']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}]"


def recall_text(m):
    return " ".join(f"{c}={cell(m['recall'][c])}" for c in CLASSES if c in m["recall"]) or "—"


lines = ["## Tabla 1. LOSO, todas las filas de S (train+val), Wilson 95%", "",
         "| fuente | n | n<200 | ataques | bloqueo ataques [IC] | benign | FP benign [IC] |", "|---|---|---|---|---|---|---|"]
for s in data["sources"]:
    m = s["c_loso_all_train_val"]
    flag = "sí" if m["n"] < 200 else ""
    lines.append(f"| {s['source']} | {m['n']} | {flag} | {m['n_attack']} | {cell(m['block_attack'])} | {m['n_benign']} | {cell(m['fp_benign'])} |")

lines += ["", "## Tabla 2. S en val: (a) rf.onnx, (b) control aleatorio (media [min, máx] de 5 semillas), (c) LOSO", ""]
for s in data["sources"]:
    if not s["b_control_seeds"]:
        continue
    a, c = s["a_rf_onnx"], s["c_loso_val"]
    seeds = list(s["b_control_seeds"].values())
    lines += [f"### {s['source']} (n_val={s['n_val']}, filas en train removidas por control={s['n_train']})", "",
              "| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |", "|---|---|---|---|---|",
              f"| (a) rf.onnx | {a['n']} | {cell(a['block_attack'])} | {cell(a['fp_benign'])} | {recall_text(a)} |"]
    b_block = [x["block_attack"]["p"] for x in seeds if x["block_attack"]["p"] is not None]
    b_fp = [x["fp_benign"]["p"] for x in seeds if x["fp_benign"]["p"] is not None]
    rec_lines = []
    for cls in CLASSES:
        vals = [x["recall"][cls]["p"] for x in seeds if cls in x["recall"]]
        if vals:
            rec_lines.append(f"{cls}={sum(vals)/len(vals):.3f} [{min(vals):.3f}, {max(vals):.3f}]")
    fmt = lambda v: f"{sum(v)/len(v):.3f} [{min(v):.3f}, {max(v):.3f}]" if v else "—"
    lines.append(f"| (b) control, 5 semillas | {seeds[0]['n']} | {fmt(b_block)} | {fmt(b_fp)} | {' '.join(rec_lines) or '—'} |")
    lines.append(f"| (c) LOSO | {c['n']} | {cell(c['block_attack'])} | {cell(c['fp_benign'])} | {recall_text(c)} |")
    lines.append("")

lines += ["Control: quita de train tantas filas aleatorias como filas tiene S en train (semillas 1-5); RF random_state=42 fijo.", ""]

lines += ["## Tabla 3. payload_full, filas sqli (train+val, n=9224), modelo LOSO", "",
          "| clase predicha (argmax) | filas | % de sqli [IC] | bloqueadas/predichas [IC] |", "|---|---|---|---|"]
pf = next(s for s in data["sources"] if s["source"] == "payload_full")["payload_full_sqli_breakdown"]
for cls, d in pf["by_predicted_class"].items():
    lines.append(f"| {cls} | {d['predicted_count']} | {cell(d['share_of_sqli'])} | {cell(d['blocked_given_predicted'])} |")

lines += ["", "## Verificación: LOSO repetido en origin/develop vs corrida anterior (35b7a28)", "",
          "| fuente | bloqueo ataques anterior | nuevo | FP anterior | nuevo |", "|---|---|---|---|---|"]
for s in data["sources"]:
    m = s["c_loso_all_train_val"]
    p = prev[s["source"]]["all_train_val"]
    lines.append(f"| {s['source']} | {p['attack_block_rate']} | {m['block_attack']['p']} | {p['benign_block_rate_fp']} | {m['fp_benign']['p']} |")

(OUT / "tables_v5.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
