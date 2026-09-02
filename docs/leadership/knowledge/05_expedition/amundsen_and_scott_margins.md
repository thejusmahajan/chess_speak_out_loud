# Amundsen and Scott — margins, not heroism

**Race to the South Pole, 1911–12. Amundsen reached the Pole 14 December 1911 and returned with all men. Scott reached it 17 January 1912 and died with his four companions on the return.**

## The situation

Two expeditions, similar era, similar technology, comparable resources, opposite outcomes. The
difference is usually told as luck or as national character. The operational differences are more
instructive and are documented.

## What differed

**Transport.** Amundsen used dogs, understood as a system: dogs pulled, and surplus dogs were
planned from the start as food for the remaining dogs and men. Scott relied on a mixture of motor
sledges, ponies and man-hauling — three systems, each with its own failure modes, and ponies are
poorly suited to the surface and cold.

**Depots and margins.** Amundsen's depots carried large surpluses. Scott's plan ran closer to the
minimum, which meant an unremarkable delay became an existential one.

**Finding the depots again.** This is the detail that best repays study. Amundsen marked each depot
with a line of flags placed at right angles to the line of travel, extending several kilometres to
either side. A navigational error of a few kilometres therefore still intersected the marker line.
Scott's depots were marked more sparingly, so finding one required navigating accurately to a point.

**Specialisation and rehearsal.** Amundsen's party were expert skiers and dog drivers; equipment was
tested and modified beforehand.

**The changed plan.** Scott took a fifth man on the final push, on a plan and rations organised for
four.

## Why it matters

Amundsen's margins were not timidity, and they are the reason the expedition looks unexciting. The
flag lines are the clearest instance of a general principle: **build for the error you will
certainly make, not for the performance you hope to achieve.** He did not assume he would navigate
accurately; he made accurate navigation unnecessary.

Scott's expedition produced far better stories. That is part of the lesson.

## The principle

**Design so that the expected error is survivable.** A plan that requires everything to go right is
not a plan. And the exciting version of a project is usually the one with insufficient margin.

## For us

**Where the flag-line principle is already in force:**

- The **EPD cache** makes the whole profile pipeline crash-resumable: a session that dies has still
  banked its work, and the next run picks it up free. That is a depot you cannot miss.
- The **11h15m watchdog** exists because Kaggle's hard 12-hour kill discards the working directory.
  Without it the run must finish accurately; with it, an overrun is survivable.
- **`--no-amp`** is a flag line for the one code path nobody has executed: if mixed precision
  misbehaves, there is a tested route through.
- **`resolve_data_dir`** accepts flat, nested, or still-archived mounts. I do not know which shape
  Kaggle will produce, so I stopped needing to know.

**Where the margin is thin and I should say so:**

- The dataset lives in exactly one place. `data/` is gitignored, so `config_steering` exists on one
  laptop with no backup. Uploading it to Kaggle is the backup, which is why it is worth doing even
  before the run.
- The **fifth man on rations for four**: this corpus, written while the interview is the live
  deadline item, is an addition to a plan whose margins were set without it.
