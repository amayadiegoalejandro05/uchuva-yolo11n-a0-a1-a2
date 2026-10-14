from pathlib import Path
import hashlib
import json
import platform

import numpy as np
import pandas as pd
from PIL import Image

import torch
import ultralytics
from ultralytics import YOLO


# ============================================================
# OPERATIONAL RECALL ANALYSIS
# Maximum Recall subject to Precision >= 0.98
#
# A0 / A1 / A2
# 5 paired seeds
# Validation only
# ============================================================


ROOT = Path(__file__).resolve().parent

VAL_IMAGES = ROOT / "dataset" / "images" / "val"
VAL_LABELS = ROOT / "dataset" / "labels" / "val"

WEIGHTS_DIR = ROOT / "weights"
OUTPUT_DIR = ROOT / "operational_results"


# ============================================================
# FIXED EVALUATION PARAMETERS
# ============================================================

IMGSZ = 640
DEVICE = "cpu"

# Keep low confidence so predictions are not discarded before
# the operational confidence sweep.
PRED_CONF = 0.001

# NMS IoU used during prediction
NMS_IOU = 0.70

MAX_DET = 300

# ------------------------------------------------------------
# IMPORTANT:
# This 0.50 detection matching IoU is currently PROVISIONAL.
# We have NOT yet verified from the historical v2 analysis code
# that this was exactly the TP/FP matching criterion used there.
#
# If the historical repository confirms another value,
# change ONLY this constant and rerun the complete script.
# ------------------------------------------------------------
MATCH_IOU = 0.50
MATCH_IOU_STATUS = "provisional_unverified_against_classical_augmentation_v2"

PRECISION_TARGET = 0.98


# Integrity checks for the current semi-field validation split
EXPECTED_IMAGES = 109
EXPECTED_INSTANCES = 312


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


# ============================================================
# UTILITIES
# ============================================================

def sha256_file(path: Path) -> str:
    """Return SHA-256 hash of a file."""
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def load_yolo_labels(label_path: Path, image_width: int, image_height: int):
    """
    Read YOLO detection labels:
        class x_center y_center width height

    Returns a list of dictionaries with xyxy coordinates
    in original image pixels.
    """

    objects = []

    if not label_path.exists():
        return objects

    text = label_path.read_text(encoding="utf-8").strip()

    if not text:
        return objects

    for line_number, line in enumerate(text.splitlines(), start=1):
        parts = line.strip().split()

        if len(parts) < 5:
            raise ValueError(
                f"Invalid YOLO label in {label_path}, line {line_number}: "
                f"{line}"
            )

        cls_id = int(float(parts[0]))
        xc = float(parts[1])
        yc = float(parts[2])
        bw = float(parts[3])
        bh = float(parts[4])

        x1 = (xc - bw / 2.0) * image_width
        y1 = (yc - bh / 2.0) * image_height
        x2 = (xc + bw / 2.0) * image_width
        y2 = (yc + bh / 2.0) * image_height

        objects.append(
            {
                "class_id": cls_id,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
            }
        )

    return objects


def box_iou_one_to_many(box, boxes):
    """
    IoU between one xyxy box and N xyxy boxes.
    """

    if len(boxes) == 0:
        return np.array([], dtype=np.float64)

    box = np.asarray(box, dtype=np.float64)
    boxes = np.asarray(boxes, dtype=np.float64)

    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])

    inter_w = np.maximum(0.0, x2 - x1)
    inter_h = np.maximum(0.0, y2 - y1)

    intersection = inter_w * inter_h

    box_area = max(0.0, box[2] - box[0]) * max(
        0.0, box[3] - box[1]
    )

    boxes_area = (
        np.maximum(0.0, boxes[:, 2] - boxes[:, 0])
        * np.maximum(0.0, boxes[:, 3] - boxes[:, 1])
    )

    union = box_area + boxes_area - intersection

    iou = np.divide(
        intersection,
        union,
        out=np.zeros_like(intersection),
        where=union > 0,
    )

    return iou


