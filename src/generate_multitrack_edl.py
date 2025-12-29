"""
Generate an EDL with explicit track assignments
This version tries to force Premiere to use separate tracks
"""

import json
import os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def seconds_to_timecode(t, fps):
    if t < 0:
        t = 0.0
    total_frames = int(round(t * fps))
    frames = int(total_frames % fps)
    total_seconds = int(total_frames // fps)
    seconds = int(total_seconds % 60)
    total_minutes = int(total_seconds // 60)
    minutes = int(total_minutes % 60)
    hours = int(total_minutes // 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

def generate_edl_with_tracks():
    edit_segments = load_json("results/edit_segments.json")
    sync_metrics = load_json("results/sync_metrics.json")
    sync_offset = sync_metrics.get("estimated_offset_seconds", 0.0)
    
    fps = 30.0
    lines = []
    
    lines.append("TITLE: PODCAST_MULTITRACK")
    lines.append("FCM: NON-DROP FRAME")
    lines.append("")
    
    current_time = 0.0
    event_num = 1
    
    for seg in edit_segments:
        start = seg["start"]
        end = seg["end"]
        dur = seg["duration"]
        cam = seg["camera"]
        
        record_in = current_time
        record_out = current_time + dur
        
        if cam == 1:
            reel = "CAM1"
            source_in = start
            source_out = end
            track = "V"  # Video track
        else:
            reel = "CAM2"
            source_in = max(0, start - sync_offset)
            source_out = max(0, end - sync_offset)
            track = "V2"  # Try to force track 2
        
        src_in_tc = seconds_to_timecode(source_in, fps)
        src_out_tc = seconds_to_timecode(source_out, fps)
        rec_in_tc = seconds_to_timecode(record_in, fps)
        rec_out_tc = seconds_to_timecode(record_out, fps)
        
        # Standard EDL line
        lines.append(f"{event_num:03d}  {reel:<8} {track:<5} C        {src_in_tc} {src_out_tc} {rec_in_tc} {rec_out_tc}")
        lines.append(f"* FROM CAMERA {cam}")
        lines.append(f"* TARGET_TRACK V{cam}")
        lines.append("")
        
        current_time = record_out
        event_num += 1
    
    with open("results/podcast_edit_multitrack.edl", "w", newline="\n") as f:
        for line in lines:
            f.write(line + "\n")
    
    print("✅ Multi-track EDL created: results/podcast_edit_multitrack.edl")
    print("   This version includes track hints for Premiere")

if __name__ == "__main__":
    generate_edl_with_tracks()
