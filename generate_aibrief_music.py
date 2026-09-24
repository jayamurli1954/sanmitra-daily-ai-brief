import numpy as np
import scipy.io.wavfile as wav
import os

SAMPLE_RATE = 44100
DURATION = 320.0  # ~5m20s to easily cover the 4.5m briefing
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

t = np.linspace(0, DURATION, TOTAL_SAMPLES, endpoint=False)

# Modern Tech News Harmonization (F minor / Ab major)
# Rhythmic 116 BPM corporate pulse (0.517s per beat)
BEAT = 60.0 / 116.0
BAR = BEAT * 4

# Standard frequencies for all octaves
NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTES = {}
for octv in range(1, 7):
    for i, name in enumerate(NOTE_NAMES):
        midi = (octv + 1) * 12 + i
        freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        NOTES[f"{name}{octv}"] = round(freq, 2)

print("[*] Generating Bloomberg/CNBC style AI Brief music bed...")

left_ch = np.zeros(TOTAL_SAMPLES)
right_ch = np.zeros(TOTAL_SAMPLES)

# 1. Warm Analog Sub Pulse (F1 -> Db1/Db2 -> Ab1 -> Eb2 cycle every 4 bars = 8.27s)
chords = [
    ('F2', 'C3', 'Ab3', 'C4'),
    ('Db3', 'Ab3', 'C4', 'F4'),
    ('Ab2', 'Eb3', 'C4', 'Eb4'),
    ('Eb3', 'Bb3', 'Db4', 'G4')
]

cycle_dur = BAR * 4
num_cycles = int(DURATION / cycle_dur) + 1

for c in range(num_cycles):
    c_start = c * cycle_dur
    for chord_idx, chord in enumerate(chords):
        seg_start = c_start + chord_idx * BAR
        if seg_start >= DURATION:
            break
        n_samples = int(SAMPLE_RATE * BAR)
        t_l = np.linspace(0, BAR, n_samples, endpoint=False)
        
        # Soft sine/triangle pad chord
        pad = np.zeros(n_samples)
        for note in chord:
            freq = NOTES[note]
            pad += np.sin(2 * np.pi * freq * t_l) * 0.25 + np.sin(4 * np.pi * freq * t_l) * 0.05
        pad /= len(chord)
        
        # Smooth window envelope
        env = np.ones(n_samples)
        fade = int(0.4 * SAMPLE_RATE)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
        
        start_idx = int(seg_start * SAMPLE_RATE)
        end_idx = min(start_idx + n_samples, TOTAL_SAMPLES)
        length = end_idx - start_idx
        if length > 0:
            left_ch[start_idx:end_idx] += pad[:length] * env[:length] * 0.28
            right_ch[start_idx:end_idx] += pad[:length] * env[:length] * 0.28

# 2. Rhythmic Tech Ticker Pulses (Subtle 16th-note clock / arpeggio)
# Gives the broadcast that Reuters/Bloomberg constant forward momentum
step_dur = BEAT / 4.0 # 16th note
total_steps = int(DURATION / step_dur)

arp_notes = ['F4', 'Ab4', 'C5', 'Eb5', 'C5', 'Ab4', 'Bb4', 'C5']
for step in range(total_steps):
    step_time = step * step_dur
    if step_time >= DURATION:
        break
    note = arp_notes[step % len(arp_notes)]
    freq = NOTES[note]
    n_pulse = int(SAMPLE_RATE * 0.065)
    t_p = np.linspace(0, 0.065, n_pulse, endpoint=False)
    
    # Crisp soft blip
    pulse = np.sin(2 * np.pi * freq * t_p) * np.exp(-45.0 * t_p)
    
    # Pan alternating slightly
    pan = 0.5 + 0.2 * np.sin(step * 0.5)
    s_idx = int(step_time * SAMPLE_RATE)
    e_idx = min(s_idx + n_pulse, TOTAL_SAMPLES)
    l = e_idx - s_idx
    if l > 0:
        left_ch[s_idx:e_idx] += pulse[:l] * (1.0 - pan) * 0.12
        right_ch[s_idx:e_idx] += pulse[:l] * pan * 0.12

# 3. Low Bass Plucks on Beats 1 and 3
for b in range(int(DURATION / BEAT)):
    if b % 2 == 0:
        b_time = b * BEAT
        n_bass = int(SAMPLE_RATE * 0.25)
        t_b = np.linspace(0, 0.25, n_bass, endpoint=False)
        chord_num = int((b_time % (BAR * 4)) / BAR)
        root = ['F1', 'Db2', 'Ab1', 'Eb2'][chord_num % 4]
        freq = NOTES[root]
        bass = (np.sin(2 * np.pi * freq * t_b) + 0.3 * np.sin(4 * np.pi * freq * t_b)) * np.exp(-9.0 * t_b)
        
        s_idx = int(b_time * SAMPLE_RATE)
        e_idx = min(s_idx + n_bass, TOTAL_SAMPLES)
        l = e_idx - s_idx
        if l > 0:
            left_ch[s_idx:e_idx] += bass[:l] * 0.25
            right_ch[s_idx:e_idx] += bass[:l] * 0.25

# Normalize and convert to 16-bit PCM
peak = max(np.max(np.abs(left_ch)), np.max(np.abs(right_ch)))
if peak > 0:
    left_ch = (left_ch / peak) * 0.85
    right_ch = (right_ch / peak) * 0.85

stereo = np.column_stack((
    (left_ch * 32767).astype(np.int16),
    (right_ch * 32767).astype(np.int16)
))

out_path = "public/audio/aibrief_theme.wav"
wav.write(out_path, SAMPLE_RATE, stereo)
print(f"[+] AI Brief newsroom theme generated successfully: {out_path} ({os.path.getsize(out_path)} bytes)")
