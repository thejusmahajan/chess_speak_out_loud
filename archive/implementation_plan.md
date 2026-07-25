# Realign "Chess Speak Out Loud" to Neural-Vision

This plan directly mirrors the single source of truth defined in `GEMINI_TASKS.md`. The objective is to build a coach that *shows* (translating LC0's neural vision to the UI without a text-generation layer) rather than one that *talks*.

## User Review Required
> [!IMPORTANT]
> The specification explicitly commands me to follow it **exactly and in order**, verifying actual API output (e.g. `lczerolens` and LC0 UCI `VerboseMoveStats`) before writing dependent code. 
> Please review and approve this plan. Upon your approval, I will begin execution with Phase 0 and proceed step-by-step.

## Proposed Changes

### Phase 0: Realignment & Disable LLM
*   **[MODIFY]** [app.py](file:///C:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py)
    *   Add global flag `LLM_ENABLED = False`.
    *   Disconnect the `coach_summary` / `generate_conversation` branch from the `/api/analyze` route so no LLM is called at runtime.
*   **[MODIFY]** [ARCHITECTURE.md](file:///C:/Users/Admin/Documents/chess_speak_out_loud/ARCHITECTURE.md)
    *   Update the Mermaid diagram to reflect the new pipeline (`UI → FastAPI → LC0 (UCI policy priors) + LC0 weights (PyTorch attention) → JSON → UI`).

### Phase 1: Policy Priors (Initiative)
*   **[MODIFY]** [engine_manager.py](file:///C:/Users/Admin/Documents/chess_speak_out_loud/backend/engine_manager.py)
    *   Add `async def get_policy_distribution(self, fen: str, nodes: int = 1) -> list[dict]`.
    *   *Verification step before implementation*: Run the `lc0.exe` binary in PowerShell and verify the `VerboseMoveStats` layout (`P: xx.xx%`) before building the regex/parser.
*   **[MODIFY]** [app.py](file:///C:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py)
    *   Call `get_policy_distribution(fen)` and append `"policy"` to the response.

### Phase 2: True Neural Attention (Vision)
*   **[NEW]** `backend/neural_vision.py`
    *   *Verification step before implementation*: Install `lczerolens` and run the exact discovery script to print the real API methods, loaders, and layer names.
    *   Create class `NeuralVision` to load `engine\791556.pb.gz` via `lczerolens` / PyTorch.
    *   Register forward hooks to extract attention activations, returning a 64-square `[0,1]` saliency map. (Fallback to policy priors only if this extraction fails).
*   **[MODIFY]** [app.py](file:///C:/Users/Admin/Documents/chess_speak_out_loud/backend/app.py)
    *   Initialize `NeuralVision` singleton and inject `"saliency"` into the `/api/analyze` response.

### Phase 3: Frontend Visualization
*   **[MODIFY]** [PgnViewer.tsx](file:///C:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/components/PgnViewer.tsx) & [index.css](file:///C:/Users/Admin/Documents/chess_speak_out_loud/frontend/src/index.css)
    *   Implement **Saliency heatmap overlay** (CSS/Canvas glow mapped to squares).
    *   Implement **Policy arrows** (Semi-transparent arrows from `from`→`to`, opacity scaled by `P`).
    *   Implement **Feedback flash** (Calculate disparity `P(best) - P(userMove)`, flash board if > 0.25).
    *   Remove all text-commentary UI (coach summaries, personas).

### Phase 4: Final Verification
*   **[NEW]** `REALIGNMENT_REPORT.md`
    *   Write the final report verifying the execution of all Acceptance Checks.

## Verification Plan
For each Phase, I will execute the precise `Acceptance check` command from `GEMINI_TASKS.md` (e.g. `curl` checks, python assertions) and ensure the real output aligns perfectly before moving to the next Phase.
