# sync_evaluation.py
# Purpose: Compare automatic sync offset vs ground truth for research metrics

import json
import os

def evaluate_sync():
    base_dir = r"C:\podcast-research"

    # Load automatic metrics
    sync_metrics_path = os.path.join(base_dir, "results", "sync_metrics.json")
    with open(sync_metrics_path, "r") as f:
        auto_metrics = json.load(f)

    # Load ground truth
    gt_path = os.path.join(base_dir, "datasets", "test_set_1", "ground_truth.json")
    with open(gt_path, "r") as f:
        gt = json.load(f)

    auto_offset = auto_metrics["estimated_offset_seconds"]
    gt_offset = gt["manual_sync_offset"]["camera2_offset_seconds"]

    abs_error = abs(auto_offset - gt_offset)

    print("\n=== SYNC EVALUATION ===")
    print(f"Ground truth offset (camera2 vs camera1): {gt_offset:.4f} s")
    print(f"Estimated offset:                         {auto_offset:.4f} s")
    print(f"Absolute error:                           {abs_error:.4f} s")

    # Simple success criterion for paper: error < 0.1s (100 ms)
    success = abs_error < 0.1
    print(f"Within 100 ms tolerance? {'✅ YES' if success else '❌ NO'}")

    # Save evaluation metrics
    eval_metrics = {
        "ground_truth_offset_seconds": gt_offset,
        "estimated_offset_seconds": auto_offset,
        "absolute_error_seconds": abs_error,
        "within_100ms": success
    }

    out_path = os.path.join(base_dir, "results", "sync_evaluation.json")
    with open(out_path, "w") as f:
        json.dump(eval_metrics, f, indent=2)

    print(f"Evaluation metrics saved to {out_path}")

if __name__ == "__main__":
    evaluate_sync()
