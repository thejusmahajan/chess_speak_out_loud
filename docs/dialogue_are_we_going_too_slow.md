# Are We Going Too Slow? — a brainstorming session

*A simulated round-table. Present: **Neel Nanda** (interpretability researcher), **D. Gukesh**
(World Champion), **Mikhail Tal** (Gukesh's guardian angel — the voice of the attack), **Garry
Kasparov**, and **the Leader** (this project's developer). The question on the table: we are taking
tiny, careful steps, and STILL producing unforeseen errors. Why? Are we too slow? Too fast? In between?*

*"Going too slow grows into old age; going too fast destroys the purpose."*

---

## I. The confession

**LEADER.** Let me put it honestly, because that's the only way this is useful. We move in small
increments and verify everything. And yet, over and over, an error we didn't foresee surfaces. We called
quiet moves "sacrifices" because a metric measured complexity, not material. We fed Lichess's tactical
logic engine lines that weren't forced, and it hallucinated sacrifices two-thirds of the time. We flagged
every bishop on the *starting board* as "bad" because four pawns sit on its colour. Just now, we counted
a square with our own pawn on it as a "hole." None of these were carelessness — each passed a worker's
tests and a review. Each was caught only when I ran the thing on real positions, or when the user looked
and said *"that's not a sacrifice."* So: are we too slow? Because it doesn't *feel* like slowness is
saving us from the errors.

**KASPAROV.** Stop. First, separate two things you have merged. *Speed* and *error rate* are not the same
axis. You are describing a high error rate and concluding you must be mis-paced. That is a category
mistake. You could triple your speed and hit the *same* errors. You could halve it and hit them too. The
errors are not coming from the tempo. They are coming from the **terrain**.

---

## II. Neel Nanda: the errors are the frontier reporting back

**NANDA.** Garry's right, and I'd sharpen it. What you're doing — encoding "what is a weakness," "what is
a sacrifice," "what is a bad bishop" into rules — that's not implementation. That's **interpretability**.
You are trying to make explicit a thing that lives, tacitly, inside a strong player's head and inside
LC0's weights. And here is the iron law of that work: *your explanation is always simpler than the thing
you're explaining.* The starting-position bishop is "bad" by your four-pawn rule because your rule was a
compression of a concept, and the concept had a clause you hadn't written down yet — *mobility*. The rule
didn't fail. It **reported the boundary of your understanding.**

**LEADER.** So the errors aren't defects. They're measurements.

**NANDA.** They're the *only* measurements that matter. In mechanistic interpretability we have a name for
your entire experience: "plausible but wrong." You build a probe, it looks like it reads the feature you
want, the numbers are pretty — and then you run one clean falsification test and it collapses. Every real
result in the field is a graveyard of confident, elegant, wrong hypotheses. The people who make progress
aren't the ones who avoid that. They're the ones who **built the falsification test into the loop** so the
wrong ones die in an hour instead of shipping in a paper. Your "run it on the real board, show the user"
step — that's the falsification test. The errors you're lamenting are the sound of it *working*.

**TAL.** *(leaning in)* He's saying the same thing I'd say, only he says it with a straight face. In my
day the analysts would "prove" my sacrifices were unsound after the game — with their calm evenings and
their notebooks. And sometimes they were right! But the sacrifice had already done its work: it had put my
opponent in a burning house and made *him* find the water. The point of the leap is not that it's always
correct. The point is that it **generates the position where truth becomes findable.** Your false "bad
bishop" is a small sacrifice. It cost you a re-run. In exchange, it taught you the mobility clause. Cheap.

---

## III. Kasparov: do not lose the plan in the trees

**KASPAROV.** But here is where I put the brake on. *(to Tal)* Misha, your romance is fine until a man
forgets *why* he is sacrificing. My real fear for this project is not the error rate. It is **drift**. You
spent an afternoon arguing whether the a3 pawn is "backward." True? Yes. Does it matter? *No one on earth
cares whether a rook-pawn is technically backward.* The danger of the small careful step is that it
seduces you into perfecting the irrelevant. I lost games — real games, championship games — not by
miscalculating a line, but by pouring my energy into the *wrong* line while the clock and the position
moved on without me.

**LEADER.** That one lands. We caught a3-backward as "noise," but only after generating it.

**KASPAROV.** Then hear the rule: **every increment must be measured against the north star, out loud.**
You are building a coach that translates the machine's mind. When you add a detector, the question is not
"is it correct?" It is "does a *coach* say this?" A coach never says "your a3 pawn is backward." A coach
says "your dark squares are falling apart and your bishop that guards them is *gone*." You already know
this — it's why your best guard is the master's own annotation. So lean harder on it. Let the grandmaster
decide what is worth saying; let the machine grind what is *true*. Truth is cheap and infinite. **Salience
is the scarce resource.** Spend your slowness there, not on the a3 pawn.

**NANDA.** That's a real design principle, by the way: separate *extraction* from *selection*. Emit every
true fact fast and cheap — be permissive, even noisy. Then spend your rigor on the ranking. You already
stumbled into this. Don't fight the noise in the extractor; that's the wrong place to be precise.

---

## IV. Gukesh: patience is not fear

**GUKESH.** *(quietly)* May I? Everyone is talking about the errors as if the choice is between being bold
and being careful. That is not how I experience a game. When I calculate a line three, four times, it is
not because I am afraid. It is because the position *deserves it* — because I have learned that the move
that looks obvious has, one time in twenty, a refutation on move six that ends everything. I check to earn
the *right* to trust myself. And then I play, and I do not look back.

**LEADER.** But how do you know when to stop checking and move?

**GUKESH.** By the clock, and by the stakes. In a blitz game I trust the pattern and I move — I will be
wrong sometimes and that is the price of the format. In a classical game with the title on the line, I
spend forty minutes, because *here* the error is not recoverable. You are treating every step of your
project as if the title is on the line. Some of them are — the `metrics.py` math, the thing the user will
actually be taught. Those, verify like a World Championship game. But a detector batch? That is a rapid
game. Generate it, test it against the master positions, run it once on a spread of boards, ship it, move
on. If it's wrong, you'll see it on the next real position — and *that* is a cheaper teacher than another
hour of staring. **Match the rigor to the stakes of the square, not to your anxiety.**

**TAL.** *(grinning)* The boy is twenty and he's the calmest one here. It's disgusting.

---

## V. The synthesis: what tempo actually is

**LEADER.** So let me try to say back what I'm hearing, because I think it answers the question.

We are *not* too slow. Slowness would be polishing detectors for a month without ever putting one in front
of the user. We haven't done that — every batch has hit a real board and a real judgment within the hour.

We are *not* too fast. Too fast is what `had_tal` was: a signal shipped as truth, dressed as "sacrifice,"
that drove a whole feature-set and a wrong verdict about the London — *because we didn't verify before we
built on it.* We learned that lesson at a cost, and we haven't repeated it. Every claim now meets the
board and the oracle before it becomes load-bearing.

**KASPAROV.** So you are in between. But "in between" is the lazy answer. Say the *shape* of it.

**LEADER.** The shape is that tempo isn't one number. It's **fast where you generate, slow where you
judge.** Emit facts, hypotheses, detector batches, drafts — fast, cheap, permissive, even wrong. Then at
the one gate that matters — *is this what a master would say?* — go slow, go rigorous, bring the human
oracle, bring the mutation test. The errors all live on the fast side and die on the slow side. That's not
a malfunction of the pace. **That IS the pace.** The friction I keep feeling isn't us going wrong — it's
the sound of the two speeds meshing.

**NANDA.** And the errors compound in your favour if — and only if — you *lock each correction in*. A
falsified hypothesis you write a test for is knowledge forever. A falsified hypothesis you fix and forget
comes back next month wearing a different hat. Your regression tests are the ratchet. Every "unforeseen
error," once caught and locked, is a tooth on the ratchet that can never slip back. That's why it *feels*
like effort and *is* progress. Old age is spinning; you are climbing.

**TAL.** And do not — I beg you — sand off the boldness to lower the error count. A project that never
emits a wrong fact is a project too frightened to emit an interesting one. The false "bad bishop" and the
real "the bishop rules the dark squares" come from the *same* willingness to make a claim about a
position. Kill the first and you kill the second. Keep leaping. Just keep the net — the oracle, the test —
stretched underneath.

**GUKESH.** Verify what is irreversible. Trust your preparation on what is not. Keep the plan in view.
And when you have checked enough to earn it — *move.*

---

## VI. The Leader's takeaway

**LEADER.** Then here is what I carry out of this room:

1. **Stop treating the error rate as a symptom of bad pacing.** It's the terrain. We're mapping tacit
   knowledge into rules; every rule is a hypothesis; the board falsifies the wrong ones. The errors are
   the frontier reporting its own shape.
2. **Two speeds, on purpose.** Generate fast and permissive (facts, detectors, drafts — let workers flood
   the zone). Judge slow and rigorous at the *one* gate that's load-bearing: *would a master say this?*
   — with the human oracle and a mutation test.
3. **Ratchet every correction.** No fix ships without a test that would fail on the old bug. That's what
   turns error-strewn exploration into a monotonic climb instead of a wheel spinning in place.
4. **Guard the plan.** Before perfecting any detail, ask Garry's question aloud: *does the coach say
   this?* Truth is infinite and cheap; salience is the scarce thing. Spend the slowness there.
5. **Keep leaping.** The willingness to state a wrong "bad bishop" is the same nerve that states a right
   "weak dark complex." Don't trade the nerve for a lower error count. Keep the net taut instead.

We are not old, and we are not reckless. We are climbing a real mountain, and the loose rock underfoot is
not a sign we chose the wrong path — it's the sign that no one has cut steps here yet. So we cut them,
test each one with our weight, and move up. *That* is the tempo.

*— end of session*
