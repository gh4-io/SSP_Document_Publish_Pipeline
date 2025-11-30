# build_notes.md — Claude Code Project Session Summary

## ⚡ Quick Start / Boot Command

Use this every time you start, reopen, or reload the project:

```text
use PRP/SSP_PRP_CORE.md as project rules.
quietly read:
- SSP_Document_Publish_Pipeline_CORE.md
- CLAUDE.md
when done, reply only with: ready
```

This command initializes Claude Code with your PRP rules, main specification, and guidance file.
Claude should reply only with `ready` when context is successfully loaded.

---

## 🔁 When PRP or CORE Are Modified

If you edit **SSP_PRP_CORE.md**, **SSP_Document_Publish_Pipeline_CORE.md**, or **CLAUDE.md**:

1. Save your changes.
2. In Claude Code, run:

   ```text
   reload PRP/SSP_PRP_CORE.md to include the latest project rules.
   ```
3. Claude will confirm with something like:
   `PRP reloaded successfully.`

If you restart VS Code or open a new session:

```text
use PRP/SSP_PRP_CORE.md as project rules.
quietly read:
- SSP_Document_Publish_Pipeline_CORE.md
- CLAUDE.md
when done, reply only with: ready
```

That ensures your session and rules are fully synchronized.

---

## 🧭 Overview

This session focused on refining your Claude Code project setup for **SSP_Document_Publish_Pipeline**.
We finalized how PRP files govern behavior, agent policies, test handling, comment requirements, and model control.

---

## ❓ Key Q&A

**Q: Should we create stub modules before implementing logic?**
A: Yes. Stubs keep architecture stable, enforce structure, and simplify later logic insertion.

**Q: How do I control Claude Code’s model (Sonnet/Opus/Haiku)?**
A: You can request the model or add a rule in the PRP to require Claude to declare and confirm which model is active.

**Q: Should I limit lines per file?**
A: Yes — a 500-line *soft limit* prevents bloat. It’s a readability boundary, not a hard cutoff.

**Q: What about human-readable comments?**
A: Required everywhere. Each module, class, and function must have plain-language docstrings and context comments.

**Q: When should full documentation be generated?**
A: After v0.1 or the first working pipeline run. Then instruct Claude:
`generate a full technical design document summarizing architecture, modules, data flow, and operations`

**Q: What about bash testing and agents?**
A: Use a lightweight MCP agent (like *Test Runner*) to execute tests locally. Claude should only receive summaries.
Avoid streaming long logs — they consume tokens unnecessarily.

**Q: Serena is using too many tokens. Can she be turned off?**
A: Yes. Disable or detach the Serena MCP agent except when needed for refactor/search.
Add this to PRP:

```
tool loading policy:
- prefer minimal tool environment
- only enable heavy agents (like serena) for repo-wide analysis
```

This ensures minimal token footprint.

---

## 🚀 How to Start the Project (Boot Command)

```text
use PRP/SSP_PRP_CORE.md as project rules.
quietly read:
- SSP_Document_Publish_Pipeline_CORE.md
- CLAUDE.md
when done, reply only with: ready
```

Then run your first stub scaffold:

```text
initialize stub phase:
create empty Python modules under scripts/ssp_pipeline/ as defined in PRP/SSP_PRP_CORE.md and SSP_Document_Publish_Pipeline_CORE.md.
requirements:
- no logic yet
- include type-hinted signatures
- include docstrings and human-readable TODOs
show short plan, then file list.
```

---

## 🪜 Next Steps

1. **Confirm PRP and CORE alignment**
   - Ensure both are in `/PRP/` and committed.
2. **Generate stubs** with the stub command above.
3. **Run validation checks:**
   ```bash
   uv run ruff check scripts/ssp_pipeline/
   uv run pytest
   ```
4. **After stubs are approved**, start real implementation:
   - Begin with `utils/`, then `parsers/`, `renderers/`, `core/`, `layouts/`.
5. **After v0.1 build passes tests**, generate documentation:
   ```text
   generate a full technical design document for this project.
   ```

---

## 🧩 Looming Questions / Common Checks

- When do we trigger a full documentation update?
  → After stable architecture or major refactor.
- Should all MCP agents be preloaded?
  → No. Use live discovery only when needed.
- When to run tests?
  → After completing a module, before release — not every step.
- How to verify PRP sync after restart?
  → Run `reload PRP/SSP_PRP_CORE.md` or boot command again.

---

## 🧠 Future Chat Summary (for reload context)

