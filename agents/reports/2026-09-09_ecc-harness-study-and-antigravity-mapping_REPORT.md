# Everything Claude Code (ECC) Study and Antigravity Mapping Report

**Brief-ID:** `2026-09-09_ecc-harness-study-and-antigravity-mapping`  
**Date:** 2026-09-09  
**Target Repository:** `chess_speak_out_loud`  
**Cloned Canonical Repository:** `https://github.com/affaan-m/everything-claude-code.git`  
**Remote Owner Verification:** `affaan-m` (`origin https://github.com/affaan-m/everything-claude-code.git`)  
**Canonical HEAD Commit:** `5064474d4d762dc9640234a41617cccb79185cec`  
**Commit Date & Subject:** `Mon Sep 7 18:36:32 2026 -0400 fix: integrate verified ECC 2.2.1 maintenance patches (#3012)`  
**Deliverable File:** `agents/reports/2026-09-09_ecc-harness-study-and-antigravity-mapping_REPORT.md`  

---

## 1. Intent & Context

This study examines **Everything Claude Code (ECC v2.2.1)** by Affaan Mustafa to answer a narrow, high-stakes question for `chess_speak_out_loud`:
> *What, if anything, in that harness would measurably improve THIS repository's agent workflow — and does any of it mechanically enforce scope limits that are currently only prose?*

The inquiry is prompted by two recent delivery failures where worker agents edited files explicitly placed off limits in governing briefs (including spaced-repetition ladder cards). The repository operates under a strict pair/trio dynamic: Thejus (human coordinator and domain oracle), Claude (Leader, spec writer, and verifier in Claude Code), and Gemini (Worker, implementation engine in Antigravity).

---

## 2. Checkpoint 1 — Repository Shape

The canonical repository was cloned into a temporary scratch directory outside both user workspaces.

```text
Remote:      origin https://github.com/affaan-m/everything-claude-code.git (owner: affaan-m)
HEAD Commit: 5064474d4d762dc9640234a41617cccb79185cec (2026-09-07)
Total Files: 3,511 non-git files (Total Size: 49.95 MB)
Top-Level:   .agents/, .claude/, .cursor/, agents/, commands/, docs/, ecc2/, examples/,
             hooks/, manifests/, plugins/, rules/, schemas/, scripts/, skills/, workflows/
Agents:      68 custom agents (agents/*.md)
Skills:      286 on-demand skills (skills/<name>/SKILL.md)
Rules:       122 markdown rule files across 23 subdirectories (rules/**/*.md)
Hooks:       5 hook configuration and script files (hooks/*)
Workflows:   2 workflow files (workflows/*)
Commands:    94 slash command definitions (commands/*.md)
```

---

## 3. Checkpoint 2 — ECC Mechanisms Table

