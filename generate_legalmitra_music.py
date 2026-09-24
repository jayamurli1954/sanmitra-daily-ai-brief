import numpy as np
import scipy.io.wavfile as wav
import os

SAMPLE_RATE = 44100
DURATION = 39.0
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

t = np.linspace(0, DURATION, TOTAL_SAMPLES, endpoint=False)

# Notes frequencies (D minor / F major legal cinematic palette)
NOTES = {
    'D2': 73.42, 'F2': 87.31, 'G2': 98.00, 'A2': 110.00, 'Bb2': 116.54, 'C3': 130.81,
    'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'Bb3': 233.08, 'C4': 261.63,
    'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'C5': 523.25, 'D5': 587.33
}

def piano_note(freq, duration):
    n = int(SAMPLE_RATE * duration)
    t_local = np.linspace(0, duration, n, endpoint=False)
    # Piano harmonics blend
    sig = (
        0.55 * np.sin(2 * np.pi * freq * t_local) +
        0.28 * np.sin(4 * np.pi * freq * t_local) +
        0.12 * np.sin(6 * np.pi * freq * t_local) +
        0.05 * np.sin(8 * np.pi * freq * t_local)
    )
    # Acoustic piano strike envelope
    envelope = np.exp(-2.2 * t_local / duration)
    return sig * envelope

left_ch = np.zeros(TOTAL_SAMPLES)
right_ch = np.zeros(TOTAL_SAMPLES)

# --- 1. Orchestral Cello & Strings Drone (Warm, Trustworthy Bed) ---
strings_chords = [
    # Scene 1: Dm (D3, F3, A3)
    (0.0, 7.0, [NOTES['D3'], NOTES['F3'], NOTES['A3']], 0.40),
    # Scene 2: Dm -> Bb -> C -> Dm
    (7.0, 3.5, [NOTES['D3'], NOTES['F3'], NOTES['A3']], 0.45),
    (10.5, 3.5, [NOTES['Bb2'], NOTES['D3'], NOTES['F3']], 0.45),
    (14.0, 3.5, [NOTES['C3'], NOTES['E3'], NOTES['G3']], 0.45),
    # Scene 3: Workflow momentum F -> C -> Dm
    (17.5, 3.5, [NOTES['F3'], NOTES['A3'], NOTES['C4']], 0.48),
    (21.0, 3.5, [NOTES['C3'], NOTES['E3'], NOTES['G3']], 0.48),
    (24.5, 3.5, [NOTES['D3'], NOTES['F3'], NOTES['A3']], 0.48),
    # Scene 4: Uplifting CTA Bb -> C -> Dm
    (28.0, 3.5, [NOTES['Bb2'], NOTES['D3'], NOTES['F3']], 0.52),
    (31.5, 3.5, [NOTES['C3'], NOTES['E3'], NOTES['G3']], 0.52),
    (35.0, 4.0, [NOTES['D3'], NOTES['F3'], NOTES['A3']], 0.52),
]

for start_t, dur, chord, vol in strings_chords:
    s_idx = int(start_t * SAMPLE_RATE)
    e_idx = min(s_idx + int(dur * SAMPLE_RATE), TOTAL_SAMPLES)
    length = e_idx - s_idx
    if length <= 0:
        continue
    t_seg = np.linspace(0, dur, length, endpoint=False)
    l_sig = np.zeros(length)
    r_sig = np.zeros(length)
    for f in chord:
        # String vibrato & detuned stereo width
        vib = 1.0 + 0.003 * np.sin(2 * np.pi * 5.0 * t_seg)
        l_sig += np.sin(2 * np.pi * (f * vib - 0.3) * t_seg) + 0.25 * np.sin(4 * np.pi * f * t_seg)
        r_sig += np.sin(2 * np.pi * (f * vib + 0.3) * t_seg) + 0.25 * np.sin(4 * np.pi * f * t_seg)
    l_sig /= len(chord)
    r_sig /= len(chord)
    env = np.ones(length)
    fade_len = int(0.25 * SAMPLE_RATE)
    if length > 2 * fade_len:
        env[:fade_len] = np.linspace(0, 1, fade_len)
        env[-fade_len:] = np.linspace(1, 0, fade_len)
    left_ch[s_idx:e_idx] += l_sig * env * vol
    right_ch[s_idx:e_idx] += r_sig * env * vol

