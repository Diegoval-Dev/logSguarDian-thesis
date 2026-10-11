## Tabla 1. LOSO, todas las filas de S (train+val), Wilson 95%

| fuente | n | n<200 | ataques | bloqueo ataques [IC] | benign | FP benign [IC] |
|---|---|---|---|---|---|---|
| capec | 181486 |  | 181486 | 0.960 [0.959, 0.961] | 0 | — |
| modsec_learn | 84698 |  | 25962 | 0.996 [0.996, 0.997] | 58736 | 0.753 [0.750, 0.757] |
| payload_full | 25262 |  | 9959 | 0.740 [0.731, 0.748] | 15303 | 0.003 [0.002, 0.003] |
| payloads_csv | 15650 |  | 10146 | 0.908 [0.902, 0.913] | 5504 | 0.266 [0.255, 0.278] |
| xss_dataset | 9226 |  | 6224 | 0.995 [0.993, 0.996] | 3002 | 0.949 [0.941, 0.957] |
| owasp_logs | 3280 |  | 3280 | 0.917 [0.907, 0.926] | 0 | — |
| seclists_cmdi | 2087 |  | 2087 | 0.288 [0.269, 0.308] | 0 | — |
| command_injection | 1745 |  | 401 | 0.509 [0.460, 0.557] | 1344 | 0.000 [0.000, 0.003] |
| synthetic_cmdi_minimal_context | 709 |  | 709 | 0.635 [0.599, 0.669] | 0 | — |
| synthetic_cmdi_compound | 425 |  | 425 | 1.000 [0.991, 1.000] | 0 | — |
| synthetic_nav | 357 |  | 0 | — | 357 | 0.739 [0.692, 0.782] |
| synthetic_cmdi_windows | 340 |  | 340 | 1.000 [0.989, 1.000] | 0 | — |
| synthetic_multifield | 210 |  | 210 | 0.905 [0.857, 0.938] | 0 | — |
| synthetic_nav_ecommerce | 113 | sí | 0 | — | 113 | 0.788 [0.703, 0.853] |
| mlops_telemetry_curated | 100 | sí | 100 | 0.970 [0.915, 0.990] | 0 | — |

## Tabla 2. S en val: (a) rf.onnx, (b) control aleatorio (media [min, máx] de 5 semillas), (c) LOSO

### capec (n_val=32028, filas en train removidas por control=149458)

| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |
|---|---|---|---|---|
| (a) rf.onnx | 32028 | 1.000 [1.000, 1.000] | — | cmdi=0.960 [0.942, 0.972] path_traversal=0.987 [0.981, 0.991] sqli=0.996 [0.995, 0.996] xss=0.951 [0.938, 0.961] |
| (b) control, 5 semillas | 32028 | 1.000 [1.000, 1.000] | — | cmdi=0.938 [0.932, 0.952] path_traversal=0.982 [0.980, 0.982] sqli=0.995 [0.995, 0.996] xss=0.949 [0.946, 0.953] |
| (c) LOSO | 32028 | 0.960 [0.958, 0.962] | — | cmdi=0.567 [0.529, 0.605] path_traversal=0.823 [0.807, 0.839] sqli=0.520 [0.514, 0.526] xss=0.013 [0.008, 0.020] |

### modsec_learn (n_val=14947, filas en train removidas por control=69751)

| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |
|---|---|---|---|---|
| (a) rf.onnx | 14947 | 0.998 [0.997, 0.999] | 0.001 [0.000, 0.001] | sqli=0.998 [0.997, 0.999] |
| (b) control, 5 semillas | 14947 | 0.998 [0.998, 0.998] | 0.001 [0.001, 0.001] | sqli=0.998 [0.998, 0.998] |
| (c) LOSO | 14947 | 0.997 [0.995, 0.998] | 0.760 [0.752, 0.768] | sqli=0.181 [0.170, 0.192] |

### payload_full (n_val=4459, filas en train removidas por control=20803)

| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |
|---|---|---|---|---|
| (a) rf.onnx | 4459 | 0.998 [0.994, 0.999] | 0.000 [0.000, 0.002] | cmdi=1.000 [0.610, 1.000] path_traversal=0.932 [0.818, 0.977] sqli=0.999 [0.997, 1.000] xss=0.988 [0.933, 0.998] |
| (b) control, 5 semillas | 4459 | 0.997 [0.997, 0.998] | 0.000 [0.000, 0.000] | cmdi=1.000 [1.000, 1.000] path_traversal=0.932 [0.932, 0.932] sqli=0.999 [0.999, 0.999] xss=0.982 [0.975, 0.988] |
| (c) LOSO | 4459 | 0.737 [0.716, 0.757] | 0.001 [0.000, 0.003] | cmdi=1.000 [0.610, 1.000] path_traversal=0.000 [0.000, 0.080] sqli=0.000 [0.000, 0.002] xss=0.650 [0.541, 0.745] |

### payloads_csv (n_val=2761, filas en train removidas por control=12889)

| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |
|---|---|---|---|---|
| (a) rf.onnx | 2761 | 0.998 [0.994, 0.999] | 0.004 [0.002, 0.011] | xss=0.997 [0.993, 0.998] |
| (b) control, 5 semillas | 2761 | 0.997 [0.996, 0.998] | 0.005 [0.004, 0.006] | xss=0.996 [0.995, 0.998] |
| (c) LOSO | 2761 | 0.906 [0.892, 0.919] | 0.270 [0.243, 0.299] | xss=0.877 [0.860, 0.891] |

