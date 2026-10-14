#!/usr/bin/env python3
"""Recalculate every figure of TABLA_VERIFICACION_CIFRAS.md from its source and compare.

Usage:
    python3 verificar_cifras.py             # all 32 rows
    python3 verificar_cifras.py --fila 12   # one row

Row status: OK, DIFERENTE (some value differs) or NO VERIFICABLE (no source or no computable value).
"""

import argparse
import ast
import fnmatch
import hashlib
import io
import json
import math
import re
import shutil
import statistics
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pyarrow.parquet as pq

SCRIPT = Path(__file__).resolve()
TESIS = SCRIPT.parents[2]
EVIDENCIA = TESIS / "_evidencia"
TABLA = EVIDENCIA / "verificacion-cifras" / "TABLA_VERIFICACION_CIFRAS.md"
PDF = TESIS / "z-main.pdf"
REPO_APP = TESIS.parent / "logSguarDian"
REPO_VULN = TESIS.parent / "logSguarDian-vulnerable-project"
REPOS = {"logSguarDian": REPO_APP, "logSguarDian-vulnerable-project": REPO_VULN}
REF = "origin/main"
WILSON_Z = 1.959963984540054
HTTP_BLOCKED = 403
REPETITIONS = 5
LATENCY_RUN = "20260926-223609"
LATENCY_TGZ = "docs/evidence/latency-linux-2026-09-26.tgz"
COAUTOR = "_evidencia/coautor-ronda5-v10/"
SKEW_TXT = "docs/findings-evidence/juice-shop-ua-bias/output/corpus_ua_skew.txt"
STATUS_OK, STATUS_DIFF, STATUS_NV = "OK", "DIFERENTE", "NO VERIFICABLE"


class MissingSource(Exception):
    pass


@dataclass
class Item:
    label: str
    claimed: str
    found: str
    ok: bool | None
    reason: str = ""


def git_show(repo, spec):
    result = subprocess.run(["git", "-C", str(repo), "show", spec], capture_output=True)
    return result.stdout if result.returncode == 0 else None


def commit_exists(repo, commit):
    result = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"], capture_output=True)
    return result.returncode == 0


def tracked_files(repo):
    result = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", REF], capture_output=True, text=True)
    return result.stdout.splitlines()


def suggest_paths(rel):
    name = rel.rsplit("/", 1)[-1]
    found = [f"{label}:{path}" for label, repo in REPOS.items() for path in tracked_files(repo) if path.endswith("/" + name)]
    return found[:3]


def blocked_counts(entries):
    counts = {}
    for entry in entries:
        category = "path" if entry["category"].startswith("path") else entry["category"]
        blocked, total = counts.get(category, (0, 0))
        counts[category] = (blocked + (entry["status"] == HTTP_BLOCKED), total + 1)
    return counts


def wilson_percent(successes, total):
    p = successes / total
    z2 = WILSON_Z ** 2
    denominator = 1 + z2 / total
    center = (p + z2 / (2 * total)) / denominator
    half = WILSON_Z * math.sqrt(p * (1 - p) / total + z2 / (4 * total ** 2)) / denominator
    return (center - half) * 100, (center + half) * 100


def cells_of(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def block_between(text, start, end):
    begin = text.index(start) + len(start)
    return text[begin:text.index(end, begin)]


class Ctx:
    """Collects the sources read and the comparisons made for one row."""

    def __init__(self):
        self.sources = []
        self.items = []
        self.notes = []

    def use(self, data, label):
        if label not in self.sources:
            self.sources.append(label)
        return data

    def blob(self, rel):
        if rel.startswith("_evidencia/"):
            path = TESIS / rel
            if path.is_file():
                return self.use(path.read_bytes(), f"tesis/{rel}")
        else:
            for label, repo in REPOS.items():
                data = git_show(repo, f"{REF}:{rel}")
                if data is not None:
                    return self.use(data, f"{label}@{REF}:{rel}")
        hints = suggest_paths(rel) if not rel.startswith("_evidencia/") else []
        raise MissingSource(f"fuente no encontrada: {rel}" + (f" · candidatas: {hints}" if hints else ""))

    def text(self, rel):
        return self.blob(rel).decode("utf-8", "replace")

    def json(self, rel):
        return json.loads(self.blob(rel))

    def glob(self, pattern):
        names = [name for name in tracked_files(REPO_APP) if fnmatch.fnmatch(name, pattern)]
        return [(name, self.json(name)) for name in names]

    def local_parquet_rows(self, rel):
        path = REPO_APP / rel
        if not path.is_file():
            raise MissingSource(f"archivo local no encontrado: {rel}")
        self.use(b"", f"logSguarDian (local, sin versionar):{rel}")
        return pq.ParquetFile(path).metadata.num_rows

    def compare(self, label, claimed, found, decimals):
        ok = abs(found - claimed) <= 0.5 * 10 ** -decimals + 1e-12
        self.items.append(Item(label, f"{claimed}", f"{found:.{decimals}f}", ok))

    def equal(self, label, claimed, found):
        self.items.append(Item(label, str(claimed), str(found), claimed == found))

    def check(self, label, condition, found=None):
        self.items.append(Item(label, "cumple", found or ("sí" if condition else "no"), bool(condition)))

    def count(self, label, claimed, found):
        self.items.append(Item(label, f"{claimed[0]}/{claimed[1]}", f"{found[0]}/{found[1]}", claimed == found))

    def unverified(self, label, reason):
        self.items.append(Item(label, "", "", None, reason))

    def note(self, text):
        self.notes.append(text)


def status_of(items):
    if any(item.ok is False for item in items):
        return STATUS_DIFF
    if not items or any(item.ok is None for item in items):
        return STATUS_NV
    return STATUS_OK


# ---------- PDF and table ----------

def pdf_pages():
    text = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True, text=True, check=True).stdout
    return [re.sub(r"\s+", " ", re.sub(r"-\n(?=\w)", "", page)) for page in text.split("\f")]


