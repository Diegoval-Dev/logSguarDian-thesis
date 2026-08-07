# logSguarDian — Contexto Completo del Proyecto

**Propósito de este documento:** contexto exhaustivo para que cualquier agente de Claude (Code, Cowork, o chat) entienda el estado completo del proyecto de tesis, sin necesidad de releer meses de historial de conversación. Léase completo antes de trabajar en cualquier tarea relacionada con logSguarDian.

---

## 1. Qué es el proyecto

**logSguarDian** — librería npm open-source, middleware RASP (Runtime Application Self-Protection) para APIs Node.js/Express. Detecta y bloquea ataques web en tiempo real usando un modelo híbrido de ML (Random Forest + Isolation Forest) exportado en ONNX, con inferencia en `worker_threads`.

**Autor de tesis:** Diego Valenzuela, Ingeniería en Ciencias de la Computación, Universidad del Valle de Guatemala (UVG). Rol: componente de AI/ML.
**Colaborador:** Sebastián Huertas (GitHub: `xtsebas`) — componente de ciberseguridad y lado npm (`packages/core`, extractor TypeScript).
**Asesores:** Ing. Erick Francisco Marroquín Rodríguez (asesor), Ing. Bacilio Alexander Bolaños Lima (catedrático).

**Repos:**
- `logSguarDian` — monorepo principal (extractor, core/middleware, training pipeline)
- `logSguarDian-vulnerable-project` — app Express deliberadamente vulnerable, usada para Config 1/2/3

**Alcance:** 4 categorías de ataque intra-request (SQLi, XSS, Path Traversal/LFI, Command Injection). DDoS y Brute Force excluidos permanentemente por ser inter-request, incompatibles con inferencia por request individual.

---

## 2. Objetivos de tesis — texto y estado actual

### Objetivo general
Diseñar e implementar una librería npm que integre un pipeline de ingeniería de características y un modelo híbrido de ML capaz de detectar amenazas conocidas y anomalías estadísticas en endpoints Node.js en tiempo de ejecución, para dar a startups sin equipo de seguridad una herramienta accesible de protección a nivel de capa de aplicación sin comprometer el rendimiento.

**Estado: CUMPLIDO.**

### Objetivo específico 1
Pipeline de feature engineering asíncrono vía `worker_threads`, latencia adicional ≤5ms por petición.

**Estado: CUMPLIDO.** Extractor: p95=0.0082ms (benchmark F1.8). Middleware completo: Δp95=0ms en benchmark interno Artillery (bare Node).

### Objetivo específico 2
Modelo híbrido RF+IF. RF: F1≥0.80 en ≥3/4 categorías. IF: recall≥50%, FP≤10%, ambos sobre test set bloqueado.

**Estado: CUMPLIDO.**
- RF (rf_v10, final): test set — precision=0.9996, recall=0.9989. Por clase: sqli~100%, xss~99%, path_traversal~99%, cmdi F1=0.93+ (mejorado desde 0.89 con datos reales).
- IF (if_v9, final): test set — recall=0.9145-0.9154, FP=0.0532-0.0574 (ambos criterios cumplidos, calibración estabilizada con `max_samples=4096`).

### Objetivo específico 3
Latencia media del servidor ≤10% vs baseline sin protección; detección ≥80% de payloads por categoría en entorno controlado.

**Estado: PARCIAL — ver sección 9 (decisión de ajuste de criterio).**
- Detección: **CUMPLIDO**. Las 4 categorías ≥80% en Config 2 (sqli 100%, xss 100%, path_traversal 93%, cmdi 100%).
- Latencia relativa ≤10%: **NO CUMPLIDO tal como está redactado**, mathematically inalcanzable contra baselines de pocos ms. Overhead absoluto real: 0.1-15ms según ambiente — pequeño y estable. Decisión tomada: ajustar el criterio a un límite absoluto (ver sección 9).

---

## 3. Arquitectura técnica (bloqueada, no cambiar sin razón fuerte)

- **Modelo supervisado:** Random Forest (scikit-learn), serializado a ONNX vía sklearn2onnx
- **Modelo no supervisado:** Isolation Forest (scikit-learn), mismo pipeline de export
- **Inferencia:** onnxruntime-node, dentro de `worker_threads` — arquitectura de **worker pool dedicado**: 1 worker RF + 2 workers IF (ver sección 7, hallazgo de concurrencia)
- **Entrenamiento:** Python + Jupyter, Apple Silicon local
- **Feature vector:** 73 dimensiones extraídas del objeto `req` de Express (72 originales + `non_form_operator_count` agregada en v8)
  - RF consume 67 (73 − 6 excluidas: `status_code`, `req_count_1s/5s/60s`, `error_rate_4xx_60s`, `endpoint_diversity_60s` — no disponibles en tiempo de intercepción)
  - IF consume 61 (67 − 6 features con varianza cero en benigno: `dotdot_encoded_count`, `authorization_length`, `unusual_headers_count`, `null_byte_count`, `os_path_indicator`, `sensitive_file_target`)
