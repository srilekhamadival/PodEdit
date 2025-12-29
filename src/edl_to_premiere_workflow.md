# EDL Import Workflow for Premiere Pro

## Problem
XML import keeps failing due to Premiere Pro's strict validation requirements.

## Solution: Use EDL + Manual Track Separation

### Step 1: Import the EDL
1. Open Premiere Pro
2. Create a new sequence (30 fps, 1920x1080 or your desired resolution)
3. Go to `File > Import`
4. Select `results/podcast_edit.edl`
5. When prompted:
   - Type: **NTSC** (or custom 30fps)
   - FPS: **30**

### Step 2: Link Media Files
1. Premiere will ask you to locate the CAM1 and CAM2 reels
2. Link CAM1 to `datasets/test_set_1/camera1_short.mp4`
3. Link CAM2 to `datasets/test_set_1/camera2_short.mp4`

### Step 3: Your Timeline is Ready!
The EDL will create a single video track with all the cuts already made according to:
- Silence removal
- Speaker detection (camera switching)
- Proper sync (0.975s offset applied)

## Alternative: Create Separated CSV for Manual Import

If you want separated tracks, I can generate a **CSV file** that lists:
- Camera 1 segments (with in/out points)
- Camera 2 segments (with in/out points)

You can then use Premiere's batch import or a script to auto-place them on separate tracks.

Would you like me to create the CSV approach instead?
