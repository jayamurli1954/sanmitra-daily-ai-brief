import numpy as np
import scipy.io.wavfile as wav
import os

SAMPLE_RATE = 44100
DURATION = 125.0
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

t = np.linspace(0, DURATION, TOTAL_SAMPLES, endpoint=False)

# Frequencies (C minor / Eb major / Ab modern corporate palette)
NOTES = {
    'C2': 65.41, 'D2': 73.42, 'Eb2': 77.78, 'F2': 87.31, 'G2': 98.00, 'Ab2': 103.83, 'Bb2': 116.54,
    'C3': 130.81, 'D3': 146.83, 'Eb3': 155.56, 'F3': 174.61, 'G3': 196.00, 'Ab3': 207.65, 'Bb3': 233.08,
    'C4': 261.63, 'D4': 293.66, 'Eb4': 311.13, 'F4': 349.23, 'G4': 392.00, 'Ab4': 415.30, 'Bb4': 466.16,
    'C5': 523.25, 'D5': 587.33, 'Eb5': 622.25, 'F5': 698.46, 'G5': 783.99, 'Ab5': 830.61, 'C6': 1046.50
}

left_ch = np.zeros(TOTAL_SAMPLES)
right_ch = np.zeros(TOTAL_SAMPLES)

def synth_bell(freq, duration):
    n = int(SAMPLE_RATE * duration)
    t_l = np.linspace(0, duration, n, endpoint=False)
    sig = (
        0.55 * np.sin(2 * np.pi * freq * t_l) +
        0.25 * np.sin(4 * np.pi * freq * t_l) +
        0.15 * np.sin(6 * np.pi * freq * t_l) +
        0.05 * np.sin(8 * np.pi * freq * t_l)
    )
    env = np.exp(-3.5 * t_l / duration)
    return sig * env

