# logSguarDian — Trabajo de Graduación

Documento de tesis para optar al grado de Ingeniería en Ciencia de la Computación y Tecnologías de la Información, Facultad de Ingeniería, Universidad del Valle de Guatemala.

**Título:** logSguarDian: Desarrollo de una Librería para la Detección de Amenazas de Seguridad en Endpoints de Aplicaciones

**Autor:** Diego Pablo Valenzuela Palacios (carné 22309)
**Asesor:** Ing. Erick Francisco Marroquín Rodríguez

## Estructura del repositorio

El documento está escrito en LaTeX usando la plantilla oficial de trabajos de graduación IE-MT de UVG. El archivo maestro es [z-main.tex](z-main.tex), que ensambla los capítulos mediante `\input`:

| Archivo | Capítulo |
|---|---|
| `d-introduccion.tex` | Introducción |
| `e-antecedentes.tex` | Antecedentes |
| `f-justificacion.tex` | Justificación |
| `g-objetivos.tex` | Objetivos |
| `h-alcance.tex` | Alcance |
| `i-marco_teorico.tex` | Marco teórico |
| `j-capitulos.tex` | Capítulos de desarrollo |
| `k-conclusiones.tex` | Conclusiones |
| `l-recomendaciones.tex` | Recomendaciones |
| `n-anexos.tex` | Anexos |
| `m-bibliografia.bib` | Referencias bibliográficas |

Datos del estudiante, título, asesor y tribunal se configuran en [0-datos_estudiante.tex](0-datos_estudiante.tex).

## Compilación

Requiere una distribución de TeX (TeX Live) con `latexmk`, `pdflatex` y `biber`.

```bash
latexmk -pdf z-main.tex
```

El PDF generado (`z-main.pdf`) y los archivos auxiliares de compilación no se versionan (ver `.gitignore`).
