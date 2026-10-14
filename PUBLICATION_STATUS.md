# Estado actual de publicación

Fecha de revisión: **2026-10-14**, America/Bogota.
Repositorio: [https://github.com/amayadiegoalejandro05/uchuva-yolo11n-a0-a1-a2](https://github.com/amayadiegoalejandro05/uchuva-yolo11n-a0-a1-a2).
Commit de `main` inspeccionado y evaluado: `715265ec848be0e1b4e8b2d4398dfa530cf8921e`.
Rama de propuesta documental: `docs/final-scientific-release-review`.

## Disponibilidad y alcance

GitHub confirmó `visibility=public`, propietario `amayadiegoalejandro05` y rama
predeterminada `main`; un fetch remoto confirmó el SHA anterior. La copia local
estaba limpia y contenía 149 archivos versionados. La verificación describe ese
snapshot, no presupone un commit posterior de revisión ni una versión científica
estable. Esta revisión no cambia visibilidad, no hace merge, no crea release,
tag definitivo ni DOI. La aprobación del PR corresponde a los autores.

El repositorio público permite inspeccionar los materiales recuperados; la
disponibilidad pública no equivale a una licencia resuelta o a reproducir el
entrenamiento completo. A0/A1/A2 mantiene tres condiciones, cinco seeds emparejadas,
quince corridas, cincuenta épocas, evaluación en validation y la regla operacional
maximum_recall_subject_to_precision_ge_0.98. No se altera ninguna receta ni threshold.
A1−A2 es la adición conjunta de HSV y Mosaic, no identifica efectos individuales.

## Código disponible y evidencia ejecutada

| Componente | Archivos disponibles | Estado en esta revisión |
|---|---|---|
| Revalidación global | evaluation/original/validate_all.py | Inspección estática; no ejecutado; requiere pesos y validation externos |
| Métrica operacional | operational_metrics/original/operational_recall.py | Inspección estática; no ejecutado; matching IoU≥0.50 y OP fijo por corrida |
| Dificultad y descriptivos emparejados | difficulty_analysis/original/integral_difficulty.py | Inspección estática; no ejecutado; requiere GT validation externo y predicciones |
| Análisis posterior de mAP | statistics/original/scripts/plot_a0_a1_a2_paired_map_deltas.py | Ejecutado sin modificaciones en temporal separado: PASS numérico |
| Configuraciones | configs/documentary_redacted y configs/extracted_redacted | Exports y train_args depurados, no launchers portátiles históricos |
| Resultados y procedencia | results y provenance | Integridad documental verificada; datos de modelo no recalculados |

## Componentes únicamente documentados o ausentes

- Launcher de entrenamiento y args.yaml históricos no recuperados.
- Quince checkpoints presentes en el manifiesto de hashes, pero no distribuidos.
- Identidad exacta del peso preentrenado inicial no recuperada con hash verificable.
- Stack cloud completo documentado directamente para A0 seed01; no evidencia de
  un entorno Python/PyTorch/CUDA idéntico en todas las corridas. Ultralytics 8.4.157
  está documentado en los checkpoints formales según la auditoría preservada.
- Versión/activación de Albumentations y raw logs completos no recuperados. El cierre
  documenta el bloque interno observado en A0 seed01; A0 no es augmentation-free.
- Implementación completa de todos los IC y Wilcoxon del cierre no recuperada.
- Metadata de dominio/curación y correspondencia del depósito Figshare con el
  split histórico no verificadas independientemente.

## Autorizaciones y pruebas

Actualización de procedencia del 2026-10-14: el investigador responsable declaró
expresamente haber desarrollado los cuatro scripts para su investigación con
asistencia de Codex y ChatGPT, sin copiarlos de repositorios externos. Los otros
directorios de recuperación pertenecían al mismo entorno de investigación.
La declaración está registrada con los hashes intactos en
[RESEARCHER_CODE_PROVENANCE_DECLARATION.md](provenance/review/RESEARCHER_CODE_PROVENANCE_DECLARATION.md).

Esa evidencia declarativa no es auditoría jurídica independiente. Faltan confirmar
titular(es), nombre legal, año de copyright, restricciones institucionales y derechos
de otros titulares si existen. MIT es aceptada como **propuesta condicional**, no
como licencia vigente; únicamente se prepara PROPOSED_LICENSE_MIT.md, sin LICENSE
definitivo. Véase [LICENSING_ACTIONS.md](LICENSING_ACTIONS.md). Las herramientas de
IA se documentan como asistencia, no como titulares ni autores científicos.

[VERIFICATION_REPORT.md](VERIFICATION_REPORT.md) conserva la única ejecución de
esta fase: análisis posterior emparejado mAP sobre summaries existentes. Se observó
Windows, Python 3.12.3, NumPy 1.26.4, SciPy 1.17.1 y Matplotlib 3.10.8. No se ejecutaron
entrenamientos, inferencias, otros evaluadores, tests unitarios ni Wilcoxon; no se
usaron imágenes, GT, pesos o test. Las métricas cerradas permanecen intactas.

## Contexto de auditorías históricas

RELEASE_AUDIT.md, MISSING_FILES.md, provenance/LICENSING_REVIEW.md y los registros
reconstruidos de preparación se conservan sin cambios. Sus frases «no publicado»
o «no ejecutado» describen aquella preparación, no el estado actual del repositorio.
El README anterior queda archivado con su hash original; INTEGRITY_SCOPE.md separa
el manifiesto del candidato de la documentación revisada.

## Próximos pasos y límites

**Antes del merge documental:** aprobación de los autores de la declaración,
los documentos de procedencia y el borrador de disponibilidad; MIT debe seguir
identificada como propuesta, sin adopción implícita mediante el merge.

**Bloqueos reales antes de MIT definitiva y release v1.0.0:** confirmar titular(es),
nombre legal, año de copyright, ausencia de restricciones institucionales y
autorización de otros titulares si existen; aprobar alcance y atribuciones por
componente. La procedencia declarada de los scripts ya no es desconocida, pero
esas condiciones jurídicas no están resueltas. La versión estable debe declarar
un alcance de reproducibilidad histórica parcial.

**Limitaciones que deben declararse, no corregirse mediante nuevos experimentos:**
launcher ausente, pesos excluidos, entornos históricos incompletos y código de
cierre estadístico no recuperado. Una versión parcial puede documentarlos.

**Mejoras opcionales:** recuperar artefactos históricos faltantes si existen,
verificar metadata/versionado de Figshare y agregar un lock para el entorno del
análisis posterior. No se propone repetir entrenamientos ni abrir test.
