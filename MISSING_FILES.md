# Componentes faltantes o no verificables

Este paquete no es una reproducción completa del entrenamiento ni una publicación aprobada. NO ENCONTRADO significa no recuperado en el alcance inspeccionado, no inexistencia universal.

- **Original training launcher / Platform submission code** — Effective exports and checkpoint train_args recovered; no historical Python/notebook launcher found.
- **Original per-run args.yaml** — No formal A0/A1/A2 args.yaml found. JSON exports and typed checkpoint train_args are available.
- **Historical pretraining checkpoint identity / hash** — YOLO11n and pretrained=true are recorded; exact initial pretrained bytes are not available as verified campaign provenance.
- **Complete cloud dependency lock / container per run** — Full stack documented in final closure for A0 seed01 only; no uniform 15-run environment evidence.
- **Original A0 seed01 raw console log** — Console excerpt and stack are preserved in final closure/lock, not an independently recovered raw console file.
- **A1/A2 raw console logs / optional Albumentations versions** — No corresponding direct console evidence or historical optional package lock.
- **Original full statistical closure script (CI and exact Wilcoxon across all metrics)** — Descriptive paired analysis recovered; later mAP Student-t script recovered. Full CI/p-value code underlying final lock not found.
- **Machine-readable domain curation / original Hub per-image manifest** — Semi-field curation is documented but not independently encoded in recovered domain metadata.
- **Public access mechanism / license for 15 formal weights** — Weights present locally and hash-verified; intentionally excluded from release, no verified public retrieval URL.
- **Dataset version-to-campaign identity from DOI** — User-supplied DOI retained. DOI browser lookup failed; no remote files downloaded or split equivalence asserted.
- **License and authorship for external experiment scripts** — External working directory scripts have no explicit license headers. Root MIT applies to original repository authorship, not automatically to external work.

Exclusiones deliberadas: RGB y anotaciones GT (incluido gt_difficulty_manifest.csv), pesos .pt, cachés, resultados visuales con fotografías, JSON redundantes de sweeps, SMOKE, Classical Augmentation v2, pilotos, Blender y correcciones EXIF posteriores. Las predicciones de modelo incluidas no son anotaciones GT.
