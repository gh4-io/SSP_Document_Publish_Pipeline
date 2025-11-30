Here is the **SSP Pipeline - Claude Code Operating Procedures** in a Canvas-ready Markdown format.

This artifact is designed to be pinned or saved as a primary reference for your workflow.

***

# SSP Pipeline – Claude Code Operating Procedures

**Purpose**: To ensure zero context loss between sessions and enforce strict governance over the SSP Pipeline using Claude Code CLI.

---

## 🏗️ 1. Boot Up (Start of Day)
*Execute this immediately upon starting a new `claude` CLI session.*

### 🛠️ Mode: `Normal` (Default)
Do not use `/plan` yet. We need immediate tool execution, not reasoning.

### 📜 The Ingest Prompt
**Copy and paste this block:**

```text
Act as the SSP Pipeline Architect.

1. INGEST GOVERNANCE (Mandatory):
   - Read: PRP/SSP_PRP_CORE.md
   - Read: SSP_Document_Publish_Pipeline_CORE.md

2. INGEST CONTINUITY (Previous Session Context):
   - Read: SSP_PROJECT_STATUS.md
   - Context: Treat this file as the "Session Handoff"—it records exactly where the previous session ended.

3. PERFORM REALITY CHECK (MCP Audit):
   - Use Serena MCP (or `tree`/`ls -R`) to scan `scripts/ssp_pipeline/`.
   - Compare the *physical* codebase against the *historical* status in `SSP_PROJECT_STATUS.md`.

4. REPORT:
   - If Synced: "SSP Pipeline Ready. Continuity Restored. Active Task: <Insert Task>"
   - If Drifted: "⚠️ Drift Detected: Codebase state does not match Project Status file."
```

### ✅ Verification
*   Wait for the agent to run `read_file` and `ls`.
*   Ensure the response confirms: **"SSP Pipeline Ready"**.

---

## ⚡ 2. Work Execution (The "Modes")
*Choose the right mode based on the task type to optimize tokens.*

### 🟢 Option A: Implementation (Standard)
**Use for:** Writing code, fixing bugs, or following a known plan.
*   **Mode:** `Normal`
*   **Prompt:**
    > "Proceed with **Edit Mode**. Implement the `Active Task` from the status file. Start with `[filename]`. Ensure strict type hinting and docstrings."

### 🔵 Option B: Architecture (Complex)
**Use for:** Designing new modules, refactoring, or when you don't know the answer yet.
*   **Mode:** `/plan` (Type `/plan` in CLI)
*   **Prompt:**
    > "Enter **Plan Mode**. Review the requirements for [Phase X]. Propose a detailed step-by-step implementation strategy. Do not write code yet."

### 🛡️ The "Accept" Gate (Crucial)
*   **NEVER** hold down `Enter` through edits.
*   **ALWAYS** check the `diff`:
    1.  Did it delete valid TODOs?
    2.  Did it remove the License/Docstring header?
    3.  Is it hallucinating imports?
*   **Rejecting:** Type *"Fix imports first"* or *"Don't delete that TODO"* to force a retry.

---

## 💾 3. Close Out (End of Session)
*Execute this **before** closing the terminal window. This is the only way to save "memory".*

### 🛠️ Mode: `Normal` (Default)

### 📜 The Session Flush Prompt
**Copy and paste this block:**

```text
Act as the SSP Project Manager.

**GOAL**: Perform a "Session Flush". Synchronize the volatile session context into persistent documentation.

**INSTRUCTIONS**:

1. **ROADMAP REALITY CHECK**:
   - Compare `scripts/` vs `SSP_PROJECT_STATUS.md`.
   - **REWRITE** the Roadmap Phase if we deviated (don't just check boxes).
   - If architecture changed, update the plan to match reality.

2. **UPDATE FOCUS**:
   - Set **Active Tasks** to the exact state where we stopped.
   - Set **Next Up** to the immediate next step for tomorrow.

3. **UPDATE DECISION LOG**:
   - Log architectural changes: `* **YYYY-MM-DD:** [Topic] Changed from X to Y.`

4. **CHANGELOG**:
   - Verify `CHANGELOG.md` covers today's work. Draft entry if missing.

**EXECUTE**: Present updated file contents for approval.
```

### ✅ Verification
1.  **Review Diff:** Ensure `SSP_PROJECT_STATUS.md` accurately reflects your progress.
2.  **Approve:** Press `Enter` to write the files.
3.  **Exit:** safely close the terminal.

---

## 🧰 Command Cheat Sheet

| Intent | Command |
| :--- | :--- |
| **Start Logic Mode** | `/plan` |
| **Reset Context** | `/clear` (Use with caution; requires re-running Boot Prompt) |
| **Force Shell Cmd** | `!ls -R` (Runs command immediately) |
| **Run Tests** | `uv run pytest` |
| **Lint Check** | `uv run ruff check .` |
| **Formatting** | `uv run ruff format .` |


## Phase Sample

