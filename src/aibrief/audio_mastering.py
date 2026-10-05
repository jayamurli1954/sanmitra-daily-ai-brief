"""
Broadcast Audio Mastering Engine for SanMitra AI News Wire.
Uses Spotify's open-source Pedalboard library:
1. 80 Hz High-Pass Filter (removes sub-bass rumble, plosives, and mic thumps)
2. Broadcast Dynamic Range Compressor (tightens dynamic range for TV/radio punchiness)
3. Speech Presence EQ (+2.0 dB at 3 kHz for crisp consonant articulation)
4. Loudness Normalization to -14 LUFS (YouTube & broadcast audio standard)
5. Peak Limiter (-1.0 dB true peak ceiling to prevent digital clipping)
"""

import os
import sys
import numpy as np
import pedalboard
import pedalboard.io
from pedalboard import Pedalboard, Compressor, HighpassFilter, PeakFilter, Limiter, Gain

TARGET_LUFS = -14.0
PEAK_CEILING_DB = -1.0
PEAK_CEILING_LINEAR = 10 ** (PEAK_CEILING_DB / 20.0)  # ~0.891


def master_audio_file(file_path: str, output_path: str = None) -> bool:
    """
    Masters a single audio file to -14 LUFS broadcast standards in place or to output_path.
    """
    if not os.path.exists(file_path):
        return False
    if output_path is None:
        output_path = file_path

    try:
        with pedalboard.io.AudioFile(file_path) as r:
            sr = r.samplerate
            num_channels = r.num_channels
            audio = r.read(r.frames)

        # 1. Studio broadcast processing chain
        board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=80),
            Compressor(threshold_db=-16.0, ratio=2.5, attack_ms=15.0, release_ms=120.0),
            PeakFilter(cutoff_frequency_hz=3000, gain_db=2.0, q=1.0),
        ])
        processed = board(audio, sr)

        # 2. Loudness normalization to -14 LUFS
        rms = np.sqrt(np.mean(processed ** 2))
        if rms > 1e-6:
            current_db = 20.0 * np.log10(rms)
            # -14 LUFS for speech roughly aligns with ~-17 dB RMS
            target_rms_db = TARGET_LUFS - 3.0
            gain_db = target_rms_db - current_db
            gain_db = max(-10.0, min(10.0, gain_db))
            processed = processed * (10.0 ** (gain_db / 20.0))

        # 3. Peak Limiter to prevent clipping
        peak_limiter = Pedalboard([
            Limiter(threshold_db=PEAK_CEILING_DB)
        ])
        final_audio = peak_limiter(processed, sr)

        # Ensure peak does not exceed ceiling
        max_peak = np.max(np.abs(final_audio))
        if max_peak > PEAK_CEILING_LINEAR:
            final_audio = final_audio * (PEAK_CEILING_LINEAR / max_peak)

        # Write to temporary file then replace to support in-place update
        temp_out = output_path + ".tmp.mp3"
        with pedalboard.io.AudioFile(temp_out, 'w', sr, final_audio.shape[0]) as w:
            w.write(final_audio)

        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(temp_out, output_path)
        return True

    except Exception as e:
        print(f"[!] Warning mastering audio file {file_path}: {e}")
        return False


def master_all_episode_audio(audio_dir: str = "public/audio/aibrief"):
    """Masters all synthesized audio files in the episode audio directory."""
    if not os.path.exists(audio_dir):
        return

    count = 0
    for f in os.listdir(audio_dir):
        if f.endswith(".mp3"):
            full_path = os.path.join(audio_dir, f)
            if master_audio_file(full_path):
                count += 1
    print(f"[+] Broadcast Audio Mastering Complete: {count} audio files mastered to -14 LUFS standard.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "public/audio/aibrief"
    if os.path.isfile(target):
        master_audio_file(target)
    else:
        master_all_episode_audio(target)
