# Prefacio

_Sin contenido redactado: el archivo fuente `a-prefacio.tex` está vacío o solo contiene comentarios._
# Lista de abreviaturas y siglas

| Sigla | Significado |
| --- | --- |
| API | interfaz de programación de aplicaciones (Application Programming Interface) |
| AUC-ROC | área bajo la curva ROC (Receiver Operating Characteristic) |
| CAPEC | Common Attack Pattern Enumeration and Classification |
| CLI | interfaz de línea de comandos |
| CmdI | inyección de comandos (Command Injection) |
| CPU | unidad central de procesamiento |
| CRS | OWASP Core Rule Set |
| DBSCAN | Density-Based Spatial Clustering of Applications with Noise |
| DDoS | denegación de servicio distribuida |
| F1 | media armónica de la precisión y el recall |
| FN, FP, VN, VP | falsos negativos, falsos positivos, verdaderos negativos y verdaderos positivos |
| HTTP | Hypertext Transfer Protocol |
| IDS | sistema de detección de intrusiones |
| IF | Isolation Forest |
| IoT | Internet de las Cosas |
| JSON | JavaScript Object Notation |
| LFI | inclusión local de archivos (Local File Inclusion) |
| LOSO | Leave-One-Source-Out (exclusión por fuente) |
| LSH | Locality-Sensitive Hashing |
| ML | aprendizaje automático (Machine Learning) |
| MLOps | Machine Learning Operations |
| MLP | perceptrón multicapa (Multilayer Perceptron) |
| OE | objetivo específico |
| ONNX | Open Neural Network Exchange |
| OWASP | Open Worldwide Application Security Project |
| p95 | percentil 95 |
| PL1 | nivel de paranoia 1 de ModSecurity (Paranoia Level 1) |
| PR | pull request (solicitud de integración de cambios) |
| RASP | Runtime Application Self-Protection |
| REST | Representational State Transfer |
| RF | Random Forest |
| ROC | Receiver Operating Characteristic |
| RSS | Resident Set Size |
| SHA | Secure Hash Algorithm |
| SHAP | SHapley Additive exPlanations |
| SIEM | Security Information and Event Management |
| SQL | Structured Query Language |
| SQLi | inyección SQL |
| URL | Uniform Resource Locator |
| vCPU | CPU virtual |
| WAF | cortafuegos de aplicaciones web (Web Application Firewall) |
| WSL2 | Windows Subsystem for Linux 2 |
| XSS | Cross-Site Scripting |

**Unidades**

| Sigla | Significado |
| --- | --- |
| MB | megabyte ($10^6$ bytes) |
| MiB | mebibyte ($2^{20}$ bytes; 150 MB equivalen a unos 143 MiB) |
| GB | gigabyte ($10^9$ bytes) |
| GiB | gibibyte ($2^{30}$ bytes) |

# Resumen

_Sin contenido redactado: el archivo fuente `b-resumen.tex` está vacío o solo contiene comentarios._
# Abstract

_Sin contenido redactado: el archivo fuente `c-abstract.tex` está vacío o solo contiene comentarios._
# Introducción

_Sin contenido redactado: el archivo fuente `d-introduccion.tex` está vacío o solo contiene comentarios._
# Antecedentes
## Introducción al estado del arte

La detección de amenazas mediante aprendizaje automático cuenta con más de una década de desarrollo académico consolidado, particularmente en el dominio de la detección de intrusiones a nivel de red. Sin embargo, la aplicación de estas técnicas a la capa de aplicación de servicios web modernos, particularmente a arquitecturas asíncronas orientadas a eventos como Node.js, constituye un área considerablemente menos explorada en la literatura indexada. Este capítulo revisa crítica y comparativamente los antecedentes académicos y técnicos directamente relacionados con el problema abordado por logSguarDian, organizados en cinco ejes: (1) los estudios de referencia sobre detección de intrusiones basada en aprendizaje automático, (2) los algoritmos base del modelo híbrido propuesto, (3) las metodologías de construcción de datasets etiquetados, (4) las restricciones de inferencia embebida documentadas en la literatura de Edge AI, y (5) las soluciones comerciales y perimetrales existentes junto con su respaldo documental. El objetivo de esta comparación directa es identificar los vacíos metodológicos que este proyecto atiende, no producir un listado cronológico de estos trabajos.

## Detección de intrusiones basada en aprendizaje automático: panorama general

Tres revisiones sistemáticas de amplio alcance delimitan el estado del arte general del uso de aprendizaje automático en ciberseguridad. [1] presentan una taxonomía comparativa de métodos de minería de datos y aprendizaje automático aplicados a la detección de intrusiones, evaluando su desempeño reportado en la literatura previa a 2016. Su hallazgo más relevante para este proyecto es doble: por un lado, confirman que los métodos de ensamble basados en árboles obtienen consistentemente una de las mejores relaciones entre precisión de clasificación y costo computacional de inferencia frente a otras familias de algoritmos; por otro, evidencian que la inmensa mayoría de los estudios revisados opera sobre datasets de flujo de red heredados (KDD Cup 99, NSL-KDD), centrados en características de nivel de transporte (duración de conexión, bytes transferidos, banderas del protocolo TCP, Transmission Control Protocol) y no en la semántica del contenido HTTP de la capa de aplicación.

[2] amplían este panorama proponiendo una taxonomía de "ciencia de datos de ciberseguridad" que organiza los enfoques de ML en función del tipo de amenaza abordada. Su revisión confirma la misma limitación estructural señalada por Buczak y Guven: los conjuntos de datos de referencia utilizados en la literatura mayoritaria siguen centrados en tráfico de red genérico, con escasa atención a la semántica de peticiones HTTP individuales o al comportamiento específico de APIs REST. [3] conducen una revisión enfocada en sistemas de detección de intrusiones para entornos de Internet de las Cosas (IoT), comparando el desempeño de múltiples algoritmos –incluyendo Random Forest– sobre datasets como NSL-KDD, CICIDS2017 y BoT-IoT. Su aporte principal es una tabla comparativa de exactitud por algoritmo y dataset que refuerza empíricamente la superioridad de los métodos de ensamble sobre alternativas más complejas en escenarios de recursos computacionales restringidos, un hallazgo directamente aplicable al contexto de inferencia embebida de logSguarDian, aunque su enfoque permanece anclado en dispositivos IoT y no en servidores de aplicaciones Node.js.

[4] completan este panorama con una revisión específica de métodos de aprendizaje profundo aplicados a ciberseguridad, cubriendo arquitecturas como redes neuronales convolucionales y recurrentes en tareas de detección de malware, tráfico de red y correo no deseado. Su conclusión más relevante para este proyecto es una advertencia recurrente: los modelos de aprendizaje profundo de alta capacidad exhiben ganancias marginales de precisión frente a métodos más ligeros cuando se contabiliza el costo de inferencia y el tamaño del modelo serializado, lo cual constituye, a partir de una fuente independiente a la arquitectura de este proyecto, una justificación empírica adicional para descartar dichas arquitecturas en favor de modelos de ensamble ligeros, como se establece en la delimitación del alcance del componente de Machine Learning.

La comparación crítica de estos tres trabajos revela una convergencia clara: la literatura de referencia en detección de intrusiones mediante ML privilegia consistentemente los métodos de ensamble basados en árboles por su balance entre precisión y costo de inferencia, pero lo hace casi exclusivamente sobre datasets de flujo de red heredados que no capturan la semántica de una petición HTTP individual. Este vacío metodológico, la ausencia de literatura consolidada sobre ingeniería de características a nivel de request HTTP para APIs REST modernas, es precisamente el espacio que ocupa el pipeline de extracción de características de logSguarDian, descrito en la sección 36.3 de este trabajo.

Dos revisiones más recientes confirman que esta limitación estructural persiste en la literatura publicada durante el desarrollo de este proyecto. [5] revisan sistemáticamente el estado de la detección de anomalías dentro del dominio de la conciencia situacional de seguridad de redes y proponen un modelo conceptual (AFEMAD) que integraría fusión de datos multimodal, detección adaptativa en línea y aprendizaje federado; se trata, sin embargo, de una propuesta para investigación futura y no de un sistema implementado y evaluado empíricamente, y el nivel de análisis de la revisión permanece anclado en el flujo de red, sin reportar restricciones de latencia ni de huella de memoria compatibles con un entorno de inferencia embebida como el de un middleware Node.js. [6] revisan de forma sistemática más de 120 estudios publicados entre 2018 y 2024 sobre cortafuegos de aplicación web potenciados por inteligencia artificial orientados a infraestructura crítica, y documentan avances reportados en esa literatura –tasas de detección de hasta 94–99% con falsos positivos por debajo de 0.7% frente a escenarios de día cero– además de una arquitectura multicapa propuesta para atender restricciones de latencia ultra baja. Los sistemas que cubre esta revisión son, no obstante, cortafuegos de arquitectura perimetral por definición, y la revisión no reporta, entre los más de 120 estudios cubiertos, un artefacto de código abierto reproducible ni una arquitectura embebida directamente en el proceso de la aplicación protegida. Ambas revisiones, publicadas en 2025 y 2026, confirman que el vacío señalado por Buczak y Guven, Sarker et al. y Verma y Ranga –la ausencia de literatura sobre detección híbrida embebida en el proceso de una aplicación web, evaluada bajo restricciones de recursos comparables a las de un middleware Node.js– seguía sin resolverse al momento de realizar esta revisión de literatura.

## Algoritmos base del modelo híbrido: Random Forest e Isolation Forest

El componente supervisado del modelo propuesto se fundamenta directamente en el trabajo seminal de [7], quien introduce Random Forest como un método de ensamble que combina bagging con selección aleatoria de características en cada nodo de división, logrando robustez frente al sobreajuste sin sacrificar velocidad de inferencia. El componente no supervisado se fundamenta en [8], quienes proponen Isolation Forest bajo el principio de que las observaciones anómalas requieren, en promedio, menos particiones aleatorias para ser aisladas que las observaciones normales. Ambos algoritmos constituyen antecedentes directos de la arquitectura del proyecto, no meramente referenciales: sus propiedades de complejidad computacional lineal y ausencia de requisitos de normalización estricta son la razón técnica por la que fueron seleccionados frente a las quince alternativas evaluadas conceptualmente en la literatura revisada.

[9] contextualizan estos dos algoritmos dentro de una taxonomía más amplia de técnicas de detección de anomalías, estableciendo la distinción formal entre detección supervisada (que requiere ejemplos etiquetados de cada clase de anomalía) y detección no supervisada de una sola clase (que modela únicamente la normalidad). Su marco conceptual es el antecedente teórico directo de la decisión arquitectónica de combinar ambos paradigmas en un modelo híbrido, en lugar de optar por uno solo: mientras el primero garantiza precisión sobre las categorías de ataque conocidas, el segundo provee una señal complementaria de anomalía, registrada y no usada para bloquear, frente a variantes no vistas durante el entrenamiento.

## Metodologías de construcción y etiquetado de datasets

El corpus de entrenamiento de logSguarDian se compone predominantemente de datasets públicos curados –SR-BH 2020/CAPEC, modsec-learn, registros de honeypot de ModSecurity, SecLists, PayloadsAllTheThings y varios conjuntos de Kaggle, cada uno con su etiqueta original y con la licencia documentada en la auditoría de datasets del proyecto– y solo de forma minoritaria de un suplemento de tráfico sintético generado deliberadamente para cubrir vacíos puntuales de cobertura detectados mediante análisis de exclusión por fuente (LOSO) y pruebas de ablación sobre el corpus público. Es esta porción sintética, y no el corpus completo, la que tiene como antecedente metodológico directo el trabajo de [10], quienes proponen un enfoque sistemático para generar datasets de referencia mediante el despliegue de un entorno de prueba controlado, la simulación de tráfico legítimo representativo y la ejecución de herramientas de ataque automatizadas, con etiquetado determinista basado en el conocimiento del proceso de generación ("ground truth by design"). Este enfoque, que dio origen a los datasets de la familia CICIDS ampliamente citados en la literatura de detección de intrusiones, constituye la base metodológica adoptada en este proyecto para el suplemento sintético, generado para atender vacíos puntuales de cobertura y no como fuente primaria de datos de entrenamiento.

La comparación crítica con este antecedente revela, no obstante, la misma limitación estructural identificada en la sección anterior: los datasets resultantes de esta metodología –incluyendo el propio CICIDS– se construyen predominantemente sobre características de flujo de red (duración, bytes por segundo, número de paquetes) y no sobre la semántica del contenido de la petición HTTP. La adopción del mismo principio metodológico de generación controlada, pero aplicado, para el suplemento sintético del corpus, a la extracción de características semánticas del objeto `req` de Express en lugar de metadatos de flujo de red, representa una adaptación metodológica específica de este proyecto frente a su antecedente directo.

## Restricciones de inferencia embebida y Edge AI

La ejecución de modelos de aprendizaje automático dentro de un proceso con restricciones estrictas de latencia y memoria, sin comunicación con servicios externos, está documentada de forma consolidada en la literatura de Edge AI, cuyo texto de referencia es el de [11]. Los autores establecen los principios de diseño para desplegar modelos ligeros bajo presupuestos de memoria y tiempo de inferencia del orden de milisegundos, incluyendo técnicas de cuantización y formatos de serialización optimizados como los adoptados en este proyecto (ONNX). Sin embargo, este cuerpo de literatura se desarrolla casi en su totalidad sobre microcontroladores y dispositivos embebidos de hardware dedicado, no sobre entornos de ejecución de un solo hilo orientados a eventos como el de Node.js. No se identificó en la revisión de literatura un antecedente académico que documente la aplicación de esta disciplina de inferencia embebida a las restricciones específicas del Event Loop de Node.js mediante `worker_threads`, lo cual constituye una adaptación metodológica original de este proyecto sobre un cuerpo de conocimiento previamente establecido en un dominio de hardware distinto.

## Soluciones perimetrales existentes y su respaldo documental

Como complemento a la revisión académica, la literatura técnica y los informes de la industria documentan de forma consistente las limitaciones estructurales de las soluciones perimetrales tradicionales frente a amenazas de capa de aplicación. La taxonomía del [12] establece las categorías de vulnerabilidad más críticas en aplicaciones web modernas, incluyendo inyección y fallos de control de acceso, y sirve como marco de referencia frente al cual se evalúa la cobertura de logSguarDian. El reporte anual de [13] y el informe de [14] aportan evidencia cuantitativa reciente sobre la prevalencia de vulnerabilidades en cadenas de suministro de software abierto y sobre la efectividad limitada de los controles perimetrales frente a ataques dirigidos a la lógica de negocio. A diferencia de los antecedentes académicos revisados en las secciones anteriores, estas fuentes constituyen documentación técnica de la industria y no literatura indexada por pares; se incorporan en este capítulo únicamente como evidencia contextual de la magnitud del problema, no como fundamento metodológico del diseño del sistema, distinción que se mantiene consistente con la naturaleza aplicada de este trabajo.

## Síntesis comparativa

El Cuadro 1 resume los antecedentes revisados en función de cuatro dimensiones críticas para el problema de investigación: el nivel de la pila de red en el que opera cada antecedente, la naturaleza del dataset o evidencia empleada, la arquitectura de despliegue del enfoque, y la limitación principal identificada frente a la propuesta de logSguarDian.

| **Antecedente** | **Nivel** | **Arquitectura** | **Limitación frente a logSguarDian** |
|:---|:---|:---|:---|
| Buczak & Guven (2016); Sarker et al. (2020); Verma & Ranga (2020) | Red (flujo) | Offline / batch | Datasets de flujo de red (KDD/NSL-KDD/CICIDS); sin semántica de petición HTTP |
| Berman et al. (2019) | Red / malware | Offline / batch | Modelos de aprendizaje profundo de alto costo, sin evaluación de restricciones de inferencia en tiempo real |
| Zhen et al. (2025) | Red (flujo) | Revisión / propuesta conceptual | Modelo híbrido (AFEMAD) propuesto como marco conceptual, sin implementación evaluada ni restricciones de latencia embebida documentadas |
| Rahman et al. (2026) | Aplicación | Revisión sistemática (WAF perimetral) | Revisión de más de 120 estudios de WAF de arquitectura perimetral; sin artefacto reproducible ni arquitectura embebida no perimetral entre los estudios cubiertos |
| Shiravi et al. (2012) | Red (flujo) | Entorno de prueba controlado | Metodología de generación adoptada, pero features de flujo, no de contenido HTTP |
| Warden & Situnayake (2019) | Hardware embebido | Microcontroladores | Disciplina de Edge AI no documentada para el Event Loop de Node.js |

Síntesis comparativa de los antecedentes revisados frente a la propuesta de logSguarDian. Elaboración propia a partir de la revisión de literatura de este capítulo.

## Conclusión: vacíos identificados y aporte del proyecto

La revisión crítica de los antecedentes académicos y técnicos converge en tres vacíos concretos que este proyecto atiende de forma directa. En primer lugar, la literatura de referencia en detección de intrusiones mediante aprendizaje automático, ejemplificada en las revisiones de Buczak y Guven, Sarker et al. y Verma y Ranga, privilegia consistentemente los datasets de flujo de red heredados sobre la semántica de peticiones HTTP individuales, dejando sin resolver la pregunta de cómo construir un pipeline de ingeniería de características orientado específicamente al objeto de petición de un framework como Express. En segundo lugar, ni la revisión de arquitecturas híbridas supervisadas/no supervisadas de Zhen et al. (2025) ni la revisión sistemática de cortafuegos de aplicación web potenciados por inteligencia artificial de Rahman et al. (2026) identifican, entre la literatura que cubren, un sistema implementado bajo una arquitectura embebida dentro del proceso de una aplicación con recursos limitados; ambas permanecen, respectivamente, en el nivel de propuesta conceptual y en el de arquitectura perimetral centralizada, sin abordar las restricciones específicas de un despliegue embebido dentro del proceso de una aplicación Node.js, que es precisamente el escenario documentado para las startups tecnológicas guatemaltecas en el planteamiento del problema de este trabajo. En tercer lugar, la disciplina de inferencia embebida bajo restricciones de latencia y memoria, consolidada en la literatura de Edge AI para hardware de microcontroladores, no cuenta con un antecedente documentado de aplicación al modelo de concurrencia de un solo hilo de Node.js mediante `worker_threads`.

Estos tres vacíos (la ausencia de ingeniería de características semántica a nivel de HTTP en la literatura de ML-IDS, la ausencia de arquitecturas híbridas embebidas, no perimetrales, documentadas para aplicaciones web, y la ausencia de una adaptación de la disciplina de Edge AI al entorno de ejecución de Node.js) no son independientes entre sí: se articulan en un mismo vacío estructural, la falta de una solución de detección de amenazas que combine aprendizaje automático híbrido con inferencia embebida en tiempo real dentro de un servidor Node.js, sin infraestructura perimetral ni dependencias externas. logSguarDian se posiciona como una respuesta directa a este vacío convergente. De sus antecedentes adopta los elementos validados empíricamente por la literatura –la superioridad de los métodos de ensamble ligeros sobre alternativas de mayor capacidad, la complementariedad teórica entre detección supervisada y no supervisada, y la metodología de generación controlada de datasets con etiquetado determinista– y los extiende hacia un dominio de aplicación, la protección embebida de APIs Node.js, en el que dicha combinación no había sido previamente documentada.

# Justificación
La motivación central de este trabajo de graduación surge de una brecha estructural verificable: las startups y empresas tecnológicas que desarrollan servicios sobre Node.js rara vez cuentan con un equipo de seguridad dedicado, mientras que la superficie de ataque de sus APIs REST –inyección SQL, Cross-Site Scripting, Path Traversal/LFI e inyección de comandos del sistema operativo– corresponde a categorías de riesgo documentadas de forma consistente en el estándar OWASP Top 10 como las más críticas para aplicaciones web modernas [12]. En un ecosistema donde una proporción mayoritaria de las aplicaciones web depende de componentes de código abierto propensos a vulnerabilidades [14], y donde los reportes anuales de la industria documentan de forma sostenida el bajo costo de explotación de fallos de lógica de negocio frente a los altos costos de mantenimiento de controles perimetrales [13], la ausencia de mecanismos de detección accesibles a nivel de capa de aplicación es una condición estructural del ecosistema, y no un vacío incidental, que este proyecto busca atender directamente.

## Importancia del problema

El problema central que motiva esta investigación es la ausencia de mecanismos automatizados, técnicamente fundamentados y económicamente viables para detectar ataques ampliamente documentados y estudiados en organizaciones sin capacidad de inversión en seguridad dedicada. Las soluciones existentes revisadas en el capítulo de Antecedentes –cortafuegos de aplicación web (WAF), sistemas de detección de intrusiones (IDS) y plataformas de gestión de eventos de seguridad (SIEM)– comparten una limitación común: exigen mantenimiento especializado continuo, infraestructura de soporte o un costo de licenciamiento que las sitúa fuera del alcance de organizaciones pequeñas [13]. Esta condición no es exclusiva de un contexto geográfico particular, pero se agudiza en economías donde el crecimiento del ecosistema tecnológico no ha sido acompañado de una madurez institucional equivalente en ciberseguridad, como es el caso de Guatemala, donde los ciberataques crecieron un 200% entre 2023 y 2024 y el país se ubica entre los diez con mayor exposición cibernética de Latinoamérica [15]. Abordar este problema es importante porque la ausencia de protección a nivel de aplicación expone directamente datos de clientes, información financiera y la continuidad operativa de organizaciones que, por su tamaño, no pueden absorber el costo de un incidente de seguridad significativo.

## Relevancia técnica y científica

Desde la perspectiva técnica, este trabajo es relevante porque atiende un vacío identificado de forma explícita en el capítulo de Antecedentes: la literatura de detección de intrusiones mediante aprendizaje automático se ha desarrollado predominantemente sobre datos de flujo de red, no sobre la semántica de peticiones HTTP individuales, y ni la revisión de arquitecturas híbridas de aprendizaje supervisado y no supervisado de [5] ni la revisión sistemática de cortafuegos de aplicación web potenciados por inteligencia artificial de [6] identifican, entre la literatura que cubren, un sistema implementado bajo una arquitectura embebida dentro del proceso de la aplicación protegida. Investigar la viabilidad de un modelo híbrido de aprendizaje automático ejecutado en tiempo de inferencia dentro de un servidor Node.js, sujeto a restricciones estrictas de latencia impuestas por su modelo de concurrencia de un solo hilo, constituye un aporte técnico concreto: extiende una disciplina de diseño –la inferencia embebida bajo restricciones de recursos, consolidada en la literatura de Edge AI para hardware de microcontroladores– hacia un dominio de ejecución distinto para el cual no se identificó antecedente documentado. Este componente de novedad metodológica es lo que justifica, desde el punto de vista científico, el carácter aplicado-experimental de la investigación: su meta es generar evidencia empírica sobre si dicha combinación arquitectónica es técnicamente viable, en lugar de implementar una solución cuya viabilidad ya esté validada de antemano.

## Relevancia social, económica e institucional

En el plano social y económico, la relevancia del proyecto se sostiene en la magnitud documentada del problema en el contexto local. El ecosistema de startups guatemaltecas opera en un entorno donde la ausencia de un marco legal específico de ciberseguridad y la escasez de profesionales especializados en la región limitan estructuralmente la capacidad de estas organizaciones para invertir en controles de seguridad tradicionales. Una herramienta distribuida sin costo a través de un registro de paquetes de uso extendido, que no requiere modificaciones a la infraestructura existente ni conocimiento especializado para su integración, reduce directamente las dos barreras de adopción más citadas en la literatura de la industria: el presupuesto disponible y la complejidad técnica de implementación [13]. En el plano institucional, el proyecto es relevante para la Universidad del Valle de Guatemala en la medida en que constituye una contribución documentada y reproducible en la intersección entre ciencia de datos, ciberseguridad e ingeniería de software, un área de creciente relevancia curricular y de investigación aplicada dentro de la Facultad de Ingeniería.

## Beneficiarios de la investigación

Los beneficiarios directos de este trabajo son, en primer lugar, las startups y empresas tecnológicas que operan servicios sobre Node.js sin un equipo de seguridad dedicado, para quienes la investigación busca proveer una herramienta de protección accesible a nivel de capa de aplicación. En segundo lugar, son beneficiarios directos los propios autores del proyecto integrador, para quienes el trabajo representa la aplicación rigurosa de las competencias desarrolladas en sus respectivas áreas de formación –inteligencia artificial y aprendizaje automático, en el caso del componente documentado en este protocolo, y ciberseguridad, en el caso del componente desarrollado en paralelo– sobre un problema real y técnicamente exigente. Como beneficiarios indirectos se identifican, por un lado, la comunidad académica y estudiantil de la Universidad del Valle de Guatemala, que podrá disponer de la metodología documentada de construcción de un pipeline de detección de amenazas sobre arquitecturas orientadas a eventos como referencia para cursos o trabajos de graduación posteriores; y por otro, de manera más amplia, los usuarios finales de las aplicaciones que eventualmente adopten la herramienta, cuya información personal y financiera se beneficia de manera transitiva de cualquier mejora en la postura de seguridad de los servicios que utilizan.

## Síntesis

La justificación de este trabajo de graduación se apoya en la combinación específica de tres factores que, tomados en conjunto, delimitan un problema real y no resuelto, y no en la novedad de los ataques que busca detectar, ya ampliamente catalogados en estándares como OWASP Top 10 [12]: una brecha de adopción de controles de seguridad documentada de forma consistente en la literatura de la industria [13], [14]; un vacío metodológico identificado en la literatura académica respecto a la detección de amenazas embebida en tiempo de ejecución dentro de aplicaciones Node.js; y un contexto local, el ecosistema de startups guatemaltecas, donde ambos factores convergen con particular intensidad [15]. Este capítulo no pretende anticipar en qué medida la solución propuesta logrará resolver dicho problema; ese es precisamente el objeto de la investigación desarrollada en los capítulos siguientes. Lo que este capítulo establece es que el problema es real, que su abordaje es pertinente tanto desde una perspectiva técnica como social e institucional, y que existen beneficiarios concretos, directos e indirectos, para quienes una respuesta fundamentada a este problema representa un aporte de valor verificable.