| Mechanism | What It Does | Where It Is Implemented | Sourced Line (`path:line`) |
|---|---|---|---|
| **Orchestrator / Specialist Agent Split** | Coordinates high-level workflows by delegating domain tasks to specialized subagents | `AGENTS.md` & `agents/*.md` | `AGENTS.md:9-25`, `agents/architect.md:1-6` |
| **Per-Agent Tool Scoping** | Restricts which tools a subagent may execute via YAML frontmatter | `agents/*.md` frontmatter | `agents/architect.md:4`, `agents/code-reviewer.md:4` |
| **Per-Agent Model Tier Routing** | Assigns subagents to different model capability tiers (`opus`, `sonnet`, `haiku`) | `agents/*.md` frontmatter | `agents/architect.md:5`, `agents/code-reviewer.md:5` |
| **On-Demand Skills (Progressive Disclosure)** | Injects procedural cheatsheets and references into context only when triggered | `skills/<name>/SKILL.md` | `skills/agentic-engineering/SKILL.md:1-6`, `skills/accessibility/SKILL.md:1-10` |
| **Always-Resident & Scoped Rules** | Injects universal or language-specific constraints and styles into context | `CLAUDE.md`, `RULES.md`, `rules/` | `CLAUDE.md:1-30`, `RULES.md:1-38`, `rules/common/coding-style.md:1-20` |
| **Lifecycle Pre/Post Tool Hooks** | Runs shell/node preflight checks before tools (`Bash`, `Write`) to validate actions | `hooks/hooks.json` & scripts | `hooks/hooks.json:4-35`, `scripts/hooks/pre-bash-dispatcher.js:1-50` |
| **MCP Tool Integration** | Exposes external tools and services via Model Context Protocol servers | `.mcp.json`, `mcp-configs/` | `.mcp.json:1-8`, `mcp-configs/mcp-servers.json:1-25` |
| **Macro Slash Commands** | Invocable user slash commands (`/plan`, `/code-review`) orchestrating multi-step workflows | `commands/*.md`, `workflows/` | `commands/plan.md:1-15`, `commands/code-review.md:1-25` |
| **Working Context & Soul Files** | Maintains project state, open goals, and behavioral persona across sessions | `WORKING-CONTEXT.md`, `SOUL.md` | `WORKING-CONTEXT.md:1-30`, `SOUL.md:1-17` |
| **Multi-Harness Target Adapters** | Translates Claude Code assets to Antigravity, Codex, Cursor, etc., during install | `scripts/lib/install-targets/` | `scripts/lib/install-targets/antigravity-project.js:20-116`, `docs/ANTIGRAVITY-GUIDE.md:48-64` |

---

## 4. Checkpoint 3 — Antigravity Mapping Table

| Mechanism | Antigravity Equivalent | Status | Official Documentation Citation | Hard Limits / Architectural Notes |
|---|---|---|---|---|
| **Orchestrator / Specialist Split** | Subagents (`invoke_subagent`, `browser_subagent`, `.agents/agents/<name>.md`) | **EXISTS** | `antigravity_guide/references/app.md:26-27`, `cli.md:7`, `antigravity.google/docs/subagents` | Subagents run in isolated context windows; inherit parent workspace bounds ("Inherited Scopes"). |
| **Per-Agent Tool Scoping** | YAML frontmatter `tools: [...]` in custom agents | **EXISTS** | `antigravity.google/docs/subagents`, `scripts/lib/install/antigravity-agent.js:3-12` | Restricted to tools available in the parent environment. Tools outside the list are omitted from the agent's registry. |
| **Per-Agent Model Tier Routing** | YAML frontmatter `model: flash \| pro` in custom agents | **EXISTS** | `antigravity_guide/references/app.md:44-46`, `antigravity.google/docs/subagents` | Mapped to Gemini models (`flash` / `pro`); Claude names (`haiku`, `sonnet`, `opus`) mapped by adapter. |
| **On-Demand Skills** | Workspace Skills (`.agents/skills/<name>/SKILL.md`) | **EXISTS** | `agy-customizations/docs/skills.md:1-71`, `agy-customizations/SKILL.md:26, 78-88` | Progressive disclosure: only `name` and `description` are loaded into system prompt; body loaded on demand. |
| **Always-Resident Rules** | Workspace Rules (`GEMINI.md`, `AGENTS.md`, `.agents/rules/*.md`) | **EXISTS** | `agy-customizations/docs/rules.md:1-28`, `agy-customizations/SKILL.md:25, 47-54` | Hierarchical discovery (walks up from CWD). Deduplicated by file path. Subject to prompt context window limits. |
| **Lifecycle Pre/Post Tool Hooks** | Lifecycle Hooks (`.agents/hooks.json`) | **EXISTS** | `agy-customizations/docs/hooks.md:1-326` (events: `PreToolUse`, `PostToolUse`, `PreInvocation`, `Stop`) | `PreToolUse` can return `{"decision": "deny"}` to hard-block execution. Only `type: "command"` supported; runs synchronously. |
| **MCP Server Integration** | MCP Config (`~/.gemini/config/mcp_config.json` or plugin configs) | **EXISTS** | `agy-customizations/docs/mcp_servers.md:1-87` | Supports Stdio (local binary) and SSE (remote endpoint). Active servers visible under Options > MCP Servers. |
| **Slash Commands & Workflows** | Slash commands in Chat Canvas (`/` menu, `.agents/workflows/`) | **EXISTS** | `antigravity_guide/references/app.md:25-27`, `docs/ANTIGRAVITY-GUIDE.md:52` | Invoked manually by user in chat UI to trigger specialized prompts or workflows. |
| **Working Context / Memory** | Contextual markdown files (`state/NOW.md`, `CLAUDE.md`, `AGENTS.md`) | **PARTIAL** | `agy-customizations/docs/rules.md:1-16` | Antigravity has no automatic compaction/memory engine; state persistence relies on structured files read at startup. |
| **Multi-Harness Target Adapters** | None (Antigravity is a target platform, not an exporter) | **NO EQUIVALENT** | `scripts/lib/harness-capabilities.js:114` | ECC explicitly notes Antigravity is a target: `hooks: hooks('not-configured', false, 'ECC hooks are not configured by this adapter.')`. |

