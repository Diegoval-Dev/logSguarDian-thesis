# logSguarDian — Contexto Completo del Proyecto
 
**Propósito de este documento:** contexto exhaustivo para que cualquier agente de Claude (Code, Cowork, o chat) entienda el estado completo del proyecto de tesis, sin necesidad de releer meses de historial de conversación. Léase completo antes de trabajar en cualquier tarea relacionada con logSguarDian.
 
**Última reescritura completa:** consolidación tras auditoría de estado real (ver sección 20). Antes de esta versión, el documento tenía numeración de secciones desordenada por ediciones incrementales acumuladas — se reescribió completo en vez de parchear una vez más.
 
---
 
## 1. Qué es el proyecto
 
**logSguarDian** — librería npm open-source, middleware RASP (Runtime Application Self-Protection) para APIs Node.js/Express. Detecta y bloquea ataques web en tiempo real usando un modelo híbrido de ML (Random Forest + Isolation Forest) exportado en ONNX, con inferencia en `worker_threads`.
 
**Autor de tesis:** Diego Valenzuela, Ingeniería en Ciencias de la Computación, Universidad del Valle de Guatemala (UVG). Rol: componente de AI/ML.
**Colaborador:** Sebastián Huertas (GitHub: `xtsebas`) — componente de ciberseguridad y lado npm (`packages/core`, extractor TypeScript).
**Asesores:** Ing. Erick Francisco Marroquín Rodríguez (asesor), Ing. Bacilio Alexander Bolaños Lima (catedrático).
 
**Repos:**
- `logSguarDian` — monorepo principal (extractor, core/middleware, training pipeline, `packages/mlops`). **⚠️ El repo se movió de organización: ahora vive en `logSguarDian2026/logSguarDian` (antes `xtsebas/logSguarDian`). Verificar `git remote -v` al iniciar cualquier sesión — el remoto `origin` puede seguir apuntando a la URL vieja si el checkout es anterior a la migración.**
- `logSguarDian-vulnerable-project` — app Express deliberadamente vulnerable, usada para Config 1/2/3
**Alcance:** 4 categorías de ataque intra-request (SQLi, XSS, Path Traversal/LFI, Command Injection). DDoS y Brute Force excluidos permanentemente por ser inter-request, incompatibles con inferencia por request individual.
 
**Fecha de defensa estimada:** noviembre 2026.
 
---
 
## 2. Objetivos de tesis — texto y estado actual
 
### Objetivo general
Diseñar e implementar una librería npm que integre un pipeline de ingeniería de características y un modelo híbrido de ML capaz de detectar amenazas conocidas y anomalías estadísticas en endpoints Node.js en tiempo de ejecución, para dar a startups sin equipo de seguridad una herramienta accesible de protección a nivel de capa de aplicación sin comprometer el rendimiento.
 
**Estado: CUMPLIDO.**
 
### Objetivo específico 1
Pipeline de feature engineering asíncrono vía `worker_threads`, latencia adicional ≤5ms por petición.
 
**Estado: CUMPLIDO.** Extractor: p95=0.0082ms. Middleware completo: overhead absoluto 0.1-15ms según ambiente (ver sección 9 sobre el ajuste de criterio de latencia).
 
### Objetivo específico 2
Modelo híbrido RF+IF. RF: F1≥0.80 en ≥3/4 categorías. IF: recall≥50%, FP≤10%, ambos sobre test set bloqueado.
 
**Estado: CUMPLIDO.**
- RF (rf_v11, actual): test set — precision=0.9996, recall=0.9989. Por clase: sqli~100%, xss~99%, path_traversal~99%, cmdi F1=0.93+ (mejorado desde 0.89 con datos reales, luego reforzado con cobertura Windows/compound).
- IF (if_v10, actual): test set — recall=0.9145-0.9154, FP=0.0532-0.0574 (ambos criterios cumplidos, calibración estabilizada con `max_samples=4096`).
### Objetivo específico 3
Detección ≥80% de payloads por categoría en entorno controlado; latencia sin elevar la media del servidor más de 15ms respecto a la línea base (criterio ajustado, ver sección 9), o más del 10% en entornos de producción representativos (latencia base ≥100ms).
 
**Estado: CUMPLIDO tras ajuste de criterio.**
- Detección: **CUMPLIDO**. Las 4 categorías ≥80% en Config 2 y Config 3b — ver sección 8 para el resultado principal (corpus de 590 payloads).
- Latencia: overhead absoluto real 0.1-15ms según ambiente — dentro del criterio ajustado. **Pendiente:** aplicar formalmente el veredicto en la redacción de la tesis (ver Frente 1 del roadmap, sección 21).
---
 
## 3. Arquitectura técnica (bloqueada, no cambiar sin razón fuerte)
 
