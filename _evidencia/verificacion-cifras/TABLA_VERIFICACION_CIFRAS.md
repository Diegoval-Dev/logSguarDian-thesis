# Tabla de verificación de cifras: logSguarDian

Estado: 13 de octubre de 2026. PDF de referencia: `z-main.pdf`, SHA-256 `b0e77e56b42d03d9dfed9f6de8c820087b09591b9a87de7414fd8bc81017cc40`.

## Cómo usarla (por cada fila)

1. **Explícala con tus palabras**, sin mirar la fuente: qué mide, en qué condiciones y qué no demuestra.
2. **Compruébala:** el script `verificar_cifras.py` recalcula la cifra desde su fuente y dice OK o DIFERENTE. Si hay una diferencia, no la corrijas a mano: avísame con la fila.
3. **Marca** `[x]` en "comprobada" cuando el script dé OK y en "explicada" cuando puedas contestar la columna "Debes poder explicar" sin leerla.
4. Las filas que no puedas explicar son las que estudias primero para la defensa.

Rutas: `_evidencia/` está en el repo `tesis`. `training/`, `docs/`, `packages/`, `benchmarks/` son de `logSguarDian` (`origin/main`, o `develop` si la nota lo dice). `attack-sim/` y `docs/evidence/` son de `logSguarDian-vulnerable-project` (`main`).

## Modelo, extractor y corpus

| # | Cifra y valor | Dónde en la tesis | Fuente | Debes poder explicar | Comprobada | Explicada |
|---|---|---|---|---|---|---|
| 1 | Extractor: p95 mixto con `worker_threads` = **0.0273 ms** (límite 5 ms) | Resultados VIII.1, Cuadro 7; Conclusiones | `benchmarks/results/extractor-*.json` (tres corridas del 9-oct, mediana) | Es el extractor **en aislamiento**; no incluye inferencia, registro ni red. El sobrecosto real del middleware es de unos 12 ms | [ ] | [ ] |
| 2 | RF: macro F1 **0.9776**; F1 de `cmdi` **0.9239** | Cuadro 9; Resumen | `training/results/v11_test_results.json` | Se calcula por **argmax**, sin el umbral 0.35, sobre el conjunto de prueba leído 3 veces. `cmdi` es la clase más débil | [ ] | [ ] |
| 3 | IF: recall **0.9125**; falsos positivos **0.0546** | Cuadro 10 | `training/results/v11_test_results.json` | IF solo marca; no bloquea. Cumple los criterios (≥ 50 % y ≤ 10 %) | [ ] | [ ] |
| 4 | Paridad scikit-learn / ONNX: **1.01 × 10⁻⁷** (RF) y **2.42 × 10⁻⁷** (IF) | Cuadro 11 | `training/models/parity_report.json` | Por qué importa: si el modelo en Node difiere del de Python, las métricas no describen lo que corre | [ ] | [ ] |
| 5 | Vector de **76** características; RF usa **69** e IF **63** | Alcance; Metodología VII.3 | `docs/feature-spec.md` (76 filas); `packages/core/src/worker.ts` líneas 61-101 | Qué se excluye: 5 temporales, `status_code`, `non_json_quote_count` (y 6 más en IF). Frase de roles: Sebastián hizo 72; tú añadiste 4 | [ ] | [ ] |
| 6 | Corpus: **383 202** filas, **17** fuentes; **268 240 / 57 481 / 57 481** | Metodología VII.4 | `training/splits/*.parquet` (no versionados; SHA-256 en los anexos); `_evidencia/loso-rf-v11/source_counts.txt` (train + val = 325 721) | Nueve conjuntos o listas públicas, siete generadores propios, una fuente de telemetría simulada | [ ] | [ ] |
| 7 | Conjunto de prueba leído **3 veces** (24, 25 y 26-sep); macro F1 0.9843 y luego 0.9776 | Metodología VII.4; Limitaciones | commits `3086318`, `fc47a5b`, `03de50f`; `training/results/v11_test_results.json` | **R2 no se cumplió.** Qué cambió entre lecturas (umbral de IF 0.00807 → 0.00421) y por qué las cifras se reportan con esa salvedad | [ ] | [ ] |
| 8 | Lock vigente `7486c258…4fd9` con **57 481** filas; el de v10 era `6c5f253d…` con **57 308** | Anexo XIII.3 | `_evidencia/query-v5/lock_history.md`; 57 308 = suma de los `support` de `_evidencia/query-v5/v10_test_results_dc2aaa6.json` (14 866 + 1 328 + 2 527 + 34 103 + 4 484); `training/splits/test.lock.sha256` | El lock es un hash de los `_row_hash` ordenados. No consta el motivo de 57 308 → 57 481 | [ ] | [ ] |

