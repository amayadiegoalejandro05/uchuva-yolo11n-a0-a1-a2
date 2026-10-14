from pathlib import Path
import hashlib
import json
import platform

import pandas as pd
import torch
import ultralytics
from ultralytics import YOLO


# ============================================================
# STANDARDIZED LOCAL VALIDATION — A0 / A1 / A2
# ============================================================

DATA_YAML = "data.yaml"
WEIGHTS_DIR = Path("weights")
OUTPUT_DIR = Path("validation_results")

IMGSZ = 640
BATCH = 8
DEVICE = "cpu"
WORKERS = 0

CONF = 0.001
IOU = 0.7
MAX_DET = 300
RECT = True


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Save evaluation environment
# ------------------------------------------------------------

environment = {
    "python": platform.python_version(),
    "ultralytics": ultralytics.__version__,
    "torch": torch.__version__,
    "device": DEVICE,
    "cpu": platform.processor(),
    "imgsz": IMGSZ,
    "batch": BATCH,
    "workers": WORKERS,
    "conf": CONF,
    "iou": IOU,
    "max_det": MAX_DET,
    "rect": RECT,
    "split": "val",
    "augment": False,
}

with open(
    OUTPUT_DIR / "evaluation_environment.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(environment, f, indent=2)


rows = []

for condition in ["A0", "A1", "A2"]:
    for seed in range(1, 6):

        run_name = f"{condition}_seed{seed:02d}"
        weight_path = WEIGHTS_DIR / f"{run_name}_best.pt"

        if not weight_path.exists():
            raise FileNotFoundError(
                f"No se encontró: {weight_path}"
            )

        print("\n" + "=" * 72)
        print(f"VALIDATING: {run_name}")
        print(f"WEIGHTS: {weight_path}")
        print("=" * 72)

        model = YOLO(str(weight_path))

        metrics = model.val(
            data=DATA_YAML,
            split="val",

            imgsz=IMGSZ,
            batch=BATCH,

            device=DEVICE,
            workers=WORKERS,

            conf=CONF,
            iou=IOU,
            max_det=MAX_DET,

            rect=RECT,
            augment=False,

            plots=True,

            project=str(OUTPUT_DIR),
            name=run_name,
            exist_ok=True,
        )

        row = {
            "condition": condition,
            "seed": seed,
            "run": run_name,

            "checkpoint": str(weight_path),
            "checkpoint_sha256": sha256_file(weight_path),

            "images": 109,
            "instances": 312,

            "mAP50_95": float(metrics.box.map),
            "mAP50": float(metrics.box.map50),
            "mAP75": float(metrics.box.map75),

            "precision": float(metrics.box.mp),
            "recall": float(metrics.box.mr),
        }

        rows.append(row)

        run_dir = OUTPUT_DIR / run_name
        run_dir.mkdir(parents=True, exist_ok=True)

        with open(
            run_dir / "metrics_summary.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(row, f, indent=2)


# ============================================================
# MASTER RESULTS
# ============================================================

df = pd.DataFrame(rows)

df.to_csv(
    OUTPUT_DIR / "all_validation_results.csv",
    index=False
)

with open(
    OUTPUT_DIR / "all_validation_results.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(rows, f, indent=2)


# ============================================================
# CONDITION SUMMARY
# ============================================================

summary = (
    df.groupby("condition")
    .agg({
        "mAP50_95": ["mean", "std"],
        "mAP50": ["mean", "std"],
        "mAP75": ["mean", "std"],
        "precision": ["mean", "std"],
        "recall": ["mean", "std"],
    })
)

summary.to_csv(
    OUTPUT_DIR / "condition_summary.csv"
)

print("\n")
print("=" * 72)
print("FINAL STANDARDIZED VALIDATION TABLE")
print("=" * 72)
print(df.to_string(index=False))

print("\n")
print("=" * 72)
print("CONDITION SUMMARY")
print("=" * 72)
print(summary)