def value_pattern(value):
    parts = [re.escape(part) for part in value.split(" ") if part]
    body = r"[\s  ]?".join(parts)
    return re.compile(rf"(?<![\w.,]){body}(?![\w]|[.,]\d)")


def count_in_pdf(pages, value):
    pattern = value_pattern(value)
    hits = [number for number, page in enumerate(pages, 1) for _ in pattern.findall(page)]
    return len(hits), sorted(set(hits))


def pdf_report(pages, cell):
    parts = []
    for value in re.findall(r"\*\*(.+?)\*\*", cell):
        total, where = count_in_pdf(pages, value)
        note = ""
        core = re.search(r"\d+(?:\.\d+)?", value)
        if total == 0 and core:
            total, where = count_in_pdf(pages, core.group())
            note = f" (literal sin coincidencia; número «{core.group()}»)"
        parts.append(f"«{value}» → {total} lugar(es), pp. {where[:6]}{note}")
    return "; ".join(parts) if parts else "sin valores en negrita"


def table_rows():
    rows = {}
    for line in TABLA.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\|\s*\d+\s*\|", line):
            cells = cells_of(line)
            rows[int(cells[0])] = cells
    return rows


# ---------- one function per row: recalculate and compare ----------

def row_01(ctx):
    runs = ctx.glob("benchmarks/results/extractor-*.json")
    p95_ms = [run["series"]["worker_roundtrip"]["fixtures"]["mixed"]["ns"]["p95"] / 1e6 for _, run in runs]
    ctx.check(f"{len(runs)} corridas del 9-oct", len(runs) == 3 and all(run["timestamp"].startswith("2026-10-09") for _, run in runs))
    ctx.compare("p95 mixto worker_threads, mediana (ms, desde ns)", 0.0273, statistics.median(p95_ms), 4)
    ctx.note("el campo fixtures.mixed.p95 está redondeado a 3 decimales en ms (0.027); la precisión está en ns.p95")


def row_02(ctx):
    v11 = ctx.json("training/results/v11_test_results.json")
    ctx.compare("macro F1 RF", 0.9776, v11["rf_macro_f1"], 4)
    ctx.compare("F1 cmdi", 0.9239, v11["rf_classification_report"]["cmdi"]["f1-score"], 4)


def row_03(ctx):
    v11 = ctx.json("training/results/v11_test_results.json")
    ctx.compare("recall IF", 0.9125, v11["if_test_recall"], 4)
    ctx.compare("falsos positivos IF", 0.0546, v11["if_test_fp_rate"], 4)
    ctx.check("criterios IF (recall ≥ 50 %, FP ≤ 10 %)", v11["if_test_recall"] >= 0.5 and v11["if_test_fp_rate"] <= 0.10)


def row_04(ctx):
    parity = ctx.json("training/models/parity_report.json")
    ctx.compare("RF max |Δprob| (×10⁻⁷)", 1.01, parity["rf_max_prob_diff"] / 1e-7, 2)
    ctx.compare("IF max |Δscore| (×10⁻⁷)", 2.42, parity["if_max_score_diff"] / 1e-7, 2)


