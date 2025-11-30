# SSP bootstrap notes

repo root:
- SSP_Document_Publish_Pipeline/
  - CLAUDE.md
  - SSP_Document_Publish_Pipeline_CORE.md
  - PRP/SSP_PRP_CORE.md
  - scripts/ssp_pipeline/ (stubs ok)
  - drafts/, templates/, assets/, published/, releases/, styles/

env:
- uv venv
- uv sync  (if pyproject.toml exists)

quick checks:
- uv run python -m pip list
- uv run ruff check .   (ok if config missing)
- uv run pytest         (ok if no tests yet)

first agent startup (claude code):
- open repo folder in vscode
- open:
  - SSP_Document_Publish_Pipeline_CORE.md
  - CLAUDE.md
  - PRP/SSP_PRP_CORE.md
- send:

  "treat PRP/SSP_PRP_CORE.md as project rules.
   quietly read SSP_Document_Publish_Pipeline_CORE.md and CLAUDE.md.
   when ready, reply only with: ready"

then send:

  "implement week-1 core of the weasyprint pipeline under scripts/ssp_pipeline/.
   focus on:
   - config.py
   - metadata.py
   - parsers/pandoc_ast.py
   - renderers/html_generator.py
   - renderers/weasyprint_renderer.py
   - pipeline.py
   use small steps, show a short plan first, then edits."

serena startup (similar):
- point serena at repo root
- tell it:

  "use PRP/SSP_PRP_CORE.md as project rules.
   read SSP_Document_Publish_Pipeline_CORE.md and CLAUDE.md.
   summarize in 3–5 bullets how you will work, then stop."

then give concrete tasks (same as claude code).