### xss_dataset (n_val=1628, filas en train removidas por control=7598)

| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |
|---|---|---|---|---|
| (a) rf.onnx | 1628 | 0.990 [0.982, 0.994] | 0.002 [0.000, 0.011] | xss=0.990 [0.982, 0.994] |
| (b) control, 5 semillas | 1628 | 0.991 [0.991, 0.993] | 0.000 [0.000, 0.000] | xss=0.991 [0.991, 0.993] |
| (c) LOSO | 1628 | 0.993 [0.986, 0.996] | 0.945 [0.923, 0.962] | xss=0.991 [0.983, 0.995] |

### owasp_logs (n_val=578, filas en train removidas por control=2702)

| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |
|---|---|---|---|---|
| (a) rf.onnx | 578 | 0.990 [0.978, 0.995] | — | cmdi=0.890 [0.817, 0.936] path_traversal=0.962 [0.934, 0.978] sqli=0.929 [0.874, 0.961] xss=0.600 [0.357, 0.802] |
| (b) control, 5 semillas | 578 | 0.994 [0.993, 0.995] | — | cmdi=0.879 [0.862, 0.899] path_traversal=0.957 [0.952, 0.962] sqli=0.939 [0.936, 0.943] xss=0.613 [0.600, 0.667] |
| (c) LOSO | 578 | 0.915 [0.890, 0.935] | — | cmdi=0.092 [0.051, 0.161] path_traversal=0.808 [0.761, 0.848] sqli=0.887 [0.824, 0.929] xss=0.400 [0.198, 0.643] |

### seclists_cmdi (n_val=368, filas en train removidas por control=1719)

| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |
|---|---|---|---|---|
| (a) rf.onnx | 368 | 1.000 [0.990, 1.000] | — | cmdi=1.000 [0.990, 1.000] |
| (b) control, 5 semillas | 368 | 1.000 [1.000, 1.000] | — | cmdi=1.000 [1.000, 1.000] |
| (c) LOSO | 368 | 0.299 [0.254, 0.348] | — | cmdi=0.280 [0.236, 0.328] |

### command_injection (n_val=308, filas en train removidas por control=1437)

| modelo | n | bloqueo ataques [IC] | FP benign [IC] | recall por clase [IC] |
|---|---|---|---|---|
| (a) rf.onnx | 308 | 0.958 [0.883, 0.986] | 0.000 [0.000, 0.016] | cmdi=0.915 [0.828, 0.961] |
| (b) control, 5 semillas | 308 | 0.952 [0.944, 0.972] | 0.000 [0.000, 0.000] | cmdi=0.924 [0.915, 0.930] |
| (c) LOSO | 308 | 0.563 [0.448, 0.673] | 0.000 [0.000, 0.016] | cmdi=0.352 [0.251, 0.468] |

Control: quita de train tantas filas aleatorias como filas tiene S en train (semillas 1-5); RF random_state=42 fijo.

## Tabla 3. payload_full, filas sqli (train+val, n=9224), modelo LOSO

| clase predicha (argmax) | filas | % de sqli [IC] | bloqueadas/predichas [IC] |
|---|---|---|---|
| benign | 2378 | 0.258 [0.249, 0.267] | 0.000 [0.000, 0.002] |
| cmdi | 6846 | 0.742 [0.733, 0.751] | 0.994 [0.992, 0.996] |
| path_traversal | 0 | 0.000 [0.000, 0.000] | — |
| sqli | 0 | 0.000 [0.000, 0.000] | — |
| xss | 0 | 0.000 [0.000, 0.000] | — |

## Verificación: LOSO repetido en origin/develop vs corrida anterior (35b7a28)

| fuente | bloqueo ataques anterior | nuevo | FP anterior | nuevo |
|---|---|---|---|---|
| capec | 0.9599969143625403 | 0.9599969143625403 | None | None |
| modsec_learn | 0.9964563592943533 | 0.9964563592943533 | 0.7534220920730046 | 0.7534220920730046 |
| payload_full | 0.7399337282859725 | 0.7399337282859725 | 0.002548519898059204 | 0.002548519898059204 |
| payloads_csv | 0.9077468953282082 | 0.9077468953282082 | 0.2663517441860465 | 0.2663517441860465 |
| xss_dataset | 0.9950192802056556 | 0.9950192802056556 | 0.9493670886075949 | 0.9493670886075949 |
| owasp_logs | 0.9167682926829268 | 0.9167682926829268 | None | None |
| seclists_cmdi | 0.2879731672256828 | 0.2879731672256828 | None | None |
| command_injection | 0.5087281795511222 | 0.5087281795511222 | 0.0 | 0.0 |
| synthetic_cmdi_minimal_context | 0.6346967559943583 | 0.6346967559943583 | None | None |
| synthetic_cmdi_compound | 1.0 | 1.0 | None | None |
| synthetic_nav | None | None | 0.7394957983193278 | 0.7394957983193278 |
| synthetic_cmdi_windows | 1.0 | 1.0 | None | None |
| synthetic_multifield | 0.9047619047619048 | 0.9047619047619048 | None | None |
| synthetic_nav_ecommerce | None | None | 0.7876106194690266 | 0.7876106194690266 |
| mlops_telemetry_curated | 0.97 | 0.97 | None | None |