# Objetivos
## Objetivo general

Diseñar e implementar una librería npm que integre un pipeline de ingeniería de características y un modelo híbrido de aprendizaje automático, capaz de detectar y clasificar amenazas conocidas y anomalías estadísticas correspondientes a variantes desconocidas de los vectores cubiertos en endpoints Node.js en tiempo de ejecución, con el propósito de proveer a startups tecnológicas sin equipo de seguridad dedicado una herramienta accesible de protección a nivel de capa de aplicación que no comprometa el rendimiento del servidor anfitrión.

## Objetivos específicos

- Construir, durante la fase de desarrollo de la librería (20 de junio – 1 de agosto de 2026), un pipeline de ingeniería de características que extraiga y vectorice atributos cuantificables del tráfico HTTP de forma asíncrona mediante *worker_threads*, verificando que su ejecución no introduzca una latencia adicional superior a 5 ms por petición en el servidor anfitrión.

- Evaluar, al cierre del ciclo de entrenamiento que produce la versión del modelo destinada a la fase de pruebas del sistema (2 de agosto de 2026), un modelo híbrido compuesto por Random Forest e Isolation Forest sobre un conjunto de prueba bloqueado, demostrando que el componente supervisado alcanza un F1-score mínimo de 0.80 en al menos tres de las cuatro categorías de ataque cubiertas, y que el componente no supervisado alcanza una tasa de detección de anomalías mínima del 50% con una tasa de falsos positivos máxima del 10%. El refinamiento iterativo del modelo continuó durante la fase de pruebas del sistema, dentro de la ventana del tercer objetivo específico, incorporando ciclos de reentrenamiento adicionales –como el que atendió vacíos de cobertura en la categoría de inyección de comandos detectados durante esa misma fase– sin alterar los criterios de aceptación aquí establecidos.

- Evaluar, durante la fase de pruebas del sistema (2 de agosto – 30 de septiembre de 2026), el desempeño integral de la librería integrada como middleware, verificando que la detección de payloads representativos alcance al menos el 80% por cada una de las cuatro categorías de ataque cubiertas en un entorno de prueba controlado, sin elevar la latencia p95 del servidor más de 15 ms respecto a la línea base sin protección.[^1]

# Alcance
Este capítulo delimita con precisión qué comprende el presente trabajo de graduación, estableciendo sus límites funcionales, técnicos y operativos, así como las condiciones, restricciones y supuestos bajo los cuales se desarrolla. La delimitación aquí definida es consistente con los objetivos planteados y sirve como referencia directa para evaluar, al cierre del proyecto, si lo entregado corresponde a lo comprometido.

## Alcance funcional

logSguarDian es una librería npm que implementa un middleware de tipo *Runtime Application Self-Protection* (RASP) para aplicaciones Node.js construidas sobre el framework Express. Su alcance funcional comprende cuatro elementos concretos. Primero, la intercepción de cada petición HTTP entrante antes de que alcance la lógica de negocio de la aplicación anfitriona. Segundo, la extracción y vectorización de un conjunto de 76 características numéricas del objeto `req` de Express, organizadas en seis grupos: semántica de ataque sobre las cuatro categorías cubiertas (37), estructura HTTP (9), URL y ruta (6), parámetros y cuerpo (9), evasión por encoding (10) y variables temporales (5). Tercero, la inferencia sobre un modelo híbrido compuesto por un Random Forest (componente supervisado) y un Isolation Forest (componente no supervisado), ambos serializados en formato ONNX y ejecutados de forma asíncrona mediante `worker_threads` sin bloquear el *Event Loop* del proceso anfitrión. Cuarto, la clasificación de cada petición como tráfico legítimo o como una de las cuatro categorías de ataque cubiertas, con la generación correspondiente de una respuesta de bloqueo configurable o de una alerta registrada.

El alcance funcional incluye además una interfaz de línea de comandos con cuatro grupos de subcomandos (`config`, `endpoints`, `attacks`, `webhooks`) que permiten al desarrollador anfitrión obtener visibilidad sobre el tráfico clasificado, perfilar rutas con mayor densidad de ataques e integrar la librería con sistemas externos de notificación mediante webhooks, sin requerir modificaciones a la arquitectura de la aplicación protegida.

## Alcance técnico

El componente de Machine Learning documentado en este trabajo comprende: el análisis, la justificación y el contrato de entrada del pipeline de ingeniería de características que transforma el objeto `req` de Express en un vector numérico de dimensión fija; la construcción de un corpus de entrenamiento compuesto predominantemente por datasets públicos curados (entre ellos SR-BH 2020/CAPEC, modsec-learn, registros de honeypot de ModSecurity, SecLists, PayloadsAllTheThings y conjuntos de Kaggle, cuyas licencias se verificaron en la auditoría de datasets, salvo dos que no declaran licencia), complementado con un conjunto acotado de tráfico sintético generado en un entorno de prueba controlado (Docker Compose) para cubrir vacíos puntuales de cobertura detectados durante la validación del modelo, con etiquetado determinista basado en el conocimiento del proceso de generación para esa porción sintética; el entrenamiento, ajuste de hiperparámetros y evaluación del modelo híbrido Random Forest e Isolation Forest sobre dicho corpus; la serialización del modelo en formato ONNX mediante `sklearn2onnx`, con verificación de paridad de predicción respecto al modelo original en Python; y la integración del modelo serializado en la librería npm mediante el runtime `onnxruntime-node`, con inferencia ejecutada en un *worker pool* dedicado. La implementación inicial del extractor estuvo a cargo de Sebastián Huertas (véase la sección 36.7).

La librería está delimitada técnicamente a aplicaciones que utilicen Node.js en versión igual o superior a 20, la versión mínima declarada en el campo `engines` de `packages/core/package.json`, y Express 4.18 o posterior, o Express 5 (`peerDependencies` de `packages/core`: `^4.18.0 ^5.0.0`), como capa de enrutamiento HTTP. El entrenamiento de los modelos se realiza íntegramente en Python sobre hardware Apple Silicon local, sin dependencia de infraestructura de cómputo en la nube.

## Alcance operativo y de evaluación

La evaluación del sistema se realiza en un entorno de prueba controlado y reproducible, compuesto por una aplicación Express deliberadamente vulnerable desplegada mediante Docker Compose. Sobre este entorno se definieron tres configuraciones de evaluación progresivas: una configuración base sin ningún mecanismo de protección, que confirma la explotabilidad de la aplicación de referencia; una configuración con logSguarDian activo como única capa de protección; y una configuración de defensa en capas que combina un Web Application Firewall perimetral (Nginx con ModSecurity y el Core Rule Set de OWASP) junto con logSguarDian operando como segunda capa. Esta tercera configuración delimita explícitamente el alcance operativo del proyecto a un escenario de defensa en profundidad, evaluando la capacidad de detección de logSguarDian de forma independiente sobre el tráfico que logra evadir o queda fuera de la cobertura de un WAF basado en firmas, en lugar de plantear la evaluación como una comparación de qué componente es individualmente superior.

El alcance de esta evaluación se limita al entorno de prueba controlado descrito; no se contempla dentro del alcance del proyecto un despliegue en un entorno de producción real de terceros como criterio de aceptación del sistema. Cualquier validación adicional con organizaciones externas se documenta como evidencia contextual complementaria y no como parte de los criterios de aceptación verificables del proyecto.

## Elementos fuera del alcance

El Cuadro 2 enumera las exclusiones explícitas del proyecto, cada una acompañada de su justificación técnica, con el fin de delimitar con precisión la frontera entre lo que logSguarDian cubre y lo que queda deliberadamente fuera de su diseño.

| **Ámbito excluido** | **Razón técnica** |
|:---|:---|
| Denegación de servicio distribuida (DDoS) y fuerza bruta | Ataques inter-request: su naturaleza maliciosa reside en patrones de frecuencia y volumen acumulados entre múltiples peticiones, incompatibles con un vector de características que opera petición a petición. |
| Broken Object Level Authorization (BOLA), Mass Assignment, Server-Side Request Forgery (SSRF), deserialización insegura | Requieren conocimiento del modelo de datos específico de la aplicación anfitriona; no generan patrones semánticos detectables sin contexto de la lógica de negocio. |
| Inyecciones NoSQL (MongoDB u otras) | Sintaxis de payload estructuralmente distinta a las inyecciones SQL cubiertas; requeriría un corpus de entrenamiento y marcadores de características independientes. |
| Modelos de aprendizaje profundo de alta capacidad (red neuronal convolucional (CNN), red neuronal recurrente (RNN), Transformers) | Costo de inferencia incompatible con el presupuesto de latencia del middleware; tamaño de modelo serializado incompatible con las convenciones de un paquete npm de uso general. |
| Aprendizaje continuo y reentrenamiento automático embebido en el proceso de la aplicación anfitriona | Requeriría infraestructura de almacenamiento de muestras y validación previa al despliegue dentro del propio proceso del middleware, incompatible con el principio de operación autónoma sin dependencias externas de la librería en tiempo de ejecución. |
| Seguridad de red (Capas 3 y 4 del modelo OSI, Open Systems Interconnection) | logSguarDian opera exclusivamente en la Capa 7, dentro del proceso Node.js; la mitigación volumétrica de red es responsabilidad de controles perimetrales complementarios. |
| Funcionalidades administrativas de WAF empresarial (gestión centralizada de reglas, dashboards, integración con red de distribución de contenidos (CDN)) | Requieren infraestructura de servicio central, incompatible con el principio de operación sin dependencias externas que fundamenta la propuesta de valor de la librería. |
| Compatibilidad con runtimes distintos de Node.js/Express | El mecanismo de integración es específico al sistema de middleware de Express; soporte para otros lenguajes o frameworks constituiría un entregable independiente. |

Elementos explícitamente fuera del alcance del proyecto, con su justificación técnica. Elaboración propia.

## Restricciones, condiciones y supuestos

El desarrollo del proyecto está sujeto a las siguientes restricciones y supuestos, que delimitan el margen de diseño y ejecución disponible. En cuanto a restricciones de tiempo, el proyecto se ejecuta dentro del período comprendido entre mayo y octubre de 2026, correspondiente al calendario del trabajo de graduación de la Facultad de Ingeniería de la Universidad del Valle de Guatemala; cualquier línea de trabajo no completable dentro de dicho período se documenta explícitamente como trabajo futuro y no como un entregable pendiente. En cuanto a restricciones de recursos, el entrenamiento de los modelos se realiza sobre hardware local sin presupuesto asignado a instancias de cómputo en la nube, condición verificada como viable dado el tamaño de los modelos de ensamble seleccionados (Random Forest e Isolation Forest) frente a alternativas de mayor capacidad computacional. En cuanto a restricciones de dependencias externas, la librería está diseñada para operar sin comunicación con servicios de inferencia remotos ni infraestructura de terceros durante su ejecución en producción, lo cual delimita el diseño hacia modelos de inferencia local suficientemente ligeros para residir en el mismo proceso que la aplicación anfitriona.

Se asume, además, que el conjunto de herramientas de simulación de ataques y generación de tráfico legítimo empleadas para construir el corpus de entrenamiento produce muestras suficientemente representativas de las cuatro categorías de ataque cubiertas; esta condición fue verificada mediante el análisis exploratorio del corpus resultante antes de proceder a la fase de entrenamiento. Se asume también que la arquitectura de middleware de Express constituye un punto de integración representativo del patrón dominante de desarrollo de APIs REST en el ecosistema de startups tecnológicas guatemaltecas descrito en la Justificación de este trabajo.

## Coherencia y viabilidad del alcance

El alcance definido en este capítulo mantiene coherencia directa con los objetivos específicos del proyecto: el alcance funcional y técnico corresponde a los objetivos de construcción del pipeline de características y del modelo híbrido, mientras que el alcance operativo de evaluación en tres configuraciones progresivas corresponde al objetivo de evaluación del desempeño integral del sistema. Las exclusiones documentadas en el Cuadro 2 son decisiones de diseño deliberadas, tomadas con anterioridad al inicio del desarrollo y orientadas a mantener un alcance verificable dentro del tiempo y los recursos disponibles, no limitaciones que el proyecto haya dejado sin resolver. La viabilidad de este alcance está respaldada por la naturaleza acotada de las cuatro categorías de ataque seleccionadas –todas de naturaleza intra-request, evaluables mediante el mismo vector de características sin requerir estado persistente entre peticiones– y por la selección de algoritmos de complejidad computacional lineal, cuya factibilidad de entrenamiento e inferencia bajo las restricciones de hardware y tiempo del proyecto fue confirmada antes de comprometer dicho alcance como parte de los objetivos específicos del trabajo.

# Marco teórico
## Introducción

Mientras el capítulo de Antecedentes compara logSguarDian contra trabajos previos para identificar los vacíos metodológicos que este proyecto atiende, el presente capítulo desarrolla los conceptos que un lector necesita para entender por qué esos vacíos existen y por qué la arquitectura propuesta los cierra de la forma en que lo hace. Los fundamentos se organizan en el orden en que se articulan dentro del sistema: primero las categorías de ataque que logSguarDian debe reconocer y el entorno de ejecución –Node.js, Express y el modelo de middleware– en el que opera; después el ecosistema de dependencias de terceros y el contexto local que motivan su necesidad; luego los algoritmos de aprendizaje automático evaluados y seleccionados para el modelo híbrido; y finalmente el proceso de ingeniería de características, las métricas con las que se evalúa el sistema, y las restricciones de serialización y concurrencia bajo las cuales debe operar en producción. Cada eje se cierra relacionando el concepto con una decisión de diseño concreta del proyecto, documentada con mayor detalle técnico en los capítulos de Alcance y Objetivos.

## Panorama de amenazas en la capa de aplicación

El OWASP Top 10 clasifica la inyección como la categoría de riesgo más consistentemente crítica en aplicaciones web desde su primera edición, y la define como cualquier mecanismo por el cual datos no confiables suministrados por un atacante alteran la interpretación de un comando o consulta por parte del intérprete que la recibe [12]. En la edición 2021, la inyección SQL, XSS y la inyección de comandos se agrupan en A03 (Inyección), y el path traversal (CWE-22) en A01 (Control de acceso defectuoso). Las cuatro categorías de ataque a nivel de aplicación cubiertas por logSguarDian se dirigen cada una a un componente distinto de la pila de una aplicación Node.js típica.

La inyección SQL (SQLi) ocurre cuando una entrada de usuario se concatena sin sanitizar dentro de una consulta destinada a un motor de bases de datos relacional, permitiendo que el atacante inserte cláusulas SQL adicionales –por ejemplo, un operador `OR 1=1` o un comentario `--` que trunca el resto de la consulta original– y así alterar su lógica de autenticación o extracción de datos. El Cross-Site Scripting (XSS) sigue el mismo principio pero dirigido al intérprete del navegador: un payload que contiene marcado HTML o JavaScript –típicamente una etiqueta `<script>` o un manejador de eventos como `onerror`– se refleja o persiste sin escapar en una respuesta, ejecutándose en el contexto de sesión de otro usuario. El Path Traversal, cuya forma más severa es la Inclusión Local de Archivos (LFI), explota la resolución de rutas del sistema de archivos: una secuencia de ascenso de directorio (`../`) inyectada en un parámetro que la aplicación concatena directamente a una ruta base permite acceder a archivos fuera del directorio previsto. La inyección de comandos del sistema operativo (CmdI) ocurre cuando una entrada de usuario llega sin sanitizar a una llamada que invoca un shell del sistema operativo, permitiendo el uso de operadores de encadenamiento (`;`, `&&`, `|`) o de sustitución de comandos (`$(...)`) para ejecutar comandos arbitrarios con los privilegios del proceso de la aplicación.

Las cuatro categorías comparten una propiedad estructural que fundamenta directamente el diseño del pipeline de características de logSguarDian: la evidencia del ataque reside íntegramente dentro de una única petición HTTP –su método, ruta, encabezados, parámetros de consulta y cuerpo– sin requerir estado acumulado de peticiones anteriores. Esta propiedad es la razón técnica, documentada en el capítulo de Alcance, por la cual el vector de características de logSguarDian opera petición a petición y por la cual ataques de naturaleza inter-request como la denegación de servicio o la fuerza bruta quedan fuera del alcance del proyecto.

## Node.js, Express y el modelo event-driven

Node.js ejecuta el código de la aplicación –incluido el middleware que la protege– sobre un único hilo de Event Loop, que atiende operaciones de entrada/salida de forma no bloqueante mediante *libuv*, pero que no puede ejecutar dos fragmentos de código JavaScript de forma simultánea dentro de ese hilo [16]. Este modelo, conocido como orientado a eventos (*event-driven*), sustituye el patrón clásico de un hilo del sistema operativo por conexión con un bucle único que procesa callbacks a medida que sus operaciones de E/S asociadas se resuelven, lo cual permite atender miles de conexiones concurrentes con un consumo de memoria muy inferior al de un servidor multihilo tradicional, a costa de que cualquier código síncrono de larga duración bloquee la atención de todas las demás conexiones mientras se ejecuta.

Express se construye sobre este modelo como un framework de enrutamiento que organiza el procesamiento de una petición HTTP en una cadena de funciones *middleware*, cada una con acceso al objeto de petición (`req`) y de respuesta (`res`), y con la capacidad de delegar el control a la siguiente función de la cadena mediante una llamada explícita (`next()`) o de interrumpirla enviando una respuesta. Esta arquitectura de cadena de middleware es la que permite insertar un componente de seguridad como logSguarDian delante de la lógica de negocio de la aplicación sin modificar su código: basta con registrarlo como una función más en la cadena, ejecutada antes que las rutas de la aplicación anfitriona. La consecuencia directa del modelo de un solo hilo para el diseño de logSguarDian es que cualquier operación de cómputo intensivo ejecutada de forma síncrona dentro de ese middleware –como la inferencia de un modelo de aprendizaje automático– bloquearía el Event Loop y, con él, todas las peticiones concurrentes de la aplicación anfitriona, sin importar cuán rápida sea esa operación en términos absolutos; esta restricción se retoma en la sección de Edge AI de este capítulo, donde se describe el mecanismo con el que logSguarDian la resuelve.

## Middleware y Runtime Application Self-Protection (RASP)

La posición de logSguarDian dentro de la cadena de middleware de Express no es solo un detalle de integración: define su categoría arquitectónica frente a otros mecanismos de defensa de la capa de aplicación. [17] formalizan, dentro de una taxonomía más amplia de sistemas de software autoprotector, la categoría de autoprotección de aplicaciones en tiempo de ejecución (RASP, por sus siglas en inglés) como aquella que instrumenta directamente el proceso de la aplicación para detectar y mitigar amenazas con visibilidad de su estado de ejecución interno, en contraposición a los mecanismos perimetrales que observan únicamente el tráfico de red que entra y sale del sistema. logSguarDian se posiciona formalmente dentro de esta categoría: al ejecutarse como middleware dentro del mismo proceso Node.js que la aplicación protegida, tiene acceso directo al objeto `req` de Express ya parseado por el framework, sin necesidad de reimplementar la normalización de protocolo HTTP que un mecanismo externo debe resolver de forma genérica y, por definición, con menor información de contexto que la propia aplicación.

La arquitectura con la que históricamente se ha contrastado un RASP es el cortafuegos de aplicación web (WAF) de arquitectura perimetral, ejemplificado en este proyecto por ModSecurity operando con el OWASP Core Rule Set (CRS). Un WAF de este tipo se despliega como proxy inverso frente al servidor de aplicaciones e inspecciona cada petición mediante un conjunto de reglas de coincidencia de patrones y funciones de normalización, entre ellas la decodificación de URL, la remoción de espacios redundantes y la detección de sintaxis SQL mediante análisis léxico (*libinjection*), antes de reenviarla o bloquearla [18]. Su fortaleza es la cobertura inmediata de firmas de ataque conocidas sin requerir instrumentación de la aplicación protegida; su limitación estructural es que opera sin visibilidad del contexto interno de la aplicación –no conoce el modelo de datos, la lógica de negocio ni el resultado real de procesar la petición– y que su eficacia depende de que el atacante no logre evadir las reglas de normalización y coincidencia mediante técnicas de ofuscación del payload.

El Cuadro 3 contrasta ambas arquitecturas en las dimensiones relevantes para la decisión de diseño de este proyecto y para la interpretación de la Configuración 3 de la evaluación, en la cual ambas arquitecturas operan en capas sobre el mismo tráfico.

| **Dimensión** | **WAF perimetral (ModSecurity/CRS)** | **RASP embebido (logSguarDian)** |
|:---|:---|:---|
| Ubicación | Proxy inverso, proceso independiente | Middleware dentro del proceso de la aplicación |
| Visibilidad de contexto | Solo tráfico de red entrante/saliente | Objeto de petición ya parseado por el framework |
| Mecanismo de detección | Coincidencia de patrones y firmas sobre payload normalizado | Clasificación estadística sobre un vector de características extraído de la petición |
| Cobertura frente a variantes no vistas | Limitada a lo cubierto por las reglas de firma | El Isolation Forest registra anomalías y no bloquea; su aporte a la detección no se midió |
| Dependencia de infraestructura externa | Requiere proxy y mantenimiento de reglas | Ninguna; opera como dependencia de la aplicación |

Comparación entre arquitectura WAF perimetral y RASP embebida en las dimensiones relevantes para este proyecto. Elaboración propia a partir de [17] y [18].

## Ecosistema npm y seguridad en la cadena de suministro

logSguarDian se distribuye como un paquete del registro npm, la misma vía por la que la aplicación anfitriona obtiene la inmensa mayoría de sus dependencias. [19] documentan, mediante el análisis sistemático del grafo de dependencias de npm, que un paquete promedio confía implícitamente en 79 paquetes de terceros y 39 mantenedores distintos de forma transitiva, y que la ausencia de un proceso de revisión centralizado antes de la publicación permite que un único paquete comprometido –ya sea por una cuenta de mantenedor secuestrada o por código malicioso introducido deliberadamente– se propague a decenas de miles de proyectos que dependen de él directa o indirectamente. Este hallazgo tiene dos implicaciones directas para el diseño de logSguarDian.

La primera es una restricción de diseño: una librería cuyo propósito es proteger una aplicación no puede, sin contradecir ese propósito, introducir ella misma una superficie de ataque de cadena de suministro significativa. Esto motiva mantener el número de dependencias de tiempo de ejecución de logSguarDian deliberadamente acotado –`onnxruntime-node` para la inferencia, `better-sqlite3` para el almacenamiento local de eventos, y las dependencias del propio framework Express– en lugar de adoptar un ecosistema extenso de utilidades de terceros para funciones que pueden resolverse con la biblioteca estándar de Node.js. La segunda implicación es de alcance: la superficie de riesgo documentada por [19] corresponde a paquetes que ejecutan código arbitrario durante su instalación o su uso, un vector estructuralmente distinto de las cuatro categorías de inyección en tráfico HTTP cubiertas por este proyecto, razón por la cual la seguridad de la cadena de suministro de npm se documenta aquí como parte del contexto que motiva un diseño de dependencias mínimas, pero no como una categoría de ataque que el modelo de clasificación de logSguarDian esté diseñado para detectar.

## Panorama de ciberseguridad en Guatemala y el ecosistema tech local

La motivación de este proyecto, desarrollada con mayor detalle en el capítulo de Justificación, se apoya en una condición estructural del contexto en el que se ubica: un ecosistema de startups tecnológicas que opera predominantemente sin equipo de seguridad dedicado, en una región donde la exposición a ciberataques ha crecido de forma pronunciada en los años recientes. El informe de [15] documenta un incremento del 200% en ciberataques registrados en Guatemala entre 2023 y 2024, y ubica al país entre los diez de mayor exposición cibernética de Latinoamérica. Esta cifra no es, en sí misma, un antecedente técnico del diseño de logSguarDian –no informa decisiones de arquitectura, algoritmo o umbral– pero sí fundamenta la premisa sobre la cual se justifica la existencia del proyecto: que la brecha entre la superficie de ataque documentada por estándares como OWASP Top 10 [12] y la capacidad real de organizaciones pequeñas para mitigarla no es un escenario hipotético, sino una condición medible del entorno en el que logSguarDian está pensado para operar. Este panorama se retoma en el capítulo de Justificación para argumentar la relevancia social y económica del proyecto, y no se desarrolla aquí más allá de establecer el marco contextual en el que se inserta la motivación técnica de las secciones siguientes.

## Aprendizaje automático supervisado y no supervisado en ciberseguridad

El modelo híbrido de logSguarDian combina un clasificador supervisado y un detector de anomalías no supervisado, decisión que se fundamenta en la distinción formal establecida por [9]: la detección supervisada requiere ejemplos etiquetados de cada clase de anomalía que se desea reconocer y ofrece alta precisión sobre esas clases específicas, mientras que la detección no supervisada de una sola clase modela únicamente la distribución de lo normal y señala como anómalo cualquier punto que se aleje de ella, sin necesidad de haber observado ejemplos de la anomalía durante el entrenamiento. Ambos paradigmas son casos particulares de los métodos de ensamble, que [20] caracteriza como algoritmos que combinan las predicciones de múltiples modelos base para obtener un clasificador agregado cuyo error es, bajo condiciones razonables de diversidad entre los modelos base, menor que el de cualquiera de ellos por separado. Esta distinción formal es la que permite justificar, más adelante en este capítulo, por qué ninguno de los dos paradigmas por sí solo –supervisado o no supervisado– es suficiente como criterio único de bloqueo, y por qué logSguarDian los combina asignándoles roles distintos: el componente supervisado como única autoridad de bloqueo sobre las categorías de ataque conocidas, y el componente no supervisado como una capa complementaria de enriquecimiento de registro frente a variantes no vistas durante el entrenamiento.

