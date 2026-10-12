import importlib.util
from collections import Counter
from pathlib import Path

REPO = Path("/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian")
spec = importlib.util.spec_from_file_location("unify_mod", REPO / "training" / "unify.py")
unify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unify)

all_records = unify.load_all_records(unify.DATA_CLEAN)
kept, dups = unify.deduplicate_exact(all_records)
print("raw total:", len(all_records), "kept:", len(kept))
print("kept per source:", dict(Counter(src for src, _ in kept)))
print("dups per source:", dict(dups))

owasp_raw = [r for r in all_records if r[0] == "owasp_logs"]
seen_before = set()
cross = 0
for src, rec in all_records:
    if src == "owasp_logs":
        break
    seen_before.add(unify.fingerprint(rec))
cross = sum(1 for src, rec in owasp_raw if unify.fingerprint(rec) in seen_before)
print("owasp rows whose fingerprint appears in an earlier-sorted source:", cross)