def synth_pad_chord(chord_notes, dur, vol, filter_mod=1.0):
    n = int(SAMPLE_RATE * dur)
    t_l = np.linspace(0, dur, n, endpoint=False)
    l_sig = np.zeros(n)
    r_sig = np.zeros(n)
    for i, note in enumerate(chord_notes):
        freq = NOTES[note]
        chorus_l = 1.0 + 0.002 * np.sin(2 * np.pi * 3.1 * t_l + i)
        chorus_r = 1.0 + 0.002 * np.cos(2 * np.pi * 3.7 * t_l + i)
        saw_sub_l = np.sin(2 * np.pi * freq * chorus_l * t_l) + 0.3 * np.sin(4 * np.pi * freq * t_l)
        saw_sub_r = np.sin(2 * np.pi * freq * chorus_r * t_l) + 0.3 * np.sin(4 * np.pi * freq * t_l)
        l_sig += saw_sub_l
        r_sig += saw_sub_r
    l_sig /= len(chord_notes)
    r_sig /= len(chord_notes)
    env = np.ones(n)
    fade = min(int(0.6 * SAMPLE_RATE), n // 4)
    if fade > 0:
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
    return l_sig * env * vol, r_sig * env * vol

# --- 1. Chords Structure across 120s ---
# Prologue & Act 1 (0-20s): Cm, Ab, Fm, G
# Act 2 (20-54s): Cm, Eb, Ab, Bb
# Act 3 (54-85s): Cm, Ab, Eb, Bb (Accounting Factory energy)
# Act 4 (85-120s): Ab, Bb, Cm, Eb, Ab, Bb, C (Triumphant Resolve)
chord_progression = [
    # Act 1 (Tense, dark problem)
    (0.0, 6.0, ['C3', 'Eb3', 'G3'], 0.28),
    (6.0, 6.0, ['Ab2', 'C3', 'Eb3'], 0.30),
    (12.0, 4.0, ['F2', 'Ab2', 'C3'], 0.32),
    (16.0, 4.0, ['G2', 'Bb2', 'D3'], 0.34),
    # Act 2 (OfficeMitra & Intake reveal)
    (20.0, 7.0, ['C3', 'Eb3', 'G3', 'C4'], 0.38),
    (27.0, 7.0, ['Ab2', 'C3', 'Eb3', 'Ab3'], 0.40),
    (34.0, 7.0, ['Eb3', 'G3', 'Bb3', 'Eb4'], 0.42),
    (41.0, 6.0, ['Bb2', 'D3', 'F3', 'Bb3'], 0.42),
    (47.0, 7.0, ['C3', 'Eb3', 'G3', 'Bb3'], 0.45),
    # Act 3 (The Accounting Factory & SSDV Engine)
    (54.0, 7.5, ['C3', 'Eb3', 'G3', 'C4'], 0.48),
    (61.5, 7.5, ['Ab2', 'C3', 'Eb3', 'Ab3'], 0.50),
    (69.0, 8.0, ['Eb3', 'G3', 'Bb3', 'Eb4'], 0.50),
    (77.0, 8.0, ['Bb2', 'D3', 'F3', 'Bb3'], 0.52),
    # Act 4 (Advisory, Command Center, Scale, Finale)
    (85.0, 7.0, ['Ab2', 'C3', 'Eb3', 'C4'], 0.52),
    (92.0, 7.0, ['Bb2', 'D3', 'F3', 'D4'], 0.54),
    (99.0, 7.0, ['C3', 'Eb3', 'G3', 'Eb4'], 0.56),
    (106.0, 7.0, ['Ab2', 'C3', 'Eb3', 'Ab3'], 0.58),
    (113.0, 7.0, ['C3', 'Eb3', 'G3', 'C5'], 0.60),
]

for start_t, dur, chord, vol in chord_progression:
    s_idx = int(start_t * SAMPLE_RATE)
    e_idx = min(s_idx + int(dur * SAMPLE_RATE), TOTAL_SAMPLES)
    actual_len = e_idx - s_idx
    if actual_len <= 0:
        continue
    l_pad, r_pad = synth_pad_chord(chord, dur, vol)
    left_ch[s_idx:e_idx] += l_pad[:actual_len]
    right_ch[s_idx:e_idx] += r_pad[:actual_len]

# --- 2. Futuristic Digital Arpeggiator (Acts 2, 3, 4: 20s to 118s) ---
arp_notes = [NOTES['C4'], NOTES['Eb4'], NOTES['G4'], NOTES['Bb4'], NOTES['C5'], NOTES['G4'], NOTES['Eb4'], NOTES['D4']]
arp_step = 0.20  # 150 BPM 8th note feel
curr_t = 20.0
step_idx = 0
while curr_t < 118.0:
    freq = arp_notes[step_idx % len(arp_notes)]
    # Filter/volume velocity based on section
    if curr_t < 54.0:
        v = 0.22
    elif curr_t < 85.0:
        v = 0.32  # Factory section punch
    else:
        v = 0.35  # Finale lift
    sig = synth_bell(freq, 0.25)
    s_idx = int(curr_t * SAMPLE_RATE)
    e_idx = min(s_idx + len(sig), TOTAL_SAMPLES)
    act_len = e_idx - s_idx
    if act_len > 0:
        pan = 0.5 + 0.35 * np.sin(step_idx * 0.7)
        left_ch[s_idx:e_idx] += sig[:act_len] * (1.0 - pan) * v
        right_ch[s_idx:e_idx] += sig[:act_len] * pan * v
    curr_t += arp_step
    step_idx += 1

# --- 3. Sub-Bass & Cinematic Kick Pulse (Starts at 20s, picks up at 54s) ---
beat_interval = 0.5  # 120 BPM tempo
for bt in np.arange(20.0, 117.0, beat_interval):
    s_idx = int(bt * SAMPLE_RATE)
    dur = 0.18
    e_idx = min(s_idx + int(dur * SAMPLE_RATE), TOTAL_SAMPLES)
    length = e_idx - s_idx
    if length > 0:
        t_k = np.linspace(0, dur, length, endpoint=False)
        kick_freq = 110.0 * np.exp(-26.0 * t_k) + 38.0
        # Louder during Accounting Factory (54s - 85s)
        vol_k = 0.55 if (54.0 <= bt <= 85.0) else 0.35
        kick = np.sin(2 * np.pi * kick_freq * t_k) * np.exp(-14.0 * t_k)
        left_ch[s_idx:e_idx] += kick * vol_k
        right_ch[s_idx:e_idx] += kick * vol_k

# --- 4. Sub-Bass Fundamental Drones ---
bass_timeline = [
    (20.0, 14.0, 'C2', 0.40),
    (34.0, 13.0, 'Ab2', 0.42),
    (47.0, 7.0, 'Bb2', 0.42),
    (54.0, 15.0, 'C2', 0.50),
    (69.0, 16.0, 'Eb2', 0.50),
    (85.0, 14.0, 'Ab2', 0.52),
    (99.0, 14.0, 'C2', 0.55),
    (113.0, 7.0, 'C2', 0.50),
]
for start_t, dur, note, vol in bass_timeline:
    s_idx = int(start_t * SAMPLE_RATE)
    e_idx = min(s_idx + int(dur * SAMPLE_RATE), TOTAL_SAMPLES)
    length = e_idx - s_idx
    if length > 0:
        t_b = np.linspace(0, dur, length, endpoint=False)
        freq = NOTES[note]
        sub = np.sin(2 * np.pi * freq * t_b) + 0.25 * np.sin(2 * np.pi * freq * 2 * t_b)
        env = np.ones(length)
        f_len = int(0.2 * SAMPLE_RATE)
        if length > 2 * f_len:
            env[:f_len] = np.linspace(0, 1, f_len)
            env[-f_len:] = np.linspace(1, 0, f_len)
        left_ch[s_idx:e_idx] += sub * env * vol
        right_ch[s_idx:e_idx] += sub * env * vol

# --- 5. Soft Mastering Limiter & Dynamic Range Fade ---
left_ch = np.tanh(left_ch * 1.3)
right_ch = np.tanh(right_ch * 1.3)

fade_in_len = int(1.0 * SAMPLE_RATE)
fade_out_len = int(3.5 * SAMPLE_RATE)
master_env = np.ones(TOTAL_SAMPLES)
master_env[:fade_in_len] = np.linspace(0, 1, fade_in_len)
master_env[-fade_out_len:] = np.linspace(1, 0, fade_out_len) ** 2

left_ch *= master_env
right_ch *= master_env

peak = max(np.max(np.abs(left_ch)), np.max(np.abs(right_ch)))
if peak > 0:
    left_ch = (left_ch / peak) * 0.92
    right_ch = (right_ch / peak) * 0.92

stereo_pcm = np.vstack((left_ch, right_ch)).T
stereo_int16 = (stereo_pcm * 32767).astype(np.int16)

out_file = os.path.join("public", "audio", "officemitra_theme.wav")
os.makedirs(os.path.dirname(out_file), exist_ok=True)
wav.write(out_file, SAMPLE_RATE, stereo_int16)
print(f"Generated {out_file} - Duration: {DURATION}s")