### Random Forest

El componente supervisado es un Random Forest, introducido por [7] como un método que construye un ensamble de árboles de decisión mediante dos fuentes independientes de aleatoriedad: cada árbol se entrena sobre una muestra bootstrap distinta del conjunto de entrenamiento, y en cada nodo de división se evalúa únicamente un subconjunto aleatorio de las características disponibles en lugar de todas ellas. La predicción final se obtiene por voto mayoritario entre los árboles. Esta doble aleatorización reduce la correlación entre los árboles individuales y, con ella, la varianza del ensamble frente a un único árbol de decisión, sin requerir normalización previa de las características ni supuestos sobre su distribución. Estas dos propiedades –tolerancia a características de escalas heterogéneas y complejidad de inferencia lineal en el número de árboles– son la justificación técnica directa, documentada también en el capítulo de Antecedentes, de por qué Random Forest fue seleccionado frente a alternativas de mayor capacidad como las redes neuronales profundas para un componente que debe ejecutarse dentro del presupuesto de latencia de un middleware.

### Isolation Forest

El componente no supervisado es un Isolation Forest, propuesto por [8] bajo un principio distinto al de la mayoría de los detectores de anomalías de la época, que suelen modelar la densidad o la distancia entre puntos: en lugar de perfilar qué aspecto tiene un punto normal, Isolation Forest mide qué tan fácil es aislar un punto del resto mediante particiones aleatorias sucesivas del espacio de características. Una observación anómala, por estar más alejada de la masa de datos normales, requiere en promedio un número menor de particiones para quedar aislada en su propia hoja que una observación típica; esa longitud de camino promedio, normalizada, constituye el puntaje de anomalía. Esta propiedad hace que el algoritmo tenga la misma complejidad computacional lineal que Random Forest sin requerir el cálculo de distancias par a par que sí exigen otros métodos de detección de anomalías, lo cual lo hace compatible con las mismas restricciones de inferencia embebida que motivaron la selección del componente supervisado.

## Redes neuronales ligeras (MLP) y autoencoders

Antes de fijar Random Forest e Isolation Forest como los algoritmos del modelo híbrido, el diseño de logSguarDian consideró dos alternativas basadas en redes neuronales, ambas descritas formalmente por [21]. Un perceptrón multicapa (MLP) es una red neuronal compuesta por capas densas sucesivas de neuronas con una función de activación no lineal, entrenada mediante descenso de gradiente y retropropagación del error para aprender fronteras de decisión que un modelo lineal no podría representar; aplicado como componente supervisado, ofrecería una capacidad de representación mayor que un ensamble de árboles a costa de un proceso de entrenamiento más sensible a la escala de las características y de una arquitectura de inferencia basada en multiplicaciones de matrices en cada capa, cuyo costo computacional crece con la profundidad y el ancho de la red. Un autoencoder es una arquitectura no supervisada compuesta por un codificador que comprime la entrada a una representación de menor dimensión y un decodificador que intenta reconstruirla; entrenado únicamente sobre tráfico benigno, el error de reconstrucción sobre una entrada nueva sirve como puntaje de anomalía, dado que un error alto indica una entrada que la red no aprendió a representar bien porque difiere de la distribución de entrenamiento, de forma conceptualmente análoga al puntaje de aislamiento de Isolation Forest.

Ambas alternativas fueron consideradas y descartadas a partir de la lógica documentada en el capítulo de Antecedentes a partir de la revisión de [4], y la medición empírica de este proyecto sobre el mismo corpus y contrato de características usados en producción confirma esa lógica de forma desigual entre los dos componentes. Para el componente supervisado, Random Forest (macro F1=0.9776) iguala en la práctica a un MLP equivalente (macro F1=0.9719) con una latencia de inferencia menor (0.0062 ms frente a 0.0074 ms), de modo que la ganancia de precisión que ofrecería la red neuronal es marginal frente al costo adicional, mínimo pero medible, que introduce.

Para el componente no supervisado, la misma medición matiza la justificación original. Un autoencoder entrenado sobre el contrato de características de Isolation Forest iguala su recall y su tasa de falsos positivos (0.9158/0.0517 frente a 0.9125/0.0546) con una latencia de inferencia y un tamaño de modelo serializado órdenes de magnitud menores (0.0065 ms frente a 0.7441 ms; 19.3 KB (kilobytes) frente a 2.06 MB). Este costo diferencial no proviene de que Isolation Forest sea, como familia de algoritmo, más costosa que una red neuronal equivalente, sino de la configuración adoptada en producción –200 árboles con `max_samples=4096`, fijados por razones de estabilidad de calibración– y de que su exportación a ONNX resulta, en la práctica, un subgrafo menos eficiente que el de Random Forest. La decisión de mantener Isolation Forest se sostiene, entonces, por una razón arquitectónica distinta a la de costo bruto de inferencia: al no tener autoridad de bloqueo sobre la respuesta al cliente y ejecutarse de forma asíncrona en el *worker pool* dedicado documentado en el capítulo de Alcance, su latencia queda absorbida fuera del camino crítico de la petición, lo que hace que la comparación de latencia bruta sea menos determinante para este componente que para el supervisado. La consideración explícita de ambas alternativas, y no solo la ausencia de su implementación, es lo que permite documentar la selección de Random Forest e Isolation Forest como una decisión de diseño evaluada –y en el caso de Isolation Forest, sostenida por arquitectura y no por costo bruto– y no como la única opción contemplada.

## Ingeniería de características para datos de seguridad HTTP

Ningún algoritmo de aprendizaje automático opera directamente sobre un objeto de petición HTTP: requiere que ese objeto se transforme primero en un vector numérico de dimensión fija, proceso que [22] denominan ingeniería de características y describen como la etapa que determina en la práctica gran parte del desempeño final de un modelo, con independencia del algoritmo de clasificación elegido sobre esas características. Entre las técnicas que documentan y que logSguarDian adopta de forma directa se encuentran el conteo de ocurrencias de patrones específicos dentro de una cadena de texto (por ejemplo, el número de operadores lógicos SQL o de secuencias de ascenso de directorio dentro de un payload), la codificación de atributos categóricos –como el método HTTP o la presencia de un encabezado particular– mediante variables indicadoras, y la derivación de estadísticos simples sobre texto libre, como la longitud de una cadena o la proporción de caracteres no alfanuméricos que contiene.

El vector de 76 características de logSguarDian, descrito en detalle en el capítulo de Alcance y en la especificación de características del proyecto, aplica estos principios generales a seis grupos funcionales: semántica de ataque (marcadores de las cuatro categorías cubiertas), estructura HTTP, URL y ruta, parámetros y cuerpo, evasión por encoding y variables temporales. La adaptación específica de este proyecto frente al cuerpo general de técnicas documentado por [22] es la selección del objeto `req` de Express –y no un flujo de red o un documento de texto genérico– como fuente de esas características, decisión motivada por el vacío metodológico identificado en el capítulo de Antecedentes respecto a la ausencia de literatura de referencia sobre ingeniería de características a nivel de petición HTTP individual.

## Detección de anomalías y ataques de día cero

Un ataque de día cero, en el sentido más general en que el término se emplea en este trabajo –y no en su acepción más estricta de vulnerabilidad de software desconocida por el fabricante–, es una variante de payload que no se parece a ningún ejemplo visto durante el entrenamiento del componente supervisado: una técnica de ofuscación nueva, una combinación de operadores no representada en el corpus, o una categoría de ataque que ni siquiera fue anticipada como clase durante el diseño del modelo. Un clasificador puramente supervisado como Random Forest no tiene, por construcción, forma de reconocer una entrada que no se parezca a ninguna de las clases sobre las que fue entrenado: la asignará a la clase más cercana en el espacio de características, con una confianza que no refleja necesariamente qué tan atípica es esa entrada frente a la distribución de entrenamiento.

Esta limitación es la que motiva, siguiendo la distinción de [9] desarrollada en la sección anterior, la inclusión de Isolation Forest como una capa de detección complementaria que no depende de haber visto ejemplos previos de una técnica de ataque para señalarla como estadísticamente atípica. En logSguarDian, esta capacidad se documenta operando en dos escenarios distintos: como diagnóstico en tiempo real dentro del middleware –donde el puntaje de anomalía enriquece el registro de una petición sin constituir por sí solo un criterio de bloqueo– y, de forma más directa, dentro del pipeline de reentrenamiento continuo del proyecto, donde se registró una prueba de concepto del pipeline de reentrenamiento, cuyo resultado se describe en la sección 38.8 de Recomendaciones.

## Métricas de evaluación: F1-score, AUC-ROC y matriz de confusión

La evaluación de un clasificador de amenazas no puede apoyarse únicamente en la exactitud (*accuracy*), la proporción de predicciones correctas sobre el total, porque un corpus con clases fuertemente desbalanceadas –como es el caso de tráfico benigno frente a tráfico malicioso en un entorno realista– permite que un clasificador que etiquete todo como benigno obtenga una exactitud alta sin utilidad práctica alguna. Por esta razón, los Objetivos específicos de este proyecto se formulan en términos de precisión, recuperación (*recall*) y su combinación en el F1-score, calculadas a partir de la matriz de confusión de verdaderos positivos ($`VP`$), falsos positivos ($`FP`$), verdaderos negativos ($`VN`$) y falsos negativos ($`FN`$):

$$
\text{Precisión} = \frac{VP}{VP + FP} \qquad
\text{Recall} = \frac{VP}{VP + FN} \qquad
\text{F1} = 2 \cdot \frac{\text{Precisión} \cdot \text{Recall}}{\text{Precisión} + \text{Recall}}
$$

La precisión mide qué proporción de las peticiones bloqueadas por el modelo corresponden efectivamente a un ataque, y su complemento (uno menos la precisión, ponderado por la tasa de falsos positivos) es la métrica directamente relevante para el criterio de aceptación del componente no supervisado, dado que un Isolation Forest con una tasa de falsos positivos alta bloquearía tráfico legítimo con la misma frecuencia con la que detecta anomalías reales. El recall mide qué proporción de los ataques reales el modelo efectivamente detecta, y es la métrica directamente relevante para el criterio de cobertura del 80% por categoría de ataque establecido en el tercer objetivo específico. El F1-score, al ser la media armónica de ambas, penaliza a un clasificador que sacrifique una métrica para maximizar la otra –por ejemplo, bloqueando indiscriminadamente para maximizar recall a costa de la precisión– y es, por esta razón, la métrica elegida como criterio de aceptación del componente supervisado en el segundo objetivo específico. [23] formaliza además el análisis de curvas ROC (*Receiver Operating Characteristic*) y de su área bajo la curva (AUC) como herramienta complementaria para evaluar el compromiso entre tasa de verdaderos positivos y tasa de falsos positivos a través de distintos umbrales de decisión, principio aplicado en este proyecto durante la calibración del umbral de bloqueo del componente supervisado y del umbral de anomalía del componente no supervisado.

## Edge AI e inferencia en tiempo de ejecución con ONNX

La ejecución de modelos de aprendizaje automático dentro de un proceso con restricciones estrictas de latencia y memoria, sin comunicación con servicios externos, está documentada de forma consolidada en la literatura de Edge AI, cuyo texto de referencia es el de [11]. Los autores establecen los principios de diseño para desplegar modelos ligeros bajo presupuestos de memoria y tiempo de inferencia del orden de milisegundos, incluyendo técnicas de cuantización y formatos de serialización optimizados; esta disciplina, desarrollada casi en su totalidad sobre microcontroladores y dispositivos embebidos de hardware dedicado, provee el principio general que logSguarDian traslada a un dominio de ejecución distinto: el de un único proceso Node.js de un servidor de aplicaciones.

El entrenamiento de los modelos de logSguarDian se realiza en Python sobre *scikit-learn*, mientras que su inferencia en producción ocurre dentro de un proceso Node.js, dos entornos de ejecución sin compatibilidad binaria directa entre sí. Open Neural Network Exchange (ONNX) resuelve esta discontinuidad como un formato abierto de representación de modelos de aprendizaje automático, que define un grafo de cómputo y un conjunto de operadores estándar independientes del framework en el que el modelo fue entrenado [24], permitiendo que un modelo serializado en ONNX se ejecute mediante un motor de inferencia distinto (en este caso, *onnxruntime-node*) al que se usó para entrenarlo. Esta propiedad es la que hace viable, en primer lugar, entrenar los modelos híbridos de logSguarDian con el ecosistema maduro de *scikit-learn* en Python y, en segundo lugar, distribuirlos embebidos dentro de un paquete npm sin requerir que el proceso de inferencia dependa de un intérprete de Python en producción. La contrapartida de esta traducción entre representaciones es la necesidad de verificar que ambas produzcan predicciones equivalentes sobre las mismas entradas –verificación de paridad que este proyecto ejecuta de forma sistemática tras cada cambio de modelo, dado que una divergencia entre el modelo evaluado en Python y el modelo efectivamente servido en Node.js invalidaría las métricas reportadas en este trabajo.

Resta resolver, sin embargo, la restricción de concurrencia descrita en la sección de Node.js y Express de este capítulo: un motor de inferencia ONNX ejecutado de forma síncrona en el hilo principal bloquearía el Event Loop durante cada predicción. La documentación oficial de Node.js introduce `worker_threads` precisamente como el mecanismo para delegar trabajo de cómputo intensivo a hilos del sistema operativo independientes del Event Loop, comunicándose con el hilo principal mediante paso de mensajes en lugar de memoria compartida [16]. Este mecanismo es el fundamento técnico directo del primer objetivo específico del proyecto, que exige que el pipeline de ingeniería de características y la inferencia del modelo híbrido se ejecuten de forma asíncrona mediante `worker_threads` sin introducir una latencia adicional superior a 5 ms por petición en el servidor anfitrión, y de la arquitectura de *worker pool* dedicado documentada en el capítulo de Alcance. La librería declara Node.js 20 o superior en el campo `engines` de su paquete. El módulo `worker_threads` es estable desde la versión 12 de Node.js, pero esa versión no es el mínimo declarado por la librería.

## Construcción y etiquetado de datasets de tráfico HTTP

Entrenar un clasificador supervisado como Random Forest requiere un corpus en el que cada petición esté etiquetada con su categoría real, condición que logSguarDian resuelve mayoritariamente aprovechando la etiqueta ya asignada por la publicación original de cada dataset público que incorpora –SR-BH 2020/CAPEC, modsec-learn, registros de honeypot de ModSecurity, SecLists, PayloadsAllTheThings y varios conjuntos de Kaggle, entre otros; sus licencias se verificaron en la auditoría de datasets, salvo dos que no declaran licencia– sin necesidad de anotación manual adicional. Esta estrategia deja, sin embargo, un problema distinto sin resolver: ningún dataset público disponible cubre de antemano los vacíos de cobertura específicos que solo se hacen evidentes al validar el modelo ya entrenado –por ejemplo, un patrón de navegación benigna subrepresentado que un análisis de exclusión por fuente (LOSO) revela como punto débil, o una técnica de inyección de comandos cuya confianza de detección una prueba de ablación muestra insuficiente–. Para ese problema, distinto al de la etiquetación del corpus público, logSguarDian recurre a un suplemento acotado de tráfico sintético generado deliberadamente para cubrir cada vacío identificado.

[10] proponen el enfoque adoptado como base metodológica para ese suplemento: en lugar de etiquetar tráfico observado después de generarlo, se despliega un entorno de prueba controlado, se simula tráfico legítimo representativo y se ejecutan herramientas de ataque automatizadas de forma deliberada, de modo que la etiqueta de cada muestra se conoce de antemano por construcción –*ground truth by design*– y no por inferencia posterior. Este principio evita la necesidad de anotación manual y garantiza una correspondencia exacta entre la muestra y su etiqueta, a costa de que la representatividad de esa porción del corpus dependa enteramente de qué tan bien el entorno de prueba y las herramientas de generación aproximan el tráfico real que el sistema enfrentará en producción, supuesto que el capítulo de Alcance documenta explícitamente como una condición verificada mediante análisis exploratorio del corpus resultante.

logSguarDian aplica este mismo principio metodológico –despliegue de un entorno de prueba controlado mediante Docker Compose, simulación de tráfico benigno y ejecución deliberada de payloads de ataque– únicamente al suplemento sintético, dirigiéndolo además a un objeto distinto del que documenta la literatura de referencia sobre generación de datasets de intrusión: en lugar de capturar metadatos de flujo de red (duración de conexión, bytes transferidos, número de paquetes), como es el caso de los datasets de la familia CICIDS derivados de [10], cada muestra sintética del corpus de logSguarDian es un vector de características extraído del objeto `req` de Express mediante el mismo pipeline de ingeniería de características que se ejecuta en producción, descrito en la sección correspondiente de este capítulo, y ese mismo pipeline se aplica después sobre las muestras de origen público para producir un vector de entrada homogéneo con independencia de la procedencia de cada fila. Esta adaptación es la que permite que el corpus de entrenamiento sea representativo de la semántica de una petición HTTP individual y no únicamente de patrones de tráfico a nivel de conexión.

## Síntesis: articulación de los fundamentos en la arquitectura de logSguarDian

Los fundamentos desarrollados en este capítulo no son piezas de conocimiento independientes: se articulan directamente en las decisiones de diseño de logSguarDian. La caracterización de las cuatro categorías de ataque como fenómenos intra-request delimita la unidad de análisis del sistema a una petición HTTP individual, y el modelo de middleware de Express sobre el Event Loop de un solo hilo de Node.js define tanto el punto de integración de logSguarDian como su restricción de latencia más estricta. La distinción entre arquitectura perimetral y arquitectura RASP embebida fundamenta la decisión de operar dentro del proceso de la aplicación en lugar de como proxy independiente, mientras que la seguridad de la cadena de suministro de npm y el panorama de ciberseguridad del contexto local delimitan, respectivamente, una restricción de diseño sobre las dependencias del proyecto y la motivación de su existencia. La complementariedad entre detección supervisada y no supervisada fundamenta la combinación de Random Forest e Isolation Forest en un modelo híbrido –evaluada frente a las alternativas de redes neuronales descritas en este capítulo, y sostenida en un caso por su costo de inferencia y en el otro por su arquitectura de ejecución asíncrona– y provee el mecanismo conceptual de detección de variantes de día cero. Los principios generales de ingeniería de características se adaptan al objeto de petición de Express para producir el vector de entrada de ambos modelos, entrenados sobre un corpus compuesto predominantemente por datasets públicos con etiqueta propia y complementado con un suplemento sintético construido bajo el principio de etiquetado determinista documentado en la literatura de generación de datasets de intrusión, y evaluados con las métricas de precisión, recall y F1-score que expresan formalmente los criterios de aceptación de los objetivos específicos de este trabajo. Finalmente, ONNX y `worker_threads` resuelven, respectivamente, la discontinuidad entre el entorno de entrenamiento en Python y el entorno de inferencia en Node.js, y la restricción de concurrencia de un solo hilo bajo la cual ese entorno de inferencia debe operar sin degradar el servicio que protege.

# Metodología

## Enfoque y tipo de investigación

Este trabajo se desarrolla bajo un enfoque de investigación aplicada y de tipo experimental. Es aplicada porque su resultado no es una contribución teórica independiente, sino un artefacto de software concreto y utilizable: la librería npm logSguarDian, con su pipeline de ingeniería de características y su modelo híbrido integrados en un middleware funcional para aplicaciones Express. Es experimental porque la validez de ese artefacto no se argumenta de forma discursiva, sino que se somete a criterios de aceptación predefinidos y cuantificados –los umbrales de F1-score, recall y tasa de falsos positivos establecidos en los objetivos específicos de este trabajo– verificados empíricamente sobre un conjunto de prueba bloqueado y sobre un entorno de evaluación controlado y reproducible.

La combinación de ambos rasgos –construcción de artefacto y validación empírica contra criterios de aceptación predefinidos– responde directamente al vacío metodológico identificado en el capítulo de Antecedentes: la literatura de referencia en detección de intrusiones mediante aprendizaje automático privilegia consistentemente los datasets de flujo de red heredados sobre la semántica de peticiones HTTP individuales, y ni las revisiones más recientes de arquitecturas híbridas supervisadas/no supervisadas ni las revisiones sistemáticas de cortafuegos de aplicación web potenciados por inteligencia artificial documentan, entre los estudios que cubren, un sistema implementado bajo una arquitectura embebida dentro del proceso de una aplicación Node.js con recursos limitados. Al no existir un antecedente documentado que combine un modelo híbrido de aprendizaje automático con las restricciones de latencia, memoria y concurrencia de un solo hilo propias de un middleware Node.js, este trabajo no puede apoyarse en un diseño experimental replicado de la literatura: requiere construir el artefacto y definir sus propios criterios de aceptación, y de ahí que el tipo de investigación aplicada-experimental sea la clasificación que corresponde al problema, y no una alternativa entre varias igualmente válidas.

## Metodología de trabajo y fases

El desarrollo del proyecto se organizó en seis fases secuenciales, cada una con una disciplina operativa asociada y un artefacto verificable como criterio de cierre (regla R3 del proyecto: ninguna fase se da por completa sin un número reproducible, una prueba que pasa, o un archivo committeado que la respalde).

**Fase 1 — Construcción del pipeline de ingeniería de características (20 de junio – 1 de agosto de 2026, objetivo específico 1).** Se implementó, en TypeScript, la extracción y vectorización de un vector de 76 características numéricas a partir del objeto `req` de Express, ejecutada de forma asíncrona mediante *worker_threads* para no bloquear el *Event Loop* del proceso anfitrión (implementación inicial a cargo de Sebastián Huertas; véase la sección 36.7). Esta fase está gobernada por la regla R1 del proyecto: la extracción de características vive únicamente en `packages/extractor` (TypeScript); ningún componente en Python recalcula features a partir de datos crudos, sino que consume matrices ya extraídas por el CLI del extractor. Esta disciplina se verificó de forma explícita incluso en la evaluación final del modelo (`training/evaluate_test.py`), donde la selección de columnas se realiza por nombre contra la lista canónica `FEATURE_NAMES` copiada literalmente del extractor TypeScript, en lugar de inferir el vector de entrada por descarte posicional. El artefacto de cierre de esta fase es el benchmark de latencia del extractor. Su p95 mixto con *worker_threads* es de 0.0273 ms (mediana de tres corridas), muy por debajo del límite de 5 ms establecido en el objetivo específico 1 (Cuadro 37.1).

**Fase 2 — Construcción del corpus de entrenamiento.** Se ensambló un corpus a partir de nueve conjuntos públicos evaluados en la auditoría (ocho incluibles, uno excluido por incompatibilidad de taxonomía de etiquetas), con licencia y procedencia verificadas y documentadas en la auditoría de datasets del proyecto, complementado con un suplemento sintético acotado generado mediante Docker Compose para cerrar vacíos de cobertura detectados mediante análisis de exclusión por fuente (*Leave-One-Source-Out*) y pruebas de ablación sobre el corpus público, nunca como base primaria del corpus. Esta fase cierra con la deduplicación del corpus y el bloqueo criptográfico del conjunto de prueba (`training/splits/test.lock.sha256`), que activa la regla R2: el conjunto de prueba se lee una sola vez para la evaluación final de cada generación de modelo, y ninguna decisión de ajuste posterior a esa lectura puede modificarse en función de los resultados observados en él. La generación v11 incumplió esta regla, como se detalla más adelante en este capítulo.

**Fase 3 — Entrenamiento y calibración del modelo híbrido.** El entrenamiento de Random Forest e Isolation Forest se realizó íntegramente en Python sobre hardware Apple Silicon local, sin dependencia de infraestructura de cómputo en la nube. La selección de los umbrales de decisión se realizó sobre el conjunto de validación. En dos versiones de Isolation Forest esa selección se revisó después de leer el conjunto de prueba: en `if_v2`, la confirmación arrojó una tasa de falsos positivos de 0.1011 frente a un límite de 0.10, y el objetivo de calibración pasó a FP $`\leq`$ 0.08; en `if_v5`, la primera confirmación arrojó 0.0811 frente a un objetivo interno de 0.08, y el objetivo se endureció a FP $`\leq`$ 0.06. En ambos casos el umbral final se seleccionó sobre validación, pero el conjunto de prueba influyó en el criterio de calibración. El umbral de `if_v10` se calibró sobre validación con recall $`\geq`$ 0.50 y FP $`\leq`$ 0.06, y el de Random Forest (`RF_THRESHOLD` = 0.35) se calibró sobre validación para `rf_v3` y se mantuvo sin recalibración para `rf_v11`.

**Fase 4 — Verificación de paridad ONNX.** Ambos modelos se serializaron a formato ONNX mediante `sklearn2onnx`, y su paridad de predicción frente al modelo original en `scikit-learn` [25] se verificó de forma automatizada (`training/models/parity_report.json`), confirmando diferencias de probabilidad en el orden de $`10^{-7}`$ entre ambos entornos de inferencia antes de habilitar el modelo serializado para su integración.

**Fase 5 — Integración en el middleware.** El modelo serializado se integró en la librería npm mediante `onnxruntime-node`, ejecutado en una arquitectura de *worker pool* dedicado (un worker para Random Forest y dos workers para Isolation Forest en hilos separados), diseño adoptado tras confirmar empíricamente que `onnxruntime-node` serializa las llamadas de inferencia concurrentes dentro de un mismo hilo nativo. Esta fase cierra con la evaluación del modelo híbrido sobre el conjunto de prueba bloqueado (objetivo específico 2, cierre 2 de agosto de 2026).

