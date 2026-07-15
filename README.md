# Chess Speak Out Loud — AI Chess Coach Trainer

> *"Never show Alex what to play without first teaching him what to look for and why it matters."*

A chess training tool that translates LC0's neural network thinking into the language of Grandmaster coaching. Instead of cryptic evaluation numbers, you get heatmaps showing board control, piece activity, and tension — plus verbal explanations of *why* a position favors one side.

## Features (Phase 1 — Barebone)

- **Interactive Chessboard** — Load positions via FEN or step through PGN games
- **LC0-Powered Analysis** — Deep positional analysis using Leela Chess Zero's neural network
- **Heatmap Overlays** — Three visualization modes:
  - **Control Map** — Who dominates which squares (red = white, blue = black)
  - **Piece Activity** — How mobile each piece is (green = active, transparent = passive)
  - **Tension Map** — Where the fight is (yellow = contested squares)
- **Verbal Coach** — GM-language explanations of king safety, pawn structure, piece activity, center control, and material imbalances
- **Mock Mode** — Full UI development without LC0 installed, with hand-crafted analyses for classic positions

## Quick Start

### 1. Set Up the Engine

Run the setup script to download LC0 and a default neural network:

```batch
setup_engine.bat
```

Or manually:
1. Download LC0 from [GitHub Releases](https://github.com/LeelaChessZero/lc0/releases/tag/v0.32.1)
2. Download a neural network from [lczero.org/play/networks/bestnets](https://lczero.org/play/networks/bestnets/)
3. Place both `lc0.exe` and the `.pb.gz` weights file in the `engine/` folder

### 2. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Run the Application

```bash
cd C:\Users\Admin\Documents\chess_speak_out_loud
uvicorn backend.app:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

> **Note:** If LC0 is not installed, the app runs in **Mock Mode** with pre-analyzed positions. The UI is fully functional.

## Project Structure

```
chess_speak_out_loud/
├── backend/
│   ├── app.py              # FastAPI server & API endpoints
│   ├── engine.py           # LC0/UCI engine wrapper
│   ├── heatmap.py          # Square-by-square heatmap generation
│   ├── concept_mapper.py   # Engine output → GM-language translator
│   ├── mock_data.py        # Mock analysis for development
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main application page
│   ├── css/
│   │   └── style.css       # Dark premium theme
│   └── js/
│       ├── app.js          # Core application logic
│       ├── heatmap.js      # Canvas heatmap overlay
│       └── coach.js        # Verbal coach panel
├── engine/                 # LC0 binary + neural network weights
│   ├── lc0.exe             # (downloaded by setup script)
│   └── *.pb.gz             # (neural network weights)
├── setup_engine.bat        # Engine download script
└── README.md               # This file
```

## Architecture

```
┌─────────────────────────────────────────────┐
│                  Frontend                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │Chessboard│  │ Heatmap  │  │  Verbal   │ │
│  │  + FEN   │  │  Canvas  │  │  Coach    │ │
│  └──────────┘  └──────────┘  └───────────┘ │
└────────────────────┬────────────────────────┘
                     │ REST API
┌────────────────────┴────────────────────────┐
│                  Backend                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  LC0     │  │ Heatmap  │  │ Concept   │ │
│  │ Engine   │  │Generator │  │  Mapper   │ │
│  └──────────┘  └──────────┘  └───────────┘ │
└──────────────────────────────────────────────┘
```

## Hardware Recommendations

| Setup | LC0 Build | Network Size | Performance |
|-------|-----------|-------------|-------------|
| CPU only | `cpu-dnnl` or `cpu-openblas` | Small/Medium | ~1K nodes/sec |
| NVIDIA GPU (mid) | `cuda11` or `cuda12` | Medium/Large (T1) | ~10-50K nodes/sec |
| NVIDIA GPU (high) | `cuda12` + `cudnn` | Very Large (BT4) | ~100K+ nodes/sec |

## Future Roadmap

- [ ] **Theme Detector** — Pawn structure recognition + tactical precondition scanning
- [ ] **Template Game Library** — Curated model games per opening variation
- [ ] **Spaced Repetition Trainer** — Anki-style drilling on concepts, not just moves
- [ ] **Structure-Tactic Map** — Predict tactical motifs from pawn formations
- [ ] **Socratic Mode** — Ask questions before revealing answers

## License

MIT
