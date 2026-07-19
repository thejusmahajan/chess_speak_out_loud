import os
import requests

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "openings")
os.makedirs(data_dir, exist_ok=True)

for letter in ['a', 'b', 'c', 'd', 'e']:
    url = f"https://raw.githubusercontent.com/lichess-org/chess-openings/master/{letter}.tsv"
    dest = os.path.join(data_dir, f"{letter}.tsv")
    if not os.path.exists(dest):
        print(f"Downloading {letter}.tsv...")
        r = requests.get(url)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
print("Done.")