def row_05(ctx):
    names = re.findall(r"^\|\s*\d+\s*\|\s*`?([a-z][a-z0-9_]*)`?\s*\|", ctx.text("docs/feature-spec.md"), re.MULTILINE)
    worker = ctx.text("packages/core/src/worker.ts")
    excluded = set(re.findall(r'"([a-z0-9_]+)"', block_between(worker, "const EXCLUDED_NAMES = new Set([", "]);")))
    if_extra = set(re.findall(r'"([a-z0-9_]+)"', block_between(worker, "const IF_ADDITIONAL_EXCLUDED = new Set([", "]);")))
    rf_names = [name for name in names if name not in excluded]
    if_names = [name for name in rf_names if name not in if_extra]
    ctx.equal("features en feature-spec.md", 76, len(names))
    ctx.equal("exclusiones comunes que existen en la lista", len(excluded), len(excluded & set(names)))
    ctx.equal("entradas RF", 69, len(rf_names))
    ctx.equal("entradas IF", 63, len(if_names))
    ctx.equal("exclusiones temporales (_1s, _5s, _60s)", 5, sum(1 for name in excluded if re.search(r"_(1s|5s|60s)$", name)))
    ctx.equal("exclusiones extra del IF", 6, len(if_extra))
    ctx.unverified("autoría 72 / 4 (Sebastián / tú)", "la autoría por feature no consta en el repo; requiere git log/blame y revisión manual")


def row_06(ctx):
    dedup = ctx.text("_evidencia/paquete-y-fuentes-v7/dedup_full.txt")
    kept_total = int(re.search(r"kept: (\d+)", dedup).group(1))
    kept_per_source = ast.literal_eval(re.search(r"kept per source: (\{.*\})", dedup).group(1))
    telemetry_rows = int(re.search(r"unique _row_hash: (\d+)", ctx.text("_evidencia/paquete-y-fuentes-v7/telemetry_counts.txt")).group(1))
    train_val = int(re.search(r"TOTAL\s+(\d+)", ctx.text("_evidencia/loso-rf-v11/source_counts.txt")).group(1))
    test_rows = ctx.json("training/results/v11_test_results.json")["n_test_rows"]
    synthetic = [source for source in kept_per_source if source.startswith("synthetic_")]
    ctx.equal("corpus total (dedup + telemetría)", 383202, kept_total + telemetry_rows)
    ctx.equal("fuentes (16 dedup + telemetría)", 17, len(kept_per_source) + 1)
    ctx.equal("generadores propios (synthetic_*)", 7, len(synthetic))
    ctx.equal("conjuntos o listas públicas", 9, len(kept_per_source) - len(synthetic))
    ctx.equal("train + val (source_counts)", 325721, train_val)
    ctx.equal("test (n_test_rows)", 57481, test_rows)
    ctx.equal("train + val + test = corpus", 383202, train_val + test_rows)
    ctx.equal("train (metadatos parquet, sin abrir test)", 268240, ctx.local_parquet_rows("training/splits/train.parquet"))
    ctx.equal("val (metadatos parquet)", 57481, ctx.local_parquet_rows("training/splits/val.parquet"))


def row_07(ctx):
    readings = []
    for commit in ["3086318", "fc47a5b", "03de50f"]:
        exists = commit_exists(REPO_APP, commit)
        ctx.check(f"commit {commit} existe en logSguarDian", exists)
        blob = git_show(REPO_APP, f"{commit}:training/results/v11_test_results.json") if exists else None
        if blob is not None:
            readings.append(ctx.use(json.loads(blob), f"logSguarDian@{commit}:training/results/v11_test_results.json"))
    ctx.check("macro F1 0,9843 en una lectura del test", any(abs(r["rf_macro_f1"] - 0.9843) < 5e-5 for r in readings))
    ctx.check("umbral IF 0,00807 en una lectura del test", any(abs(r.get("if_threshold", 0) - 0.00807) < 5e-6 for r in readings))
    current = ctx.json("training/results/v11_test_results.json")
    ctx.compare("umbral IF actual", 0.00421, current["if_threshold"], 5)


def row_08(ctx):
    lock = ctx.text("training/splits/test.lock.sha256").split()[0]
    history = ctx.text("_evidencia/query-v5/lock_history.md")
    ctx.check("lock vigente 7486c258…4fd9", lock.startswith("7486c258") and lock.endswith("4fd9"), found=lock[:8] + "…" + lock[-4:])
    ctx.check("lock v10 6c5f253d… en historial", "6c5f253d" in history)
    ctx.equal("filas del test con lock vigente", 57481, ctx.json("training/results/v11_test_results.json")["n_test_rows"])
    if "57 308" in history or "57308" in history:
        ctx.check("57 308 filas en lock_history.md", True)
    else:
        ctx.unverified("57 308 filas del lock v10", "lock_history.md no registra el número de filas del lock v10")


def row_09(ctx):
    text = ctx.text("_evidencia/revalidacion-umbral-if/analysis_out.txt")
    benign, recall = re.search(r"Stability T=0\.30 vs 0\.40: \|d benign_block\|=([\d.]+) pp, \|d recall_global\|=([\d.]+) pp", text).groups()
    ctx.compare("|Δ bloqueo benigno| T 0,30–0,40 (pp)", 0.0067, float(benign), 4)
    ctx.compare("|Δ recall| T 0,30–0,40 (pp)", 0.056, float(recall), 3)
    ctx.check("criterio < 0,5 pp en ambos", "Criterion (<0.5 pp both): True" in text)


