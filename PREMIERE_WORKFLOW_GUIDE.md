# Premiere Pro Complete Workflow Guide
## No Scripting Required - Manual but Efficient

Since Premiere Pro automation isn't available, here's the **complete practical workflow** with all the tools you need.

---

## What You Have Now:

✅ **`results/podcast_edit.edl`** - Standard EDL (single track)  
✅ **`results/podcast_edit_multitrack.edl`** - EDL with track hints  
✅ **`results/premiere_edit_reference.csv`** - Complete edit spreadsheet (785 clips)  
✅ **Both video files** ready to import

---

## Method 1: Import EDL + Manual Track Separation (Fastest)

### Step 1: Pre-Import Media
1. Open Premiere Pro
2. Create new project  
3. **Import FIRST** (critical for automatic linking):
   - `datasets/test_set_1/camera1_short.mp4`
   - `datasets/test_set_1/camera2_short.mp4`
4. **Rename in Project Panel**:
   - `camera1_short.mp4` → `CAM1`
   - `camera2_short.mp4` → `CAM2`

### Step 2: Import EDL
1. `File > Import`
2. Select `results/podcast_edit.edl`
3. Choose **NTSC / 30 FPS**
4. Premiere should auto-link because clip names match reel names!

### Step 3: Separate Camera 2 to Track 2
1. In the timeline, **right-click** on any clip
2. Choose `Select > Select All Instances`
3. Type "CAM2" to filter only Camera 2 clips
4. Select all CAM2 clips
5. **Drag them up to Video Track 2**

**Done!** You now have:
- Track V1: All Camera 1 footage
- Track V2: All Camera 2 footage
- All synced and silence removed

---

## Method 2: Using the CSV Reference (Most Control)

If Method 1 doesn't work, use the CSV as a manual guide:

### Step 1: Open the Reference
1. Open `results/premiere_edit_reference.csv` in Excel/Google Sheets
2. You'll see 785 rows with complete edit data

### Step 2: Build Timeline Manually
The CSV tells you exactly:
- Which camera (CAM1 or CAM2)
- Which track (V1 or V2)
- Source timecodes (where to cut from)
- Timeline position (where to place it)

You can manually place clips following this guide, or use it to verify an EDL import.

---

## Troubleshooting

### "Media offline" or manual linking required
**Solution**: You didn't pre-import and rename the files.
- Delete the sequence
- Follow Step 1 of Method 1 EXACTLY
- Reimport the EDL

### Clips all on one track
**Solution**: 
- Use `Edit > Select > Select All`
- In the Properties panel, look for "Source Name"
- Filter/sort by source
- Manually drag Camera 2 clips to V2

### Wrong sync / clips don't match
**Solution**: The sync offset is baked into the EDL
- Camera 1 uses original timecodes
- Camera 2 has 0.975s offset already applied
- If you see drift, the EDL import worked incorrectly

---

## Quick Reference

| File | Purpose | How to Use |
|------|---------|------------|
| `podcast_edit.edl` | Standard EDL | Import in Premiere (all clips on V1) |
| `podcast_edit_multitrack.edl` | EDL with track tags | Import in Premiere (hints for V1/V2) |
| `premiere_edit_reference.csv` | Complete breakdown | Open in Excel for manual editing |
| `camera1_short.mp4` | Source media | Rename to "CAM1" before EDL import |
| `camera2_short.mp4` | Source media | Rename to "CAM2" before EDL import |

---

## Expected Result

After following any method above, your timeline should have:

**Video Track 1 (V1)**: 394 clips from Camera 1  
**Video Track 2 (V2)**: 391 clips from Camera 2  
**Total Duration**: ~64 minutes (3,872 seconds)  
**All silence removed**  
**Perfect sync** (0.975s offset applied to Camera 2)

---

## Final Tips

1. **Save your project** immediately after successful import
2. **Color code** tracks: V1 = Blue, V2 = Green for easy visualization
3. **Lock audio tracks** if you don't want accidental edits
4. The CSV can be used to **verify any edit** if something looks wrong
5. If all else fails, the CSV has EVERY single edit detail - you can build it clip by clip

---

## Alternative: Try DaVinci Resolve

If Premiere continues to be problematic:
- Download DaVinci Resolve (FREE)
- Use `resolve_timeline_builder.py` 
- Get perfect automated results in 30 seconds

But I understand you want Premiere - this workflow should get you there!
