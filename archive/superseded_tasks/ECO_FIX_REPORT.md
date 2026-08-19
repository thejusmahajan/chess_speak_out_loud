# Root-Cause & Fix Report — `ECO='???'` Opening Classification

## 1. Investigation Findings (Root Cause)

### Data Dependency & `.gitignore` Exclusion ([data/.gitignore](file:///c:/Users/Admin/Documents/chess_speak_out_loud/data/.gitignore#L1-L2))
- `backend/training/openings.py` relies on 5 TSV database files (`a.tsv`, `b.tsv`, `c.tsv`, `d.tsv`, `e.tsv`) containing ~387 KB of ECO opening move sequences.
- `data/.gitignore` contained `*\n!.gitignore`, which gitignored ALL contents of `data/`, including `data/openings/*.tsv`.
- Because `data/openings/*.tsv` was ignored by git, any git dataset build / deployment zip created for Kaggle **excluded `data/openings/*.tsv`**.

### Path Resolution Mismatch ([openings.py:7-8](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/openings.py#L7-L8))
- `openings.py` previously resolved `ROOT_DIR` by calling `os.path.dirname` 3 times up from `openings.py`, expecting `data/openings` to exist at the repository root level outside `backend/`.
- On Kaggle, the execution environment imports `backend` directly (`/kaggle/input/.../backend/` or `/kaggle/working/backend/`), but `data/openings/` was not present alongside `backend/`.

### Silent Exception & Missing File Fallback ([openings.py:28-30](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/openings.py#L28-L30))
- When `OPENINGS_DIR` did not exist (or contained no `.tsv` files), `_load_openings()` set `_loaded = True` and returned silently without logging a warning or throwing an exception.
- `_openings_trie` remained empty (`{}`), causing `openings.classify(...)` to return `None` for every single move sequence. `pipeline.py` subsequently defaulted every finding's ECO to `"???"`.

---

### 2. Implemented Fix

1. **Package-Bundled Opening Data ([backend/openings_data/](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/openings_data/))**:
   - Bundled `a.tsv`, `b.tsv`, `c.tsv`, `d.tsv`, `e.tsv` directly inside `backend/openings_data/`.
   - `backend/openings_data/` is inside `backend/` and is **tracked in git** (not ignored by `data/.gitignore`). When `backend/` is copied/zipped for Kaggle, the opening data ships automatically with zero extra deployment steps.

2. **Robust Path Resolution Order ([openings.py:9-30](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/openings.py#L9-L30))**:
   - `_get_openings_dir()` resolves in order of priority:
     1. `CSZERO_OPENINGS_DIR` environment variable (if explicitly set).
     2. `backend/openings_data/` (package-bundled directory relative to `__file__`).
     3. `data/openings/` (legacy repository root path).

3. **Loud Logging ([openings.py:46-107](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/training/openings.py#L46-L107))**:
   - Added logger `chess_speak_out_loud.openings`.
   - Logs `logger.warning(...)` if opening directory is missing or empty, explicitly alerting operators that classification will fall back to `'???'`.
   - Logs `logger.info(...)` when opening variations are successfully loaded.
   - Logs `logger.debug(...)` if a row parsing error occurs instead of silent `pass`.

---

### 3. Verification & Test Results

- **Unit Tests ([test_openings.py](file:///c:/Users/Admin/Documents/chess_speak_out_loud/backend/tests/test_openings.py))**:
  - `test_openings_dir_resolution_order`: Verified priority resolution (env var > bundled `backend/openings_data` > legacy `data/openings`).
  - `test_missing_openings_dir_logs_warning`: Verified warning logging and state restoration.
  - Test results: **5 / 5 passed**.
- **Full Backend Suite**: `pytest backend/tests` — **165 / 165 passed** (100% green).
- **Dataset Requirement**: Shipping `backend/` in the Kaggle dataset automatically includes `backend/openings_data/*.tsv` (~387 KB). No manual external file download required.
- **Git Push**: Zero pushes made.
