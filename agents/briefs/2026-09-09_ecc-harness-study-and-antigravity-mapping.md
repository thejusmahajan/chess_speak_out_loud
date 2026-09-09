```
Brief-ID:      2026-09-09_ecc-harness-study-and-antigravity-mapping
Written:       2026-09-09
Target repo:   chess_speak_out_loud (report only). The study material is downloaded OUTSIDE both repos.
Route:         Antigravity (full workspace) + network access for the clone
Type:          research -- study and mapping, NO implementation
Blast-radius:  private -- a report the leader reads. Nothing ships from this brief.
Reversibility: trivial
Failure-mode:  SILENT -- a confident, plausible description of a mechanism that does not exist is
               indistinguishable from a correct one, and this task is almost entirely mechanism
               descriptions
Depends on:    none
Status:        ACTIVE
```

**Environment:** git, network, any Python. No GPU, no engine. **Time-box: 90 minutes.**

---

## 1. INTENT

*(Intent outranks instructions. If any instruction conflicts with this paragraph, the intent wins
— stop and report. Doing so is a success, never a boundary violation.)*

Thejus runs an agent workflow by hand: a leader writes pinned briefs, a worker executes them, and
the leader audits the diff. It works, and it has failed twice in the past week in the same way —
**a brief declared which files may be touched, and files outside that list were written anyway.**

**Everything Claude Code** (Affaan Mustafa) is a widely-adopted harness for Claude Code with an
orchestrator/specialist agent split, on-demand skills, hooks and scoped tool permissions. **The
question this brief exists to answer is narrow:**

> **What, if anything, in that harness would measurably improve THIS repository's agent workflow —
> and does any of it mechanically enforce scope limits that are currently only prose?**

You are not producing an inventory of ECC. You are producing a **filtered, sourced judgement** about
what transfers. A short answer with five well-sourced rows is worth far more than a long one.

**A finding of "very little here applies, and here is why" is a complete and welcome result.**

---

## 2. ⚑ The two ways this task goes wrong

**(a) You will be describing a system you are not.** ECC is built for Claude Code. You run in
Antigravity. It will be easy to describe a Claude Code mechanism accurately and then assert an
Antigravity equivalent that does not exist. **Every mechanism claim needs a source. Every
Antigravity claim needs a documentation citation, not your recollection.**

**(b) You will want to recommend too much.** ECC targets general software teams — code review,
refactoring, test generation. This repository is interpretability research plus a job search. Most
of ECC will not apply. **Your NOT-APPLICABLE list must be non-empty** (see Acceptance).

---

## 3. WHAT YOU MAY TOUCH

```
<a working directory OUTSIDE both repos>     -- the clone, freely
agents/reports/2026-09-09_ecc-harness-study-and-antigravity-mapping_REPORT.md   (new -- deliverable)
```

**That is the complete list. Implement nothing.**

- **Do not create `AGENTS.md`, `SKILL.md`, `agent.md`, rules files, workflows or MCP config.** Not
  in this repo, not anywhere. This brief is study and mapping only; the leader decides what is built.
- **Do not modify `~/.gemini/`, `~/.claude/`, or any settings file.**
- **Do not touch `trainer/content/ladders/*.json`** — every `.json` under it is off limits, no cards,
  no edits, no rewording. This rule was broken on 2026-09-03.
- **Do not touch `job_search/` or the website repo.**
- **Do not commit anything, in any repository.**

---

## 4. STEPS

### Step 1 — download it first, and measure it before reading it

**Clone the canonical repository**, into a working directory **outside both repos**:

```
git clone https://github.com/affaan-m/everything-claude-code.git ecc
cd ecc
git remote -v
git log -1 --format="%H %ad %s"
```

**⚠ There are many forks** — `chchwa/affaan-m-everything-claude-code`, `giovanisp/…`,
`ysyecust/…`, `WorldFlowAI/…` and others, several of them modified for particular stacks (one is
retargeted at C++20 HPC). **You want `affaan-m`.** The repository appears to have been renamed to
`affaan-m/ECC`, so the URL above may redirect — that is expected. **Paste the `git remote -v`
output and confirm the owner is `affaan-m`.** If it is not, stop: you have a fork, and its
contents are somebody else's edits.

