````markdown
# SSP Pipeline — Phase-Based Prompt Playbook (v1)

This is a **full project script** for Claude Code, structured by phases.  
Follow in order from Phase 0 → Phase 9. Each phase has:
- **Goal**
- **Prerequisites**
- **Claude prompts** (for Project Mode)
- **Shell commands** (you run in terminal)
- **Exit criteria** (how you know the phase is done)

---

## Phase 0 — Boot, Context, and Rules

**Goal:** Load PRP, core spec, and CLAUDE rules into Claude Code.

**Claude Prompt (Project Mode ON):**
```text
use PRP/SSP_PRP_CORE.md as project rules.
quietly read:
- SSP_Document_Publish_Pipeline_CORE.md
- CLAUDE.md
when done, reply only with: ready
````

**Optional verification:**

```text
summarize the active PRP policies and key points from SSP_Document_Publish_Pipeline_CORE.md in 5–10 bullets.
```

**Exit criteria:**

* Claude responds with `ready`.
* Claude can list core policies when asked.

---

## Phase 1 — Environment & Tooling Bootstrap

**Goal:** Ensure `uv`, `pyproject.toml`, and dev tools (`ruff`, `pytest`) are set up.

**Shell (project root):**

```bash
uv init            # if pyproject.toml does not exist
uv add --dev ruff pytest
```

**Claude Prompt:**

```text
check if our environment matches the PRP environment policy.
if pyproject.toml or required dev tools are missing, list the exact uv commands I should run.
do not run commands yourself.
```

**Exit criteria:**

* `pyproject.toml` exists.
* This works without error:

  ```bash
  uv run ruff --version
  uv run pytest -q || true
  ```

---

## Phase 2 — Stub Phase (Structure Only)

**Goal:** Create all module files under `scripts/ssp_pipeline/` with docstrings, type hints, and TODOs; no real logic.

**Claude Prompt:**

```text
initialize stub phase:
create empty Python modules under scripts/ssp_pipeline/ as defined in PRP/SSP_PRP_CORE.md and SSP_Document_Publish_Pipeline_CORE.md.
requirements:
- no implementation logic yet
- for each module:
  - imports (only what is needed for signatures)
  - module-level docstring (plain english)
  - type-hinted function/class shells
  - TODOs in human-readable language describing intent
