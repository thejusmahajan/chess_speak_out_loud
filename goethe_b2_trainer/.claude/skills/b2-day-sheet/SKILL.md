---
name: b2-day-sheet
description: Build, check and ship the Goethe B2 sprint day sheets (study_materials/b2_sprint/day_NN.md) and their Anki decks. Use whenever Thejus asks for "today's learning script", "the b2_sprint", a day sheet, a missed day, or a review of existing sheets.
---

# Goethe B2 sprint: building a day sheet

Thejus studies three hours a day from one printed Markdown sheet, for the Goethe-Zertifikat B2 on **Do 10.12.2026** (Schreiben and Sprechen; Sprechen is his weakest skill). This skill is the procedure and the lessons from building Days 1–9. Paths below are relative to `goethe_b2_trainer/`.

## 1. Which sheet, and which are missing

```
python scripts/verify_day_sheet.py plan 2026-10-26
```

This prints the sheet that belongs to the date, its calendar row, the words and loci due for review, whether it is a Sunday, and **every earlier sheet not built yet**. Use the conda env `C:\Users\Admin\miniconda3\envs\cszero\python.exe` and set `PYTHONIOENCODING=utf-8`.

- **The calendar is exact (Thejus, 25.10.2026).** Every sheet is built for **its own plan date**, as if studied that day. Missed days still get their own sheet; he catches up in free time. **Never merge days and never re-date a sheet** to the day it is actually done. This overrides the generator's slip rule ("merges two later days"); keep printing the slip rule in the header, but do not apply it.
- "Today's learning script" = the sheet for today's date **plus** any missing earlier sheets. Build them oldest first; each one's Tomorrow line must name the next sheet on the calendar.
- Reviews are counted from the **plan dates**: a batch learned on day D is due on D+1, D+3, D+7, D+14 and D+30. The Sunday error-type rewrite goes only on sheets whose plan date is a Sunday.
- Dates: Days 1–12 run Sa 17.10.–Mi 28.10.; the merged sheets 13–14, 15–16 and 17–18 fall on 29., 30. and 31.10.; from Day 19 on, Day N is 13.10. + N days (Day 19 = So 01.11., Day 57 = Mi 09.12.).

## 2. Sources, and only these

The kit is the specification and the only content source: `knowledge/b2_kit_to_produce_daily_work_material/goethe_b2_kit.zip`. Read it with `unzip -p … goethe_b2_kit/<file>`, or extract it into the scratchpad, never into the repo.

| File in the kit | Use |
| --- | --- |
| `01_generator_prompt.md` | **Read it in full every time.** The calendar (§4), the sheet skeleton (§5), the block rules (§6), his style (§7), the Palace A frame bank (§8), the speech rotation (§9) and the checklist (§10). |
| `02_toolkit.md` | §4 the plan rows (from Day 19), §5 palaces, §6–§11 frames, tasks and models, §13 grammar, §15 AI prompts, then the Wortschatz tab. |
| `03_speech_log.md` | His seven talks; print the **German version** only. |
| `daily_sheets/day_01.md` | The original format reference. The newest sheet in `study_materials/b2_sprint/` is the current one. |

`knowledge/exam_prepration_guidelines_gemini_research/split_and_study_prompt.md` is an **older, superseded spec** (different timetable, "Pl. wie Sg." rule). Do not follow it.

## 3. Rules learned the hard way

**Copying**
- Copy word batches, grammar points, frames, worked examples, locus images, speeches, routines, register traps and model texts **verbatim**. You write only exercises, answers, practice topics and models "in his style", and every one of those gets checked (§5).
- Wortschatz Grammar column: `–` becomes `kein Pl.` **on nouns only** (der/die/das). On verbs and adjectives it stays `–`. A lone `-` (plural = singular, e.g. *das Anliegen*) stays `-`, with one explanatory line under the table. Never write "Pl. wie Sg.": the Anki generator would colour the noun as a plural.
- Palace A frames come from the generator's §8 bank (his style). **Palace B, C and D come from the toolkit unchanged**, because his argumentative style does not belong in a formal email.
- Palace B frame codes were introduced on Days 8–9 and are **fixed now**, because Anki card IDs hang on them: `Anrede-1…4`, `Anlass-1…5`, `Situation-1…6`, `Entschuldigung-1…4`; Days 10–12 added `Verständnis-1…5` (1–2 ask for it, 3–5 show it), `Bitte-1…3`, `Vorschlag-1…3`, `Angebot-1…2`, `Frage-1…2`, `Schluss-1…4`, `Gruß-1…2`. That is all of toolkit §8, forty codes. Never renumber.
- A Wortschatz phrase that starts with an article but ends in a verb (*die Initiative ergreifen*, *das A und O sein*) is not a noun: its `–` stays `–`, and the verifier knows this.

