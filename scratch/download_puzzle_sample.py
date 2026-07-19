import os
import requests
import zstandard as zstd
import io

url = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "puzzles")
os.makedirs(data_dir, exist_ok=True)
dest_path = os.path.join(data_dir, "lichess_db_puzzle.csv.zst")

if not os.path.exists(dest_path):
    print("Downloading puzzle DB...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("Download complete.")

print("Reading header...")
with open(dest_path, "rb") as f:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(f) as reader:
        text_stream = io.TextIOWrapper(reader, encoding="utf-8")
        header = text_stream.readline().strip()
        print(f"HEADER_ROW: {header}")