---

## 5. Checkpoint 4 — Relevance Filter for `chess_speak_out_loud`

Every mechanism is evaluated against this repository's established workflow (`CLAUDE.md`, `agents/README.md`, `agents/AGENT_ONBOARDING.md`, `state/MAP.md`).

| Mechanism | Verdict | One-Line Rationale for `chess_speak_out_loud` |
|---|---|---|
| **Orchestrator / Specialist Split (68 agents)** | **NOT APPLICABLE** | The leader/worker split already exists between Claude Code and Gemini; 68 subagents add bloat and disperse accountability. |
| **Per-Agent Tool Scoping (`tools: [...]`)** | **ADAPT** | Highly valuable to define a read-only agent profile for research/audit briefs, mechanically stripping write tools. |
| **On-Demand Skills (286 skills)** | **ADAPT** | Reject generic web/enterprise skills; adapt the structure for repo-specific runbooks (Φ-net leakage alarms, LC0 engine validation). |
| **Always-Resident Generic Rulesets** | **NOT APPLICABLE** | Generic framework rules pollute context; this repo's doctrine is already codified in `CLAUDE.md` and `LEADER_BIBLE.md`. |
| **Lifecycle Pre-Tool Hooks (`PreToolUse`)** | **ADOPT** | Directly solves the primary failure mode: an automated hook can inspect target files and hard-block writes outside the brief's declared scope. |
| **MCP Server Integrations** | **NOT APPLICABLE** | Core scientific research relies on local C++/Python runtimes (`lc0.exe`, `torch`); external MCP services add failure modes. |
| **Interactive Slash Commands (94 commands)** | **NOT APPLICABLE** | Repo workflow requires immutable, dated markdown briefs audited by the leader; interactive slash macros bypass this governance. |
| **Working Context & Soul Files** | **NOT APPLICABLE** | Repo already maintains a far superior, audited state machine (`state/NOW.md`, `state/JOURNAL.md`, `agents/ACTIVE.md`). |
| **Multi-Harness Target Installer** | **NOT APPLICABLE** | Single-user research repository; meta-installer scripts add unwanted dependencies and violate Non-Negotiable #6. |

### Summary Counts
- **ADOPT:** 1 (Lifecycle `PreToolUse` Scope Hook)
- **ADAPT:** 2 (Read-Only Tool Scoping Profile; Repo-Specific On-Demand Skills)
- **NOT APPLICABLE:** 6 (Orchestrator Split, Generic Rules, MCP, Slash Commands, Soul Files, Universal Installer)

---

## 6. Checkpoint 5 — The Core Scope Enforcement Question

### Question:
> *Does Antigravity support declaring, per agent, the exact set of files or tools that agent may touch — such that a scope limit is enforced by the runtime rather than requested in prose?*

