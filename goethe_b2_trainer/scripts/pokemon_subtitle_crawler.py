"""
Pokemon Subtitle Crawler & German B1-B2 Language Learning Study Builder
Supports downloading official and auto subtitles from YouTube via yt-dlp & youtube-transcript-api.
Generates:
1. Standard SRT file (.de.srt, .en.srt)
2. Clean German Reading Text (.de_clean.txt)
3. Dual-Language Aligned Study Guide (.bilingual_study.md)
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube 11-char video ID from various URL formats or raw ID."""
    url_or_id = url_or_id.strip()
    if len(url_or_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)
    return url_or_id

def format_timestamp(seconds: float) -> str:
    """Convert seconds float to SRT timestamp format HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def clean_text_for_reading(raw_text: str) -> str:
    """Clean subtitle text by removing sound effects like [Musik], ♪, narrator tags, etc."""
    # Remove musical notes
    text = re.sub(r'♪[^♪]*♪', '', raw_text)
    text = text.replace('♪', '')
    # Remove sound tags like [Lachen], [Erzähler], (beide)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    # Remove speaker hyphens at start of lines
    text = re.sub(r'^\s*-\s*', '', text, flags=re.MULTILINE)
    # Clean whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return ' '.join(lines)

def fetch_via_transcript_api(video_id: str, lang: str = 'de'):
    """Fetch transcript using youtube-transcript-api."""
    if not YouTubeTranscriptApi:
        return None
    try:
        ytt = YouTubeTranscriptApi()
        transcript_list = ytt.list(video_id)
        transcript = transcript_list.find_transcript([lang])
        data = transcript.fetch()
        return data
    except Exception as e:
        print(f"[-] youtube-transcript-api error for lang '{lang}': {e}")
        return None

def fetch_via_ytdlp(video_url: str, output_dir: Path, title_prefix: str = ""):
    """Download subtitles using yt-dlp CLI with android player client fallback."""
    import subprocess
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--extractor-args", "youtube:player_client=android",
        "--write-sub",
        "--sub-lang", "de,en",
        "--sub-format", "srt",
        "--skip-download",
        "-o", str(output_dir / "%(title)s.%(ext)s"),
        video_url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.returncode == 0, res.stdout, res.stderr

def get_snippet_val(item, attr, default=None):
    if hasattr(item, attr):
        return getattr(item, attr)
    if isinstance(item, dict):
        return item.get(attr, default)
    return default

# High-yield B1-B2 Connectors and Grammar markers to detect
B2_GRAMMAR_MARKERS = {
    "Konnektoren / Nebensätze": [
        "nachdem", "obwohl", "obgleich", "während", "indem", "sodass", "so dass",
        "damit", "sowohl als auch", "weder noch", "entweder oder", "nicht nur sondern auch",
        "einerseits andererseits", "zwar aber", "je desto", "je umso", "insofern", "falls"
    ],
    "Konjunktiv II & Indirekte Rede": [
        "wäre", "hätte", "würde", "könnte", "müsste", "dürfte", "sollte", "als ob", "als wenn"
    ],
    "Passiv / Passiversatz": [
        "wurde", "worden", "geworden", "lässt sich", "ist zu"
    ],
    "Feste Nomen-Verb-Verbindungen & Redewendungen": [
        "sorgen machen", "in frage stellen", "zur verfügung", "rücksicht nehmen", "angst haben"
    ]
}

def analyze_b2_grammar_and_vocab(de_data):
    """Scan transcript for B1-B2 grammatical motifs and rich vocabulary."""
    detected = {category: [] for category in B2_GRAMMAR_MARKERS}
    vocab_counter = {}

    for item in de_data:
        raw_text = get_snippet_val(item, 'text', '')
        clean = clean_text_for_reading(raw_text).lower()
        if not clean:
            continue
        
        # Check grammar markers
        for category, markers in B2_GRAMMAR_MARKERS.items():
            for m in markers:
                pattern = r'\b' + re.escape(m) + r'\b'
                if re.search(pattern, clean):
                    detected[category].append({
                        "marker": m,
                        "timestamp": format_timestamp(get_snippet_val(item, 'start', 0.0)),
                        "sentence": get_snippet_val(item, 'text', '').replace('\n', ' ').strip()
                    })

        # Tokenize words (length >= 5 for vocabulary study)
        words = re.findall(r'\b[A-Za-zÄÖÜäöüß]{5,}\b', raw_text)
        for w in words:
            w_norm = w.capitalize() if w[0].isupper() else w.lower()
            vocab_counter[w_norm] = vocab_counter.get(w_norm, 0) + 1

    return detected, sorted(vocab_counter.items(), key=lambda x: x[1], reverse=True)

def build_study_materials(video_id: str, episode_name: str, output_dir: Path):
    """
    Build complete study packet:
    1. German SRT
    2. English SRT
    3. Clean German text
    4. Bilingual side-by-side study markdown
    5. B2 Grammar & Vocabulary Study Dossier (.b2_study_guide.md)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    de_data = fetch_via_transcript_api(video_id, 'de')
    en_data = fetch_via_transcript_api(video_id, 'en')

    if not de_data:
        print(f"[!] Warning: Could not fetch German transcript via API, falling back to yt-dlp...")
        success, out, err = fetch_via_ytdlp(f"https://www.youtube.com/watch?v={video_id}", output_dir)
        print(f"yt-dlp fallback result: {success}")
        return

    # 1. Write German SRT
    de_srt_path = output_dir / f"{episode_name}.de.srt"
    with open(de_srt_path, "w", encoding="utf-8") as f:
        for idx, item in enumerate(de_data, 1):
            start = format_timestamp(get_snippet_val(item, 'start', 0.0))
            duration = get_snippet_val(item, 'duration', 0.0)
            end = format_timestamp(get_snippet_val(item, 'start', 0.0) + duration)
            text = get_snippet_val(item, 'text', '').strip()
            f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
    print(f"[+] Saved German SRT: {de_srt_path}")

    # 2. Write English SRT (if available)
    if en_data:
        en_srt_path = output_dir / f"{episode_name}.en.srt"
        with open(en_srt_path, "w", encoding="utf-8") as f:
            for idx, item in enumerate(en_data, 1):
                start = format_timestamp(get_snippet_val(item, 'start', 0.0))
                duration = get_snippet_val(item, 'duration', 0.0)
                end = format_timestamp(get_snippet_val(item, 'start', 0.0) + duration)
                text = get_snippet_val(item, 'text', '').strip()
                f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
        print(f"[+] Saved English SRT: {en_srt_path}")

    # 3. Clean German Reading Text
    clean_path = output_dir / f"{episode_name}.de_clean.txt"
    cleaned_sentences = []
    current_block = []
    for item in de_data:
        text = clean_text_for_reading(get_snippet_val(item, 'text', ''))
        if text:
            current_block.append(text)
            if len(current_block) >= 4 or any(text.endswith(p) for p in ['.', '!', '?']):
                cleaned_sentences.append(' '.join(current_block))
                current_block = []
    if current_block:
        cleaned_sentences.append(' '.join(current_block))

    with open(clean_path, "w", encoding="utf-8") as f:
        f.write(f"# {episode_name} - Deutsche Abschrift (Clean Script)\n\n")
        for p in cleaned_sentences:
            f.write(f"{p}\n\n")
    print(f"[+] Saved Clean German Script: {clean_path}")

    # 4. Generate Bilingual Side-by-Side Markdown
    study_path = output_dir / f"{episode_name}.bilingual_study.md"
    with open(study_path, "w", encoding="utf-8") as f:
        f.write(f"# Pokémon Staffel 1: {episode_name} - Deutsch ↔ English Lernmaterial\n\n")
        f.write("> **Lernmethode (B1 -> B2)**:\n")
        f.write("> 1. **Hörverstehen**: Schau dir die Szene zuerst ohne Untertitel an.\n")
        f.write("> 2. **Lese- und Hörvergleich**: Spiele die Szene mit deutschen Untertiteln ab.\n")
        f.write("> 3. **Shadowing**: Sprich die Sätze synchron mit gleicher Intonation und Tempo nach.\n\n")
        f.write("| Zeit | Deutsch (Original) | English (Referenz) |\n")
        f.write("| :--- | :--- | :--- |\n")

        en_idx = 0
        num_en = len(en_data) if en_data else 0
        for item in de_data:
            start_sec = get_snippet_val(item, 'start', 0.0)
            time_str = f"{int(start_sec // 60):02d}:{int(start_sec % 60):02d}"
            de_text = get_snippet_val(item, 'text', '').replace('\n', ' ').strip()
            
            en_text = ""
            if en_data:
                while en_idx < num_en - 1 and get_snippet_val(en_data[en_idx + 1], 'start', 0.0) <= start_sec + 1.0:
                    en_idx += 1
                if en_idx < num_en:
                    en_text = get_snippet_val(en_data[en_idx], 'text', '').replace('\n', ' ').strip()
            
            de_cell = de_text.replace('|', '\\|')
            en_cell = en_text.replace('|', '\\|')
            f.write(f"| `{time_str}` | {de_cell} | {en_cell} |\n")

    print(f"[+] Saved Bilingual Study Guide: {study_path}")

    # 5. Generate B2 Grammar & Vocabulary Study Dossier
    grammar_hits, vocab_freq = analyze_b2_grammar_and_vocab(de_data)
    guide_path = output_dir / f"{episode_name}.b2_grammar_vocab_guide.md"
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(f"# B2 Grammatik & Wortschatz Analyse: {episode_name}\n\n")
        f.write("Dieser Leitfaden analysiert die konkreten B1- und B2-Grammatikstrukturen und Vokabeln aus der Folge.\n\n")
        
        f.write("## 1. Grammatikalische B1/B2 Schwerpunkte in dieser Folge\n\n")
        for category, hits in grammar_hits.items():
            f.write(f"### {category} ({len(hits)} Fundstellen)\n")
            if hits:
                seen_sentences = set()
                count = 0
                for hit in hits:
                    if hit['sentence'] not in seen_sentences:
                        seen_sentences.add(hit['sentence'])
                        f.write(f"- **`{hit['marker']}`** (`{hit['timestamp']}`): *\"{hit['sentence']}\"*\n")
                        count += 1
                        if count >= 6:
                            break
            else:
                f.write("- Keine direkten Treffer in dieser Kategorie.\n")
            f.write("\n")

        f.write("## 2. Relevanter Wortschatz (Top Vokabeln der Episode)\n\n")
        f.write("| Wort | Häufigkeit | B2-Bedeutung / Kontext |\n")
        f.write("| :--- | :---: | :--- |\n")
        # Filter top 25 non-trivial words
        stopwords = {"Pokemon", "Pikachu", "Misty", "Rocko", "nicht", "haben", "einen", "einer", "einem", "eines", "dieser", "dieses", "diese"}
        written_vocab = 0
        for word, count in vocab_freq:
            if word not in stopwords and len(word) >= 5:
                f.write(f"| **{word}** | {count} | Im Dialog zu wiederholen |\n")
                written_vocab += 1
                if written_vocab >= 30:
                    break

    print(f"[+] Saved B2 Grammar & Vocabulary Guide: {guide_path}")

def main():
    parser = argparse.ArgumentParser(description="Download Pokemon YouTube subtitles for German B1/B2 learning.")
    parser.add_argument("url", help="YouTube URL or Video ID (e.g., https://www.youtube.com/watch?v=XwpbJK-WE8Q)")
    parser.add_argument("--name", default="Episode_26_Hypnos_Nickerchen", help="Episode title or file prefix")
    parser.add_argument("--outdir", default="subtitles/pokemon_staffel_1", help="Output directory")
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    print(f"[*] Processing Video ID: {video_id}")
    out_path = Path(args.outdir)
    build_study_materials(video_id, args.name, out_path)
    print("[*] Completed successfully!")

if __name__ == "__main__":
    main()
