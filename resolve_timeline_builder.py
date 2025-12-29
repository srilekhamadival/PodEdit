"""
DaVinci Resolve Timeline Builder
Automatically creates a multi-cam timeline from edit_segments.json

USAGE:
1. Open DaVinci Resolve
2. Open the Scripting Console (Workspace > Console)
3. In the console, run:
   exec(open(r'C:\\path\\to\\resolve_timeline_builder.py').read())
   
   OR simply run from command line if Resolve's Python API is configured:
   python resolve_timeline_builder.py

REQUIREMENTS:
- DaVinci Resolve 16 or later (Free or Studio)
- Python 3.6+
- Resolve's Python API must be accessible
- edit_segments.json and sync_metrics.json in results/
- camera1_short.mp4 and camera2_short.mp4 in datasets/test_set_1/

SETUP (First time only):
- Set RESOLVE_SCRIPT_API environment variable to Resolve's Python modules
  Example: C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules
"""

import sys
import os
import json

# Add Resolve's Python API to path
try:
    import DaVinciResolveScript as dvr_script
except ImportError:
    print("ERROR: DaVinci Resolve Python API not found!")
    print("\nPlease set RESOLVE_SCRIPT_API environment variable or add Resolve's Python modules to your path.")
    print("Typical location: C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules")
    sys.exit(1)

# ========================================
# CONFIGURATION
# ========================================
FPS = "30"
SEQUENCE_NAME = "Podcast Multi-Cam Edit"
PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# ========================================
# UTILITY FUNCTIONS
# ========================================

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def frames_to_timecode(frames, fps=30):
    """Convert frame count to timecode string HH:MM:SS:FF"""
    total_frames = int(frames)
    ff = total_frames % fps
    total_seconds = total_frames // fps
    ss = total_seconds % 60
    total_minutes = total_seconds // 60
    mm = total_minutes % 60
    hh = total_minutes // 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

# ========================================
# MAIN SCRIPT
# ========================================

def main():
    print("=== DaVinci Resolve Timeline Builder ===\n")
    
    # Get Resolve instance
    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        print("ERROR: Could not connect to DaVinci Resolve!")
        print("Please make sure Resolve is running.")
        return False
    
    # Get current project
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    
    if not project:
        print("ERROR: No project is open in Resolve!")
        print("Please open or create a project first.")
        return False
    
    print(f"Project: {project.GetName()}")
    
    # Load edit segments
    segments_path = os.path.join(PROJECT_FOLDER, "results", "edit_segments.json")
    sync_path = os.path.join(PROJECT_FOLDER, "results", "sync_metrics.json")
    
    if not os.path.exists(segments_path):
        print(f"ERROR: {segments_path} not found!")
        return False
    
    if not os.path.exists(sync_path):
        print(f"ERROR: {sync_path} not found!")
        return False
    
    edit_segments = load_json(segments_path)
    sync_metrics = load_json(sync_path)
    sync_offset = sync_metrics.get("estimated_offset_seconds", 0.0)
    
    print(f"Segments loaded: {len(edit_segments)}")
    print(f"Sync offset: {sync_offset:.4f}s")
    print(f"FPS: {FPS}\n")
    
    # Get media pool
    media_pool = project.GetMediaPool()
    root_folder = media_pool.GetRootFolder()
    
    # Import media files
    print("Importing media files...")
    cam1_path = os.path.join(PROJECT_FOLDER, "datasets", "test_set_1", "camera1_short.mp4")
    cam2_path = os.path.join(PROJECT_FOLDER, "datasets", "test_set_1", "camera2_short.mp4")
    
    if not os.path.exists(cam1_path):
        print(f"ERROR: {cam1_path} not found!")
        return False
    
    if not os.path.exists(cam2_path):
        print(f"ERROR: {cam2_path} not found!")
        return False
    
    # Import clips
    imported_clips = media_pool.ImportMedia([cam1_path, cam2_path])
    
    if not imported_clips or len(imported_clips) < 2:
        print("ERROR: Failed to import media files!")
        return False
    
    print(f"✓ Imported camera1_short.mp4")
    print(f"✓ Imported camera2_short.mp4\n")
    
    # Find the clips in media pool
    clips = root_folder.GetClipList()
    cam1_clip = None
    cam2_clip = None
    
    for clip in clips:
        name = clip.GetName()
        if "camera1" in name.lower():
            cam1_clip = clip
        elif "camera2" in name.lower():
            cam2_clip = clip
    
    if not cam1_clip or not cam2_clip:
        print("ERROR: Could not find imported clips in media pool!")
        return False
    
    # Create new timeline
    print(f"Creating timeline: {SEQUENCE_NAME}...")
    timeline = media_pool.CreateEmptyTimeline(SEQUENCE_NAME)
    
    if not timeline:
        print("ERROR: Failed to create timeline!")
        return False
    
    # Set timeline settings
    timeline.SetSetting("timelineFrameRate", FPS)
    
    print(f"✓ Timeline created\n")
    print("Building timeline...")
    
    # Current position on timeline (in frames)
    current_position = 0
    
    # Process each segment
    for i, seg in enumerate(edit_segments):
        start_master = seg["start"]
        duration = seg["duration"]
        camera = seg["camera"]
        
        # Calculate source in/out (in frames)
        if camera == 1:
            source_in = int(start_master * int(FPS))
            source_out = int((start_master + duration) * int(FPS))
            source_clip = cam1_clip
            track_index = 1  # Video Track 1
        else:
            # Apply sync offset for camera 2
            source_in = int(max(0, (start_master - sync_offset) * int(FPS)))
            source_out = int(max(0, (start_master + duration - sync_offset) * int(FPS)))
            source_clip = cam2_clip
            track_index = 2  # Video Track 2
        
        # Create media pool item with in/out points
        clip_info = {
            "mediaPoolItem": source_clip,
            "startFrame": source_in,
            "endFrame": source_out,
            "recordFrame": current_position,
            "trackIndex": track_index
        }
        
        # Add clip to timeline
        success = media_pool.AppendToTimeline([clip_info])
        
        if not success:
            print(f"Warning: Failed to add clip {i}")
        
        # Move position forward
        current_position += int(duration * int(FPS))
        
        # Progress update
        if i % 50 == 0:
            print(f"Progress: {i}/{len(edit_segments)}")
    
    print(f"\n✅ Timeline built successfully!")
    print(f"   Track 1: Camera 1 clips")
    print(f"   Track 2: Camera 2 clips")
    print(f"   Total segments: {len(edit_segments)}")
    print(f"   Final duration: {current_position / int(FPS):.2f}s")
    
    return True

# ========================================
# RUN
# ========================================
if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
