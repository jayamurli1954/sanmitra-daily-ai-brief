import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pedalboard.io
    from src.aibrief import audio_mastering
except ImportError:  # pedalboard is not in every venv
    audio_mastering = None


def voice_like(sr=24000, seconds=6.0):
    """A 110 Hz harmonic buzz with syllable-rate and sentence-rate level swings."""
    t = np.arange(int(sr * seconds)) / sr
    tone = sum(np.sin(2 * np.pi * 110 * k * t) / k for k in range(1, 40))
    syllables = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 2.5 * t))
    sentences = np.where((t % 3.0) < 1.5, 1.0, 0.25)
    x = tone * syllables * sentences
    return (0.3 * x / np.abs(x).max()).astype(np.float32)[None, :]


@unittest.skipIf(audio_mastering is None, "pedalboard not installed")
class AudioMasteringTest(unittest.TestCase):
    def test_chain_is_warm_and_tames_the_top(self):
        names = [type(p).__name__ for p in audio_mastering.build_voice_chain()]
        self.assertEqual(names[:2], ["HighpassFilter", "LowShelfFilter"])
        self.assertEqual(names.count("Compressor"), 2)
        self.assertEqual(names[-1], "HighShelfFilter")
        self.assertLessEqual(audio_mastering.build_voice_chain()[0].cutoff_frequency_hz, 60)

    def test_master_hits_level_and_respects_ceiling(self):
        sr = 24000
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "in.mp3")
            with pedalboard.io.AudioFile(src, "w", sr, 1) as w:
                w.write(voice_like(sr))
            out = os.path.join(d, "out.mp3")
            self.assertTrue(audio_mastering.master_audio_file(src, out))
            with pedalboard.io.AudioFile(out) as r:
                y = r.read(r.frames)
        peak_db = 20 * np.log10(np.abs(y).max())
        rms_db = 20 * np.log10(np.sqrt(np.mean(y ** 2)))
        self.assertLessEqual(peak_db, audio_mastering.PEAK_CEILING_DB + 0.5)  # mp3 encode overshoot
        # Normalized to -17 dB RMS; Pedalboard's Limiter adds some make-up gain on top.
        self.assertGreater(rms_db, -18.0)
        self.assertLess(rms_db, -12.0)


if __name__ == "__main__":
    unittest.main()
