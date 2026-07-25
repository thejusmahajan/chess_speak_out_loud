# Questions and Audit Items for Leader Review

## 1. Backend Route & Profile Schema Alignment
- **Verification**: `@app.get("/api/training/profile")` in `backend/app.py:500-505` loads and serves `profile.json` directly via `store.load_profile()`.
- **Observation**: `profile.json` written by `backend/training/pipeline.py` contains all required TS2 fields (`steer_findings`, `steer_summary`, `steer_budget_exhausted`).
- **Backend Touch Audit**: Zero backend code modifications were made to `backend/training/metrics.py` (leader-owned) or any other backend logic.

## 2. Frontend Surface Additions for Review
- `frontend/src/api/training.ts`: Added explicit TS interfaces `SteerCandidate`, `SteerFinding`, `SteerSummaryItem`, and `ProfileData`. Annotated `getProfile()`.
- `frontend/src/components/Training/ProfileReport.tsx`: Added TS2 stat box in header, TS2 Opening Summary table, and Sharp/Sacrificial Candidate card grid. Wired candidate card clicks to `onFindingClick` for `TrainingBoard` position review.
- `frontend/src/components/Training/DiagnosePanel.tsx`: Added TS2 progress display when `progress.stage_steer_done` is present in job status polling.
- `frontend/src/components/Training/__tests__/ProfileReport.test.tsx`: Added unit test suite covering TS2 stat boxes, summary table, candidate cards, and empty state fallbacks.

## 3. Git Staging Status
- All changes remain local/staged on the working tree per instructions (**no push**). Ready for leader audit and merge approval.