```markdown
Here is the complete compound prompt. It instructs Claude to first backfill the missing milestone documentation for Phase 4, and then proceed immediately to executing Phase 5 with the same rigorous standard.

  We have code for **Phase 4 (Utilities)** complete, but we need to generate its milestone documentation before moving on. Please execute the following multi-step plan in order.

  ### STEP 1: Phase 4 Milestone Documentation (Retroactive)
  1. **Analyze Phase 4 Code:** Review the existing utility scripts to understand how to verify they are working.
  2. **Create Documentation:** Generate the file `documentation/milestones/P04_Utilities_Core.md`.
  3. **Content Requirements:**
     - **Context:** Briefly describe what utilities were created.
     - **"Fresh Terminal" Testing Instructions:**
       - How to set up the venv and install requirements.
       - **Verification Script:** Provide a specific Python snippet (using `python -c` or a temporary script) that imports a utility function (like the logger or path validator) and runs it.
       - **Expected Output:** Show exactly what the success message looks like in the terminal.

  ### STEP 2: Holistic Analysis for Next Phase
  1. **Analyze Phase 4 vs Phase 5:** Review the current utilities again to ensure they are sufficient to support the parsing logic required in Phase 5. If minor adjustments to utilities are needed to support the parser, identify them
  now.

  ### STEP 3: Implement Phase 5 (Parsers)
  **Target File:** `scripts/ssp_pipeline/parsers/pandoc_ast.py`

  **Goal:** Parse Pandoc JSON AST into the internal block model described in `SSP_Document_Publish_Pipeline_CORE.md`.

  **Process:**
  1. **Plan:**  to understand the target model. Provide a short plan (5 bullets) in the chat.
  2. **Implement:** Write the code for `pandoc_ast.py` in small chunks.
     - Requirement: Read Pandoc JSON AST.
     - Requirement: Convert to internal block model.
     - Requirement: Ensure type hints and docstrings are rigorous.
     - *Constraint:* Prefer clarity over cleverness.

  ### STEP 4: Phase 5 Milestone Documentation
  Once the code is implemented:
  1. Update `requirements.txt` if any new libraries were needed.
  2. Create the milestone documentation file: `documentation/milestones/P05_Parsers_PandocAST.md`.
  3. **Content Requirements:**
     - **"Fresh Terminal" Testing Instructions:**
       - Setup/Install steps.
       - **Verification Script:** A Python snippet to parse a sample Pandoc JSON string and print the resulting Block Model object.
       - **Expected Output:** The specific console output indicating success.

  # NEXT

  **GOAL**: Perform a "Session Flush". Synchronize the volatile session context (code changes, decisions) into the persistent documentation.

**SYSTEM INSTRUCTION: SESSION FLUSH & HANDOFF**

**GOAL:** Synchronize `SSP_PROJECT_STATUS.md` and `CHANGELOG.md` for context continuity.
**CONTEXT:** `scripts/`, `SSP_PROJECT_STATUS.md`, `CHANGELOG.md`.

**STEP 1: AUDIT & SCAN (Serena/Tools)**
1. **[IMPORTANT]** Engage **Serena MCP** (if available) to validate the current file architecture against the Roadmap.
   - *Fallback:* If Serena is unavailable/errors, run `ls -R scripts/` to verify reality.
2. Read `SSP_PROJECT_STATUS.md` and `CHANGELOG.md`.

**STEP 2: COMPILE STATUS UPDATES**
Construct the new `SSP_PROJECT_STATUS.md` content:

*   **SECTION A: DASHBOARD (Overwrite)**
    *   `## 📍 Current Focus`: Set "Active Tasks" and "Next Up" to immediate reality.
    *   `## 📅 Roadmap`: **[IMPORTANT]** Compare reality vs plan. **REWRITE** lines if the plan changed. Do not just check boxes on a stale plan.

*   **SECTION B: HISTORY (Append)**
    *   `## 🧠 Decision Log`: Append new architectural decisions using strict format (`* **YYYY-MM-DD:** [Topic] Changed... Reason...`).
    *   `## 🚧 Known Constraints`: Keep existing.

*   **SECTION C: THE BRAIN DUMP (Overwrite)**
    *   `## ⚡ Active Context`: Generate a fresh summary of the session.
    *   **Latest Summary:** 2-3 sentences on status (e.g., "Phase 6 started, HTML generator stubbed").
    *   **Critical Technical State:** Specifics on broken/risky files.
    *   **Carry-Over Notes:** User preferences (e.g., "Use Project Mode", "Command Voice tags active").

**STEP 3: CHANGELOG VERIFICATION**
1. Check if work done in this session is recorded in `CHANGELOG.md`.
2. If missing, draft a new entry following PRP conventions.

**STEP 4: EXECUTION**
1. **CRITICAL:** Overwrite `SSP_PROJECT_STATUS.md` with the new content.
2. **CRITICAL:** Update `CHANGELOG.md` (if needed).
3. Report: "✅ **Project Status & Changelog Updated.** Ready for Handoff."
  ```