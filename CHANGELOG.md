# Changelog

All notable changes to the SSP Document Publishing Pipeline project.

## [2025-11-30] Phase 4-5: Utils Documentation + Parser Implementation

### Phase 4: Retroactive Milestone Documentation
**Deliverable:** `documentation/milestones/P04_Utilities_Core.md`

**Content:**
- Fresh terminal testing instructions for logging, file_ops, validators
- Verification script with expected output
- Function capability summary (11 functions, 351 LOC)

### Phase 5: Pandoc AST Parser Implementation

**Core Parser (`pandoc_ast.py` - 5 functions, ~140 lines):**
- Implemented `parse_pandoc_json()` - JSON loading and error handling
- Implemented `parse_block()` - Type dispatch for all Pandoc block types (Header, Para, BulletList, OrderedList, CodeBlock, BlockQuote→Callout, Table)
- Implemented `extract_inline_text()` - Recursive inline element flattening (Str, Space, LineBreak, Emph, Strong, Code, Link, Image)
- Implemented `detect_callout()` - Obsidian admonition detection (`[!WARNING]`, `[!DANGER]`, `[!NOTE]`, `[!TIP]`, `[!INFO]`, `[!CAUTION]`)
- Implemented `parse_wikilink()` - Internal reference syntax parsing (`[[target | display]]`)

**Specialized Parsers (~430 lines total):**
- `callouts.py` (~50 lines) - Documentation module (logic in core parser)
- `images.py` (~95 lines) - Asset path resolution via file_ops integration (standard Markdown + Obsidian wikilink images)
- `wikilinks.py` (~110 lines) - Target resolution against published/ directory (exact match, glob, recursive search)
- `tables.py` (~225 lines) - Pandoc table structure → simplified headers/rows model

**Testing:**
- Created `tests/fixtures/sample_test.json` with realistic Pandoc JSON
- Verified parser with 5 block types (heading, paragraph, list, callout, code)
- Phase 5 milestone test passing ✅

**Code Quality:**
- All functions < 50 lines
- Full type hints and docstrings
- Stdlib-only dependencies (json, pathlib, re, logging, typing)
- Total parser layer: ~570 lines across 5 modules
- Error handling: log warnings for unsupported Pandoc types, never crash

**Deliverable:** `documentation/milestones/P05_Parsers_PandocAST.md`

---

## [2025-11-30] Phase 1-4: Initial Implementation

### Phase 2: Project Scaffold and Architecture
**Commit:** e59cef9 (2025-11-30)

**Core:**
- Established Pandoc → JSON AST → HTML + CSS → WeasyPrint pipeline
- Created main pipeline orchestrator stub (pipeline.py)
- Added configuration loader (config.py) and metadata parser (metadata.py) stubs
- Initialized Python package structure with `__init__.py` exports

**Parsers:**
- Created Pandoc AST parser with block model (headings, paragraphs, lists, tables, code)
- Added specialized parser stubs for callouts, images, tables, wikilinks
- Defined dataclass-based block types for type-safe parsing

**Renderers:**
- Created HTML generator stub for block-to-HTML conversion
- Added WeasyPrint renderer stub for HTML-to-PDF conversion
- Included legacy Scribus renderer stub for fallback compatibility

**Layouts:**
- Added Scribus layout extractor for frame geometry extraction
- Created CSS builder for converting Scribus layouts to WeasyPrint CSS

**Utils:**
- Created logging, file operations, and validation utility stubs
- Prepared directory structure for logs, published outputs, and releases

**PRP/Documentation:**
- Added SSP_PRP_CORE.md (project rules and conventions)
- Added SSP_Document_Publish_Pipeline_CORE.md (technical specification)
- Added CLAUDE.md (AI agent development guidelines)
- Created BUILD_NOTES.md and PIPELINE_SEQ.md for implementation tracking

**Project Structure:**
- Added pyproject.toml and uv.lock for dependency management
- Updated .gitignore for tool caches (.ruff_cache, .claude, .serena)
- Removed legacy Scribus-centered documentation
- Reformatted layout profiles and templates

### Phase 3: Documentation and Code Quality
**Commit:** ec44df6 (2025-11-30)

**All Modules:**
- Added comprehensive module-level docstrings to all 21 Python files
- Added function/class docstrings with clear parameter and return type documentation
- Enhanced TODO comments with specific implementation requirements
- Added inline comments for non-obvious logic

**Parsers:**
- Documented callout detection for Obsidian-style admonitions
- Documented image parsing for Markdown and wikilink syntax
- Documented table structure extraction from Pandoc
- Documented wikilink resolution for internal references

**Renderers:**
- Documented Scribus renderer as legacy fallback option
- Clarified WeasyPrint as primary rendering engine

### Phase 4: Utils Layer Implementation
**Commits:** f5fada0, d27e572, fad2a8e (2025-11-30)

**Utils - Logging (89 lines):**
- Implemented `setup_logger` with console and optional file handlers
- Daily log files with format: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [module] message`
- Auto-creates logs/ directory
- Added `log_pipeline_start` and `log_pipeline_complete` for execution tracking

**Utils - File Operations (122 lines):**
- Implemented `ensure_dir` for directory creation with parents
- Implemented `resolve_asset_path` with recursive asset directory search
- Implemented `copy_to_published` for standardized output naming
- Implemented `archive_to_releases` with timestamped immutable archives

**Utils - Validators (140 lines):**
- Implemented `validate_markdown` with YAML front matter detection
- Implemented `validate_profile` for layout profile schema validation
- Implemented `validate_metadata` for required fields checking
- Implemented `validate_css_path` for CSS file validation

**Code Quality:**
- All functions fully typed with type hints
- All modules under 200 lines (well under 500-line limit)
- Stdlib-only dependencies (logging, pathlib, shutil, datetime)
- Clear error messages for validation failures

---

## Project Status

**Completed:**
- ✅ Project scaffold and architecture
- ✅ Complete documentation and docstrings
- ✅ Utils layer (logging, file ops, validators)

**In Progress:**
- 🔄 Core modules (config, metadata, pipeline)
- 🔄 Parsers (Pandoc AST, callouts, images, tables, wikilinks)
- 🔄 Renderers (HTML generation, WeasyPrint rendering)
- 🔄 Layouts (Scribus extraction, CSS building)

**Planned:**
- ⏳ Integration testing
- ⏳ End-to-end pipeline testing
- ⏳ Documentation examples