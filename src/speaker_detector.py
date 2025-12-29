# speaker_detector.py
# Purpose: Decide which speaker (and thus which camera) should be active over time
# based on two audio tracks (one per speaker).

import numpy as np
import json
import os
import time
from datetime import datetime
import librosa
import matplotlib.pyplot as plt

class SpeakerActivityAnalyzer:
    """
    Analyzes two audio tracks (speaker 1 & speaker 2) and produces
    a timeline of which speaker is active, with smoothing rules.
    """

    def __init__(
        self,
        sample_rate=44100,
        frame_length_ms=50,
        hop_length_ms=25,
        db_floor=-60.0,
        min_db_diff=6.0,
        min_activation_db=-40.0,
        min_switch_interval=2.0
    ):
        """
        sample_rate: must match audio
        frame_length_ms / hop_length_ms: analysis resolution
        db_floor: below this we consider it effectively silence[web:213]
        min_db_diff: how many dB louder one speaker must be to be "dominant"[web:219][web:221]
        min_activation_db: minimum dB to consider as speech (not noise)[web:213]
        min_switch_interval: minimum time between camera switches to avoid rapid cuts[web:221][web:226]
        """
        self.sample_rate = sample_rate
        self.frame_length = int(frame_length_ms * sample_rate / 1000)
        self.hop_length = int(hop_length_ms * sample_rate / 1000)
        self.db_floor = db_floor
        self.min_db_diff = min_db_diff
        self.min_activation_db = min_activation_db
        self.min_switch_interval = min_switch_interval

        self.metrics = {}
        self.timeline = []  # list of {start, end, active_speaker}

    def analyze(self, audio_spk1, audio_spk2, plot_debug=False):
        """
        Returns: list of segments: [{start, end, active_speaker}], where
        active_speaker ∈ {0, 1, 2}
        """
        start_time = time.time()

        # Ensure same length
        min_len = min(len(audio_spk1), len(audio_spk2))
        audio_spk1 = audio_spk1[:min_len]
        audio_spk2 = audio_spk2[:min_len]

        # Compute frame-wise RMS for both speakers
        rms1 = librosa.feature.rms(
            y=audio_spk1,
            frame_length=self.frame_length,
            hop_length=self.hop_length,
            center=True
        )[0]
        rms2 = librosa.feature.rms(
            y=audio_spk2,
            frame_length=self.frame_length,
            hop_length=self.hop_length,
            center=True
        )[0]

        eps = 1e-10
        db1 = 20 * np.log10(rms1 + eps)
        db2 = 20 * np.log10(rms2 + eps)

        frame_times = np.arange(len(db1)) * (self.hop_length / self.sample_rate)

        # Initial raw decision per frame
        raw_active = np.zeros(len(db1), dtype=int)  # 0: none/ambiguous, 1: spk1, 2: spk2

        for i in range(len(db1)):
            d1 = max(db1[i], self.db_floor)
            d2 = max(db2[i], self.db_floor)

            # If both are very quiet, mark as none
            if d1 < self.min_activation_db and d2 < self.min_activation_db:
                raw_active[i] = 0
                continue

            diff = d1 - d2

            if diff >= self.min_db_diff:
                raw_active[i] = 1
            elif diff <= -self.min_db_diff:
                raw_active[i] = 2
            else:
                # Too close, ambiguous (both talking or background)
                raw_active[i] = 0

        # Now smooth into segments with min_switch_interval constraint
        segments = []
        current_speaker = raw_active[0]
        seg_start_time = frame_times[0]

        last_switch_time = frame_times[0]

        for i in range(1, len(raw_active)):
            t = frame_times[i]
            spk = raw_active[i]

            if spk != current_speaker:
                # Potential switch: check min_switch_interval
                if (t - last_switch_time) >= self.min_switch_interval:
                    # End current segment
                    segments.append({
                        "start": float(seg_start_time),
                        "end": float(t),
                        "active_speaker": int(current_speaker)
                    })
                    # Start new segment
                    seg_start_time = t
                    current_speaker = spk
                    last_switch_time = t
                else:
                    # Ignore short fluctuation: keep current_speaker
                    continue

        # Close final segment
        segments.append({
            "start": float(seg_start_time),
            "end": float(frame_times[-1]),
            "active_speaker": int(current_speaker)
        })

        elapsed = time.time() - start_time

        self.timeline = segments
        self.metrics = {
            "sample_rate": self.sample_rate,
            "frame_length": self.frame_length,
            "hop_length": self.hop_length,
            "db_floor": self.db_floor,
            "min_db_diff": self.min_db_diff,
            "min_activation_db": self.min_activation_db,
            "min_switch_interval": self.min_switch_interval,
            "num_segments": len(segments),
            "processing_time_seconds": float(elapsed),
            "timestamp": datetime.now().isoformat()
        }

        print("\n=== SPEAKER ACTIVITY ANALYSIS ===")
        print(f"Segments: {len(segments)}")
        for seg in segments[:15]:  # limit print
            label = {0: "NONE", 1: "SPK1", 2: "SPK2"}.get(seg["active_speaker"], "UNK")
            print(f" {seg['start']:.2f} -> {seg['end']:.2f}: {label}")
        if len(segments) > 15:
            print(f" ... ({len(segments)-15} more segments)")

        if plot_debug:
            self._plot_debug(frame_times, db1, db2, raw_active)

        return segments

    def _plot_debug(self, frame_times, db1, db2, raw_active):
        os.makedirs("paper/figures", exist_ok=True)

        plt.figure(figsize=(10, 5))
        plt.plot(frame_times, db1, label="Speaker 1 (dB)")
        plt.plot(frame_times, db2, label="Speaker 2 (dB)")
        plt.axhline(self.min_activation_db, color="gray", linestyle="--", label="Activation threshold")
        plt.xlabel("Time (s)")
        plt.ylabel("Level (dB)")
        plt.title("Speaker Levels Over Time")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("paper/figures/speaker_levels.png", dpi=200)
        plt.close()

        # Simple visualization of active speaker over time
        plt.figure(figsize=(10, 2))
        plt.step(frame_times, raw_active, where="post")
        plt.yticks([0, 1, 2], ["NONE", "SPK1", "SPK2"])
        plt.xlabel("Time (s)")
        plt.ylabel("Active")
        plt.title("Raw Active Speaker per Frame")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("paper/figures/speaker_raw_active.png", dpi=200)
        plt.close()

        print("Saved speaker debug plots to paper/figures/")

    def save_results(self, output_dir="results"):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "speaker_timeline.json"), "w") as f:
            json.dump(self.timeline, f, indent=2)
        with open(os.path.join(output_dir, "speaker_metrics.json"), "w") as f:
            json.dump(self.metrics, f, indent=2)
        print(f"Speaker analysis saved in {output_dir}")


# Simple test harness
if __name__ == "__main__":
    # For now, assume you have two mono WAVs:
    #   camera1_audio.wav and camera2_audio.wav in results/
    # You can create those with FFmpeg or in Premiere.
    mic1_path = "results/camera1_audio.wav"
    mic2_path = "results/camera2_audio.wav"

    if not (os.path.exists(mic1_path) and os.path.exists(mic2_path)):
        print("❌ Please run audio_processor.py first to generate camera1_audio.wav and camera2_audio.wav.")
        exit()

    audio1, sr1 = librosa.load(mic1_path, sr=44100, mono=True)
    audio2, sr2 = librosa.load(mic2_path, sr=44100, mono=True)

    analyzer = SpeakerActivityAnalyzer(
        sample_rate=44100,
        frame_length_ms=50,
        hop_length_ms=25,
        db_floor=-60.0,
        min_db_diff=6.0,
        min_activation_db=-40.0,
        min_switch_interval=2.0
    )

    segments = analyzer.analyze(audio1, audio2, plot_debug=True)
    analyzer.save_results("results")
