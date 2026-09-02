# LeMessurier and the Citicorp Center — the engineer who reported himself

**New York, 1978. William LeMessurier, structural engineer for the Citicorp Center (now 601 Lexington Avenue). The definitive public account is Joe Morgenstern's "City Perils: The Fifty-Nine-Story Crisis", *The New Yorker*, 29 May 1995.**

## The situation

The tower had an unusual design: it stands on four columns placed at the *midpoints* of its sides
rather than at the corners, to leave room beneath for a church that had to remain on the site. That
configuration made the building unusually sensitive to **quartering winds** — wind striking a corner
rather than a face.

LeMessurier had designed for it. His calculations accounted for quartering winds and the building was
safe as designed.

## What happened

In 1978, prompted by a question from a student, LeMessurier re-examined the structure and discovered
two things in combination.

First, his own analysis had not treated quartering winds as a governing case for the diagonal
wind-bracing members in the way the built structure required.

Second, and decisively: the contractor had **substituted bolted joints for welded ones** in those
braces. The substitution was made through proper channels, was cheaper, and was approved by his own
firm's New York office as satisfying the code. It was code-compliant. It was also substantially
weaker against the quartering-wind case.

Running the numbers, LeMessurier concluded the building could fail in a storm of a magnitude
expected roughly once every sixteen years — and that the tuned mass damper, which reduced sway,
required electrical power that a severe storm might cut.

It was hurricane season.

## What was done

He told them. He went to his insurers, to the architect, to Citicorp's executives, and effectively
handed them a disclosure that could have destroyed his career and his firm.

The repair was carried out at night, through the autumn of 1978, welding two-inch-thick steel plates
over more than two hundred bolted joints, while the building remained occupied by day. Emergency
evacuation plans were drawn up with the Red Cross. Hurricane Ella approached the coast during the
work and turned away.

The building was made stronger than its original design. Because of a newspaper strike and a
deliberate decision not to publicise, the episode stayed largely unknown for seventeen years.

## The principle

**When you find your own error, the cost of reporting it is always lower than the cost of the
failure you are gambling against — and the calculation is not yours to make privately.**

## For us

This is not an abstract case here. **It is the story Thejus tells about himself in job
applications**, and the reason this repository is shaped as it is:

> *"I found two silent correctness bugs in my own interpretability pipeline, one after publication,
> and corrected them publicly."*

The BT3 history-planes bug — 84 of 112 planes left empty by bare-FEN input — was found after
publication and the posts were corrected. The attention frame bug produced plausible pictures of
nothing, and it is written up in `docs/writeup_attention_frame_bug.md` as a portfolio piece rather
than buried.

That is LeMessurier's move, and it is worth understanding *why* it works as a credential. Anyone can
claim rigour. Publicly correcting your own published work is the only evidence of it that cannot be
faked, because it costs something. The reason the story is an asset in an interview is precisely the
reason it felt bad to do.

**The standing obligation it creates.** Everything in this project inherits that standard, which is
why:

- Φ's honest limit is written into the README and the notebook: it learns *what a human in the
  1500–2200 band gets wrong*, not objective attacking potential — and *must never be claimed as
  more, anywhere, including in a job application.*
- The CNP result is recorded as **4.42× worse on CRPS than the exact GP posterior**, which is the
  correct outcome and is never to be phrased as a win.
- The corrections this week — my frame error, my B1 gate trap, my `subprocess.call` regression — are
  in commit messages and audit files under my own name, not quietly patched.

The moment that discipline lapses, the career story stops being true.