## Umbral e Isolation Forest (solo validación)

| # | Cifra y valor | Dónde en la tesis | Fuente | Debes poder explicar | Comprobada | Explicada |
|---|---|---|---|---|---|---|
| 9 | Barrido de T: estable entre 0.30 y 0.40 (**0.0067 pp** en bloqueo benigno, **0.056 pp** en recall) | Anexo XIII.1; Discusión | `_evidencia/revalidacion-umbral-if/analysis_out.txt` (sección 1) | **Estabilidad, no optimalidad:** con recall ≈ 99.9 % la validación casi no distingue entre 0.20 y 0.40. El criterio lo fijaste tú antes de mirar, sin registro | [ ] | [ ] |
| 10 | RF deja pasar **39** de 42 594 ataques; IF marca **19**; regla "RF o IF" suma **866** benignos (bloqueo benigno 0.107 → **5.925 %**) | Anexo XIII.1; Conclusiones | `_evidencia/revalidacion-umbral-if/analysis_out.txt` (sección 2) | Por qué IF solo registra: 19 ataques extra frente a 866 falsos positivos. Cifras optimistas (el umbral de IF se eligió en la misma validación) | [ ] | [ ] |
| 11 | IF marca **874** de 14 887 benignos; con User-Agent, **67 de 69** (97.1 %) | Anexo XIII.1 | `_evidencia/revalidacion-umbral-if/ua_check_regenerado_out.txt` | Por qué un login normal sale anómalo: `ua_length`, `method_is_post`, `ua_present` y `content_type_encoded` son raros en el corpus benigno | [ ] | [ ] |

## Evaluación integral

| # | Cifra y valor | Dónde en la tesis | Fuente | Debes poder explicar | Comprobada | Explicada |
|---|---|---|---|---|---|---|
| 12 | Ronda 4 (590 payloads): Config 2 **583/590** (98.8 %); WAF solo **550/590** (93.2 %); en capas **587/590** (99.5 %); logSguarDian atrapó **37 de 40** | Cuadro 15; Discusión; Conclusiones | `docs/config3b-results.md` (Round 4), repo de la app | `cmdi` 200/200 **coincide con el entrenamiento**: no es generalización. Se ejecutó con el par A | [ ] | [ ] |
| 13 | Ronda 5, par C (tarball de validación `cf1238…`; trae los mismos modelos que el tgz de 0.1.1, `abf8d5c4…`, con bytes distintos): sqli **199**, path **190**, cmdi **192** de 200 (99.5 / 95.0 / 96.0 %) | Cuadro 17 | `attack-sim/results_config2-develop-tarball-20261009.json` (app) | Es la evidencia casi sin solapamiento (cmdi 21/200 con vecino). Bloqueado = solo HTTP 403 | [ ] | [ ] |
| 14 | Ronda 5, par A (tarball `e09120…`): **200 / 170 / 183**; Wilson de path **79.4–89.3 %** | Cuadro 17; Discusión | `attack-sim/results_config2.json` (app, commit `a3aada0`) | Por qué el límite inferior de 79.4 % queda bajo el criterio del 80 %. El tarball no es el del registro | [ ] | [ ] |
| 15 | XSS: **97.3 %** (110/113) en los 590 payloads; ZAP: **1/1** (n = 1), 538 alertas | Cuadro 15; anexo XIII.8.1 | `docs/config3b-results.md`; `_evidencia/coautor-ronda5-v10/zap-xss-report.json` y `zap-alerts-full.json` | Sin corpus limpio no hay verificación independiente; un caso no alcanza para decir "cumple" el 80 % | [ ] | [ ] |

## Rendimiento

| # | Cifra y valor | Dónde en la tesis | Fuente | Debes poder explicar | Comprobada | Explicada |
|---|---|---|---|---|---|---|
| 16 | Δp95: **12.08 ms** (normal) y **12.85 ms** (ataque) | VIII.3.2; Conclusiones; Cuadro 21 | `docs/evidence/latency-linux-2026-09-26.tgz` (run 36276690236, app) | Mediana de las 5 repeticiones (la tesis lo declara en VIII.3.2; con la media daría 12.31). Una corrida, 2 vCPU, par B, cinco repeticiones. Cumple el criterio de 15 ms con 2-3 ms de margen | [ ] | [ ] |
| 17 | Volumen: Δp95 **6 495.46 ms**; **7.00 %** de timeouts (1 824 de 26 048) | VIII.3.2 | mismo `.tgz` | Mediana de las 5 repeticiones (con la media daría 6 431.30). No cumple. Los timeouts no entran al p95, así que la cifra subestima la cola | [ ] | [ ] |
| 18 | Memoria: **+331.9 / +332.0 / +375.9 MiB** (ataque / normal / volumen) | Cuadro 18 | `docs/evidence/resources_summary.json` (app) | Criterio del protocolo: 150 MB ≈ 143 MiB; no cumple. Es el contenedor completo, sin atribuir a un componente | [ ] | [ ] |
| 19 | CPU: **+529.6 % / +614.4 % / +40.1 %** | Cuadro 18 | `docs/evidence/resources_summary.json` | Criterio: 15 %; no cumple. 100 % equivale a un núcleo | [ ] | [ ] |

