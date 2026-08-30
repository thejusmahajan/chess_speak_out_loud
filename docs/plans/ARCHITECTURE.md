# Architecture: Chess Speak Out Loud

This document provides a high-level overview of the data flow and system boundaries, following the realignment to a neural-vision focus.

## System Diagram

```mermaid
graph TD
    UI[React Frontend] -->|REST API| API[FastAPI Backend]
    
    API -->|Evaluate FEN| LC0[Leela Chess Zero Binary]
    LC0 -->|Policy Priors / PV| API
    
    API -->|Extract Attention| PyTorch[LC0 Weights via lczerolens]
    PyTorch -->|Saliency Map| API
    
    API -->|JSON Response (Policy + Saliency)| UI
    
    %% Dormant LLM Node
    API -.->|Unreachable - seam removed 2026-08-30| Gemini[Google Gemini API]
    style Gemini stroke-dasharray: 5 5, fill:#eee, color:#aaa
```

## Component Boundaries

1. **Frontend (`frontend/`)**: Pure UI. Renders direct visual overlays (policy arrows, saliency heatmaps) from raw neural data. Should not contain chess logic.
2. **Backend (`backend/`)**: FastAPI orchestrator.
   - **`engine_manager.py`**: Interacts with the `lc0.exe` subprocess to extract policy priors (`VerboseMoveStats`) and PV.
   - **`neural_vision.py`**: Interacts with `lczerolens` / PyTorch to extract true neural attention (saliency maps).
   - **`llm_client.py`**: **Unreachable from any request path**, enforced by `backend/tests/test_llm_seam.py` (no non-test module under `backend/` may import it). It was NOT previously disabled: the `LLM_ENABLED` flag was never read, and two repertoire endpoints reached this module until 2026-08-30. Retained as scaffolding for the eventual *translator* role.

## Data Flow for Neural Vision Analysis
1. User plays a move or requests analysis.
2. FastAPI asks LC0 for the policy priors (energy/initiative).
3. FastAPI interrogates PyTorch for the attention saliency map (vision/structure).
4. FastAPI returns a JSON payload containing `policy` and `saliency`.
5. UI renders thick arrows for policy and glowing red squares for saliency.
