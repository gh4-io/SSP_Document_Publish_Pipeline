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
  - keep files < 500 lines
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
- code generation: Claude 3 Opus (or highest available)
- bulk text or markdown editing: Claude 3 Haiku
- agents should automatically select the model based on task type.
- prefer lower-token models for reading or summarization to minimize cost.
- always confirm before switching to a high-cost model.


project mode policy:
- default to Project Mode ON for all planning, code generation, and refactor tasks.
- switch to File Mode only for single-file formatting or textual edits.
- when uncertain, stay in Project Mode to preserve repo context.

session reload policy:
- when project context is lost or VS Code restarts, auto-run boot command:
  use PRP/SSP_PRP_CORE.md as project rules.
  quietly read SSP_Document_Publish_Pipeline_CORE.md and CLAUDE.md.
- respond "ready" when cache restored.
- confirm PRP version and last changelog line to verify sync.

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