## Falsos positivos y User-Agent

| # | Cifra y valor | Dónde en la tesis | Fuente | Debes poder explicar | Comprobada | Explicada |
|---|---|---|---|---|---|---|
| 20 | Juice Shop: **303/312** (97.1 %) con UA de navegador; **123/312** (39.4 %) con `curl` | VIII.3.7; Cuadro 21 | `docs/limitations.md` líneas 787-799 (librería) | Modo **`monitor`**, solo tráfico benigno: "veredicto de bloqueo", no se bloqueó nada. Par C | [ ] | [ ] |
| 21 | dvws-node: **37/40** (92.5 %) con UA de navegador; con el UA de Node **30/40** (75 %) | VIII.3.7 | **PENDIENTE: la fuente no consta en `docs/limitations.md` ni en ningún doc revisado; buscar en `docs/vulnerable-projects-tests/` y en las ramas** | Modo `block`. El modelo exacto de esa medición **no consta** | [ ] | [ ] |
| 22 | Artillery: **0** bloqueos benignos en **6 300** solicitudes por repetición | VIII.3.2 | `docs/evidence/latency-linux-2026-09-26.tgz` | Par B. El UA de Artillery es corto y no se parece a un navegador | [ ] | [ ] |
| 23 | UA largo (> 40 caracteres) en **0.4 %** de las filas benignas (train + val: **0.36 %**); xss 33.3 %, cmdi 54.4 %, sqli 81.7 %, path 97.7 % | VIII.3.9 (SHAP); anexo XIII.4 | `_evidencia/ua-v6/ua_length_audit.json`; `docs/findings-evidence/juice-shop-ua-bias/output/` | Por qué es un sesgo del corpus benigno: el modelo aprendió que "UA largo = ataque" | [ ] | [ ] |
| 24 | SHAP: `ua_length` es la 1.ª característica en `benign` (0.0866) y `sqli` (0.0734) | Cuadro 19 | `training/results/shap_global_report.json` | Cómo se lee un valor SHAP global; por qué `cmdi` es el caso débil (`method_is_get`, `ua_length`) | [ ] | [ ] |

## Particiones y generalización

| # | Cifra y valor | Dónde en la tesis | Fuente | Debes poder explicar | Comprobada | Explicada |
|---|---|---|---|---|---|---|
| 25 | ≈ **60 %** de val, test y train tiene un vecino con J ≥ 0.8 (**59.61 / 59.83 / 59.63 %**); Ronda 5: `cmdi` **21/200**, sqli y path **0** | Anexo XIII.2; Discusión | `_evidencia/casi-duplicados/neardup_v2_results.json` | Qué es un casi-duplicado (MinHash, shingles de 3, J = 0.8). Son cotas inferiores: el LSH pierde ≈ 11 % a 0.8 | [ ] | [ ] |
| 26 | Con vecino frente a sin vecino en val: FP **1/4 491** frente a **15/10 396**; diferencias de recall ≤ **0.6 pp** | Anexo XIII.2.3 | `_evidencia/casi-duplicados-v3/block_gap_counts.json` | Los casi-duplicados inflan **poco** las métricas de val; n pequeño en FP; no es causalidad | [ ] | [ ] |
| 27 | LOSO (config. de `rf_v11`): bloqueo `payload_full` **0.998 → 0.737**, `seclists_cmdi` **1.000 → 0.299**, `command_injection` **0.958 → 0.563**; FP `modsec_learn` **0.001 → 0.760**, `xss_dataset` **0.002 → 0.945** | Anexo XIII.5; Discusión | `_evidencia/loso-rf-v11/results.json` | El control de mismo tamaño no reproduce las caídas: depende de la fuente, no del tamaño. Es un modelo por fold, no el `rf.onnx` | [ ] | [ ] |
| 28 | `owasp_logs`: **56 399 → 3 860** (52 526 duplicados + 13); telemetría **119** filas (82 / 18 / 19), **simulada** | Anexo XIII.5 | `_evidencia/paquete-y-fuentes-v7/dedup_full.txt`, `owasp_counts.txt`, `telemetry_counts.txt` | 56 399 − 52 526 − 13 = 3 860. La telemetría no es tráfico real; la curación fue manual y sin criterio escrito | [ ] | [ ] |

