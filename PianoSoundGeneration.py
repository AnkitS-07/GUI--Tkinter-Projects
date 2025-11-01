import numpy as np
import sounddevice as sd
import soundfile as sf
import tkinter as tk
from tkinter import ttk
from functools import partial
from scipy.signal import fftconvolve
import threading
import os
from datetime import datetime

# 🎵 Piano Sound Engine

def adsr_envelope(t, attack=0.01, decay=0.1, sustain=0.7, release=0.2, duration=1.0):
    envelope = np.zeros_like(t)
    attack_samples = int(attack * len(t) / duration)
    decay_samples = int(decay * len(t) / duration)
    release_samples = int(release * len(t) / duration)
    sustain_samples = len(t) - (attack_samples + decay_samples + release_samples)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain, decay_samples)
    envelope[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = sustain
    envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
    return envelope

def piano_tone(frequency, duration=1.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = (
        1.0 * np.sin(2 * np.pi * frequency * t) +
        0.5 * np.sin(2 * np.pi * 2 * frequency * t) +
        0.3 * np.sin(2 * np.pi * 3 * frequency * t) +
        0.15 * np.sin(2 * np.pi * 4 * frequency * t)
    )
    envelope = adsr_envelope(t, attack=0.01, decay=0.15, sustain=0.6, release=0.3, duration=duration)
    wave *= envelope
    left = wave
    right = np.sin(2 * np.pi * (frequency * 1.005) * t) * envelope
    stereo_wave = np.vstack((left, right)).T
    stereo_wave /= np.max(np.abs(stereo_wave))
    return stereo_wave

def apply_reverb(signal, sample_rate=44100, decay=0.3):
    impulse_length = int(sample_rate * 0.3)
    impulse = np.logspace(0, -3, impulse_length)
    impulse *= decay
    reverb_signal = fftconvolve(signal, impulse[:, None], mode="full")[:len(signal)]
    reverb_signal /= np.max(np.abs(reverb_signal))
    return reverb_signal

# 🎧 Playback & Recording Controls

recorded_notes = []
is_recording = False
sample_rate = 44100

def note_freq(note):
    """Compute frequency for given note (e.g., 'C4', 'F#5')."""
    A4 = 440
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    n = notes.index(note[:-1])
    octave = int(note[-1])
    semitone_distance = n - 9 + (octave - 4) * 12
    return A4 * (2 ** (semitone_distance / 12))

def play_note(note, duration=1.0, highlight_btn=None):
    """Play the piano note asynchronously."""
    def _play():
        freq = note_freq(note)
        current_note_label.config(text=f"🎵 Playing: {note} ({freq:.2f} Hz)", fg="#00FFCC")
        wave = piano_tone(freq, duration)
        wave = apply_reverb(wave)
        sd.play(wave, sample_rate)
        sd.wait()
        if is_recording:
            recorded_notes.append(wave)
        current_note_label.config(text="")
        if highlight_btn:
            highlight_btn.config(bg=highlight_btn.default_bg)
    if highlight_btn:
        highlight_btn.config(bg="#77dd77")
    threading.Thread(target=_play).start()

def toggle_recording():
    """Start or stop recording."""
    global is_recording, recorded_notes
    if not is_recording:
        recorded_notes = []
        is_recording = True
        record_btn.config(text="⏹ Stop Recording", bg="#FF5555")
        record_status.config(text="🔴 Recording...", fg="#FF5555")
    else:
        is_recording = False
        record_btn.config(text="⏺ Start Recording", bg="#4CAF50")
        record_status.config(text="⚪ Not Recording", fg="#CCCCCC")
        status_label.config(text="Recording stopped. You can now save or play it.", fg="#00FFFF")

def save_recording():
    """Save the recorded notes as a .wav file."""
    if recorded_notes:
        audio = np.concatenate(recorded_notes, axis=0)
        os.makedirs("Recordings", exist_ok=True)
        filename = f"Recordings/piano_recording_{datetime.now().strftime('%H-%M-%S')}.wav"
        sf.write(filename, audio, sample_rate)
        status_label.config(text=f"✅ Saved as {filename}", fg="#00FF99")
    else:
        status_label.config(text="⚠️ No recording to save!", fg="#FF4444")

def play_recording():
    """Play back the last recorded notes."""
    if recorded_notes:
        audio = np.concatenate(recorded_notes, axis=0)
        status_label.config(text="🎧 Playing back recording...", fg="#00FFFF")
        threading.Thread(target=lambda: sd.play(audio, sample_rate)).start()
    else:
        status_label.config(text="⚠️ No recording to play!", fg="#FF4444")

def delete_recording():
    """Clear all recorded notes."""
    global recorded_notes
    recorded_notes = []
    status_label.config(text="🗑️ Cleared current recording.", fg="#FF7777")


# 🎹 GUI Setup

root = tk.Tk()
root.title("🎹 Virtual Piano Studio (Record, Play, Save)")
root.geometry("1200x520")
root.config(bg="#1b1b1b")

title = tk.Label(root, text="🎶 Virtual Piano Studio 🎶",
                 font=("Poppins", 22, "bold"), bg="#1b1b1b", fg="#E0E0E0")
title.pack(pady=10)

# 🎵 Current note label
current_note_label = tk.Label(root, text="", font=("Poppins", 18, "bold"),
                              bg="#1b1b1b", fg="#00FFCC")
current_note_label.pack(pady=5)

# Scrollable piano canvas
main_frame = tk.Frame(root, bg="#1b1b1b")
main_frame.pack(fill=tk.BOTH, expand=1)

canvas = tk.Canvas(main_frame, bg="#2b2b2b", height=260, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=1)

# Scrollbar BELOW
scrollbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
canvas.configure(xscrollcommand=scrollbar.set)

frame = tk.Frame(canvas, bg="#2b2b2b")
canvas.create_window((0, 0), window=frame, anchor="nw")

# Notes (C1–C7)
notes = []
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
for octave in range(1, 8):
    for n in note_names:
        notes.append(f"{n}{octave}")

WHITE_STYLE = {"bg": "#FFFFFF", "activebackground": "#E8E8E8", "relief": "raised"}
BLACK_STYLE = {"bg": "#1C1C1C", "activebackground": "#333333", "relief": "raised"}

note_buttons = {}

# Create keys
for note in notes:
    is_sharp = "#" in note
    color = BLACK_STYLE if is_sharp else WHITE_STYLE
    btn = tk.Button(
        frame,
        text=note,
        font=("Arial", 9, "bold"),
        width=4 if is_sharp else 7,
        height=10 if is_sharp else 14,
        fg="#FFF" if is_sharp else "#000",
        bd=3,
        highlightthickness=0,
        command=partial(play_note, note),
        **color
    )
    btn.default_bg = btn["bg"]
    if is_sharp:
        btn.pack(side=tk.LEFT, padx=1, pady=35)
    else:
        btn.pack(side=tk.LEFT, padx=1, pady=10)
    note_buttons[note] = btn

# 🎛️ Recording Control Panel
control_frame = tk.Frame(root, bg="#1b1b1b")
control_frame.pack(pady=10)

record_btn = tk.Button(control_frame, text="⏺ Start Recording", font=("Arial", 12, "bold"),
                       bg="#4CAF50", fg="white", padx=10, pady=5, command=toggle_recording)
record_btn.pack(side=tk.LEFT, padx=10)

play_btn = tk.Button(control_frame, text="▶️ Play Recording", font=("Arial", 12, "bold"),
                     bg="#2196F3", fg="white", padx=10, pady=5, command=play_recording)
play_btn.pack(side=tk.LEFT, padx=10)

save_btn = tk.Button(control_frame, text="💾 Save Recording", font=("Arial", 12, "bold"),
                     bg="#9C27B0", fg="white", padx=10, pady=5, command=save_recording)
save_btn.pack(side=tk.LEFT, padx=10)

delete_btn = tk.Button(control_frame, text="🗑️ Delete Recording", font=("Arial", 12, "bold"),
                       bg="#F44336", fg="white", padx=10, pady=5, command=delete_recording)
delete_btn.pack(side=tk.LEFT, padx=10)

record_status = tk.Label(root, text="⚪ Not Recording", font=("Arial", 11, "bold"),
                         bg="#1b1b1b", fg="#CCCCCC")
record_status.pack(pady=2)

status_label = tk.Label(root, text="", font=("Arial", 11, "bold"),
                        bg="#1b1b1b", fg="#BBBBBB")
status_label.pack(pady=3)


# 🎹 Keyboard Bindings
key_bind_map = {
    'a': 'C4', 'w': 'C#4', 's': 'D4', 'e': 'D#4', 'd': 'E4',
    'f': 'F4', 't': 'F#4', 'g': 'G4', 'y': 'G#4', 'h': 'A4',
    'u': 'A#4', 'j': 'B4', 'k': 'C5', 'o': 'C#5', 'l': 'D5'
}

def on_key_press(event):
    key = event.char.lower()
    if key in key_bind_map:
        note = key_bind_map[key]
        btn = note_buttons.get(note)
        if btn:
            play_note(note, highlight_btn=btn)

root.bind("<KeyPress>", on_key_press)

# Scroll updates
def update_scroll(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame.bind("<Configure>", update_scroll)
root.mainloop()