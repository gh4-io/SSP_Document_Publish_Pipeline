# SSP PRP core

scope:
- repo: SSP_Document_Publish_Pipeline
- domain: sop/std/ref/app publishing
- main spec: SSP_Document_Publish_Pipeline_CORE.md
- dev rules: CLAUDE.md

priority:
- follow SSP_Document_Publish_Pipeline_CORE.md over old docbook/scribus docs
- scribus = design only, not render
- markdown = single source of truth

roles:
- coder (Claude Code):
  - focus: implementation, refactoring, testing.
  - context: specific files being edited + project rules.
- auditor (Serena / MCP):
  - focus: repo-wide analysis, drift detection, roadmap verification.
  - task: compare `SSP_PROJECT_STATUS.md` vs actual file state.
  - frequency: run before major phases or when "lost".

agent rules:
- read:
  - PRP/SSP_Document_Publish_Pipeline_CORE.md
  - PRP/CLAUDE.md
- do not:
  - edit .sla xml
  - move/delete drafts/, published/, releases/ without user ask
- must:
  - use weasyprint pipeline by default
  - keep functions small, typed
  - complexity over brevity: 
    - target < 500 lines per file.
    - if > 500 lines: prefer cohesive logic over artificial splitting.
    - if > 800 lines: mandatory refactor proposal required.
  - docstrings: mandatory for all public functions (does not count toward complexity).
  - run ruff / pytest when possible

code layout (target):
- scripts/ssp_pipeline/
  - config.py
  - metadata.py
  - pipeline.py
  - parsers/pandoc_ast.py (+ helpers)
  - renderers/html_generator.py
  - renderers/weasyprint_renderer.py
  - layouts/scribus_extractor.py
  - layouts/css_builder.py
  - utils/logging.py
  - utils/file_ops.py
  - utils/validators.py

workflow per task:
1) scan repo (rg, ls) and read relevant files
2) write short plan (3–7 bullets, filenames)
3) change few files at a time
4) run uv commands when present:
   - uv run ruff check .
   - uv run pytest
5) output:
   - what changed
   - how to run it
   - open questions (very short)

file editing safety policy:
- MANDATORY: Read file before EVERY Edit operation (even if read earlier in session)
- LIMIT: No more than 2 consecutive Edit calls on same file without re-reading
- BATCH: For multiple changes to same section, use single Edit with larger old_string/new_string
- VERIFY: After Edit, use Bash (head/tail) to confirm change applied correctly
- RECOVERY: If Edit fails with ENOENT:
  1. Use Bash to verify file exists
  2. Re-read file to refresh state
  3. Check if change already applied before retrying
- FALLBACK: For complete file rewrites (>50% changed), use Write instead of Edit

self-update policy:
- claude code and approved agents may update PRP and core docs when:
  - a new phase begins (scaffolding, implementation, integration)
  - architecture, naming, or workflow changes occur
  - new conventions are established during code evolution

update rules:
- summarize proposed change in chat before editing ("PRP update proposal: <summary>")
- apply small, atomic edits — never rewrite full file
- add comment line: `# PRP updated <YYYY-MM-DD> <summary>`
- confirm in chat: `PRP updated: <summary>`
- never remove history; append or version sections
- if unsure, ask user before persistent edits

governance:
- human (Jason) retains override authority
- sensitive or structural changes require confirmation
- maintain version bump on each approved update (phase1 → phase2)
- keep changelog at bottom when revisions accumulate

example changelog:
    # changelog
    - 2025-12-01: phase2 init — added validation module rules
    - 2026-01-05: adjusted renderers structure; introduced css_builder.py

model usage policy:
- default: Claude 3.5 Sonnet (planning, reading, maintenance)
- code generation: Claude 3.5 Sonnet (default)
- bulk text or markdown editing: Claude 3 Haiku
- agents should automatically select the model based on task type.
- prefer lower-token models for reading or summarization to minimize cost.
- always confirm before switching to a high-cost model.


project mode policy:
- default to Project Mode ON for all planning, code generation, and refactor tasks.
- switch to File Mode only for single-file formatting or textual edits.
- when uncertain, stay in Project Mode to preserve repo context.

session reload policy:
- when project context is lost or VS Code restarts:
  1. User will run/prompt: "Run the boot command and digest the rules."
  2. Agent must execute `boot` (which cats the core rules).
  3. Agent must reply "SSP Pipeline Ready" when context is restored.

comment and docstring policy:

goal:
- future humans (including tired future me) must understand this project by reading code + comments alone.

rules:
- every module:
  - top-level docstring saying what this file is for and how it fits the pipeline.
- every class and public function:
  - docstring in plain english:
    - what it does
    - inputs / outputs
    - important side effects (files, network, subprocess, external tools like pandoc/weasyprint).
- complex logic or non-obvious lines:
  - add inline comments above the block, not at the end of the line.
  - explain intent, not mechanics (the “why”, not just the “what”).
- TODOs:
  - always include a human-readable sentence, not just "TODO: implement".
  - example: "TODO: validate YAML metadata against schema and collect all errors, do not raise on first failure."

style:
- use short, direct sentences.
- avoid jokes, metaphors, and vague wording.
- prefer clear naming + small functions over heavy commenting.
- comments must stay in sync with code; when code changes, update or remove stale comments.

enforcement:
- when generating or editing code, agent must:
  - add missing docstrings and key comments.
  - fix obviously stale comments.
  - call out any areas where intent is unclear and ask for clarification before guessing.


tool loading policy:
- prefer minimal tool environment
- only enable heavy agents (like serena) for repo-wide analysis

environment policy:
- environment manager: uv
- if pyproject.toml is missing, auto-run:
  uv init
  uv add --dev ruff pytest
- ensure these dev tools are always present:
  ruff, pytest, weasyprint, pandoc


changelog policy:
- maintain a CHANGELOG.md in the project root.
- use this structure:
  # Changelog

  ## [YYYY-MM-DD] <short phase or feature name>
  - <1–2 sentence summary>
  - <bullets grouped by area: utils, parsers, renderers, core, layouts, tests, docs, PRP>

- language must be plain and human-readable.
- never delete or rewrite past entries; always append new ones at the top.

changelog automation rule:
- after each significant phase or commit batch, Claude may:
  1) inspect the current git diff and relevant files.
  2) propose a new changelog entry (date, phase title, bullets).
  3) show the proposed CHANGELOG.md diff.
  4) only write to CHANGELOG.md after user approval.
- changelog updates should be included in the same commit as the related code changes.


project state policy:
- The file `SSP_PROJECT_STATUS.md` is the source of truth for progress.
- BEFORE starting code: Read `SSP_PROJECT_STATUS.md`.
- AFTER finishing a task:
  1. Check off the item in `SSP_PROJECT_STATUS.md`.
  2. Update the "Current Focus" section.
  3. Log any architectural changes in "Decision Log".
- If the user requests work that contradicts the Roadmap:
  - Warning: "This deviates from the Phase <X> plan."
  - Ask: "Should we update the Decision Log and Proceed?"

# PRP Changelog
- 2025-11-30: Added "file editing safety policy" — prevents ENOENT errors by mandating Read before Edit, limiting consecutive edits, and providing recovery protocol.