- **Modelo supervisado:** Random Forest (scikit-learn), serializado a ONNX vía sklearn2onnx
- **Modelo no supervisado:** Isolation Forest (scikit-learn), mismo pipeline de export
- **Inferencia:** onnxruntime-node, dentro de `worker_threads` — arquitectura de **worker pool dedicado**: 1 worker RF + pool de 2 workers IF (round-robin)
- **Entrenamiento:** Python + Jupyter, Apple Silicon local
- **Feature vector: 75 dimensiones actuales** extraídas del objeto `req` de Express (73 base + `non_form_operator_count` desde v8 + `distinct_shell_command_count`/`shell_to_path_ratio` desde v11)
  - **RF consume 69** (75 − 6 excluidas: `status_code`, `req_count_1s/5s/60s`, `error_rate_4xx_60s`, `endpoint_diversity_60s` — no disponibles en tiempo de intercepción)
  - **IF consume 63** (69 − 6 features con varianza cero en benigno: `dotdot_encoded_count`, `authorization_length`, `unusual_headers_count`, `null_byte_count`, `os_path_indicator`, `sensitive_file_target`)
  - ⚠️ **Riesgo activo confirmado (sección 20):** `docs/api.md`, `docs/decision-policy.md`, y `docs/architecture.md` todavía citan conteos viejos (73/67/61 o incluso 72/66) — desactualizados respecto al real 75/69/63. Máxima prioridad de corrección, ver Frente 1 del roadmap.
