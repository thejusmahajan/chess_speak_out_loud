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
    API -.->|Dormant/Disabled| Gemini[Google Gemini API]
    style Gemini stroke-dasharray: 5 5, fill:#eee, color:#aaa
```

## Component Boundaries

1. **Frontend (`frontend/`)**: Pure UI. Renders direct visual overlays (policy arrows, saliency heatmaps) from raw neural data. Should not contain chess logic.
2. **Backend (`backend/`)**: FastAPI orchestrator.
   - **`engine_manager.py`**: Interacts with the `lc0.exe` subprocess to extract policy priors (`VerboseMoveStats`) and PV.
   - **`neural_vision.py`**: Interacts with `lczerolens` / PyTorch to extract true neural attention (saliency maps).
   - **`llm_client.py`**: **Dormant**. Wraps `google.generativeai` but is disabled behind the `LLM_ENABLED` flag.

## Data Flow for Neural Vision Analysis
1. User plays a move or requests analysis.
2. FastAPI asks LC0 for the policy priors (energy/initiative).
3. FastAPI interrogates PyTorch for the attention saliency map (vision/structure).
4. FastAPI returns a JSON payload containing `policy` and `saliency`.
5. UI renders thick arrows for policy and glowing red squares for saliency.
