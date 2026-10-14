from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
from PIL import Image


# ============================================================
# INTEGRAL DIFFICULTY ANALYSIS — A0 / A1 / A2
#
# Uses the already generated operational_results:
#   - predictions_lowconf.csv
#   - selected_operating_point.json
#
# It DOES NOT run inference again.
#
# Main outputs:
#   - recall by size: small / medium / large
#   - recall for clustered objects
#   - recall for border-contact objects
#   - per-seed paired deltas vs A0
#
# The selected confidence threshold is the one already chosen
# independently for each run under:
#   maximum Recall subject to Precision >= 0.98
# ============================================================


ROOT = Path(__file__).resolve().parent

VAL_IMAGES = ROOT / "dataset" / "images" / "val"
VAL_LABELS = ROOT / "dataset" / "labels" / "val"

OPERATIONAL_DIR = ROOT / "operational_results"
OUTPUT_DIR = ROOT / "integral_results"

EXPECTED_IMAGES = 109
EXPECTED_INSTANCES = 312

# ------------------------------------------------------------------
# Detection matching criterion.
# Keep identical to operational_recall.py.
#
# IMPORTANT: 0.50 is still marked provisional until the historical
# Classical Augmentation v2 matching code is independently verified.
# ------------------------------------------------------------------
MATCH_IOU = 0.50
MATCH_IOU_STATUS = (
    "provisional_unverified_against_classical_augmentation_v2"
)

# ------------------------------------------------------------------
# Difficulty definitions inherited from the documented v2 protocol.
#
# Size bands were fixed from TRAIN terciles:
# small  : area_ratio < 0.02423
# medium : 0.02423 <= area_ratio < 0.05196
# large  : area_ratio >= 0.05196
#
# Engineering heuristics:
# clustered      : GT overlaps another GT in same image with IoU >= 0.05
# border_contact : normalized distance from bbox to nearest image border
#                  <= 0.01
# ------------------------------------------------------------------
SMALL_MAX = 0.02423
MEDIUM_MAX = 0.05196

CLUSTER_IOU = 0.05
BORDER_CONTACT_NORMALIZED = 0.01

# Historical-v2 thresholds used ONLY as a descriptive sensitivity audit.
# They were predeclared for v2, NOT for the newer A0/A1/A2 campaign.
MAJORITY_SIGN_FRACTION_V2 = 0.80
MAX_OPERATIONAL_DROP_V2 = 0.02

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"
}


# ============================================================
# BASIC GEOMETRY
# ============================================================

def iou_xyxy(box_a, box_b):
    ax1, ay1, ax2, ay2 = map(float, box_a)
    bx1, by1, bx2, by2 = map(float, box_b)

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)

    union = area_a + area_b - inter

    if union <= 0:
        return 0.0

    return inter / union


def best_unmatched_gt(pred_box, pred_class, gt_objects, matched_indices):
    best_idx = None
    best_iou = -1.0

    for idx, gt in enumerate(gt_objects):

        if idx in matched_indices:
            continue

        if int(gt["class_id"]) != int(pred_class):
            continue

        value = iou_xyxy(
            pred_box,
            [gt["x1"], gt["y1"], gt["x2"], gt["y2"]],
        )

        if value > best_iou:
            best_iou = value
            best_idx = idx

    return best_idx, best_iou


# ============================================================
# DATASET / GT LOADING
# ============================================================