def row_10(ctx):
    text = ctx.text("_evidencia/revalidacion-umbral-if/analysis_out.txt")
    passed, total = re.search(r"RF-passed attacks: (\d+) of (\d+)", text).groups()
    ctx.equal("ataques que pasan RF", 39, int(passed))
    ctx.equal("ataques totales", 42594, int(total))
    ctx.equal("ataques extra marcados por IF", 19, int(re.search(r"IF flags among RF-passed attacks, total: (\d+)", text).group(1)))
    ctx.equal("benignos marcados por IF (costo)", 866, int(re.search(r"IF-flagged \(cost\): (\d+)", text).group(1)))
    rf_block, or_block = re.search(r"benign block: RF=([\d.]+)%\s+OR=([\d.]+)%", text).groups()
    ctx.compare("bloqueo benigno solo RF (%)", 0.107, float(rf_block), 3)
    ctx.compare("bloqueo benigno RF o IF (%)", 5.925, float(or_block), 3)


def row_11(ctx):
    text = ctx.text("_evidencia/revalidacion-umbral-if/ua_check_regenerado_out.txt")
    flagged, benign = re.search(r"benign flagged total: (\d+) of (\d+)", text).groups()
    ua_n, ua_flagged = re.search(r"ua_present=\s*1 n=\s*(\d+) .*?flagged=(\d+)", text).groups()
    ctx.equal("benignos marcados por IF", 874, int(flagged))
    ctx.equal("benignos totales", 14887, int(benign))
    ctx.equal("benignos con User-Agent", 69, int(ua_n))
    ctx.equal("de ellos marcados", 67, int(ua_flagged))
    ctx.compare("porcentaje con UA marcado (%)", 97.1, int(ua_flagged) / int(ua_n) * 100, 1)


def row_12(ctx):
    lines = ctx.text("docs/config3b-results.md").splitlines()
    header_index = next(i for i, line in enumerate(lines) if line.startswith("| Category |"))
    header = cells_of(lines[header_index])
    overall = cells_of(next(line for line in lines if line.startswith("| **Overall**")))
    cmdi = cells_of(next(line for line in lines[header_index:] if line.startswith("| cmdi |")))
    ctx.check("columnas: Config 2 / 3a / 3b", "Config 2" in header[2] and "Config 3a" in header[3] and "Config 3b" in header[4])
    for index, (k, n, pct) in zip((2, 3, 4), ((583, 590, 98.8), (550, 590, 93.2), (587, 590, 99.5))):
        found_k, found_n = map(int, re.search(r"(\d+)/(\d+)", overall[index]).groups())
        ctx.count(f"Overall columna {header[index]}", (k, n), (found_k, found_n))
        ctx.compare(f"  porcentaje {header[index]}", pct, found_k / found_n * 100, 1)
    ctx.count("cmdi Config 2", (200, 200), tuple(map(int, re.search(r"(\d+)/(\d+)", cmdi[2]).groups())))
    caught = int(re.search(r"(\d+) were independently caught", "\n".join(lines)).group(1))
    ctx.equal("ataques que pasan el WAF y atrapa logSguarDian", 37, caught)
    ctx.equal("ataques que pasan el WAF (590 − 550)", 40, 590 - 550)


def row_13(ctx):
    counts = blocked_counts(ctx.json("attack-sim/results_config2-develop-tarball-20261009.json"))
    for category, claimed, pct in (("sqli", 199, 99.5), ("path", 190, 95.0), ("cmdi", 192, 96.0)):
        blocked, total = counts[category]
        ctx.count(f"{category} bloqueadas (HTTP 403)", (claimed, 200), (blocked, total))
        ctx.compare(f"  porcentaje {category}", pct, blocked / total * 100, 1)
    config3b = ctx.text("docs/config3b-results.md")
    match = re.search(r"SHA-256 `cf1238[0-9a-f]*`", config3b)
    if match is None:
        ctx.unverified("tarball cf1238… (par C)", "docs/config3b-results.md no registra el SHA-256 cf1238…")
        return
    preceding = config3b[max(0, match.start() - 300):match.start()]
    built_from = "logsguardian-0.1.0.tgz" if "logsguardian-0.1.0.tgz" in preceding else "desconocido"
    ctx.check("cf1238… es el par C de la fila 31 (logsguardian 0.1.1, abf8d5c4…)", built_from == "logsguardian-0.1.1.tgz", found=f"docs: {built_from} (develop)")


def row_14(ctx):
    counts = blocked_counts(ctx.json("attack-sim/results_config2.json"))
    for category, claimed in (("sqli", 200), ("path", 170), ("cmdi", 183)):
        ctx.count(f"{category} bloqueadas (HTTP 403)", (claimed, 200), counts[category])
    low, high = wilson_percent(*counts["path"])
    ctx.compare("Wilson 95 % path, límite inferior (%)", 79.4, low, 1)
    ctx.compare("Wilson 95 % path, límite superior (%)", 89.3, high, 1)
    ctx.check("commit a3aada0 existe en logSguarDian-vulnerable-project", commit_exists(REPO_VULN, "a3aada0"))