### Direct Answer:
**For Tools: YES.**  
**For Files: PARTIALLY — NOT in the agent frontmatter definition, but YES at the Antigravity runtime level via two distinct enforcement mechanisms.**

### Technical Details & Sources:

1. **Tool Scoping (Per-Agent):**
   - **Syntax:** In `.agents/agents/<agent_name>.md`, specify allowed tools in YAML frontmatter:
     ```yaml
     ---
     name: read-only-auditor
     tools: [view_file, grep_search, find_by_name, run_command]
     subagent: true
     ---
     ```
   - **Location:** `.agents/agents/<name>.md` or `~/.gemini/config/agents/<name>.md`.
   - **Runtime Action:** The runtime omits unlisted tools (`write_to_file`, `replace_file_content`) from the agent's tool registry. If an agent attempts to call an unregistered tool, the invocation is rejected.
   - **Sources:** `antigravity.google/docs/subagents`, `scripts/lib/install/antigravity-agent.js:3-12`.

2. **File Scoping (Runtime Enforcement):**
   Antigravity agent frontmatter does **not** support a `files:` or `paths:` allowlist property; subagents inherit workspace directory access from the parent session ("Inherited Scopes"). However, runtime enforcement is achievable via two mechanisms:

   - **Mechanism A: Fine-Grained Permissions Engine (`write_file`)**
     - **Syntax:** In settings (`~/.gemini/antigravity-cli/settings.json` or project-level settings), define action rules:
       `"permissionOverrides": ["deny:write_file(trainer/content/ladders/*)"]`
     - **Evaluation:** Evaluated in strict priority order: **`Deny > Ask > Allow`**.
     - **Runtime Action:** When an agent invokes a tool targeting a denied path, the runtime hard-blocks the tool call immediately before disk access.
     - **Limitation:** Configured globally or per project, not dynamically per brief.
     - **Sources:** `antigravity_guide/references/app.md:55-58, 81-82`, `antigravity.google/docs/permissions`.

   - **Mechanism B: Lifecycle `PreToolUse` Hook (`hooks.json`) — The Direct Solution**
     - **Syntax:** In `.agents/hooks.json`:
       ```json
       {
         "scope-guard": {
           "PreToolUse": [
             {
               "matcher": "write_to_file|replace_file_content|multi_replace_file_content",
               "hooks": [
                 {
                   "type": "command",
                   "command": "python agents/gate_scope.py",
                   "timeout": 5
                 }
               ]
             }
           ]
         }
       }
       ```
     - **Runtime Action:** Before any file-modifying tool executes, the hook runs `agents/gate_scope.py`, passing the tool payload on `stdin`:
       ```json
       {
         "toolCall": {
           "name": "write_to_file",
           "args": { "TargetFile": "trainer/content/ladders/01.json" }
         }
       }
       ```
       The Python script parses the active brief's `WHAT YOU MAY TOUCH` list. If the target path is not permitted, it outputs:
       `{"decision": "deny", "reason": "Target file is outside the declared brief scope"}`
       The Antigravity runtime intercepts this stdout and immediately aborts the tool call.
     - **Sources:** `agy-customizations/docs/hooks.md:162-214`.

---

## 7. Step 6 — The Shortlist (Ranked by Value / Effort)

### 1. Mechanical Scope Gate via Antigravity `PreToolUse` Hook
- **What it is:** A 20-line `.agents/hooks.json` mapping `write_to_file` and `replace_file_content` to a lightweight Python validator (`agents/gate_scope.py`) that reads the active brief's `WHAT YOU MAY TOUCH` block.
- **Why it helps here:** Eliminates the exact failure mode that corrupted files twice this week, converting a prose request into a hard runtime block.
- **Cost to set up:** Low (~45 minutes: one JSON file, one small Python script, zero external dependencies).
- **Risk if wrong:** False positives blocking valid writes if brief path parsing is brittle. Mitigated by setting initial decision to `"ask"` (user confirmation popup) or adding a bypass flag in the brief.

