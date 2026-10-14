# A0/A1/A2 RGB calyx detection — code release candidate

This is a **human-review candidate, not a published or fully reproducible release**.
It preserves recovered code and frozen evidence for RGB detection of the calyx of
*Physalis peruviana* L. using YOLO11n. No training, inference, metric replacement,
test access, package installation or external publication was performed during preparation.

## Experiment and scope

The closed campaign comprises A0, A1 and A2, five paired seeds (1–5), fifteen formal
runs and fifty epochs per run. Five-epoch smoke runs are excluded. A0 sets the
campaign-targeted configurable augmentation coefficients to zero; it is not an
absolutely augmentation-free baseline. The final closure records an internal
Albumentations block observed in A0 seed01. Equivalent A1/A2 console evidence is absent.
A1 uses native geometry, HSV and Mosaic. A2 uses translate=0.1, scale=0.5 and
fliplr=0.5 without HSV or Mosaic. A1−A2 assesses their **joint addition**, not their
individual effects. No recipe, seed, threshold or frozen conclusion was changed.
Common training settings include imgsz=640, batch=8, AdamW, lr0=0.001, lrf=0.01,
workers=8, deterministic=true and AMP=false. A1 closes Mosaic for the last ten
epochs; A0/A2 have close_mosaic=0. See the original final lock for the complete design.

## Organization and evidence classes

- `training/`: recovery status; no invented historical training script.
- `configs/documentary_redacted/`: fifteen original effective configuration exports
  with private Platform identifiers/locations replaced; original string types retained.
- `configs/extracted_redacted/`: fifteen typed train_args extracts from checkpoint
  metadata using an inert opcode interpreter; private fields replaced.
- `configs/documentary_reconstructed/`: labelled design extract and local validation template.
- `evaluation/original/`, `operational_metrics/original/`, `difficulty_analysis/original/`:
  byte-preserved recovered experiment scripts.
- `statistics/original/scripts/`: recovered later mAP paired-figure analysis.
- `results/`: locked global, operational and difficulty tables, thresholds, cached
  model predictions and CSV sweeps. Absolute operational checkpoint paths are redacted;
  numeric observations and selections are unchanged. Fifteen original final-epoch training
  metric exports are separate from homogeneous evaluation; they are not substituted for it.
  Later figure data are separate.
- `provenance/`: original closure/lock, archive inventories, integrity evidence,
  excluded-weight hashes, redactions, software evidence and licensing review.
- `RELEASE_AUDIT.md`, `MISSING_FILES.md`, `SHA256SUMS.txt`: audit, gaps and integrity.

ORIGINAL means byte-preserved local source; EXTRAÍDO DE ARCHIVO means bytes checked
against a locked historical archive. RECONSTRUIDO includes new documentation,
inert metadata extracts and privacy-redacted derivatives, not fabricated historical code.
Original-source paths use aliases to avoid disclosing private roots; an absolute-path
inventory is retained locally outside this package. All four historical ZIPs contain
results/configuration exports and checkpoints where applicable, **no Python/notebook source**.

## Software evidence and environment preparation

All fifteen formal checkpoints were hash-checked and inert metadata confirms
Ultralytics 8.4.157. The full cloud stack is documented directly for A0 seed01 only:
Python 3.12.3, PyTorch 2.14.0+cu132 and the GPU recorded in the final lock. The original
raw console log was not independently recovered here. This is not proof of a common
Python/PyTorch/CUDA environment across all fifteen runs.

Archived homogeneous evaluation reports Python 3.14.7, Ultralytics 8.4.157 and
PyTorch 2.14.0+cpu. These are historical self-reports, supported by recovered local
evaluation-venv package metadata, not a runtime certification in this preparation.
The current audit interpreter is distinct. `provenance/reconstructed/software_evidence.json`
separates these sources. A complete historical dependency lock is unavailable.
The optional Albumentations version cannot be inferred from checkpoint version strings.

`requirements.txt` lists direct imports justified by recovered code. Only the
documented Ultralytics version is pinned; this is not a historical environment lock.
For a future, explicitly approved replication, create an isolated environment and
resolve compatible dependencies after reviewing versions and upstream licenses:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