respond with:
1) short plan (3–6 bullets)
2) file list with relative paths
3) code stubs ready for commit
```

**Shell (optional, after stubs):**

```bash
uv run ruff check scripts/ssp_pipeline/ --fix
```

**Exit criteria:**

* All target modules & `__init__.py` files exist.
* Ruff passes or only reports expected stub warnings.

---

## Phase 3 — Comment & Docstring Quality Pass

**Goal:** Ensure every stub is documented and human-readable before adding logic.

**Claude Prompt:**

```text
pass 1: comments and docstrings only.
for all files under scripts/ssp_pipeline/:
- verify module-level docstrings exist and are clear
- verify each public function/class has a plain-english docstring
- ensure TODOs describe intended behavior, not just "TODO: implement"
- add brief inline comments only where logic will be non-obvious later
make no functional changes.
summarize changes by file.
```

**Exit criteria:**

* You can understand the intended behavior of each module and function by reading docstrings/TODOs alone.

---

## Phase 4 — Implement Utils Layer

**Goal:** Implement `utils` functions for logging, file operations, and validation.

**Claude Prompt:**

```text
implement the utils layer first.
modules:
- scripts/ssp_pipeline/utils/logging.py
- scripts/ssp_pipeline/utils/file_ops.py
- scripts/ssp_pipeline/utils/validators.py
requirements:
- follow PRP comment and docstring policy
- keep functions small and typed
- respect soft 500-line limit per file
process:
1) propose a 5–7 bullet plan
2) implement one module at a time
3) show diffs for each module
```

**Shell:**

```bash
uv run ruff check scripts/ssp_pipeline/utils/
uv run pytest -q || true
```

**Exit criteria:**

* Utils functions compiled, linted, and are testable.
* You have at least a minimal test scaffold for utils or a plan to add it.

---

## Phase 5 — Implement Parsers (Pandoc AST)

**Goal:** Parse Pandoc JSON AST into an internal block model.

**Claude Prompt:**

```text
implement scripts/ssp_pipeline/parsers/pandoc_ast.py in small steps.
requirements:
- read pandoc JSON AST and convert it into the internal block model described in SSP_Document_Publish_Pipeline_CORE.md
- keep structure simple and well-documented
- prefer clarity over cleverness
process:
1) write a short plan (5 bullets)
2) implement in small chunks with explanations
3) ensure type hints and comments match behavior
```

**Shell (after implementation):**

```bash
uv run ruff check scripts/ssp_pipeline/parsers/
uv run pytest -q || true
```

**Exit criteria:**

* `pandoc_ast.py` can be imported and used in isolation.
* There is at least one test (or test plan) for AST parsing.

---

## Phase 6 — Implement Renderers (HTML + WeasyPrint)

**Goal:** Turn the internal block model into HTML and PDF.

**Claude Prompt:**

```text
implement the renderer layer in order:
1) scripts/ssp_pipeline/renderers/html_generator.py
2) scripts/ssp_pipeline/renderers/weasyprint_renderer.py
requirements:
- html_generator: convert internal block model into HTML using configured CSS classes
- weasyprint_renderer: take HTML + CSS and produce PDF using weasyprint
- maintain clear interfaces, type hints, and docstrings
work in small steps and show diffs per file.
```

**Shell:**

```bash
uv run ruff check scripts/ssp_pipeline/renderers/
uv run pytest -q || true
```

**Exit criteria:**

* HTML generation and PDF rendering functions exist and are reasonably tested.

---

## Phase 7 — Implement Core Modules (Config, Metadata, Pipeline)

**Goal:** Orchestrate the full markdown → JSON → AST → HTML → PDF flow.

**Claude Prompt:**

```text
implement the core modules in this order:
1) scripts/ssp_pipeline/config.py
2) scripts/ssp_pipeline/metadata.py
3) scripts/ssp_pipeline/pipeline.py
requirements:
- config: load layout profiles, paths, and engine choices (weasyprint default)
- metadata: normalize YAML front matter and related metadata fields
- pipeline: orchestrate end-to-end flow using utils, parsers, and renderers
handle one module at a time, with a short plan and diffs for each.
```

**Shell:**

```bash
uv run ruff check scripts/ssp_pipeline/
uv run pytest -q || true
```

**Exit criteria:**

* `pipeline.py` exposes a clear callable entry point (e.g., `run_pipeline` or CLI wrapper).
* Core modules integrate utils, parsers, and renderers without obvious gaps.

---

## Phase 8 — Layout Helpers (Scribus + CSS)

**Goal:** Implement layout helper modules and keep them simple.

**Claude Prompt:**

```text
implement layout helpers:
- scripts/ssp_pipeline/layouts/scribus_extractor.py
- scripts/ssp_pipeline/layouts/css_builder.py
align behavior with SSP_Document_Publish_Pipeline_CORE.md, but keep each file focused and readable.
add comments/docstrings explaining how these helpers interact with the rest of the pipeline.
```

**Shell:**

```bash
uv run ruff check scripts/ssp_pipeline/layouts/
uv run pytest -q || true
```

**Exit criteria:**

* Layout helpers can be imported and used by `config.py` or `pipeline.py` as described in the core spec.

---

## Phase 9 — End-to-End Test & Technical Documentation

**Goal:** Verify the full flow and generate a long-term technical reference.

### 9a) End-to-End Test Plan

**Claude Prompt:**

```text
propose a minimal end-to-end test:
- input: specific markdown file under drafts/
- process: pandoc json export → pipeline entrypoint
- output: html and pdf under published/
provide:
- uv commands to run
- expected file paths
- what to check to confirm success.
```

**Shell (example):**

```bash
pandoc drafts/example.md -t json -o assets/xml/metadata/example.json
uv run python -m scripts.ssp_pipeline.pipeline drafts/example.md
```

### 9b) Generate Technical Design Document

**Claude Prompt:**

```text
generate a full technical design document for this project.
include:
- problem statement and goals
- high-level architecture (markdown → json → AST → html → pdf)
- module-by-module breakdown
- data flow across folders (drafts, assets, templates, published, releases)
- extension points and configuration
output as markdown suitable for docs/SSP_Technical_Design.md.
```

### 9c) Update PRP and Build Notes

**Claude Prompt:**

```text
after this milestone, propose updates to:
- PRP/SSP_PRP_CORE.md
- build_notes.md
summarize what changed in architecture and workflow, then show proposed diffs.
```

**Exit criteria:**

* End-to-end run works for at least one markdown file.
* `docs/SSP_Technical_Design.md` and PRP reflect the current reality.

---

## Phase 10 — Resuming Future Work

Any time you come back to this project (new day / new session):

**Claude Prompt:**

```text
use PRP/SSP_PRP_CORE.md as project rules.
quietly read:
- SSP_Document_Publish_Pipeline_CORE.md
- CLAUDE.md
when done, reply only with: ready
```

Then:

```text
summarize the current implementation status of scripts/ssp_pipeline/ and suggest the next 3 concrete tasks.
```

Use this to re-enter the project at the correct phase without rereading everything manually.

```
```
