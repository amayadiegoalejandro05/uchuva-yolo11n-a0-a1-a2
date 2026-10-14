# Cierre documental — campaña A0/A1/A2

**Fecha de cierre:** 2026-09-21  
**Estado:** `CLOSED_WITH_DOCUMENTED_LIMITATIONS`  
**Alcance:** campaña separada de *Classical Augmentation v2*. Sus métricas absolutas no deben mezclarse silenciosamente con las de v2.

## 1. Pregunta experimental

La campaña compara tres condiciones con YOLO11n y cinco semillas emparejadas:

- **A0:** baseline con los coeficientes de augmentation configurables objetivo de la campaña fijados en cero. **No debe describirse como literalmente “sin augmentation”**, porque el log de A0 seed01 muestra un bloque interno/default de Albumentations.
- **A1:** política nativa estándar de Ultralytics: geometría + HSV + Mosaic.
- **A2:** ablación geométrica de A1: `translate=0.1`, `scale=0.5` y `fliplr=0.5`, con HSV y Mosaic desactivados.

Los contrastes deben interpretarse así:

- **A1−A0:** política estándar completa frente al baseline con los coeficientes configurables objetivo fijados en cero.
- **A2−A0:** paquete geométrico frente al baseline con los coeficientes configurables objetivo fijados en cero.
- **A1−A2:** adición **conjunta** de HSV + Mosaic al mismo paquete geométrico. Este contraste no separa el efecto individual de HSV y Mosaic.

## 2. Dataset actual de esta campaña

| Split | Imágenes | Objetos |
|---|---:|---:|
| train | 1062 | 2882 |
| validation | 109 | 312 |
| test | 109 | 311 |
| **Total** | **1280** | **3505** |

El `validation` usado en la revalidación homogénea tiene fingerprint local:

`30e92af8e4b7b46a74512f4e5a68d92f790c7c9aa4d6f9edc03f3662a958d6c2`

### Estado de dominio semicampo

La curación de trabajo usada para esta campaña considera `val/test` como conjuntos sin las imágenes de laboratorio. **Sin embargo, esto aún no está respaldado por metadato reproducible dentro del perfil actual**, que registra que no se encontró metadata fiable laboratorio/semicampo. Por tanto, para el manuscrito la afirmación “109 imágenes solo de semicampo” queda **pendiente de un artefacto de procedencia/curación reproducible**.

## 3. Entrenamiento formal congelado

- Modelo: **YOLO11n**
- Tarea: detección, una clase (`calyx`)
- Condiciones: **3**
- Semillas: **1–5**
- Corridas formales: **15**
- Épocas: **50**
- `imgsz=640`
- `batch=8`
- `optimizer=AdamW`
- `lr0=0.001`
- `lrf=0.01`
- `workers=8`
- `deterministic=true`
- `AMP=false`
- `rect=false`
- `max_det=300`

Los *smoke tests* de 5 épocas quedan documentados como diagnóstico técnico y **no forman parte de la inferencia estadística formal**.

### Corrección importante sobre A0 y el pipeline interno

El `Console` de A0 seed01 muestra explícitamente:

```text
albumentations: Blur(p=0.01, blur_limit=(3, 7)),
MedianBlur(p=0.01, blur_limit=(3, 7)),
ToGray(p=0.01, method='weighted_average', num_output_channels=3),
CLAHE(p=0.01, clip_limit=(1.0, 4.0), tile_grid_size=(8, 8))
```

Por tanto, **A0 no es un baseline absolutamente libre de augmentation**. La definición correcta es que A0 fijó en cero los coeficientes configurables que eran objeto de la campaña (HSV, transformaciones geométricas, Mosaic, MixUp, CutMix, Copy-Paste y parámetros afines conservados en la configuración formal), mientras el pipeline interno/default anterior permaneció activo al menos en la corrida A0 seed01.

Como el archivo preservado no contiene el mismo fragmento de consola para A1 y A2, no se afirma documentalmente que ese bloque interno fuera idéntico en las tres condiciones. En el manuscrito, por seguridad, los contrastes deben describirse como comparaciones entre **paquetes de augmentation configurados**, no como “augmentation vs. no augmentation”.


Los 15 checkpoints formales son únicos por SHA-256 y preservan **Ultralytics 8.4.157**.

Se recuperó además del `Console` de **A0 seed01** el entorno cloud:

- Ultralytics: **8.4.157**
- Python: **3.12.3**
- PyTorch: **2.14.0+cu132**
- CUDA build asociado al sufijo de PyTorch: **13.2**
- dispositivo reportado: `CUDA:3`
- GPU: **NVIDIA RTX PRO 6000 Blackwell Server Edition**
- VRAM reportada: **97252 MiB**

Este stack completo queda confirmado directamente para **A0 seed01**. No se afirma que Python/PyTorch/CUDA/GPU hayan sido idénticos en las 15 corridas porque los logs completos de A1/A2 no quedaron preservados en el archivo actual.

## 4. Revalidación homogénea

