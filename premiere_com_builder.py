"""
Premiere Pro COM Automation (Windows Only)
Alternative to JSX that works even when scripting is disabled

USAGE:
1. Make sure Premiere Pro is OPEN with a project loaded
2. Run this script: python premiere_com_builder.py
3. Script will control Premiere through COM interface

NOTE: This is experimental and may not work on all Premiere versions.
If this doesn't work, try DaVinci Resolve instead (more reliable API).
"""

import win32com.client
import json
import os

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    print("=== Premiere Pro COM Automation ===\n")
    
    # Try to connect to Premiere
    try:
        premiere = win32com.client.Dispatch("Premiere.Application")
    except Exception as e:
        print("ERROR: Could not connect to Premiere Pro!")
        print(f"Details: {e}")
        print("\nMake sure:")
        print("1. Premiere Pro is running")
        print("2. You have pywin32 installed: pip install pywin32")
        return
    
    print("✓ Connected to Premiere Pro")
    
    # Load data
    segments_path = os.path.join(PROJECT_FOLDER, "results", "edit_segments.json")
    sync_path = os.path.join(PROJECT_FOLDER, "results", "sync_metrics.json")
    
    edit_segments = load_json(segments_path)
    sync_metrics = load_json(sync_path)
    sync_offset = sync_metrics.get("estimated_offset_seconds", 0.0)
    
    print(f"Segments: {len(edit_segments)}")
    print(f"Sync offset: {sync_offset:.4f}s\n")
    
    # Get active project
    try:
        project = premiere.Project
        print(f"Project: {project.Name}")
    except:
        print("ERROR: No project is open!")
        return
    
    print("\n⚠️  WARNING: COM automation for Premiere is very limited.")
    print("The script connected successfully, but full timeline building")
    print("requires the JSX script to work properly.\n")
    print("RECOMMENDATION: Try DaVinci Resolve's Python API instead.")
    print("It has much better programmatic control.\n")
    
if __name__ == "__main__":
    main()