def row_15(ctx):
    lines = ctx.text("docs/config3b-results.md").splitlines()
    start = lines.index("### Results")
    xss = cells_of(next(line for line in lines[start:] if line.startswith("| xss |")))
    found_k, found_n = map(int, re.search(r"(\d+)/(\d+)", xss[2]).groups())
    ctx.count("XSS Config 2 (ronda 4)", (110, 113), (found_k, found_n))
    ctx.compare("XSS Config 2 porcentaje (%)", 97.3, found_k / found_n * 100, 1)
    ctx.check("ZAP XSS ronda 5: 1/1 (100,0 %)", "1/1 (100.0%)" in "\n".join(lines))
    ctx.equal("alertas ZAP totales", 538, len(ctx.json(COAUTOR + "zap-alerts-full.json")["alerts"]))


def latency_files(ctx):
    archive = tarfile.open(fileobj=io.BytesIO(ctx.blob(LATENCY_TGZ)))
    return {
        member.name: archive.extractfile(member).read()
        for member in archive.getmembers()
        if member.isfile() and not member.name.rsplit("/", 1)[-1].startswith("._")
    }


def latency_run(files, scenario, phase, rep, suffix=".parsed.json"):
    name = f"{LATENCY_RUN}/{scenario}-{phase}-rep{rep}{suffix}"
    matches = [data for path, data in files.items() if path.endswith("/" + name)]
    if len(matches) != 1:
        raise MissingSource(f"{name}: {len(matches)} coincidencias en el tgz")
    return json.loads(matches[0])


def p95_median_delta(ctx, files, scenario):
    active = [latency_run(files, scenario, "active", rep)["p95"] for rep in range(1, REPETITIONS + 1)]
    baseline = [latency_run(files, scenario, "baseline", rep)["p95"] for rep in range(1, REPETITIONS + 1)]
    mean_pair_delta = statistics.mean(a - b for a, b in zip(active, baseline))
    ctx.note(f"{scenario}: con media de pares el Δp95 sería {mean_pair_delta:.2f}; la tabla no declara el estadístico y reproduce con mediana")
    return statistics.median(active) - statistics.median(baseline)


def row_16(ctx):
    files = latency_files(ctx)
    for scenario, claimed in (("normal", 12.08), ("attack", 12.85)):
        delta = p95_median_delta(ctx, files, scenario)
        ctx.compare(f"Δp95 {scenario} (mediana de 5 repeticiones, ms)", claimed, delta, 2)
        ctx.check(f"Δp95 {scenario} ≤ 15 ms (criterio)", delta <= 15)


def row_17(ctx):
    files = latency_files(ctx)
    timeouts, requests = 0, 0
    for rep in range(1, REPETITIONS + 1):
        counters = latency_run(files, "volume", "active", rep, suffix=".json")["aggregate"]["counters"]
        timeouts += counters.get("errors.ERR_SOCKET_TIMEOUT", 0)
        requests += counters.get("http.requests", 0)
    delta = p95_median_delta(ctx, files, "volume")
    ctx.compare("Δp95 volumen (mediana de 5 repeticiones, ms)", 6495.46, delta, 2)
    ctx.equal("timeouts volumen", 1824, timeouts)
    ctx.equal("solicitudes volumen", 26048, requests)
    ctx.compare("porcentaje de timeouts", 7.00, timeouts / requests * 100, 2)
    ctx.check("Δp95 volumen > 15 ms (no cumple)", delta > 15)


def row_18(ctx):
    increments = {inc["scenario"]: inc["summary"] for inc in ctx.json("docs/evidence/resources_summary.json")["increments"] if inc["window"] == "A"}
    ctx.compare("memoria ataque (MiB)", 331.9, increments["attack"]["mem_mb_delta"], 1)
    ctx.compare("memoria normal (MiB)", 332.0, increments["normal"]["mem_mb_delta"], 1)
    ctx.compare("memoria volumen (MiB)", 375.9, increments["volume"]["mem_mb_delta"], 1)
    ctx.compare("150 MB expresados en MiB", 143, 150e6 / 2 ** 20, 0)


def row_19(ctx):
    increments = {inc["scenario"]: inc["summary"] for inc in ctx.json("docs/evidence/resources_summary.json")["increments"] if inc["window"] == "A"}
    ctx.compare("CPU ataque (%)", 529.6, increments["attack"]["cpu_rel_pct"], 1)
    ctx.compare("CPU normal (%)", 614.4, increments["normal"]["cpu_rel_pct"], 1)
    ctx.compare("CPU volumen (%)", 40.1, increments["volume"]["cpu_rel_pct"], 1)
    ctx.check("criterio 15 % no cumple", all(inc["cpu_rel_pct"] > 15 for inc in increments.values()))


