# Phase 7 Milestone: Core Integration (Pipeline Orchestrator)

**Date:** 2025-11-30
**Status:** ✅ Complete
**Deliverable:** End-to-end Markdown → PDF workflow orchestration + live watch mode

---

## Implementation Summary

### config.py (157 lines)
**Purpose:** Configuration loading and rendering engine selection

**Functions Implemented:**
1. `load_layout_profile()` - Load and validate JSON profile
2. `get_rendering_engine()` - Extract rendering engine with default fallback
3. `get_resource_paths()` - Resolve all resource paths to absolute paths
4. `get_styles_map()` - Extract Pandoc → CSS styles mapping

**Features:**
- JSON profile loading with schema validation
- Support for both WeasyPrint and Scribus engines
- Automatic path resolution relative to project root
- Backward compatibility with DocBook-style profiles
- Detailed logging of configuration steps

---

### metadata.py (184 lines)
**Purpose:** YAML frontmatter parsing and metadata normalization

**Functions Implemented:**
1. `parse_frontmatter()` - Extract YAML frontmatter from Markdown
2. `normalize_metadata()` - Normalize field names and validate required fields
3. `extract_document_id()` - Validate and extract document ID (e.g., SOP-200)
4. `get_required_fields()` - Define required metadata fields
5. `merge_with_defaults()` - Merge user metadata with defaults

**Features:**
- Simple YAML parser (stdlib-only, key:value pairs)
- Field name normalization (handles doc_id, docid, id → document_id)
- Document ID validation (TYPE-NNN format)
- Required fields: document_id, title, revision, author
- Auto-generation of timestamp (generated_at)

---

### pipeline.py (231 lines)
**Purpose:** Main workflow orchestration (Markdown → PDF)

**Functions Implemented:**
1. `run_pipeline()` - Execute complete 9-step publishing workflow
2. `generate_pandoc_ast()` - Call Pandoc subprocess to generate JSON AST
3. `cleanup_temp_files()` - Clean up temporary AST JSON files
4. `get_pipeline_version()` - Return version string (4.0.0)

**Workflow Steps:**
1. Load layout profile
2. Validate inputs (Markdown, profile schema)
3. Parse Markdown frontmatter
4. Generate Pandoc JSON AST (subprocess call)
5. Parse AST to block model
6. Generate HTML with CSS classes
7. Render to PDF (WeasyPrint or Scribus)
8. Copy to published/ directory
9. Archive to releases/ with timestamp

**Features:**
- Full end-to-end automation
- Detailed step-by-step logging
- Error handling at each step
- Pandoc subprocess integration with timeout
- Automatic directory creation
- Document categorization (SOP, STD, REF, APP)
- Temp file cleanup

---

### watch.py (185 lines)
**Purpose:** File monitor for live document authoring (WYSIWYG-ish behavior)

**Functions Implemented:**
1. `MarkdownChangeHandler` (class) - File system event handler
2. `watch_markdown()` - Monitor file and auto-rebuild on changes
3. `main()` - CLI entry point for watch mode

