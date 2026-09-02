# Mars Climate Orbiter — two teams, two unit systems, one lost spacecraft

**Lost 23 September 1999 on Mars orbit insertion. NASA JPL and Lockheed Martin Astronautics.**

## The situation

Ground software supplied by Lockheed Martin produced thruster impulse figures in **pound-force
seconds**. The JPL navigation software consuming them expected **newton-seconds**. The ratio is
about 4.45.

The error accumulated across months of small trajectory-correction manoeuvres, quietly biasing the
computed trajectory. The spacecraft arrived at Mars far lower than intended and was destroyed.

## Why it was not caught

This is the part worth studying, because the units mistake itself is trivial and the failure to
catch it was not.

**Both systems worked perfectly.** Neither had a bug in the ordinary sense. Each was internally
correct. The error lived in the *interface*, which is nobody's module.

**The discrepancy was visible and was not escalated.** Navigators had noticed anomalies in the
trajectory during cruise and had raised concerns, but the issue was not tracked to resolution through
a channel that could stop the mission.

**The end-to-end path was never tested with real data in both directions.** Each side tested its own
half.

The investigation board's finding was systemic rather than personal: the process failed to catch an
error that the process should have been designed to catch.

## The principle

**A frame — units, point of view, coordinate system, side to move — is an unstated contract, and
unstated contracts are where correct components produce wrong systems.** State the frame explicitly
at every boundary, and test the boundary end to end with real values, not each side separately.

## For us

This is the **POV/frame family** in `LEADER_BIBLE.md` §5, and it is the failure family this project
has suffered most often.

The record:

- **White-POV versus mover-POV centipawn signs**, throughout the metrics.
- **Black-to-move saliency** required a mirror *and* a rank flip; the old `saliency()` was frame-buggy
  for months and produced plausible pictures of nothing. The fix shipped as a new public function,
  `saliency_absolute(fen)`, because the old frame was baked into callers.
- **Opt #2 value-screen pruning:** `fen_after` is opponent-to-move, so a raw `value < -0.60` test
  prunes the mover's *winning* moves. Caught in spec review, before implementation.
- **The Lichess puzzle `fen` is one ply before the tactic.** Read naively it would have shifted every
  positive sample in the dataset by one ply, with no error and no crash.
- **Φ's meaning flips with the side to move.** I wrote `Φ(after) − Φ(before)` into both the README
  and the plan — subtracting *my* error-proneness from *the opponent's*. For ranking candidates it is
  harmless, which is exactly why it would have survived until someone extended it across plies.

Five instances of one failure family, in one project, over six weeks. That is not carelessness; it
is a structural property of a codebase where every quantity has an implicit observer.

**What actually works against it**, learned here:

1. **Canonicalise at the boundary.** `encode.py` flips the board so the side to move is always
   "us" — the frame is normalised once, at the edge, and never again.
2. **Test the boundary, not the halves.** `phi_net._unpack` was checked to produce *byte-identical*
   planes to `encode.unpack()` for three positions including a black-to-move one. That is the
   end-to-end test Mars Climate Orbiter never had.
3. **Make the frame part of the name.** `saliency_absolute` says its frame out loud.
