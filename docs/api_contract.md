# REST API Contract

This document acts as the strict contract between the React Frontend and the FastAPI Backend.

## Endpoints

### 1. `GET /api/health`
Health check to ensure the API and LC0 engine are running.
**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### 2. `POST /api/analyze`
Analyzes a specific FEN position using LC0. Generates heatmaps and concept mappings.
**Request Body:**
```json
{
  "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
  "nodes": 5000
}
```
**Response:**
```json
{
  "fen": "...",
  "best_move": "d2d4",
  "score": 1.5,
  "concept_maps": {
    "king_safety": { ... },
    "space": { ... }
  },
  "heatmaps": {
    "activity": "base64_encoded_image..."
  }
}
```

### 3. `POST /api/play-move`
Simulates playing a move from a position and retrieves LC0's PV response.
**Request Body:**
```json
{
  "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
  "move": "e4e5"
}
```

### 4. `POST /api/analyze-pgn`
Performs a deep tactical analysis of a PGN sequence using Lichess Tagger and Gemini.
**Request Body:**
```json
{
  "pgn": "[Event \"Casual Game\"]\n\n1. e4 e5 2. Nf3 Nc6..."
}
```
**Response:**
```json
{
  "tactics_found": ["fork", "pin"],
  "commentary": "Magnus: The tension here on the light squares..."
}
```
