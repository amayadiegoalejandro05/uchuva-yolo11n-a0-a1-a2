# Acciones de licencia, procedencia declarada y propuesta MIT

Actualización: **2026-10-14**, sobre el commit documental `0b23a48f1d331138f173080afbf4e585a4c79f39`.
Estado: **procedencia de los cuatro scripts declarada por el investigador;
confirmaciones jurídicas pendientes; MIT propuesta, todavía no adoptada**.
El estado científico y el PASS estadístico previamente documentados no cambian.

## A. Procedencia declarada

El investigador responsable confirmó expresamente que desarrolló para su
investigación los cuatro scripts siguientes, con asistencia de Codex y ChatGPT:

- evaluation/original/validate_all.py
- operational_metrics/original/operational_recall.py
- difficulty_analysis/original/integral_difficulty.py
- statistics/original/scripts/plot_a0_a1_a2_paired_map_deltas.py

Ninguno fue copiado de un repositorio externo, según esa declaración. Fueron
recuperados de otros directorios del propio entorno de investigación, no de
repositorios de terceros. La ubicación de recuperación no determina autoría ni
derechos. Ya no se los clasifica como código de procedencia externa no identificada.

## B. Evidencia de autoría y asistencia de IA

Existe una **declaración explícita del investigador**, registrada por archivo/hash
en [RESEARCHER_CODE_PROVENANCE_DECLARATION.md](provenance/review/RESEARCHER_CODE_PROVENANCE_DECLARATION.md).
No se efectuó una auditoría jurídica independiente de titularidad o de restricciones.
No se atribuye titularidad a Codex o ChatGPT ni autoría científica del artículo a
esas herramientas. La revisión, validación, documentación y mantenimiento del
código corresponden a los investigadores. La descripción del uso de IA no sustituye
los requisitos de transparencia que establezca la revista.

## C. Derechos pendientes y clasificación actual

| Material | Procedencia/autoría documentada | Derechos y licencia actuales |
|---|---|---|
| Los cuatro scripts anteriores | Desarrollo propio del investigador con asistencia de IA, según declaración explícita | No licencia definitiva; confirmar titular(es), nombre legal, año, restricciones institucionales y autorización de otros titulares si existen |
| Configuraciones y resultados del estudio | Procedencia del estudio/derivados documentada en manifiestos; no se altera | No se extiende MIT automáticamente; confirmar derechos y alcance si se incluyen en una adopción futura |
| Cierre original, lock y demás documentos históricos | Procedencia documental registrada, no reescrita | La declaración recibida se refiere a los cuatro scripts, no aclara titularidad de todos los documentos; no aplicarles MIT por inferencia |
| Documentación de revisión y esta propuesta | Elaborada por encargo de revisión del propietario | Autorización de cambios documentales verificada por la tarea; no equivale a una licencia general de distribución |
| Bibliotecas externas no vendorizadas | Distribuciones de terceros con sus propios términos | Mantienen sus licencias; MIT no se aplica a ellas |

La declaración resuelve el vacío de **procedencia declarada** de los scripts, pero
no documenta por sí sola la titularidad efectiva ni elimina posibles restricciones
institucionales o derechos de otros colaboradores. No se inventan permisos,
contratos o acuerdos. Tampoco se presume una licencia MIT heredada de otro proyecto.

## D. Licencia propuesta

El investigador acepta **MIT como propuesta** para los componentes originales sobre
los que los titulares tengan facultad de licenciamiento. El texto oficial, con
campos pendientes y alcance condicional, está en
[PROPOSED_LICENSE_MIT.md](PROPOSED_LICENSE_MIT.md). No se creó LICENSE definitivo,
no se asignó una licencia a dependencias ni a documentos de titularidad no aclarada.

## Auditoría histórica

provenance/LICENSING_REVIEW.md se conserva sin cambios. La nota posterior de
procedencia enlazada arriba complementa ese documento: la recuperación desde otro
directorio del entorno propio no es evidencia de copia de terceros. RELEASE_AUDIT.md
y MISSING_FILES.md mantienen su contexto temporal, no se reescriben retrospectivamente.

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

## Confirmaciones y próximos pasos

**Antes de aprobar esta documentación o hacer merge del PR:** los autores deben
revisar la fidelidad de la declaración registrada, el alcance parcial de Code
Availability y que MIT figure únicamente como propuesta condicional. El merge de
documentación no debe describirse como adopción de una licencia definitiva.

**Antes de un LICENSE definitivo y de una versión científica estable v1.0.0:**

1. Confirmar titular o titulares efectivos del código y el nombre legal del aviso.
2. Confirmar el año o años correspondientes, sin inferirlos de esta revisión.
3. Documentar la ausencia de restricciones institucionales aplicables.
4. Confirmar si existen otros titulares/colaboradores con derechos y obtener sus
   autorizaciones, o confirmar que no hay otros titulares que deban autorizar.
5. Aprobar el alcance por componente y las atribuciones; solo entonces adoptar
   MIT para material propio licenciable, mediante una acción futura autorizada.

Estas confirmaciones son bloqueos reales para la **adopción definitiva de MIT**;
no son razones para modificar resultados ni repetir entrenamientos. El launcher
ausente, los pesos no distribuidos y los entornos incompletos siguen siendo
limitaciones explícitas de reproducibilidad histórica, no se solucionan con una licencia.
No se propone merge automático, release, tag, DOI ni cambio de visibilidad.