def f1_score(precision, recall):
    denominator = precision + recall

    if denominator == 0:
        return 0.0

    return 2.0 * precision * recall / denominator


# ============================================================
# DATASET MANIFEST
# ============================================================

def build_validation_manifest():
    """
    Creates a reproducible manifest of the validation split
    and loads all ground-truth boxes.
    """

    if not VAL_IMAGES.exists():
        raise FileNotFoundError(
            f"Validation images folder not found: {VAL_IMAGES}"
        )

    if not VAL_LABELS.exists():
        raise FileNotFoundError(
            f"Validation labels folder not found: {VAL_LABELS}"
        )

    image_paths = sorted(
        p
        for p in VAL_IMAGES.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

    gt_by_image = {}
    manifest_rows = []

    total_instances = 0

    print("\nBuilding validation manifest...")

    for image_path in image_paths:

        label_path = VAL_LABELS / f"{image_path.stem}.txt"

        if not label_path.exists():
            raise FileNotFoundError(
                f"Missing label for image: {image_path.name}"
            )

        with Image.open(image_path) as img:
            width, height = img.size

        objects = load_yolo_labels(
            label_path,
            width,
            height,
        )

        total_instances += len(objects)

        gt_by_image[image_path.stem] = objects

        manifest_rows.append(
            {
                "image": image_path.name,
                "image_width": width,
                "image_height": height,
                "image_sha256": sha256_file(image_path),
                "label": label_path.name,
                "label_sha256": sha256_file(label_path),
                "gt_instances": len(objects),
            }
        )

    image_count = len(image_paths)

    print(f"Validation images: {image_count}")
    print(f"Validation instances: {total_instances}")

    if image_count != EXPECTED_IMAGES:
        raise RuntimeError(
            f"Expected {EXPECTED_IMAGES} validation images, "
            f"but found {image_count}."
        )

    if total_instances != EXPECTED_INSTANCES:
        raise RuntimeError(
            f"Expected {EXPECTED_INSTANCES} validation instances, "
            f"but found {total_instances}."
        )

    manifest_df = pd.DataFrame(manifest_rows)

    # Dataset-level fingerprint
    fingerprint_hasher = hashlib.sha256()

    for row in manifest_rows:
        fingerprint_hasher.update(row["image"].encode("utf-8"))
        fingerprint_hasher.update(row["image_sha256"].encode("utf-8"))
        fingerprint_hasher.update(row["label"].encode("utf-8"))
        fingerprint_hasher.update(row["label_sha256"].encode("utf-8"))

    validation_fingerprint = fingerprint_hasher.hexdigest()

    return (
        image_paths,
        gt_by_image,
        manifest_df,
        validation_fingerprint,
        total_instances,
    )


# ============================================================
# PREDICTION EXTRACTION
# ============================================================

def collect_predictions(model, image_paths):
    """
    Run low-confidence inference and return all post-NMS
    predictions in one DataFrame.
    """

    rows = []

    sources = [str(p) for p in image_paths]

    results = model.predict(
        source=sources,
        imgsz=IMGSZ,
        conf=PRED_CONF,
        iou=NMS_IOU,
        max_det=MAX_DET,
        device=DEVICE,
        augment=False,
        verbose=False,
        stream=True,
    )

    for result in results:

        image_path = Path(result.path)
        image_stem = image_path.stem

        boxes = result.boxes

        if boxes is None or len(boxes) == 0:
            continue

        xyxy = boxes.xyxy.cpu().numpy()
        confidences = boxes.conf.cpu().numpy()
        classes = boxes.cls.cpu().numpy().astype(int)

        for pred_index, (
            box,
            confidence,
            class_id,
        ) in enumerate(zip(xyxy, confidences, classes)):

            rows.append(
                {
                    "image": image_path.name,
                    "image_stem": image_stem,
                    "pred_index": pred_index,
                    "class_id": int(class_id),
                    "confidence": float(confidence),
                    "x1": float(box[0]),
                    "y1": float(box[1]),
                    "x2": float(box[2]),
                    "y2": float(box[3]),
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "image",
                "image_stem",
                "pred_index",
                "class_id",
                "confidence",
                "x1",
                "y1",
                "x2",
                "y2",
            ]
        )

    df = pd.DataFrame(rows)

    # Deterministic ordering
    df = df.sort_values(
        by=[
            "confidence",
            "image_stem",
            "pred_index",
        ],
        ascending=[
            False,
            True,
            True,
        ],
        kind="mergesort",
    ).reset_index(drop=True)

    return df


# ============================================================
# CONFIDENCE SWEEP
# ============================================================

def build_confidence_sweep(pred_df, gt_by_image, total_gt):
    """
    Greedy confidence-ordered matching.

    A prediction is TP when:
      - class matches
      - its best currently-unmatched GT in the same image
        has IoU >= MATCH_IOU

    Otherwise it is FP.

    GT objects can be matched only once.
    """

    matched_gt = {
        image_stem: set()
        for image_stem in gt_by_image.keys()
    }

    records = []

    cumulative_tp = 0
    cumulative_fp = 0

    # Initial no-detection operating point
    records.append(
        {
            "confidence": 1.0,
            "tp": 0,
            "fp": 0,
            "fn": total_gt,
            "precision": 1.0,
            "recall": 0.0,
            "f1": 0.0,
        }
    )

    if pred_df.empty:
        return pd.DataFrame(records)

    # Process predictions grouped by identical confidence.
    # This guarantees each saved row corresponds to an actual
    # confidence threshold that includes all detections with
    # confidence >= threshold.
    grouped = pred_df.groupby(
        "confidence",
        sort=False,
    )

    for confidence, group in grouped:

        for _, pred in group.iterrows():

            image_stem = pred["image_stem"]
            pred_class = int(pred["class_id"])

            gt_objects = gt_by_image.get(
                image_stem,
                [],
            )

            unmatched_indices = [
                idx
                for idx, gt in enumerate(gt_objects)
                if idx not in matched_gt[image_stem]
                and int(gt["class_id"]) == pred_class
            ]

            is_tp = False

            if unmatched_indices:

                candidate_boxes = np.array(
                    [
                        [
                            gt_objects[idx]["x1"],
                            gt_objects[idx]["y1"],
                            gt_objects[idx]["x2"],
                            gt_objects[idx]["y2"],
                        ]
                        for idx in unmatched_indices
                    ],
                    dtype=np.float64,
                )

                pred_box = np.array(
                    [
                        pred["x1"],
                        pred["y1"],
                        pred["x2"],
                        pred["y2"],
                    ],
                    dtype=np.float64,
                )

                ious = box_iou_one_to_many(
                    pred_box,
                    candidate_boxes,
                )

                best_local_index = int(np.argmax(ious))
                best_iou = float(ious[best_local_index])

                if best_iou >= MATCH_IOU:

                    matched_index = unmatched_indices[
                        best_local_index
                    ]

                    matched_gt[image_stem].add(
                        matched_index
                    )

                    is_tp = True

            if is_tp:
                cumulative_tp += 1
            else:
                cumulative_fp += 1

        fn = total_gt - cumulative_tp

        denominator = cumulative_tp + cumulative_fp

        if denominator > 0:
            precision = cumulative_tp / denominator
        else:
            precision = 1.0

        recall = cumulative_tp / total_gt

        f1 = f1_score(
            precision,
            recall,
        )

        records.append(
            {
                "confidence": float(confidence),
                "tp": int(cumulative_tp),
                "fp": int(cumulative_fp),
                "fn": int(fn),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
            }
        )

    return pd.DataFrame(records)


# ============================================================
# OPERATING POINT SELECTION
# ============================================================

def select_operating_point(sweep_df):
    """
    Selection rule:

    maximum recall subject to precision >= 0.98

    Deterministic tie-break:
      1. maximum recall
      2. maximum precision
      3. highest confidence threshold
    """

    eligible = sweep_df[
        sweep_df["precision"] >= PRECISION_TARGET
    ].copy()

    if eligible.empty:
        raise RuntimeError(
            "No operating point satisfies the required precision."
        )

    eligible = eligible.sort_values(
        by=[
            "recall",
            "precision",
            "confidence",
        ],
        ascending=[
            False,
            False,
            False,
        ],
        kind="mergesort",
    )

    best = eligible.iloc[0]

    return {
        "confidence": float(best["confidence"]),
        "precision": float(best["precision"]),
        "recall": float(best["recall"]),
        "f1": float(best["f1"]),
        "tp": int(best["tp"]),
        "fp": int(best["fp"]),
        "fn": int(best["fn"]),
        "selection_rule":
            "maximum_recall_subject_to_precision_ge_0.98",
        "precision_target": PRECISION_TARGET,
        "match_iou": MATCH_IOU,
        "match_iou_status": MATCH_IOU_STATUS,
        "prediction_confidence_floor": PRED_CONF,
        "nms_iou": NMS_IOU,
        "max_det": MAX_DET,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        image_paths,
        gt_by_image,
        manifest_df,
        validation_fingerprint,
        total_gt,
    ) = build_validation_manifest()

    manifest_df.to_csv(
        OUTPUT_DIR / "validation_manifest.csv",
        index=False,
    )

    environment = {
        "python": platform.python_version(),
        "ultralytics": ultralytics.__version__,
        "torch": torch.__version__,
        "device": DEVICE,
        "processor": platform.processor(),
        "imgsz": IMGSZ,
        "prediction_confidence_floor": PRED_CONF,
        "nms_iou": NMS_IOU,
        "max_det": MAX_DET,
        "match_iou": MATCH_IOU,
        "match_iou_status": MATCH_IOU_STATUS,
        "precision_target": PRECISION_TARGET,
        "validation_images": len(image_paths),
        "validation_instances": total_gt,
        "validation_fingerprint_sha256":
            validation_fingerprint,
    }

    with open(
        OUTPUT_DIR / "operational_environment.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            environment,
            f,
            indent=2,
        )

    all_selected = []

    for condition in ["A0", "A1", "A2"]:

        for seed in range(1, 6):

            run_name = (
                f"{condition}_seed{seed:02d}"
            )

            weight_path = (
                WEIGHTS_DIR
                / f"{run_name}_best.pt"
            )

            if not weight_path.exists():
                raise FileNotFoundError(
                    f"Missing checkpoint: {weight_path}"
                )

            run_dir = (
                OUTPUT_DIR
                / run_name
            )

            run_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            print("\n" + "=" * 72)
            print(
                f"OPERATIONAL ANALYSIS: {run_name}"
            )
            print(
                f"WEIGHTS: {weight_path}"
            )
            print("=" * 72)

            checkpoint_hash = sha256_file(
                weight_path
            )

            model = YOLO(
                str(weight_path)
            )

            pred_df = collect_predictions(
                model,
                image_paths,
            )

            pred_df.to_csv(
                run_dir
                / "predictions_lowconf.csv",
                index=False,
            )

            print(
                f"Predictions retained "
                f"(conf >= {PRED_CONF}): "
                f"{len(pred_df)}"
            )

            sweep_df = build_confidence_sweep(
                pred_df,
                gt_by_image,
                total_gt,
            )

            sweep_df.to_csv(
                run_dir
                / "confidence_sweep.csv",
                index=False,
            )

            sweep_records = (
                sweep_df
                .to_dict(
                    orient="records"
                )
            )

            with open(
                run_dir
                / "confidence_sweep.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    sweep_records,
                    f,
                    indent=2,
                )

            selected = (
                select_operating_point(
                    sweep_df
                )
            )

            selected.update(
                {
                    "condition": condition,
                    "seed": seed,
                    "run": run_name,
                    "checkpoint":
                        str(weight_path),
                    "checkpoint_sha256":
                        checkpoint_hash,
                    "validation_images":
                        len(image_paths),
                    "validation_instances":
                        total_gt,
                    "validation_fingerprint_sha256":
                        validation_fingerprint,
                }
            )

            with open(
                run_dir
                / "selected_operating_point.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    selected,
                    f,
                    indent=2,
                )

            all_selected.append(
                selected
            )

            print("\nSELECTED OPERATING POINT")
            print(
                f"threshold : "
                f"{selected['confidence']:.6f}"
            )
            print(
                f"precision : "
                f"{selected['precision']:.6f}"
            )
            print(
                f"recall    : "
                f"{selected['recall']:.6f}"
            )
            print(
                f"F1        : "
                f"{selected['f1']:.6f}"
            )
            print(
                f"TP / FP / FN: "
                f"{selected['tp']} / "
                f"{selected['fp']} / "
                f"{selected['fn']}"
            )

    # ========================================================
    # MASTER TABLE
    # ========================================================

    master_df = pd.DataFrame(
        all_selected
    )

    preferred_columns = [
        "condition",
        "seed",
        "run",
        "confidence",
        "precision",
        "recall",
        "f1",
        "tp",
        "fp",
        "fn",
        "precision_target",
        "match_iou",
        "match_iou_status",
        "prediction_confidence_floor",
        "nms_iou",
        "max_det",
        "validation_images",
        "validation_instances",
        "validation_fingerprint_sha256",
        "checkpoint_sha256",
        "checkpoint",
        "selection_rule",
    ]

    master_df = master_df[
        preferred_columns
    ]

    master_df.to_csv(
        OUTPUT_DIR
        / "all_operational_results.csv",
        index=False,
    )

    with open(
        OUTPUT_DIR
        / "all_operational_results.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            master_df.to_dict(
                orient="records"
            ),
            f,
            indent=2,
        )

    # ========================================================
    # CONDITION SUMMARY
    # ========================================================

    summary = (
        master_df
        .groupby("condition")
        .agg(
            recall_mean=(
                "recall",
                "mean",
            ),
            recall_sd=(
                "recall",
                "std",
            ),
            precision_mean=(
                "precision",
                "mean",
            ),
            precision_sd=(
                "precision",
                "std",
            ),
            f1_mean=(
                "f1",
                "mean",
            ),
            f1_sd=(
                "f1",
                "std",
            ),
            fp_mean=(
                "fp",
                "mean",
            ),
            fp_sd=(
                "fp",
                "std",
            ),
            fn_mean=(
                "fn",
                "mean",
            ),
            fn_sd=(
                "fn",
                "std",
            ),
            threshold_mean=(
                "confidence",
                "mean",
            ),
            threshold_sd=(
                "confidence",
                "std",
            ),
        )
        .reset_index()
    )

    summary.to_csv(
        OUTPUT_DIR
        / "operational_condition_summary.csv",
        index=False,
    )

    print("\n")
    print("=" * 72)
    print(
        "FINAL OPERATIONAL RESULTS"
    )
    print("=" * 72)

    print(
        master_df[
            [
                "condition",
                "seed",
                "confidence",
                "precision",
                "recall",
                "f1",
                "tp",
                "fp",
                "fn",
            ]
        ].to_string(
            index=False
        )
    )

    print("\n")
    print("=" * 72)
    print(
        "CONDITION SUMMARY"
    )
    print("=" * 72)

    print(
        summary.to_string(
            index=False
        )
    )

    print("\nDone.")
    print(
        f"Results saved to:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()