"""
XML Generator for Premiere Pro Import
Creates a proper Final Cut Pro XML 7 file with multi-track timeline
"""

import json
import os
import uuid
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def frames_to_timecode(frames, fps):
    """Convert frame count to HH:MM:SS:FF format"""
    total_frames = int(frames)
    ff = total_frames % int(fps)
    total_seconds = total_frames // int(fps)
    ss = total_seconds % 60
    total_minutes = total_seconds // 60
    mm = total_minutes % 60
    hh = total_minutes // 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

def create_file_element(file_id, filename, fps, duration_frames, pathurl):
    """Create a proper <file> element with all required metadata"""
    file_elem = Element('file', id=file_id)
    
    # Basic info
    SubElement(file_elem, 'name').text = filename
    SubElement(file_elem, 'pathurl').text = pathurl
    
    # Rate
    rate = SubElement(file_elem, 'rate')
    SubElement(rate, 'timebase').text = str(int(fps))
    SubElement(rate, 'ntsc').text = 'FALSE'
    
    # Duration
    SubElement(file_elem, 'duration').text = str(duration_frames)
    
    # Timecode (start at 00:00:00:00)
    timecode = SubElement(file_elem, 'timecode')
    SubElement(timecode, 'rate')
    SubElement(timecode.find('rate'), 'timebase').text = str(int(fps))
    SubElement(timecode.find('rate'), 'ntsc').text = 'FALSE'
    SubElement(timecode, 'string').text = '00:00:00:00'
    SubElement(timecode, 'frame').text = '0'
    SubElement(timecode, 'displayformat').text = 'NDF'
    
    # Media
    media = SubElement(file_elem, 'media')
    video = SubElement(media, 'video')
    
    # Video characteristics
    video_char = SubElement(video, 'samplecharacteristics')
    SubElement(video_char, 'width').text = '1920'
    SubElement(video_char, 'height').text = '1080'
    
    return file_elem

def create_clipitem(clip_id, file_id, filename, start_frame, end_frame, in_frame, out_frame, fps):
    """Create a <clipitem> element"""
    clipitem = Element('clipitem', id=clip_id)
    
    SubElement(clipitem, 'name').text = filename
    SubElement(clipitem, 'enabled').text = 'TRUE'
    
    # Rate
    rate = SubElement(clipitem, 'rate')
    SubElement(rate, 'timebase').text = str(int(fps))
    SubElement(rate, 'ntsc').text = 'FALSE'
    
    # Timeline position
    SubElement(clipitem, 'start').text = str(start_frame)
    SubElement(clipitem, 'end').text = str(end_frame)
    
    # Source in/out
    SubElement(clipitem, 'in').text = str(in_frame)
    SubElement(clipitem, 'out').text = str(out_frame)
    
    # File reference
    file_ref = SubElement(clipitem, 'file', id=file_id)
    
    return clipitem