# --- 2. Low Acoustic Piano Bass (Authoritative Root Notes) ---
piano_bass = [
    (0.0, 3.5, 'D2'), (3.5, 3.5, 'D2'),
    (7.0, 3.5, 'D2'), (10.5, 3.5, 'Bb2'), (14.0, 3.5, 'C3'),
    (17.5, 3.5, 'F2'), (21.0, 3.5, 'C3'), (24.5, 3.5, 'D2'),
    (28.0, 3.5, 'Bb2'), (31.5, 3.5, 'C3'), (35.0, 4.0, 'D2')
]

for start_t, dur, note in piano_bass:
    freq = NOTES[note]
    s_idx = int(start_t * SAMPLE_RATE)
    sig = piano_note(freq, dur)
    e_idx = min(s_idx + len(sig), TOTAL_SAMPLES)
    actual_len = e_idx - s_idx
    if actual_len > 0:
        left_ch[s_idx:e_idx] += sig[:actual_len] * 0.70
        right_ch[s_idx:e_idx] += sig[:actual_len] * 0.70

# --- 3. Classical Legal Piano Arpeggios (Refined & Prestigious) ---
piano_arp_pattern = [NOTES['D4'], NOTES['F4'], NOTES['A4'], NOTES['D5'], NOTES['A4'], NOTES['F4']]

def add_piano_arp(start_t, end_t, vol):
    step = 0.25  # 8th notes
    curr = start_t
    idx = 0
    while curr < end_t:
        f = piano_arp_pattern[idx % len(piano_arp_pattern)]
        sig = piano_note(f, 0.4)
        s_idx = int(curr * SAMPLE_RATE)
        e_idx = min(s_idx + len(sig), TOTAL_SAMPLES)
        act_len = e_idx - s_idx
        if act_len > 0:
            pan = 0.5 + 0.3 * np.sin(idx * 0.8)
            left_ch[s_idx:e_idx] += sig[:act_len] * (1.0 - pan) * vol
            right_ch[s_idx:e_idx] += sig[:act_len] * pan * vol
        curr += step
        idx += 1

add_piano_arp(0.5, 6.8, 0.32)
add_piano_arp(7.2, 27.5, 0.40)
add_piano_arp(27.8, 37.0, 0.45)

# --- 4. Subtle Cinematic Pulse Kick (Scenes 2, 3, 4) ---
for bt in np.arange(7.0, 37.0, 0.5):
    s_idx = int(bt * SAMPLE_RATE)
    dur = 0.15
    e_idx = min(s_idx + int(dur * SAMPLE_RATE), TOTAL_SAMPLES)
    length = e_idx - s_idx
    if length > 0:
        t_k = np.linspace(0, dur, length, endpoint=False)
        kick = np.sin(2 * np.pi * (110.0 * np.exp(-22.0 * t_k) + 40.0) * t_k) * np.exp(-12.0 * t_k)
        left_ch[s_idx:e_idx] += kick * 0.55
        right_ch[s_idx:e_idx] += kick * 0.55

# --- 5. Saturation & Master Limiting ---
left_ch = np.tanh(left_ch * 1.4)
right_ch = np.tanh(right_ch * 1.4)

# Master Fade
fade_in_len = int(0.5 * SAMPLE_RATE)
fade_out_len = int(2.0 * SAMPLE_RATE)
master_env = np.ones(TOTAL_SAMPLES)
master_env[:fade_in_len] = np.linspace(0, 1, fade_in_len)
master_env[-fade_out_len:] = np.linspace(1, 0, fade_out_len) ** 2

left_ch *= master_env
right_ch *= master_env

peak = max(np.max(np.abs(left_ch)), np.max(np.abs(right_ch)))
if peak > 0:
    left_ch = (left_ch / peak) * 0.94
    right_ch = (right_ch / peak) * 0.94

stereo_pcm = np.vstack((left_ch, right_ch)).T
stereo_int16 = (stereo_pcm * 32767).astype(np.int16)

out_file = os.path.join("public", "audio", "legalmitra_score.wav")
wav.write(out_file, SAMPLE_RATE, stereo_int16)
print(f"Generated {out_file} - Duration: {DURATION}s")
