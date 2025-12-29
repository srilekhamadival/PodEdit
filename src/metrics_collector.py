import json
import numpy as np
from datetime import datetime
import os

class MetricsCollector:
    """Collects all evaluation metrics for research paper"""
    
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        self.metrics = {
            'experiment_name': experiment_name,
            'timestamp': datetime.now().isoformat(),
            'sync_metrics': {},
            'silence_detection_metrics': {},
            'speaker_detection_metrics': {},
            'performance_metrics': {},
            'comparison_metrics': {}
        }
    
    def log_sync_accuracy(self, predicted_offset, ground_truth_offset):
        """
        Calculate sync accuracy for RQ1
        
        Metrics for paper:
        - Absolute error (seconds)
        - Relative error (%)
        - Success rate (error < 0.1s threshold)
        """
        error_seconds = abs(predicted_offset - ground_truth_offset)
        relative_error = (error_seconds / ground_truth_offset * 100) if ground_truth_offset != 0 else 0
        
        self.metrics['sync_metrics'] = {
            'predicted_offset': predicted_offset,
            'ground_truth_offset': ground_truth_offset,
            'absolute_error_seconds': error_seconds,
            'relative_error_percent': relative_error,
            'success': error_seconds < 0.1  # Within 100ms = success
        }
        
        print(f"\n📊 Sync Accuracy:")
        print(f"   Predicted: {predicted_offset:.3f}s")
        print(f"   Ground Truth: {ground_truth_offset:.3f}s")
        print(f"   Error: {error_seconds:.3f}s ({relative_error:.2f}%)")
        print(f"   Status: {'✅ SUCCESS' if error_seconds < 0.1 else '⚠️ NEEDS IMPROVEMENT'}")
    
    def log_silence_detection(self, detected_segments, ground_truth_segments):
        """
        Calculate precision, recall, F1-score for RQ2
        
        True Positive: Detected silence that matches ground truth
        False Positive: Detected silence that isn't actually silence
        False Negative: Missed silence that should be detected
        """
        tp = 0  # True positives
        fp = 0  # False positives
        fn = 0  # False negatives
        
        # For each ground truth silence segment
        for gt_seg in ground_truth_segments:
            if not gt_seg['should_remove']:
                continue  # Skip segments that shouldn't be removed
                
            matched = False
            for det_seg in detected_segments:
                # Check overlap using IoU (Intersection over Union)
                overlap = self._calculate_overlap(
                    (gt_seg['start'], gt_seg['end']),
                    (det_seg['start'], det_seg['end'])
                )
                if overlap > 0.5:  # 50% IoU threshold
                    tp += 1
                    matched = True
                    break
            
            if not matched:
                fn += 1  # Missed this ground truth segment
        
        # Check for false positives (detected but not in ground truth)
        for det_seg in detected_segments:
            matched = False
            for gt_seg in ground_truth_segments:
                if not gt_seg['should_remove']:
                    continue
                overlap = self._calculate_overlap(
                    (gt_seg['start'], gt_seg['end']),
                    (det_seg['start'], det_seg['end'])
                )
                if overlap > 0.5:
                    matched = True
                    break
            if not matched:
                fp += 1
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        self.metrics['silence_detection_metrics'] = {
            'true_positives': tp,
            'false_positives': fp,
            'false_negatives': fn,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'detected_count': len(detected_segments),
            'ground_truth_count': len([s for s in ground_truth_segments if s['should_remove']])
        }
        
        print(f"\n📊 Silence Detection Performance:")
        print(f"   Precision: {precision:.3f}")
        print(f"   Recall: {recall:.3f}")
        print(f"   F1-Score: {f1_score:.3f}")
        print(f"   TP: {tp}, FP: {fp}, FN: {fn}")
    
    def log_processing_time(self, total_time, video_duration):
        """
        Calculate time savings for RQ3
        
        Key metric: Real-time factor = processing_time / video_duration
        < 1.0 = Faster than real-time
        """
        real_time_factor = total_time / video_duration
        speedup = video_duration / total_time
        
        self.metrics['performance_metrics'] = {
            'processing_time_seconds': total_time,
            'video_duration_seconds': video_duration,
            'real_time_factor': real_time_factor,
            'speedup_factor': speedup,
            'faster_than_realtime': real_time_factor < 1.0
        }
        
        print(f"\n⚡ Performance:")
        print(f"   Processing Time: {total_time:.2f}s")
        print(f"   Video Duration: {video_duration:.2f}s")
        print(f"   Real-time Factor: {real_time_factor:.2f}x")
        print(f"   Speedup: {speedup:.2f}x {'✅' if speedup > 1 else '⚠️'}")
    
    def _calculate_overlap(self, segment1, segment2):
        """Calculate Intersection over Union (IoU) for two segments"""
        start1, end1 = segment1
        start2, end2 = segment2
        
        # Calculate intersection
        intersection_start = max(start1, start2)
        intersection_end = min(end1, end2)
        intersection = max(0, intersection_end - intersection_start)
        
        # Calculate union
        union = (end1 - start1) + (end2 - start2) - intersection
        
        return intersection / union if union > 0 else 0
    
    def save_results(self, output_dir="results"):
        """Save metrics in format ready for LaTeX tables"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON for processing
        json_path = f"{output_dir}/{self.experiment_name}_metrics.json"
        with open(json_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Save LaTeX-ready table
        latex_path = f"{output_dir}/{self.experiment_name}_table.tex"
        self._generate_latex_table(latex_path)
        
        print(f"\n💾 Results saved:")
        print(f"   JSON: {json_path}")
        print(f"   LaTeX: {latex_path}")
    
    def _generate_latex_table(self, output_path):
        """Generate LaTeX table for paper"""
        latex_content = f"""
% Auto-generated metrics table for {self.experiment_name}
\\begin{{table}}[h]
\\centering
\\caption{{Performance Metrics - {self.experiment_name}}}
\\begin{{tabular}}{{lc}}
\\hline
\\textbf{{Metric}} & \\textbf{{Value}} \\\\
\\hline
Sync Error (seconds) & {self.metrics['sync_metrics'].get('absolute_error_seconds', 'N/A'):.3f} \\\\
Silence Precision & {self.metrics['silence_detection_metrics'].get('precision', 'N/A'):.3f} \\\\
Silence Recall & {self.metrics['silence_detection_metrics'].get('recall', 'N/A'):.3f} \\\\
Silence F1-Score & {self.metrics['silence_detection_metrics'].get('f1_score', 'N/A'):.3f} \\\\
Processing Time (s) & {self.metrics['performance_metrics'].get('processing_time_seconds', 'N/A'):.2f} \\\\
Real-time Factor & {self.metrics['performance_metrics'].get('real_time_factor', 'N/A'):.2f}x \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
"""
        with open(output_path, 'w') as f:
            f.write(latex_content)