def load_validation_gt():
    if not VAL_IMAGES.exists():
        raise FileNotFoundError(
            f"Missing validation image folder: {VAL_IMAGES}"
        )

    if not VAL_LABELS.exists():
        raise FileNotFoundError(
            f"Missing validation label folder: {VAL_LABELS}"
        )

    image_paths = sorted(
        p for p in VAL_IMAGES.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

    if len(image_paths) != EXPECTED_IMAGES:
        raise RuntimeError(
            f"Expected {EXPECTED_IMAGES} validation images, "
            f"but found {len(image_paths)}."
        )

    gt_by_image = {}
    gt_manifest_rows = []

    total_instances = 0

    for image_path in image_paths:
        label_path = VAL_LABELS / f"{image_path.stem}.txt"

        if not label_path.exists():
            raise FileNotFoundError(
                f"Missing label: {label_path}"
            )

        with Image.open(image_path) as im:
            image_width, image_height = im.size

        text = label_path.read_text(encoding="utf-8").strip()
        lines = [] if not text else text.splitlines()

        objects = []

        # ------------------------------------------------------
        # First pass: read YOLO GT and convert to pixel xyxy.
        # ------------------------------------------------------
        for gt_index, line in enumerate(lines):
            parts = line.strip().split()

            if len(parts) < 5:
                raise ValueError(
                    f"Invalid YOLO line in {label_path}: {line}"
                )

            class_id = int(float(parts[0]))
            xc = float(parts[1])
            yc = float(parts[2])
            bw = float(parts[3])
            bh = float(parts[4])

            x1n = xc - bw / 2.0
            y1n = yc - bh / 2.0
            x2n = xc + bw / 2.0
            y2n = yc + bh / 2.0

            x1 = x1n * image_width
            y1 = y1n * image_height
            x2 = x2n * image_width
            y2 = y2n * image_height

            area_ratio = bw * bh

            if area_ratio < SMALL_MAX:
                size_band = "small"
            elif area_ratio < MEDIUM_MAX:
                size_band = "medium"
            else:
                size_band = "large"

            border_distance_normalized = min(
                x1n,
                y1n,
                1.0 - x2n,
                1.0 - y2n,
            )

            border_contact = (
                border_distance_normalized
                <= BORDER_CONTACT_NORMALIZED
            )

            objects.append(
                {
                    "gt_index": gt_index,
                    "class_id": class_id,

                    "xc_norm": xc,
                    "yc_norm": yc,
                    "w_norm": bw,
                    "h_norm": bh,

                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,

                    "area_ratio": area_ratio,
                    "size_band": size_band,

                    "border_distance_normalized":
                        border_distance_normalized,
                    "border_contact": bool(border_contact),

                    # Filled in second pass.
                    "clustered": False,
                }
            )

        # ------------------------------------------------------
        # Second pass: clustered flag.
        # A GT is clustered if it overlaps ANY other GT in the
        # same image with IoU >= CLUSTER_IOU.
        # ------------------------------------------------------
        for i, gt_i in enumerate(objects):
            clustered = False

            box_i = [
                gt_i["x1"],
                gt_i["y1"],
                gt_i["x2"],
                gt_i["y2"],
            ]

            for j, gt_j in enumerate(objects):
                if i == j:
                    continue

                box_j = [
                    gt_j["x1"],
                    gt_j["y1"],
                    gt_j["x2"],
                    gt_j["y2"],
                ]

                if iou_xyxy(box_i, box_j) >= CLUSTER_IOU:
                    clustered = True
                    break

            gt_i["clustered"] = bool(clustered)

        gt_by_image[image_path.stem] = objects
        total_instances += len(objects)

        for gt in objects:
            gt_manifest_rows.append(
                {
                    "image": image_path.name,
                    "image_stem": image_path.stem,
                    "image_width": image_width,
                    "image_height": image_height,

                    "gt_index": gt["gt_index"],
                    "class_id": gt["class_id"],

                    "xc_norm": gt["xc_norm"],
                    "yc_norm": gt["yc_norm"],
                    "w_norm": gt["w_norm"],
                    "h_norm": gt["h_norm"],

                    "area_ratio": gt["area_ratio"],
                    "size_band": gt["size_band"],

                    "clustered": gt["clustered"],
                    "border_distance_normalized":
                        gt["border_distance_normalized"],
                    "border_contact": gt["border_contact"],
                }
            )

    if total_instances != EXPECTED_INSTANCES:
        raise RuntimeError(
            f"Expected {EXPECTED_INSTANCES} validation instances, "
            f"but found {total_instances}."
        )

    return (
        image_paths,
        gt_by_image,
        pd.DataFrame(gt_manifest_rows),
        total_instances,
    )


# ============================================================
# MATCHING AT THE ALREADY-SELECTED OPERATING POINT
# ============================================================

def match_at_selected_threshold(pred_df, gt_by_image, threshold):
    """
    Reproduces the greedy matching used by operational_recall.py.

    Only predictions with confidence >= selected threshold are used.

    Returns:
      TP, FP, FN
      set of matched GT keys: (image_stem, gt_index)
    """

    selected_preds = pred_df[
        pred_df["confidence"] >= threshold
    ].copy()

    # Same deterministic ordering used in operational_recall.py.
    selected_preds = selected_preds.sort_values(
        by=["confidence", "image_stem", "pred_index"],
        ascending=[False, True, True],
        kind="mergesort",
    ).reset_index(drop=True)

    matched_by_image = {
        image_stem: set()
        for image_stem in gt_by_image
    }

    matched_gt_keys = set()

    tp = 0
    fp = 0

    for _, pred in selected_preds.iterrows():

        image_stem = str(pred["image_stem"])
        pred_class = int(pred["class_id"])

        pred_box = [
            float(pred["x1"]),
            float(pred["y1"]),
            float(pred["x2"]),
            float(pred["y2"]),
        ]

        gt_objects = gt_by_image.get(image_stem, [])

        best_idx, best_iou = best_unmatched_gt(
            pred_box=pred_box,
            pred_class=pred_class,
            gt_objects=gt_objects,
            matched_indices=matched_by_image[image_stem],
        )

        if best_idx is not None and best_iou >= MATCH_IOU:
            matched_by_image[image_stem].add(best_idx)
            matched_gt_keys.add((image_stem, int(best_idx)))
            tp += 1
        else:
            fp += 1

    total_gt = sum(len(v) for v in gt_by_image.values())
    fn = total_gt - tp

    return {
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "matched_gt_keys": matched_gt_keys,
        "selected_prediction_count": int(len(selected_preds)),
    }


# ============================================================
# DIFFICULTY METRICS
# ============================================================

def calculate_stratum(gt_manifest, matched_gt_keys, mask):
    subset = gt_manifest[mask].copy()

    gt_count = len(subset)

    if gt_count == 0:
        return {
            "ground_truth": 0,
            "true_positive": 0,
            "false_negative": 0,
            "recall": np.nan,
        }

    tp = 0

    for _, row in subset.iterrows():
        key = (
            str(row["image_stem"]),
            int(row["gt_index"]),
        )

        if key in matched_gt_keys:
            tp += 1

    fn = gt_count - tp
    recall = tp / gt_count

    return {
        "ground_truth": int(gt_count),
        "true_positive": int(tp),
        "false_negative": int(fn),
        "recall": float(recall),
    }


def calculate_all_strata(gt_manifest, matched_gt_keys):
    strata = {}

    # Size
    for size_band in ["small", "medium", "large"]:
        strata[f"size:{size_band}"] = calculate_stratum(
            gt_manifest,
            matched_gt_keys,
            gt_manifest["size_band"] == size_band,
        )

    # Cluster
    strata["clustered:True"] = calculate_stratum(
        gt_manifest,
        matched_gt_keys,
        gt_manifest["clustered"] == True,  # noqa: E712
    )

    strata["clustered:False"] = calculate_stratum(
        gt_manifest,
        matched_gt_keys,
        gt_manifest["clustered"] == False,  # noqa: E712
    )

    # Border
    strata["border_contact:True"] = calculate_stratum(
        gt_manifest,
        matched_gt_keys,
        gt_manifest["border_contact"] == True,  # noqa: E712
    )

    strata["border_contact:False"] = calculate_stratum(
        gt_manifest,
        matched_gt_keys,
        gt_manifest["border_contact"] == False,  # noqa: E712
    )

    return strata


# ============================================================
# OPTIONAL mAP TABLE
# ============================================================

def find_validation_results():
    candidates = [
        ROOT / "validation_results" / "all_validation_results.csv",
        ROOT / "runs" / "detect" / "validation_results"
             / "all_validation_results.csv",
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


# ============================================================
# PAIRED COMPARISONS
# ============================================================

def paired_comparison_table(master_df):
    """
    Seed-paired comparisons:
      A1 - A0
      A2 - A0
      A1 - A2

    Positive values mean the first condition has higher recall.
    """

    metric_columns = [
        "operational_recall",
        "recall_small",
        "recall_medium",
        "recall_large",
        "recall_clustered",
        "recall_border_contact",
    ]

    if "mAP50_95" in master_df.columns:
        metric_columns.insert(0, "mAP50_95")

    comparisons = [
        ("A1", "A0"),
        ("A2", "A0"),
        ("A1", "A2"),
    ]

    rows = []

    for cond_a, cond_b in comparisons:

        a = (
            master_df[master_df["condition"] == cond_a]
            .set_index("seed")
        )

        b = (
            master_df[master_df["condition"] == cond_b]
            .set_index("seed")
        )

        common_seeds = sorted(
            set(a.index).intersection(set(b.index))
        )

        for seed in common_seeds:
            for metric in metric_columns:
                value_a = float(a.loc[seed, metric])
                value_b = float(b.loc[seed, metric])
                delta = value_a - value_b

                rows.append(
                    {
                        "condition_a": cond_a,
                        "condition_b": cond_b,
                        "comparison": f"{cond_a}-{cond_b}",
                        "seed": int(seed),
                        "metric": metric,
                        "value_a": value_a,
                        "value_b": value_b,
                        "delta": float(delta),
                    }
                )

    return pd.DataFrame(rows)


def summarize_paired_deltas(delta_df):
    rows = []

    for (comparison, metric), group in delta_df.groupby(
        ["comparison", "metric"]
    ):
        values = group["delta"].to_numpy(dtype=float)
        n = len(values)

        mean_delta = float(np.mean(values))
        sd_delta = (
            float(np.std(values, ddof=1))
            if n > 1 else np.nan
        )

        positive = int(np.sum(values > 0))
        negative = int(np.sum(values < 0))
        zero = int(np.sum(values == 0))

        positive_fraction = positive / n if n else np.nan

        rows.append(
            {
                "comparison": comparison,
                "metric": metric,
                "n_pairs": n,

                "mean_delta": mean_delta,
                "sd_delta": sd_delta,

                "positive_seeds": positive,
                "negative_seeds": negative,
                "zero_seeds": zero,
                "positive_fraction": positive_fraction,

                "minimum_delta": float(np.min(values)),
                "maximum_delta": float(np.max(values)),

                # Descriptive sensitivity flag only.
                "meets_v2_80pct_positive_direction":
                    bool(
                        positive_fraction
                        >= MAJORITY_SIGN_FRACTION_V2
                    ),
            }
        )

    return pd.DataFrame(rows)


def build_v2_sensitivity_audit(delta_summary):
    """
    This is NOT a claim that v2 criteria were predeclared for A0/A1/A2.

    It only asks:
    "What would the newer campaign look like if inspected through
    the historical v2 engineering tolerances?"
    """

    output = {
        "status":
            "descriptive_sensitivity_analysis_not_predeclared_for_A0_A1_A2",
        "historical_v2_thresholds": {
            "majority_sign_fraction": MAJORITY_SIGN_FRACTION_V2,
            "maximum_operational_recall_drop": MAX_OPERATIONAL_DROP_V2,
        },
        "comparisons_vs_A0": {},
    }

    key_metrics = [
        "operational_recall",
        "recall_small",
        "recall_clustered",
        "recall_border_contact",
    ]

    for comparison in ["A1-A0", "A2-A0"]:

        sub = delta_summary[
            delta_summary["comparison"] == comparison
        ].set_index("metric")

        audit = {}

        for metric in key_metrics:
            if metric not in sub.index:
                continue

            row = sub.loc[metric]

            audit[metric] = {
                "mean_delta": float(row["mean_delta"]),
                "positive_seeds":
                    int(row["positive_seeds"]),
                "n_pairs": int(row["n_pairs"]),
                "positive_fraction":
                    float(row["positive_fraction"]),
                "minimum_seed_delta":
                    float(row["minimum_delta"]),
                "meets_80pct_positive_direction":
                    bool(
                        row[
                            "meets_v2_80pct_positive_direction"
                        ]
                    ),
                "mean_drop_exceeds_0p02":
                    bool(
                        float(row["mean_delta"])
                        < -MAX_OPERATIONAL_DROP_V2
                    ),
            }

        output["comparisons_vs_A0"][comparison] = audit

    return output


# ============================================================
# MAIN
# ============================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("INTEGRAL DIFFICULTY ANALYSIS")
    print("=" * 78)

    (
        image_paths,
        gt_by_image,
        gt_manifest,
        total_gt,
    ) = load_validation_gt()

    print(f"Validation images    : {len(image_paths)}")
    print(f"Validation instances : {total_gt}")

    gt_manifest.to_csv(
        OUTPUT_DIR / "gt_difficulty_manifest.csv",
        index=False,
    )

    # Dataset difficulty composition
    difficulty_counts = {
        "validation_images": int(len(image_paths)),
        "validation_instances": int(total_gt),

        "size_small": int(
            (gt_manifest["size_band"] == "small").sum()
        ),
        "size_medium": int(
            (gt_manifest["size_band"] == "medium").sum()
        ),
        "size_large": int(
            (gt_manifest["size_band"] == "large").sum()
        ),

        "clustered_true": int(
            (gt_manifest["clustered"] == True).sum()  # noqa: E712
        ),
        "clustered_false": int(
            (gt_manifest["clustered"] == False).sum()  # noqa: E712
        ),

        "border_contact_true": int(
            (gt_manifest["border_contact"] == True).sum()  # noqa: E712
        ),
        "border_contact_false": int(
            (gt_manifest["border_contact"] == False).sum()  # noqa: E712
        ),

        "definitions": {
            "small_area_ratio_lt": SMALL_MAX,
            "medium_area_ratio_ge": SMALL_MAX,
            "medium_area_ratio_lt": MEDIUM_MAX,
            "large_area_ratio_ge": MEDIUM_MAX,
            "cluster_iou_ge": CLUSTER_IOU,
            "border_contact_normalized_le":
                BORDER_CONTACT_NORMALIZED,
            "detection_match_iou_ge": MATCH_IOU,
            "detection_match_iou_status":
                MATCH_IOU_STATUS,
        },
    }

    with open(
        OUTPUT_DIR / "difficulty_dataset_summary.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            difficulty_counts,
            f,
            indent=2,
        )

    print("\nDifficulty composition:")
    print(
        f"  small / medium / large = "
        f"{difficulty_counts['size_small']} / "
        f"{difficulty_counts['size_medium']} / "
        f"{difficulty_counts['size_large']}"
    )
    print(
        f"  clustered = "
        f"{difficulty_counts['clustered_true']}"
    )
    print(
        f"  border contact = "
        f"{difficulty_counts['border_contact_true']}"
    )

    # Optional homogeneous mAP results
    validation_results_path = find_validation_results()

    map_df = None

    if validation_results_path is not None:
        print(
            "\nFound homogeneous validation results:"
            f"\n  {validation_results_path}"
        )

        map_df = pd.read_csv(validation_results_path)

        required = {
            "condition",
            "seed",
            "mAP50_95",
        }

        missing = required - set(map_df.columns)

        if missing:
            raise RuntimeError(
                f"Validation result table missing columns: {missing}"
            )

        map_df["seed"] = map_df["seed"].astype(int)

    else:
        print(
            "\nNOTE: all_validation_results.csv not found. "
            "Difficulty analysis will continue without mAP merge."
        )

    master_rows = []
    long_rows = []

    for condition in ["A0", "A1", "A2"]:

        for seed in range(1, 6):

            run_name = f"{condition}_seed{seed:02d}"

            run_dir = OPERATIONAL_DIR / run_name

            selected_path = (
                run_dir / "selected_operating_point.json"
            )

            predictions_path = (
                run_dir / "predictions_lowconf.csv"
            )

            if not selected_path.exists():
                raise FileNotFoundError(
                    f"Missing: {selected_path}"
                )

            if not predictions_path.exists():
                raise FileNotFoundError(
                    f"Missing: {predictions_path}"
                )

            with open(
                selected_path,
                "r",
                encoding="utf-8",
            ) as f:
                selected = json.load(f)

            # Hard protocol checks
            if abs(
                float(selected["match_iou"]) - MATCH_IOU
            ) > 1e-12:
                raise RuntimeError(
                    f"{run_name}: selected_operating_point uses "
                    f"match_iou={selected['match_iou']}, "
                    f"but this script uses MATCH_IOU={MATCH_IOU}."
                )

            if int(selected["validation_images"]) != EXPECTED_IMAGES:
                raise RuntimeError(
                    f"{run_name}: validation image count mismatch."
                )

            if int(selected["validation_instances"]) != EXPECTED_INSTANCES:
                raise RuntimeError(
                    f"{run_name}: validation instance count mismatch."
                )

            threshold = float(
                selected["confidence"]
            )

            pred_df = pd.read_csv(
                predictions_path
            )

            match = match_at_selected_threshold(
                pred_df=pred_df,
                gt_by_image=gt_by_image,
                threshold=threshold,
            )

            # --------------------------------------------------
            # CRITICAL INTEGRITY CHECK:
            # Recalculated TP/FP/FN must reproduce the previous
            # operational analysis exactly.
            # --------------------------------------------------
            expected_tp = int(selected["tp"])
            expected_fp = int(selected["fp"])
            expected_fn = int(selected["fn"])

            if (
                match["tp"] != expected_tp
                or match["fp"] != expected_fp
                or match["fn"] != expected_fn
            ):
                raise RuntimeError(
                    f"\nINTEGRITY FAILURE for {run_name}\n"
                    f"Expected from operational analysis:\n"
                    f"  TP={expected_tp} FP={expected_fp} FN={expected_fn}\n"
                    f"Recalculated here:\n"
                    f"  TP={match['tp']} FP={match['fp']} FN={match['fn']}\n"
                    f"Stop analysis and inspect matching logic."
                )

            strata = calculate_all_strata(
                gt_manifest=gt_manifest,
                matched_gt_keys=match["matched_gt_keys"],
            )

            row = {
                "condition": condition,
                "seed": int(seed),
                "run": run_name,

                "operating_threshold": threshold,
                "operational_precision":
                    float(selected["precision"]),
                "operational_recall":
                    float(selected["recall"]),
                "operational_f1":
                    float(selected["f1"]),

                "tp": match["tp"],
                "fp": match["fp"],
                "fn": match["fn"],

                "recall_small":
                    strata["size:small"]["recall"],
                "recall_medium":
                    strata["size:medium"]["recall"],
                "recall_large":
                    strata["size:large"]["recall"],

                "recall_clustered":
                    strata["clustered:True"]["recall"],
                "recall_not_clustered":
                    strata["clustered:False"]["recall"],

                "recall_border_contact":
                    strata["border_contact:True"]["recall"],
                "recall_no_border_contact":
                    strata["border_contact:False"]["recall"],

                "gt_small":
                    strata["size:small"]["ground_truth"],
                "gt_medium":
                    strata["size:medium"]["ground_truth"],
                "gt_large":
                    strata["size:large"]["ground_truth"],
                "gt_clustered":
                    strata["clustered:True"]["ground_truth"],
                "gt_border_contact":
                    strata["border_contact:True"]["ground_truth"],
            }

            # Merge mAP if available
            if map_df is not None:
                match_map = map_df[
                    (map_df["condition"] == condition)
                    & (map_df["seed"] == seed)
                ]

                if len(match_map) != 1:
                    raise RuntimeError(
                        f"Expected exactly one mAP row for "
                        f"{condition} seed {seed}, "
                        f"found {len(match_map)}."
                    )

                map_row = match_map.iloc[0]

                row["mAP50_95"] = float(
                    map_row["mAP50_95"]
                )

                if "mAP50" in map_row.index:
                    row["mAP50"] = float(
                        map_row["mAP50"]
                    )

                if "mAP75" in map_row.index:
                    row["mAP75"] = float(
                        map_row["mAP75"]
                    )

            master_rows.append(row)

            for stratum_name, values in strata.items():
                long_rows.append(
                    {
                        "condition": condition,
                        "seed": int(seed),
                        "run": run_name,
                        "operating_threshold": threshold,
                        "stratum": stratum_name,
                        "ground_truth":
                            values["ground_truth"],
                        "true_positive":
                            values["true_positive"],
                        "false_negative":
                            values["false_negative"],
                        "recall":
                            values["recall"],
                    }
                )

            print(
                f"\n{run_name}"
                f" | R@P>=0.98={row['operational_recall']:.4f}"
                f" | small={row['recall_small']:.4f}"
                f" | cluster={row['recall_clustered']:.4f}"
                f" | border={row['recall_border_contact']:.4f}"
            )

    # ========================================================
    # MASTER TABLES
    # ========================================================

    master_df = pd.DataFrame(master_rows).sort_values(
        ["condition", "seed"]
    )

    long_df = pd.DataFrame(long_rows).sort_values(
        ["condition", "seed", "stratum"]
    )

    master_df.to_csv(
        OUTPUT_DIR / "all_integral_results.csv",
        index=False,
    )

    long_df.to_csv(
        OUTPUT_DIR / "difficulty_results_long.csv",
        index=False,
    )

    with open(
        OUTPUT_DIR / "all_integral_results.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            master_df.to_dict(orient="records"),
            f,
            indent=2,
        )

    # ========================================================
    # CONDITION SUMMARY
    # ========================================================

    metrics_to_summarize = [
        "operational_recall",
        "operational_f1",
        "recall_small",
        "recall_medium",
        "recall_large",
        "recall_clustered",
        "recall_border_contact",
    ]

    if "mAP50_95" in master_df.columns:
        metrics_to_summarize.insert(0, "mAP50_95")

    summary_rows = []

    for condition, group in master_df.groupby("condition"):
        for metric in metrics_to_summarize:
            values = group[metric].to_numpy(dtype=float)

            summary_rows.append(
                {
                    "condition": condition,
                    "metric": metric,
                    "n": int(len(values)),
                    "mean": float(np.mean(values)),
                    "sd": float(np.std(values, ddof=1)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                }
            )

    condition_summary = pd.DataFrame(summary_rows)

    condition_summary.to_csv(
        OUTPUT_DIR / "integral_condition_summary.csv",
        index=False,
    )

    # ========================================================
    # PAIRED DELTAS
    # ========================================================

    paired_df = paired_comparison_table(
        master_df
    )

    paired_df.to_csv(
        OUTPUT_DIR / "paired_deltas_by_seed.csv",
        index=False,
    )

    delta_summary = summarize_paired_deltas(
        paired_df
    )

    delta_summary.to_csv(
        OUTPUT_DIR / "paired_delta_summary.csv",
        index=False,
    )

    # ========================================================
    # HISTORICAL-v2 SENSITIVITY AUDIT
    # ========================================================

    sensitivity = build_v2_sensitivity_audit(
        delta_summary
    )

    with open(
        OUTPUT_DIR / "v2_sensitivity_audit.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            sensitivity,
            f,
            indent=2,
        )

    # ========================================================
    # PRINT COMPACT RESULTS
    # ========================================================

    print("\n")
    print("=" * 78)
    print("INTEGRAL RESULTS — PER RUN")
    print("=" * 78)

    compact_columns = [
        "condition",
        "seed",
    ]

    if "mAP50_95" in master_df.columns:
        compact_columns.append("mAP50_95")

    compact_columns += [
        "operational_recall",
        "recall_small",
        "recall_medium",
        "recall_large",
        "recall_clustered",
        "recall_border_contact",
    ]

    print(
        master_df[
            compact_columns
        ].to_string(index=False)
    )

    print("\n")
    print("=" * 78)
    print("PAIRED DELTA SUMMARY")
    print("=" * 78)

    print(
        delta_summary[
            [
                "comparison",
                "metric",
                "mean_delta",
                "positive_seeds",
                "n_pairs",
                "minimum_delta",
                "maximum_delta",
                "meets_v2_80pct_positive_direction",
            ]
        ].to_string(index=False)
    )

    print("\n")
    print("=" * 78)
    print("DONE")
    print("=" * 78)

    print(f"Results saved in:\n{OUTPUT_DIR}")

    print(
        "\nIMPORTANT: the v2_sensitivity_audit.json file is only a "
        "descriptive sensitivity analysis. The historical v2 promotion "
        "criteria were not predeclared for the newer A0/A1/A2 campaign."
    )


if __name__ == "__main__":
    main()
