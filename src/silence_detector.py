# silence_detector.py
# Purpose: Detect long silence sections in an audio track
# We will use this to remove dead air in podcasts.

import numpy as np
import json
import os
import time
from datetime import datetime
import librosa
import matplotlib.pyplot as plt

class SilenceDetector:
    """
    Detects silence in an audio signal using frame-wise RMS analysis.
    """

    def __init__(
        self,
        sample_rate=44100,
        frame_length_ms=20,
        hop_length_ms=10,
        db_threshold=-40.0,
        min_silence_duration=1.5,
        padding=0.2
    ):
        """
        sample_rate: audio sample rate (must match previous modules)
        frame_length_ms: window size in ms for RMS calculation (e.g., 20ms)
        hop_length_ms: step between frames in ms (e.g., 10ms => 50% overlap)
        db_threshold: frames below this dB are considered silent
        min_silence_duration: minimum continuous silence length in seconds
        padding: extra seconds to keep before/after speech when we cut
        """
        self.sample_rate = sample_rate
        self.frame_length = int(frame_length_ms * sample_rate / 1000)
        self.hop_length = int(hop_length_ms * sample_rate / 1000)
        self.db_threshold = db_threshold
        self.min_silence_duration = min_silence_duration
        self.padding = padding

        self.metrics = {}
        self.detected_silence_segments = []

    def detect_silence(self, audio):
        """
        Main function: takes 1D numpy array `audio` and returns a list of
        silence segments: [{start, end, duration}, ...] in seconds.
        """
        start_time = time.time()

        # Compute frame-wise RMS (energy)
        rms = librosa.feature.rms(
            y=audio,
            frame_length=self.frame_length,
            hop_length=self.hop_length,
            center=True
        )[0]  # shape (n_frames,)

        # Convert RMS to dB (avoid log(0))
        eps = 1e-10
        rms_db = 20 * np.log10(rms + eps)

        # Determine which frames are "silent"
        silent_frames = rms_db < self.db_threshold

        # Convert frame indices to time
        frame_times = np.arange(len(rms)) * (self.hop_length / self.sample_rate)

        # Group consecutive silent frames into segments
        silence_segments = []
        in_silence = False
        silence_start_time = 0.0

        for i, is_silent in enumerate(silent_frames):
            t = frame_times[i]
            if is_silent and not in_silence:
                # We just entered a silent region
                in_silence = True
                silence_start_time = t
            elif not is_silent and in_silence:
                # We just left a silent region
                in_silence = False
                silence_end_time = t
                duration = silence_end_time - silence_start_time
                if duration >= self.min_silence_duration:
                    silence_segments.append({
                        "start": float(silence_start_time),
                        "end": float(silence_end_time),
                        "duration": float(duration)
                    })

        # Handle case: audio ends while still in silence
        if in_silence:
            silence_end_time = frame_times[-1]
            duration = silence_end_time - silence_start_time
            if duration >= self.min_silence_duration:
                silence_segments.append({
                    "start": float(silence_start_time),
                    "end": float(silence_end_time),
                    "duration": float(duration)
                })

        elapsed = time.time() - start_time

        self.detected_silence_segments = silence_segments
        self.metrics = {
            "sample_rate": self.sample_rate,
            "frame_length": self.frame_length,
            "hop_length": self.hop_length,
            "db_threshold": self.db_threshold,
            "min_silence_duration": self.min_silence_duration,
            "padding": self.padding,
            "num_silence_segments": len(silence_segments),
            "processing_time_seconds": float(elapsed),
            "timestamp": datetime.now().isoformat()
        }

        print("\n=== SILENCE DETECTION ===")
        print(f"Threshold: {self.db_threshold} dB")
        print(f"Min duration: {self.min_silence_duration:.2f} s")
        print(f"Detected segments: {len(silence_segments)}")
        for seg in silence_segments:
            print(f" - {seg['start']:.2f} -> {seg['end']:.2f} ({seg['duration']:.2f}s)")

        return silence_segments

    def get_keep_segments(self, audio_duration):
        """
        Convert silence segments into KEEP segments (non-silent parts).
        This is what we’ll feed into EDL generation later.

        We also apply padding around speech so cuts don’t feel too sudden.
        """
        if not self.detected_silence_segments:
            # No silence found: keep everything
            return [{
                "start": 0.0,
                "end": float(audio_duration),
                "duration": float(audio_duration)
            }]

        keep_segments = []
        current_start = 0.0

        for seg in self.detected_silence_segments:
            # End of the non-silent segment is just before silence, minus padding
            end_keep = max(current_start, seg["start"] - self.padding)
            if end_keep > current_start:
                keep_segments.append({
                    "start": float(current_start),
                    "end": float(end_keep),
                    "duration": float(end_keep - current_start)
                })
            # Next non-silent segment will start after silence + padding
            current_start = seg["end"] + self.padding

        # Tail segment after last silence
        if current_start < audio_duration:
            keep_segments.append({
                "start": float(current_start),
                "end": float(audio_duration),
                "duration": float(audio_duration - current_start)
            })

        print("\n=== KEEP SEGMENTS (Non-silent) ===")
        for seg in keep_segments:
            print(f"KEEP: {seg['start']:.2f} -> {seg['end']:.2f} ({seg['duration']:.2f}s)")

        return keep_segments

    def save_results(self, output_dir="results", keep_segments=None):
        """
        Save silence metrics, silence segments, and optionally keep_segments.
        """
        os.makedirs(output_dir, exist_ok=True)

        # Save detection metrics
        with open(os.path.join(output_dir, "silence_detection_metrics.json"), "w") as f:
            json.dump(self.metrics, f, indent=2)

        # Save silence segments
        with open(os.path.join(output_dir, "silence_segments.json"), "w") as f:
            json.dump(self.detected_silence_segments, f, indent=2)

        # Save keep segments if provided
        if keep_segments is not None:
            with open(os.path.join(output_dir, "keep_segments.json"), "w") as f:
                json.dump(keep_segments, f, indent=2)

        print(f"\nSilence metrics and segments saved in {output_dir}")

    def plot_rms_debug(self, audio, max_time=None):
        """
        Optional: visualize RMS and threshold for understanding (for your paper figures).
        """
        rms = librosa.feature.rms(
            y=audio,
            frame_length=self.frame_length,
            hop_length=self.hop_length,
            center=True
        )[0]
        eps = 1e-10
        rms_db = 20 * np.log10(rms + eps)
        frame_times = np.arange(len(rms)) * (self.hop_length / self.sample_rate)

        if max_time is not None:
            mask = frame_times <= max_time
            frame_times = frame_times[mask]
            rms_db = rms_db[mask]

        plt.figure(figsize=(10, 4))
        plt.plot(frame_times, rms_db, label="RMS (dB)")
        plt.axhline(self.db_threshold, color="red", linestyle="--", label="Threshold")
        plt.xlabel("Time (s)")
        plt.ylabel("RMS (dB)")
        plt.title("Frame-wise RMS and Silence Threshold")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        os.makedirs("paper/figures", exist_ok=True)
        plt.savefig("paper/figures/silence_rms_plot.png", dpi=200)
        plt.close()
        print("Saved RMS debug plot to paper/figures/silence_rms_plot.png")


# Simple test harness
if __name__ == "__main__":
    audio_path = "results/camera1_audio.wav"

    if not os.path.exists(audio_path):
        print("❌ Please run audio_processor.py first to generate camera1_audio.wav")
        exit()

    print("Loading audio for silence detection test...")
    audio, sr = librosa.load(audio_path, sr=44100, mono=True)

    detector = SilenceDetector(
        sample_rate=sr,
        db_threshold=-40.0,         # tweak based on your audio
        min_silence_duration=1.5,   # long pauses only
        padding=0.2
    )

    # 1) Detect silence
    silence_segments = detector.detect_silence(audio)

    # 2) Compute non-silent keep segments
    keep_segments = detector.get_keep_segments(audio_duration=len(audio) / sr)

    # 3) Save everything (metrics, silence, keep_segments)
    detector.save_results("results", keep_segments=keep_segments)

    # 4) Optional visualization
    detector.plot_rms_debug(audio, max_time=60)  # first 60s for visualization

    print("\n✅ Silence detection test completed.")