When resuming this project, run:


reload PRP/SSP_PRP_CORE.md to restore session.
summarize current PRP and project policies before continuing.


Then continue development from the last module implemented.

---


# SSP Pipeline – Prompt Sequence (Start → Finish)

1) boot / reload session

use PRP/SSP_PRP_CORE.md as project rules.
quietly read:
- SSP_Document_Publish_Pipeline_CORE.md
- CLAUDE.md
when done, reply only with: ready


2) verify understanding of rules (optional)

summarize the active PRP policies and key points from SSP_Document_Publish_Pipeline_CORE.md in 5–10 bullets.


3) stub phase – create module skeletons

initialize stub phase:
create empty Python modules under scripts/ssp_pipeline/ as defined in PRP/SSP_PRP_CORE.md and SSP_Document_Publish_Pipeline_CORE.md.
requirements:
- no implementation logic yet
- include:
  - imports
  - module-level docstrings
  - type-hinted function/class signatures
  - human-readable TODOs for intended behavior
respond with:
1) short plan (3–6 bullets)
2) file list with relative paths


4) comment + docstring pass (if needed)

pass 1: comments and docstrings only.
for all files under scripts/ssp_pipeline/:
- add module-level docstrings
- add function/class docstrings in plain english
- add human-readable TODOs where logic will go
- do not change any real implementation logic
summarize edits by file.


5) environment sanity (if pyproject missing)

check whether uv environment and pyproject.toml exist for this project.
if missing, propose concrete steps but do not run commands.


6) implement utils first

implement the utils layer first.
focus on:
- scripts/ssp_pipeline/utils/logging.py
- scripts/ssp_pipeline/utils/file_ops.py
- scripts/ssp_pipeline/utils/validators.py
requirements:
- follow PRP comment and docstring policy
- keep functions small and typed
- stay under the soft file-size limit
show:
1) short plan
2) diffs per file


7) suggest tests for utils

based on the current utils implementation, propose:
- minimal pytest test cases
- file layout under tests/
- short commands to run tests with uv
only output code and commands, do not run anything.


8) implement parsers (pandoc_ast)

implement scripts/ssp_pipeline/parsers/pandoc_ast.py in small steps.
requirements:
- parse pandoc JSON AST into a clean internal block model
- keep code readable and well-commented
- align behavior with SSP_Document_Publish_Pipeline_CORE.md
start with a 5-bullet plan, then implement incrementally.


9) implement renderers (html + weasyprint)

implement these modules in order:
- scripts/ssp_pipeline/renderers/html_generator.py
- scripts/ssp_pipeline/renderers/weasyprint_renderer.py
requirements:
- generate HTML from the internal block model
- call weasyprint to produce PDFs using layout CSS
- keep interfaces clean and documented
work in small steps and show diffs per file.


10) implement core (config, metadata, pipeline)

implement core modules in this order:
1) scripts/ssp_pipeline/config.py
2) scripts/ssp_pipeline/metadata.py
3) scripts/ssp_pipeline/pipeline.py
requirements:
- load layout profiles and resources
- normalize YAML front matter and metadata
- orchestrate markdown → json → AST → html → pdf flow
provide a short plan, then implement each module one at a time.


11) implement layouts helpers

implement layout helpers:
- scripts/ssp_pipeline/layouts/scribus_extractor.py
- scripts/ssp_pipeline/layouts/css_builder.py
align behavior with the core spec, but keep each file focused and readable.


12) test and validate end-to-end

propose a minimal end-to-end test:
- from a sample markdown file in drafts/
- through pandoc json export
- into the pipeline script
output only:
- commands to run with uv
- expected outputs (pdf/html paths)
- what to check if something fails.


13) generate full technical design document

generate a full technical design document for this project.
include:
- overview of the problem and goals
- architecture diagram in text form
- module-by-module description
- data flow (drafts → assets → published → releases)
- extension points and configuration
output as a single markdown file suitable for docs/SSP_Technical_Design.md.


14) update PRP and build notes after major changes

after any major architectural change or v0.1 milestone, do:
- propose PRP updates
- summarize changes
- update build_notes.md or equivalent notes file
always show a concise summary of edits.


15) resume work in future sessions

when resuming later, always start with:

use PRP/SSP_PRP_CORE.md as project rules.
quietly read:
- SSP_Document_Publish_Pipeline_CORE.md
- CLAUDE.md
when done, reply only with: ready

then ask:

summarize current implementation status and suggest the next 3 concrete tasks.


