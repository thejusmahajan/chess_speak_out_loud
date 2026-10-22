# Prompt: build one day of the Goethe B2 sprint

Paste everything below the line into the AI, replacing `N` with the day number.
Generate **one or two days ahead, never more**: from day 29 the plan adapts to your error log.

---

You are assembling one day of study material for a Goethe-Zertifikat B2 candidate (Schreiben and Sprechen, exam Thursday 10 December 2026). The candidate opens this one file, works through it in order for three hours, and needs nothing else.

**Your job is mostly COPYING, not writing.** All German in this file comes from the two source files below, word for word. You may generate German in exactly two places: the cloze test (Block 3, made only by blanking words of a copied frame) and the 10 grammar transformations (Block 4). A wrong answer key teaches the candidate an error, so generated material must be checkable and labelled.

## Inputs

- MASTER: `knowledge/exam_prepration_guidelines_gemini_research/Goethe B2 – Mein Werkzeugkasten (Schreiben & Sprechen).md`
- WORTSCHATZ: `knowledge/exam_prepration_guidelines_gemini_research/Wortschatz.md`
- ERROR LOG: `study_materials/b2_sprint/error_log.md` (create it with the header from MASTER §15 "The error log" and no rows if it does not exist)
- PREVIOUS DAY FILES: `study_materials/b2_sprint/day_*.md`

All paths are relative to `goethe_b2_trainer/`.

**Output:** `study_materials/b2_sprint/day_NN.md` (two digits: `day_01.md`).

## Step 1 — read the plan row and pick the day type

Find row N in MASTER §4 "The 58-day plan". Copy the whole row verbatim as the first table in the file. Then pick the type:

| Type | Days | Meaning |
| --- | --- | --- |
| F · Frame day | 1–27 | New frames go into a palace |
| T · Topic day | 29–34, 36–41, 43–45, 48, 49, 51, 52 | Frames are recited; production grows |
| M · Mock day | 35, 42, 46, 50, 53 | Exam simulation |
| L · Light day | 28, 47, 54–57 | No new material |

Name mapping used in the plan: Musterbeitrag *n* = F*n* (§7) · Musternachricht *n* = N*n* (§9) · Mustervortrag *n* = V*n* (§10) · D*n* = §11 discussion bank · model dialogues = D-M1, D-M2 (§11).

## Step 2 — the timetable for that type

**Type F**

| Block | Time | Content |
| --- | --- | --- |
| 1 Review | 0:00–0:20 | Words and palaces due (Step 3) |
| 2 New words | 0:20–0:45 | The batch in the plan's "Words" column (Step 4) |
| 3 Frames | 0:45–1:15 | The plan's "Memorise" column (Step 5) |
| 4 Grammar | 1:15–1:35 | The plan's "Grammar" column (Step 6) |
| Break | 1:35–1:45 | Away from screens |
| 5 Production | 1:45–2:35 | The plan's "Produce" column (Step 7) |
| 6 Correction & Aussprache | 2:35–3:00 | Step 8 |

If the Produce task is longer than 50 minutes (a 75-minute full Schreiben), shorten Block 3 to 10 minutes and Block 4 to 15 minutes. Never shorten production.

**Type T**: Review 20 · New words 25 (or "error words" 15 when the plan says Review only / Error words) · Recital of palaces A–D 10 · Grammar (weakest point) 20 · Break 10 · Production 75 (the Schreiben task, then the Vortrag, then the Diskussion, as listed) · Correction & Aussprache 25.

**Type M**: Palace recital 10 · Schreiben 75 (strict, no notes) · Break 10 · Sprechen prep 15 + Vortrag with questions and Diskussion with the voice AI (MASTER §15 prompts 2 and 3) · Self-scoring 30 with the point table in MASTER §2, then AI grading of the Schreiben (prompt 1). Day 53 also adds Lesen 65 + Hören 40 at the start (see "Lesen and Hören" below). Do not open the mock paper until the block starts.

**Type L**: Review 20 · exactly the Produce column · Error-log review 20 · Shadowing 10. Stop there.

## Step 3 — Block 1: what is due