These commands were **not run**. Successful installation and compatibility must be
verified separately; no bitwise historical training equivalence is claimed.

## Dataset preparation

Dataset DOI supplied by the authors: https://doi.org/10.6084/m9.figshare.34476066
Download the dataset separately under its own terms. No images or ground-truth
annotations are redistributed. The DOI landing page could not be retrieved by the
browser used in preparation; remote availability, version and split correspondence
were not independently verified. No remote dataset files were downloaded.

The campaign expects 1062 training images/2882 objects and 109 validation images/312
objects, with class 0 named `calyx`. Counts alone do not establish dataset identity.
Use the frozen `results/operational_results/validation_manifest.csv` for validation
file hashes and the fingerprint recorded in the final lock. Obtain any required
version/curation provenance from the authors. Leave test frozen and inaccessible.
No test entry is supplied in the validation template.

The recovered original local data.yaml pointed **train, val and test at images/val**
and used an absolute local path. It was an evaluation-only convenience and is excluded;
it must never be used for training. The labelled validation template replaces it
without asserting that the replacement is historical evidence.

## Execution layout for future approved replication

The original scripts retain their path assumptions. Do not execute them in the
source result directories or directly in this candidate. Prepare a new disposable
workspace, outside original data/results, and stage the files as follows:

```text
replication_workspace/
  validate_all.py
  operational_recall.py
  integral_difficulty.py
  scripts/plot_a0_a1_a2_paired_map_deltas.py
  data.yaml
  dataset/images/val/        # separately obtained, verified validation only
  dataset/labels/val/        # separately obtained, verified validation only
  weights/A0_seed01_best.pt  # all 15 external formal weights, hashes verified
  validation_results/       # copy package results/validation_results for statistics
  operational_results/      # copy package results/operational_results for difficulty
  integral_results/         # copy package results/integral_results for auditing
```

Copy each original script from its labelled folder into this layout; place the
statistics script under `scripts/`. Configure `data.yaml` from the validation-only
template with an absolute local dataset root. The weights manifest records names
and hashes; weights are not distributed and no verified public download is available.
Do not execute inference without these external inputs and appropriate authorization.
Every original evaluator writes outputs; use a fresh workspace for each replication
and preserve the packaged historical results as immutable reference evidence.

## Training

The original Platform training launcher was not recovered. Historical effective
exports, seed/determinism values, pretrained=true and model-family references are
available for documentary reconstruction, but original initial pretrained bytes,
complete per-run environments and historical input/sampling state are missing.
Consequently this candidate does not offer a verified end-to-end training command.
Do not treat redacted exports or checkpoint train_args as portable executable recipes.

## Homogeneous global evaluation

With independently obtained, hash-verified formal weights and the correct validation
dataset in a fresh staged workspace, the recovered entrypoint is:

```powershell
python -B validate_all.py
```

It evaluates all fifteen models on `val` with imgsz=640, batch=8, workers=0, CPU,
conf=0.001, NMS IoU=0.7, max_det=300, rect=true and augment=false. It records
mAP50–95, mAP50, mAP75, global Precision and Recall, per-run checkpoint hashes,
and condition means/sample SD. Global Precision/Recall are distinct from the
precision-constrained operational metric. This entrypoint executes at import time
and uses exist_ok=true; do not import it for tests or point it at closed results.

## Operational metric

The original entrypoint, subject to the same external-input requirements, is:

```powershell
python -B operational_recall.py
```

Low-confidence predictions use conf=0.001, NMS IoU=0.70, max_det=300, imgsz=640,
CPU and augment=false on validation only. Predictions are sorted by decreasing
confidence (stable image/prediction ordering for ties) and grouped at identical
confidence values. Greedy matching assigns a detection to the best unmatched
same-class GT in the same image when IoU ≥ 0.50. Each GT is matched once.
TP/FP are cumulative; FN=GT−TP, Precision=TP/(TP+FP), Recall=TP/GT, and
F1=2PR/(P+R), with the source's zero-denominator conventions retained.
The initial no-detection point has Precision=1 and Recall=0.

