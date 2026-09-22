"""
Pure Python WAV generator for Hören audio demo.
Uses only standard library (wave, math, struct).
"""

import math
import struct
import wave
from pathlib import Path

AUDIO_DIR = Path(__file__).resolve().parent / "content" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE_WAV = AUDIO_DIR / "hoeren_sample.wav"


def create_audio():
    sample_rate = 22050
    duration = 12.0  # 12 seconds preview
    num_samples = int(sample_rate * duration)

    with wave.open(str(OUT_FILE_WAV), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        # Formant frequencies simulating human vowel-like formants: F1 ~ 500Hz, F2 ~ 1500Hz
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            # Speech cadence envelope (simulating word pauses)
            envelope = 0.5 * (1.0 + math.sin(2 * math.pi * 1.2 * t))
            if int(t * 2) % 3 == 2:
                envelope *= 0.2  # Pause between sentences

            # Pitch fundamental f0 ~ 130 Hz with intonation contour
            f0 = 130 + 15 * math.sin(2 * math.pi * 0.8 * t)
            # Harmonics
            s = 0.6 * math.sin(2 * math.pi * f0 * t) + 0.3 * math.sin(4 * math.pi * f0 * t) + 0.15 * math.sin(6 * math.pi * f0 * t)
            val = int(envelope * s * 16000)
            val = max(-32768, min(32767, val))
            frames.extend(struct.pack("<h", val))

        wav_file.writeframes(frames)
    print(f"Generated {OUT_FILE_WAV} successfully.")


if __name__ == "__main__":
    create_audio()
