# edl_generator.py
# Purpose: Convert edit_segments + sync offset into a CMX 3600 EDL
# that Premiere Pro can import as a cut sequence.

import json
import os
import math
from datetime import datetime
import ffmpeg  # only for reading clip durations if needed

# BASE_DIR is removed, using relative paths now.

# ---------- Utility functions ----------

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def seconds_to_timecode(t, fps):
    """
    Convert seconds (float) to SMPTE timecode string "HH:MM:SS:FF".
    We floor frames.
    """
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

def probe_duration(path):
    """
    Get clip duration in seconds (optional sanity check).
    """
    try:
        probe = ffmpeg.probe(path)
        for s in probe["streams"]:
            if s["codec_type"] == "video":
                return float(s["duration"])
        # fallback: first stream
        return float(probe["streams"][0]["duration"])
    except Exception as e:
        print(f"Warning: could not probe duration for {path}: {e}")
        return None

# ---------- Core EDL generator ----------

def generate_edl(
    edit_segments,
    sync_offset_seconds,
    fps,
    camera1_reel="CAM1",
    camera2_reel="CAM2",
    camera1_start_time=0.0,
    camera2_start_time=0.0
):
    """
    edit_segments: list of {start, end, duration, camera, active_speaker}
                   'start'/'end' are in master timeline seconds AFTER silence removal logic.
    sync_offset_seconds: estimated offset of audio2 relative to audio1 (from sync_engine).
                         positive => camera2 starts later than camera1.
    fps: frames per second (e.g., 25, 29.97 approx as 29.97, 30).
    cameraX_reel: reel names used in EDL (Premiere will show these).
    cameraX_start_time: if your clips don’t actually start at 0, you can adjust here.

    Returns: EDL as a list of lines (strings).
    """
    lines = []

    # Header
    lines.append("TITLE: PODCAST_EDIT")
    lines.append(f"FCM: NON-DROP FRAME")  # change if you want drop-frame
    lines.append("")

    current_record_time = 0.0
    event_number = 1

    for seg in edit_segments:
        master_start = seg["start"]      # seconds
        master_end = seg["end"]          # seconds
        dur = seg["duration"]
        cam = seg["camera"]

        record_in = current_record_time
        record_out = current_record_time + dur

        # Source in/out mapping
        if cam == 1:
            reel = camera1_reel
            # camera1 is reference, so source time = master time + any camera1_start_time
            source_in = camera1_start_time + master_start
            source_out = camera1_start_time + master_end
        elif cam == 2:
            reel = camera2_reel
            # camera2 time is offset relative to camera1
            # if sync_offset_seconds > 0, audio2 (camera2) is delayed; so camera2's picture lags.
            # we treat master timeline as camera1 reference.
            source_in = camera2_start_time + (master_start - sync_offset_seconds)
            source_out = camera2_start_time + (master_end - sync_offset_seconds)
        else:
            # Fallback: treat as camera1
            reel = camera1_reel
            source_in = camera1_start_time + master_start
            source_out = camera1_start_time + master_end

        # Prevent negative source times
        source_in = max(0.0, source_in)
        source_out = max(source_in, source_out)

        # Convert to timecode
        src_in_tc = seconds_to_timecode(source_in, fps)
        src_out_tc = seconds_to_timecode(source_out, fps)
        rec_in_tc = seconds_to_timecode(record_in, fps)
        rec_out_tc = seconds_to_timecode(record_out, fps)

        ev_str = f"{event_number:03d}  {reel:<8} V     C        {src_in_tc} {src_out_tc} {rec_in_tc} {rec_out_tc}"
        lines.append(ev_str)
        # Optional comment lines (Premiere shows these in comments)
        lines.append(f"* FROM CAMERA {cam}")
        if "active_speaker" in seg:
            lines.append(f"* ACTIVE_SPEAKER {seg['active_speaker']}")
        lines.append("")

        current_record_time = record_out
        event_number += 1

    return lines

def save_edl(lines, path):
    with open(path, "w", newline="\n") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"✅ EDL saved to {path}")

# ---------- XML Generator (Multi-Track) ----------

import uuid
import urllib.parse