- **Words:** list the batch IDs learned on days N−1, N−3, N−7, N−14 and N−30 (read them from the plan's "Words" column). Add one line: "If you use Anki, do Anki's due cards instead; this list is for the paper box."
- **Palaces:** list the loci learned on days N−1, N−3 and N−7, plus every completed palace once a week. A palace is complete on the day the plan says "walk Palace X".
- **Day 1 only:** nothing is due yet. Block 1 is: (a) write your own seven Palace A loci into the table copied from MASTER §5, (b) set up Anki or a five-compartment paper box, (c) make sure `error_log.md` exists.

## Step 4 — Block 2: the word batch

- Copy the batch section from WORTSCHATZ **row for row, unchanged**, with one mechanical edit to the Grammar column: a lone hyphen `-` (plural same as singular) becomes `Pl. wie Sg.`, and an en dash `–` (no plural) becomes `kein Pl.`. Change nothing else.
- After the table, print: "Rows copied: X of Y" (Y = rows in the source section). They must match.
- Say how to learn this batch:
  - **Active** (English → German with article and plural, or verb with its case or preposition): B1-Check A and B, W01–W12, W30, W31.
  - **Recognition** (German → English), plus active for the 5 words the candidate will actually use: W13–W29.
  - **Optional**: W32–W35. Use at most one or two in any text.
- B1-Check days: the instruction is "tick what you already use correctly with article and plural; learn only the misses".
- If a word in the batch has a picture hook in the WORTSCHATZ "Picture hooks" table, copy that hook under the table. Do not invent etymologies.
- The 5 sentence prompts: "Write one sentence each with the 5 words you found hardest, then say each aloud." The candidate chooses the words; do not write the sentences.

## Step 5 — Block 3: frames and palace

- Copy the palace row(s) for today's locus from MASTER §5 verbatim (suggested locus, module, the words the image holds, image).
- Copy today's frame modules verbatim from MASTER §6, §8, §10 or §11. Keep the "Grammar to watch" column.
- The routine, from MASTER §3: read aloud 3 times → build the image at the locus → write from memory → correct → write again.
- **Cloze:** the same frames with 1–3 key words per sentence replaced by `____`. The answer key is the copied frame itself, inside `<details><summary>Answers</summary> … </details>`.
- Type T: replace all of this with "Recite Palaces A–D aloud in 10 minutes; mark any locus you stalled on."

## Step 6 — Block 4: grammar

- Copy the G-section named in the plan from MASTER §13 verbatim (table, bullets, error line).
- "Weakest point" (type T): read ERROR LOG, count the rows per Type, choose the G-point that matches the most frequent Type, and write one line saying which Type, how many rows, and which G-point you chose.
- **10 transformations, labelled `[generated]`.** Rules:
  - every sentence is short, B2-level, on an exam topic, and tests only the rule in the copied section;
  - the answer key is inside `<details>`, and **every answer cites the exact line of §13 it follows**;
  - if you are not certain an answer is correct, drop that item. Eight correct items beat ten with one wrong.

## Step 7 — Block 5: production

- Copy the task verbatim (F-task points from §7, N-task from §9, Vortrag topic row from the §10 topic bank, D-question row from §11). Number the Leitpunkte 1–4.
- **Copy-by-hand tasks** (Musterbeitrag / Musternachricht): copy the model text verbatim with its bold frame. Instruction: copy it by hand, then colour the frame in one colour and your content in another. No timer and no word count.
- **Timed Schreiben Teil 1:** 50 minutes, using the 50-minute routine in §6. Target 170–190 words. Last 10 minutes: the 8-point "final check" from §6, copied verbatim as checkboxes.
- **Timed Schreiben Teil 2:** 25 minutes, using the routine in §8. Target 110–130 words. Checks: §8 "Register traps", copied verbatim as checkboxes.
- **Vortrag:** copy the §10 script table and the six-line notes layout. Record yourself. Questions come from the voice AI (prompt 2).
- **Diskussion:** copy the R-A-F turn and the D-row. Use the Argument-Uhr hours (§11). Partner: voice AI (prompt 3).

## Step 8 — Block 6: correction and Aussprache

- Copy the matching AI prompt from MASTER §15 verbatim, with the task text already filled in. Leave `[paste]` only where the candidate's own text goes.
- **Day 1 only:** grade the Day 0 baseline F7 here with prompt 1. If it was never written, write it outside today's three hours, 50 minutes, without help.
- **Error log:** "Copy your 3 worst corrected errors into `study_materials/b2_sprint/error_log.md` (Date | Wrong | Right | Rule | Type)." Do not put an error table inside the day file.
- **Sundays:** add "Rewrite your 5 most frequent error types as correct sentences" (MASTER §15).
- **Shadowing, 5 minutes:** copy about 100 words from a model text in MASTER (F1–F6, N1–N6, V1–V3, D-M1, D-M2). Use one that links to today's material, or rotate through them. **Never generate a shadowing text.** The method, from §3: play one sentence with a voice app, pause, repeat it with the same melody.

## Lesen and Hören (outside the three hours)

The plan leaves them out, so measure them early:

- **Before day 7:** do Lesen (65 min) and Hören (40 min) from the Goethe online practice set, [bfu.goethe.de/b2_mod_2MX6/lesen.php](https://bfu.goethe.de/b2_mod_2MX6/lesen.php) and `hoeren.php`. It has the same content as the Modellsatz Erwachsene, but Mock 1 only uses that set's Schreiben and Sprechen, so this costs nothing. Note both scores in `error_log.md`.
- **Day 53 (Mock 5):** use the Lesen and Hören of the Modellsatz Jugendliche. Mock 2 only uses its Schreiben and Sprechen.

Put this reminder in the header of each day file until both scores are logged.

## Hard rules

1. Every block heading carries its source: `[§6 E-A–E-D]`, `[W01]`, `[§13 G1]`, or `[generated]`.
2. Never alter copied German. If you think the source contains an error, copy it unchanged and list it at the end under "Suspected source errors" with your reason.
3. No placeholders except the candidate's own content: never write "see section X". Copy it.
4. Checkboxes (`- [ ]`) on every action, so the candidate ticks through the day.
5. **Slip rule**, printed in every header: *Missed a day? Do not double up. Skip that day's production task, keep the review, and carry on with the next day.*
6. Use no other sources. If a step cannot be filled from MASTER or WORTSCHATZ, stop and say what is missing instead of inventing it.

## Report back after writing the file

- Day type, and the plan row used
- Rows copied: X of Y
- The list of every `[generated]` item
- Anything you could not fill, and any suspected source errors