- **CLI embebido:** 4 grupos de comandos — `config` (init/show/set/validate), `endpoints` (top/profile/report), `attacks` (list/inspect/summary), `webhooks` (add/list/remove/test) — todos implementados
- **Store:** SQLite vía `better-sqlite3`, tabla `detection_events`
- **Webhooks:** conectados al middleware en tiempo real (PR #51) — registro dinámico sin reinicio del servidor
- **`packages/mlops`:** pipeline de Continuous Training de 8 fases, infraestructura separada del middleware npm (ver sección 15) — **tiene una regresión real activa**, ver sección 20
### Regla R1 (crítica, nunca violar)
El feature extraction vive ÚNICAMENTE en `packages/extractor` (TypeScript). Python nunca recalcula features — solo consume matrices ya extraídas por el CLI del extractor TS. Cualquier implementación de features en Python invalida las métricas del modelo.
 
### Regla R2 (crítica, nunca violar)
El test set se lee UNA SOLA VEZ para evaluación final, después de bloquearse con `test.lock.sha256`. Nunca se re-tunea contra resultados de test. (Excepción documentada: recalibración de umbral de IF fue leída dos veces con justificación explícita en algunos ciclos — la selección de umbral desde val no puede sobreajustar a test de la misma forma que un retraining sí podría.)
 
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
| rf_v10/if_v9 | + datos reales de cmdi (SecLists+PayloadsAllTheThings) + contexto mínimo | cmdi F1: 0.89→0.93+ |
| **rf_v11/if_v10** | **+ cobertura Windows/compound-command en cmdi (2 features nuevas), corrección §10 (RF también afectado por UA), integración `synthetic_nav_ecommerce`** | **MODELOS ACTUALES EN PRODUCCIÓN — 75 features totales, 69 (RF)/63 (IF)** |
 
**Modelos activos actuales: rf_v11 / if_v10.** `RF_THRESHOLD=0.35` (global, no per-class). Verificar `IF_THRESHOLD` actual contra `parity_report.json` antes de citarlo — ha cambiado en cada retrain de IF.
 
---
 
## 5. Bugs de seguridad reales encontrados y corregidos
 
Hallazgos de ingeniería genuinos — no solo mejoras de métricas, sino vulnerabilidades reales que habrían afectado producción:
 
### 5.1 Bypass de detección crítico en `deriveRawPayload` (el más grave del proyecto)
La lógica de prioridad `body>query>path` descartaba silenciosamente el `path` cuando `query` tenía CUALQUIER contenido, sin importar relevancia. Un atacante podía anexar `?ver=1.0` a un path malicioso y el middleware ignoraba el payload real. Afectaba 11,595 filas del corpus de entrenamiento (3.06%) y cualquier request real con esa forma. **Arreglado** con selección basada en score (reutilizando la lógica de `extractBestPayload`), con decodificación en el scoring para capturar casos percent-encoded.
 
### 5.2 Bug de tie-break en `extractBestPayload`
Cuando ningún campo de un formulario multi-campo tenía señal de ataque (caso benigno normal), el desempate por defecto elegía el primer campo evaluado en vez de usar el body completo — causaba que `username=alice&password=alice123` se redujera a solo `"alice"` (5 caracteres) y se clasificara como SQLi. **Arreglado**, requirió re-entrenamiento (rf_v6/if_v5 habían sido entrenados CON el bug activo).
 
### 5.3 Fail-open silencioso (dos instancias distintas)
- Alpine/glibc: `onnxruntime-node` requiere glibc: en Alpine (musl), el worker falla al cargar sin error visible, y el middleware pasa TODO el tráfico sin protección.
- Post-merge de PR #38+#39: `middleware.ts` quedó con `RF_THRESHOLDS`/`DEFAULT_THRESHOLD` no declarados (TS2552/TS2304) — no compilaba, pero además `worker.ts` seguía excluyendo `non_form_operator_count` de forma inconsistente, causando crash silencioso del worker de inferencia (fail-open total). Ambos arreglados en PR #44.
### 5.4 Tarball npm sin modelos ONNX
El script `postbuild` nunca copiaba `rf.onnx`/`if.onnx` al paquete empaquetado — solo `class_metrics.json`/`feature_importance.json`. Instalar el paquete NPM real habría dejado el middleware sin modelos, fail-open en cada request, viéndose "limpio" sin ningún error. Arreglado en PR #48.
 
### 5.5 Cuello de botella de concurrencia en ONNX Runtime
`onnxruntime-node` serializa llamadas `session.run()` concurrentes sobre la misma sesión — bajo carga concurrente real, la latencia de IF crecía sin límite (7ms→48ms+ en ráfagas). Confirmado que es un lock a nivel de thread/proceso nativo, no por sesión. **Arreglado**: arquitectura de worker pool dedicado (1 RF + 2 IF en threads separados, que sí escapan el lock). PR #46.
 
### 5.6 Grace window bloqueante en el path crítico — historia completa
Tras el worker pool, se agregó una "ventana de gracia" (5ms) para esperar a IF antes de resolver — pero como IF nunca bloquea, esta espera agregaba ~1ms constante a CADA request sin beneficio de seguridad. Se eliminó (PR #53): RF resuelve inmediatamente, IF actualiza el log de forma asíncrona (`patchIfScore`). **Luego se descubrió que esto empeoraba las cosas en el ambiente real Docker+Postgres** (contención de Postgres + costo fijo de inferencia hacían que esperar fuera más rápido que no esperar). Se probó un diseño híbrido (grace window restaurado + write-queue por lotes) como experimento, pero **quedó sin fusionar a `develop`** (rama `experiment/grace-window-plus-write-queue`, commit `65e4a79`).
**Estado real confirmado en la auditoría (sección 20): el diseño actualmente en `develop` es async-patch puro, SIN grace window.** No citar el diseño híbrido como el estado actual — fue un experimento, no lo que está en producción.
 
### 5.7 Escritura síncrona doble bajo carga sostenida
El primer diseño de "async log-patch" (PR #53) escribía a SQLite de forma síncrona dos veces por request bajo IF tardío. `better-sqlite3` no tiene API async real — bajo carga sostenida esto competía por I/O. **Arreglado**: cola de escritura en memoria, flush por lotes cada 50ms en una sola transacción.
 
### 5.8 Bug de ordenamiento multipart + XSS almacenado real (Config 3b)
`logsguardian` montado antes del parseo multipart (multer montado por ruta, corría después). Cualquier request `multipart/form-data` llegaba con `req.body={}`, pasando de largo sin importar el contenido del ataque. Confirmado como vulnerabilidad XSS almacenado explotable (payloads sin escapar persistidos directamente en Postgres). **Arreglado** con parser multipart global montado antes de logSguarDian. Encontrado durante investigación de Config 3b Round 3, no durante desarrollo normal.
 
### 5.9 Dos bugs colaterales sin arreglar (fuera de alcance deliberado, pendientes de seguimiento)
1. `SHELL_COMMAND_COUNT`'s `\b` anchor nunca puede coincidir antes de `/etc/passwd` o `/bin/` cuando hay un espacio precediendo — esas alternativas del regex son código muerto en payloads realistas. Preexistente, no arreglado.
2. `extractBestPayload` fragmenta bodies crudos en `&`/`&&` literales como límites de campo de `URLSearchParams` — un comando compuesto real usando `&&` como separador de shell podría fragmentarse antes de llegar al modelo. Mitigado en datos sintéticos (percent-encoding en un solo campo), mecanismo del extractor no tocado. Posible vector de evasión real en producción, sin investigar a fondo.
### 5.10 Regresión activa en `packages/mlops` (confirmada en auditoría, sección 20)
`POST /telemetry` devuelve 400 en vez de 201 — 4/10 tests fallando ahora mismo. No es flakiness, es una regresión real, invisible porque `packages/mlops` no corre en CI. **Sin arreglar** — máxima prioridad de código pendiente (Frente 1 del roadmap).
 
---
 
## 6. Metodología de datos — hallazgos importantes
 
### 6.1 cmdi — de SMOTE fallido a datos reales exitosos
SMOTE dio resultado negativo (+0.015 F1 solamente) — confirmó que el problema NO era volumen de datos, sino falta de diversidad de técnicas reales. Se agregaron 2,470 payloads genuinamente nuevos (SecLists + PayloadsAllTheThings, verificado con MinHash: 0% de solapamiento). Resultado: cmdi F1 rompió el techo de 0.89-0.90, llegó a 0.93+.
 
### 6.2 cmdi — cobertura Windows y comandos compuestos (v11)
Dos sub-gaps adicionales cerrados: sintaxis Windows (`certutil`, `wmic`, `net user`, `powershell -enc`, etc. — regex extendido + datos sintéticos) y comandos compuestos multi-paso (`cmd1 && cmd2 && cmd3` con rutas de archivo mezcladas, que confundían al modelo hacia `path_traversal`). Para compuestos se necesitaron 2 features nuevas (`distinct_shell_command_count`, `shell_to_path_ratio`) porque agregar solo datos no bastaba — el modelo no tenía ninguna señal que capturara "múltiples comandos de shell distintos presentes". Ambos verificados con generalización real (comandos nunca vistos en entrenamiento, correctamente clasificados).
 
### 6.3 Deduplicación — MinHash confirmado viable, con hallazgos importantes
El método viejo (Levenshtein, cutoff de 100 caracteres, cap de 10,000 pares) subestimaba masivamente la duplicación real. Bug descubierto en el camino: `find_near_duplicates` solo comparaba `query`, nunca `path`/`body` — llevó directamente al descubrimiento del bug 5.1. Duplicación genuina confirmada en las 5 clases tras ajuste de banding LSH (b=8,r=16): xss/cmdi/path_traversal 30-120x de saturación, **sqli hasta 395x** (dominado por generación de plantillas sqlmap/CAPEC), benign solo 9.5x (tráfico real, cola larga). Decisión: flag-only, no deduplicar — es una decisión de re-balanceo de corpus separada del alcance de este proyecto.
 
### 6.4 LOSO (Leave-One-Source-Out) — dos mecanismos de degradación distintos
- Mecanismo 1 (8/9 fuentes): "hambre de volumen" — cuando una fuente domina una clase, excluirla simula "entrenar con 10-15% de los datos normales". Correlación -0.744 confirmada.
- Mecanismo 2 (caso atípico `synthetic_nav`): fallo genuino por estilo — 0.9% de benign, peor LOSO F1 (0.0027) porque era la ÚNICA fuente con ese patrón, sin redundancia.
- **Mitigación parcial aplicada:** se agregó `synthetic_nav_ecommerce` (segunda fuente independiente de navegación pura, taxonomía distinta) — LOSO F1 de `synthetic_nav` mejoró de 0.0027 a **0.2916** (100x mejor, pero aún en la banda de "generalización pobre", no resuelto completamente).
### 6.5 Hallazgo estructural mayor: el corpus benigno casi no modela tráfico HTTP real
Al investigar por qué rutas de e-commerce (`/orders/8198/track`, `/category/electronics/laptops/455`) fallaban (~34-36% de tasa benigna, confirmado igual en rf_v10 y rf_v11 — no es un artefacto de una versión específica), se encontró que **99.6% del corpus "benigno" no modela la forma de un request HTTP real**. Los datos benignos dominantes (`modsec_learn` 69.7%, `payload_full` 18.2%, `payloads_csv` 6.5%) son valores de campo aislados de datasets de clasificación de payloads (nombres, direcciones, emails) — sin path, sin headers, sin la forma de un request de navegación real. `synthetic_nav` + `synthetic_nav_ecommerce` combinadas representan apenas **~0.8%** del corpus benigno total.
 
Este hallazgo reencuadra la tensión de UA (sección 7, antes documentada solo para IF) como un síntoma de este problema más amplio — no un problema aislado de User-Agent.
 
**Decisión:** no se intentó resolver en este ciclo. La curva dosis-respuesta ya conocida (sección 7) muestra que incrementos pequeños no mueven la aguja y sí arriesgan regresión. Una solución real necesitaría generación sistemática de tráfico de múltiples "personas" de aplicación (blog, e-commerce, dashboard, API, admin) a escala — documentado como trabajo futuro, ver roadmap sección 21.
 
### 6.6 Corrección importante: §10/sección 7 — RF también está afectado, no solo IF
La afirmación original ("RF's detection is completely unaffected by any part of this investigation") **nunca se verificó directamente contra RF** — solo contra IF. Al investigar el hallazgo 6.5, se encontró evidencia reproducible de que RF también se ve afectado: `GET /profile` sin User-Agent clasifica top-class `xss @ 0.50`; el mismo request con un UA de navegador real clasifica `path_traversal @ 0.50` — un cambio real en la salida de bloqueo de RF, no solo en el diagnóstico de IF. **Corregido en la documentación** (commit `6603a8b`). No reabre la decisión de no perseguir un fix de datos para IF — esa decisión se sostiene independientemente.
 
### 6.7 Confusión de atribución cmdi/sqli — re-medida y reconciliada contra rf_v11
La cifra de ~49% (julio 2026) quedó obsoleta al re-medir contra el modelo actual. Hallazgo reconciliado, no contradictorio:
- **Offline, corpus diverso de validación (el mismo que produce el F1=0.9461 de cmdi ya documentado):** 94.6% de atribución de clase correcta — ambas métricas (F1 y atribución) son exact-class-match, no métricas distintas.
- **En vivo, corpus de prueba de Config 2 (`attack-sim/large_corpus_requests.json`):** 0% de atribución correcta — 200/200 payloads cmdi etiquetados como sqli.
- **Causa raíz confirmada (no un artefacto de la app ni del modelo cargado — verificado con SHA256 byte-a-byte y con inferencia directa sin Docker):** el corpus de prueba en vivo es estructuralmente homogéneo — una sola familia de payloads de cmdi por blind timing/comparación aritmética (`sleep`, `$((...))`, `-eq`/`-ne`) que estructuralmente se parece a SQLi blind injection. Es la misma causa raíz que ya se había insinuado en el hallazgo original de ~49% de julio, solo que ese corpus mezclaba esta técnica con otras, diluyendo el problema; el corpus actual la expone al 100% porque coincidencialmente es puro ese subtipo.
- **Seguridad no afectada:** ≥99% de estos payloads SÍ se bloquean correctamente (verdict=block) — el problema es la etiqueta de clase reportada (relevante para `attacks inspect`/`attacks summary` del CLI), no la decisión de bloqueo.
- **Para la tesis:** hallazgo real y preciso — "el modelo tiene una debilidad de atribución específica y consistente en técnicas de cmdi basadas en blind timing/comparación, persistente a través de generaciones de modelo (v9→v11), sin afectar la postura de seguridad." Documentado en `docs/config2-results-v1.md` §5.1 y `docs/STATUS.md`.
---
 
## 7. Limitaciones documentadas (docs/limitations.md) — estado consolidado
 
| # | Limitación | Estado |
|---|---|---|
| 1 | cmdi separabilidad | **Resuelto** — datos reales, F1 0.89→0.93+ |
| 2 | Memoria ONNX del RF | **Resuelto** |
| 3 | `base64_like_count` posible leakage | Documentado, bajo impacto (0.86% de splits), nunca atacado — bajo retorno esperado |
| 4 | LOSO / cobertura de fuentes | **Medido y explicado** (dos mecanismos) + **mitigación parcial aplicada** para `synthetic_nav` (0.0027→0.2916) |
| 5 | Dedup cutoff/cap arbitrarios | **Completado** — las 5 clases medidas con banding LSH ajustado, decisión de no deduplicar tomada con información completa |
| 6 | Blank method/path en benign | **Resuelto** |
| 7 | XSS HTML-entity encoding | **Resuelto** — unicode-escape 0%→100%, double-percent 50%→100% |
| 8 | Confianza reducida en cmdi con contexto HTTP mínimo | **Resuelto** — Unix, Windows, y comandos compuestos, los 3 sub-gaps cerrados en v11 |
| 9 (antes §10) | IF benign-calibration / attack-camouflage tension | **Investigado exhaustivamente, ambas alternativas de fix probadas y rechazadas con evidencia.** Corregido para incluir que RF también está afectado (6.6). |
| 10 (nuevo) | Representación de tráfico benigno real en el corpus (99.6% no modela requests reales) | **Documentado como hallazgo estructural + trabajo futuro** (6.5). Mitigación parcial para el caso `synthetic_nav` aplicada. |
 
**Solo 2 limitaciones quedan sin ningún trabajo:** #3 (bajo impacto, bajo retorno) y la pieza de "hambre de volumen" de #4 (requeriría datasets públicos completamente nuevos para sqli/benign/path_traversal — fuera de alcance realista).
 
---
 
## 8. Config 1 / Config 2 / Config 3 — resultado principal para la tesis
 
**Config 1 (sin protección):** 6/6 vectores comprometidos — confirma explotabilidad de la app de referencia.
 
**Config 2 (+logSguarDian):** cobertura PASS (93-100% por categoría). Latencia: overhead absoluto 0.1-15ms, criterio ajustado (sección 9).
 
**Config 3a (WAF solo, ModSecurity+CRS PL1):** 9/9 ataques base + 14/14 evasiones bloqueadas con corpus pequeño (23 payloads hand-picked) — sobreestimaba a CRS como "invencible".
 
**Config 3b (WAF+logSguarDian en capas):** 23/23 (100%) con el corpus pequeño, tras encontrar y arreglar el bug de multipart (5.8).
 
### El resultado que debe citarse como principal: corpus grande e independiente (590 payloads SecLists)
 
| Categoría | Config 1 | Config 2 (solo logSguarDian) | Config 3a (solo WAF) | Config 3b (WAF+logSguarDian) |
|---|---|---|---|---|
| sqli | 0.0% | 98.7% | 85.7% | 100.0% |
| xss | 0.0% | 97.3% | 97.3% | 100.0% |
| path_traversal | 0.0% | 98.5% | 87.0% | 98.5% |
| cmdi | 0.0% | 100.0% | 100.0% | 100.0% |
| **Total** | **0%** | **98.8%** | **93.2%** | **99.5%** |
 
**El hallazgo de defensa en profundidad:** de los 40 ataques que CRS PL1 deja pasar, **37 son atrapados de forma independiente por logSguarDian**. Solo 3 pasan ambas capas, y ni siquiera son explotables contra esta app. Esta es la evidencia más fuerte del proyecto: un WAF de firmas bien configurado SÍ tiene brechas reales (85.7% en SQLi, no el "100%" que sugería el corpus pequeño), y logSguarDian las cierra de forma demostrablemente independiente.
 
**Round 4 (590 payloads) — completamente redactado y comiteado** (commit `af61eba`, en ambos repos). Ya NO está pendiente de análisis — la auditoría de sección 20 confirmó esto.
 
### Hallazgo adicional: sensibilidad al string de User-Agent "poco común"
Misma query benigna, distinta confianza de RF según qué tan "típico" se vea el string de UA (curl→0.367, Python→0.400, herramienta propia→0.616). Distinto del hallazgo de UA-ausente (limitación 9/10). Pendiente como estudio futuro.
 
---
 
## 9. Decisión de ajuste — Objetivo Específico 3 (criterio de latencia)
 
**Ya decidido y aplicado en el texto del protocolo actual:**
 
> "sin elevar la latencia media del servidor más de 15ms respecto a la línea base, o más del 10% en entornos de producción representativos (latencia base ≥100ms)"
 
**Justificación:** el criterio relativo puro es matemáticamente adverso contra baselines de latencia sub-milisegundo — cualquier costo absoluto pequeño produce un porcentaje relativo desproporcionado cuando el denominador es diminuto. El sistema SÍ cumple el criterio absoluto: overhead 0.1-15ms en múltiples ambientes medidos.
 
**NO citar en la tesis:** cualquier extrapolación de "millones de filas necesarias" para cumplir el criterio original — ese cálculo fue descartado por no estar basado en mediciones reales (incidente de integridad, ver sección 12).
 
**Pendiente:** aplicar formalmente este veredicto como cerrado en `docs/decision-policy.md` (no solo como investigación abierta) — Frente 1 del roadmap, sección 21.
 
---
 
## 10. Publicación en npm
 
Paquete publicado: `logsguardian@0.1.0`, con CI de auto-publish (workflow gated por lint/build/tests, solo dispara en push a `main`, usa `pnpm publish` no `npm publish` por la resolución correcta de `workspace:*` y `bundledDependencies`).
 
**Sobre adopción — no sobrevender:** el paquete está indexado y es descargable. Las cifras de descargas semanales no permiten aún distinguir tráfico real de bots/mirrors. No hay issues ni feedback de usuarios reales todavía. Es un hito de distribución, no de adopción — presentarlo así en la defensa.
 
README raíz y de `packages/core` reescritos (README.md ya no dice "skeleton, en desarrollo", afirmación falsa de aprendizaje continuo removida). README de `packages/core` incluye badges, sección "Why", tabla de métricas medidas, y limitaciones honestas con links al monorepo.
 
---
 
## 11. Pipeline MLOps CT/CI/CD — 8 fases, funcional y verificado
 
Implementación funcional (no solo diseño) del ciclo de vida completo de reentrenamiento continuo, en `packages/mlops/`.
 
**Fases 1-8, todas completadas y verificadas:**
- **1-2:** Recolección de telemetría (vectores de features, nunca payloads crudos, patrón fire-and-forget) + simulación de flota multi-fuente
- **3:** Clustering de anomalías con IF+DBSCAN. **Hallazgo clave:** un payload poliglota (SQLi+XSS+path_traversal+cmdi combinados) fue aislado como anómalo sin etiqueta previa, aunque RF lo clasificó erróneamente como una sola clase. Matiz honesto: se necesitaron 2 rondas de ajuste del payload para lograrlo — la afirmación correcta es "IF detecta desviaciones multi-eje significativas", no "cualquier técnica nueva individual".
- **4:** Curación humana vía CLI (`lg mlops review-clusters`)
- **5:** Orquestador de reentrenamiento (`training/ct_pipeline.py`, ~90s end-to-end). **Reveló un hallazgo de reproducibilidad real** (sección 13).
- **6:** 5 gates automáticos (contrato de features, métricas, paridad, E2E, memoria), fail-fast. Ambos resultados verificados (candidato bueno aprueba, candidato saboteado se rechaza en 0.19s).
- **7:** Despliegue canario en modo sombra — worker bajo demanda (nunca activo por defecto), reutiliza el patrón async de IF. Mecanismo primario: reemplazo de corpus con ground truth real. Secundario: sombra en tráfico vivo, acotado en tiempo. Memoria real medida (no estimada), varía por máquina (ver sección 14) — lo estable y citable es la arquitectura y el margen relativo, no el número absoluto.
- **8:** Promoción/rollback (`lg mlops promote-canary`, `lg mlops rollback`), versionado, requiere restart (sin hot-reload de sesiones ONNX).
**Estado actual real (confirmado en auditoría, sección 20):**
- Sin README propio
- Sin cobertura en `.github/workflows/ci.yml`
- **Con una regresión activa:** `POST /telemetry` devuelve 400 en vez de 201, 4/10 tests fallando ahora mismo — invisible porque no corre en CI
- Framing de alcance pendiente de decisión: cómo reconciliar esto con la exclusión de "aprendizaje continuo" en la tabla de alcance del protocolo (Opción A ya decidida: calificar la exclusión para que hable del middleware embebido específicamente, documentar el pipeline como trabajo exploratorio complementario)
---
 
## 12. Disciplina de integridad — dos incidentes detectados y corregidos antes de llegar a la tesis
 
1. **Extrapolación fabricada:** un borrador de Config 2 citó "406 millones de filas necesarias" para cumplir el criterio de latencia original — nunca fue computado sobre datos reales. Detectado y corregido antes de comitear.
2. **Archivo mal atribuido:** una referencia a `config2-results-v1.md` apuntaba al repo equivocado.
3. **Citas bibliográficas con metadata fabricada (documento de tesis, no código):** dos referencias del capítulo de Antecedentes (Zeng et al. y Chen et al.) tenían nombres de autor y caracterización de contenido incorrectos — verificadas contra las fuentes reales (ambas son revisiones sistemáticas/surveys, no sistemas aplicados individuales como se las describía). Corrección pendiente de aplicar (ver roadmap).
Este es el patrón de disciplina que motivó crear la skill `redaccion-academica-es` (sección 16) — verificar cualquier afirmación fáctica o cita contra la fuente real antes de aceptarla en cualquier documento, técnico o de tesis.
 
---
 
## 13. Hallazgo de reproducibilidad — notebooks desincronizados de los artefactos reales
 
Al construir `training/ct_pipeline.py` (Fase 5 del MLOps), se descubrió que los notebooks comiteados (`04_isolation_forest.ipynb`, `05_onnx_export.ipynb`) entrenaban con parámetros viejos (67 features, `max_samples="auto"`), mientras el `if.onnx` real en producción usaba parámetros distintos y correctos (61 features en ese momento, `max_samples=4096`). Los notebooks quedaron congelados en el estado de un retrain de hace 3 ciclos.
 
**Causa raíz confirmada:** gap de reproducibilidad, no de integridad de datos. El notebook se editó y corrió interactivamente en Jupyter para producir los artefactos reales, pero el `.ipynb` editado nunca se guardó de vuelta a git.
 
**Verificación de que el fix reproduce el modelo real:** al correr el notebook corregido, se obtuvieron métricas que coinciden a 4 decimales con las ya documentadas del modelo de producción — confirma que el modelo es legítimo y el notebook corregido ahora sí lo reproduce fielmente.
 
**Para la tesis:** mencionar que el código de entrenamiento fue re-sincronizado con los artefactos comiteados, verificado para reproducir las métricas exactas — anticipa la pregunta legítima de "muéstreme el notebook que produjo este modelo" con una respuesta honesta y verificada.
 
---
 
## 14. Fix del gate de memoria — de aproximación a medición real
 
`gate_memory.py` (Fase 6 del MLOps) medía memoria cargando RF+IF como sesiones simples en el hilo principal — no replicaba la arquitectura real de worker pool. **Arreglado:** cambiado a usar el benchmark de worker pool real (`onnx-memory-pool.bench.js`).
 
**Hallazgo sobre varianza entre máquinas (no fabricar coincidencias):** el número medido tras el fix (179.67MB) difiere del históricamente documentado (~245MB) — verificado explícitamente que es varianza de máquina, no un error del fix (comparación metodología vieja vs nueva en la misma máquina confirmó ~60MB de diferencia atribuible al fix mismo). **Conclusión para la tesis: los números absolutos de memoria varían según la máquina — lo estable y citable es la arquitectura, el margen relativo al límite de 300MB, y la metodología de medición.**
 
---
 
## 15. Convenciones de trabajo del proyecto
 
- **Git — logSguarDian:** rama protegida `develop`. TODO cambio requiere rama feature + PR, sin excepción.
- **Git — logSguarDian-vulnerable-project:** sin protección de rama, push directo a `feat/logsguardian-integration` es el patrón establecido.
- **Antes de cualquier fix de extractor/modelo:** investigar primero con datos reales antes de implementar.
- **Antes de comitear cualquier número/medición a documentación:** verificar que existe evidencia trazable (commit, log, archivo real) — ver sección 12, disciplina de integridad.
- **Cambios de extractor que afectan valores de features:** siempre requieren re-entrenamiento completo (unify → extract → split con nuevo `test.lock.sha256` → train → calibrar thresholds → parity → E2E). Nunca desplegar un extractor nuevo con un modelo viejo.
- **Verificación de paridad ONNX:** Python vs Node.js siempre re-confirmada tras cualquier cambio de modelo.
- **Al encontrar contradicciones entre lo que un documento afirma y lo que el repo muestra:** reportar la discrepancia explícitamente, nunca reconciliar en silencio asumiendo cuál versión es correcta.
---
 
## 16. Skill de Claude Code: `redaccion-academica-es`
 
Creada tras encontrar 4 problemas de contenido reales en el documento de tesis (descripción incorrecta del corpus, contradicción de alcance sobre reentrenamiento continuo, dos citas con metadata fabricada, fechas de objetivos inconsistentes) y patrones repetidos de "AI slop" en español académico (construcción "no es X, sino Y" 9+ veces, densidad alta de rayas parentéticas).
 
**Ubicación recomendada:** `.claude/skills/redaccion-academica-es/SKILL.md` en el proyecto de tesis LaTeX.
 
**Qué hace:** (1) nunca permite escribir una afirmación fáctica o cita sin verificarla contra la fuente real primero; (2) detecta y varía (no elimina mecánicamente) patrones de escritura genérica de IA en español académico, con la regla de "contar antes de corregir"; (3) nunca resuelve una contradicción de contenido en silencio — siempre la reporta y espera decisión del autor.
 
---
 
## 17. Estado del documento de tesis (LaTeX)
 
**Capítulos escritos:** 1 (Introducción), 2 (Antecedentes), 3 (Justificación), 4 (Objetivos), 5 (Alcance), 6 (Marco Teórico) — 34 páginas.
 
**Capítulos vacíos o con placeholder:** 7 (título placeholder "Título del capítulo" — probablemente Metodología), 8 (Conclusiones), 9 (Recomendaciones), 11 (Anexos).
 
**Correcciones de contenido identificadas y en proceso (rama de trabajo en el repo LaTeX):**
1. Descripción del corpus corregida — no es "tráfico sintético generado en Docker Compose", es predominantemente datasets públicos curados (9 fuentes, ~99.4% del corpus) + suplemento sintético dirigido (~0.6%) para gaps específicos encontrados vía LOSO/ablation.
2. Contradicción de alcance sobre reentrenamiento continuo — Opción A decidida (calificar la exclusión, documentar `packages/mlops` como trabajo exploratorio complementario).
3. Citas [8]/[9] (Zeng et al., Chen et al.) — ambas son papers reales pero mal atribuidos (autores fabricados, caracterizados como sistemas aplicados cuando son revisiones sistemáticas). Corrección de metadata + reposicionamiento del argumento en proceso.
4. Fechas de objetivos específicos — Objetivo 2 fechado antes de que el Objetivo 1 completara según el texto original; ancla real es 2 de agosto de 2026 (fecha de rf_v10, después reforzado por rf_v11 el 30 de agosto).
5. Patrón "no es X, sino Y" — 8 de 9-10 instancias reescritas con variación.
6. Densidad de rayas parentéticas — reducida en los capítulos más densos (Antecedentes, Marco Teórico).
---
 
## 18. Dónde está todo (para navegar el repo)
 
- `docs/results.md` (logSguarDian) — resultados técnicos completos, benchmarks, investigación de latencia
- `docs/limitations.md` (logSguarDian) — las limitaciones documentadas con su estado (ver sección 7 de este documento para el resumen consolidado)
- `docs/decision-policy.md` (logSguarDian) — política de decisión RF/IF, umbrales — **contiene conteo de features desactualizado (66), corregir**
- `docs/dataset-audit.md` (logSguarDian) — licencias, DOIs, citas APA 7 de los datasets — verificado completo, 0 campos `[verify]` restantes
- `docs/api.md` (logSguarDian) — **contiene conteo de features desactualizado (73/67/61), corregir**
- `docs/architecture.md` (logSguarDian) — **contiene conteo de features desactualizado (72), corregir**
- `docs/commands.md` (logSguarDian) — referencia completa del CLI
- `docs/config2-results.md` / `docs/config2-latency-evaluation.md` (logSguarDian-vulnerable-project, también espejado en `docs/vulnerable-app-evaluation/` de logSguarDian) — resultados de Config 2, todas las iteraciones
- `docs/config3b-results.md` — resultados completos de Config 3, incluyendo Round 4 (590 payloads) ya redactado
- `training/label_map.yaml` (logSguarDian) — taxonomía de etiquetas, fuente única de verdad
- `training/notebooks/` — 02_baseline, 03_random_forest, 04_isolation_forest, 05_onnx_export
- `packages/mlops/` — pipeline CT completo, sin README propio actualmente
- `PROJECT_CONTEXT.md` (este archivo) — colocar en la raíz de `logSguarDian`
- `IMPLEMENTATION_PLAN_MLOPS_CT.md` — plan de las 8 fases del MLOps
- `ROADMAP_CIERRE_TESIS.md` — plan de cierre completo del proyecto (ver sección 21)
---
 
## 19. PRs activos / recién mergeados (verificar estado al iniciar sesión nueva)
 
- `investigate/ecommerce-path-traversal-fp` — PR abierto, contiene la corrección de sección 6.6 (RF afectado por UA) + integración de `synthetic_nav_ecommerce`. Verificar si Sebastián ya respondió.
- Verificar historial reciente de PRs mergeados a `develop` antes de asumir qué versión de modelo/features está activa — **este documento se desactualizó una vez ya (creía que el modelo activo era rf_v6 en una sesión reciente cuando ya iba en rf_v11) — siempre confirmar contra `training/models/parity_report.json` antes de citar versión de modelo en cualquier tarea nueva.**
---
 
## 20. Auditoría de estado real (referencia — insumo para el roadmap)
 
Última auditoría completa encontró:
- Tests actuales: **74/74 extractor** (11 suites), **169/169 middleware/core** (21 suites) — no 68/68 ni 147/147 como en documentación vieja
- Paridad ONNX confirmada current: rf_max_prob_diff=9.465e-08, if_max_score_diff=2.404e-07
- Config 3 Round 4: confirmado completamente redactado y comiteado (no pendiente)
- Conteo de features en docs: **confirmado roto** — `api.md` dice 73/67/61, `decision-policy.md` dice 66, `architecture.md` dice 72; ninguno coincide con el real 75/69/63
- `middleware.test.ts` flaky: **confirmado ya arreglado** (aislamiento de proyecto Jest dedicado, 5/5 corridas limpias)
- Diseño de IF grace-window: **confirmado async-patch puro**, el diseño híbrido nunca se fusionó a `develop`
- `packages/mlops`: sin README, sin CI, **con regresión real activa** (telemetry endpoint 400 vs 201 esperado)
- ~~Confusión de atribución cmdi/sqli (~49%)~~ — **re-medido contra rf_v11 (sección 6.7), la cifra de julio queda obsoleta**
---
 
## 21. Roadmap de cierre — 4 frentes (ver `ROADMAP_CIERRE_TESIS.md` para el detalle completo)
 
**Frente 1 — Correcciones críticas de código y documentación (~2-3 días):**
Reconciliar conteo de features en 3 documentos; arreglar regresión de `packages/mlops`; actualizar `results.md`/`decision-policy.md` con métricas v11; cerrar veredicto formal de Δp95; re-correr Config 2 en vivo para cifra actual de confusión cmdi/sqli.
 
**Frente 2 — Redacción de la tesis (~3-3.5 semanas, el más grande y más importante):**
Capítulo 7 (Metodología), 8 (Conclusiones), 9 (Recomendaciones), 11 (Anexos). Usar la skill `redaccion-academica-es` en cada uno.
 
**Frente 3 — Decisiones de alcance pendientes:**
Framing de `packages/mlops` vs. protocolo (Opción A ya decidida, falta redactar). Revisar PR abierto cuando Sebastián responda. Decidir si vale la pena intentar la diversificación sistemática de personas de benign traffic antes de noviembre (recomendación: no, documentar como trabajo futuro).
 
**Frente 4 — Trabajo adicional condicional (solo si sobra tiempo):**
Monitoreo de issues, validación con startup real, proyectos vulnerables adicionales, ampliación de métricas ML, comando de reentrenamiento local (verificar primero si `packages/mlops` ya lo cubre).
 
**Calendario sugerido:** 12-14 semanas hasta noviembre, con Frente 2 ocupando la mayor parte del tiempo. El riesgo real para la defensa no es "falta investigación técnica" — ya hay de sobra, verificada y documentada — es "falta convertir la investigación en documento de tesis".
 
---
 
*Este documento debe releerse completo al inicio de cualquier sesión nueva de Claude relacionada con este proyecto. Si algo aquí contradice lo que el repo muestra, confiar en el repo y reportar la discrepancia — este documento es un resumen de apoyo, no la fuente de verdad.*