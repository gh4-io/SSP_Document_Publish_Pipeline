# SSP Pipeline - Claude Assistant Config

## Core Information
- **Project Rules**: `PRP/SSP_PRP_CORE.md` (Authority)
- **Architecture**: `PRP/SSP_Document_Publish_Pipeline_CORE.md`

## Commands
- **test**: `uv run pytest`
- **lint**: `uv run ruff check .`
- **clean**: `rm -rf published/ drafts/*.html`
- **boot**: `cat PRP/SSP_PRP_CORE.md SSP_Document_Publish_Pipeline_CORE.md`

## Style
- Use `uv` for package management.
- Python 3.12+ features enabled.
- Docstrings required for all modules.