**Writing what is not copied**
- **Model forum posts: 170–190 words. Every paragraph needs at least two sentences**, because the sheet's own final check (item 1) demands it and three of my models broke it. Model emails: 110–130 words. The `(N words)` in the summary must be the counted number.
- **Practice scenarios must make sense.** "Something came up" plus "I forgot the appointment" is a contradiction that teaches nothing. Read each answer as the situation it claims to be.
- **Round two of a speech** (Days 8–12) uses a different E-frame *and* a different opinion sentence from round one. Open the earlier sheet and check.
- **Labels must match content.** A drill labelled "station 4, Beispiel geben" must actually use an example frame.
- **Colours and images follow the bank's image text** (the bank's statue of *der Staat* is blue; I once painted it red).
- **No unsourced claims**, such as scoring rules or facts the toolkit does not state. Keep claims in the German soft (*Ich habe den Eindruck, dass …*).
- **Forward references** ("comes back on Day 11") must be checked against the calendar.
- English instructions name people in the nominative ("write to Herr Lange"); only the German teaches *Herrn*.
- Every exercise has an Answers block (`<details><summary>Answers</summary>` plus a blank line), warm-up drills included. Checkboxes on every task. Clock times run 0:00–3:00 without gaps.
- Keep his professional background out. Use only everyday personal anchors.

**What the Anki generator expects** (`scripts/day_sheet_to_anki.py`; break these and cards silently vanish)
- `# Day N · Wd dd.mm.yyyy · …`, and `## Block 4 · Grammar: G3 Nebensätze II · 1:15–1:35`.
- Word batch: `### W04 · Title — …` with the `Deutsch | Grammar | English | Example` table.
- `### The frames`: a table with `Code | Use it when | Frame | Grammar to watch | …`. Use `Use it when` as the column name even where the bank says "The task asks for".
- `### The frames filled in…`: bullets `- **CODE · Topic:** text`.
- `### Say it with a new topic`, `### Cloze`, `### 10 new transformations…`: numbered items, answers numbered inside `<details>`; cloze and transformation answers carry the rule after ` — `.
- Paragraph tasks: a section heading with "… paragraphs", a `Task | Task point | Your frame` table and models as `- **F10 · V-2:** text`.
- Error lines: `✗ *wrong* → ✓ *right* rule`.
- Locus box: `**Locus 4 — Dining table.** Words the image holds: *…*`, a blank line, then `Image: …`. For other palaces: `**Palace B · Locus 1 — Entrance.** …`.

## 4. Verify, then ship

1. `python scripts/verify_day_sheet.py check study_materials/b2_sprint/day_NN.md`. It checks copied German against the kit, model word counts and two-sentence paragraphs, clock contiguity, header and Tomorrow dates, and that the Sunday task appears only on Sundays. It must say `0 failed`.
2. **Backward pass by hand.** The script cannot judge the German you wrote. Read every answer, model and practice item for verb position, case, endings, commas, logic and labels. On Days 5–9 this pass found 16 errors after the script had passed.
3. `python scripts/day_sheet_to_anki.py study_materials/b2_sprint/day_NN.md`, and check the note counts per subdeck are plausible (frames + say-it items + cloze items + paragraphs + loci).
4. If you changed either script: mutation-check it. Break one copied word in a **copy** of a sheet, confirm the check fails, and confirm the break was actually applied (a `sed` that matches nothing proves nothing). Then rerun all sheets: Days 1–3 must still rebuild to 85, 95 and 55 notes.
5. Commit only the sheet, its `.apkg` and any script you changed. **Never** add `subtitles/` (held back pending a publishing decision) or `to_del_sample_email.txt`. Write the message as "what and why", with the Co-Authored-By line, then `git push origin windows-dev` and confirm `git status` is not ahead.

## 5. What the verifier does not cover yet

Palace C and D frames from toolkit §5/§10/§11, the Mustervortrag texts, the discussion bank rows, and the AI prompts. Copy those with extra care, or extend `check_toolkit_pieces` before Day 15, when they start to appear.

## 6. Running it headless

`claude -p "…"` prints nothing until the whole job ends, and one sheet takes 10 minutes or more, so it looks hung. On 25.10. it was interrupted after 4 minutes, having written nothing. Run it interactively, or add `--output-format stream-json --verbose` to watch the progress.