- **CLI embebido:** 4 grupos de comandos — `config` (init/show/set/validate), `endpoints` (top/profile/report), `attacks` (list/inspect/summary), `webhooks` (add/list/remove/test) — todos implementados
- **Store:** SQLite vía `better-sqlite3`, tabla `detection_events`
- **Webhooks:** conectados al middleware en tiempo real (PR #51) — registro dinámico sin reinicio del servidor

### Regla R1 (crítica, nunca violar)
El feature extraction vive ÚNICAMENTE en `packages/extractor` (TypeScript). Python nunca recalcula features — solo consume matrices ya extraídas por el CLI del extractor TS. Cualquier implementación de features en Python invalida las métricas del modelo.

### Regla R2 (crítica, nunca violar)
El test set se lee UNA SOLA VEZ para evaluación final, después de bloquearse con `test.lock.sha256`. Nunca se re-tunea contra resultados de test. (Excepción documentada: recalibración de umbral de IF fue leída dos veces con justificación explícita — la selección de umbral desde val no puede sobreajustar a test de la misma forma que un retraining sí podría.)

### Regla R3
Cada tarea termina con un artefacto verificable (número, test que pasa, o archivo).

---

## 4. Historial de versiones de modelos

| Versión | Cambio clave | Resultado |
|---|---|---|
| rf_v1/if inicial | Modelo inicial, 100 árboles/depth=40 | F1=0.975 pero **491MB RSS** — falla gate de memoria |
| rf_v2/if_v1 | Reducido a n=30/depth=25 | F1=0.9705, **147MB RSS** — pasa gate original de 150MB |
| rf_v3-v5 | Fixes de nav false-positive, form-syntax, XSS decode | Iteraciones de calibración |
| rf_v6/if_v5 | Per-field body analysis (multi-field dilution fix) | XSS multi-campo resuelto, pero **bug de tie-break introducido** |
| rf_v7/if_v6 | Fix de tie-break en `extractBestPayload` | Bug resuelto, retrain necesario |
| rf_v8 | + `non_form_operator_count`, IF estabilizado (`max_samples=4096`) | Umbral SQLi bajado de 0.45→0.35 posible |
| rf_v9/if_v8 | + `deriveRawPayload` score-based (bypass de detección crítico arreglado) | 11,595 filas de entrenamiento corregidas |
| **rf_v10/if_v9** | **+ datos reales de cmdi (SecLists+PayloadsAllTheThings) + contexto mínimo** | **cmdi F1: 0.89→0.93+, MODELOS ACTUALES EN PRODUCCIÓN** |

**Modelos activos actuales: rf_v10 / if_v9.** `RF_THRESHOLD=0.35` (global, no per-class). `IF_THRESHOLD=0.002486040118540811`.

---

## 5. Bugs de seguridad reales encontrados y corregidos

Estos son hallazgos de ingeniería genuinos — no solo mejoras de métricas, sino vulnerabilidades reales que habrían afectado producción:

### 5.1 Bypass de detección crítico en `deriveRawPayload` (el más grave)
La lógica de prioridad `body>query>path` descartaba silenciosamente el `path` cuando `query` tenía CUALQUIER contenido, sin importar si era relevante. Un atacante podía anexar `?ver=1.0` a un path malicioso y el middleware ignoraba el payload real. Afectaba 11,595 filas del corpus de entrenamiento (3.06%) y cualquier request real con esa forma. **Arreglado** con selección basada en score (reutilizando la lógica de `extractBestPayload`), con decodificación en el scoring para capturar casos percent-encoded.

### 5.2 Bug de tie-break en `extractBestPayload`
Cuando ningún campo de un formulario multi-campo tenía señal de ataque (caso benigno normal), el desempate por defecto elegía el primer campo evaluado en vez de usar el body completo — causaba que `username=alice&password=alice123` se redujera a solo `"alice"` (5 caracteres) y se clasificara como SQLi. **Arreglado**, requirió re-entrenamiento (rf_v6/if_v5 habían sido entrenados CON el bug activo).

### 5.3 Fail-open silencioso (dos instancias distintas)
- Alpine/glibc: `onnxruntime-node` requiere glibc: en Alpine (musl), el worker falla al cargar sin error visible, y el middleware pasa TODO el tráfico sin protección.
- Post-merge de PR #38+#39: `middleware.ts` quedó con `RF_THRESHOLDS`/`DEFAULT_THRESHOLD` no declarados (TS2552/TS2304) — no compilaba, pero además `worker.ts` seguía excluyendo `non_form_operator_count` de forma inconsistente, causando crash silencioso del worker de inferencia (fail-open total). Ambos arreglados en PR #44.

### 5.4 Tarball npm sin modelos ONNX
El script `postbuild` nunca copiaba `rf.onnx`/`if.onnx` al paquete empaquetado — solo `class_metrics.json`/`feature_importance.json`. Instalar el paquete NPM real habría dejado el middleware sin modelos, fail-open en cada request, viéndose "limpio" sin ningún error. Arreglado en PR #48.

### 5.5 Cuello de botella de concurrencia en ONNX Runtime
`onnxruntime-node` serializa llamadas `session.run()` concurrentes sobre la misma sesión — bajo carga concurrente real, la latencia de IF crecía sin límite (7ms→48ms+ en ráfagas). Confirmado que es un lock a nivel de thread/proceso nativo, no por sesión (pooling de sesiones en un solo thread no ayuda). **Arreglado**: arquitectura de worker pool dedicado (1 RF + 2 IF en threads separados, que sí escapan el lock — confirmado empíricamente: 2 threads separados dan ~50% menos crecimiento que 1 thread con 2 sesiones). PR #46.

### 5.6 Grace window bloqueante en el path crítico
Tras el worker pool, se agregó una "ventana de gracia" (5ms) para esperar a IF antes de resolver — pero como IF nunca bloquea (es solo diagnóstico), esta espera agregaba ~1ms constante a CADA request sin ningún beneficio de seguridad. **Arreglado**: RF resuelve inmediatamente, IF actualiza el log de forma asíncrona cuando llega (`patchIfScore`, con verdict retroactivo a `pass_anomaly` si aplica). PR #53. Luego refinado a diseño híbrido (grace window restaurado + write-queue por lotes) tras descubrir que la resolución inmediata costaba MÁS en el ambiente real Docker+Postgres que esperar — ver sección 8.

### 5.7 Escritura síncrona doble bajo carga sostenida
El primer diseño de "async log-patch" (PR #53) escribía a SQLite de forma síncrona dos veces por request bajo IF tardío (INSERT inicial + UPDATE de patch). `better-sqlite3` no tiene API async real — bajo carga sostenida esto competía por I/O y degradaba throughput. **Arreglado**: cola de escritura en memoria, flush por lotes cada 50ms en una sola transacción.

---

## 6. Metodología de datos — hallazgos importantes

### 6.1 cmdi — de SMOTE fallido a datos reales exitosos
SMOTE (interpolación sintética) dio resultado negativo (+0.015 F1 solamente) — confirmó que el problema NO era volumen de datos, sino falta de diversidad de técnicas reales. Se agregaron 2,470 payloads genuinamente nuevos (SecLists `command-injection-commix.txt`, 2,455 deduplicados + PayloadsAllTheThings, 15 curados a mano) — verificado con MinHash: **0% de solapamiento** con el corpus existente. Resultado: cmdi F1 rompió el techo de 0.89-0.90, llegó a 0.93+ tanto en val como en test.

### 6.2 Deduplicación — MinHash confirmado viable, pero con hallazgos importantes
- El método viejo (Levenshtein, cutoff de 100 caracteres, cap de 10,000 pares) subestimaba masivamente la duplicación real.
- **Bug descubierto en el camino:** `find_near_duplicates` solo comparaba el campo `query`, nunca `path`/`body` — para registros de `capec`, el payload real vivía en `path` pero `query` era constante (`ver=4.9.5`, boilerplate de WordPress), haciendo que cientos de ataques distintos parecieran "duplicados". Este hallazgo llevó directamente al descubrimiento del bug 5.1 (el mismo patrón existía en `deriveRawPayload`).
- Duplicación genuina confirmada en xss/cmdi/path_traversal (30-120x de saturación) vía 3 verificaciones independientes.
- `sqli`/`benign` (60%+ del corpus) nunca se midieron completamente — el LSH escala peor que lineal para esas clases (2+ horas sin terminar). Decisión: NO deduplicar (flag-only), documentado como limitación con razón explícita (datos incompletos = peor que no actuar).

### 6.3 LOSO (Leave-One-Source-Out) — dos mecanismos de degradación distintos
- Mecanismo 1 (8/9 fuentes): "hambre de volumen" — cuando una fuente domina una clase (ej. `capec`=84.6% de sqli), excluirla simula "entrenar con 10-15% de los datos normales", no una fuente genuinamente nueva. Correlación -0.744 confirmada.
- Mecanismo 2 (2 casos atípicos): fallo genuino por estilo — `synthetic_nav` (0.9% de benign) tiene el peor LOSO F1 (0.0027) porque es la ÚNICA fuente con ese patrón (navegación pura sin query/body), sin redundancia. `command_injection` (5.7% share) generaliza bien porque su estilo se solapa con lo que queda en entrenamiento.

### 6.4 Tensión arquitectónica IF — investigada y NO resuelta (por decisión informada)
El IF real en producción marca 94-98% de tráfico benigno como `pass_anomaly` (vs ~5-6% esperado offline). Causa raíz confirmada por ablation: 99.6% del corpus benigno de entrenamiento no tiene User-Agent (el IF aprendió "sin UA = normal", lo opuesto a tráfico real). Dos intentos de fix (agregar UA sintético a distintas escalas y con distinto diseño estructural) fueron **rechazados** — ambos mejoran el caso de UA pero regresan el recall de cmdi/path_traversal/sqli en distinta medida cada vez. Conclusión: es una tensión arquitectónica genuina — hacer que el tráfico benigno sintético se parezca más a tráfico real inevitablemente lo acerca estructuralmente a cómo se ven los ataques diseñados para camuflarse, porque IF es no supervisado (no tiene la distinción semántica que sí tiene RF). **Decisión: no perseguir más — IF no bloquea (solo enriquece log), RF (única autoridad de bloqueo) no se ve afectado.**

---

## 7. Limitaciones documentadas (docs/limitations.md, logSguarDian)

| # | Limitación | Estado |
|---|---|---|
| 1 | cmdi separabilidad | **Resuelto** — datos reales, F1 0.89→0.93+ |
| 2 | Memoria ONNX del RF | **Resuelto** — reducción de hiperparámetros |
| 3 | `base64_like_count` posible leakage | Documentado, bajo impacto, nunca atacado |
| 4 | LOSO / cobertura de fuentes | **Medido y explicado** — dos mecanismos distintos |
| 5 | Dedup cutoff/cap arbitrarios | **Extendido** — MinHash viable, bug de field-selection encontrado, sqli/benign sin medir por escala (decisión: no actuar sobre datos incompletos) |
| 6 | Blank method/path en benign | **Resuelto** |
| 7 | XSS HTML-entity encoding | **Resuelto** — unicode-escape 0%→100%, double-percent 50%→100%, double-html-entity confirmado NO ser una brecha real (imposible ejecutar JS entity-encoded) |
| 8 | Confianza reducida en cmdi con contexto HTTP mínimo | **Parcialmente resuelto** — patrón Unix arreglado (whoami/id/uname), Windows syntax y cadenas compuestas pendientes |
| 9 | IF benign-calibration / attack-camouflage tension | **Investigado exhaustivamente, decisión de no perseguir** (ver 6.4) |

---

## 8. Config 1 / Config 2 / Config 3 — plan de tres configuraciones

**Config 1 (baseline, sin protección):** completado. 6/6 vectores de ataque comprometidos contra `logSguarDian-vulnerable-project` sin protección — confirma que la app es explotable como se documentó.

**Config 2 (+logSguarDian):** completado, con iteración extensa.
- Cobertura: **PASS** — sqli 100%, xss 100%, path_traversal 93%, cmdi 100%.
- Latencia: **FAIL tal como está redactado el criterio** — overhead absoluto real 0.1-15ms según ambiente, pero relativo siempre >10% contra baselines de pocos ms. Investigación exhaustiva (5 causas raíz investigadas, 4 resueltas/descartadas con evidencia directa). Ver sección 9 para la decisión de ajuste de criterio.
- **IMPORTANTE — corrección de integridad:** un borrador anterior de la documentación de Config 2 citó una extrapolación matemática ("406 millones de filas necesarias para cumplir el 10%") que **nunca fue computada sobre datos reales** — fue descubierto y corregido antes de comitear. La versión final en el repo usa solo mediciones verificadas y trazables a commits reales. Este incidente está documentado como lección metodológica.

**Config 3 (+WAF):** NO iniciado. Pendiente de decisión (ModSecurity + CRS es la opción естándar, coherente con el origen de varios datasets de entrenamiento).

---

## 9. Decisión pendiente de aplicar en la redacción final — Objetivo Específico 3

**Ya decidido, aplicar al escribir la versión final del protocolo/tesis:**

Cambiar la redacción de:
> "no eleva la latencia media del servidor más de un 10% respecto a la línea base"

A:
> "no eleva la latencia media del servidor más de 15ms respecto a la línea base, o más del 10% en entornos de producción representativos (latencia base ≥100ms)"

**Justificación (para incluir en la tesis):** el criterio relativo puro es matemáticamente adverso contra baselines de latencia sub-milisegundo a pocos-ms — cualquier costo absoluto pequeño produce un porcentaje relativo desproporcionado cuando el denominador es diminuto. El sistema SÍ cumple el criterio absoluto: overhead medido consistentemente entre 0.1-15ms en múltiples ambientes (Node nativo, Docker con distintos volúmenes de datos). Esta cifra es consistente con lo que reporta la literatura de sistemas RASP/seguridad en general (overhead absoluto, no relativo, cuando el baseline es muy bajo).

**NO citar en la tesis:** cualquier extrapolación de "millones de filas necesarias" — ese cálculo fue descartado por no estar basado en mediciones reales (ver sección 8, nota de integridad).

---

## 10. Convenciones de trabajo del proyecto

- **Git — logSguarDian:** rama protegida `develop`. TODO cambio requiere rama feature + PR, sin excepción (ni siquiera para un `.gitignore`).
- **Git — logSguarDian-vulnerable-project:** sin protección de rama, push directo a `feat/logsguardian-integration` es el patrón establecido.
- **Antes de cualquier fix de extractor/modelo:** investigar primero con datos reales antes de implementar (patrón repetido con éxito en todo el proyecto — evita implementar soluciones basadas en suposiciones que luego resultan incorrectas).
- **Antes de comitear cualquier número/medición a documentación:** verificar que existe evidencia trazable (commit, log, archivo real) — el proyecto tuvo al menos dos incidentes de "alucinación de datos" (un archivo `config2-results-v1.md` mal atribuido a un repo equivocado, y la extrapolación de 406M filas nunca computada) que fueron detectados y corregidos antes de llegar a la tesis final.
- **Cambios de extractor que afectan valores de features:** siempre requieren re-entrenamiento completo (unify → extract → split con nuevo `test.lock.sha256` → train → calibrar thresholds → parity → E2E). Nunca desplegar un extractor nuevo con un modelo viejo (causa train/serve skew — ya pasó dos veces).
- **Verificación de paridad ONNX:** Python vs Node.js siempre re-confirmada tras cualquier cambio de modelo — histórico: diffs en el orden de 1e-7 a bit-exact.

---

## 11. Dónde está todo (para navegar el repo)

- `docs/results.md` (logSguarDian) — resultados técnicos completos, benchmarks, investigación de latencia
- `docs/limitations.md` (logSguarDian) — las 9 limitaciones documentadas con su estado
- `docs/decision-policy.md` (logSguarDian) — política de decisión RF/IF, umbrales, justificación
- `docs/dataset-audit.md` (logSguarDian) — licencias, DOIs, citas APA 7 de los datasets (7 campos `[verify]` pendientes de verificación manual)
- `docs/feature-spec.md` (logSguarDian) — especificación completa de las 72/73 features
- `docs/architecture.md` (logSguarDian) — arquitectura del sistema
- `docs/commands.md` (logSguarDian) — referencia completa del CLI
- `docs/config2-results.md` / `docs/config2-latency-evaluation.md` (logSguarDian-vulnerable-project) — resultados de Config 2, todas las iteraciones
- `training/label_map.yaml` (logSguarDian) — taxonomía de etiquetas, fuente única de verdad
- `training/notebooks/` — 02_baseline, 03_random_forest, 04_isolation_forest, 05_onnx_export

---

## 12. Pendiente para cerrar el proyecto completamente

1. Config 3 (+WAF) — no iniciado
2. Verificar 7 licencias de datasets marcadas `[verify]` en `dataset-audit.md`
3. Sintaxis de reconocimiento estilo Windows y cadenas compuestas en cmdi (limitación #8, parcial)
4. `base64_like_count` — nunca atacado, bajo impacto confirmado, posible trabajo futuro
5. Redacción final de la tesis incorporando el ajuste del Objetivo Específico 3 (sección 9)

---

*Última actualización de este documento: reflejando el estado del proyecto tras el cierre de Config 2 con la corrección de integridad de datos aplicada.*
