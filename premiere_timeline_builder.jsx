/*
Premiere Pro Timeline Builder
Automatically creates a multi-cam timeline from edit_segments.json

USAGE:
1. Open Premiere Pro
2. Create a new project and sequence (30 fps)
3. File > Scripts > Run Script File
4. Select this file (premiere_timeline_builder.jsx)
5. When prompted, navigate to your project folder and select edit_segments.json

REQUIREMENTS:
- Premiere Pro CC 2018 or later
- edit_segments.json and sync_metrics.json in the same folder
- camera1_short.mp4 and camera2_short.mp4 in datasets/test_set_1/
*/

// ========================================
// CONFIGURATION
// ========================================
var FPS = 30;
var SEQUENCE_NAME = "Podcast Multi-Cam Edit";

// ========================================
// UTILITY FUNCTIONS
// ========================================

function readJSONFile(file) {
    if (!file.exists) {
        alert("File not found: " + file.fsName);
        return null;
    }
    
    file.open("r");
    var content = file.read();
    file.close();
    
    try {
        return eval("(" + content + ")");
    } catch(e) {
        alert("Error parsing JSON: " + e.toString());
        return null;
    }
}

function secondsToTicks(seconds) {
    // Premiere uses ticks (254016000000 ticks per second)
    return Math.floor(seconds * 254016000000);
}

function importMediaFile(filePath) {
    var file = new File(filePath);
    if (!file.exists) {
        alert("Media file not found: " + filePath);
        return null;
    }
    
    // Import file into project
    var success = app.project.importFiles([filePath], false, app.project.rootItem, false);
    
    if (success) {
        // Find the imported item
        for (var i = 0; i < app.project.rootItem.children.numItems; i++) {
            var item = app.project.rootItem.children[i];
            if (item.name === file.name) {
                return item;
            }
        }
    }
    
    return null;
}

// ========================================
// MAIN SCRIPT
// ========================================

function main() {
    // Check if a project is open
    if (!app.project) {
        alert("Please open a Premiere Pro project first.");
        return;
    }
    
    // Prompt user to select edit_segments.json
    var segmentsFile = File.openDialog("Select edit_segments.json");
    if (!segmentsFile) {
        return; // User cancelled
    }
    
    // Load edit segments
    var editSegments = readJSONFile(segmentsFile);
    if (!editSegments) return;
    
    // Load sync metrics (same folder as edit_segments.json)
    var syncFile = new File(segmentsFile.parent.fsName + "/sync_metrics.json");
    var syncMetrics = readJSONFile(syncFile);
    if (!syncMetrics) {
        alert("sync_metrics.json not found in the same folder!");
        return;
    }
    
    var syncOffset = syncMetrics.estimated_offset_seconds || 0.0;
    
    // Get project folder path
    var projectFolder = segmentsFile.parent.parent.fsName; // Go up to project root
    
    // Media file paths
    var cam1Path = projectFolder + "/datasets/test_set_1/camera1_short.mp4";
    var cam2Path = projectFolder + "/datasets/test_set_1/camera2_short.mp4";
    
    alert("Starting timeline build...\n\n" +
          "Segments: " + editSegments.length + "\n" +
          "Sync offset: " + syncOffset.toFixed(4) + "s\n" +
          "FPS: " + FPS);
    
    // Import media files
    $.writeln("Importing camera 1...");
    var cam1Clip = importMediaFile(cam1Path);
    if (!cam1Clip) return;
    
    $.writeln("Importing camera 2...");
    var cam2Clip = importMediaFile(cam2Path);
    if (!cam2Clip) return;
    
    // Create new sequence
    $.writeln("Creating sequence...");
    var sequence = app.project.createNewSequence(SEQUENCE_NAME, "preset-id-placeholder");
    
    if (!sequence) {
        // Try to use active sequence
        if (app.project.activeSequence) {
            sequence = app.project.activeSequence;
            sequence.name = SEQUENCE_NAME;
        } else {
            alert("Could not create sequence. Please create a 30fps sequence manually, then re-run this script.");
            return;
        }
    }
    
    // Get video tracks
    var videoTrack1 = sequence.videoTracks[0];
    var videoTrack2;
    
    // Add second track if it doesn't exist
    if (sequence.videoTracks.numTracks < 2) {
        sequence.videoTracks.addTrack();
    }
    videoTrack2 = sequence.videoTracks[1];
    
    $.writeln("Building timeline with " + editSegments.length + " segments...");
    
    // Track current timeline position (in ticks)
    var currentTimelineTicks = 0;
    
    // Process each segment
    for (var i = 0; i < editSegments.length; i++) {
        var seg = editSegments[i];
        var startMaster = seg.start;
        var duration = seg.duration;
        var camera = seg.camera;
        
        // Calculate source in/out (in ticks)
        var sourceIn, sourceOut;
        
        if (camera === 1) {
            sourceIn = secondsToTicks(startMaster);
            sourceOut = secondsToTicks(startMaster + duration);
        } else {
            // Apply sync offset for camera 2
            sourceIn = secondsToTicks(Math.max(0, startMaster - syncOffset));
            sourceOut = secondsToTicks(Math.max(0, startMaster + duration - syncOffset));
        }
        
        // Add clip to appropriate track
        var targetTrack = (camera === 1) ? videoTrack1 : videoTrack2;
        var sourceClip = (camera === 1) ? cam1Clip : cam2Clip;
        
        try {
            targetTrack.insertClip(sourceClip, currentTimelineTicks);
            
            // Get the just-inserted clip and set its in/out points
            var insertedClip = targetTrack.clips[targetTrack.clips.numItems - 1];
            insertedClip.inPoint = sourceIn;
            insertedClip.outPoint = sourceOut;
            
        } catch(e) {
            $.writeln("Warning: Failed to insert clip " + i + ": " + e.toString());
        }
        
        // Move timeline position forward
        currentTimelineTicks += secondsToTicks(duration);
        
        // Progress update
        if (i % 50 === 0) {
            $.writeln("Progress: " + i + "/" + editSegments.length);
        }
    }
    
    $.writeln("Timeline build complete!");
    alert("Timeline built successfully!\n\n" +
          "Track 1: Camera 1 clips\n" +
          "Track 2: Camera 2 clips\n" +
          "Total clips: " + editSegments.length);
}

// Run the script
try {
    main();
} catch(e) {
    alert("Script error: " + e.toString() + "\n\nLine: " + e.line);
}
