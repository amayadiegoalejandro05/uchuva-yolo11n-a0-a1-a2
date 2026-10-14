# Acciones de licencia y autoría

Revisión: **2026-10-14**, snapshot `715265ec848be0e1b4e8b2d4398dfa530cf8921e`.
Estado: **derechos de redistribución no resueltos para una versión científica definitiva**.
La visibilidad pública no demuestra que las licencias estén resueltas. No se
asigna una licencia, no se elimina material y no se presupone cobertura MIT heredada.
`provenance/LICENSING_REVIEW.md` se conserva como auditoría de preparación histórica.

## Evidencia disponible

No existe LICENSE/COPYING ni atribución de titulares verificable en el snapshot.
Los cuatro scripts Python no contienen encabezados de autoría/licencia explícita.
file_inventory.json documenta sus directorios externos de recuperación y hashes,
pero una ruta de procedencia no prueba autoría ni permiso de redistribución. El
propietario de GitHub, el autor técnico de un commit y la autorización de esta
tarea tampoco prueban por sí solos titularidad de código previo.

## Clasificación de archivos y acciones

| Clasificación solicitada | Archivos o material | Evidencia y acción |
|---|---|---|
| Autorización verificada | Esta revisión documental y su PR | Autorización explícita del propietario en la tarea. Alcance: editar documentos, ejecutar el análisis aislado y proponer un PR; no es una licencia de distribución del software histórico |
| Autorización pendiente | evaluation/original/validate_all.py | Recuperado de directorio externo; autor/titular y permiso escrito no documentados. Confirmar ambos antes de la versión definitiva |
| Autorización pendiente | operational_metrics/original/operational_recall.py | Misma limitación; no inferir que importar Ultralytics confiera licencia sobre este script |
| Autorización pendiente | difficulty_analysis/original/integral_difficulty.py | Misma limitación; comentarios de protocolo/v2 no establecen autoría ni autorización |
| Autorización pendiente | statistics/original/scripts/plot_a0_a1_a2_paired_map_deltas.py | Código posterior recuperado, PASS numérico no demuestra derechos; confirmar autoría y permiso |
| Autorización pendiente | provenance/original/A0_A1_A2_CIERRE_FINAL_2026-09-21.md y A0_A1_A2_campaign_final_lock.json | Procedencia de cierre documentada; no se identifica un titular o concesión explícita por archivo. Autores deben confirmar autorización y atribución |
| Material original sin licencia explícita | results/** y configs/** | Materiales del estudio/derivados según sus manifiestos, no código de dependencias; preservar atribución y obtener confirmación del titular. «Original» describe procedencia, no una conclusión jurídica de autoría |
| Material original sin licencia explícita | README.md, RELEASE_AUDIT.md, MISSING_FILES.md, requirements.txt, training/RECOVERY_STATUS.md, statistics/RECOVERY_STATUS.md, .gitignore, .gitattributes y SHA256SUMS.txt | Documentación, listas de dependencias y controles elaborados al preparar el paquete; no se observa una concesión de licencia en estos archivos |
| Material original sin licencia explícita | provenance/reconstructed/**, provenance/SOURCE_ROOTS.md y provenance/LICENSING_REVIEW.md | Documentación y manifiestos derivados; no acreditan ni sustituyen una concesión de derechos sobre sus fuentes |
| Material original sin licencia explícita | Documentos y manifiestos añadidos por este PR bajo raíz y provenance/review/** | Revisión solicitada por el propietario; no incorpora una licencia retroactiva. El README histórico archivado conserva su condición original |
| Material de terceros con licencia identificada | Dependencias externas, no vendorizadas: NumPy, SciPy, Matplotlib, Ultralytics, PyTorch, Pillow y pandas | Ver tabla siguiente. Esas licencias cubren sus distribuciones respectivas, no asignan automáticamente licencia a estos scripts |

Ningún script científico recuperado se clasifica como autorización de redistribución
verificada. No se encontró material de terceros vendorizado con licencia explícita
en el snapshot; esto no prueba autoría independiente de cada implementación.
Las menciones de bibliotecas/metadata de software no son copias de sus paquetes.

## Dependencias de terceros: licencias identificadas, sin relicenciar el repositorio

La evidencia procede de metadata de distribuciones instaladas inspeccionada el
2026-10-14. Las tres primeras se usaron efectivamente en la prueba; las restantes
se inspeccionaron solo para contexto de licencia, **no se importaron ni ejecutaron**.
Estas versiones locales no son un lock de entrenamiento histórico.

| Distribución observada | Licencia identificada en su metadata | Alcance |
|---|---|---|
| NumPy 1.26.4 | BSD; texto con tres cláusulas | Dependencia usada en esta prueba |
| SciPy 1.17.1 | BSD; texto con tres cláusulas | Dependencia usada en esta prueba |
| Matplotlib 3.10.8 | Acuerdo Matplotlib; classifier PSF License | Revisar su acuerdo propio, no atribuir una licencia genérica al repositorio |
| Ultralytics 8.4.21 | AGPL-3.0; classifier AGPLv3+ | Versión local no usada en esta prueba; distinta del 8.4.157 histórico. Revisar términos de la distribución realmente utilizada en futuras ejecuciones |
| PyTorch 2.9.1+cpu | BSD-3-Clause | Dependencia externa no usada aquí |
| Pillow 12.1.1 | License-Expression MIT-CMU | Dependencia externa no usada aquí |
| pandas 3.0.3 | BSD 3-Clause | Dependencia externa no usada aquí |

Fuentes primarias de referencia consultadas:
[Ultralytics LICENSE](https://github.com/ultralytics/ultralytics/blob/main/LICENSE),
[Matplotlib license](https://matplotlib.org/stable/project/license.html),
[NumPy license](https://numpy.org/doc/stable/license.html) y
[SciPy LICENSE](https://github.com/scipy/scipy/blob/main/LICENSE.txt).
Las páginas actuales no se usan para inventar equivalencia con releases históricos.
Dependencias/transitivos pueden contener avisos adicionales; no se distribuyen en este PR.

## Bloqueos y tareas concretas

1. **Bloqueo:** autores/titulares deben confirmar por escrito la autoría y derechos
   de redistribución de cada uno de los cuatro scripts recuperados y del cierre.
   Una declaración o permiso identificable por archivo/hash permite resolverlo;
   no basta con la existencia pública del repositorio.
2. **Bloqueo:** tras esa confirmación, autores deben acordar la licencia y las
   atribuciones aplicables a su material, separando cualquier aportación externa;
   este PR no hace esa elección ni aplica MIT/AGPL/otra licencia.
3. Verificar los términos del depósito de dataset y dependencias si se redistribuyen
   en otro paquete futuro. Aquí los datos/pesos/paquetes no se redistribuyen; el DOI
   se enlaza y la licencia del dataset **no fue verificada**.

No se recomienda repetir entrenamientos para resolver derechos. Tampoco se cambia
visibilidad ni se eliminan archivos de forma silenciosa. Los autores deciden cómo
resolver la autorización de materiales ya visibles antes de una versión definitiva.