**Features:**
- Real-time file monitoring using watchdog
- Debounce logic (2-second default, prevents rapid re-triggers)
- Initial build on watch start
- Error-tolerant (rebuild failures don't crash watcher)
- Keyboard interrupt handling (Ctrl+C)
- Detailed rebuild status (✅ success / ❌ failure)

---

## Code Quality

**Total Lines:** 757 (157 + 184 + 231 + 185)
**Per-file Maximum:** 231 lines (well under 500-line limit)
**Type Hints:** 100% coverage
**Docstrings:** All functions documented
**Linting:** ✅ All ruff checks passing
**Dependencies:** stdlib + weasyprint + watchdog

---

## Testing Instructions ("Fresh Terminal")

### Prerequisites
```bash
# Install dependencies
uv sync

# Verify tools available
pandoc --version
uv run python -c "import weasyprint; print('WeasyPrint OK')"
uv run python -c "from watchdog.observers import Observer; print('Watchdog OK')"
```

### Test 1: Single Pipeline Run
```bash
# Create a test Markdown file with frontmatter
cat > test_doc.md <<'EOF'
---
document_id: SOP-999
title: Test Document
revision: 1.0
author: Test User
---

# Introduction
This is a test document.

> [!NOTE]
> This is a test callout.

## Section 2
Some content here.
EOF

# Run pipeline
uv run python -m scripts.ssp_pipeline.pipeline \
    test_doc.md \
    templates/profiles/layout_profile_dts_master_report.json
```

**Expected Output:**
```
==============================================================
SSP Document Publishing Pipeline v4 Starting
==============================================================
Step 1/9: Loading layout profile
Step 2/9: Validating inputs
Step 3/9: Parsing frontmatter
Document ID: SOP-999
Step 4/9: Generating Pandoc JSON AST
Step 5/9: Parsing AST to block model
Parsed 3 blocks
Step 6/9: Generating HTML
Step 7/9: Rendering to PDF using weasyprint
Step 8/9: Copying to published directory
Step 9/9: Archiving to releases
==============================================================
Pipeline Complete! Output: published/pdf/SOP-999.pdf
==============================================================
```

### Test 2: Watch Mode (Live Authoring)
```bash
# Start watch mode
uv run python -m scripts.ssp_pipeline.watch \
    drafts/SOP-200.md \
    templates/profiles/layout_profile_dts_master_report.json
```

**Expected Output:**
```
==============================================================
SSP Watch Mode Starting
==============================================================
Monitoring: /path/to/drafts/SOP-200.md
Profile: /path/to/templates/profiles/layout_profile_dts_master_report.json
Press Ctrl+C to stop
==============================================================
Running initial build...
[... pipeline output ...]
✅ Initial build complete: published/pdf/SOP-200.pdf

👀 Watching for changes... (Ctrl+C to stop)
```

**Manual Test:**
1. Edit `drafts/SOP-200.md` in another window
2. Save the file
3. Watch console for rebuild trigger
4. Verify PDF updates in `published/pdf/SOP-200.pdf`

---

## Integration Points

**Upstream Dependencies (Phase 4-6):**
- Utils: logging, file_ops, validators
- Parsers: pandoc_ast, callouts, images, wikilinks, tables
- Renderers: html_generator, weasyprint_renderer

**External Tools:**
- Pandoc (subprocess call for JSON AST generation)
- WeasyPrint (PDF rendering)
- Watchdog (file monitoring)

**Downstream Consumers:**
- Phase 8: CSS builder will use config.get_styles_map()
- Phase 8: Scribus extractor will integrate with config.get_resource_paths()

---

## Architectural Decisions

**Decision:** Default to WeasyPrint if rendering_engine not specified
**Reason:** New pipeline standard; Scribus is legacy fallback only

**Decision:** Simple YAML parser (stdlib-only)
**Reason:** Avoid PyYAML dependency; frontmatter structure is simple key:value pairs

**Decision:** Temp JSON files in /tmp/
**Reason:** Pandoc AST is intermediate artifact, not needed after pipeline run

**Decision:** 2-second debounce in watch mode
**Reason:** Editors often trigger multiple save events; prevents wasted rebuilds

**Decision:** Archive copies use document category (SOP, STD, REF, APP)
**Reason:** Aligns with organizational structure in releases/ directory

---

## Known Limitations

1. **YAML Parser:** Only supports flat key:value pairs, no nested structures
2. **Watch Mode:** Monitors single file only (not directory-wide)
3. **Pandoc Timeout:** 60-second hard limit (may fail on very large documents)
4. **Scribus Engine:** Stub only (not yet implemented, will error if selected)

---

## Next Steps (Phase 8)

1. Implement `layouts/scribus_extractor.py` (geometry extraction from .sla)
2. Implement `layouts/css_builder.py` (convert Scribus layout → CSS)
3. Test layout fidelity (WeasyPrint PDF vs Scribus reference)
4. Create sample layout profiles with Pandoc styles_map