For each run independently, select `maximum_recall_subject_to_precision_ge_0.98`
on **validation exclusively**. Ties prefer higher precision, then higher confidence.
Frozen selected points and CSV sweeps are included. Do not adjust their thresholds.
The source retains `provisional_unverified_against_classical_augmentation_v2`:
IoU=0.50 is frozen for A0/A1/A2; equivalence to the separate historical v2 code is
not asserted. Old source comments suggesting changing the constant are historical
comments and do not authorize changes to the closed campaign.

## Difficulty analysis

In a separately approved staged workspace with validation GT and cached predictions:

```powershell
python -B integral_difficulty.py
```

No inference is required by this script. It reuses each run's selected threshold,
checks TP/FP/FN against the frozen point, and calculates stratum recall. Definitions
agree with the final lock and closure, and are **not generic COCO size bins**:

- small: normalized bounding-box area < 0.02423;
- medium: 0.02423 ≤ area < 0.05196;
- large: area ≥ 0.05196;
- clustered: overlaps another GT in the same image at IoU ≥ 0.05;
- border contact: min(x1/W, y1/H, 1−x2/W, 1−y2/H) ≤ 0.01.

The recorded validation composition is 101 small, 115 medium, 96 large,
19 clustered and 61 border-contact instances. Thresholds are retained from the
documented protocol; train-tercile derivation source was not independently recovered.
GT per-instance manifests are omitted because they reproduce annotations.

## Statistical analysis

Condition summaries and paired A1−A0, A2−A0 and A1−A2 tables are included.
The integral script uses sample SD (ddof=1) and pairs by seed. Its historical v2
sensitivity flags are descriptive only, not predeclared acceptance criteria here.
The recovered **later** analysis can regenerate paired mAP figure statistics from
the fifteen saved validation summaries, without dataset or model weights:

```powershell
python -B scripts/plot_a0_a1_a2_paired_map_deltas.py
```

Run only in the staged disposable workspace. This later script uses Student-t
95% intervals, df=4: mean_delta ± t(0.975,4) × SD_delta/sqrt(5), and verifies rounded
closure controls. The original full script generating all closure CIs and exact
Wilcoxon p-values was not recovered. Those values remain documentary evidence in
the original final lock; no replacement statistical implementation is represented
as historical code and no closed metrics were recomputed during preparation.

## Integrity, limits and publication review

All four archive SHA-256 hashes agree with the final lock, ZIP CRC checks pass,
and fifteen unique formal weights agree with reference hashes and local evaluation
copies. Source code was AST-parsed; JSON/YAML and copied/extracted bytes were
validated. No experiment module or unit test was executed. No dedicated safe
experiment unit tests were found. `SHA256SUMS.txt` covers all package files except
itself (avoiding self-reference); the outer ZIP digest is supplied separately.

Audit-only: historical training, complete cloud-runtime identity, original console
provenance and full closure statistical implementation. Conditionally executable:
validation/operational evaluation with external verified dataset and weights;
difficulty with external validation GT and included predictions; later paired mAP
analysis with included summaries and compatible scientific dependencies. Execution
was not runtime-tested in this preparation. This is not a fully reproducible release.

Confirm external-script authorship and redistribution rights before publication;
no blanket MIT license is assigned to recovered external work. Review upstream
dependency terms. Private identifiers and locations have been removed from exported
configs/results; originals are retained locally with hashes. Read RELEASE_AUDIT.md
and MISSING_FILES.md before approving any GitHub or DOI deposit.

## Proposed Code Availability statement (current, unpublished state)

“A review candidate containing the recovered A0/A1/A2 validation, operational-metric,
difficulty-analysis and later paired mAP analysis code, together with frozen result
tables and provenance records, has been prepared but has not yet been publicly
deposited. The dataset is referenced separately by DOI 10.6084/m9.figshare.34476066.
The candidate excludes images, ground-truth annotations and model checkpoints.
The original training launcher, complete per-run training environments and the full
statistical closure implementation were not recovered; therefore, complete end-to-end
reproducibility is not claimed.”
