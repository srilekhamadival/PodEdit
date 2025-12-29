"""
Generate FCP XML Version 4 (older format)
Some Premiere versions accept this better than version 5
"""

import json
import os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def generate_fcp_xml_v4():
    edit_segments = load_json("results/edit_segments.json")
    sync_metrics = load_json("results/sync_metrics.json")
    sync_offset = sync_metrics.get("estimated_offset_seconds", 0.0)
    
    fps = 30
    cwd = os.getcwd()
    cam1_path = os.path.join(cwd, "datasets", "test_set_1", "camera1_short.mp4").replace("\\", "/")
    cam2_path = os.path.join(cwd, "datasets", "test_set_1", "camera2_short.mp4").replace("\\", "/")
    
    # Build XML manually (version 4 format)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<!DOCTYPE xmeml>\n'
    xml += '<xmeml version="4">\n'
    xml += '  <sequence>\n'
    xml += '    <name>Podcast Edit</name>\n'
    xml += '    <duration>120000</duration>\n'
    xml += '    <rate>\n'
    xml += f'      <timebase>{fps}</timebase>\n'
    xml += '      <ntsc>FALSE</ntsc>\n'
    xml += '    </rate>\n'
    xml += '    <timecode>\n'
    xml += '      <rate>\n'
    xml += f'        <timebase>{fps}</timebase>\n'
    xml += '        <ntsc>FALSE</ntsc>\n'
    xml += '      </rate>\n'
    xml += '      <string>00:00:00:00</string>\n'
    xml += '      <frame>0</frame>\n'
    xml += '    </timecode>\n'
    xml += '    <media>\n'
    xml += '      <video>\n'
    xml += '        <format>\n'
    xml += '          <samplecharacteristics>\n'
    xml += '            <width>1920</width>\n'
    xml += '            <height>1080</height>\n'
    xml += '          </samplecharacteristics>\n'
    xml += '        </format>\n'
    
    # Track 1
    xml += '        <track>\n'
    current_pos = 0
    for i, seg in enumerate(edit_segments):
        if seg["camera"] != 1:
            continue
        
        start_frames = int(seg["start"] * fps)
        dur_frames = int(seg["duration"] * fps)
        end_frames = start_frames + dur_frames
        
        xml += f'          <clipitem id="clip-{i}">\n'
        xml += f'            <name>camera1_short.mp4</name>\n'
        xml += f'            <duration>{dur_frames}</duration>\n'
        xml += f'            <rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>\n'
        xml += f'            <start>{current_pos}</start>\n'
        xml += f'            <end>{current_pos + dur_frames}</end>\n'
        xml += f'            <in>{start_frames}</in>\n'
        xml += f'            <out>{end_frames}</out>\n'
        xml += f'          </clipitem>\n'
        
        current_pos += dur_frames
    
    xml += '        </track>\n'
    
    # Track 2
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
        
        xml += f'          <clipitem id="clip-{i}">\n'
        xml += f'            <name>camera2_short.mp4</name>\n'
        xml += f'            <duration>{dur_frames}</duration>\n'
        xml += f'            <rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>\n'
        xml += f'            <start>{current_pos}</start>\n'
        xml += f'            <end>{current_pos + dur_frames}</end>\n'
        xml += f'            <in>{start_frames}</in>\n'
        xml += f'            <out>{end_frames}</out>\n'
        xml += f'          </clipitem>\n'
        
        current_pos += dur_frames
    
    xml += '        </track>\n'
    xml += '      </video>\n'
    xml += '    </media>\n'
    xml += '  </sequence>\n'
    xml += '</xmeml>\n'
    
    with open("results/podcast_edit_v4.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    
    print("✅ FCP XML Version 4 created: results/podcast_edit_v4.xml")
    print("   This is a simpler format that some Premiere versions accept better")

if __name__ == "__main__":
    generate_fcp_xml_v4()
