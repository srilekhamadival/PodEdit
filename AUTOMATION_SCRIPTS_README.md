# Platform-Specific Timeline Builders

This folder contains professional automation scripts for both Premiere Pro and DaVinci Resolve.

## Files

- **`premiere_timeline_builder.jsx`** - Premiere Pro ExtendScript
- **`resolve_timeline_builder.py`** - DaVinci Resolve Python API script

Both scripts read the **same data files** (`edit_segments.json` and `sync_metrics.json`) and produce identical timelines.

---

## Using the Premiere Pro Script

### Requirements:
- Adobe Premiere Pro CC 2018 or later
- Generated files in `results/`:
  - `edit_segments.json`
  - `sync_metrics.json`
- Media files in `datasets/test_set_1/`:
  - `camera1_short.mp4`
  - `camera2_short.mp4`

### Steps:
1. Open Premiere Pro
2. Create a new project
3. Create a new sequence (30 fps)
4. Go to: `File > Scripts > Run Script File...`
5. Navigate to and select `premiere_timeline_builder.jsx`
6. When prompted, select `results/edit_segments.json`
7. Wait for the script to complete

### Result:
- **Track 1**: All Camera 1 clips
- **Track 2**: All Camera 2 clips
- Sync offset applied automatically
- All silences removed

---

## Using the DaVinci Resolve Script

### Requirements:
- DaVinci Resolve 16+ (Free or Studio)
- Python 3.6+
- Resolve's Python API configured
- Same data files as above

### Setup (First Time Only):

#### Windows:
```bash
# Set environment variable (adjust path if different)
setx RESOLVE_SCRIPT_API "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
```

#### macOS/Linux:
```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
```

### Steps:

#### Method 1: From Resolve's Console
1. Open DaVinci Resolve
2. Create or open a project
3. Go to: `Workspace > Console`
4. In the console, run:
```python
exec(open(r'C:\third year\sem 6\mini project\podedit\resolve_timeline_builder.py').read())
```
(Adjust path as needed)

#### Method 2: From Command Line
```bash
cd "C:\third year\sem 6\mini project\podedit"
python resolve_timeline_builder.py
```

### Result:
- **Track 1**: All Camera 1 clips
- **Track 2**: All Camera 2 clips
- Sync offset applied automatically
- All silences removed

---

## Troubleshooting

### Premiere Pro:

**"Script error: Cannot find function..."**
- Your Premiere version may be too old
- Update to CC 2018 or later

**"Media file not found"**
- Check that video files are in `datasets/test_set_1/`
- Ensure paths don't have special characters

### DaVinci Resolve:

**"DaVinci Resolve Python API not found"**
- Set the `RESOLVE_SCRIPT_API` environment variable
- Restart terminal/console after setting it

**"Could not connect to DaVinci Resolve"**
- Make sure Resolve is running before executing the script

**"No project is open"**
- Create or open a project in Resolve first

---

## What These Scripts Do

1. **Import media files** (camera1_short.mp4 and camera2_short.mp4)
2. **Read your edit decisions** from `edit_segments.json`
3. **Apply sync offset** from `sync_metrics.json` (0.975s in your case)
4. **Build timeline** with all cuts on separate tracks
5. **No manual linking needed** - everything is automated!

---

## Benefits Over XML/EDL

✅ **No import errors** - Uses native APIs  
✅ **No manual media linking** - Imports files automatically  
✅ **Separated tracks** - Camera 1 and 2 on different tracks  
✅ **Perfect sync** - Offset applied correctly  
✅ **Professional workflow** - How real post-production facilities work
