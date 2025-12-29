"""
Generate a CSV reference file for manual Premiere Pro editing
This creates a spreadsheet showing exactly which clips go on which track
"""

import json
import os
import csv

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def seconds_to_timecode(seconds, fps=30):
    """Convert seconds to HH:MM:SS:FF"""
    total_frames = int(seconds * fps)
    frames = total_frames % fps
    total_seconds = total_frames // fps
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

def main():
    # Load data
    edit_segments = load_json("results/edit_segments.json")
    sync_metrics = load_json("results/sync_metrics.json")
    sync_offset = sync_metrics.get("estimated_offset_seconds", 0.0)
    
    # Create CSV
    csv_path = "results/premiere_edit_reference.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow([
            'Clip #',
            'Camera',
            'Track',
            'Timeline In',
            'Timeline Out',
            'Source File',
            'Source In',
            'Source Out',
            'Duration (s)',
            'Notes'
        ])
        
        current_time = 0.0
        
        for i, seg in enumerate(edit_segments, 1):
            start = seg["start"]
            end = seg["end"]
            dur = seg["duration"]
            cam = seg["camera"]
            
            # Timeline position
            timeline_in = seconds_to_timecode(current_time)
            timeline_out = seconds_to_timecode(current_time + dur)
            
            # Source position
            if cam == 1:
                source_file = "camera1_short.mp4"
                source_in = seconds_to_timecode(start)
                source_out = seconds_to_timecode(end)
                track = "V1"
            else:
                source_file = "camera2_short.mp4"
                # Apply sync offset
                adjusted_start = max(0, start - sync_offset)
                adjusted_end = max(0, end - sync_offset)
                source_in = seconds_to_timecode(adjusted_start)
                source_out = seconds_to_timecode(adjusted_end)
                track = "V2"
            
            notes = f"Speaker {seg.get('active_speaker', '?')}"
            
            writer.writerow([
                i,
                f"CAM{cam}",
                track,
                timeline_in,
                timeline_out,
                source_file,
                source_in,
                source_out,
                f"{dur:.2f}",
                notes
            ])
            
            current_time += dur
    
    print(f"✅ CSV reference created: {csv_path}")
    print(f"   Total clips: {len(edit_segments)}")
    print(f"   Camera 1: {sum(1 for s in edit_segments if s['camera'] == 1)}")
    print(f"   Camera 2: {sum(1 for s in edit_segments if s['camera'] == 2)}")
    print(f"\nOpen this in Excel to see the complete edit breakdown.")

if __name__ == "__main__":
    main()
