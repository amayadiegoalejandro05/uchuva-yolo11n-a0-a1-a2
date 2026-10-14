# Verificación del análisis posterior emparejado de mAP50–95

Fecha: **2026-10-14**, America/Bogota.
Commit evaluado: `715265ec848be0e1b4e8b2d4398dfa530cf8921e`.
Resultado: **PASS del análisis posterior de mAP; no reproducción del entrenamiento**.

## Entorno observado y aislamiento

- Sistema operativo: `Windows-10-10.0.19045-SP0` (cadena observada).
- Python: `3.12.3`; build `3.12.3 (tags/v3.12.3:f6650f9, Apr  9 2024, 14:05:25) [MSC v.1938 64 bit (AMD64)]`.
- NumPy: `1.26.4`.
- SciPy: `1.17.1`.
- Matplotlib: `3.10.8`.

Se usaron dependencias ya instaladas; no se instaló ni descargó ningún componente.
El script fue inspeccionado completamente antes de ejecutarlo. Sus imports son
stdlib, NumPy, SciPy y Matplotlib; no importa YOLO/PyTorch ni abre datos de imágenes.
Se copió byte a byte a un directorio temporal del sistema fuera de este checkout,
denominado aquí `VERIFICATION_WORKSPACE` para no divulgar rutas privadas. También
se copiaron únicamente los quince JSON de entrada. MPLCONFIGDIR se dirigió al
temporal; se usó -B y salida UTF-8. El hash del script antes/después fue
`91d27b73866bbdd09b30a95e68f08bcf29c3180680237f0667f81cb551189df2`. El archivo original no se modificó.

Comando, ejecutado desde ese temporal usando el intérprete Python observado:

```text
python -B scripts/plot_a0_a1_a2_paired_map_deltas.py
```

`PYTHONUTF8=1` y `PYTHONIOENCODING=utf-8` evitaron conversiones de consola; no
modifican las recetas ni el código original. Exit code: `0`.

## Entradas y CSV relacionados

El script consume **JSON, no CSV**. Sus quince entradas fueron:

- `results/validation_results/A0_seed01/metrics_summary.json`
- `results/validation_results/A0_seed02/metrics_summary.json`
- `results/validation_results/A0_seed03/metrics_summary.json`
- `results/validation_results/A0_seed04/metrics_summary.json`
- `results/validation_results/A0_seed05/metrics_summary.json`
- `results/validation_results/A1_seed01/metrics_summary.json`
- `results/validation_results/A1_seed02/metrics_summary.json`
- `results/validation_results/A1_seed03/metrics_summary.json`
- `results/validation_results/A1_seed04/metrics_summary.json`
- `results/validation_results/A1_seed05/metrics_summary.json`
- `results/validation_results/A2_seed01/metrics_summary.json`
- `results/validation_results/A2_seed02/metrics_summary.json`
- `results/validation_results/A2_seed03/metrics_summary.json`
- `results/validation_results/A2_seed04/metrics_summary.json`
- `results/validation_results/A2_seed05/metrics_summary.json`

Se conservaron los seeds emparejados 1–5 y el campo mAP50_95 original. Los siguientes
CSV disponibles se localizaron y usaron como cross-check numérico independiente
del output, no se suministraron como entradas al script:

- `results/validation_results/all_validation_results.csv`
- `results/integral_results/paired_deltas_by_seed.csv`
- `results/later_analysis/a0_a1_a2_paired_map_deltas_data.csv`

El cierre usado como referencia es
`provenance/original/A0_A1_A2_campaign_final_lock.json`, sección
results.paired.<contrast>.mAP50_95. Los hashes de script, inputs, CSV acompañantes
y cierre constan en `provenance/review/STATISTICAL_INPUT_SHA256SUMS.txt`.

## Resultados y diferencia frente al cierre

| Contraste | Media observada | IC95% t observado | Seeds positivos | Δ media frente al lock | Δ extremos IC frente al lock |
|---|---:|---|---:|---:|---|
| A1-A0 | +0.071849388 | [0.055058929121, 0.088639847790] | 5/5 | -4.555e-10 | [-1.914e-13, +2.554e-13] |
| A2-A0 | +0.068954608 | [0.051323904122, 0.086585311079] | 5/5 | +3.994e-10 | [+1.307e-13, -2.854e-13] |
| A1-A2 | +0.002894781 | [-0.001719601133, 0.007509162843] | 3/5 | +1.451e-10 | [+2.321e-13, -1.339e-14] |

