# CONSULTATION — selftest

**Status:** UNAUDITED

## Claims table

| # | claim | tag | source | quoted text / command output |
|---|---|---|---|---|
| 1 | the motto is stated in CLAUDE.md | VERIFIED | `CLAUDE.md` | "LC0 is the ultimate coach" |
| 2 | a fabricated quote | VERIFIED | `CLAUDE.md` | "the engine achieves 99.7% accuracy on all positions" |
| 3 | cites a file that does not exist | VERIFIED | `backend/does_not_exist.py` | "some plausible text here" |
| 4 | external with no fetch date | EXTERNAL | https://example.org/paper | "a sentence" |
| 5 | inferred with no source | INFERRED | - | - |
| 6 | something I could not source | UNVERIFIED | - | - |