**Record the HEAD commit hash and date** and put them at the top of the report. This repository is
actively developed; a finding is only meaningful against a stated version.

Then, **before** reading deeply, report its shape: directory tree to two levels, file count, total
size, and the number of agents, skills, rules, hooks and workflows it defines.

**⚠ Token discipline: do not paste file contents into the report.** Cite `path:line`. A report that
quotes the repo at length is a failed report — it costs a fortune and tells the leader nothing he
could not read himself.

**CHECKPOINT 1.** The shape, in under 20 lines.

---

### Step 2 — the mechanisms, with sources

For each **mechanism** ECC uses — not each agent, the *mechanisms* — record:

| mechanism | what it does | where it is implemented | source |
|---|---|---|---|

Expect roughly: orchestrator/specialist agent split, per-agent tool scoping, on-demand skills,
always-resident rules, hooks, MCP enablement/disablement, and whatever else you find.

**Every row needs a `path:line` in the cloned repo.** A row you cannot source does not go in the
table; it goes in "what I could not check".

**CHECKPOINT 2.** The mechanism table.

---

### Step 3 — map to Antigravity, with citations

For each mechanism, state the Antigravity equivalent **and cite the documentation that says so**.

Known starting points, all of which you must verify rather than trust:
`AGENTS.md` at project root; Rules; custom agents (`agent.md`, tools and skills in YAML
frontmatter); `SKILL.md`; Workflows; `~/.gemini/config/mcp_config.json`.

Record for each: **EXISTS / PARTIAL / NO EQUIVALENT**, with the citation. Note any hard limits you
find — for example the rules-file character cap — because they change what is portable.

**If Antigravity has no equivalent, say so.** That is a finding, not a gap in your work.

**CHECKPOINT 3.** The mapping table with citations.

---

### Step 4 — the relevance filter

Now judge each mechanism **against this repository specifically**. Read `CLAUDE.md`,
`agents/README.md`, `agents/AGENT_ONBOARDING.md` and `state/MAP.md` first so you know what already
exists — much of ECC's value may already be present here in a different form, and saying so is a
finding.

Label every row **ADOPT** / **ADAPT** / **NOT APPLICABLE**, each with a one-line reason.

**CHECKPOINT 4.** The labelled table, and the counts per label.

---

### Step 5 — the question that prompted this brief

Answer directly, with sources:

> **Does Antigravity support declaring, per agent, the exact set of files or tools that agent may
> touch — such that a scope limit is enforced by the runtime rather than requested in prose?**

If yes: what is the exact syntax, where does the file live, and what happens when the agent attempts
something outside the declared set? If no, or only partially: say precisely how far it goes.

This matters because two deliveries this week wrote files that the governing brief had explicitly
placed off limits. Prose scope is a request; the leader wants to know whether it can become a rule.

**CHECKPOINT 5.** The answer, sourced.

---

### Step 6 — the shortlist

At most **five** recommendations, ranked by value to this repository divided by effort. For each:
what it is, why it helps *here*, what it would cost to set up, and the risk if it is wrong.

**Fewer than five is fine. Zero is fine if that is what the evidence supports.**

---

## 5. REPORT

`agents/reports/2026-09-09_ecc-harness-study-and-antigravity-mapping_REPORT.md`, with every
checkpoint, and:

- **"What I could not check"** — mandatory, non-empty. Anything you asserted from memory rather than
  from a source belongs here.
- The standing question, answered:

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check
> that?**

---

## 6. ACCEPTANCE

1. **Nothing implemented.** No config file created anywhere, no settings modified, nothing committed.
2. **Every mechanism claim carries a `path:line`; every Antigravity claim carries a doc citation.**
   Unsourced claims live in "what I could not check", not in the tables.
3. **The NOT APPLICABLE list is non-empty.** ECC is a general software-development harness and this
   is a research and job-search repository; a mapping in which everything applies has not been
   filtered.
4. The report is under ~400 lines and quotes no file at length.
5. Step 5 is answered directly, yes or no, with a source.

---

## 7. STOP AND ASK

Not covered: implementing anything; editing settings; touching flashcards, `job_search/` or the
website; committing; spending beyond the 90-minute box.

**A stop with a clear question is a successful delivery.**
**And "most of this does not apply, here is the little that does" is the most likely correct answer.
Do not pad it into something bigger.**