Las medias se leen del stdout impreso a nueve decimales; los IC están impresos a
doce decimales. Las diferencias residuales mostradas son consistentes con ese
redondeo, no evidencia de cambios en resultados históricos.

El propio script calcula SD muestral (`ddof=1`) de cinco diferencias emparejadas e
IC95% **Student-t**: media_delta ± t.ppf(0.975, df=4) × SD_delta / sqrt(5).
El intervalo describe incertidumbre de la diferencia media bajo ese método y sus
supuestos; no equivale a una prueba formal de significación ejecutada aquí.
No se ejecutó Wilcoxon ni se verificó su implementación histórica ausente.
El IC A1−A2 incluye cero; no identifica efectos separados de HSV y Mosaic.

## Criterios PASS y comprobaciones efectivamente ejecutadas

1. Script intacto, ejecución exitosa y `CONSISTENCY CONTROLS: PASS`.
2. Medias y extremos de IC concuerdan con el lock dentro de **5.1×10⁻⁷**, la
   tolerancia del control del script para referencias a seis decimales.
3. Seeds positivos: 5/5, 5/5 y 3/5, iguales al cierre.
4. El CSV generado contiene exactamente cinco seeds; valores por condición coinciden
   con all_validation_results.csv. Sus diferencias y datos de figura concuerdan con
   paired_deltas_by_seed.csv y el CSV histórico posterior dentro de **10⁻¹⁴**.
5. Los 149 archivos preexistentes conservaban sus hashes al terminar la ejecución;
   el checkout permaneció limpio. El script no escribió resultados en el repositorio.

## Salidas generadas fuera del repositorio

| Ruta relativa a VERIFICATION_WORKSPACE | Bytes | SHA-256 de esta ejecución |
|---|---:|---|
| figures/a0_a1_a2_paired_map_deltas.pdf | 10385 | b31609f58265f37e386e27bd2d6541b2c3977fa597d3c786883847340cfa234d |
| figures/a0_a1_a2_paired_map_deltas.png | 78159 | b9bbcda1a355d87e24b82bfe890054cd4de4598cc4d107945ee78318b5e5f43b |
| figures/a0_a1_a2_paired_map_deltas.svg | 13318 | c0f649d5fbde1fb0431458e81d279465d8a2eb8e12ea8f7c1dc90a118ba15ceb |
| figures/a0_a1_a2_paired_map_deltas_data.csv | 684 | ead4c8559b4bfc04083d140ed47605c594c3fe6ade39cf758b98ae9403fb927b |

PDF/PNG/SVG son figuras estadísticas, no fotografías del dataset. Las cuatro
salidas se retienen en el temporal local para revisión, no se agregan al PR como
nuevos resultados oficiales. El CSV histórico en results permanece intacto.
Sus hashes se documentan en STATISTICAL_OUTPUT_SHA256SUMS.txt; no se promete igualdad
binaria entre futuras figuras, pues metadata de tiempo/identificadores puede variar.
La ruta absoluta local se conserva únicamente en el registro local fuera del repositorio.

`provenance/review/statistical_verification_stdout.txt` conserva stdout con las
rutas del temporal reemplazadas por su alias y finales de línea normalizados a LF;
los valores numéricos no se editaron.
`statistical_verification_stderr.txt` conserva stderr igualmente depurado (vacío
si no hubo mensajes). Son evidencia posterior, no logs históricos de entrenamiento.

## Limitaciones

Esta prueba no verifica datos originales, matching operacional, recalls por
dificultad, inferencia, entrenamiento, GPU/CUDA, entornos históricos ni generalización.
No se cargaron modelos, imágenes, anotaciones o test. No se sustituyó ninguna métrica
oficial ni se ejecutó ningún otro evaluador. El PASS se limita al código posterior
recuperado de análisis emparejado mAP y a sus entradas existentes.
