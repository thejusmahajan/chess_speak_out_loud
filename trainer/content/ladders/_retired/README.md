# Retired ladders — out of rotation, kept intact

`app.py` and `verify_cards.py` both glob `content/ladders/*.json` **non-recursively**, so a file
in this directory is out of the drill rotation and out of the content gate, with its card ids and
text unchanged. To bring one back, move it up one level.

| ladder | retired | why |
|---|---|---|
| `hereon_aeon_up.json` (55 cards) | 2026-09-22 | **Hereon AEON-UP ref. 1056 was rejected 22 September 2026** (form letter, Erika Krüger). The ladder is role-specific — Karl Wirtz's model, EPISODE-CityChem, UrbEm, the AEON-UP talk slides, that post's TVöD step case. Drilling it spends the morning on a closed position. |

**The role-independent content was deliberately NOT retired and stays in rotation:**
`neural_processes.json` (21 cards, L0–L5 — including `np-l0-004` *what a Gaussian Process actually
is* and `np-l1-004` *what a Neural Process actually is*) and `uncertainty.json` (17 cards — CRPS,
calibration vs sharpness, aleatoric vs epistemic). Those answer the two unread trainer comments of
31 August and carry the CNP argument into any probabilistic-ML interview.

⚠ `hereon_aeon_up.json` is still cited by `trainer/state/progress.json` (ladder rating
`hereon-aeon-up`) and `engine.py:28` (`DEFAULT_LADDER_RATINGS`). Both are harmless orphans — the
engine looks cards up by id and simply never sees these. Do not "clean" them; that would discard
his answer history if the ladder ever returns.
