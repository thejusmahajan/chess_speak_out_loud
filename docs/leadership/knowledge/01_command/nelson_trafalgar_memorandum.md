# Nelson's Memorandum — the order for when the orders cannot arrive

**Royal Navy, Trafalgar Memorandum of 9 October 1805; the battle fought 21 October 1805.**

## The situation

A fleet action in the age of sail was fought inside cannon smoke. Signal flags were the only command
channel, and within minutes of the first broadside nobody could see them. Whatever a commander
wished to say during a battle, he largely could not.

## What was done

Nelson wrote his plan down and briefed it to his captains **before** the fleet sailed — he called
them the band of brothers, and the briefing was as much of the mechanism as the document. The
Memorandum explained the intent: break the enemy line in two places, bring on a close-quarters
melee, and prevent the enemy van from supporting the rear.

Its most famous sentence is the one that matters here, and it is genuine:

> "…in case Signals can neither be seen or perfectly understood, no Captain can do very wrong if he
> places his Ship alongside that of an Enemy."

That is a **default action for the case where command has failed**. Not a hope that command will not
fail — an instruction for when it does.

## Why it worked

Two reasons, and the second is the one usually missed.

First, the intent was understood in advance by everyone who would have to act on it, so the fleet
could execute without instruction.

Second, the fallback was *specific*. "Use your judgement" is not a fallback; it is an abdication
dressed as trust. "Lay your ship alongside an enemy" is a concrete action that is nearly always
better than hesitating, and it can be carried out by a captain who knows nothing except that he has
lost contact.

## The principle

**Brief the intent before the work starts, and write down the specific default action for the case
where communication fails.** A fallback that requires judgement is not a fallback.

## For us

We have the first half and keep rediscovering that we need the second.

Every brief carries a **STOP AND ASK** section, which is a good fallback — but it is a *stop*, and a
stop is only correct when stopping is safe. The Kaggle work exposed the gap: a worker eleven hours
into a session, on a machine I cannot reach, with the notebook about to be killed by a hard cap, has
no useful way to stop and ask me anything. The watchdog that flushes the cache and exits cleanly at
11h15m is Nelson's sentence in software: *when you cannot reach the commander, here is the specific
thing to do.*

The same reasoning produced `b1_verdict`. "If B1 looks bad, use judgement" would have been an
abdication. "Continue unless F0 fails or Φ fails to beat the material baseline" is an action a
process can take at 3 a.m. with nobody watching.

**Where we are still weak:** the briefs' stop-and-ask lists what is *not covered*, but rarely says
what to do instead. That asymmetry is worth fixing.