def generate_xml(
    edit_segments,
    sync_offset_seconds,
    fps,
    camera1_filename="camera1_short.mp4",
    camera2_filename="camera2_short.mp4"
):
    """
    Generate an FCP XML with URL-encoded paths and optimized structure.
    """
    seq_uuid = str(uuid.uuid4())
    cwd = os.getcwd()
    
    # URL encode paths for XML safety
    def get_url(filename):
        abs_path = os.path.join(cwd, "datasets", "test_set_1", filename).replace("\\", "/")
        # Properly encode spaces and special characters
        quoted_path = urllib.parse.quote(abs_path)
        return f"file://localhost/{quoted_path}"

    cam1_url = get_url(camera1_filename)
    cam2_url = get_url(camera2_filename)

    xml_header = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5">
  <sequence id="sequence_1">
    <uuid>{seq_uuid}</uuid>
    <name>Podcast Multi-Cam Edit</name>
    <rate>
      <timebase>{int(fps)}</timebase>
      <ntsc>FALSE</ntsc>
    </rate>
    <media>
      <video>"""
    
    track1_clips = []
    track2_clips = []
    current_record_time = 0.0
    
    for i, seg in enumerate(edit_segments):
        start_master = seg["start"]
        dur = seg["duration"]
        cam = seg["camera"]
        
        in_frame = int(round(current_record_time * fps))
        out_frame = int(round((current_record_time + dur) * fps))
        
        if cam == 1:
            source_in = int(round(start_master * fps))
            source_out = int(round((start_master + dur) * fps))
            clip_name = camera1_filename
            path_url = cam1_url
            file_id = "file_1"
            current_track = track1_clips
        else:
            source_in = int(round((start_master - sync_offset_seconds) * fps))
            source_out = int(round((start_master + dur - sync_offset_seconds) * fps))
            source_in = max(0, source_in)
            source_out = max(source_in, source_out)
            clip_name = camera2_filename
            path_url = cam2_url
            file_id = "file_2"
            current_track = track2_clips
            
        clip_xml = f"""
            <clipitem id="clip_{i}">
              <name>{clip_name}</name>
              <rate><timebase>{int(fps)}</timebase><ntsc>FALSE</ntsc></rate>
              <start>{in_frame}</start>
              <end>{out_frame}</end>
              <in>{source_in}</in>
              <out>{source_out}</out>
              <file id="{file_id}">
                <name>{clip_name}</name>
                <pathurl>{path_url}</pathurl>
              </file>
            </clipitem>"""
        current_track.append(clip_xml)
        current_record_time += dur

    xml_body = "\n        <track>\n" + "".join(track1_clips) + "\n        </track>"
    xml_body += "\n        <track>\n" + "".join(track2_clips) + "\n        </track>"
    
    xml_footer = """
      </video>
    </media>
  </sequence>
</xmeml>"""
    
    return xml_header + xml_body + xml_footer

# ---------- Main test harness ----------

def main():
    edit_path = "results/edit_segments.json"
    if not os.path.exists(edit_path):
        print("❌ edit_segments.json not found. Please run timeline_merger.py first.")
        return
    edit_segments = load_json(edit_path)

    # 2) Load sync offset
    sync_path = "results/sync_metrics.json"
    if not os.path.exists(sync_path):
        print("❌ sync_metrics.json not found. Please run sync_engine.py first.")
        return
    sync_metrics = load_json(sync_path)
    sync_offset_seconds = sync_metrics.get("estimated_offset_seconds", 0.0)

    print("\n=== GENERATION (EDL & XML) ===")
    print(f"Using sync offset: {sync_offset_seconds:.4f} s at 30 FPS")

    fps = 30.0
    
    # 4) Generate EDL
    edl_lines = generate_edl(
        edit_segments=edit_segments,
        sync_offset_seconds=sync_offset_seconds,
        fps=fps
    )
    save_edl(edl_lines, "results/podcast_edit.edl")
    
    # 5) Generate XML (for Multi-Track)
    xml_content = generate_xml(
        edit_segments=edit_segments,
        sync_offset_seconds=sync_offset_seconds,
        fps=fps,
        camera1_filename="camera1_short.mp4",
        camera2_filename="camera2_short.mp4"
    )
    with open("results/podcast_edit.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"✅ Multi-track XML saved to results/podcast_edit.xml")

if __name__ == "__main__":
    main()
