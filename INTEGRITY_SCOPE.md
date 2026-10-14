# Alcance de los manifiestos de integridad

Fecha de revisión: 2026-10-14. Base inspeccionada: `715265ec848be0e1b4e8b2d4398dfa530cf8921e`.

## Manifiesto histórico: SHA256SUMS.txt

Se conserva **byte a byte**, igual que RELEASE_AUDIT.md, MISSING_FILES.md,
provenance/LICENSING_REVIEW.md y los manifiestos reconstruidos de preparación.
Sus 146 entradas describen los archivos del candidato original; el propio
SHA256SUMS.txt y los dos controles Git añadidos después no estaban en su alcance.
Al iniciar esta revisión, las 146 entradas coincidían con el snapshot de main.

Solo README.md cambia entre los 149 archivos preexistentes. Por tanto, aplicar
el manifiesto histórico directamente al árbol revisado da una divergencia
**esperada y explícita** en README.md; no indica alteración de resultados.
La entrada histórica README.md corresponde ahora a la copia byte-idéntica
`provenance/review/historical/README_candidate_2026-10-14.md`, con SHA-256
`374af967e9c1e550b24a43f2e143ef2666ef5e23a39797d631fd4986cc8277bd`. Las otras 145 entradas siguen coincidiendo con las rutas
actuales sin remapeo. Los 148 archivos preexistentes distintos de README.md
conservan sus hashes originales, incluidos scripts, configuraciones y resultados.

No se han actualizado los hashes históricos para fingir que el README no cambió.
El inventario y la tabla de auditoría históricos también mantienen su contexto:
sus referencias al hash del README deben leerse contra la copia archivada.

## Manifiesto actual: SHA256SUMS_REVIEW.txt

Describe los bytes de este árbol propuesto de revisión documental. Incluye el
README actualizado, los documentos históricos preservados, .gitignore,
.gitattributes, la copia del README antiguo, reportes y manifiestos derivados.
Solo se excluye a sí mismo para evitar autorreferencia; no incluye .git ni los
artefactos locales temporales de ejecución. El commit del PR fijará su snapshot;
los reportes nombran el commit científico evaluado, no su propio commit futuro.

Los manifiestos derivados bajo provenance/review distinguen entradas usadas por
la prueba y salidas producidas fuera del repositorio. Las salidas no sustituyen
CSV/JSON históricos y no se copiaron como resultados oficiales al PR.
El README histórico archivado es documentación original; los logs y reportes
de revisión son evidencia posterior claramente separada.

## Comprobación y límites

Se verifican todos los hashes históricos remapeando únicamente README.md a su
copia archivada; se verifica el nuevo manifiesto sobre todas sus rutas actuales.
La comprobación de hashes prueba identidad de bytes, no corrección científica,
autoría, licencia, identidad del dataset remoto ni entornos históricos completos.
Git mantiene la política * -text y core.autocrlf=false para evitar conversiones.