def row_20(ctx):
    text = ctx.text("docs/limitations.md")
    match = re.search(
        r"(\d+) de (\d+) peticiones con User-Agent de navegador \(([\d.]+)%\)[^.]*?frente a (\d+) de (\d+) \(([\d.]+)%\) con curl",
        text,
    )
    browser_k, browser_n, browser_pct, curl_k, curl_n, curl_pct = match.groups()
    ctx.count("UA de navegador bloqueadas", (303, 312), (int(browser_k), int(browser_n)))
    ctx.compare("UA de navegador (%)", 97.1, float(browser_pct), 1)
    ctx.count("curl bloqueadas", (123, 312), (int(curl_k), int(curl_n)))
    ctx.compare("curl (%)", 39.4, float(curl_pct), 1)
    ctx.check("modo monitor, solo tráfico benigno", "solo benigno en modo `monitor`" in text)


def row_21(ctx):
    text = ctx.text("docs/limitations.md")
    for token in ("37/40", "92.5", "30/40"):
        if token in text:
            ctx.check(f"«{token}» en docs/limitations.md", True)
        else:
            ctx.unverified(f"«{token}» dvws-node", "la cifra no aparece en docs/limitations.md (solo se nombra dvws-node en la lista de apps)")


def row_22(ctx):
    files = latency_files(ctx)
    raw = [latency_run(files, "normal", "active", rep, suffix=".json")["aggregate"]["counters"] for rep in range(1, REPETITIONS + 1)]
    requests = [counters.get("http.requests", 0) for counters in raw]
    mean_requests = statistics.mean(requests)
    ctx.check(f"solicitudes por repetición ≈ 6 300 (media {mean_requests:.0f})", round(mean_requests, -2) == 6300, found=f"{mean_requests:.0f}")
    ctx.equal("bloqueos HTTP 403 en tráfico benigno (5 repeticiones)", 0, sum(counters.get("http.codes.403", 0) for counters in raw))


def row_23(ctx):
    skew = ctx.text(SKEW_TXT)
    rates = {m.group(1): float(m.group(2)) for m in re.finditer(r"^(\w+)\s+n=\s*\d+\s+UA>40:\s*([\d.]+)%", skew, re.M)}
    for name, claimed in (("xss", 33.3), ("cmdi", 54.4), ("path_traversal", 97.7), ("sqli", 81.7), ("benign", 0.4)):
        ctx.compare(f"UA>40 {name} (%) corpus completo", claimed, rates[name], 1)
    ctx.check("copia de _evidencia/ua-v6 idéntica al docs", ctx.text("_evidencia/ua-v6/corpus_ua_skew_docs_output.txt").split() == skew.split())
    audit = ctx.json("_evidencia/ua-v6/ua_length_audit.json")
    ctx.compare("benignos train + val con UA > 40 (%)", 0.36, audit["train+val"]["benign"]["pct_long"], 2)


def row_24(ctx):
    shap = ctx.json("training/results/shap_global_report.json")
    ctx.check("ua_length primera en benign", shap["benign"][0][0] == "ua_length")
    ctx.compare("SHAP ua_length benign", 0.0866, shap["benign"][0][1], 4)
    ctx.check("ua_length primera en sqli", shap["sqli"][0][0] == "ua_length")
    ctx.compare("SHAP ua_length sqli", 0.0734, shap["sqli"][0][1], 4)


def row_25(ctx):
    report = ctx.json("_evidencia/casi-duplicados/neardup_v2_results.json")
    for split, claimed in (("val", 59.61), ("test", 59.83), ("train_self", 59.63)):
        block = report[split]["ALL"]
        ctx.compare(f"{split}: con vecino J ≥ 0,8 (%)", claimed, block["any_ge_0.8"] / block["n"] * 100, 2)
    round5 = report["round5"]
    ctx.equal("Ronda 5 cmdi con vecino", 21, round5["cmdi"]["any_ge_0.8"])
    ctx.equal("Ronda 5 sqli con vecino", 0, round5["sqli"]["any_ge_0.8"])
    ctx.equal("Ronda 5 path con vecino", 0, round5["path_traversal"]["any_ge_0.8"])
    sample = report["lsh_recall_check_val_sample"]
    loss = (1 - sample["lsh_found_among_exact_ge"]["0.8"] / sample["exact_ge"]["0.8"]) * 100
    ctx.compare("pérdida del LSH a J = 0,8 (%)", 11, loss, 0)