La comparación principal reproducible usa un evaluador local común:

- Python: `3.14.7`
- Ultralytics: `8.4.157`
- PyTorch: `2.14.0+cpu`
- CPU: `AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD`
- `imgsz=640`
- `batch=8`
- `workers=0`
- `conf=0.001`
- NMS `iou=0.7`
- `max_det=300`
- `rect=true`
- `augment=false`
- split: `val`

### Métricas globales

| Condición | mAP50-95 | mAP50 | mAP75 | Precision global | Recall global |
|---|---:|---:|---:|---:|---:|
| A0 | 0.6565 ± 0.0133 | 0.8869 ± 0.0100 | 0.7689 ± 0.0218 | 0.8457 ± 0.0224 | 0.8469 ± 0.0147 |
| A1 | 0.7284 ± 0.0015 | 0.9454 ± 0.0029 | 0.8594 ± 0.0102 | 0.8626 ± 0.0347 | 0.8774 ± 0.0317 |
| A2 | 0.7255 ± 0.0045 | 0.9439 ± 0.0033 | 0.8536 ± 0.0092 | 0.8510 ± 0.0292 | 0.8867 ± 0.0230 |

El efecto emparejado en mAP50-95 fue:

- **A1−A0:** `0.071849` (+7.18 pp) y **5/5** semillas positivas; IC95% t emparejado [0.055059, 0.088640].
- **A2−A0:** `0.068955` (+6.90 pp) y **5/5** semillas positivas; IC95% t emparejado [0.051324, 0.086585].
- **A1−A2:** `0.002895` (+0.29 pp) y 3/5 semillas positivas; IC95% [-0.001720, 0.007509].

Con `n=5`, el Wilcoxon exacto bilateral mínimo cuando las cinco diferencias tienen el mismo signo es `p=0.0625`; por ello la interpretación no debe descansar únicamente en pruebas de significancia.

## 5. Métrica operacional congelada

La regla queda fijada como:

`maximum_recall_subject_to_precision_ge_0.98`

Para cada corrida se seleccionó su propio threshold **exclusivamente en validation**.

Parámetros del análisis:

- objetivo de Precision: **≥ 0.98**
- `prediction_confidence_floor=0.001`
- NMS IoU: **0.70**
- `max_det=300`
- matching detección-GT: **IoU ≥ 0.50**
- estado del matching IoU: `provisional_unverified_against_classical_augmentation_v2`

| Condición | Recall @ P≥0.98 | Precision en OP | F1 en OP | FP | FN | Threshold |
|---|---:|---:|---:|---:|---:|---:|
| A0 | 0.3147 ± 0.2291 | 0.9874 ± 0.0073 | 0.4386 ± 0.2733 | 1.6 ± 1.3 | 213.8 ± 71.5 | 0.9621 ± 0.0128 |
| A1 | 0.5385 ± 0.1204 | 0.9824 ± 0.0020 | 0.6889 ± 0.1072 | 3.0 ± 0.7 | 144.0 ± 37.6 | 0.8630 ± 0.0344 |
| A2 | 0.5481 ± 0.0596 | 0.9816 ± 0.0011 | 0.7019 ± 0.0478 | 3.2 ± 0.4 | 141.0 ± 18.6 | 0.8716 ± 0.0210 |

Comparación emparejada:

- **A1−A0:** +0.2237 de Recall operacional; 4/5 semillas positivas; IC95% [-0.1244, 0.5718].
- **A2−A0:** +0.2333; 4/5 semillas positivas; IC95% [-0.0193, 0.4859].
- **A1−A2:** −0.0096; 3/5 semillas favorecen A1 y 2/5 A2; IC95% [-0.2244, 0.2052].

Por tanto, la señal operacional es favorable en promedio frente a A0, pero claramente más variable que la señal de mAP.

## 6. Casos difíciles en el operating point

El validation contiene:

- **101** objetos small
- **115** medium
- **96** large
- **19** objetos clustered
- **61** objetos con border contact

Definiciones:

- `small`: `bbox_area_ratio < 0.02423`
- `medium`: `0.02423 ≤ bbox_area_ratio < 0.05196`
- `large`: `bbox_area_ratio ≥ 0.05196`
- `clustered`: solapamiento con otra GT de la misma imagen, `IoU ≥ 0.05`
- `border_contact`: distancia normalizada mínima al borde `≤ 0.01`

| Métrica de recall | A0 | A1 | A2 | Δ A1−A0 | Δ A2−A0 |
|---|---:|---:|---:|---:|---:|
| Small | 0.1030 ± 0.0984 | 0.2198 ± 0.1336 | 0.2257 ± 0.0712 | +0.1168 (4/5) | +0.1228 (4/5) |
| Medium | 0.3878 ± 0.2960 | 0.6174 ± 0.1429 | 0.6243 ± 0.0767 | +0.2296 (4/5) | +0.2365 (4/5) |
| Large | 0.4500 ± 0.2998 | 0.7792 ± 0.0882 | 0.7958 ± 0.0380 | +0.3292 (4/5) | +0.3458 (5/5) |
| Clustered | 0.3263 ± 0.2616 | 0.5263 ± 0.1342 | 0.4842 ± 0.0686 | +0.2000 (3/5; 1 empate) | +0.1579 (3/5) |
| Border contact | 0.2721 ± 0.2066 | 0.4033 ± 0.1355 | 0.3803 ± 0.1267 | +0.1311 (3/5) | +0.1082 (4/5) |

