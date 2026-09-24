import numpy as np
import scipy.io.wavfile as wav
import os

SAMPLE_RATE = 44100
DURATION = 37.0  # 37 seconds to cover all 36s (1080 frames) + safe tail
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

t = np.linspace(0, DURATION, TOTAL_SAMPLES, endpoint=False)

# 120 BPM: 1 beat = 0.5s, 1 bar = 2.0s
BEAT = 0.5

# Frequencies in D minor
NOTES = {
    'D2': 73.42, 'F2': 87.31, 'G2': 98.00, 'A2': 110.00, 'Bb2': 116.54, 'C3': 130.81,
    'D3': 146.83, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'Bb3': 233.08, 'C4': 261.63,
    'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'Bb4': 466.16, 'C5': 523.25, 'D5': 587.33
}

def synth_note(freq, duration, phase=0.0):
    n_samples = int(SAMPLE_RATE * duration)
    t_local = np.linspace(0, duration, n_samples, endpoint=False)
    # Layer fundamental + harmonics (saw/pulse blend)
    sig = (
        0.5 * np.sin(2 * np.pi * freq * t_local + phase) +
        0.3 * np.sin(4 * np.pi * freq * t_local + phase * 1.5) +
        0.15 * np.sin(6 * np.pi * freq * t_local) +
        0.05 * np.sin(8 * np.pi * freq * t_local)
    )
    # Exponential decay envelope
    envelope = np.exp(-3.0 * t_local / duration)
    return sig * envelope

# Initialize stereo channels
left_ch = np.zeros(TOTAL_SAMPLES)
right_ch = np.zeros(TOTAL_SAMPLES)

# --- 1. Bassline & Root Progression ---
# Scene 1 (0-10s): D2 pulse
# Scene 2 (10-25s): D2 -> Bb2 -> C3 -> G2
# Scene 3 (25-36s): Bb2 -> C3 -> D2 -> D2
bass_notes = [
    # Scene 1: Dark tension
    (0.0, 2.0, 'D2'), (2.0, 2.0, 'D2'), (4.0, 2.0, 'D2'), (6.0, 2.0, 'D2'), (8.0, 2.0, 'D2'),
    # Scene 2: Uplifting progression
    (10.0, 3.5, 'D2'), (13.5, 3.5, 'Bb2'), (17.0, 3.5, 'C3'), (20.5, 4.5, 'D2'),
    # Scene 3: High energy CTA resolution
    (25.0, 2.75, 'Bb2'), (27.75, 2.75, 'C3'), (30.5, 3.0, 'D2'), (33.5, 3.5, 'D2')
]

for start_time, dur, note_name in bass_notes:
    freq = NOTES[note_name]
    start_idx = int(start_time * SAMPLE_RATE)
    end_idx = min(start_idx + int(dur * SAMPLE_RATE), TOTAL_SAMPLES)
    length = end_idx - start_idx
    if length <= 0:
        continue
    t_seg = np.linspace(0, dur, length, endpoint=False)
    # Rich sub + warm analog bass
    bass_sig = 0.45 * np.sin(2 * np.pi * freq * t_seg) + 0.25 * np.sin(4 * np.pi * freq * t_seg)
    # Soft attack and release
    env = np.ones(length)
    fade_len = int(0.08 * SAMPLE_RATE)
    if length > 2 * fade_len:
        env[:fade_len] = np.linspace(0, 1, fade_len)
        env[-fade_len:] = np.linspace(1, 0, fade_len)
    left_ch[start_idx:end_idx] += bass_sig * env * 0.75
    right_ch[start_idx:end_idx] += bass_sig * env * 0.75

# --- 2. Ambient Pad Chords (Wide Stereo Warmth) ---
pads = [
    # Scene 1: Dm (D3, F3, A3)
    (0.0, 9.5, [NOTES['D3'], NOTES['F3'], NOTES['A3']], 0.38),
    # Scene 2: Dm -> Bb -> C -> Dm
    (10.0, 4.0, [NOTES['D3'], NOTES['F3'], NOTES['A3']], 0.45),
    (14.0, 4.0, [NOTES['Bb2'], NOTES['D3'], NOTES['F3']], 0.45),
    (18.0, 3.5, [NOTES['C3'], NOTES['E4'], NOTES['G3']], 0.45),
    (21.5, 3.5, [NOTES['D3'], NOTES['F3'], NOTES['A3']], 0.45),
    # Scene 3: Energy lift Bb -> C -> Dm -> Dm
    (25.0, 3.0, [NOTES['Bb3'], NOTES['D4'], NOTES['F4']], 0.50),
    (28.0, 3.0, [NOTES['C4'], NOTES['E4'], NOTES['G4']], 0.50),
    (31.0, 5.5, [NOTES['D4'], NOTES['F4'], NOTES['A4']], 0.50),
]

for start_time, dur, chord, vol in pads:
    start_idx = int(start_time * SAMPLE_RATE)
    end_idx = min(start_idx + int(dur * SAMPLE_RATE), TOTAL_SAMPLES)
    length = end_idx - start_idx
    if length <= 0:
        continue
    t_seg = np.linspace(0, dur, length, endpoint=False)
    chord_l = np.zeros(length)
    chord_r = np.zeros(length)
    for f in chord:
        # Detune for stereo chorus width
        chord_l += np.sin(2 * np.pi * (f - 0.4) * t_seg) + 0.3 * np.sin(4 * np.pi * f * t_seg)
        chord_r += np.sin(2 * np.pi * (f + 0.4) * t_seg) + 0.3 * np.sin(4 * np.pi * f * t_seg)
    chord_l /= len(chord)
    chord_r /= len(chord)
    # Smooth pad fade
    env = np.ones(length)
    fade_len = int(0.35 * SAMPLE_RATE)
    if length > 2 * fade_len:
        env[:fade_len] = np.linspace(0, 1, fade_len)
        env[-fade_len:] = np.linspace(1, 0, fade_len)
    left_ch[start_idx:end_idx] += chord_l * env * vol
    right_ch[start_idx:end_idx] += chord_r * env * vol