def row_26(ctx):
    gap = ctx.json("_evidencia/casi-duplicados-v3/block_gap_counts.json")
    with_neighbour, without = gap["con_vecino_J>=0.8"], gap["sin_vecino_J>=0.8"]
    ctx.count("FP con vecino", (1, 4491), (with_neighbour["benign"]["k"], with_neighbour["benign"]["n"]))
    ctx.count("FP sin vecino", (15, 10396), (without["benign"]["k"], without["benign"]["n"]))
    gaps = [abs(with_neighbour[c]["rate"] - without[c]["rate"]) * 100 for c in ("cmdi", "path_traversal", "sqli", "xss")]
    ctx.check("máx. diferencia de recall ≤ 0,6 pp", max(gaps) <= 0.6, found=f"{max(gaps):.2f} pp")


def row_27(ctx):
    by_name = {s["source"]: s for s in ctx.json("_evidencia/loso-rf-v11/results.json")["sources"]}
    claims = (
        ("payload_full", "block_attack", 0.998, 0.737),
        ("seclists_cmdi", "block_attack", 1.000, 0.299),
        ("command_injection", "block_attack", 0.958, 0.563),
        ("modsec_learn", "fp_benign", 0.001, 0.760),
        ("xss_dataset", "fp_benign", 0.002, 0.945),
    )
    for source, metric, before, after in claims:
        entry = by_name[source]
        ctx.compare(f"{source} {metric}, rf_onnx", before, entry["a_rf_onnx"][metric]["p"], 3)
        ctx.compare(f"{source} {metric}, LOSO", after, entry["c_loso_val"][metric]["p"], 3)


def row_28(ctx):
    owasp = ctx.text("_evidencia/paquete-y-fuentes-v7/owasp_counts.txt")
    dedup = ctx.text("_evidencia/paquete-y-fuentes-v7/dedup_full.txt")
    rows = int(re.search(r"owasp_logs\.jsonl rows: (\d+)", owasp).group(1))
    exact_dups = int(re.search(r"dups: \{'owasp_logs': (\d+)\}", owasp).group(1))
    kept = ast.literal_eval(re.search(r"kept per source: (\{.*\})", dedup).group(1))["owasp_logs"]
    ctx.equal("owasp filas", 56399, rows)
    ctx.equal("owasp duplicados exactos", 52526, exact_dups)
    ctx.equal("owasp tras deduplicar", 3860, kept)
    ctx.equal("residuo (56 399 − 52 526 − 3 860)", 13, rows - exact_dups - kept)
    telemetry = ctx.text("_evidencia/paquete-y-fuentes-v7/telemetry_counts.txt")
    splits = {name: int(n) for name, n in re.findall(r"(train|val|test) mlops_telemetry_curated: (\d+)", telemetry)}
    ctx.equal("telemetría train/val/test", (82, 18, 19), (splits["train"], splits["val"], splits["test"]))
    ctx.equal("telemetría filas únicas", 119, int(re.search(r"unique _row_hash: (\d+)", telemetry).group(1)))
    ctx.check("telemetría de hosts simulados (sim-host-*)", "sim-host" in telemetry)


def row_29(ctx):
    new = ctx.json("_evidencia/query-v5/round5_wire_report.json")["new_vs_old"]
    ctx.equal("réplica n", 600, new["n"])
    ctx.equal("bloqueadas, lado izquierdo", 574, new["block_left"])
    ctx.equal("bloqueadas, lado derecho", 574, new["block_right"])
    ctx.equal("diferencias de características", 0, new["rows_with_any_feature_difference"])
    ctx.equal("cambios de clase", 0, new["rf_argmax_class_changed"])
    ctx.equal("cambios de decisión", 0, new["rf_block_decision_changed_T035"])
    ctx.check("commit 25c7e64 existe en logSguarDian", commit_exists(REPO_APP, "25c7e64"))


PLACEHOLDER_CATEGORY = "xss_placeholder"


def without_placeholder(entries, ctx):
    ctx.note(f"se excluye la entrada «{PLACEHOLDER_CATEGORY}_0» (placeholder de la ronda 5, no es un payload de los 600)")
    return [entry for entry in entries if entry["category"] != PLACEHOLDER_CATEGORY]


def row_30(ctx):
    for name, claimed in (("results_config3a-round5-20261010.json", (532, 600)), ("results_config3b-round5-20261010.json", (597, 600))):
        counts = blocked_counts(without_placeholder(ctx.json(COAUTOR + name), ctx))
        blocked = sum(k for k, _ in counts.values())
        total = sum(n for _, n in counts.values())
        ctx.count(name, claimed, (blocked, total))
    original = blocked_counts(without_placeholder(ctx.json(COAUTOR + "results_config2-published-0.1.1-20261010.json"), ctx))
    fixed = blocked_counts(without_placeholder(ctx.json(COAUTOR + "results_config2-published-0.1.1-harness-fixed-20261010.json"), ctx))
    for category, claimed in (("sqli", 199), ("path", 190), ("cmdi", 192)):
        ctx.count(f"0.1.1 arnés original, {category}", (claimed, 200), original[category])
    for category, claimed in (("sqli", 199), ("path", 200), ("cmdi", 185)):
        ctx.count(f"0.1.1 arnés corregido, {category}", (claimed, 200), fixed[category])
    ctx.check("commit 00ea3a3 existe en logSguarDian-vulnerable-project", commit_exists(REPO_VULN, "00ea3a3"))