El estrato de clusters debe interpretarse con especial cautela: solo hay **19 GT**, de modo que una detección cambia el recall del estrato en aproximadamente `1/19 = 5.26` puntos porcentuales.

## 7. Interpretación congelada

### Evidencia confirmada

1. **A1 y A2 aumentan mAP50-95 frente a A0 de forma direccionalmente consistente en 5/5 semillas.**
2. En promedio, **A1 y A2 también muestran mayor Recall @ P≥0.98** que A0, pero la dirección es 4/5 y la variabilidad es considerable.
3. Los recalls medios de `small`, `medium`, `large`, `clustered` y `border contact` son mayores para A1 y A2 que para A0.
4. **A1 y A2 permanecen muy próximas entre sí.** No hay separación clara que permita sostener un beneficio adicional global u operacional de añadir conjuntamente HSV + Mosaic sobre el paquete geométrico.
5. Los resultados son **compatibles** con que la geometría explique una parte sustancial de la mejora de la política completa, pero **no permiten atribuir causalmente** el efecto a `translate`, `scale` o `fliplr` por separado.

### Lo que NO se concluye

- No se declara una receta “ganadora” o “best”.
- No se afirma que A2 sea superior a A1.
- No se afirma que HSV o Mosaic sean inútiles individualmente.
- No se afirma mejora integral confirmada mediante un criterio predeclarado para esta campaña; el análisis que usa tolerancias históricas de v2 es solo una sensibilidad descriptiva.
- No se afirma generalización externa.
- No se compara directamente el valor absoluto de estas métricas con Classical Augmentation v2 debido al cambio de protocolo/split.

## 8. Test: decisión de cierre

**Test permanece congelado y no se usa para cerrar A0/A1/A2.**

No se abrirá para seleccionar recetas, thresholds, checkpoints, análisis o narrativa. El perfil actual lo registra como `frozen_but_historically_consulted`, por lo que incluso si se evalúa en el futuro no debe describirse como un holdout externo virgen.

Si posteriormente se decide usarlo, el análisis deberá estar cerrado antes y los operating points seleccionados en validation deberán trasladarse **sin reajuste**.

## 9. Limitaciones documentales congeladas

Estas limitaciones quedan **documentadas y aceptadas como parte del cierre**; no obligan a repetir entrenamientos:

1. El perfil reproducible actual no conserva metadata fiable laboratorio/semicampo. La curación de trabajo de los autores indica que las imágenes de laboratorio fueron retiradas de los subconjuntos revisados de 109 imágenes, pero esa procedencia no está codificada actualmente en un manifest de dominio verificable.
2. Para A0/A1/A2 el matching operacional queda fijado en `IoU ≥ 0.50`. No se afirma que sea idéntico al código histórico de Classical Augmentation v2.
3. El stack cloud completo (Python/PyTorch/CUDA/GPU) se recuperó directamente para A0 seed01. No se generaliza automáticamente a todas las corridas A1/A2 sin logs equivalentes.
4. El bloque interno de Albumentations se observó directamente en A0 seed01; no se conservó evidencia de consola equivalente para A1/A2.
5. `test` permanece congelado y fue consultado históricamente fuera de esta campaña; no es un holdout externo virgen.

### Redacción segura para el manuscrito

- A0: “baseline with the campaign-targeted configurable augmentation coefficients set to zero”.
- Evitar: “augmentation-free baseline”.
- Las 109 imágenes de evaluación pueden describirse como la **versión revisada del split**; si se usa la expresión “semi-field only”, debe quedar claro que proviene del proceso de curación de los autores y no de metadata de dominio actualmente preservada.
- El entorno cloud completo debe atribuirse directamente a A0 seed01, salvo que aparezcan logs adicionales.
- No comparar métricas absolutas de A0/A1/A2 con v2 como si provinieran del mismo protocolo.

## 10. Estado final de la campaña

**A0/A1/A2 queda cerrada y congelada sobre validation.**

No se requieren nuevas recetas, nuevas corridas ni apertura de test para cerrar estos tres escenarios. Las incertidumbres restantes quedan registradas como limitaciones documentales y no deben resolverse mediante ajuste retrospectivo del experimento.

**Selección/promoción:** ninguna.  
**Winner:** ninguno.  
**Test consultado para este cierre:** no.  
**Resultado científico principal:** A1 y A2 muestran una mejora reproducible de mAP frente a A0; la evidencia operacional y por dificultad es favorable en promedio pero más variable; A1 y A2 no muestran separación suficiente para atribuir un beneficio adicional claro a HSV + Mosaic sobre la geometría.
