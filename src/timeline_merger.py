# timeline_merger.py
# Purpose: Combine keep segments (non-silent) with speaker timeline
# to produce final edit segments with camera decisions.

import json
import os
from copy import deepcopy

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def merge_keep_and_speaker(
    keep_segments,
    speaker_segments,
    default_camera=1
):
    """
    keep_segments: list of {start, end, duration}
    speaker_segments: list of {start, end, active_speaker} with 0/1/2
    returns: list of {start, end, duration, active_speaker, camera}
    """
    merged = []
    last_camera = default_camera

    for keep in keep_segments:
        ks = keep["start"]
        ke = keep["end"]

        # Find speaker segments that overlap this keep interval
        overlapping = []
        for sp in speaker_segments:
            ss = sp["start"]
            se = sp["end"]
            # Check overlap
            if se <= ks or ss >= ke:
                continue
            # Overlap exists
            overlap_start = max(ks, ss)
            overlap_end = min(ke, se)
            overlapping.append({
                "start": overlap_start,
                "end": overlap_end,
                "active_speaker": sp["active_speaker"]
            })

        # If no overlapping speaker info, keep as default camera
        if not overlapping:
            merged.append({
                "start": ks,
                "end": ke,
                "duration": ke - ks,
                "active_speaker": 0,
                "camera": last_camera
            })
            continue

        # Ensure overlapping covers entire keep interval [ks, ke]
        overlapping.sort(key=lambda x: x["start"])

        # Lead gap
        if overlapping[0]["start"] > ks:
            overlapping.insert(0, {
                "start": ks,
                "end": overlapping[0]["start"],
                "active_speaker": 0
            })

        # Tail gap
        if overlapping[-1]["end"] < ke:
            overlapping.append({
                "start": overlapping[-1]["end"],
                "end": ke,
                "active_speaker": 0
            })

        # Now overlapping covers [ks, ke] without gaps
        for sp in overlapping:
            seg_start = sp["start"]
            seg_end = sp["end"]
            speaker = sp["active_speaker"]

            if speaker == 1:
                camera = 1
            elif speaker == 2:
                camera = 2
            else:
                # NONE or ambiguous: stick with last used camera
                camera = last_camera

            merged.append({
                "start": seg_start,
                "end": seg_end,
                "duration": seg_end - seg_start,
                "active_speaker": int(speaker),
                "camera": int(camera)
            })
            last_camera = camera

    # Optional: merge adjacent segments with same camera to reduce cuts
    merged = merge_adjacent_same_camera(merged)
    return merged

def merge_adjacent_same_camera(segments, time_tolerance=1e-3):
    """
    Combine consecutive segments if they have same camera and are contiguous.
    """
    if not segments:
        return []

    segments = sorted(segments, key=lambda x: x["start"])
    merged = [deepcopy(segments[0])]

    for seg in segments[1:]:
        last = merged[-1]
        if (
            abs(seg["start"] - last["end"]) <= time_tolerance
            and seg["camera"] == last["camera"]
        ):
            # Extend last segment
            last["end"] = seg["end"]
            last["duration"] = last["end"] - last["start"]
        else:
            merged.append(deepcopy(seg))

    return merged

def main_test():
    keep_path = "results/keep_segments.json"
    if not os.path.exists(keep_path):
        print("❌ keep_segments.json not found. Please run silence_detector.py first.")
        return

    keep_segments = load_json(keep_path)

    speaker_path = "results/speaker_timeline.json"
    if not os.path.exists(speaker_path):
        print("❌ speaker_timeline.json not found. Please run speaker_detector.py.")
        return

    speaker_segments = load_json(speaker_path)

    # Merge
    final_segments = merge_keep_and_speaker(keep_segments, speaker_segments, default_camera=1)

    # Save
    out_path = "results/edit_segments.json"
    with open(out_path, "w") as f:
        json.dump(final_segments, f, indent=2)

    print(f"✅ Merged edit segments saved to {out_path}")
    print("First 10 segments:")
    for seg in final_segments[:10]:
        print(f"{seg['start']:.2f} -> {seg['end']:.2f} | cam {seg['camera']} | spk {seg['active_speaker']}")

if __name__ == "__main__":
    main_test()