# --- 3. Kinetic Arpeggio (16th notes: 0.125s each) ---
arp_notes_s1 = [NOTES['D4'], NOTES['F4'], NOTES['A4'], NOTES['C5'], NOTES['A4'], NOTES['F4'], NOTES['D4'], NOTES['F4']]
arp_notes_s2 = [NOTES['D4'], NOTES['A4'], NOTES['D5'], NOTES['A4'], NOTES['F4'], NOTES['C5'], NOTES['D5'], NOTES['A4']]
arp_notes_s3 = [NOTES['D4'], NOTES['F4'], NOTES['A4'], NOTES['D5'], NOTES['C5'], NOTES['A4'], NOTES['D5'], NOTES['F4']]

def add_arpeggio(start_t, end_t, note_pattern, base_vol):
    step = 0.125
    curr = start_t
    idx = 0
    while curr < end_t:
        note_freq = note_pattern[idx % len(note_pattern)]
        note_sig = synth_note(note_freq, 0.18, phase=idx * 0.5)
        n_len = len(note_sig)
        s_idx = int(curr * SAMPLE_RATE)
        e_idx = min(s_idx + n_len, TOTAL_SAMPLES)
        actual_len = e_idx - s_idx
        if actual_len > 0:
            pan = 0.5 + 0.35 * np.sin(idx * 0.7)  # Dynamic stereo panning
            left_ch[s_idx:e_idx] += note_sig[:actual_len] * (1.0 - pan) * base_vol
            right_ch[s_idx:e_idx] += note_sig[:actual_len] * pan * base_vol
        curr += step
        idx += 1

# Scene 1 subtle tension arp
add_arpeggio(0.5, 8.0, arp_notes_s1, 0.28)
# Scene 2 driving tech arp
add_arpeggio(10.2, 24.8, arp_notes_s2, 0.38)
# Scene 3 triumphant CTA arp
add_arpeggio(25.2, 35.0, arp_notes_s3, 0.42)

# --- 4. Electronic Kick & Percussion Pulse (Scene 2 & 3) ---
def add_kick(time_s):
    dur = 0.18
    s_idx = int(time_s * SAMPLE_RATE)
    e_idx = min(s_idx + int(dur * SAMPLE_RATE), TOTAL_SAMPLES)
    length = e_idx - s_idx
    if length <= 0:
        return
    t_k = np.linspace(0, dur, length, endpoint=False)
    # Pitch drop from 140Hz to 45Hz
    freq_drop = 140.0 * np.exp(-28.0 * t_k) + 45.0
    kick_sig = np.sin(2 * np.pi * freq_drop * t_k) * np.exp(-14.0 * t_k)
    left_ch[s_idx:e_idx] += kick_sig * 0.65
    right_ch[s_idx:e_idx] += kick_sig * 0.65

# Electronic pulse kicks at 120 BPM in Scene 2 & Scene 3
for b_time in np.arange(10.0, 35.5, 0.5):
    add_kick(b_time)

# --- 5. Scene 1 Crash SFX (Down-pitch Glitch Sweep around 8.2s - 9.8s) ---
crash_start = int(8.2 * SAMPLE_RATE)
crash_len = int(1.4 * SAMPLE_RATE)
t_c = np.linspace(0, 1.4, crash_len, endpoint=False)
crash_freq = 400.0 * np.exp(-4.5 * t_c)
crash_noise = np.random.uniform(-0.15, 0.15, crash_len) * np.exp(-3.0 * t_c)
crash_sig = (np.sin(2 * np.pi * crash_freq * t_c) * 0.3 + crash_noise) * np.exp(-2.5 * t_c)
left_ch[crash_start:crash_start+crash_len] += crash_sig * 0.6
right_ch[crash_start:crash_start+crash_len] += crash_sig * 0.6

# --- 6. Warm Saturation & Master Limiting ---
# Soft analog-style tanh saturation for warmth and volume density
left_ch = np.tanh(left_ch * 1.5)
right_ch = np.tanh(right_ch * 1.5)

# Overall fade-in (first 0.6s) and fade-out (last 2.0s)
master_env = np.ones(TOTAL_SAMPLES)
fade_in_s = int(0.6 * SAMPLE_RATE)
fade_out_s = int(2.0 * SAMPLE_RATE)
master_env[:fade_in_s] = np.linspace(0, 1, fade_in_s)
master_env[-fade_out_s:] = np.linspace(1, 0, fade_out_s) ** 2

left_ch *= master_env
right_ch *= master_env

# Normalize peak to 0.95 for maximum clean headroom and loudness
peak = max(np.max(np.abs(left_ch)), np.max(np.abs(right_ch)))
if peak > 0:
    left_ch = (left_ch / peak) * 0.95
    right_ch = (right_ch / peak) * 0.95

# Convert to 16-bit PCM WAV
stereo_pcm = np.vstack((left_ch, right_ch)).T
stereo_int16 = (stereo_pcm * 32767).astype(np.int16)

out_file = os.path.join("public", "audio", "bg_music.wav")
wav.write(out_file, SAMPLE_RATE, stereo_int16)
print(f"Generated {out_file} - Duration: {DURATION}s, SampleRate: {SAMPLE_RATE}Hz")