**Fase 6 — Evaluación en tres configuraciones progresivas (2 de agosto – 30 de septiembre de 2026, objetivo específico 3).** La librería integrada como middleware se evaluó en un entorno de prueba controlado (Docker Compose) bajo tres configuraciones sucesivas: sin protección, con logSguarDian como única capa, y en defensa en profundidad junto con un Web Application Firewall perimetral. El refinamiento iterativo del modelo continuó dentro de esta fase –incluyendo el ciclo de reentrenamiento que atendió los vacíos de cobertura de la categoría de inyección de comandos detectados durante la evaluación– sin alterar los criterios de aceptación establecidos en los objetivos específicos.

## Técnicas e instrumentos

La técnica central de la fase de construcción del modelo es la ingeniería de características sobre el objeto `req` de Express: un vector de 76 dimensiones organizado en grupos funcionales orientados a capturar los marcadores semánticos de las cuatro categorías de ataque cubiertas (inyección SQL, *cross-site scripting*, recorrido de directorios e inyección de comandos), además de características estadísticas transversales (longitud, entropía de Shannon, proporción de caracteres especiales) y metadatos de la petición (método HTTP, encabezados, indicadores de codificación). Conviene distinguir aquí lo que el extractor produce de lo que cada modelo efectivamente consume: de esas 76 dimensiones, el componente Random Forest consume 69 y el componente Isolation Forest 63, tras excluir en cada caso las variables no disponibles en el momento de la intercepción de la petición (código de estado de respuesta, contadores de frecuencia por ventana temporal), las variables con varianza próxima a cero sobre tráfico benigno en el caso de Isolation Forest, y –en ambos modelos, de forma temporal– la característica más reciente del extractor (`non_json_quote_count`, que descuenta las comillas de sintaxis JSON del conteo de comillas del payload). Esta última se excluye no por invalidez, sino porque su incorporación al vector de entrada de los modelos en producción implica un reentrenamiento completo, y esa promoción es una decisión pendiente y deliberadamente separada de su adición al extractor.

El Cuadro 36.1 enumera los seis grupos funcionales y el número de variables que contiene cada uno, según la tabla de features de la especificación del extractor.



<table id="tabla:grupos-features">
<caption>Grupos de características del vector de 76 dimensiones, con el número de variables de cada uno.</caption>
<thead>
<tr>
<th style="text-align: center;">**Grupo**</th>
<th style="text-align: left;">**Descripción**</th>
<th style="text-align: center;">**Variables**</th>
<th style="text-align: left;">**Posiciones en la especificación**</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;">A</td>
<td style="text-align: left;">Semántica de ataque (SQLi, XSS, *path traversal*, CmdI)</td>
<td style="text-align: center;">37</td>
<td style="text-align: left;">#26–#62</td>
</tr>
<tr>
<td style="text-align: center;">B</td>
<td style="text-align: left;">Estructura HTTP</td>
<td style="text-align: center;">9</td>
<td style="text-align: left;">#63–#71</td>
</tr>
<tr>
<td style="text-align: center;">C</td>
<td style="text-align: left;">URL y ruta</td>
<td style="text-align: center;">6</td>
<td style="text-align: left;">#3–#5, #8–#10</td>
</tr>
<tr>
<td style="text-align: center;">D</td>
<td style="text-align: left;">Parámetros y cuerpo (composición del payload)</td>
<td style="text-align: center;">9</td>
<td style="text-align: left;">#1, #2, #6, #7, #11–#14, #18</td>
</tr>
<tr>
<td style="text-align: center;">E</td>
<td style="text-align: left;">Evasión por encoding y caracteres</td>
<td style="text-align: center;">10</td>
<td style="text-align: left;">#15–#17, #19–#25</td>
</tr>
<tr>
<td style="text-align: center;">—</td>
<td style="text-align: left;">Temporales (ventanas de 1, 5 y 60 segundos)</td>
<td style="text-align: center;">5</td>
<td style="text-align: left;">#72–#76</td>
</tr>
<tr>
<td colspan="2" style="text-align: left;">**Total**</td>
<td style="text-align: center;">**76**</td>
<td style="text-align: left;"></td>
</tr>
</tbody>
</table>


Fuente: `docs/feature-spec.md` del repositorio logSguarDian, rama `docs/feature-spec-76`. Elaboración propia.

