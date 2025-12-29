# How to Import EDL Without Manual Linking

## The Problem
Premiere Pro asks you to link every clip individually because it doesn't know where CAM1 and CAM2 are.

## The Solution: Pre-Import Workflow

### Step 1: Import Source Files First
1. Open Premiere Pro
2. **Before doing anything else**, import these two files into your Project Panel:
   - `datasets/test_set_1/camera1_short.mp4`
   - `datasets/test_set_1/camera2_short.mp4`
3. In the Project Panel, **rename them exactly**:
   - Rename `camera1_short.mp4` to `CAM1`
   - Rename `camera2_short.mp4` to `CAM2`
   
   (This is critical! The names must match the reel names in the EDL)

### Step 2: Create a New Sequence
1. Right-click on one of the clips → New Sequence from Clip
2. Make sure it's **30 fps**

### Step 3: Import the EDL
1. Go to `File > Import`
2. Select `results/podcast_edit.edl`
3. Choose **NTSC / 30 FPS**
4. **Premiere should now automatically link everything** because the reel names (CAM1, CAM2) match the clip names in your project!

### What Happens
- Premiere reads "CAM1" in the EDL
- Looks in your current project for a clip named "CAM1"
- Finds it and uses it automatically!
- Same for CAM2

No manual linking needed!

## Alternative: Batch Rename Reels
If the above doesn't work, after EDL import, you can:
1. Select ALL clips in the timeline
2. Right-click → "Modify > Clip Name"
3. Replace CAM1 with actual path to camera1_short.mp4

But the pre-import method is much cleaner.
