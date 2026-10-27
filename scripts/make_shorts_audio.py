"""Builds the Shorts soundtrack and the final MP4 from store/video/work/ (made by scripts/shorts.mjs).

Sound effects are re-synthesized from the game's own tone log, the same way the game plays them with
Web Audio (oscillator + exponential frequency slide + exponential fade), on top of a quiet background loop.

Run from the project root:  python3 scripts/make_shorts_audio.py
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "store/video/work"
OUT = ROOT / "store/video/orbit-hop-shorts.mp4"
SR = 44100


def osc(kind, phase):
    if kind == "sine":
        return np.sin(phase)
    if kind == "triangle":
        return 2 / np.pi * np.arcsin(np.sin(phase))
    if kind == "sawtooth":  # band-limited: sum a handful of harmonics so it is not harsh
        return sum(np.sin(k * phase) / k for k in range(1, 12)) * (2 / np.pi)
    raise ValueError(kind)


def tone(freq, dur, kind="sine", vol=0.18, slide=0.0):
    """Mirror of tone() in src/game.html."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    if slide:
        end = max(40.0, freq + slide)
        f = freq * (end / freq) ** (t / dur)
    else:
        f = np.full(n, float(freq))
    phase = 2 * np.pi * np.cumsum(f) / SR
    gain = vol * (0.0001 / vol) ** (t / dur)
    return osc(kind, phase) * gain


def add(buf, start, sig, pan=0.0):
    i = int(start * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i : i + len(sig), 0] += sig * left
    buf[i : i + len(sig), 1] += sig * right


def note(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def envelope(n, attack, release):
    env = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    env[:a] = np.linspace(0, 1, a)
    env[n - r :] *= np.linspace(1, 0, r)
    return env


def music(seconds, drums_until):
    """A major loop, 100 BPM: A - F#m - D - E, soft pad, plucked arpeggio, light kick and shaker."""
    buf = np.zeros((int(seconds * SR) + SR, 2))
    beat = 60 / 100
    bar = beat * 4
    chords = [[57, 61, 64], [54, 57, 61], [50, 54, 57], [52, 56, 59]]  # A, F#m, D, E
    rng = np.random.default_rng(3)
    t, i = 0.0, 0
    while t < seconds:
        chord = chords[i % 4] if t + bar < seconds else chords[0]
        n = int(bar * SR)
        tt = np.arange(n) / SR
        for k, m in enumerate(chord):
            for det, pan in ((-0.07, -0.5), (0.07, 0.5)):
                f = note(m) * 2 ** (det / 12)
                pad = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt)) * envelope(n, 0.6, 0.6) * 0.022
                add(buf, t, pad, pan)
        # arpeggio: 8th notes walking up the chord an octave higher
        for s in range(8):
            m = chord[s % 3] + 12 + (12 if s >= 6 else 0)
            add(buf, t + s * beat / 2, tone(note(m), 0.32, "triangle", 0.045), pan=(-0.3 if s % 2 else 0.3))
        if t < drums_until:
            for b in range(4):
                add(buf, t + b * beat, tone(110, 0.22, "sine", 0.16, -70))  # kick
                hat = rng.standard_normal(int(0.05 * SR)) * np.linspace(1, 0, int(0.05 * SR)) ** 3 * 0.025
                add(buf, t + b * beat + beat / 2, hat - np.convolve(hat, np.ones(8) / 8, "same"))
        t += bar
        i += 1
    return buf


def main():
    run = json.loads((WORK / "run.json").read_text())
    seconds = run["seconds"]
    over_at = run["overAt"] or seconds

    buf = music(seconds, drums_until=over_at)
    sfx = np.zeros_like(buf)
    for at_ms, freq, dur, kind, vol, slide in run["tones"]:
        add(sfx, at_ms / 1000, tone(freq, dur, kind, vol, slide))
    mix = buf * 0.9 + sfx * 1.15

    # fade out over the last 1.2 s, trim to the video length, normalize to -1 dBFS
    n = int(seconds * SR)
    mix = mix[:n]
    fade = int(1.2 * SR)
    mix[n - fade :] *= np.linspace(1, 0, fade)[:, None]
    mix *= 0.89 / max(1e-9, np.abs(mix).max())

    wav_path = WORK / "audio.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", str(run["fps"]), "-i", str(WORK / "frames/f%05d.jpg"),
            "-i", str(wav_path),
            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-r", str(run["fps"]),
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-shortest",
            str(OUT),
        ],
        check=True,
    )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