Las variables temporales (#72–#76) no son consumidas por ninguno de los dos modelos, porque requieren estado compartido entre peticiones que el extractor no mantiene por diseño. Tampoco lo son `status_code` (#71), que no existe al interceptar la petición, ni `non_json_quote_count` (#32). Random Forest consume así 69 variables; Isolation Forest consume 63, tras excluir además `null_byte_count`, `sensitive_file_target`, `dotdot_encoded_count`, `os_path_indicator`, `authorization_length` y `unusual_headers_count`.

Sobre ese vector opera el modelo híbrido de aprendizaje automático descrito en el Marco Teórico: Random Forest [7] como componente supervisado, encargado de clasificar cada petición en una de las cuatro categorías de ataque cubiertas o como tráfico legítimo, e Isolation Forest [8] como componente no supervisado, entrenado únicamente sobre tráfico benigno para aportar una señal complementaria de detección de anomalías estadísticas frente a variantes no vistas durante el entrenamiento. La justificación teórica de esta combinación –la complementariedad entre detección supervisada y no supervisada de una sola clase [9], y la selección de métodos de ensamble ligeros frente a alternativas de redes neuronales de mayor capacidad– se desarrolla en el Marco Teórico y no se repite aquí; esta sección se limita a documentar su aplicación instrumental. En su forma ONNX publicada, `rf.onnx` pesa 8.90 MB e `if.onnx` 2.16 MB.

El instrumental de construcción y despliegue del modelo comprende `scikit-learn` [25] para el entrenamiento de ambos algoritmos, `sklearn2onnx` para su serialización a formato ONNX [24], `onnxruntime-node` como motor de inferencia embebido en el proceso Node.js, y Docker Compose para levantar tanto el entorno de generación de tráfico sintético (fase 2) como el entorno de prueba vulnerable de las tres configuraciones de evaluación (fase 6). La restricción de recursos de este instrumental –modelos de ensamble de complejidad computacional acotada, entrenados y servidos sin infraestructura de cómputo en la nube– es consistente con la disciplina de inferencia embebida bajo restricciones de memoria y latencia documentada en la literatura de Edge AI [11].

Como técnica de interpretabilidad se empleó SHAP, específicamente su explicador `TreeExplainer` sobre el modelo Random Forest, en dos modalidades complementarias: importancia global por clase, calculada sobre el conjunto de validación para identificar las diez características con mayor contribución promedio a cada categoría de ataque, y explicación local de casos individuales, empleada para diagnosticar el comportamiento del modelo frente a peticiones específicas (por ejemplo, el efecto de la presencia o ausencia de encabezado *User-Agent* sobre la puntuación de Isolation Forest). Los casos locales analizados mediante esta técnica se documentan con su evidencia numérica en el capítulo de Resultados. El análisis se calculó sobre `rf_v11.pkl` tras la corrección de trazabilidad de artefactos descrita en la sección de Recolección, procesamiento y validación de datos, por lo que las características y casos que explica corresponden al modelo efectivamente evaluado en este capítulo. La importancia global confirma que los encabezados de *User-Agent* (`ua_present`, `ua_length`) figuran entre las características de mayor contribución no solo para la calibración de Isolation Forest ya documentada, sino también para la clasificación de Random Forest en las categorías `benign`, `sqli` y `path_traversal`, con una contribución más débil, aunque presente, en `cmdi` y `xss`. Este predominio es desigual entre clases: es más marcado en tres de las cinco categorías y no debe leerse como uniforme. Para `cmdi`, el análisis aporta evidencia cuantitativa adicional sobre la dificultad de separabilidad ya documentada: incluso sobre el modelo corregido, las dos características de mayor contribución para esta clase (`method_is_get`, `ua_length`) no son marcadores semánticos de inyección de comandos, y solo una característica semántica relacionada (`subshell_count`) figura entre las diez de mayor peso; `shell_command_count` y `pipe_count`, pese a formar parte del vector de entrada, no se encuentran entre las diez principales. Esto es consistente con, aunque no idéntico a, la dificultad estructural ya identificada entre `cmdi` y `path_traversal`, y se documenta aquí como un hallazgo parcialmente resuelto, no cerrado.

### Pares de modelos evaluados

El paquete publicado y los modelos sobre los que se midieron las métricas de este trabajo no son el mismo par. Las métricas del capítulo de Resultados corresponden al par C, mientras que el paquete `logsguardian@0.1.0` del registro contiene el par A. El Cuadro 36.2 identifica cada par por el SHA-256 de sus archivos ONNX y registra en qué evaluaciones se usó.



| **Par** | **Modelos** | **SHA-256 (`rf.onnx` / `if.onnx`)** | **Origen** | **Evaluaciones en que se usó** |
|:--:|:---|:---|:---|:---|
| A | `rf_v10` / `if_v9`, 67 y 61 características | `18083725…` / `5de374a7…` | Commit `dc2aaa65`, 2 de agosto de 2026 | Paquete publicado `logsguardian@0.1.0` (30 de agosto de 2026, commit `c3d591a`); Configuraciones 2, 3a y 3b sobre los 590 payloads (Ronda 4, 15 de agosto de 2026; sobre el solapamiento de ese corpus con el entrenamiento, véase la sección 37.3.5)<sup>4</sup>; Configuración 2 sobre 100 payloads por categoría (6 de agosto de 2026; el modelo consta en `docs/config2-latency-evaluation.md`, sin hash); Ronda 5 con el paquete publicado<sup>3</sup>; estudio de User-Agent de la aplicación vulnerable del proyecto (24 de septiembre)<sup>1</sup> |
| B | `rf_v11` / `if_v10`, primera versión, 69 y 63 características | `a7c015f5…` / `3cf8e45c…` | Commit `734c24f`, 30 de agosto de 2026 | Primera lectura del conjunto de prueba (24 de septiembre); repetición de Config 2 sobre los 590 payloads (9 de septiembre)<sup>1</sup>; experimento de latencia, memoria y CPU en Linux nativo |
| C | `rf_v11` / `if_v10`, reentrenamiento, 69 y 63 características | `25b407e6…` / `5be28ee8…` | Commit `03de50f`, 26 de septiembre de 2026 | Lecturas del 25 y 26 de septiembre del conjunto de prueba; paridad ONNX; análisis SHAP; Ronda 5 (9 de octubre de 2026) con el tarball de validación del commit `22550ea` (SHA-256 `cf1238…`; véase la sección 37.3.6)<sup>3</sup>; copia de Juice Shop<sup>2</sup> |

Pares de modelos evaluados, con su origen y las evaluaciones en que se usó cada uno.


Notas: (1) El JSON de resultados de la repetición de Config 2 del 9 de septiembre y el del estudio de User-Agent no registran el modelo. Su atribución se apoya en el mensaje del commit `14c0e15` de la aplicación vulnerable del proyecto, que actualizó los modelos a `rf_v11`/`if_v10`, y en el contenido de `models/` en el commit del estudio (`5966712`). (2) De las aplicaciones de terceros DVNA, node-api-goat y dvws-node no consta el modelo exacto de cada medición; solo la medición de Juice Shop usa una copia cuyo modelo sí consta. (3) La Ronda 5 con el paquete publicado se atribuye al par A según `docs/config3b-results.md` de la aplicación vulnerable del proyecto (rama main); el mismo documento atribuye el tarball del commit `22550ea` al par C. Los tres archivos se denominan `logsguardian-0.1.0.tgz`, pero son distintos: el paquete publicado contiene el par A, y el tarball de validación y la copia local de Juice Shop, no publicados, contienen el par C. Los nombres usados en este documento son: *paquete publicado en npm* (`logsguardian@0.1.0`, par A); *tarball de validación del commit 22550ea* (SHA-256 , par C); y *copia local de Juice Shop* (SHA-256 , par C). (4) La Configuración 1 no usa los modelos, porque la aplicación no tiene protección; en las Rondas 1 a 3, con corpus pequeño, el modelo no consta en los resultados. Hashes completos: par A, `rf.onnx` e `if.onnx` ; par B, `rf.onnx` e `if.onnx` ; par C, `rf.onnx` e `if.onnx` .

### Validación en aplicaciones de terceros

La validación con una startup guatemalteca, prevista en el protocolo, era opcional y no se realizó. Por recomendación del asesor, Ing. Erick Francisco Marroquín Rodríguez, el sistema se evaluó en cuatro aplicaciones vulnerables de terceros: DVNA, node-api-goat, dvws-node y OWASP Juice Shop. En las tres primeras se usó el middleware en modo `block` con la configuración por defecto (`RF_THRESHOLD=0.35`), y se enviaron ataques reales junto con tráfico benigno. En OWASP Juice Shop se usó el modo `monitor` y solo se enviaron peticiones benignas, porque con la tasa de falsos positivos observada no se generó corpus de ataque para esa aplicación. En esa misma aplicación se comparó el efecto del encabezado *User-Agent*, con un valor de navegador y con `curl`. Los resultados se presentan en la sección 37.3.7.

## Recolección, procesamiento y validación de datos

El corpus final reúne 383 202 filas de 17 fuentes: 268 240 en entrenamiento, 57 481 en validación y 57 481 en prueba. Siete provienen de conjuntos públicos auditados (CAPEC, modsec-learn, registros de ModSecurity [26], Payloads.csv, payload_full, XSS_dataset y command injection), dos de listas públicas de payloads (SecLists[27] y PayloadsAllTheThings[28], ambas con licencia MIT), siete de generadores propios y una de telemetría curada del pipeline de MLOps. La auditoría evaluó nueve conjuntos: ocho se consideraron incluibles y uno se excluyó por incompatibilidad de taxonomía de etiquetas (AIT-LDSv2, porque sus etiquetas describen roles del atacante y no tipos de payload). Uno de los ocho, omurugur, no se incorporó al corpus final. Las licencias de los conjuntos auditados se verificaron con las API de Zenodo, Harvard Dataverse y GitHub y con los metadatos de Kaggle; dos conjuntos quedan con licencia desconocida (`XSS_dataset` y `command injection`). Ese suplemento sintético no es una fuente primaria del corpus, sino un conjunto de correcciones dirigidas: `synthetic_nav` y `synthetic_nav_ecommerce` se generaron para cerrar un vacío de generalización sobre tráfico benigno de navegación pura detectado mediante *Leave-One-Source-Out* (`synthetic_nav` resultó ser, antes de esa corrección, la fuente con peor F1 al excluirla del entrenamiento, por carecer de redundancia con el resto del corpus); `synthetic_multifield` se generó para reforzar la señal de formularios multi-campo tras el hallazgo del bug de desempate en `extractBestPayload`; y `synthetic_cmdi_minimal_context`, `synthetic_cmdi_windows` y `synthetic_cmdi_compound` se generaron específicamente para cerrar los vacíos de separabilidad de la categoría de inyección de comandos identificados mediante pruebas de ablación, descritos con su justificación completa en el Marco Teórico y en la sección de limitaciones documentadas del proyecto. En ningún caso el suplemento sintético sustituye al corpus público como base del entrenamiento: cada adición está motivada por un hallazgo específico de cobertura, no por una decisión general de completar el corpus con datos generados.

La validación del corpus antes de su uso comprendió dos procedimientos concretos. El primero es la verificación de licencias: en los dos casos donde el propio proveedor (Kaggle) reporta la licencia como no especificada (`XSS_dataset.csv` y `command injection.csv`), esa ausencia se documenta explícitamente como tal en lugar de asumir una licencia permisiva por defecto. El segundo es la detección de duplicados casi idénticos mediante MinHash, con *banding* de LSH ajustado explícitamente (`num_perm=128`, `params=(8,16)`) frente a la configuración por defecto derivada del umbral, que resultaba intratable en tiempo de cómputo sobre las clases de mayor volumen. Esta técnica confirmó una saturación de duplicados genuina y considerable en las cinco clases del corpus, con la clase `sqli` alcanzando aproximadamente 395 veces más pares casi-duplicados que filas (dominada por generación template de `sqlmap`/CAPEC) y la clase `benign` mostrando la saturación más baja de las cinco (aproximadamente 9.5 veces), consistente con tráfico real de cola larga en lugar de contenido generado por plantilla. La decisión tomada fue de marcado sin eliminación (*flag-only*): no deduplicar el corpus para esta generación de modelos, dado que remover filas constituye una decisión de reconfiguración del balance de clases que requiere su propia estrategia de reentrenamiento, independiente de los ajustes de features o umbrales de esta generación, y que la cuantificación completa de la saturación (incluyendo las clases `sqli` y `benign`, antes sin medir por completo dado el costo computacional del escaneo) no altera esa decisión, solo la vuelve una decisión informada por evidencia completa en lugar de parcial.

El procesamiento del corpus hacia los conjuntos de entrenamiento, validación y prueba sigue un procedimiento secuencial y verificable, no una descripción abstracta de buenas prácticas: primero, la unificación de las fuentes dispares en un esquema común de columnas; segundo, la extracción del vector de 76 características (de las cuales 69 alimentan a Random Forest y 63 a Isolation Forest, según se detalla en la sección de Técnicas e instrumentos) sobre cada registro unificado mediante el mismo CLI del extractor TypeScript usado en producción (regla R1: nunca se recalculan features en Python); tercero, la partición en conjuntos de entrenamiento, validación y prueba; cuarto, el bloqueo criptográfico del conjunto de prueba mediante un hash SHA-256 committeado al repositorio (`training/splits/test.lock.sha256`) antes de iniciar cualquier entrenamiento; y quinto, el entrenamiento y calibración de ambos modelos exclusivamente contra los conjuntos de entrenamiento y validación. La regla R2 –el conjunto de prueba se lee exactamente una vez para la evaluación final de cada generación de modelo– no es una declaración de intención sino un procedimiento verificable en el propio repositorio: la evaluación final de `rf_v11`/`if_v10` (`training/evaluate_test.py`) recalcula el hash del conjunto de prueba restaurado y lo compara contra el valor bloqueado antes de ejecutar cualquier inferencia, abortando si no coinciden; el resultado de esa verificación (`lock_verified: true`) queda registrado junto con las métricas en `training/results/v11_test_results.json`. Para la generación v11, el conjunto de prueba se leyó en tres ocasiones, por lo que el criterio de lectura única de R2 no se cumplió. El 24 de septiembre de 2026 se evaluó el modelo entrenado el 30 de agosto (macro F1 de 0.9843) sobre el conjunto re-bloqueado el 23 de septiembre; el repositorio no conserva la huella de la partición con que ese modelo se entrenó, por lo que no puede descartarse solapamiento. El 25 de septiembre se evaluó un modelo reentrenado sobre la partición vigente, como parte de la comparación con MLP y autoencoder. El 26 de septiembre se evaluó el modelo vigente en el repositorio, reconstruido con el mismo procedimiento porque el artefacto serializado original había sido sobrescrito. Estas dos últimas lecturas coinciden en macro F1 (0.9776) y sus predicciones sobre validación son idénticas. Las métricas de este capítulo corresponden a la lectura del 26 de septiembre. El historial no registra ninguna decisión de modelado atribuida al resultado de la primera lectura. El umbral de Isolation Forest de la primera lectura (0.00807) corresponde al modelo del 30 de agosto; el de las dos siguientes (0.00421), al modelo reentrenado, cuyo umbral se calculó sobre validación. El historial no atribuye ese cambio al resultado de la primera lectura, pero no puede descartarse su influencia. La confirmación en prueba del umbral de 0.35 con `rf_v3`, afirmada en el commit `e74a8c6`, no tiene artefacto de respaldo en el repositorio. Dos limitaciones adicionales: 261 de las 1 468 filas de `cmdi` del conjunto de prueba (17.8 %) son sintéticas y su generador no está versionado, y la fuente de los datos restaurados el 23 de septiembre no está documentada.

Durante la preparación de este capítulo se detectó y corrigió una brecha de trazabilidad de artefactos en el pipeline de evaluación, documentada aquí por transparencia metodológica. El archivo `training/models/rf_v11.pkl`, al no estar bajo control de versiones, fue sobrescrito silenciosamente por una versión candidata –generada durante una investigación no relacionada sobre diversificación de tráfico benigno sintético, y explícitamente no promovida a producción– bajo el mismo nombre de archivo. Esto dejó huérfano el emparejamiento exacto entre modelo y conjunto de prueba que una evaluación previamente citada había medido: el mecanismo de bloqueo criptográfico del conjunto de prueba en sí no se violó (ancla la identidad de cada fila, no el valor de sus características, por lo que es correctamente invariante a cambios del extractor), pero ninguna suma de verificación vinculaba una métrica citada con el contenido exacto, byte a byte, del par modelo/conjunto de prueba que la produjo. Reentrenados `rf_v11`/`if_v10` contra el contrato de 69/63 features vigente en producción (`parity_report.json`) y evaluados sobre el conjunto de prueba correctamente re-bloqueado, las cifras reportadas en este capítulo corresponden a la lectura del 26 de septiembre de 2026; el mismo conjunto se había leído también el 24 de septiembre (commit `3086318`) y el 25 de septiembre de 2026 (commit `fc47a5b`). Como salvaguarda estructural se incorporaron tres mecanismos: un manifiesto de sumas de verificación sha256 (conjunto de prueba y ambos modelos ONNX) que acompaña ahora cada evaluación citada; una extensión del pipeline de integración continua de entrenamiento que respalda y restaura `training/splits/` de la misma forma en que ya protegía `training/models/`; y el paso de `rf_v11.pkl`/`rf_v11_metadata.json` a control de versiones, para que el modelo efectivamente evaluado no pueda volver a sobrescribirse sin dejar rastro.

## Métricas e indicadores

Ninguna métrica de este trabajo se reporta como *accuracy* global. El corpus es fuertemente desbalanceado –la clase `benign` y la clase `sqli` concentran, entre las dos, más de la mitad de los registros, mientras que `cmdi` es la categoría de ataque con menor representación– y bajo ese desbalance un clasificador que prediga siempre la clase mayoritaria obtendría una *accuracy* alta sin haber aprendido a distinguir ninguna categoría de ataque. Por esa razón, cada componente del sistema se evalúa con la métrica que corresponde a su naturaleza –clasificación multiclase supervisada en un caso, detección de anomalías de una sola clase en el otro– y no con una métrica agregada que oculte ese desbalance.

Para Random Forest, la métrica de aceptación es el F1-score por clase: la media armónica de precisión y recall, que penaliza específicamente el sacrificio de una a expensas de la otra, a diferencia de reportar ambas por separado o de promediarlas aritméticamente. Esto importa de forma directa para este sistema: un modelo que maximizara solo precisión bloquearía pocas peticiones legítimas pero dejaría pasar ataques (bajo recall), y uno que maximizara solo recall bloquearía tráfico legítimo con frecuencia inaceptable para un middleware de producción (baja precisión); el F1-score es la métrica que exige un balance entre ambos costos operativos. El objetivo específico 2 fija el criterio de aceptación en F1-score mínimo de 0.80 en al menos tres de las cuatro categorías de ataque cubiertas, y no en las cuatro, en reconocimiento explícito de la dificultad estructural de separabilidad de `cmdi` documentada en el Marco Teórico y en las limitaciones del proyecto: la sintaxis de inyección de comandos comparte marcadores léxicos (rutas de sistema de archivos, operadores de redirección) con la categoría de recorrido de directorios, lo cual reduce estructuralmente su separabilidad frente a las otras tres categorías, cuyos marcadores semánticos son más distintivos entre sí. El umbral de tres de cuatro clases no es, por tanto, una relajación arbitraria del criterio, sino el reconocimiento de una dificultad de separabilidad ya documentada antes de fijar el criterio de aceptación.

Sobre el conjunto de prueba bloqueado, la generación de modelos vigente (`rf_v11`/`if_v10`) alcanza un F1-score macro de 0.9776, con F1 por clase de 0.9984 (`benign`), 0.9239 (`cmdi`, precisión 0.9015 / recall 0.9475), 0.9826 (`path_traversal`), 0.9956 (`sqli`) y 0.9877 (`xss`) –superando en las cinco clases el umbral de 0.80 del objetivo específico 2, incluida la clase estructuralmente más difícil–. Como evidencia complementaria se calculó también el área bajo la curva ROC uno-contra-el-resto [23] para cada clase, con valores entre 0.99899 y 0.99998, que confirma que la separación entre clases no depende del punto de corte de probabilidad elegido para la decisión de bloqueo. Las métricas por clase se calculan sobre la clase de mayor probabilidad (argmax), sin el umbral de confianza de 0.35 con el que el sistema decide el bloqueo; no se calculó una métrica de prueba con la regla de decisión desplegada.

Para Isolation Forest, la métrica de aceptación es distinta por diseño: recall de detección de anomalías y tasa de falsos positivos sobre tráfico benigno, no F1-score. La razón es la naturaleza no supervisada del componente: Isolation Forest se entrena únicamente sobre tráfico benigno y no tiene conocimiento de las categorías de ataque como clases distintas, por lo que no existe una matriz de confusión multiclase sobre la cual calcular precisión o F1 por categoría; su tarea es binaria (anómalo o no) y se evalúa como tal. El protocolo original fija el criterio de aceptación en recall de detección mínimo del 50% con una tasa de falsos positivos máxima del 10%, y ambos criterios se cumplen sobre el conjunto de prueba bloqueado (`training/results/v11_test_results.json`, lectura verificada contra el bloqueo criptográfico, correspondiente a la evaluación del 26 de septiembre de 2026 descrita en este capítulo) con la generación vigente: recall agregado de 0.9125 y tasa de falsos positivos de 0.0546. Ese umbral del 10% de falsos positivos, sin embargo, se endureció operativamente durante iteraciones previas del proyecto (generación `if_v5`) a un objetivo de calibración de 6% en el conjunto de validación, no por preferencia estética sino por una lección concreta de margen insuficiente: una calibración anterior de `if_v5` (umbral 0.02868, con un objetivo interno de calibración de 8% en validación) dio en el conjunto de prueba una tasa de falsos positivos de 0.0811, es decir, 0.0011 por encima de ese objetivo interno. El límite formal del objetivo específico 2 seguía siendo 10%. El corrimiento observado entre validación y prueba, se atribuyó al cambio de features introducido junto con `rf_v6` (el análisis por campo del cuerpo de la petición, que redujo la señal de longitud de payload de la que Isolation Forest dependía parcialmente). Ese cambio se introdujo antes de la calibración de `if_v5` dentro del mismo ciclo de reentrenamiento, y motivó la recalibración. El modelo recalibrado de `if_v5` (umbral 0.00941) no es el de producción: el modelo vigente, `if_v10`, usa el umbral 0.00421 y también se calibró en validación contra una tasa de falsos positivos $`\leq`$ 6%. Desde entonces, la calibración de cada nueva generación de Isolation Forest se realiza contra el objetivo más estricto de 6%, dejando margen deliberado de holgura frente al límite duro de 10% fijado por el objetivo específico 2.

La verificación de paridad ONNX se reporta como una métrica de validación en sí misma, no como un detalle de implementación: dado que el entrenamiento ocurre en Python sobre `scikit-learn` y la inferencia en producción ocurre en Node.js sobre `onnxruntime-node`, cualquier discontinuidad entre ambos entornos invalidaría todas las métricas anteriores como descripción del comportamiento real del sistema en producción. La paridad medida entre ambos entornos es del orden de $`10^{-7}`$ en la diferencia de probabilidad de salida, confirmada de forma automatizada antes de habilitar cada modelo para su integración (`training/models/parity_report.json`, `parity_passed: true`). Esta métrica es la que permite afirmar que el F1-score, el recall y la tasa de falsos positivos reportados para el modelo en Python son también válidos como descripción del modelo efectivamente servido por el middleware.

Finalmente, la cobertura de detección por categoría en las configuraciones de evaluación integradas (Config 2 y Config 3) es una métrica distinta de las anteriores por su nivel de análisis: mientras el F1-score y el recall/FP de Isolation Forest evalúan el modelo de forma aislada sobre un conjunto de prueba estático, la cobertura por categoría evalúa el sistema integrado –extractor, modelos e inferencia en *worker_threads*– contra tráfico HTTP real dirigido a una aplicación en ejecución. El objetivo específico 3 fija este criterio exactamente como sigue: “verificando que la detección de payloads representativos alcance al menos el 80% por cada una de las cuatro categorías de ataque cubiertas en un entorno de prueba controlado, sin elevar la latencia p95 del servidor más de 15 ms respecto a la línea base sin protección”. Este umbral del 80% por categoría se cumple en Config 2 para las cuatro categorías, medido sobre 100 payloads por categoría (`sqli` 100%, `xss` 100%, `path_traversal` 93%, `cmdi` 100%).

Como indicador complementario –de interpretabilidad, no de desempeño– se reporta también el análisis SHAP descrito en la sección anterior: la importancia global por clase documenta qué grupos de características sostienen cada F1-score por categoría, y las explicaciones locales documentan casos específicos donde el modelo se comporta de forma distinta a lo esperado (por ejemplo, el efecto del encabezado *User-Agent* sobre la puntuación de Isolation Forest), evidencia que complementa las métricas agregadas anteriores sin sustituirlas. Los hallazgos de esta importancia global, incluido el carácter parcialmente resuelto de `cmdi`, se detallan en la sección de Técnicas e instrumentos.

## Matriz de trazabilidad

El Cuadro 36.3 articula la correspondencia entre cada objetivo del proyecto, la actividad concreta de la fase de trabajo que lo atiende, el instrumento o técnica empleada, la métrica de aceptación aplicada y el resultado real medido, con su fuente verificable en el repositorio del proyecto.

| **Objetivo** | **Actividad** | **Instrumento/técnica** | **Métrica** | **Resultado real** |
|:---|:---|:---|:---|:---|
| **Objetivo** | **Actividad** | **Instrumento/técnica** | **Métrica** | **Resultado real** |
| Específico 1 (pipeline de features, 20 jun – 1 ago 2026) | Fase 1: construcción del pipeline de ingeniería de características | Extractor TypeScript + *worker_threads* (regla R1) | Latencia p95 de extracción $`\leq`$ 5 ms por petición | p95 mixto = 0.0273 ms con *worker_threads* (microbenchmark en aislamiento, mediana de tres corridas; Cuadro 37.1); $`\Delta`$p95 = 0 ms en benchmark Artillery de middleware completo sobre WSL2, con resolución de 1 ms |
| Específico 2 — RF (modelo híbrido, cierre 2 ago 2026) | Fase 3: entrenamiento y calibración; Fase 4: verificación de paridad ONNX | Random Forest (`scikit-learn` + ONNX) sobre conjunto de prueba bloqueado (R2) | F1-score $`\geq`$ 0.80 en al menos 3 de 4 categorías de ataque | F1 macro = 0.9776; por clase: `benign` 0.9984, `cmdi` 0.9239, `path_traversal` 0.9826, `sqli` 0.9956, `xss` 0.9877 — las 5 clases superan el umbral |
| Específico 2 — IF (modelo híbrido, cierre 2 ago 2026) | Fase 3: entrenamiento y calibración; Fase 4: verificación de paridad ONNX | Isolation Forest (`scikit-learn` + ONNX) sobre conjunto de prueba bloqueado (R2) | Recall de anomalías $`\geq`$ 50%, tasa de falsos positivos $`\leq`$ 10% | Recall = 0.9125, FP = 0.0546 — ambos criterios cumplidos con margen |
| Específico 2 — paridad (prerrequisito de integración) | Fase 4: verificación de paridad ONNX | Comparación de salida `scikit-learn` (Python) vs. `onnxruntime-node` | Diferencia de probabilidad entre ambos entornos | $`\sim 10^{-7}`$; `parity_passed: true` (`parity_report.json`) |
| Específico 3 — cobertura (2 ago – 30 sep 2026) | Fase 6: evaluación en Config 2 (+logSguarDian) | Middleware integrado sobre app vulnerable en Docker Compose | Detección $`\geq`$ 80% de payloads representativos por categoría | Config 2, sobre 100 payloads por categoría: `sqli` 100%, `xss` 100%, `path_traversal` 93%, `cmdi` 100%; las cuatro categorías superan el umbral (véase la sección 37.3.2 sobre su solapamiento con el entrenamiento). Ronda 5, sin solapamiento con el entrenamiento, 200 payloads por categoría, paquete publicado en npm (par A) y par C validado: `sqli` 100 % y 99.5 %, `path_traversal` 85.0 % y 95.0 %, `cmdi` 91.5 % y 96.0 % (secciones 37.3.5 y 37.3.6). `xss` no tiene corpus limpio y no se evaluó en la Ronda 5 |
| Específico 3 — latencia (2 ago – 30 sep 2026) | Fase 6: evaluación en Config 2 (+logSguarDian) | Benchmark de latencia (Artillery; WSL2, Linux nativo y Docker+Postgres) | $`\Delta`$p95 $`\leq`$ 15 ms respecto a la línea base sin protección | $`\Delta`$p95 de 0 ms en WSL2 (resolución de 1 ms) y de 7–9 ms en Docker+Postgres, dentro del límite. En Linux nativo (GitHub Actions, ejecución 36276690236, 2 vCPU), $`\Delta`$p95 de 12.08 ms en normal y 12.85 ms en ataque, dentro del límite, y de 6 495.5 ms en volumen con 7.00 % de timeouts, que no cumple (sección 37.3.2) |
| Específico 3 — defensa en profundidad (Config 3) | Fase 6 extendida: evaluación en Config 3a/3b (WAF solo / WAF + logSguarDian) sobre un corpus de 590 payloads de SecLists (solapamiento con el entrenamiento en la sección 37.3.5) | ModSecurity v3 + OWASP CRS (PL1) como capa perimetral, logSguarDian como segunda capa | Cobertura agregada por configuración; capacidad de logSguarDian de detectar de forma independiente los ataques que evaden el WAF | Config 3a (solo WAF): 550/590 (93.2%), con brechas reales por categoría (`sqli` 85.7%, `path_traversal` 87.0%). Config 3b (capas): 587/590 (99.5%). De los 40 ataques que evadieron el WAF, 37 fueron capturados de forma independiente por logSguarDian (92.5% del vacío cerrado) |
|  |  |  |  |  |

Correspondencia entre objetivos, actividades, instrumentos, métricas y resultados verificados. Elaboración propia.

## Recursos, participantes y restricciones

En cuanto a recursos, el entrenamiento de los modelos se realizó sobre hardware local (Apple Silicon), sin presupuesto asignado a instancias de cómputo en la nube –condición ya establecida como restricción de recursos en el capítulo de Alcance y verificada como viable dado el tamaño acotado de los modelos de ensamble seleccionados frente a alternativas de mayor capacidad computacional–. El entorno de evaluación integrado (Config 1/2/3) se ejecutó igualmente sobre infraestructura local mediante Docker Compose, sin servicios de terceros ni infraestructura de cómputo remota.

En cuanto a participantes, este documento corresponde al trabajo de graduación individual de Diego Pablo Valenzuela Palacios, y documenta específicamente el componente de aprendizaje automático de logSguarDian: el pipeline de ingeniería de características, el modelo híbrido Random Forest/Isolation Forest, su serialización y verificación de paridad ONNX, y su evaluación integrada como middleware –el alcance exacto delimitado en el capítulo de Alcance de este trabajo–. El desarrollo del proyecto logSguarDian en su conjunto contó además con la colaboración de Sebastián Huertas en el componente de ciberseguridad y en la implementación del lado npm de la librería (extractor TypeScript y paquete `core`), colaboración que se reconoce aquí por transparencia metodológica sin que ello implique coautoría de este documento ni extienda su alcance evaluado más allá del componente de Machine Learning aquí documentado. El extractor inicial de 72 características y el paso a *worker_threads* los implementó Sebastián Huertas. Diego Valenzuela analizó y justificó cada característica, definió cuáles no existen en inferencia y fijó el contrato de entrada, añadió cuatro características y las correcciones del extractor surgidas del análisis del modelo, y desarrolló el entrenamiento, la serialización ONNX y el pipeline de reentrenamiento.

En cuanto a restricciones, el proyecto se ejecutó dentro de la ventana comprendida entre mayo y octubre de 2026, conforme al calendario del trabajo de graduación de la Facultad de Ingeniería de la Universidad del Valle de Guatemala, y cualquier línea de trabajo no completable dentro de dicho período se documenta explícitamente como trabajo futuro y no como un entregable pendiente sin reconocer. La configuración de evaluación en defensa en profundidad (Config 3) completó su ronda de mayor escala (590 payloads de SecLists, cuyo solapamiento con el entrenamiento se describe en la sección 37.3.5) dentro de esa ventana, con el resultado reportado en el Cuadro 36.3: el corpus expuso brechas reales del Web Application Firewall operando solo (93.2% de cobertura agregada, con categorías tan bajas como 85.7%), y logSguarDian, operando como segunda capa, capturó 37 de los 40 ataques que evadieron esa primera capa. Esa misma ronda dejó, no obstante, un hallazgo de calibración que motivó el estudio de falsos positivos descrito en las secciones 37.3.2 y 37.3.7: una petición benigna de bajo contenido semántico puede acercarse lo suficiente al umbral de decisión de Random Forest como para que un metadato incidental de la petición (la cadena de *User-Agent* del cliente HTTP, no el contenido del payload) determine el veredicto, lo cual motivó un estudio de tasa de falsos positivos contra tráfico legítimo diverso, independiente de esta comparación basada en corpus de ataque. Ampliar el corpus benigno queda como trabajo futuro, según se indica en el capítulo de Recomendaciones ([cap:recomendaciones]). De igual manera, y como ya se estableció en el capítulo de Alcance, no se contempla dentro del alcance del proyecto un despliegue en un entorno de producción real de terceros como criterio de aceptación del sistema; esta es una restricción reconocida explícitamente, no un límite que el proyecto haya dejado sin identificar.

Finalmente, las cifras del componente Random Forest/Isolation Forest reportadas en el Cuadro 36.3 (F1 macro, F1 por clase, recall y tasa de falsos positivos de Isolation Forest) provienen de una corrección de trazabilidad de artefactos descrita en la sección de Recolección, procesamiento y validación de datos, integrada a la rama principal del repositorio del proyecto mediante el *pull request* \#79. El análisis SHAP se regeneró posteriormente contra el modelo corregido (*pull request* \#80), de modo que las cifras y los hallazgos de interpretabilidad de este capítulo corresponden al mismo artefacto.

# Resultados

Este capítulo presenta las mediciones obtenidas al evaluar logSguarDian, organizadas según los tres objetivos específicos del trabajo y la evaluación de interpretabilidad. Cada sección reporta los valores medidos, la condición bajo la cual se midieron y su fuente en el repositorio del proyecto. Las rutas de archivo se expresan relativas a la raíz de dicho repositorio. Cada medición se contrasta con su criterio de aceptación cuando existe uno; la interpretación de los valores se reserva para el capítulo de Discusión de resultados.

## Resultados del objetivo específico 1: pipeline de ingeniería de características

El pipeline de ingeniería de características extrae 76 características por petición, de las cuales 69 alimentan al componente Random Forest y 63 al componente Isolation Forest (`training/results/v11_test_results.json`). Esta sección reporta la latencia del extractor en aislamiento y el sobrecosto absoluto del middleware completo en los entornos donde se midió.

### Latencia del extractor en aislamiento

El Cuadro 37.1 presenta la latencia de la función `extractFeatureVector()` para cada una de las cinco clases de tráfico y para el tráfico mixto, en dos series: la llamada directa en el hilo principal y el ciclo de ida y vuelta a un *worker_threads*, que es la ruta asíncrona del pipeline. Cada cifra es la mediana de tres corridas independientes del benchmark `benchmarks/extractor.bench.js` del repositorio `logSguarDian` (PR #97, fusionado en `develop`), del 9 de octubre de 2026. Cada corrida descartó 200 iteraciones de calentamiento, midió 2 000 iteraciones por *fixture* de forma serial y tomó el tiempo con alta resolución. El hardware fue un Apple M5 con macOS (Darwin 27.0.0, arm64) y Node.js v25.6.0.



| **Fixture** | **Serie** | **p50 (ms)** | **p95 (ms)** | **p99 (ms)** | **Throughput (req/s)** |
|:---|:---|---:|---:|---:|---:|
| `benign` | Directa (hilo principal) | 0.0103 | 0.0169 | 0.0409 | 86 059 |
| `sqli` | Directa (hilo principal) | 0.0092 | 0.0120 | 0.0340 | 98 161 |
| `xss` | Directa (hilo principal) | 0.0102 | 0.0135 | 0.0340 | 92 380 |
| `path_traversal` | Directa (hilo principal) | 0.0076 | 0.0097 | 0.0302 | 122 212 |
| `cmdi` | Directa (hilo principal) | 0.0090 | 0.0102 | 0.0314 | 105 878 |
| Mixto (*round-robin*) | Directa (hilo principal) | 0.0097 | 0.0126 | 0.0350 | 98 383 |
| `benign` | Ida y vuelta a *worker_threads* | 0.0213 | 0.0304 | 0.0467 | 43 960 |
| `sqli` | Ida y vuelta a *worker_threads* | 0.0210 | 0.0275 | 0.0405 | 45 459 |
| `xss` | Ida y vuelta a *worker_threads* | 0.0226 | 0.0305 | 0.0430 | 42 974 |
| `path_traversal` | Ida y vuelta a *worker_threads* | 0.0162 | 0.0264 | 0.0377 | 54 884 |
| `cmdi` | Ida y vuelta a *worker_threads* | 0.0212 | 0.0283 | 0.0405 | 45 180 |
| **Mixto (*round-robin*)** | **Ida y vuelta a *worker_threads*** | **0.0206** | **0.0273** | **0.0413** | **46 635** |

Latencia del extractor de características en aislamiento, por *fixture* y serie de ejecución.


Fuente: `benchmarks/results/extractor-*.json` (tres corridas del 9 de octubre de 2026, commit `7b036bb` del código medido), rama `develop` del repositorio `logSguarDian`; mediana de las tres corridas por *fixture* y serie, a partir de los campos en nanosegundos. Elaboración propia.

La cifra que se compara con el criterio de 5 ms del objetivo específico 1 es el p95 mixto de la serie con *worker_threads*, de 0.0273 ms. Ambas series son microbenchmarks en aislamiento: no incluyen el resto del middleware, la red ni la carga concurrente.

Nota: una cifra anterior de 0.0082 ms, fechada el 20 de julio de 2026, no registra el hardware ni la versión de Node.js, por lo que no se usa como referencia en este trabajo.

### Sobrecosto absoluto del middleware completo

El Cuadro 37.2 reúne las mediciones de latencia p95 con y sin el middleware activo en cada entorno donde se midió. Las filas difieren en entorno, escala de datos y compilación del middleware, por lo que cada una declara esas condiciones. Las filas de Docker más Postgres usan la aplicación de referencia (Express y Postgres) con el flujo de navegación benigno de Artillery (`attack-sim/artillery-baseline.yml`, 60 s, 20 usuarios virtuales por segundo con cuatro solicitudes por usuario, es decir, una tasa objetivo de 80 solicitudes por segundo). La fila de Node.js sobre WSL2 usa el benchmark de `packages/core/bench` (Artillery, 50 solicitudes por segundo, 30 s, 3 000 solicitudes por corrida, Node.js v22.5.1, Windows 11 con WSL2, 9 de julio de 2026) con resolución de 1 ms. La fila de microbenchmark mide una función Express sin aplicación detrás.



| **Entorno** | **Compilación del middleware** | **p95 sin middleware (ms)** | **p95 con middleware (ms)** | **$`\Delta`$p95 absoluto (ms)** |
|:---|:---|---:|---:|---:|
| Node.js sobre WSL2, Artillery | Versión de julio de 2026 (modo *monitor*) | 1 | 1 | 0 |
| Microbenchmark sintético (función Express) | Registro asíncrono sin ventana de gracia (PR \#53) | 0.116 | 0.300 | 0.184$`^{\dagger}`$ |
| Aplicación real con Postgres, sin Docker | *Worker pool* con ventana de gracia, sin registro asíncrono | 3 | 6 | 3$`^{\dagger}`$ |
| Docker y Postgres, 10 filas | *Worker pool* con ventana de gracia, sin registro asíncrono | 5.0 | 12.8 | 7.8$`^{\dagger}`$ |
| Docker y Postgres, 10 filas | Diseño híbrido (ventana de gracia y cola de escritura por lotes) | $`\approx`$5 | $`\approx`$12–14 | $`\approx`$7–9 |
| Docker y Postgres, 2 010 filas | Diseño híbrido (ventana de gracia y cola de escritura por lotes) | 13.67 | 23–28 | 9.33–14.33$`^{\dagger}`$ |

Latencia p95 con y sin middleware y diferencia absoluta, por entorno medido.


$`^{\dagger}`$ Diferencia calculada como p95 con middleware menos p95 sin middleware; la fuente reporta ambos valores y no la diferencia. Las compilaciones con ventana de gracia corresponden a versiones anteriores del middleware; la versión vigente resuelve la respuesta sin esperar al Isolation Forest y actualiza el registro con su puntaje tardío (`packages/core/src/middleware.ts`, rama `develop`).\
Fuente: `docs/results.md`, secciones A19 y F6.5; `docs/config2-latency-evaluation.md`, secciones Final latency y Config 2 Final Status. Elaboración propia.

El Cuadro 37.2 reporta la latencia p95 con y sin middleware, y su diferencia $`\Delta`$p95 frente al límite de 15 ms fijado en el objetivo específico 3.

Como evidencia complementaria de inferencia, dos mediciones independientes documentan la latencia a nivel de componente, en contextos distintos que no deben compararse entre sí. Durante la instrumentación de la fase de *grace-window* (250 peticiones muestreadas), el tiempo medio de `session.run()` fue de 0.026 ms para Random Forest y 0.978 ms para Isolation Forest, con un tiempo medio de espera en cola (extracción y cola) de 0.038 ms y 0.052 ms, respectivamente (`docs/results.md`, líneas 445–460). Por separado, una ejecución de 60 s bajo carga sostenida midió el tiempo de inferencia por llamada de Isolation Forest en un rango de 2.99 ms a 3.22 ms de media (aproximadamente 2.9–3.2 ms, con p95 de 5.0–6.0 ms) a lo largo de diez segmentos cronológicos consecutivos, sin mostrar un patrón de crecimiento sostenido (`docs/results.md`, líneas 550–560; `docs/config2-latency-evaluation.md`, línea 452).

## Resultados del objetivo específico 2: modelo híbrido Random Forest e Isolation Forest

El conjunto de prueba bloqueado (57 481 filas) se leyó tres veces para la generación `rf_v11`/`if_v10`: el 24 de septiembre de 2026 (commit `3086318`), el 25 de septiembre de 2026 (commit `fc47a5b`) y el 26 de septiembre de 2026 (commit `03de50f`, mediante `training/evaluate_test.py`). Las cifras reportadas en esta sección corresponden a la lectura del 26 de septiembre de 2026. Se evaluaron los modelos `rf_v11` e `if_v10` en su forma ONNX (`rf.onnx` e `if.onnx`, ejecutados con `onnxruntime`) del repositorio de entrenamiento, y no los archivos `.pkl` ni el paquete publicado en npm. El archivo `training/splits/test.lock.sha256` coincidió con el *hash* registrado antes de ejecutar cualquier inferencia (`7486c258…4fd9`). Todos los valores de esta sección provienen de `training/results/v11_test_results.json`.

### Random Forest

El Cuadro 37.3 presenta la precisión, el *recall*, el F1-score y el AUC-ROC de Random Forest por clase. El AUC-ROC se calculó con el método uno contra el resto (`roc_auc_score`, `multi_class=’ovr’`). El F1-score macro fue de 0.9776, la exactitud global de 0.9932 y el F1-score ponderado de 0.9933. El AUC-ROC por clase estuvo entre 0.99899 (`path_traversal`) y 0.99998 (`benign`). Las métricas por clase se calculan por argmax de la probabilidad (`training/evaluate_test.py`, salida de etiquetas del modelo ONNX), sin el umbral de confianza de 0.35 con el que el middleware decide el bloqueo (`packages/core/src/middleware.ts`); no se calculó una métrica de prueba con la regla de decisión desplegada.



| **Clase** | **Precisión** | ***Recall*** | **F1-score** | **Soporte** | **AUC-ROC** |
|:---|---:|---:|---:|---:|---:|
| `benign` | 0.9984 | 0.9985 | 0.9984 | 14 886 | 0.99998 |
| `cmdi` | 0.9015 | 0.9475 | 0.9239 | 1 468 | 0.99901 |
| `path_traversal` | 0.9853 | 0.9798 | 0.9826 | 2 529 | 0.99899 |
| `sqli` | 0.9955 | 0.9956 | 0.9956 | 34 107 | 0.99982 |
| `xss` | 0.9950 | 0.9804 | 0.9877 | 4 491 | 0.99930 |
| **Promedio macro** | **0.9751** | **0.9804** | **0.9776** | **57 481** | — |

Métricas de Random Forest (`rf_v11`) por clase sobre el conjunto de prueba bloqueado.


Fuente: `training/results/v11_test_results.json`. Elaboración propia.

### Isolation Forest

El Cuadro 37.4 presenta las métricas de Isolation Forest (`if_v10`) sobre el mismo conjunto de prueba. Una petición se considera detectada como anomalía cuando su puntaje queda por debajo del umbral de 0.004205941820353609, congelado en `training/models/if_v10_metadata.json` y no recalibrado contra el conjunto de prueba. El umbral de Isolation Forest pasó de 0.00807 (lectura del 24 de septiembre de 2026, con el modelo previo a ese reentrenamiento) a 0.00421 (lecturas del 25 y 26 de septiembre de 2026) tras reentrenar y recalibrar en validación. Las clases de ataque (42 595 filas) se tratan como positivas y la clase `benign` (14 886 filas) como negativa. La matriz de confusión resultante fue: 38 868 verdaderos positivos, 3 727 falsos negativos, 813 falsos positivos y 14 073 verdaderos negativos.



| **Métrica**                  | **Valor** |
|:-----------------------------|----------:|
| *Recall* global              |    0.9125 |
| Tasa de falsos positivos     |    0.0546 |
| Precisión                    |    0.9795 |
| *Recall* en `cmdi`           |    0.9564 |
| *Recall* en `path_traversal` |    0.9968 |
| *Recall* en `sqli`           |    0.8954 |
| *Recall* en `xss`            |    0.9802 |

Métricas de Isolation Forest (`if_v10`) sobre el conjunto de prueba bloqueado.


Fuente: `training/results/v11_test_results.json`. Elaboración propia.

### Paridad entre scikit-learn y ONNX

El Cuadro 37.5 presenta la diferencia máxima observada entre la salida de los modelos en scikit-learn y la de sus versiones ONNX, calculada sobre 1 000 muestras con *opset* 17.



| **Modelo**                  | **Magnitud comparada** |   **Diferencia máxima** |
|:----------------------------|:-----------------------|------------------------:|
| Random Forest (`rf_v11`)    | Probabilidad por clase | $`1.01 \times 10^{-7}`$ |
| Isolation Forest (`if_v10`) | Puntaje de anomalía    | $`2.42 \times 10^{-7}`$ |

Diferencia máxima de salida entre scikit-learn y ONNX sobre 1 000 muestras. El reporte registra `parity_passed: true`.


Fuente: `training/models/parity_report.json`. Elaboración propia.

## Resultados del objetivo específico 3: evaluación integrada en las configuraciones 1, 2, 3a y 3b

La evaluación integrada se ejecutó sobre una aplicación Express y Postgres deliberadamente vulnerable (`logSguarDian-vulnerable-project`), en cuatro configuraciones: Config 1, sin protección; Config 2, solo logSguarDian; Config 3a, solo *Web Application Firewall* (ModSecurity v3 con OWASP CRS en nivel de paranoia 1 y modo de bloqueo); y Config 3b, ModSecurity más logSguarDian en capas. En las configuraciones con logSguarDian, los modelos desplegados fueron `rf_v10` e `if_v9`, con `RF_THRESHOLD` de 0.35. La evaluación de Config 1, 2, 3a y 3b (rondas de julio-agosto de 2026) se ejecutó sobre la generación de modelos vigente en ese momento, `rf_v10`/`if_v9`. Las métricas de Random Forest e Isolation Forest reportadas en las secciones anteriores de este capítulo corresponden a la generación posterior, `rf_v11`/`if_v10`, resultado del reentrenamiento del 30 de agosto de 2026 (PR #66), cuyas métricas de prueba se re-derivaron en el PR #79. Las Configuraciones 2 y 3b se evaluaron con la generación vigente en ese momento, `rf_v10`/`if_v9`. La Configuración 1 y la Configuración 3a no usan los modelos de logSguarDian. La Configuración 2 se repitió después con `rf_v11`/`if_v10`, primera versión del 30 de agosto de 2026, como se reporta en las secciones 37.3.2 y 37.3.5, y con el par validado, como se reporta en la sección 37.3.6; la Configuración 3b no se repitió. Las rutas de archivo de esta sección se expresan relativas a `docs/` del repositorio del proyecto.

### Config 1: aplicación sin protección

El Cuadro 37.6 resume los vectores de ataque ejecutados contra la aplicación sin ningún componente de seguridad, con la prueba de concepto de `curl` de cada vector y capturando la respuesta real.



| **Categoría** | **Vectores probados** | **Vectores comprometidos** |
|:---|:---|---:|
| Inyección SQL | Evasión de autenticación; exfiltración con `UNION` | 2/2 |
| XSS almacenado | Campo de biografía; contenido de publicación | 2/2 |
| *Path traversal* | Descarga de adjuntos | 1/1 |
| Inyección de comandos | Utilidad de administración `ping` | 1/1 |
| **Total** |  | **6/6** |

Vectores de ataque comprometidos en Config 1, sin protección.


Fuente: `baseline-config1.md`, sección 5 (ejecutado el 24 de julio de 2026). Elaboración propia.

En el vector de inyección de comandos, `whoami` devolvió `root`.

### Config 2: solo logSguarDian

El Cuadro 37.7 presenta la cobertura por categoría de Config 2 sobre 100 payloads por categoría (`attack-sim/payloads/*.json`), disparados contra el *endpoint* que corresponde a cada vulnerabilidad con el middleware activo en modo `block`. Se contabilizó como bloqueada la respuesta HTTP 403 del middleware.

Los 100 payloads por categoría de esta medición no son disjuntos del entrenamiento. Con la misma normalización de la sección 37.3.5, coinciden con alguna partición, por igualdad normalizada, 2 de 100 en `sqli`, 14 en `xss`, 4 en `path_traversal` y ninguno en `cmdi`, y por subcadena normalizada, 15, 33, 29 y 8, respectivamente. Algunas filas de las particiones no conservan el texto crudo, por lo que los conteos son cotas inferiores. El repositorio conserva solo los valores agregados de esta medición, documentados el 6 de agosto de 2026, y no registra los resultados por payload ni el hash de los modelos, por lo que la cobertura no se recalculó sin las coincidencias.



| **Categoría**    | **Bloqueados** | **Total** | **Cobertura** |
|:-----------------|---------------:|----------:|--------------:|
| `sqli`           |            100 |       100 |       100.0 % |
| `xss`            |            100 |       100 |       100.0 % |
| `path_traversal` |             93 |       100 |        93.0 % |
| `cmdi`           |            100 |       100 |       100.0 % |

Cobertura de detección por categoría en Config 2, 100 payloads por categoría.


Fuente: `docs/config2-latency-evaluation.md` (secciones *Final coverage* y *Config 2 Final Status*) del repositorio `logSguarDian-vulnerable-project` (commit `944feb1`); valores agregados. Elaboración propia.

El recuento de eventos de bloqueo en la base de detección de logSguarDian (393) coincide con el total de payloads bloqueados del Cuadro 37.7, que el criterio de la sección anterior define como la respuesta HTTP 403 del middleware. En los escenarios normal y de volumen, las peticiones benignas de Artillery no recibieron ninguna respuesta 403 en las cinco repeticiones de cada condición (corrida de latencia de Linux, run 36276690236, `docs/evidence/latency-linux-2026-09-26.tgz` del repositorio `logSguarDian-vulnerable-project`, rama `main`). Cada repetición del escenario normal envió 6 300 solicitudes, incluido el calentamiento, de las cuales 4 725 respondieron 200 y 1 575 respondieron 302. En el escenario de volumen con middleware activo, 1 824 solicitudes en total agotaron el tiempo de espera entre las cinco repeticiones; un tiempo de espera no es una respuesta 403 y se reporta por separado.

Este resultado vale para el User-Agent por defecto de Artillery, `Artillery (https://artillery.io)`, una cadena corta que no representa a un navegador. Con cadenas de User-Agent de navegadores reales, el estudio `attack-sim/ua_fp_study.py` bloqueó 13 de 15 combinaciones de agente y ruta; solo Firefox en macOS evitó el bloqueo en `/login` y `/posts`.

Ese estudio corresponde al commit del 24 de septiembre de 2026, y su archivo de resultados no registra el modelo cargado. Por el contenido de `models/` en ese commit, el modelo es el par `rf_v10`/`if_v9`, mientras que la corrida de latencia de Linux usó el par `rf_v11`/`if_v10`, primera versión del 30 de agosto de 2026 (`a7c015f5…`/`3cf8e45c…`). Los dos resultados corresponden a modelos distintos y no se comparan directamente. En la condición de ataque no es posible aislar la tasa de 403 de las peticiones benignas, porque el informe agrega las respuestas por *endpoint* y `/profile` recibe tanto peticiones benignas como el ataque de XSS.

El Cuadro 37.8 reporta el incremento relativo del p95, definido como $`\Delta`$p95 expresado como porcentaje de la línea base sin middleware. Es un indicador complementario. El criterio vigente del objetivo específico 3 es el $`\Delta`$p95 absoluto de 15 ms del Cuadro 37.2. Cada medición usa el flujo benigno de Artillery (`attack-sim/artillery-baseline.yml`, 60 s, 20 usuarios virtuales por segundo con cuatro solicitudes por usuario) sobre Docker y Postgres, y las filas difieren en la compilación del middleware y en la escala de datos. Esas mediciones se documentaron entre el 31 de julio y el 6 de agosto de 2026, cuando el archivo tenía esa configuración; el cambio a 25 usuarios virtuales por segundo es del 24 de septiembre de 2026.



| **Compilación del middleware** | **Datos sembrados** | **p95 sin middleware (ms)** | **p95 con middleware (ms)** | **$`\Delta`$p95 relativo** |
|:---|:---|---:|---:|---:|
| Un solo *worker* (`rf_v9`/`if_v8`) | 10 filas | 4.0 | 14.6 | +265.8 % |
| *Worker pool* (`rf_v10`/`if_v9`), medición inicial | 10 filas | 5.0 | 10.6 | +111.3 % |
| *Worker pool* (`rf_v10`/`if_v9`), umbral de IF corregido (6 corridas) | 10 filas | 5.0 | 12.8 | +156.7 % |
| Diseño híbrido (ventana de gracia y cola de escritura por lotes) | 2 010 filas | 13.67 | 23–28 | +70.2 % |

Incremento relativo del p95 de Config 2 (indicador complementario), por compilación del middleware. Las generaciones medidas son `rf_v9`/`if_v8` y `rf_v10`/`if_v9`; no corresponden a `rf_v11`/`if_v10`.


Fuente: `docs/config2-latency-evaluation.md`, secciones *Latency Results*, *Comparison across iterations*, *Final latency*, *Definitive comparison* y *Config 2 Final Status*. Elaboración propia.

Las tres mediciones con 10 filas sembradas arrojaron un incremento relativo del p95 de +111.3 % a +265.8 %; la medición con 2 010 filas arrojó +70.2 %.

**Experimento independiente de latencia en Linux nativo.** El flujo manual `Latency Benchmark` del repositorio `logSguarDian-vulnerable-project` (ejecución 36276690236, commit `f15a9e8`, 26 de septiembre de 2026) se ejecutó en un runner `ubuntu-latest` con 2 vCPU y 7.8 GiB de memoria, con contenedores Docker sobre Linux y sin Docker Desktop/macOS. El $`\Delta`$p95 relativo fue de +485.1 % en el escenario normal, +278.1 % en el de ataque y +10 174.6 % en el de volumen con 2 010 filas sembradas. En términos absolutos, la diferencia entre el p95 con y sin middleware fue de 12.08 ms en el escenario normal (de 2.49 a 14.57 ms), 12.85 ms en el de ataque (de 4.62 a 17.47 ms) y 6 495.46 ms en el de volumen (de 63.84 a 6 559.30 ms). Frente al límite de 15 ms del objetivo específico 3, los escenarios normal y de ataque quedan por debajo y el de volumen lo supera ampliamente. Este experimento difiere de las mediciones anteriores en entorno, carga ofrecida, arnés de medición y procedencia de los artefactos. Se reporta por separado: no reemplaza ni refuta las cifras de +111.3 % a +265.8 % y +70.2 %, ni se promedia con ellas.

Cada corrida descarta 15 s de calentamiento y mide 60 s, con cinco repeticiones por condición. La tasa medida fue de 25 usuarios virtuales por segundo en los escenarios normal y de volumen, y de 30 en el de ataque, mediante `--overrides` en `attack-sim/run_latency_suite.sh`. El p95 de cada corrida es una aproximación calculada como promedio ponderado por conteo de los p95 de los intervalos de Artillery posteriores al calentamiento (`attack-sim/parse-latency-report.js`). Cada condición resume sus cinco repeticiones con la mediana de tres valores, tras descartar el mínimo y el máximo; no corresponde a un percentil exacto calculado sobre el conjunto agrupado de muestras.

En el escenario de volumen con middleware, 1 824 de 26 048 solicitudes (7.00 %, sumadas las cinco repeticiones) terminaron con `ERR_SOCKET_TIMEOUT`: 1 804 en `/login` y 20 en `/posts`. La línea base de volumen no registró errores. Las solicitudes con timeout no tienen tiempo de respuesta registrado y no entran en el p95.

Los modelos de esta ejecución son `rf.onnx` (SHA-256 `a7c015f5…`) e `if.onnx` (`3cf8e45c…`), que se encuentran en el directorio `models/` de la aplicación vulnerable (commit `f15a9e8`) y no forman parte del paquete publicado en npm (`logsguardian@0.1.0`, par A), que contiene `rf_v10`/`if_v9`. Corresponden al build `rf_v11`/`if_v10` del 30 de agosto de 2026 (commit `734c24f` del repositorio logSguarDian), el mismo que usaron las ejecuciones de Config 2 del 9 de septiembre de 2026. No son el par canónico posterior al PR #79 (`rf.onnx` `25b407e6…`, `if.onnx` `5be28ee8…`), que es el que declara el campo `artifact_checksums` de `training/results/v11_test_results.json` y con el que se calcularon las métricas de la sección del objetivo específico 2. La ejecución de Linux no se repitió con ese par. Fuente: `cybersecurity-objectives-compliance.md`, sección OE3.2 y sus notas metodológica y de procedencia del modelo, en el repositorio logSguarDian.

### Config 3a y Config 3b: corpus pequeño

En las Rondas 1 y 2, ejecutadas con el *stack* en capas y ModSecurity en modo de bloqueo, el corpus fue de 23 payloads: los 9 casos de ataque de las Configs 1 y 2 y 14 variantes diseñadas para evadir las reglas de firmas de CRS. ModSecurity respondió 403 a los 9 casos originales y a las 14 variantes (23/23), y ninguna petición llegó a la aplicación (`docs/config3b-results.md`, secciones *Round 1* y *Round 2*).

En la Ronda 3, con `MODSEC_RULE_ENGINE` en `DetectionOnly`, de modo que CRS registra pero no bloquea y toda petición llega a la aplicación, los 23 payloads se reejecutaron contra logSguarDian. La auditoría de CRS registró que habría bloqueado los 23. El resultado inicial fue de 16/23 bloqueados por logSguarDian (la cifra original del documento fuente, 21/23, resultó aritméticamente inconsistente con el detalle de 7 casos no detectados que el propio documento reporta; se corrigió a 16/23, consistente con 16+7=23, sin re-medición porque los datos crudos de esa ronda ya no existen); los 7 no detectados eran de XSS y se habían enviado como `multipart/form-data`. Tras montar un *parser* multipart global antes del middleware, 23/23 devolvieron `verdict: block`, confirmado en `detection_events`. Dos payloads (traversal de rutas y una inyección de comandos) se bloquearon con una clase asignada distinta de la esperada (`config3b-results.md`, sección *Round 3*).

### Config 3a y Config 3b: corpus grande

La Ronda 4 ejecutó las cuatro configuraciones contra 590 payloads de SecLists (rama `master`), deduplicados y muestreados aleatoriamente con semilla 42 hasta un máximo de 200 por categoría: 77 de `sqli`, 113 de `xss`, 200 de `path_traversal` y 200 de `cmdi`. El Cuadro 37.9 presenta los payloads bloqueados por configuración y categoría.



| **Categoría** | **Config 1 (sin protección)** | **Config 2 (solo logSguarDian)** | **Config 3a (solo WAF, PL1)** | **Config 3b (en capas)** |
|:---|---:|---:|---:|---:|
| `sqli` (77) | 0/77 (0.0 %) | 76/77 (98.7 %) | 66/77 (85.7 %) | 77/77 (100.0 %) |
| `xss` (113) | 0/113 (0.0 %) | 110/113 (97.3 %) | 110/113 (97.3 %) | 113/113 (100.0 %) |
| `path_traversal` (200) | 0/200 (0.0 %) | 197/200 (98.5 %) | 174/200 (87.0 %) | 197/200 (98.5 %) |
| `cmdi` (200) | 0/200 (0.0 %) | 200/200 (100.0 %) | 200/200 (100.0 %) | 200/200 (100.0 %) |
| **Total (590)** | **0/590 (0.0 %)** | **583/590 (98.8 %)** | **550/590 (93.2 %)** | **587/590 (99.5 %)** |

Payloads bloqueados por configuración y categoría sobre el corpus de 590 payloads de SecLists.


Fuente: `docs/config3b-results.md`, sección *Round 4*. Elaboración propia.

De los 40 ataques que CRS en nivel de paranoia 1 no bloqueó en Config 3a (590 menos 550), la atribución de los bloqueos de Config 3b por firma de respuesta (el encabezado `X-Powered-By: Express` aparece solo en bloqueos de la capa de aplicación) registró 37 capturados por logSguarDian tras pasar el WAF. Tres payloads pasaron ambas capas: las cadenas ` /.gtkrc`, `/proc/filesystems` y ` /.atfp_history`, de la categoría `path_traversal`.

### Solapamiento del corpus de 590 payloads con el entrenamiento

Los 590 payloads de la evaluación integral provienen de SecLists. Los 200 de inyección de comandos son las líneas del archivo `command-injection-commix.txt`, del que también provienen las 2 455 filas de la fuente `seclists_cmdi` (1 719 en entrenamiento, 368 en validación y 368 en prueba). Con igualdad de la cadena normalizada (dígitos sustituidos por `N` y marcadores de seis letras mayúsculas por `CANARY` en `cmdi`; decodificación URL, minúsculas y dígitos sustituidos en las demás categorías), los 200 payloads de `cmdi` coinciden con alguna partición. Por texto literal, 63 de ellos aparecen en alguna partición: 46 en entrenamiento, 8 en validación y 9 en prueba, sin que ninguno aparezca en dos particiones. En `xss`, 7 de 113 payloads coinciden por igualdad normalizada; en `sqli`, ninguno de 77; en `path_traversal`, ninguno de 200. Al excluir las coincidencias por igualdad normalizada, la cobertura de logSguarDian en Config 2 fue de 98.7 % en `sqli`, 97.2 % en `xss` y 98.5 % en `path_traversal`, frente a 98.7 %, 97.3 % y 98.5 % con el corpus completo. La coincidencia por subcadena produce 26 payloads de `sqli`, 13 de `xss` y los 200 de `cmdi`, y constituye un límite superior, no una medida de solapamiento. En `cmdi` todo el corpus coincide, por lo que la cobertura de 100 % en esa categoría no constituye evidencia de generalización a payloads de otra procedencia.

Config 2 se ejecutó también sobre los mismos 590 payloads con dos generaciones de modelo; el cuadro anterior corresponde a la primera. Con `rf_v10`/`if_v9` (`attack-sim/results_config2.json`, commit `af61eba` del repositorio `logSguarDian-vulnerable-project`) se bloquearon 583 de 590 payloads. Con `rf_v11`/`if_v10` (build del 30 de agosto de 2026, `attack-sim/results_config2-rfv11.json`, commit `14c0e15`) también se bloquearon 583 de 590. Al comparar por identificador, 10 payloads cambiaron de estado: `sqli` pasó de 76 a 77 bloqueados (`sqli_31` pasó a bloquearse), `xss` de 110 a 111 (`xss_12`), `path_traversal` se mantuvo en 197 con tres payloads que dejaron de bloquearse (`path_traversal_13`, `_127` y `_186`) y tres que empezaron a bloquearse (`_6`, `_36` y `_69`), y `cmdi` bajó de 200 a 198 (`cmdi_88` y `cmdi_118` dejaron de bloquearse). El archivo `results_config2-rfv11.json` no registra el modelo utilizado; su atribución al build del 30 de agosto de 2026 (`rf.onnx` `a7c015f5…`, `if.onnx` `3cf8e45c…`) se apoya en el mensaje del commit `14c0e15`, que describe el reemplazo de `models/rf.onnx` e `models/if.onnx` por el build `rf_v11`/`if_v10` antes de esa ejecución. El archivo `results_config2.json` (590 payloads) corresponde a `rf_v10`/`if_v9`: los blobs de `models/rf.onnx` e `models/if.onnx` en `af61eba` tienen los hashes `18083725…` y `5de374a7…` de ese par, y el reporte de paridad `training/models/parity_report.json` del commit `dc2aaa65` (repositorio logSguarDian) declara `rf_v10`/`if_v9`.

### Evaluación sobre un corpus sin solapamiento (Ronda 5)

Para acotar el solapamiento descrito en la subsección anterior se construyó un corpus de 608 solicitudes. Contiene 200 payloads de inyección SQL generados con sqlmap, 200 de path traversal y 200 de inyección de comandos (`cmdi`). Estos dos últimos conjuntos se produjeron con generadores propios deterministas, con semilla 20260923, no derivados de SecLists. El corpus incluye además 8 marcadores de `xss` escritos a mano; no entran en la cobertura, por lo que esta categoría no se evaluó en esta ronda.

Antes de incluir cada candidato se descartó toda coincidencia exacta del campo completo con el conjunto de entrenamiento. El filtro descartó 3 de 400 candidatos de path traversal, todos por coincidencia con `owasp_logs.jsonl`, y ninguno de los 1 995 candidatos de sqli ni de los 400 de cmdi (`attack-sim/exclusion_report.json`). El solapamiento con las particiones se midió con `training/leakage_check.py` del repositorio `logSguarDian` (commit 22550ea), ejecutado en solo lectura contra `train`, `val` y `test`. Se usan dos criterios. El primero, (a), es la igualdad normalizada del campo completo: un payload coincide si su forma normalizada es igual a la de algún campo `path`, `query` o `body` de la partición. El segundo, (b), es la regla de subcadena de `round4_vs_split`: un payload coincide si aparece como subcadena de algún campo, con y sin normalización. La regla (b) es permisiva, por lo que sus cifras son un límite superior y no una medida de solapamiento.

El Cuadro 37.10 presenta el número de payloads de cada categoría que coinciden con cada partición, por criterio.



| **Categoría** | **Criterio** | **Train** | **Val** | **Test** | **Unión** |
|:---|:---|---:|---:|---:|---:|
| `sqli` | \(a\) igualdad normalizada | 4 | 1 | 2 | 4 |
| `sqli` | \(b\) subcadena normalizada | 4 | 1 | 2 | 4 |
| `sqli` | \(b\) subcadena literal | 0 | 0 | 0 | 0 |
| `path_traversal` | \(a\) igualdad normalizada | 0 | 0 | 0 | 0 |
| `path_traversal` | \(b\) subcadena normalizada | 6 | 5 | 5 | 7 |
| `path_traversal` | \(b\) subcadena literal | 5 | 2 | 5 | 5 |
| `cmdi` | \(a\) igualdad normalizada | 0 | 0 | 0 | 0 |
| `cmdi` | \(b\) subcadena normalizada | 1 | 1 | 1 | 2 |
| `cmdi` | \(b\) subcadena literal | 0 | 0 | 0 | 0 |

Payloads de 200 por categoría que coinciden con cada partición, según el criterio de solapamiento. Unión: payloads que coinciden con al menos una partición.


Fuente: `training/leakage_check.py` (commit 22550ea) sobre `training/splits/` del repositorio `logSguarDian`, y `attack-sim/large_corpus_requests.json`. Elaboración propia.

Con el criterio (a), 4 de los 200 payloads de sqli coinciden con alguna partición y ninguno de path traversal ni de cmdi. Con el criterio (b), path traversal alcanza 7 coincidencias en la unión y cmdi 2; por ser un límite superior, estas cifras no deben leerse como solapamiento confirmado.

El modelo validado tiene una cadena de procedencia verificable. El tarball de validación, que no se publicó en el registro npm, se construyó desde el commit 22550ea de `develop` del repositorio `logSguarDian`, con SHA-256 . Sus modelos, par C, son `rf.onnx` (`25b407e6…`) e `if.onnx` (`5be28ee8…`), y las sumas de verificación se comprobaron dentro del contenedor. La construcción quedó registrada en el commit 4d928b5 del repositorio `logSguarDian-vulnerable-project`. La repetición de Config 2 con ese tarball se ejecutó el 9 de octubre de 2026 (`attack-sim/results_config2-develop-tarball-20261009.json`), con los mismos 200 payloads por categoría. El archivo de resultados no registra el modelo; esa atribución consta en `docs/config3b-results.md` y en dicho commit.

El Cuadro 37.11 presenta la cobertura de Config 2 sobre este corpus con ambos pares de modelos.



| **Categoría** | **`rf_v10`/`if_v9` (paquete publicado)** | **`rf_v11`/`if_v10` (validado)** |
|:---|---:|---:|
| `sqli` | 200/200 (100.0 %) | 199/200 (99.5 %) |
| `path_traversal` | 170/200 (85.0 %) | 190/200 (95.0 %) |
| `cmdi` | 183/200 (91.5 %) | 192/200 (96.0 %) |

Cobertura de Config 2 sobre el corpus de la Ronda 5, con 200 solicitudes por categoría, por par de modelos.


Fuente: `attack-sim/results_config2.json` en el commit a3aada0 y `attack-sim/results_config2-develop-tarball-20261009.json`, del repositorio `logSguarDian-vulnerable-project`. Elaboración propia.

Con `rf_v10`/`if_v9`, los intervalos de Wilson al 95 % son 98.1–100.0 % en sqli, 79.4–89.3 % en path traversal y 86.8–94.6 % en cmdi. Con `rf_v11`/`if_v10` son 97.2–99.9 %, 91.0–97.3 % y 92.3–98.0 %, en el mismo orden. Las tres categorías superan el 80 % del objetivo específico 3 con ambos pares de modelos, aunque el límite inferior del intervalo de path traversal con `rf_v10`/`if_v9` queda por debajo de ese umbral.

Al comparar por identificador, 26 payloads de path traversal pasaron de no bloqueados a bloqueados y 6 en sentido inverso; en cmdi, 16 pasaron a bloqueados y 7 en sentido inverso; en sqli, ninguno pasó a bloqueado y 1 en sentido inverso. En la corrida del paquete, `cmdi_94` terminó por *timeout*; en la corrida validada, `sqli_75` devolvió HTTP 500. Ambas entradas se contaron como no bloqueadas.

Esta evaluación tiene limitaciones que acotan su alcance. Se realizó una sola corrida, con 200 solicitudes por categoría. Los corpus de path traversal y cmdi son sintéticos, y la categoría `xss` no tiene un corpus limpio, por lo que su cobertura permanece en el corpus de 590 payloads. A la fecha de redacción de este capítulo (10 de octubre de 2026), las configuraciones 3a y 3b no se repitieron, de modo que la comparación con el WAF también permanece en ese corpus. Los resultados de la Ronda 5 con `rf_v10`/`if_v9` se conocieron el 24 de septiembre de 2026, y el modelo `rf_v11`/`if_v10` se reconstruyó el 26 de septiembre de 2026. El historial no vincula ambos hechos, por lo que esta no es una evaluación estrictamente ciega del modelo reconstruido. Por último, este capítulo no evalúa la causa de la diferencia de path traversal entre ambas corridas (de 85.0 % a 95.0 %).

### Falsos positivos en aplicaciones de terceros

En la aplicación vulnerable del proyecto, con el User-Agent por defecto de Artillery, ninguna petición benigna de los escenarios normal y de volumen recibió una respuesta 403 (cifras en la sección de resultados de Config 2, obtenidas con el par `rf_v11`/`if_v10`, primera versión del 30 de agosto de 2026, `a7c015f5…`/`3cf8e45c…`); el resultado cambia con User-Agent de navegador, como se describe a continuación. En aplicaciones de terceros la proporción de peticiones benignas bloqueadas fue alta. En OWASP Juice Shop (modo `monitor`, solo peticiones benignas), 303 de 312 peticiones con User-Agent de navegador (97.1 %) y 123 de 312 con `curl` (39.4 %) recibieron el veredicto de bloqueo. Con un User-Agent de navegador se bloquearon 37 de 40 peticiones benignas en dvws-node (92.5 %) y 5 de 5 en DVNA, medición preliminar. En node-api-goat se bloquearon 50 de 50 valores enviados a una sola ruta, todos con el User-Agent de Chrome 128 (`evidence/node-api-goat/run-attacks.js`); el chequeo de cinco peticiones con ese mismo User-Agent dio 4 de 5. En dvws-node, el User-Agent por defecto de Node bloqueó 30 de 40 (75 %).

La medición en Juice Shop usó la copia local de Juice Shop (par C), no el paquete publicado en npm. Esa copia contiene `rf_v11` e `if_v10` (SHA-256 `25b407e6…` y `5be28ee8…`), los mismos que el repositorio de entrenamiento conserva en `training/models/`. Para dvna, node-api-goat y dvws-node, el paquete y el modelo exactos de cada medición no constan en el repositorio.

### Consumo de memoria y CPU

La memoria y la CPU se midieron con `docker stats` sobre el contenedor de la aplicación, no sobre un proceso. La CPU se expresa como porcentaje del contenedor, de modo que 100 % equivale a un núcleo. La medición corresponde a la misma ejecución del experimento de latencia en Linux nativo (ejecución 36276690236), en un runner `ubuntu-latest` con 2 vCPU y 7.8 GiB de memoria, con cinco repeticiones por condición. La ventana A, primaria, excluye los primeros 15 s de cada repetición, que corresponden al calentamiento a baja carga; la ventana B (repetición completa) sí lo incluye.



| **Escenario** | **Memoria baseline / active (MiB)** | **$`\Delta`$Memoria (MiB)** | **CPU baseline / active (% de un núcleo)** | **$`\Delta`$CPU (pp / relativo)** |
|:---|:--:|:--:|:--:|:--:|
| Ataque | 63.2 / 394.8 | 331.9 | 16.1 / 101.3 | 85.1 pp / 529.6 % |
| Normal | 65.2 / 397.5 | 332.0 | 14.5 / 103.3 | 88.9 pp / 614.4 % |
| Volumen | 83.3 / 459.1 | 375.9 | 82.3 / 115.3 | 33.0 pp / 40.1 % |

Memoria y CPU del contenedor con y sin middleware, por escenario (ventana A).


Fuente: `docs/evidence/resources_summary.json`, rama `docs/latency-linux-evidence`, ventana A. Medias por condición; $`\Delta`$Memoria y $`\Delta`$CPU son la media de las diferencias pareadas por repetición. Elaboración propia.

El Cuadro 37.12 usa la ventana A, que descarta los primeros 15 s de cada repetición. La ventana B, que conserva la repetición completa con el arranque, da una $`\Delta`$CPU relativa mayor en los tres escenarios (541.3 %, 668.9 % y 57.5 %). Ambas ventanas llevan a la misma conclusión: ningún escenario cumple el criterio de CPU.

El criterio de memoria del protocolo es de 150 MB de memoria adicional, equivalentes a unos 143 MiB. Se aplica al incremento $`\Delta`$Memoria que añade el middleware, no a la memoria absoluta del contenedor. Los incrementos medios fueron de 331.9 MiB en ataque, 332.0 MiB en normal y 375.9 MiB en volumen. Los tres superan el límite, y cada uno es más del doble de los 143 MiB, por lo que el criterio no se cumple en este experimento. El repositorio del proyecto revisó internamente este límite a 300 MB; esta tesis mantiene el criterio del protocolo. Los tres incrementos (331.9, 332.0 y 375.9 MiB, es decir, 348.0, 348.1 y 394.2 MB) superan también ese valor revisado. El incremento es casi el mismo en los escenarios normal y de ataque (331.9 y 332.0 MiB).

El límite se fijó antes de medir la memoria nativa de `onnxruntime-node` y pensando en instancias de 1 GB (Droplet). El contenedor completo con el middleware activo ocupó entre 394.8 y 459.1 MiB (ataque, normal y volumen: 394.8, 397.5 y 459.1 MiB), y no se probó en una instancia de 1 GB, por lo que el cumplimiento en ese entorno no se verificó. El criterio de CPU aprobado es un $`\Delta`$CPU relativo de hasta 15 % bajo carga normal y de ataque. Ambos escenarios lo superan (529.6 % y 614.4 %), y el escenario de volumen también (40.1 %).

Estas cifras corresponden a una sola corrida (ejecución 36276690236, commit medido f15a9e8) en un runner de 2 vCPU, con cinco repeticiones por condición. Se midió el contenedor completo con `docker stats`, sin separar sus procesos, por lo que el costo no se atribuye a ningún componente. El archivo de datos tiene SHA-256 `b96d9014…2290187cec`.

La memoria con el middleware activo es prácticamente la misma en los escenarios normal y de ataque, y se mantiene en un rango similar entre repeticiones. La corrida de monitoreo continuo de 41.9 minutos (374 muestras) registró un pico de 494.8 MiB, medido sobre el contenedor.

No se midió el costo por componente. La configuración crea tres `worker_threads`: dos workers de Isolation Forest (`IF_POOL_SIZE` = 2) y uno de Random Forest. Las cifras de este experimento corresponden al conjunto del middleware y no pueden atribuirse a ninguno de sus componentes.

Estas cifras no son comparables con el RSS de 245.11 MB del benchmark aislado de `logSguarDian` (`benchmarks/onnx-memory-pool.bench.js`). Ese benchmark no incluye carga HTTP ni contenedor y no tiene línea base sin middleware.

## Resultados de interpretabilidad: análisis SHAP

El análisis de interpretabilidad se calculó con `shap.TreeExplainer` sobre el modelo `rf_v11` (`training/models/rf_v11.pkl`) y la partición de validación (`training/splits/val.parquet`), con las características de entrada del modelo seleccionadas por nombre. El *script* es `training/results/shap_analysis.py`, y los reportes y figuras de esta sección están en `training/results/`. La importancia global de una característica para una clase es la media del valor absoluto de su valor SHAP sobre la partición de validación, para la salida de esa clase.

### Importancia global por clase

El Cuadro 37.13 presenta, para cada una de las cinco clases, las tres características de mayor importancia global y la posición (entre las diez primeras) de `ua_length` y `ua_present`. Las Figuras 37.1 a 37.5 muestran las diez características de mayor importancia de cada clase. La Figura 37.2 muestra la importancia SHAP global de la clase `sqli`. La Figura 37.3 muestra la de la clase `xss`. La Figura 37.4 muestra la de la clase `path_traversal`.



| **Clase** | **Tres características de mayor importancia (media $`|`$SHAP$`|`$)** | **Posición de `ua_length`** | **Posición de `ua_present`** |
|:---|:---|:--:|:--:|
| `benign` | `ua_length` (0.08659); `ua_present` (0.05109); `path_depth` (0.03777) | 1 | 2 |
| `sqli` | `ua_length` (0.07342); `sqli_keyword_density` (0.05159); `ua_present` (0.03683) | 1 | 3 |
| `xss` | `alert_function_present` (0.03458); `xss_marker_density` (0.0274); `html_tag_count` (0.02689) | 5 | 8 |
| `path_traversal` | `traversal_sequence_count` (0.05172); `special_char_ratio` (0.03731); `ua_length` (0.03207) | 3 | 4 |
| `cmdi` | `method_is_get` (0.02554); `ua_length` (0.02122); `subshell_count` (0.01584) | 2 | 9 |

Características de mayor importancia SHAP global por clase de `rf_v11` y posición de las características de *User-Agent*.


Fuente: `training/results/shap_global_report.json`. Elaboración propia.

![Importancia SHAP global, clase `benign`.](figuras/shap_global_benign.png)

Fuente: elaboración propia, `training/results/shap_analysis.py`.

![Importancia SHAP global, clase `sqli`.](figuras/shap_global_sqli.png)

Fuente: elaboración propia, `training/results/shap_analysis.py`.

![Importancia SHAP global, clase `xss`.](figuras/shap_global_xss.png)

Fuente: elaboración propia, `training/results/shap_analysis.py`.

![Importancia SHAP global, clase `path_traversal`.](figuras/shap_global_path_traversal.png)

Fuente: elaboración propia, `training/results/shap_analysis.py`.

![Importancia SHAP global, clase `cmdi`.](figuras/shap_global_cmdi.png)

Fuente: elaboración propia, `training/results/shap_analysis.py`.

En la lista de diez características de `cmdi` no figuran `shell_command_count` ni `pipe_count`.

Las características del User-Agent figuran entre las de mayor contribución. `ua_length` ocupa el primer lugar en `benign` (0.0866) y en `sqli` (0.0734), el segundo en `cmdi` y el tercero en `path_traversal`; `ua_present` ocupa el segundo lugar en `benign` y el tercero en `sqli`. En el caso local de `sqli` del Cuadro 37.14, `ua_length` aporta +0.1136, la mayor contribución individual. Solo el 0.4 % de las filas benignas tiene un User-Agent largo (más de 40 caracteres), frente a entre 33.3 % (`xss`) y 97.7 % (`path_traversal`) en las clases de ataque.

### Explicaciones locales

Las Figuras 37.6 y 37.7 presentan la explicación local de dos peticiones `GET /profile`, una sin *User-Agent* y otra con él, y la Figura 37.8 la de una petición de `sqli` del conjunto de prueba de extremo a extremo (`e2e/fixtures/test_payloads.jsonl`). En cada caso el valor SHAP corresponde a la clase de mayor probabilidad predicha, y el valor base es 0.2000. El Cuadro 37.14 reporta los valores SHAP de `ua_present` y `ua_length` en los tres casos.



| **Caso** | **Clase predicha (probabilidad)** | **Valor de `ua_present`; SHAP** | **Valor de `ua_length`; SHAP** | **Mayor contribución (SHAP)** |
|:---|:---|---:|---:|---:|
| `GET /profile` sin *User-Agent* | `xss` (0.650) | 0; $`+0.0596`$ | 0; $`+0.0678`$ | `path_length` ($`+0.1008`$) |
| `GET /profile` con *User-Agent* | `benign` (0.533) | 1; $`-0.0498`$ | 75; $`-0.0327`$ | `special_char_ratio` ($`+0.0566`$) |
| Petición de `sqli` del conjunto de extremo a extremo | `sqli` (0.999) | 1; $`+0.0485`$ | 68; $`+0.1136`$ | `ua_length` ($`+0.1136`$) |

Valores SHAP locales de las características de *User-Agent* y mayor contribución, para la clase predicha de cada caso.


Fuente: valores SHAP recalculados con `training/results/shap_analysis.py` sobre `rf_v11`; figuras en `training/results/shap_local_*.png`. Elaboración propia.

![Explicación local de `GET /profile` sin *User-Agent* (clase `xss`).](figuras/shap_local_profile_no_ua.png)

Fuente: elaboración propia, `training/results/shap_analysis.py`.

![Explicación local de `GET /profile` con *User-Agent* (clase `benign`).](figuras/shap_local_profile_with_ua.png)

Fuente: elaboración propia, `training/results/shap_analysis.py`.

![Explicación local de una petición de `sqli` detectada (clase `sqli`).](figuras/shap_local_attack_sqli.png)

Fuente: elaboración propia, `training/results/shap_analysis.py`.

## Limitaciones de los resultados

La regla R2 no se cumplió para la generación vigente. El conjunto de prueba se leyó tres veces para `rf_v11`/`if_v10`, el 24, el 25 y el 26 de septiembre de 2026, y las cifras de este capítulo corresponden a la lectura del 26 de septiembre. La sección de Recolección, procesamiento y validación de datos describe las tres lecturas.

Los objetivos de calibración de Isolation Forest se endurecieron después de fallos observados en el conjunto de prueba. En `if_v2`, la tasa de falsos positivos fue de 0.1011 frente a un límite de 0.10; en `if_v5`, de 0.0811 frente a un objetivo interno de 0.08. El límite formal del objetivo específico 2 se mantiene en una tasa de falsos positivos de 10 %.

El umbral de 0.35 de Random Forest se calibró sobre validación para `rf_v3` y no se recalibró para `rf_v11`. Como se indicó en la sección de resultados del objetivo específico 2, las métricas de prueba de Random Forest se calculan por argmax y no con este umbral.

De las 1 468 filas de `cmdi` del conjunto de prueba, 261 (17.8 %) son sintéticas. Su generador no está versionado en el repositorio, por lo que esas filas no pueden regenerarse a partir del código del proyecto.

En el conjunto de entrenamiento, CAPEC aporta el 81.3 % de las filas de `sqli` y el 85.8 % de las de `path_traversal`, y modsec-learn el 69.6 % de las filas `benign`. Además, 1 221 de las 6 853 filas de `cmdi` del entrenamiento (17.8 %) son sintéticas.

La fuente de los datos restaurados el 23 de septiembre de 2026 no está documentada. Además, `unified.jsonl` contiene 383 083 filas y `features.parquet` contiene 383 202; la diferencia de 119 filas corresponde a las filas de telemetría curada del pipeline de MLOps, que `unify.py` excluye y `ct_pipeline.py` añade después.

Las pruebas en aplicaciones de terceros muestran una tasa alta de bloqueo de tráfico benigno, y la contribución del User-Agent al modelo, descrita en la sección SHAP. Este trabajo no evaluó el modelo con un corpus benigno alternativo. El conjunto de tráfico benigno no cubre la diversidad de clientes HTTP que cabría esperar en un entorno real.

La contribución de Isolation Forest a la detección se midió solo sobre el conjunto de validación (anexo, sección 38.10). Marca 19 de los 39 ataques que Random Forest no bloquea, y bloquear sus marcas agregaría 866 falsos positivos. No se evaluó sobre el conjunto de prueba. Por diseño, este componente no bloquea peticiones; su salida solo enriquece los registros.

Los datos crudos de latencia de Config 2 no constan en el repositorio: los reportes de Artillery de los experimentos en Docker no están versionados, porque `attack-sim/results/` está excluido en `.gitignore`. Las cifras de Config 2 se documentan en `docs/config2-latency-evaluation.md` del repositorio `logSguarDian-vulnerable-project`. Los reportes del experimento de latencia en Linux nativo se conservan en el artefacto de GitHub Actions `latency-benchmark-results` (id 10917957439, ejecución 36276690236), copiado a `docs/evidence/latency-linux-2026-09-26.tgz` del repositorio `logSguarDian-vulnerable-project` (rama `main`).

En cuanto a memoria y CPU, las cifras y el alcance de la medición se describen en la subsección 37.3.8. El indicador heurístico `possibleLeak` de la corrida de monitoreo de 41.9 minutos compara las mitades de una serie que mezcla condiciones distintas, por lo que no es concluyente. Además, 60 s por repetición no bastan para descartar una fuga de memoria.

La confusión entre `cmdi` y `sqli` en técnicas de tiempo ciego es la limitación de etiquetado más marcada. En la re-medición del 9 de septiembre de 2026 con `rf_v11`/`if_v10`, los 200 payloads de inyección de comandos del corpus se etiquetaron todos como `sqli` y ninguno como `cmdi`; 198 se bloquearon y 2 se registraron como `pass_anomaly`. El corpus usa oráculos de tiempo (`sleep`) y comparaciones aritméticas, y el hallazgo afecta la clase reportada en el triaje, no la decisión de bloqueo. Como los 200 payloads coinciden con filas de las particiones de entrenamiento, validación o prueba (sección 37.3.5), la medición no constituye evidencia de generalización. Una evaluación sobre un corpus sin solapamiento, con las cautelas que allí se describen, se presenta en la subsección 37.3.6. Fuentes: `docs/config2-results-v1.md`, §5.1, del repositorio `logSguarDian`, y `attack-sim/cmdi_sqli_attribution_rfv11_2026-09-09.json` del repositorio `logSguarDian-vulnerable-project` (commit 14c0e15).

Los 100 payloads por categoría de la cobertura de Config 2 tampoco son disjuntos del entrenamiento, y la cobertura no se recalculó sin esas coincidencias; véase la subsección 37.3.2.

El conjunto de prueba se vectoriza a partir de las cadenas almacenadas, mientras que el middleware reconstruye la query con `URLSearchParams` antes de extraer las características, lo que modifica algunas de ellas para la misma petición (por ejemplo, `quote_count` pasa de 1 a 0 con el payload `' OR 1=1--`). Las métricas de prueba de este capítulo no incluyen ese efecto, que no se midió.

A la fecha de redacción de este capítulo (10 de octubre de 2026), el paquete publicado en npm (`logsguardian@0.1.0`, par A) contiene `rf_v10`/`if_v9`. Esos modelos son los que se evaluaron de extremo a extremo en las Configuraciones 1 a 3b. En esa fecha, las métricas de modelo de este capítulo corresponden a `rf_v11`/`if_v10`, disponibles en el repositorio y no publicados.

# Discusión de resultados

Este capítulo interpreta los resultados del capítulo de Resultados frente a los criterios de aceptación de los tres objetivos específicos. No introduce mediciones nuevas.

## Pipeline de ingeniería de características

El extractor cumple el criterio del objetivo específico 1. El p95 mixto del ciclo de ida y vuelta a un `worker_threads` es de 0.0273 ms (Cuadro 37.1), frente al límite de 5 ms. La medición aísla la extracción y excluye la inferencia, el registro de eventos y la respuesta HTTP.

El incremento de latencia de extremo a extremo en Linux es de 12.08 ms en carga normal y de 12.85 ms en carga de ataque, más de 400 veces el costo del extractor (subsección 37.3.2). La extracción no explica el sobrecosto del middleware. El middleware crea tres `worker_threads`, dos de Isolation Forest y uno de Random Forest (sección 37.3.8), comunica los hilos por mensajes y persiste los eventos en SQLite. Este trabajo no midió el costo de cada componente por separado, y su atribución queda como trabajo futuro.

## Modelo híbrido

El Random Forest supera el F1 de 0.80 en las cuatro clases de ataque. El macro es de 0.9776, con un mínimo de 0.9239 en `cmdi` (Cuadro 37.3). El Isolation Forest alcanza un *recall* de 91.25 % con una tasa de falsos positivos de 5.46 %, frente a un mínimo de 50 % y un máximo de 10 % (Cuadro 37.4). Ambos criterios del objetivo específico 2 se cumplen con margen.

Estas cifras miden la separación entre clases dentro del corpus. Tres hechos acotan su lectura como estimación del desempeño en producción. El conjunto de prueba de `rf_v11` se leyó tres veces, el 24, el 25 y el 26 de septiembre de 2026, y se reporta la última lectura (0.9776), inferior a la de la primera (0.9843). El umbral de Isolation Forest también cambió entre esas lecturas, de 0.00807 a 0.00421; el historial de ese cambio se describe en la sección 38.10. El F1 se calcula por argmax y no incluye el umbral de decisión de 0.35, calibrado con `rf_v3` y sin recalibrar para `rf_v11` (sección 37.5). Un barrido sobre validación confirma que el valor es estable entre 0.30 y 0.40, aunque no demuestra que sea óptimo (sección 38.10). Además, 261 de las 1 468 filas de `cmdi` del conjunto de prueba (17.8 %) son sintéticas, y `cmdi` es la clase de menor F1.

El Isolation Forest no bloquea peticiones, porque el diseño reserva esa decisión al Random Forest. Su criterio se cumple como detector individual. Sobre el conjunto de validación, marca 19 de los 39 ataques que el Random Forest deja pasar, pero bloquear sus marcas agregaría 866 benignos bloqueados de más (sección 38.10). Esas cifras son optimistas, porque el umbral de Isolation Forest se eligió sobre el mismo conjunto de validación.

## Falsos positivos y generalización

En la aplicación de referencia, ninguna petición benigna de Artillery recibió un 403. El escenario normal envió 6 300 solicitudes por repetición, incluido el calentamiento (subsección 37.3.2). Con cadenas de User-Agent de navegadores reales se bloquearon 13 de 15 combinaciones (subsección 37.3.2).

En cuatro aplicaciones de terceros, el modelo bloqueó entre 92.5 % y 100 % del tráfico benigno con un User-Agent de navegador (subsección 37.3.7). Las muestras son pequeñas: 5 peticiones en DVNA, 40 en dvws-node y 50 valores enviados a una sola ruta en node-api-goat. En OWASP Juice Shop, con 312 peticiones, el bloqueo fue de 97.1 %. Con `curl`, Juice Shop bajó a 39.4 %, y con el User-Agent por defecto de Node, dvws-node bajó a 75 %.

El User-Agent amplifica el bloqueo, pero no lo explica por completo: con `curl`, Juice Shop bloquea todavía el 39.4 %. El análisis SHAP (Cuadro 37.13) coincide: `ua_length` es la característica de mayor contribución en las clases `benign` y `sqli`. Solo el 0.4 % de las filas benignas del corpus tiene un User-Agent largo, frente a entre 33.3 % y 97.7 % en las clases de ataque. El modelo aprendió esa diferencia del corpus. Una explicación consistente con los datos es que el corpus benigno no representa el tráfico de aplicaciones reales. Este trabajo no la verificó con un corpus benigno alternativo. La recomendación de ampliar el corpus benigno y volver a medir estos falsos positivos se formula en el capítulo [cap:recomendaciones].

## Cobertura en la evaluación integrada

Con el corpus sin solapamiento (Cuadro 37.11), la cobertura supera el 80 % en `sqli`, `path_traversal` y `cmdi` con ambos pares de modelos. Con el paquete publicado (`rf_v10`/`if_v9`) es de 100 %, 85.0 % y 91.5 %, y con `rf_v11`/`if_v10` es de 99.5 %, 95.0 % y 96.0 %. El corpus es el mismo en ambas corridas, así que la diferencia de 10 puntos en `path_traversal` corresponde al cambio de modelo, y su explicación está pendiente. Con el paquete publicado, el límite inferior del intervalo de Wilson (79.4 %) queda bajo el criterio, por lo que el cumplimiento con ese par es frágil (subsección 37.3.6). La Ronda 5 no es una evaluación estrictamente ciega del modelo reconstruido: los resultados con el paquete publicado se conocieron el 24 de septiembre y el modelo vigente se reconstruyó el 26, y el historial no vincula ambos hechos.

La Ronda 5 no incluye XSS. La cobertura de esa categoría proviene del corpus de 590 payloads de SecLists (Cuadro 37.9): 97.3 %, y 97.2 % al excluir las coincidencias con el entrenamiento. En ese corpus, los 200 payloads de `cmdi` coinciden con datos de entrenamiento, y su cobertura de 100 % no es evidencia de generalización. Con el criterio de igualdad normalizada, la cobertura de `sqli`, `xss` y `path_traversal` cambia como máximo 0.1 puntos al excluir las coincidencias; `sqli` y `path_traversal` no tienen coincidencias exactas (subsección 37.3.5).

Sobre esos 590 payloads, ModSecurity (CRS, nivel de paranoia 1) bloqueó 93.2 %, logSguarDian 98.8 % y ambos en capas 99.5 %. De los 40 ataques que el WAF no bloqueó (11 de `sqli`, 3 de `xss` y 26 de `path_traversal`), logSguarDian bloqueó 37. Los tres restantes pasaron ambas capas, y ninguno de los 40 es de `cmdi`. La comparación no se repitió con el corpus de la Ronda 5.

## Latencia, memoria y CPU

El criterio del objetivo específico 3 ($`\Delta`$p95 $`\leq`$ 15 ms) se cumple en carga normal (12.08 ms) y de ataque (12.85 ms), con márgenes de 2.92 y 2.15 ms. No se cumple en volumen: el $`\Delta`$p95 es de 6 495.46 ms y el 7.00 % de las peticiones termina por tiempo de espera. Esas peticiones no entran en el p95, por lo que la cifra subestima la cola.

El protocolo fijaba un incremento de hasta 10 % de la latencia media sobre la línea base. Esta tesis reporta el incremento relativo del p95, que fue de +485.1 % y +278.1 % en carga normal y de ataque, y no reporta la media. Con líneas base de 2.49 y 4.62 ms, el 10 % equivale a 0.25 y 0.46 ms. El incremento relativo del p95 se presenta como indicador complementario y no como el criterio del protocolo. Los datos son de una sola corrida en un ejecutor de 2 vCPU, con cinco repeticiones por condición (subsección 37.3.2).

La memoria aumenta 331.9, 332.0 y 375.9 MiB en ataque, normal y volumen, más del doble del límite de 150 MB (unos 143 MiB) (Cuadro 37.12). El incremento es casi igual en normal y ataque, lo que sugiere un costo fijo asociado a la carga de los modelos. Esa interpretación no se verificó. La CPU aumenta 85.1 y 88.9 puntos porcentuales (+529.6 % y +614.4 %) en ataque y normal, frente a un límite de 15 %. El contenedor completo usa entre 394.8 y 459.1 MiB y no se probó en una instancia de 1 GB, para la que se fijó el límite (sección 37.3.8).

## Comparación con trabajos previos

IntelliWAF [29] combina un Random Forest y un Isolation Forest con reglas y limitación de tasa, y opera como proxy inverso externo a la aplicación. Reporta una exactitud de 91.5 % del Random Forest sobre CSIC 2010 (61 065 muestras) y no reporta latencia de detección. Este trabajo difiere en la arquitectura, embebida en el proceso de la aplicación, y en el papel del Isolation Forest, que no participa en el bloqueo. Las diferencias de conjunto de datos y de métrica impiden comparar cifras de detección.

## Cumplimiento de los objetivos

| **Objetivo** | **Criterio** | **Resultado** | **Estado** |
|:---|:---|:---|:---|
| OE1 | Extractor $`\leq`$ 5 ms por petición | 0.0273 ms (ida y vuelta al *worker*) | Cumple |
| OE2 | F1 $`\geq`$ 0.80 en al menos 3 de 4 clases | 4 de 4 (mínimo 0.9239) | Cumple |
| OE2 | *Isolation Forest*: *recall* $`\geq`$ 50 %, falsos positivos $`\leq`$ 10 % | 91.25 % y 5.46 % | Cumple |
| OE3 | Cobertura $`\geq`$ 80 % por categoría | 99.5, 95.0 y 96.0 % en `sqli`, `path_traversal` y `cmdi`; XSS: 97.3 % sobre el corpus de 590 | Cumple; XSS sin corpus limpio |
| OE3 | $`\Delta`$p95 $`\leq`$ 15 ms | 12.08 ms (normal) y 12.85 ms (ataque) | Cumple; volumen no cumple |
| Protocolo | Memoria adicional $`\leq`$ 150 MB | +332 MiB | No cumple |
| Protocolo | $`\Delta`$CPU $`\leq`$ 15 % | +530 % a +614 % | No cumple |

Cumplimiento de los criterios de aceptación por objetivo específico y criterio del protocolo.

Fuente: capítulo de Resultados (Cuadros 37.1, 37.3, 37.4, 37.11, 37.9 y 37.12, y subsección 37.3.2). Elaboración propia. OE: objetivo específico.

# Conclusiones

_Sin contenido redactado: el archivo fuente `k-conclusiones.tex` está vacío o solo contiene comentarios._
# Recomendaciones
## Infraestructura complementaria: un pipeline de MLOps para reentrenamiento continuo

El capítulo de Alcance excluye explícitamente el aprendizaje continuo y el reentrenamiento automático embebido en el proceso de la aplicación anfitriona, por ser incompatible con el principio de operación autónoma sin dependencias externas que rige el diseño de logSguarDian en tiempo de ejecución. Esa exclusión sigue vigente: la librería npm entregada no reentrena modelos dentro del proceso de la aplicación que protege. Durante el desarrollo del proyecto, sin embargo, el equipo construyó y verificó, como infraestructura separada y exploratoria –no como parte del paquete npm ni de sus dependencias en tiempo de ejecución–, un pipeline de ocho fases para el ciclo completo de recolección de telemetría, reentrenamiento y despliegue controlado de nuevas versiones del modelo híbrido. Se documenta aquí como recomendación de arquitectura de producción para quien adopte logSguarDian a escala, y no como parte del alcance evaluado en los objetivos específicos de este trabajo.

La motivación de esta exploración es directa: cada cambio al pipeline de extracción de características exige un reentrenamiento completo del modelo, condición que el proyecto siguió de forma estricta a lo largo de sus más de diez ciclos de reentrenamiento documentados. Un despliegue real de logSguarDian a múltiples aplicaciones cliente enfrentaría el mismo problema de forma recurrente, y sin un mecanismo que sistematice la recolección de evidencia de producción, la curación de esa evidencia y la validación de un modelo candidato antes de promoverlo, cada ciclo de mejora tendría que repetirse manualmente. El pipeline construido –bajo el directorio `packages/mlops` del repositorio del proyecto– explora si ese proceso puede automatizarse sin comprometer la garantía de bloqueo del modelo en producción.

Las ocho fases del pipeline son las siguientes:

1.  **Recolección de telemetría.** Un endpoint dedicado recibe únicamente el vector de 76 características de cada petición clasificada, nunca el payload crudo, siguiendo el mismo patrón de notificación asíncrona sin bloqueo (*fire-and-forget*) ya empleado por el sistema de webhooks de la librería.

2.  **Simulación de flota.** Múltiples fuentes simuladas envían telemetría de forma concurrente para poblar un corpus de validación representativo de un despliegue con varios clientes.

3.  **Agrupamiento de anomalías.** El componente no supervisado (Isolation Forest) y un algoritmo de agrupamiento por densidad (DBSCAN) se aplican sobre el espacio de 63 características que consume el modelo no supervisado, para aislar patrones estadísticamente atípicos sin necesidad de una etiqueta previa.

4.  **Curación humana.** Una interfaz de línea de comandos presenta los grupos resultantes para revisión manual y genera un archivo con el mismo esquema que consume el script de unificación del corpus de entrenamiento del proyecto.

5.  **Reentrenamiento orquestado.** Un script coordina de punta a punta la unificación del corpus curado, el reentrenamiento del modelo híbrido y la generación de los artefactos ONNX correspondientes, reutilizando el mismo pipeline de entrenamiento documentado en el capítulo de Alcance.

6.  **Validación automática mediante cinco criterios de aceptación (*gates*).** Se verifican, en orden creciente de costo computacional y con interrupción inmediata ante el primer fallo (*fail-fast*): el contrato de features del modelo candidato, sus métricas de precisión y recall frente al conjunto de prueba bloqueado, la paridad de predicción entre el modelo en Python y su versión serializada en ONNX, su desempeño sobre la suite de pruebas end-to-end, y su huella de memoria bajo la arquitectura real de *worker pool* de producción.

7.  **Despliegue canario.** Un modelo candidato que aprueba los cinco criterios anteriores se evalúa mediante dos mecanismos: reemplazo del corpus de prueba etiquetado como mecanismo primario de decisión, y una ventana acotada de sombra sobre tráfico en vivo como mecanismo secundario, nunca como proceso continuo indefinido.

8.  **Promoción o reversión.** La promoción de un modelo candidato a producción exige el cumplimiento simultáneo de un criterio estricto –cero casos en los que el candidato deje pasar un ataque que el modelo en producción bloquea correctamente– y un criterio de concordancia general de al menos 99.5% entre los veredictos de bloqueo del candidato y los del modelo vigente sobre el corpus de reemplazo.

Como prueba de concepto, el pipeline de reentrenamiento se ejecutó el 29 de agosto de 2026 sobre telemetría simulada: 244 eventos de cinco fuentes simuladas (sim-host-1 a sim-host-5, 238 eventos, que reparten el corpus de payloads de prueba) y de una fuente dedicada (sim-host-novel, 6 eventos), que envió seis réplicas de un payload poliglota diseñado para combinar, en una sola petición, sintaxis de las cuatro categorías de ataque cubiertas. El reporte de agrupamiento (DBSCAN con `eps` 2.5 y `min_samples` 3) registra 183 eventos anómalos y 16 grupos, además de un grupo de ruido de 53 eventos. Las seis réplicas formaron un grupo propio, con puntaje de anomalía promedio de $`-0.153`$, inferior al umbral de 0.002486 que usa el script de agrupamiento (el de `if_v9`), y el componente supervisado las clasificó como XSS. Según un comentario del script generador, una versión anterior del script, con un payload ofuscado de una sola clase, no produjo esa separación; esa versión no se conserva en el repositorio. Dos cautelas acotan el resultado: las seis peticiones son réplicas idénticas, por lo que su agrupación no mide la capacidad de generalizar a variantes distintas, y el reporte proviene de una sola ejecución local, conservada fuera del repositorio (SHA-256 `7fb882d5…e7e6`).

Se recomienda, para quien adopte logSguarDian en un despliegue con múltiples aplicaciones cliente, evaluar la maduración de esta infraestructura complementaria –hoy una prueba de concepto verificada, no un servicio productivo– como mecanismo de mantenimiento a largo plazo del modelo, manteniendo en todo momento la separación arquitectónica ya adoptada en este proyecto entre la librería embebida que protege la aplicación en tiempo real y la infraestructura externa que sostiene su ciclo de mejora continua.

Como trabajo futuro, queda pendiente medir la memoria y la CPU por componente en el mismo entorno de medición: solo Random Forest, Random Forest más un worker de Isolation Forest, y la configuración actual de tres `worker_threads`. Con esas mediciones debería evaluarse también `IF_POOL_SIZE` = 1. Este trabajo no establece el resultado de esas mediciones.

## Ampliación del corpus benigno

Se recomienda ampliar el corpus benigno con tráfico representativo de cada aplicación objetivo y volver a medir los falsos positivos en aplicaciones de terceros con el mismo protocolo descrito en la subsección 37.3.7.

# Anexos
## Revalidación del umbral de decisión de Random Forest y aporte de Isolation Forest

Este anexo verifica si el umbral de decisión de Random Forest se mantiene estable para la generación `rf_v11`, y mide qué aporta Isolation Forest (`if_v10`) a la detección cuando se combina con Random Forest. Todas las cifras provienen de la evaluación sobre el conjunto de validación, no sobre el conjunto de prueba.

### Revalidación del umbral de Random Forest

El umbral `RF_THRESHOLD = 0.35` se fijó sobre el conjunto de validación con `rf_v3` y se mantuvo en las generaciones posteriores sin recalibración (`docs/decision-policy.md`, §2.2.1, del repositorio logSguarDian). Para `rf_v11` se repitió el barrido sobre el conjunto de validación de 57 481 filas, sin cambiar el valor desplegado. El autor definió el criterio de estabilidad antes de ejecutar el barrido; no consta registro en el repositorio. El criterio exige que la variación entre los umbrales 0.30 y 0.40 sea menor que 0.5 puntos porcentuales, tanto en la tasa de bloqueo benigno como en el recall global.

Las variaciones observadas fueron de 0.0067 puntos porcentuales en la tasa de bloqueo benigno y de 0.056 puntos porcentuales en el recall global, por lo que el criterio se cumple. Esta lectura acota el resultado a estabilidad y no a optimalidad. Con un recall cercano a 99.9 %, la validación discrimina poco entre los umbrales 0.20 y 0.40. El umbral no se recalibró, y la Configuración 2 y la Ronda 5 se mantienen con 0.35.

El Cuadro 38.2 presenta el barrido completo.



| **Umbral** $`T`$ | **Benignos bloqueados (%)** | **Recall global (%)** | **`sqli`** | **`xss`** | **`path_traversal`** | **`cmdi`** |
|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.114 | 99.930 | 99.977 | 99.666 | 99.842 | 99.796 |
| 0.25 | 0.114 | 99.930 | 99.977 | 99.666 | 99.842 | 99.796 |
| 0.30 | 0.114 | 99.930 | 99.977 | 99.666 | 99.842 | 99.796 |
| **0.35** | **0.107** | **99.908** | **99.962** | **99.644** | **99.723** | **99.796** |
| 0.40 | 0.107 | 99.873 | 99.938 | 99.577 | 99.644 | 99.659 |
| 0.45 | 0.107 | 99.775 | 99.877 | 99.443 | 99.446 | 98.978 |
| 0.50 | 0.107 | 99.634 | 99.780 | 99.354 | 99.051 | 98.093 |
| 0.55 | 0.067 | 99.364 | 99.598 | 99.043 | 98.378 | 96.594 |
| 0.60 | 0.067 | 99.117 | 99.417 | 98.798 | 97.785 | 95.436 |
| 0.65 | 0.054 | 98.742 | 99.117 | 98.397 | 97.191 | 93.733 |
| 0.70 | 0.047 | 98.296 | 98.695 | 98.063 | 96.598 | 92.643 |
| 0.75 | 0.027 | 97.610 | 98.053 | 97.506 | 95.728 | 90.872 |
| 0.80 | 0.020 | 96.774 | 97.218 | 96.794 | 95.055 | 89.373 |
| 0.85 | 0.020 | 95.976 | 96.537 | 95.569 | 94.146 | 87.330 |
| 0.90 | 0.013 | 94.858 | 95.576 | 94.166 | 92.642 | 84.128 |

Barrido del umbral de decisión de Random Forest (`rf_v11`) sobre el conjunto de validación de 57 481 filas. Las columnas por clase son recall en porcentaje.


Fuente: `_evidencia/revalidacion-umbral-if/analysis_out.txt`, sección 1. Elaboración propia.

### Aporte de Isolation Forest

Con $`T = 0.35`$, Random Forest deja pasar 39 de los 42 594 ataques del conjunto de validación. Isolation Forest marca 19 de esos 39 ataques: 5 de 13 de `sqli`, 10 de 16 de `xss`, 4 de 7 de `path_traversal` y ninguno de los 3 de `cmdi` que Random Forest dejó pasar. El Cuadro 38.3 resume estas cifras.

Se evaluó una regla hipotética que bloquea una petición si cualquiera de los dos modelos la marca. Esa regla eleva el recall global de 99.908 % a 99.953 %. El costo es un aumento del bloqueo benigno de 0.107 % a 5.925 %, es decir, 866 benignos adicionales bloqueados. El umbral de Isolation Forest (0.004206) se eligió sobre este mismo conjunto de validación, por lo que estas cifras son optimistas. La regla no se desplegó.

Estas cifras respaldan que Isolation Forest solo registre. Su aporte en detección es de 19 ataques frente a 42 594, mientras que bloquear sus marcas agregaría 866 falsos positivos. Según el diseño del sistema, las marcas de Isolation Forest se registran con veredicto `pass_anomaly` y no bloquean (`packages/core/src/middleware.ts`, líneas 243–244 y 333–337 del repositorio logSguarDian).



| **Concepto** | **Casos** | **Valor** |
|:---|---:|---:|
| Ataques no bloqueados por Random Forest ($`T = 0.35`$) | 39 de 42 594 | — |
| Ataques de esos 39 marcados por Isolation Forest | 19 de 39 | — |
| `sqli` | 5 de 13 | — |
| `xss` | 10 de 16 | — |
| `path_traversal` | 4 de 7 | — |
| `cmdi` | 0 de 3 | — |
| Recall global, solo Random Forest | 42 555 de 42 594 | 99.908 % |
| Recall global, regla “RF o IF” | 42 574 de 42 594 | 99.953 % |
| Benignos bloqueados por Random Forest | 16 de 14 887 | 0.107 % |
| Benignos que Random Forest no bloquea y que Isolation Forest marca | 866 de 14 871 | 5.82 % |
| Benignos marcados por Isolation Forest (tasa global) | 874 de 14 887 | 5.87 % |
| Benignos bloqueados por la regla “RF o IF” | 882 de 14 887 | 5.925 % |

Aporte de Isolation Forest sobre el conjunto de validación con $`T = 0.35`$ y regla hipotética “RF o IF”.


Fuente: `_evidencia/revalidacion-umbral-if/analysis_out.txt`, sección 2. El numerador 874 no figura en esa salida; proviene de `_evidencia/revalidacion-umbral-if/ua_check_regenerado_out.txt` (suma de 807 y 67 marcas), y la tasa de 5.871 % coincide con `training/models/if_v10_metadata.json`. Elaboración propia.

### Dependencia de Isolation Forest respecto del User-Agent

De los 874 benignos que Isolation Forest marca en validación, 807 son filas sin User-Agent y 67 son filas con User-Agent. En las 14 818 filas benignas sin User-Agent, la tasa de marca es de 5.45 %. En cambio, entre las 69 filas benignas con User-Agent, Isolation Forest marca 67 (97.1 %). Este grupo es pequeño, por lo que la tasa no permite una estimación precisa. Sin embargo, es compatible con una dependencia de Isolation Forest respecto de las características de User-Agent, que conviene vigilar (`_evidencia/revalidacion-umbral-if/ua_check_regenerado_out.txt`).

### Limitaciones

Este análisis usa una sola partición de validación de 57 481 filas. No se dispone de una segunda partición que permita medir la variación entre particiones.

El umbral de Random Forest (0.35) se eligió sobre validación con `rf_v3`. El umbral de Isolation Forest de `if_v10` (0.004206) se eligió sobre validación como el máximo recall con tasa de falsos positivos menor o igual a 0.06 (`training/retrain_v11_contract69.py`, líneas 107–110). Para `rf_v11`, el gate de validación exige al menos tres de las cuatro clases de ataque con F1 mayor o igual a 0.80 (línea 60). Sus hiperparámetros, como `n_estimators=30` y `max_depth=25` (línea 51), están fijados en el script, que no realiza búsqueda de hiperparámetros sobre validación.

El umbral de Isolation Forest pasó de 0.00807 a 0.00421 entre las lecturas del conjunto de prueba. El umbral de 0.00807 corresponde al modelo previo al reentrenamiento, leído el 24 de septiembre de 2026. El de 0.00421 corresponde al modelo reentrenado, leído el 25 y el 26 de septiembre de 2026, y se calculó sobre validación. El historial no atribuye ese cambio al resultado de la primera lectura, pero no puede descartarse su influencia. Este hecho acota la afirmación de que el umbral se fijó solo sobre validación.

Isolation Forest no se evaluó fuera de validación en este anexo. La regla R2 de la metodología impide una nueva lectura del conjunto de prueba, por lo que la regla “RF o IF” no se midió sobre dicho conjunto.

Los scripts `analysis.py` y `part3.py` usan rutas absolutas de la máquina del autor, por lo que requieren ajustarlas para reproducirse.

### Procedencia

Los modelos evaluados son `rf.onnx` e `if.onnx` del par C, descrito en la sección de pares de modelos (sección 36.3.1). Sus sumas SHA-256 completas son las del Cuadro 38.4. El commit del repositorio logSguarDian que produjo estos modelos es `03de50f`. El archivo `analysis_out.txt` no registra el commit de ejecución; durante la verificación, el árbol de trabajo estaba limpio en el commit `41553a7`.



| **Archivo**                                        | **SHA-256** |
|:---------------------------------------------------|:------------|
| `rf.onnx` (modelo, par C)                          |             |
| `if.onnx` (modelo, par C)                          |             |
| `analysis_out.txt`                                 |             |
| `part3_out.txt`                                    |             |
| `ua_check.txt`                                     |             |
| `analysis.py` (genera `analysis_out.txt`)          |             |
| `part3.py` (genera `part3_out.txt`)                |             |
| `ua_check_regenerado.py` (regenera `ua_check.txt`) |             |
| `ua_check_regenerado_out.txt`                      |             |

Sumas SHA-256 de los modelos evaluados, de los archivos de evidencia y de los scripts que los generaron o regeneraron.


Fuente: hashes de los modelos, de `training/models/` en el commit `03de50f` del repositorio logSguarDian; hashes de los archivos de evidencia y de los scripts, calculados con `shasum -a 256` sobre `_evidencia/revalidacion-umbral-if/`. El script original que generó `ua_check.txt` no se conserva; `ua_check_regenerado.py` es una regeneración que reproduce las cifras de validación de ese archivo, y su salida se guarda en `ua_check_regenerado_out.txt`. La línea de `ua_check.txt` sobre el `login` no se reproduce, porque depende de `login_vec.json`. Elaboración propia.

# Bibliografía

[1] A. L. Buczak and E. Guven, “A survey of data mining and machine learning methods for cyber security intrusion detection,” *IEEE Communications Surveys & Tutorials*, vol. 18, no. 2, pp. 1153–1176, 2016, doi: [10.1109/COMST.2015.2494502](https://doi.org/10.1109/COMST.2015.2494502).

[2] I. H. Sarker, A. S. M. Kayes, S. Badsha, H. Alqahtani, P. Watters, and A. Ng, “Cybersecurity data science: An overview from machine learning perspective,” *Journal of Big Data*, vol. 7, no. 1, pp. 1–29, 2020, doi: [10.1186/s40537-020-00318-5](https://doi.org/10.1186/s40537-020-00318-5).

[3] A. Verma and V. Ranga, “Machine learning based intrusion detection systems for IoT paradigms and datasets: A review,” *IEEE Access*, vol. 8, pp. 180664–180709, 2020, doi: [10.1109/ACCESS.2020.3027778](https://doi.org/10.1109/ACCESS.2020.3027778).

[4] D. S. Berman, A. L. Buczak, J. S. Chavis, and C. L. Corbett, “A survey of deep learning methods for cyber security,” *Information*, vol. 10, no. 4, p. 122, 2019, doi: [10.3390/info10040122](https://doi.org/10.3390/info10040122).

[5] L. Zhen, N. Hafizah Kamarudin, V. Jyn Kok, and F. Qamar, “Anomaly detection model in network security situational awareness based on machine learning: Limitation, techniques, and future trends,” *IEEE Access*, vol. 13, pp. 126084–126129, 2025, doi: [10.1109/ACCESS.2025.3589620](https://doi.org/10.1109/ACCESS.2025.3589620).

[6] A. Rahman, S. Sultana, U. Twaha, and M. Rowshon, “AI-enhanced web application firewalls for protecting united states critical infrastructure against zero-day exploits,” *Scientia. Technology, Science and Society*, vol. 3, no. 2, pp. 11–32, 2026, doi: [10.59324/stss.2026.3(2).02](https://doi.org/10.59324/stss.2026.3(2).02).

[7] L. Breiman, “Random forests,” *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001, doi: [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324).

[8] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in *2008 eighth IEEE international conference on data mining*, IEEE, 2008, pp. 413–422. doi: [10.1109/ICDM.2008.17](https://doi.org/10.1109/ICDM.2008.17).

[9] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A survey,” *ACM Computing Surveys*, vol. 41, no. 3, pp. 1–58, 2009, doi: [10.1145/1541880.1541882](https://doi.org/10.1145/1541880.1541882).

[10] A. Shiravi, H. Shiravi, M. Tavallaee, and A. A. Ghorbani, “Toward developing a systematic approach to generate benchmark datasets for intrusion detection,” *Computers & Security*, vol. 31, no. 3, pp. 357–374, 2012, doi: [10.1016/j.cose.2011.12.014](https://doi.org/10.1016/j.cose.2011.12.014).

[11] P. Warden and D. Situnayake, *TinyML: Machine learning with TensorFlow lite on arduino and ultra-low-power microcontrollers*. O’Reilly Media, 2019.

[12] OWASP Foundation, “OWASP top 10: 2021. The most critical web application security risks.” <https://owasp.org/Top10/>, 2021.

[13] Verizon, “2024 data breach investigations report (DBIR).” <https://www.verizon.com/business/resources/reports/dbir/>, 2024.

[14] Snyk, “State of open source security report 2024.” <https://snyk.io/reports/state-of-open-source-security/>, 2024.

[15] Mastercard, “Cyber insights report: Threat landscape in latin america.” Mastercard Cybersecurity, 2024.

[16] OpenJS Foundation, “Node.js documentation: Event loop and worker threads.” <https://nodejs.org/en/docs>, 2024.

[17] E. Yuan and S. Malek, “A taxonomy and survey of self-protecting software systems,” in *2012 7th international symposium on software engineering for adaptive and self-managing systems (SEAMS)*, IEEE, 2012, pp. 109–118. doi: [10.1109/SEAMS.2012.6224397](https://doi.org/10.1109/SEAMS.2012.6224397).

[18] OWASP Foundation, “OWASP core rule set (CRS) project.” <https://owasp.org/www-project-modsecurity-core-rule-set/>, 2024.

[19] M. Zimmermann, C.-A. Staicu, C. Tenny, and M. Pradel, “Small world with high risks: A study of security threats in the npm ecosystem,” in *28th USENIX security symposium (USENIX security 19)*, USENIX Association, 2019, pp. 995–1010.

[20] T. G. Dietterich, “Ensemble methods in machine learning,” in *Multiple classifier systems. MCS 2000. Lecture notes in computer science*, Springer, 2000, pp. 1–15. doi: [10.1007/3-540-45014-9_1](https://doi.org/10.1007/3-540-45014-9_1).

[21] I. Goodfellow, Y. Bengio, and A. Courville, *Deep learning*. MIT Press, 2016.

[22] A. Zheng and A. Casari, *Feature engineering for machine learning: Principles and techniques for data scientists*. O’Reilly Media, 2018.

[23] T. Fawcett, “An introduction to ROC analysis,” *Pattern Recognition Letters*, vol. 27, no. 8, pp. 861–874, 2006, doi: [10.1016/j.patrec.2005.10.010](https://doi.org/10.1016/j.patrec.2005.10.010).

[24] <span class="nocase">J. Bai, F. Lu, K. Zhang, *et al.*

[25] F. Pedregosa *et al.*, “Scikit-learn: Machine learning in Python,” *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.

[26] G. Lucz and B. Forstner, “A thirty-day dataset of malicious HTTP requests blocked by OWASP ModSecurity on a production web server,” *Data*, vol. 10, no. 11, 2025, doi: [10.3390/data10110186](https://doi.org/10.3390/data10110186).

[27] Miessler, Daniel, “SecLists.” <https://github.com/danielmiessler/SecLists>.

[28] Swissky, “PayloadsAllTheThings.” <https://github.com/swisskyrepo/PayloadsAllTheThings>.

[29] P. K. Shinde, Y. R. Ingole, N. P. Tikore, G. S. Gosavi, and S. B. Chaudhari, “IntelliWAF: A six-layer intelligent web application firewall with machine learning and anomaly detection for real-time web threat mitigation,” *International Journal of Engineering Research & Technology (IJERT)*, vol. 15, no. 6, 2026, doi: [10.5281/zenodo.20917852](https://doi.org/10.5281/zenodo.20917852).

[^1]: Se reporta el percentil 95, no la media, dado que es más representativo de la experiencia real de un usuario bajo carga y menos sensible a valores atípicos que un promedio aritmético.