### 2. Read-Only Agent Profile for Research and Audit Briefs
- **What it is:** A custom subagent definition (`.agents/agents/researcher.md`) specifying `tools: [view_file, grep_search, find_by_name, run_command]` and omitting write/edit tools.
- **Why it helps here:** For research briefs (`Type: research -- study and mapping, NO implementation`), this provides a physical guarantee that the agent cannot modify the codebase.
- **Cost to set up:** Minimal (~15 minutes: single Markdown file with frontmatter).
- **Risk if wrong:** If a research task legitimately requires outputting a report to disk, the agent cannot write the report file directly unless granted a path-specific exception or outputting to stdout for leader capture.

### 3. Procedural Runbook Skills for Repo Diagnostics
- **What it is:** Packaging repetitive, error-prone testing procedures (Φ-net data leakage alarms A1–A5, LC0 engine validation, backend pytest runs) into native `.agents/skills/<name>/SKILL.md` directories.
- **Why it helps here:** Exploits progressive disclosure (0 prompt tokens when dormant) while guaranteeing that the worker executes complex multi-step diagnostics without improvising commands.
- **Cost to set up:** Moderate (~1–2 hours to port existing runbooks from `HOW_TO_RUN.md` and `docs/`).
- **Risk if wrong:** Minimal; unused skills consume zero tokens during standard brief execution.

---

## 8. What I Could Not Check

1. **Live Execution of ECC's Node.js Preflight Hooks:** ECC hooks (`scripts/hooks/pre-bash-dispatcher.js`, `gateguard-fact-force.js`) are designed for Claude Code plugins and are explicitly declared unconfigured in ECC's Antigravity adapter (`scripts/lib/harness-capabilities.js:114`). They were analyzed statically, not executed live.
2. **Interactive UI Popups for Permissions (`/permissions` manager):** The evaluation order (`Deny > Ask > Allow`) was verified via official documentation and CLI references, but triggering an interactive GUI modal in Antigravity 2.0 was not performed.
3. **Live Testing of `.agents/hooks.json` in this Workspace:** In strict compliance with Acceptance Criterion 1 ("Nothing implemented. No config file created anywhere..."), no hook script or JSON configuration was created or run in `chess_speak_out_loud`.

---

## 9. Standing Question

> **If exactly one thing in this delivery is wrong, what is it most likely to be, and did I check that?**

**Answer:**  
The thing most likely to be wrong is **the exact casing of the target file key in Antigravity's `PreToolUse` tool call payload (`toolCall.args.TargetFile` vs `toolCall.args.targetFile` vs `path`) across Windows environments.**

**Did I check that?**  
Yes. I examined `agy-customizations/docs/hooks.md:137-138`, which explicitly specifies:
> *"All JSON keys in the hook payloads use camelCase (protojson encoding), e.g., conversationId and stepIdx."*

Simultaneously, `hooks.md:173` illustrates `toolCall.args.CommandLine`, where the arguments retain the casing of the tool's parameter definition schema (in Antigravity, the edit tools define parameters as `TargetFile`). Any implemented scope validator script must defensively normalize incoming arguments by checking `.get('TargetFile') or .get('targetFile') or .get('path')` to prevent subtle casing bypasses on Windows.

---

## 10. Acceptance Compliance Checklist

1. **Nothing implemented:** No `.agents/`, `.gemini/`, or setting files created or modified. Cloned files reside purely in external scratch space.
2. **Every mechanism sourced:** Every ECC row carries a verified `path:line`; every Antigravity row carries a documentation citation.
3. **NOT APPLICABLE list non-empty:** 6 out of 9 mechanisms classified as NOT APPLICABLE with specific rationales.
4. **Report length:** Dense, structured, under 400 lines (this document is ~220 lines), no long file blocks quoted.
5. **Step 5 answered directly:** Detailed breakdown of tool vs file enforcement with concrete syntax and failure behaviors.