def npm_pack_sha256(spec):
    if shutil.which("npm") is None:
        return None, "npm no disponible en este equipo"
    with tempfile.TemporaryDirectory() as directory:
        result = subprocess.run(["npm", "pack", spec, "--pack-destination", directory], capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            return None, result.stderr.strip().splitlines()[-1][:160] if result.stderr.strip() else "npm pack falló"
        tarball = next(Path(directory).glob("*.tgz"))
        return hashlib.sha256(tarball.read_bytes()).hexdigest(), ""


def row_31(ctx):
    hashes = dict(re.findall(r"(logsguardian@[\d.]+)\s+published\s+\S+\s+tgz sha256 ([0-9a-f]{64})", ctx.text("_evidencia/paquete-y-fuentes-v7/package_hashes.txt")))
    ctx.check("0.1.0 tgz c5c1a1da…80dcb0", hashes["logsguardian@0.1.0"].startswith("c5c1a1da") and hashes["logsguardian@0.1.0"].endswith("80dcb0"))
    ctx.check("0.1.1 tgz abf8d5c4…258d15", hashes["logsguardian@0.1.1"].startswith("abf8d5c4") and hashes["logsguardian@0.1.1"].endswith("258d15"))
    for spec in ("logsguardian@0.1.0", "logsguardian@0.1.1"):
        digest, error = npm_pack_sha256(spec)
        if digest is None:
            ctx.unverified(f"npm pack {spec}", error)
        else:
            ctx.check(f"npm pack {spec} = registro", digest == hashes[spec], found=digest[:12] + "…")


def row_32(ctx):
    v10 = ctx.json("_evidencia/query-v5/v10_test_results_dc2aaa6.json")
    ctx.compare("macro F1 rf_v10", 0.9787, v10["rf_v10_test_f1_macro"], 4)
    ctx.compare("recall IF v9", 0.9156, v10["if_v9_test_recall"], 4)
    ctx.compare("falsos positivos IF v9", 0.0516, v10["if_v9_test_fp_rate"], 4)


ROW_CHECKS = {number: function for number, function in enumerate(
    [row_01, row_02, row_03, row_04, row_05, row_06, row_07, row_08, row_09, row_10, row_11, row_12, row_13, row_14, row_15, row_16,
     row_17, row_18, row_19, row_20, row_21, row_22, row_23, row_24, row_25, row_26, row_27, row_28, row_29, row_30, row_31, row_32],
    start=1,
)}


def verify_row(number, cell, pages):
    ctx = Ctx()
    try:
        ROW_CHECKS[number](ctx)
    except Exception as error:
        ctx.unverified("cálculo", f"{type(error).__name__}: {error}")
    status = status_of(ctx.items)
    print(f"\n=== Fila {number} — {status}")
    print(f"  a) PDF: {pdf_report(pages, cell)}")
    print("  b) fuentes: " + ("; ".join(ctx.sources) if ctx.sources else "ninguna"))
    for item in ctx.items:
        mark = {True: "OK", False: "DIFERENTE", None: "NO VERIFICABLE"}[item.ok]
        if item.ok is None:
            print(f"  [{mark}] {item.label} · motivo: {item.reason}")
        else:
            print(f"  [{mark}] {item.label} · tabla: {item.claimed} · recalculado: {item.found}")
    for text in ctx.notes:
        print(f"  nota: {text}")
    print(f"  repetir: python3 {SCRIPT.relative_to(TESIS.parent)} --fila {number}")
    return status, ctx.sources[0] if ctx.sources else "—"


def main():
    parser = argparse.ArgumentParser(description="Verify the figures of TABLA_VERIFICACION_CIFRAS.md")
    parser.add_argument("--fila", type=int, choices=sorted(ROW_CHECKS), help="verify one row only")
    args = parser.parse_args()
    expected_hash = re.search(r"SHA-256 `([0-9a-f]{64})`", TABLA.read_text(encoding="utf-8")).group(1)
    actual_hash = hashlib.sha256(PDF.read_bytes()).hexdigest()
    print(f"PDF z-main.pdf SHA-256 {'coincide' if actual_hash == expected_hash else 'NO COINCIDE'} con la tabla ({actual_hash})")
    rows, pages = table_rows(), pdf_pages()
    numbers = [args.fila] if args.fila else sorted(ROW_CHECKS)
    summary = [(number, *verify_row(number, rows[number][1], pages)) for number in numbers]
    print("\n=== RESUMEN")
    for number, status, source in summary:
        print(f"{number:>3}  {status:<16} {source}")


if __name__ == "__main__":
    main()
