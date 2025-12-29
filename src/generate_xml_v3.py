"""
Generate FCP XML Version 3 (oldest supported format)
Even simpler than v4 - maximum compatibility
"""

import json
import os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def generate_fcp_xml_v3():
    edit_segments = load_json("results/edit_segments.json")
    sync_metrics = load_json("results/sync_metrics.json")
    sync_offset = sync_metrics.get("estimated_offset_seconds", 0.0)
    
    fps = 30
    
    # Build XML manually (version 3 format - most basic)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<!DOCTYPE xmeml>\n'
    xml += '<xmeml version="3">\n'
    xml += '  <sequence>\n'
    xml += '    <name>Podcast Edit</name>\n'
    xml += '    <duration>120000</duration>\n'
    xml += '    <rate>\n'
    xml += f'      <timebase>{fps}</timebase>\n'
    xml += '    </rate>\n'
    xml += '    <media>\n'
    xml += '      <video>\n'
    
    # Track 1 - Camera 1
    xml += '        <track>\n'
    current_pos = 0
    clip_num = 0
    
    for i, seg in enumerate(edit_segments):
        if seg["camera"] != 1:
            continue
        
        start_frames = int(seg["start"] * fps)
        dur_frames = int(seg["duration"] * fps)
        end_frames = start_frames + dur_frames
        
        xml += f'          <clipitem id="c{clip_num}">\n'
        xml += f'            <name>camera1_short.mp4</name>\n'
        xml += f'            <start>{current_pos}</start>\n'
        xml += f'            <end>{current_pos + dur_frames}</end>\n'
        xml += f'            <in>{start_frames}</in>\n'
        xml += f'            <out>{end_frames}</out>\n'
        xml += f'          </clipitem>\n'
        
        current_pos += dur_frames
        clip_num += 1
    
    xml += '        </track>\n'
    
    # Track 2 - Camera 2
    xml += '        <track>\n'
    current_pos = 0
    
    for i, seg in enumerate(edit_segments):
        if seg["camera"] != 2:
            continue
        
        # Apply sync offset
        start_sec = max(0, seg["start"] - sync_offset)
        start_frames = int(start_sec * fps)
        dur_frames = int(seg["duration"] * fps)
        end_frames = start_frames + dur_frames
        
        xml += f'          <clipitem id="c{clip_num}">\n'
        xml += f'            <name>camera2_short.mp4</name>\n'
        xml += f'            <start>{current_pos}</start>\n'
        xml += f'            <end>{current_pos + dur_frames}</end>\n'
        xml += f'            <in>{start_frames}</in>\n'
        xml += f'            <out>{end_frames}</out>\n'
        xml += f'          </clipitem>\n'
        
        current_pos += dur_frames
        clip_num += 1
    
    xml += '        </track>\n'
    xml += '      </video>\n'
    xml += '    </media>\n'
    xml += '  </sequence>\n'
    xml += '</xmeml>\n'
    
    with open("results/podcast_edit_v3.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    
    print("✅ FCP XML Version 3 created: results/podcast_edit_v3.xml")
    print("   This is the most basic/oldest format")
    print("   Track 1: Camera 1 clips")
    print("   Track 2: Camera 2 clips")

if __name__ == "__main__":
    generate_fcp_xml_v3()
