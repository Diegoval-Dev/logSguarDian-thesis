import json, hashlib
import numpy as np
import onnxruntime as ort
import pyarrow.parquet as pq

REPO = "/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian"
MODELS = f"{REPO}/training/models"
VAL = f"{REPO}/training/splits/val.parquet"
RF_CLASSES = ["benign", "cmdi", "path_traversal", "sqli", "xss"]
RF_THRESHOLD_CURRENT = 0.35
IF_THRESHOLD = 0.004205941820353609
EXCLUDED = {"status_code", "req_count_1s", "req_count_5s", "req_count_60s",
            "error_rate_4xx_60s", "endpoint_diversity_60s", "non_json_quote_count"}
IF_EXTRA = {"dotdot_encoded_count", "authorization_length", "unusual_headers_count",
            "null_byte_count", "os_path_indicator", "sensitive_file_target"}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def load_val():
    t = pq.read_table(VAL)
    return t

def feature_matrix(table, names):
    cols = [np.asarray(table.column(n).to_numpy(zero_copy_only=False), dtype=np.float32) for n in names]
    return np.stack(cols, axis=1)

def main():
    print("rf sha256:", sha256(f"{MODELS}/rf.onnx"))
    print("if sha256:", sha256(f"{MODELS}/if.onnx"))
    parity = json.load(open(f"{MODELS}/parity_report.json"))
    print("parity_report threshold_if:", parity.get("threshold_if"))

    table = load_val()
    n = table.num_rows
    labels = np.array(table.column("label").to_pylist())
    print("rows:", n)
    feature_names = [c for c in table.schema.names if c not in
                     {"sample_id", "label", "timestamp", "_source", "_row_hash"}]
    print("feature columns:", len(feature_names))

    rf_names = [c for c in feature_names if c not in EXCLUDED]
    if_names = [c for c in rf_names if c not in IF_EXTRA]
    print("RF features:", len(rf_names), "IF features:", len(if_names))
    assert len(rf_names) == 69 and len(if_names) == 63

    rf_sess = ort.InferenceSession(f"{MODELS}/rf.onnx", providers=["CPUExecutionProvider"])
    if_sess = ort.InferenceSession(f"{MODELS}/if.onnx", providers=["CPUExecutionProvider"])
    rf_out = rf_sess.get_outputs()[1].name
    if_out = if_sess.get_outputs()[1].name
    print("rf input:", rf_sess.get_inputs()[0].name, rf_sess.get_inputs()[0].shape, "output[1]:", rf_out)
    print("if input:", if_sess.get_inputs()[0].name, if_sess.get_inputs()[0].shape, "output[1]:", if_out)

    X_rf = feature_matrix(table, rf_names)
    X_if = feature_matrix(table, if_names)
    rf_probs = np.asarray(rf_sess.run([rf_out], {rf_sess.get_inputs()[0].name: X_rf})[0], dtype=np.float32)
    if_scores = np.asarray(if_sess.run([if_out], {if_sess.get_inputs()[0].name: X_if})[0], dtype=np.float32).reshape(-1)
    np.savez("/tmp/lg_work/scores.npz", rf_probs=rf_probs, if_scores=if_scores, labels=labels)

    pred_idx = rf_probs.argmax(axis=1)
    pred = np.array(RF_CLASSES)[pred_idx]
    conf = rf_probs.max(axis=1)
    attack_mask = labels != "benign"
    benign_mask = labels == "benign"
    attack_classes = ["sqli", "xss", "path_traversal", "cmdi"]

    print("\n== 1. RF threshold sweep ==")
    print(f"{'T':>5} {'benign_block%':>14} {'recall_global%':>15} " +
          " ".join(f"{c+'%':>14}" for c in attack_classes))
    sweep = {}
    for T in np.round(np.arange(0.20, 0.9001, 0.05), 2):
        blocked = (pred != "benign") & (conf >= T)
        bb = blocked[benign_mask].mean() * 100
        rg = blocked[attack_mask].mean() * 100
        per = {c: blocked[labels == c].mean() * 100 for c in attack_classes}
        sweep[float(T)] = (bb, rg, per)
        print(f"{T:5.2f} {bb:14.3f} {rg:15.3f} " + " ".join(f"{per[c]:14.3f}" for c in attack_classes))

    b30, r30 = sweep[0.30][0], sweep[0.30][1]
    b40, r40 = sweep[0.40][0], sweep[0.40][1]
    print(f"\nStability T=0.30 vs 0.40: |d benign_block|={abs(b30-b40):.4f} pp, |d recall_global|={abs(r30-r40):.4f} pp")
    print("Criterion (<0.5 pp both):", abs(b30-b40) < 0.5 and abs(r30-r40) < 0.5)

    print("\n== 2. IF contribution at T=0.35 ==")
    rf_blocked = (pred != "benign") & (conf >= RF_THRESHOLD_CURRENT)
    if_anom = if_scores < IF_THRESHOLD
    passed_attack = attack_mask & ~rf_blocked
    print(f"RF-passed attacks: {passed_attack.sum()} of {attack_mask.sum()}")
    print("IF flags among RF-passed attacks, total:", (passed_attack & if_anom).sum())
    for c in attack_classes:
        m = passed_attack & (labels == c)
        print(f"  {c}: RF-passed={m.sum()} IF-flagged={(m & if_anom).sum()}")
    passed_benign = benign_mask & ~rf_blocked
    print(f"(b) benign passed by RF: {passed_benign.sum()}; IF-flagged (cost): {(passed_benign & if_anom).sum()}")
    print(f"  as % of all benign: {(passed_benign & if_anom).sum() / benign_mask.sum() * 100:.3f}%")

    or_blocked = rf_blocked | if_anom
    print("(c) RF only vs RF OR IF:")
    print(f"  attack recall: RF={rf_blocked[attack_mask].mean()*100:.3f}%  OR={or_blocked[attack_mask].mean()*100:.3f}%")
    print(f"  benign block: RF={rf_blocked[benign_mask].mean()*100:.3f}%  OR={or_blocked[benign_mask].mean()*100:.3f}%")
    extra = benign_mask & or_blocked & ~rf_blocked
    print(f"  extra benign blocked by IF: {extra.sum()}")
    print(f"  IF-only extra attacks caught: {(attack_mask & or_blocked & ~rf_blocked).sum()}")

if __name__ == "__main__":
    main()