def generate_premiere_xml(
    edit_segments,
    sync_offset_seconds,
    fps,
    camera1_filename="camera1_short.mp4",
    camera2_filename="camera2_short.mp4",
    camera1_duration=4157.28,  # seconds
    camera2_duration=4155.9    # seconds
):
    """
    Generate a complete FCP XML 7 file for Premiere Pro
    """
    # Calculate frame durations
    cam1_frames = int(camera1_duration * fps)
    cam2_frames = int(camera2_duration * fps)
    
    # Get absolute paths
    cwd = os.getcwd()
    cam1_path = os.path.join(cwd, "datasets", "test_set_1", camera1_filename).replace("\\", "/")
    cam2_path = os.path.join(cwd, "datasets", "test_set_1", camera2_filename).replace("\\", "/")
    
    # Root element
    root = Element('xmeml', version='5')
    
    # Sequence
    sequence = SubElement(root, 'sequence', id='sequence-1')
    SubElement(sequence, 'uuid').text = str(uuid.uuid4())
    SubElement(sequence, 'name').text = 'Podcast Multi-Cam Edit'
    SubElement(sequence, 'duration').text = str(int(sum(seg['duration'] for seg in edit_segments) * fps))
    
    # Sequence rate
    seq_rate = SubElement(sequence, 'rate')
    SubElement(seq_rate, 'timebase').text = str(int(fps))
    SubElement(seq_rate, 'ntsc').text = 'FALSE'
    
    # Media container
    media = SubElement(sequence, 'media')
    video = SubElement(media, 'video')
    
    # Track 1: Camera 1 clips
    track1 = SubElement(video, 'track')
    
    # Track 2: Camera 2 clips  
    track2 = SubElement(video, 'track')
    
    # Process segments and add to appropriate tracks
    current_timeline_pos = 0
    
    for i, seg in enumerate(edit_segments):
        start_master = seg["start"]
        dur = seg["duration"]
        cam = seg["camera"]
        
        # Timeline position (in frames)
        start_frame = int(current_timeline_pos)
        end_frame = int(current_timeline_pos + dur * fps)
        
        # Source position (in frames)
        if cam == 1:
            source_in = int(start_master * fps)
            source_out = int((start_master + dur) * fps)
            
            clipitem = create_clipitem(
                f"clipitem-{i}",
                "file-1",
                camera1_filename,
                start_frame,
                end_frame,
                source_in,
                source_out,
                fps
            )
            track1.append(clipitem)
            
        else:  # cam == 2
            # Apply sync offset
            source_in = int((start_master - sync_offset_seconds) * fps)
            source_out = int((start_master + dur - sync_offset_seconds) * fps)
            source_in = max(0, source_in)
            source_out = max(source_in, source_out)
            
            clipitem = create_clipitem(
                f"clipitem-{i}",
                "file-2",
                camera2_filename,
                start_frame,
                end_frame,
                source_in,
                source_out,
                fps
            )
            track2.append(clipitem)
        
        current_timeline_pos += dur * fps
    
    # Create file definitions at root level (required by Premiere)
    file1 = create_file_element("file-1", camera1_filename, fps, cam1_frames, f"file://localhost/{cam1_path}")
    file2 = create_file_element("file-2", camera2_filename, fps, cam2_frames, f"file://localhost/{cam2_path}")
    
    # Insert files before sequence
    root.insert(0, file2)
    root.insert(0, file1)
    
    return root

def prettify_xml(elem):
    """Return a pretty-printed XML string"""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')

def main():
    # Load data
    edit_path = "results/edit_segments.json"
    sync_path = "results/sync_metrics.json"
    
    if not os.path.exists(edit_path):
        print(f"❌ {edit_path} not found")
        return
    
    if not os.path.exists(sync_path):
        print(f"❌ {sync_path} not found")
        return
    
    edit_segments = load_json(edit_path)
    sync_metrics = load_json(sync_path)
    sync_offset = sync_metrics.get("estimated_offset_seconds", 0.0)
    
    print("\n=== XML GENERATION ===")
    print(f"Segments: {len(edit_segments)}")
    print(f"Sync offset: {sync_offset:.4f}s")
    print(f"FPS: 30")
    
    # Generate XML
    xml_root = generate_premiere_xml(
        edit_segments=edit_segments,
        sync_offset_seconds=sync_offset,
        fps=30.0
    )
    
    # Write to file
    xml_string = prettify_xml(xml_root)
    
    # Add DOCTYPE
    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    final_xml += '<!DOCTYPE xmeml>\n'
    final_xml += xml_string.split('?>')[1].strip()
    
    output_path = "results/podcast_edit.xml"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_xml)
    
    print(f"✅ XML saved to: {output_path}")
    print(f"   File size: {len(final_xml)} bytes")
    print(f"\nTo import:")
    print(f"1. Open Premiere Pro")
    print(f"2. File > Import")
    print(f"3. Select: {output_path}")

if __name__ == "__main__":
    main()
