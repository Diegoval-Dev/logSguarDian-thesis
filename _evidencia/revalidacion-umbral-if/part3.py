import json
import numpy as np
import onnxruntime as ort
import pyarrow.parquet as pq

REPO = "/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian"
IF_THRESHOLD = 0.004205941820353609
EXCLUDED = {"status_code", "req_count_1s", "req_count_5s", "req_count_60s",
            "error_rate_4xx_60s", "endpoint_diversity_60s", "non_json_quote_count"}
IF_EXTRA = {"dotdot_encoded_count", "authorization_length", "unusual_headers_count",
            "null_byte_count", "os_path_indicator", "sensitive_file_target"}

login = json.load(open("/tmp/lg_work/login_vec.json"))
ext_names, ext_vec = login["names"], login["vec"]
rf_names = [n for n in ext_names if n not in EXCLUDED]
if_names = [n for n in rf_names if n not in IF_EXTRA]
assert len(if_names) == 63
login_by_name = dict(zip(ext_names, ext_vec))

sess = ort.InferenceSession(f"{REPO}/training/models/if.onnx", providers=["CPUExecutionProvider"])
out_name = sess.get_outputs()[1].name
def if_score(x63):
    x = np.asarray(x63, dtype=np.float32).reshape(1, 63)
    return float(sess.run([out_name], {sess.get_inputs()[0].name: x})[0].reshape(-1)[0])

table = pq.read_table(f"{REPO}/training/splits/val.parquet")
labels = np.array(table.column("label").to_pylist())
benign = labels == "benign"
val_cols = {n: np.asarray(table.column(n).to_numpy(zero_copy_only=False), dtype=np.float64) for n in if_names}
X_if_val = np.stack([val_cols[n] for n in if_names], axis=1).astype(np.float32)

base_x = [login_by_name[n] for n in if_names]
base_score = if_score(base_x)
print(f"login IF score: {base_score:.6f} (expected ~ -0.159), anomaly: {base_score < IF_THRESHOLD}")

med = {n: float(np.median(val_cols[n][benign])) for n in if_names}
rows = []
for i, n in enumerate(if_names):
    x = list(base_x)
    x[i] = med[n]
    s = if_score(x)
    rows.append((s - base_score, n, login_by_name[n], med[n], s))
rows.sort(reverse=True)
print("\nTop 10 substitutions that most RAISE the score (toward normal):")
print(f"{'delta':>10} {'feature':<28} {'login':>12} {'benign_median':>14} {'new_score':>12}")
for d, n, lv, mv, s in rows[:10]:
    print(f"{d:10.6f} {n:<28} {lv:12.4f} {mv:14.4f} {s:12.6f}")
print("\nLargest decreases (for context):")
for d, n, lv, mv, s in rows[-3:]:
    print(f"{d:10.6f} {n:<28} {lv:12.4f} {mv:14.4f} {s:12.6f}")
all_med = if_score([med[n] for n in if_names])
print(f"\nall 63 replaced by benign medians: score {all_med:.6f}, anomaly: {all_med < IF_THRESHOLD}")

print("\n== 3c. benign validation rows ==")
Bmask = benign
is_post = val_cols["method_is_post"] == 1
ct = val_cols["content_type_encoded"] == 1
body_len = val_cols["body_length"] > 0
flag = np.asarray(sess.run([out_name], {sess.get_inputs()[0].name: X_if_val})[0]).reshape(-1) < IF_THRESHOLD
print(f"benign rows: {Bmask.sum()}, IF flag rate: {flag[Bmask].mean()*100:.3f}%")
print("method_is_post x content_type_encoded (benign):")
for p in (False, True):
    for c in (False, True):
        m = Bmask & (is_post == p) & (ct == c)
        if m.sum():
            print(f"  post={int(p)} ct_form={int(c)}: n={m.sum():6d} ({m.sum()/Bmask.sum()*100:6.2f}%) flag_rate={flag[m].mean()*100:7.3f}%")
pf = Bmask & is_post & ct
print(f"POST with form content-type (benign): {pf.sum()} = {pf.sum()/Bmask.sum()*100:.3f}% of benign")
pfb = pf & body_len
print(f"  of which body_length>0: {pfb.sum()} = {pfb.sum()/Bmask.sum()*100:.3f}% of benign; flag rate {flag[pfb].mean()*100:.3f}%" if pfb.sum() else "  none with body")
print(f"all benign POST (any ct): {(Bmask & is_post).sum()}")
print("content_type_encoded values in val:", np.unique(val_cols["content_type_encoded"]))
print("method_is_post values in val:", np.unique(val_cols["method_is_post"]))