## Query, paquetes y evaluaciones del coautor

| # | Cifra y valor | Dónde en la tesis | Fuente | Debes poder explicar | Comprobada | Explicada |
|---|---|---|---|---|---|---|
| 29 | Réplica de la query: **574/600** bloqueadas con ambas derivaciones, **0** diferencias de características, clase o decisión | Anexo XIII.6 | `_evidencia/query-v5/round5_wire_report.json` | El fix `25c7e64` es posterior a todas las evaluaciones y no cambia la Ronda 5 (codificada con `quote_plus`). El desajuste con el entrenamiento **no se midió** | [ ] | [ ] |
| 30 | Coautor: 3a **532/600**, 3b **597/600**; 0.1.1 con arnés original **199 / 190 / 192**, con arnés corregido **199 / 200 / 185** | Anexo XIII.8 | `_evidencia/coautor-ronda5-v10/results_*.json` (cuenta solo HTTP 403) | El 200/200 de path se debe al cambio del arnés (`00ea3a3`), no al fix de la query; es optimista. Ninguna de las dos variantes entrega los 200 de cmdi | [ ] | [ ] |
| 31 | `logsguardian@0.1.0`: tgz `c5c1a1da…80dcb0`, par A; `@0.1.1`: tgz `abf8d5c4…258d15`, par C | Cuadro 5 (notas); anexo XIII.6 | `npm pack logsguardian@0.1.0` y `@0.1.1`; `_evidencia/paquete-y-fuentes-v7/package_hashes.txt` | Qué modelos, umbral de IF y construcción de la query trae cada versión. Ninguna evaluación de integración del capítulo 8 usó el tgz del registro | [ ] | [ ] |
| 32 | `rf_v10`/`if_v9` (otra partición, 57 308 filas): macro F1 **0.9787** (0.97869); IF recall **0.91556**, FP **0.05159** | Anexo XIII.7; Conclusiones | `_evidencia/query-v5/v10_test_results_dc2aaa6.json` | Cumple el OE2 con la generación de ese momento; no es comparable con `rf_v11` por ser otra partición | [ ] | [ ] |

## Frases que sostienen la defensa (para memorizar, no se verifican con script)

- Las métricas miden separación **dentro del corpus**; la evidencia fuera de él es la Ronda 5 y los falsos positivos en aplicaciones de terceros.
- IF registra, no bloquea: 866 benignos por cada 19 ataques extra.
- El umbral 0.35 es estable entre 0.30 y 0.40, no demostrado óptimo.
- Latencia: cumple en carga normal y de ataque; no en volumen. Memoria y CPU no cumplen.
- Path traversal con 0.1.1: 190/200 con el arnés original y 200/200 con el corregido; la diferencia es del arnés.


## Resultado del script (13-oct-2026)

`verificar_cifras.py` (SHA-256 `d4b3a851e802682529dd3afe5a0a15187f76d4c6a73aa1679d3cdb188f929944`) dio **28 OK, 1 DIFERENTE y 3 NO VERIFICABLE**. Salida: `resultado.txt` (SHA-256 `e58a98fd432a6fa17f73161f8097f6045097e7a0047aa1b5b8bc152ede75cb72`).

| Fila | Estado | Qué significa |
|---|---|---|
| 13 | DIFERENTE | Falsa alarma: el script comparó el nombre del `.tgz`. `cf1238…` (tarball de validación) y `abf8d5c4…` (0.1.1 del registro) tienen los mismos modelos y bytes distintos. Las cifras 199/190/192 sí coinciden. Ya reescrita la fila |
| 5 | NO VERIFICABLE | La autoría (72 de Sebastián, 4 tuyas) es una afirmación tuya, no un dato de un archivo. 76/69/63 sí dieron OK |
| 8 | NO VERIFICABLE | 57 308 no es un campo: es la suma de los soportes de `v10_test_results.json`. Hash y 57 481 sí dieron OK |
| 21 | NO VERIFICABLE | **Hallazgo real:** 37/40, 92.5 % y 30/40 de dvws-node no están en ninguna fuente revisada. Aparecen en el Resumen y en las Conclusiones |

Notas del script: las filas 16 y 17 usan la mediana (así lo declara la tesis); la fila 30 excluye el marcador `xss_placeholder_0`; en la fila 1 se usa `ns.p95`, no el campo redondeado.