# Taiichi Ohno — go and see, and stop the line

**Toyota Motor Corporation, roughly 1950–1980. Ohno as the principal architect of the Toyota Production System.**

## The situation

Post-war Toyota could not afford the inventory buffers that let mass producers hide defects. A
defective part in a large-batch system is discovered late, after hundreds more have been made, and
the cost of the discovery is enormous. Toyota's constraint — no capital for buffers — forced a
different answer: find the defect at the moment it is created.

## What was done

Three practices, all about closing the distance between a manager and reality.

**Genchi genbutsu** — "go and see for yourself, at the actual place". A manager investigating a
problem goes to the floor and observes the process, rather than reading a report about it. Ohno is
associated with the practice of standing in a chalk circle on the shop floor for hours, watching one
operation until he could see what was actually happening as opposed to what was supposed to happen.

**Jidoka and the andon cord** — any worker who sees a defect may stop the line. This is the
counter-intuitive one, because stopping the line is expensive and visible and the authority is given
to the most junior person present. The reasoning: a defect that passes is multiplied by every unit
built after it; a line stopped now is bounded.

**Five whys** — ask why repeatedly to reach the cause rather than the symptom. Ohno's canonical
example runs from a stopped machine through an overloaded fuse and an insufficiently lubricated
bearing to a worn pump shaft with no strainer — the actual fix being at the fifth answer, not the
first.

## Why it worked

Because it inverted where authority to halt sat. In most systems, escalating a suspicion costs the
escalator and is therefore rationed; at Toyota the default was reversed and stopping was cheap and
expected.

And because it treated **the report as a lossy encoding of the thing**. Ohno's circle exists because
a report tells you what someone believed happened.

## The principle

**Go to the object. Give whoever can see the defect the authority to stop. Ask why until you reach
something you can change.**

## For us

*Go and see* is already doctrine — `LEADER_GROUNDING.md` §3c.5: *inspect the artefact in the form
the recipient receives it. The PDF, not the .tex. The diff, not my intention for the diff.* The
practice that has repeatedly paid: on 2026-09-01 I ran `build_sac_session()` instead of reading it,
and found it returning `0`.

*Stop the line* is where we are genuinely strong and genuinely weak at once.

**Strong:** the brief's stop-and-ask rule explicitly says a stop with a clear question is a
successful delivery, and *"a fired alarm is a stop, not a parameter."* Gemini has stopped correctly.
The A4 alarm stopped a dataset build. `b1_verdict` stops a Kaggle session.

**Weak:** almost nothing in the *running system* can stop the line. `sac_drill` returned an empty
list as an answer for five weeks and no andon cord existed to pull. The empty list was indistinguishable
from a legitimate "no findings". Ohno's insight applies exactly: **a silent wrong answer is worse
than a halt**, and our failure catalogue calls this the SILENT factor in the rigour formula. The
answer is not more review; it is more assertions inside the code that make an impossible state
crash instead of returning a plausible value.

*Five whys*, applied to today's eight defects, does not stop at "I forgot to thread `--no-amp`". It
runs: why → I changed a signature and did not check callers; why → I have no mechanical step that
enumerates call sites; why → my review habit is semantic (does this make sense) rather than
exhaustive (where else is this named). The fix is at the fourth answer, and it is `grep`.
