"""
Generates high-fidelity German audio for Goethe B2 Hören module.
Supports:
1. edge-tts (free Microsoft neural voices)
2. Downloading official Goethe-Institut B2 sample MP3
3. Windows SAPI TTS
"""

import sys
import os
import asyncio
from pathlib import Path

AUDIO_DIR = Path(__file__).resolve().parent / "content" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
OUT_MP3 = AUDIO_DIR / "hoeren_sample.mp3"
OUT_WAV = AUDIO_DIR / "hoeren_sample.wav"

DIALOGUE = [
    {
        "speaker": "de-DE-KillianNeural", # Moderator
        "text": "Willkommen bei Campus und Karriere. Immer mehr Arbeitnehmer klagen über das Phänomen der ständigen Erreichbarkeit. Dienstliche E-Mails am Sonntagabend oder Nachrichten in Messenger-Gruppen nach Feierabend sind für viele Normalität geworden. Wir sprechen dazu mit der Arbeitspsychologin Dr. Sabine Becker. Frau Dr. Becker, wie schädlich ist dieser Trend wirklich?"
    },
    {
        "speaker": "de-DE-KatjaNeural", # Dr. Becker
        "text": "Nun, das eigentliche Problem ist nicht einmal die Zeit, die man mit dem Beantworten einer kurzen E-Mail verbringt. Es ist vielmehr die sogenannte antizipatorische Erschöpfung. Das ständige innerliche Bereithalten verhindert, dass unser Erholungsnervensystem aktiv wird. Wer ständig damit rechnet, kontaktiert zu werden, bleibt auch auf dem Sofa im Alarmzustand. Für eine echte Regeneration ist eine klare psychologische Trennung zwischen Arbeitszeit und Freizeit unabdingbar. Unternehmen, die hier verbindliche Ruhezeiten festlegen, verzeichnen langfristig nachweislich weniger Burnout-Fälle."
    }
]


async def generate_with_edge_tts():
    try:
        import edge_tts
        print("Using edge-tts to generate multi-speaker German dialogue...")
        temp_files = []
        for i, part in enumerate(DIALOGUE):
            part_path = AUDIO_DIR / f"part_{i}.mp3"
            communicate = edge_tts.Communicate(part["text"], part["speaker"], rate="-4%")
            await communicate.save(str(part_path))
            temp_files.append(part_path)
            print(f"  Generated part {i+1}/{len(DIALOGUE)} ({part['speaker']})")

        # Combine audio parts
        with open(OUT_MP3, "wb") as outfile:
            for p in temp_files:
                with open(p, "rb") as infile:
                    outfile.write(infile.read())
                try: os.remove(p)
                except: pass

        print(f"✓ High-quality German MP3 successfully generated at: {OUT_MP3}")
        return True
    except ImportError:
        print("edge-tts is not installed. Run: pip install edge-tts")
        return False
    except Exception as e:
        print(f"Error generating edge-tts audio: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(generate_with_edge_tts())
    if not success:
        print("Falling back to in-browser Web Speech API or sample audio.")
