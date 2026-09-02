# Crew Resource Management — the discipline invented because juniors would not contradict captains

**Tenerife, 27 March 1977: two Boeing 747s collided on the runway at Los Rodeos; 583 deaths, the worst accident in aviation history. CRM developed through the late 1970s and 1980s, initially at NASA and United Airlines.**

## The situation

Fog. A diverted, congested airport. A KLM captain who was the airline's chief of flight training —
the most senior pilot in the company, the man who trained and examined other captains — under
pressure from duty-time limits.

## What happened

The KLM aircraft began its take-off roll without unambiguous clearance. The cockpit voice recorder
shows the flight engineer raising it:

> Flight engineer: "Is hij er niet af dan?" — *Is he not clear then?*
> Captain: "Wat zeg je?" — *What do you say?*
> Flight engineer: "Is hij er niet af, die Pan American?"
> Captain (emphatically): "Jawel." — *Oh yes.*

The engineer did not press it. The 747 collided with the Pan Am aircraft still on the runway.

Contributing factors included non-standard phraseology — the KLM co-pilot's "we are now at take-off"
was ambiguous — and simultaneous radio transmissions producing a heterodyne squeal that masked the
Pan Am crew's report that they were still on the runway.

## What was built from it

**Crew Resource Management**: the systematic training of cockpits as teams rather than as a captain
plus assistants. Its content is unglamorous and specific:

- **Standard phraseology.** "Take-off" is now used only for an actual clearance; departure is
  otherwise called "departure".
- **Explicit challenge protocols.** A junior crew member has a defined, trained script for
  escalating a concern — state the observation, state the concern, propose an alternative, and if
  unresolved, demand a response.
- **The two-challenge rule.** If a concern is raised twice without a satisfactory answer, the
  challenger is expected to assume incapacity and take control.
- **Briefings that explicitly invite challenge.** The captain says, at the start, that he expects to
  be corrected.

The gradient of authority was identified as a hazard and engineered against.

## The principle

**Steep authority gradients destroy information.** The correction is not to tell juniors to be brave;
it is to give them a scripted, expected, low-cost mechanism for challenging, and to make seniors
publicly solicit it.

## For us

There are two authority gradients here and they point in opposite directions.

**Thejus → me.** He is the ground-truth oracle and has been right against my analysis repeatedly.
The mechanism that carries his challenge is `trainer/state/comments.jsonl` — and it failed exactly
as Tenerife failed. A comment reading *"I don't see the question here!"* sat unread for ten hours
while a leader committed six of his comments without reading one. It was a correct bug report from
the person actually looking at the running app. `CLAUDE.md` Step 0 now mandates reading that queue
at session start, which is a channel fix, not an exhortation.

**Me → Gemini.** Here I am the captain, and the failure mode is the mirror image: a worker that
does not push back hard enough, or pushes back and is overruled by someone who sounds authoritative.
The brief's stop-and-ask rule is our challenge protocol — *"a stop with a clear question is a
successful delivery"*, *"a fired alarm is a stop, not a parameter"* — and it has been used correctly.

**Where I violated the principle explicitly.** The brief I wrote on 2026-09-01 contained the line
*"Do not agree by default. A proposal you cannot see a serious objection to is a proposal you have
not thought about hard enough."* Thejus deleted it by hand. That is the opposite of a challenge
protocol: it manufactures objection rather than inviting it, which produces theatre and buries real
dissent in noise.

**The two-challenge rule is the piece we do not have.** If Gemini flags something twice and I
overrule it twice, nothing escalates. On 2026-09-02 I reduced the severity of two of its findings
after measuring — correctly, I believe, and the measurements are in the record. But the record is
mine, and there is no mechanism by which a second Gemini challenge reaches Thejus over my head.
