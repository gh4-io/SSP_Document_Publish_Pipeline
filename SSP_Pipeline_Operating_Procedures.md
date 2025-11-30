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