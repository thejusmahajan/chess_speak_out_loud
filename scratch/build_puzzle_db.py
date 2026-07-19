import os
import sqlite3
import csv
import zstandard as zstd
import io
import sys
from collections import defaultdict

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data", "puzzles")
    zst_path = os.path.join(data_dir, "lichess_db_puzzle.csv.zst")
    sqlite_path = os.path.join(data_dir, "puzzles.sqlite")
    
    if os.path.exists(sqlite_path):
        os.remove(sqlite_path)
        
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("PRAGMA synchronous = OFF")
    cur.execute("PRAGMA journal_mode = MEMORY")
    
    cur.execute("""
    CREATE TABLE puzzles (
        id TEXT PRIMARY KEY,
        fen TEXT,
        moves TEXT,
        rating INT,
        popularity INT,
        themes TEXT,
        opening_tags TEXT
    )
    """)
    cur.execute("CREATE INDEX idx_rating ON puzzles(rating)")
    
    cur.execute("""
    CREATE TABLE opening_motifs (
        opening_tag TEXT,
        theme TEXT,
        n INT
    )
    """)
    
    print("Building SQLite DB from puzzle CSV...")
    sys.stdout.flush()
    
    motif_counts = defaultdict(lambda: defaultdict(int))
    count = 0
    
    with open(zst_path, "rb") as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            text_stream = io.TextIOWrapper(reader, encoding="utf-8")
            csv_reader = csv.DictReader(text_stream)
            
            puzzles_batch = []
            
            for row in csv_reader:
                popularity = int(row.get("Popularity", 0) or 0)
                if popularity >= 70:
                    puzzle_id = row["PuzzleId"]
                    fen = row["FEN"]
                    moves = row["Moves"]
                    rating = int(row.get("Rating", 0) or 0)
                    themes = row["Themes"]
                    opening_tags = row["OpeningTags"]
                    
                    puzzles_batch.append((puzzle_id, fen, moves, rating, popularity, themes, opening_tags))
                    
                    if opening_tags and themes:
                        tag_list = opening_tags.split()
                        theme_list = themes.split()
                        for tag in tag_list:
                            for theme in theme_list:
                                motif_counts[tag][theme] += 1
                                
                    count += 1
                    if count % 100000 == 0:
                        cur.executemany("""
                        INSERT INTO puzzles (id, fen, moves, rating, popularity, themes, opening_tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, puzzles_batch)
                        puzzles_batch.clear()
                        conn.commit()
                        print(f"Processed {count} puzzles...")
                        sys.stdout.flush()
                        # LIMIT FOR SPEED IN DEVELOPMENT SO WE DON'T BLOCK FOREVER
                        if count >= 300000:
                            break
                            
            if puzzles_batch:
                cur.executemany("""
                INSERT INTO puzzles (id, fen, moves, rating, popularity, themes, opening_tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, puzzles_batch)
                conn.commit()
                
    print("Inserting aggregated opening motifs...")
    sys.stdout.flush()
    motifs_batch = []
    for tag, themes in motif_counts.items():
        for theme, n in themes.items():
            motifs_batch.append((tag, theme, n))
            
    cur.executemany("INSERT INTO opening_motifs (opening_tag, theme, n) VALUES (?, ?, ?)", motifs_batch)
    
    print("Committing and closing...")
    sys.stdout.flush()
    conn.commit()
    conn.close()
    print("Done!")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
