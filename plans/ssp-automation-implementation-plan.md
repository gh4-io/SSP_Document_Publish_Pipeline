---
title: SSP Document Automation - Implementation Plan
version: 1.0
date: 2025-12-01
author: Claude Code Planning
status: Ready for Implementation
input_document: research/ssp-automation-requirements.md
---

# SSP Document Automation - Implementation Plan

## Executive Summary

**Purpose**: Transform SSP document pipeline from manual Scribus-based workflow to automated, flexible Markdown → HTML/PDF system.

**Current State**:
- Manual Scribus PDF generation (10-15s per doc, brittle)
- No web output
- No metadata validation
- Manual image optimization
- No batch processing

**Target State**:
- Automated pipeline: Markdown → Pandoc → HTML/PDF
- Web + PDF outputs from single source
- Schema-validated metadata
- Auto-generated image variants (print/web)
- Batch processing w/ dependency tracking
- 10-15x faster PDF generation (WeasyPrint)

**Implementation Timeline**: 6 phases over ~3-4 months

---

## 1. Architecture Overview

### 1.1 High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MARKDOWN SOURCE                          │
│                (YAML front matter + content)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─→ [Metadata Validator] (jsonschema)
                     │   • Schema validation
                     │   • Cross-reference checks
                     │   • Status transition validation
                     │
                     ├─→ [Image Processor] (Pillow)
                     │   • Generate print variants (300 DPI PNG)
                     │   • Generate web variants (WebP multi-res)
                     │   • Create image registry
                     │
                     ↓
         ┌──────────────────────────────┐
         │   PANDOC JSON AST            │
         │   (via Lua filters)          │
         │   • Callouts                 │
         │   • Wikilinks                │
         │   • Custom directives        │
         └──────────┬───────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ↓                     ↓
    [HTML Builder]        [HTML Builder]
    (Jinja2)              (Jinja2)
         │                     │
         ↓                     ↓
    HTML + CSS            HTML + CSS
    (Web)                 (PDF-optimized)
         │                     │
         ↓                     ↓
    Web Output            [WeasyPrint]
    (Responsive)              │
         │                     ↓
         │                 PDF Output
         │                     │
         └─────────┬───────────┘
                   │
                   ↓
           [Release Packager]
           • Timestamped archives
           • Source + outputs
           • Metadata registry
```

### 1.2 Technology Stack

**Core Technologies**:
- **Pandoc** 3.6+: Markdown → JSON AST conversion
- **Lua filters**: Custom transformations (callouts, wikilinks, directives)
- **Jinja2**: HTML template rendering
- **WeasyPrint**: HTML → PDF rendering (10-15x faster than Scribus)
- **Pillow / Pillow-SIMD**: Image processing
- **jsonschema**: YAML metadata validation

**Supporting Libraries**:
- **PyYAML**: YAML parsing
- **Click**: CLI interface
- **Pygments**: Code syntax highlighting
- **tqdm**: Progress bars

**Asset Formats**:
- Print images: PNG @ 300 DPI
- Web images: WebP (640w, 1024w, 1920w)
- Fonts: WOFF2 (web), TTF (PDF)

### 1.3 Data Flow

```
INPUT: drafts/SOP-001.md
    ↓
1. Validate metadata (schemas/sop_metadata.json)
2. Process images (assets/images/master/ → print/web/)
3. Pandoc conversion (Markdown → JSON AST)
4. Apply Lua filters (callouts, wikilinks, directives)
5. Render HTML (templates/html/sop.html.j2)
6. Generate outputs:
   • Web: published/web/SOP-001.html
   • PDF: WeasyPrint → published/pdf/SOP-001.pdf
7. Package release (if status=Active)
    ↓
OUTPUT: HTML + PDF + release archive
```

### 1.4 Integration with Existing System

**Preserved Components**:
- ✅ YAML front-matter metadata schema
- ✅ Directory structure (`drafts/`, `assets/`, `published/`, `releases/`)
- ✅ Document state logic (Draft/Review/Active/Retired)
- ✅ Revision numbering system
- ✅ Release packaging pattern

**Replaced Components**:
- ❌ DocBook XML intermediate format → Pandoc JSON AST
- ❌ Scribus PDF generation → WeasyPrint
- ❌ Manual image optimization → Automated variants

**New Components**:
- ✨ Metadata validation (pre-pipeline)
- ✨ Web HTML output
- ✨ Batch processing w/ dependency tracking
- ✨ Image directive expansion

---

## 2. Phase Breakdown

### Phase 1: Foundation & Validation

**Objective**: Establish core infrastructure for validation, config management, error handling.

**Dependencies**: None (foundational phase)

**Tasks**:

#### 1.1 Create Configuration System
- **Files to create**:
  - `./config/default.yaml` - System defaults
  - `./config/profiles/sop.yaml` - SOP-specific config
  - `./config/profiles/std.yaml` - STD-specific config
  - `./config/profiles/ref.yaml` - REF-specific config
  - `./config/profiles/app.yaml` - APP-specific config
  - `./scripts/core/config.py` - Config loader class

- **Changes**:
  - Implement hierarchical config loader (default → profile → local)
  - Support dot-notation access (`config.get('pipeline.pandoc.executable')`)
  - Deep merge for config overrides

- **Rationale**: Centralized config prevents hard-coded paths/settings; enables per-family customization.

- **Verification**:
  ```bash
  python3 -c "from scripts.core.config import Config; c = Config('sop'); print(c.get('pipeline.pandoc.executable'))"
  ```

#### 1.2 Implement Metadata Validation
- **Files to create**:
  - `./schemas/sop_metadata.json` - JSON Schema for SOP metadata
  - `./schemas/std_metadata.json` - JSON Schema for STD metadata
  - `./schemas/ref_metadata.json` - JSON Schema for REF metadata
  - `./schemas/app_metadata.json` - JSON Schema for APP metadata
  - `./scripts/validators/metadata_validator.py` - Validation logic

- **Changes**:
  - Define JSON schemas for all document families
  - Implement `validate_metadata()` function (returns bool, errors list)
  - Implement `validate_cross_references()` for APN validation
  - Implement `validate_status_transition()` for revision rules
  - Create `ValidationReport` class for structured error reporting

- **Rationale**: Fast-fail validation prevents invalid docs from entering pipeline; clear error messages aid authoring.

- **Verification**:
  ```bash
  python3 -c "from scripts.validators.metadata_validator import validate_metadata; \
  print(validate_metadata('drafts/SOP-200_Create_Workackage_Sequencing_Type.md', 'schemas/sop_metadata.json'))"
  ```

#### 1.3 Setup Logging & Error Handling
- **Files to create**:
  - `./scripts/core/logging_config.py` - Centralized logging setup
  - `./logs/.gitkeep` - Ensure logs directory exists

- **Changes**:
  - Configure Python logging (file + console)
  - Implement structured log format: `timestamp [level] module: message`
  - Create log rotation (daily, keep 30 days)

- **Rationale**: Consistent logging aids debugging; file logs preserve build history.

- **Verification**:
  ```bash
  python3 -c "from scripts.core.logging_config import setup_logging; \
  import logging; setup_logging(); logging.info('Test log')"
  ls -l logs/
  ```

#### 1.4 Document Registry & Dependency Tracking
- **Files to create**:
  - `./scripts/core/registry.py` - Document registry builder
  - `./document_registry.json` - Auto-generated list of all doc IDs

- **Changes**:
  - Scan `drafts/` directory for all Markdown files
  - Extract document_id from YAML front matter
  - Build registry: `{doc_id: {path, status, revision, ...}}`
  - Regenerate on each build

- **Rationale**: Registry enables cross-reference validation; single source of truth for all docs.

- **Verification**:
  ```bash
  python3 scripts/core/registry.py
  cat document_registry.json | jq '.["SOP-200"]'
  ```

**Phase 1 Deliverables**:
- ✅ Hierarchical configuration system
- ✅ JSON schema-based metadata validation
- ✅ Structured logging infrastructure
- ✅ Auto-generated document registry

**Verification Criteria**:
- Config loads without errors; overrides work correctly
- Invalid metadata triggers clear error messages
- Logs written to both console and file
- Registry contains all documents in drafts/

---

### Phase 2: Asset Pipeline

**Objective**: Automated image variant generation for print/web outputs.

**Dependencies**: Phase 1 (config system)

**Tasks**:

#### 2.1 Image Variant Generator
- **Files to create**:
  - `./scripts/processors/image_processor.py` - Core image processing
  - `./assets/images/master/.gitkeep` - Master images directory
  - `./assets/images/print/.gitkeep` - Print variants directory
  - `./assets/images/web/.gitkeep` - Web variants directory

- **Changes**:
  - Implement `generate_image_variants()`:
    - Input: Master image path
    - Outputs:
      - Print: 300 DPI PNG
      - Web: WebP @ 640w, 1024w, 1920w
      - Thumbnail: WebP @ 200px
  - Use Pillow with Lanczos resampling
  - Preserve aspect ratio
  - Optimize for file size (WebP quality=85)

- **Rationale**: Eliminates manual image prep; consistent quality across outputs.

- **Verification**:
  ```bash
  # Place test image in assets/images/master/doc/SOP-001/test.png
  python3 scripts/processors/image_processor.py SOP-001
  ls -lh assets/images/print/SOP-001/
  ls -lh assets/images/web/SOP-001/
  ```

#### 2.2 Image Registry & Metadata
- **Files to create**:
  - `./assets/xml/metadata/.gitkeep` - Metadata directory
  - Extend `./scripts/processors/image_processor.py` for registry generation

- **Changes**:
  - Generate JSON registry per document: `{doc_id}_images.json`
  - Schema:
    ```json
    {
      "SOP-001_valve_assembly": {
        "master": "path/to/master.png",
        "print": "path/to/print.png",
        "web": {
          "640": "path/to/640.webp",
          "1024": "path/to/1024.webp",
          "1920": "path/to/1920.webp"
        },
        "alt_text": "Extracted from Markdown",
        "caption": "Extracted from directive",
        "dimensions": {"width": 4000, "height": 3000}
      }
    }
    ```

- **Rationale**: Registry enables HTML template lookups; metadata aids accessibility.

- **Verification**:
  ```bash
  cat assets/xml/metadata/SOP-001_images.json | jq '.'
  ```

#### 2.3 Image Format Decision Logic
- **Files to create**:
  - Extend `./scripts/processors/image_processor.py` with format selector

- **Changes**:
  - Implement `select_image_format(use_case, has_transparency, is_photo)`
  - Decision tree:
    - Print → PNG (300 DPI, lossless)
    - Web → WebP (85 quality, lossy)
  - Future: AVIF support via feature flag

- **Rationale**: Optimal format selection per context; futureproof architecture.

- **Verification**:
  ```bash
  python3 -c "from scripts.processors.image_processor import select_image_format; \
  print(select_image_format('web', has_transparency=False, is_photo=True))"
  ```

#### 2.4 Batch Image Processing
- **Files to modify**:
  - `./scripts/processors/image_processor.py`

- **Changes**:
  - Add CLI interface: `python image_processor.py <doc_id>`
  - Support batch mode: `python image_processor.py --all`
  - Progress bar (tqdm) for multi-image processing

- **Rationale**: Enables one-command image prep for all documents.

- **Verification**:
  ```bash
  python3 scripts/processors/image_processor.py --all
  ```

**Phase 2 Deliverables**:
- ✅ Automated print/web image variant generation
- ✅ Image registry with metadata
- ✅ Format-aware image processing
- ✅ Batch processing CLI

**Verification Criteria**:
- Master images generate all variants correctly
- Registry JSON contains accurate paths + metadata
- WebP files 30%+ smaller than PNG equivalents
- Batch mode processes 50 images in <5 seconds (Pillow-SIMD)

---

### Phase 3: Web Output Generation

**Objective**: Generate responsive HTML from Markdown via Pandoc + Lua filters + Jinja2 templates.

**Dependencies**: Phase 1 (config, validation), Phase 2 (image assets)

**Tasks**:

#### 3.1 Pandoc Lua Filters
- **Files to create**:
  - `./filters/callouts.lua` - Convert `> [!WARNING]` → styled divs
  - `./filters/wikilinks.lua` - Convert `[[REF-2201]]` → HTML links
  - `./filters/directives.lua` - Expand `<!-- ::FIGURE -->` directives
  - `./filters/pagebreak.lua` - Handle `<!-- ::PAGEBREAK -->`

- **Changes**:
  - Implement Pandoc AST transformations
  - Callouts: Match `> [!TYPE]` → `<div class="callout callout-TYPE">`
  - Wikilinks: Parse `[[doc-id | label]]` → `<a href="/doc-id">`
  - Directives: Parse attributes (scale, align, border, shadow, caption)

- **Rationale**: Preserves all Markdown semantics lost in DocBook; enables rich formatting.

- **Verification**:
  ```bash
  echo '> [!WARNING] Test' | pandoc -f markdown -t json --lua-filter=filters/callouts.lua | \
  pandoc -f json -t html
  ```

#### 3.2 HTML Template System
- **Files to create**:
  - `./templates/html/base.html.j2` - Base layout (header, footer, nav)
  - `./templates/html/sop.html.j2` - SOP-specific layout (extends base)
  - `./templates/html/std.html.j2` - STD-specific layout
  - `./templates/html/ref.html.j2` - REF-specific layout
  - `./templates/html/app.html.j2` - APP-specific layout
  - `./templates/html/components/header.html.j2` - Reusable header
  - `./templates/html/components/footer.html.j2` - Reusable footer
  - `./templates/html/components/toc.html.j2` - Table of contents
  - `./templates/html/partials/callout.html.j2` - Callout rendering
  - `./templates/html/partials/figure.html.j2` - Figure w/ caption
  - `./scripts/renderers/template_renderer.py` - Jinja2 wrapper

- **Changes**:
  - Implement `TemplateRenderer` class
  - Register custom filters: `markdown`, `date_format`
  - Metadata grid display (doc ID, revision, status, owner, approver)
  - Responsive image rendering (`<picture>` w/ srcset)
  - TOC generation from headings

- **Rationale**: Separation of content (Markdown) from presentation (templates); reusable components.

- **Verification**:
  ```bash
  python3 -c "from scripts.renderers.template_renderer import TemplateRenderer; \
  r = TemplateRenderer(); print(r.render('sop.html.j2', {'metadata': {'title': 'Test'}}))"
  ```

#### 3.3 CSS Framework Integration
- **Files to create**:
  - `./styles/web.css` - Main web stylesheet
  - `./styles/pdf.css` - PDF-specific overrides
  - `./styles/components/callouts.css` - Callout styling
  - `./styles/components/code.css` - Code block styling (Pygments)
  - `./styles/components/tables.css` - Table styling
  - `./styles/components/figures.css` - Figure/image styling

- **Changes**:
  - Adopt Tailwind CSS utility classes (or equivalent)
  - Define CSS custom properties for theming:
    ```css
    :root {
      --color-primary: #0066cc;
      --color-warning: #ff9800;
      --color-danger: #f44336;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    ```
  - Responsive breakpoints: 640px (mobile), 1024px (tablet), 1920px (desktop)
  - Print media queries for PDF output

- **Rationale**: Consistent styling; responsive design; print optimization.

- **Verification**:
  ```bash
  # Manual: Open generated HTML in browser, resize window
  # Check: Responsive images, readable text, proper spacing
  ```

#### 3.4 Font Loading & Unicode Handling
- **Files to create**:
  - `./assets/fonts/.gitkeep` - Fonts directory
  - Copy web fonts (WOFF2) to `./assets/fonts/web/`
  - Copy PDF fonts (TTF) to `./assets/fonts/pdf/`

- **Changes**:
  - Define `@font-face` declarations in CSS
  - Implement font fallback stack
  - Normalize Unicode (NFC) in text processing:
    ```python
    import unicodedata
    text = unicodedata.normalize('NFC', text)
    ```

- **Rationale**: Consistent typography; proper emoji/special char rendering.

- **Verification**:
  ```bash
  # Manual: Check HTML displays emoji, accented characters correctly
  ```

#### 3.5 Markdown → HTML Converter
- **Files to create**:
  - `./scripts/converters/web_generator.py` - Main conversion logic

- **Changes**:
  - Implement `convert_markdown_to_html(md_path, output_path)`:
    1. Parse YAML metadata (reuse Phase 1 validator)
    2. Run Pandoc w/ Lua filters:
       ```bash
       pandoc -f markdown+yaml_metadata_block -t json \
         --lua-filter=filters/callouts.lua \
         --lua-filter=filters/wikilinks.lua \
         --lua-filter=filters/directives.lua \
         input.md
       ```
    3. Process JSON AST → Python data structures
    4. Load image registry (from Phase 2)
    5. Render Jinja2 template w/ context
    6. Write HTML to `published/web/{doc_id}.html`

- **Rationale**: Single function orchestrates full Markdown → HTML pipeline.

- **Verification**:
  ```bash
  python3 scripts/converters/web_generator.py drafts/SOP-200_Create_Workackage_Sequencing_Type.md
  firefox published/web/SOP-200.html
  ```

#### 3.6 Syntax Highlighting (Code Blocks)
- **Files to modify**:
  - `./scripts/converters/web_generator.py`
  - `./styles/components/code.css`

- **Changes**:
  - Use Pygments for code highlighting:
    ```python
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    ```
  - Generate CSS classes via Pygments
  - Support languages: Python, Bash, YAML, JSON, SQL

- **Rationale**: Professional code formatting; better readability.

- **Verification**:
  ```bash
  # Create test Markdown with ```python code block
  # Verify HTML has highlighted syntax
  ```

#### 3.7 Accessibility (ARIA, Semantic HTML)
- **Files to modify**:
  - All templates in `./templates/html/`

- **Changes**:
  - Use semantic HTML5 elements: `<nav>`, `<main>`, `<article>`, `<section>`, `<figure>`
  - Add ARIA landmarks: `role="main"`, `aria-label="Document navigation"`
  - Alt text for all images (extracted from Markdown)
  - Color contrast ratio ≥4.5:1 (normal text)
  - Skip-to-content link for keyboard navigation

- **Rationale**: WCAG 2.2 AA compliance; legal requirement (EAA 2025).

- **Verification**:
  ```bash
  # Use axe DevTools or Lighthouse accessibility audit
  # Target: 0 violations, 0 warnings
  ```

**Phase 3 Deliverables**:
- ✅ Pandoc Lua filters (callouts, wikilinks, directives)
- ✅ Jinja2 HTML templates (base + family-specific)
- ✅ Responsive CSS framework
- ✅ Font loading + Unicode normalization
- ✅ Markdown → HTML converter
- ✅ Syntax highlighting
- ✅ WCAG 2.2 AA accessibility

**Verification Criteria**:
- Markdown with callouts/wikilinks renders correctly in HTML
- HTML displays properly on mobile/tablet/desktop
- All images have alt text
- Lighthouse accessibility score ≥90
- Unicode characters (emoji, accents) render correctly

---

### Phase 4: PDF Generation (WeasyPrint)

**Objective**: Replace Scribus with WeasyPrint for 10-15x faster PDF rendering.

**Dependencies**: Phase 3 (web HTML output)

**Tasks**:

#### 4.1 WeasyPrint Integration
- **Files to create**:
  - `./scripts/renderers/pdf_generator.py` - PDF rendering logic

- **Changes**:
  - Install WeasyPrint: `pip install weasyprint`
  - Implement `generate_pdf_from_html(html_path, pdf_path, css_path)`:
    ```python
    from weasyprint import HTML, CSS
    html = HTML(filename=html_path)
    css = CSS(filename=css_path)
    html.write_pdf(pdf_path, stylesheets=[css])
    ```

- **Rationale**: WeasyPrint provides 10-15x speed vs Scribus; better typography; CSS-based layout.

- **Verification**:
  ```bash
  python3 scripts/renderers/pdf_generator.py published/web/SOP-200.html published/pdf/SOP-200.pdf
  evince published/pdf/SOP-200.pdf
  ```

#### 4.2 PDF-Specific CSS (Paged Media)
- **Files to create**:
  - `./styles/pdf.css` - CSS Paged Media styles

- **Changes**:
  - Define page size, margins:
    ```css
    @page {
      size: Letter;
      margin: 1in 0.75in;
    }
    ```
  - Add running headers/footers:
    ```css
    @page {
      @top-center {
        content: string(doc-id);
      }
      @bottom-right {
        content: "Page " counter(page);
      }
    }
    ```
  - Page breaks:
    ```css
    h1, h2 { page-break-after: avoid; }
    figure { page-break-inside: avoid; }
    ```

- **Rationale**: Professional PDF layout w/ headers, footers, page numbers.

- **Verification**:
  ```bash
  # Manual: Check PDF has headers, footers, proper page breaks
  ```

#### 4.3 Metadata Embedding (PDF)
- **Files to modify**:
  - `./scripts/renderers/pdf_generator.py`

- **Changes**:
  - Embed metadata in PDF:
    ```python
    from pypdf import PdfWriter, PdfReader
    # After WeasyPrint generates PDF
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.add_metadata({
        '/Title': metadata['title'],
        '/Author': metadata['author'],
        '/Subject': metadata['document_id'],
        '/Keywords': ', '.join(metadata.get('tags', []))
    })
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    ```

- **Rationale**: PDF metadata aids searchability, document management.

- **Verification**:
  ```bash
  pdfinfo published/pdf/SOP-200.pdf | grep Title
  ```

#### 4.4 High-Resolution Image Handling
- **Files to modify**:
  - `./scripts/converters/web_generator.py` (add PDF variant)

- **Changes**:
  - Create separate HTML for PDF w/ print images:
    - Web HTML: Uses WebP srcset (640w, 1024w, 1920w)
    - PDF HTML: Uses 300 DPI PNG (no srcset)
  - Template conditional:
    ```jinja2
    {% if output_type == 'pdf' %}
      <img src="{{ image.print }}" alt="{{ image.alt }}">
    {% else %}
      <picture>...</picture>
    {% endif %}
    ```

- **Rationale**: PDF requires high-res print images; web requires responsive variants.

- **Verification**:
  ```bash
  # Check PDF image resolution: 300 DPI
  pdfimages -list published/pdf/SOP-200.pdf
  ```

#### 4.5 Layout Engine Abstraction
- **Files to create**:
  - `./scripts/renderers/layout_engine.py` - Abstract base class

- **Changes**:
  - Define `LayoutEngine` ABC:
    ```python
    from abc import ABC, abstractmethod

    class LayoutEngine(ABC):
        @abstractmethod
        def render_pdf(self, html_path, pdf_path, css_path=None):
            pass

        @abstractmethod
        def supports_feature(self, feature):
            pass
    ```
  - Implement `WeasyPrintEngine` (primary)
  - Implement `PagedJSEngine` (optional, for JavaScript support)
  - Factory function: `create_layout_engine(engine_type)`

- **Rationale**: Enables future engine swaps (e.g., Paged.js for JS features).

- **Verification**:
  ```bash
  python3 -c "from scripts.renderers.layout_engine import create_layout_engine; \
  e = create_layout_engine('weasyprint'); print(e.supports_feature('css_paged_media'))"
  ```

#### 4.6 Scribus Migration Path
- **Files to modify**:
  - `./scripts/scribus_pipeline_adv_v3.py` (deprecate, but preserve for reference)

- **Changes**:
  - Add deprecation warning to Scribus script
  - Document migration: "Use `python build.py build <doc-id>` instead"
  - Keep script in repo for 1-2 releases (fallback)

- **Rationale**: Smooth transition; preserve legacy path during validation period.

- **Verification**:
  ```bash
  # Compare outputs: Scribus PDF vs WeasyPrint PDF
  # Visual inspection for layout parity
  ```

**Phase 4 Deliverables**:
- ✅ WeasyPrint PDF generation (2-3s per doc)
- ✅ CSS Paged Media styles (headers, footers, page breaks)
- ✅ PDF metadata embedding
- ✅ High-res image handling (300 DPI)
- ✅ Layout engine abstraction (future-proof)
- ✅ Scribus deprecation path

**Verification Criteria**:
- PDF generates in <3 seconds (vs 10-15s Scribus)
- Headers/footers render correctly
- Page breaks logical (no orphaned headings)
- Images at 300 DPI resolution
- PDF metadata correct (title, author, keywords)

---

### Phase 5: Batch Processing & Build Orchestration

**Objective**: Enable multi-document builds w/ dependency tracking, parallelization, incremental builds.

**Dependencies**: All previous phases (validation, images, web, PDF)

**Tasks**:

#### 5.1 Dependency Tracker
- **Files to create**:
  - `./scripts/core/dependency_tracker.py` - File hashing & change detection
  - `./.build_cache.json` - Build cache (gitignored)

- **Changes**:
  - Implement `DependencyTracker` class:
    - Hash files (SHA256)
    - Compare hashes to cache
    - Return `needs_rebuild(source, dependencies)` bool
    - Update cache: `mark_built(source, dependencies)`
  - Track dependencies:
    - Markdown source
    - Images (from image registry)
    - Templates
    - CSS files
    - Config files

- **Rationale**: Incremental builds 10-100x faster for unchanged docs.

- **Verification**:
  ```bash
  # Build all docs
  python3 build.py build-all
  # Modify one doc
  touch drafts/SOP-200_Create_Workackage_Sequencing_Type.md
  # Rebuild (should only rebuild SOP-200)
  python3 build.py build-all --incremental
  ```

#### 5.2 Parallel Build Executor
- **Files to create**:
  - `./scripts/core/batch_processor.py` - Multiprocessing orchestrator

- **Changes**:
  - Implement `batch_convert_documents(paths, max_workers)`:
    - Use `ProcessPoolExecutor` for CPU-bound tasks
    - Default workers: CPU count
    - Progress bar (tqdm)
    - Error isolation (one doc failure doesn't stop batch)
  - Return results: `{success: [...], failed: [(path, error), ...]}`

- **Rationale**: Parallel processing exploits multi-core CPUs; 4-8x speedup.

- **Verification**:
  ```bash
  time python3 scripts/core/batch_processor.py --all
  # Compare: Sequential vs parallel (expect 4-8x speedup on 4+ core CPU)
  ```

#### 5.3 Build Transactions & Rollback
- **Files to create**:
  - `./scripts/core/build_transaction.py` - Atomic build operations

- **Changes**:
  - Implement `BuildTransaction` class:
    - Backup files before modification
    - Track all changes (create, modify, delete)
    - Rollback on error: restore backups
    - Commit on success: delete backups
  - Use in build pipeline for safety

- **Rationale**: Atomic builds prevent partial failures corrupting outputs.

- **Verification**:
  ```bash
  # Inject error in pipeline
  # Verify outputs rolled back to previous state
  ```

#### 5.4 CLI Build Interface (Click)
- **Files to create**:
  - `./build.py` - Main build orchestrator CLI

- **Changes**:
  - Implement Click commands:
    - `build <doc-id>` - Build single document
    - `build-all [--category SOP|STD|REF|APP] [--incremental|--full]` - Batch build
    - `clean` - Remove generated files
    - `validate <doc-id>` - Validate metadata only
    - `images <doc-id>` - Process images only
  - Progress reporting (tqdm)
  - Structured logging
  - Exit codes (0=success, 1=failure)

- **Rationale**: Single entry point for all build operations; scriptable.

- **Verification**:
  ```bash
  # Test all commands
  python3 build.py build SOP-200
  python3 build.py build-all --category SOP --incremental
  python3 build.py clean
  python3 build.py validate SOP-200
  python3 build.py images SOP-200
  ```

#### 5.5 Progress Reporting & Logging
- **Files to modify**:
  - `./scripts/core/batch_processor.py`
  - `./scripts/core/logging_config.py`

- **Changes**:
  - Add progress bars (tqdm):
    ```python
    with tqdm(total=len(documents), desc="Building") as pbar:
        for doc in documents:
            pbar.set_description(f"Building {doc}")
            # ... build logic ...
            pbar.update(1)
    ```
  - Log to file: `logs/build_{timestamp}.log`
  - Console output: summary only (success/fail counts)

- **Rationale**: Clear progress feedback; detailed logs for debugging.

- **Verification**:
  ```bash
  python3 build.py build-all
  # Check: Progress bar visible
  # Check: logs/build_*.log contains detailed info
  ```

#### 5.6 Error Aggregation & Reporting
- **Files to modify**:
  - `./build.py`

- **Changes**:
  - Collect all errors during batch build
  - Display summary at end:
    ```
    Build complete: 45 succeeded, 3 failed

    Failed builds:
      • SOP-001: Metadata validation failed (missing 'approver')
      • STD-2201: Image not found (valve.png)
      • REF-2202: Cross-reference invalid (REF-9999)
    ```
  - Write full error details to log file

- **Rationale**: Batch errors easy to diagnose; actionable error messages.

- **Verification**:
  ```bash
  # Introduce errors in 2-3 docs
  python3 build.py build-all
  # Verify: Summary lists all failures w/ clear messages
  ```

**Phase 5 Deliverables**:
- ✅ Dependency tracker w/ content hashing
- ✅ Parallel build executor (multiprocessing)
- ✅ Build transactions w/ rollback
- ✅ CLI interface (Click)
- ✅ Progress reporting (tqdm)
- ✅ Error aggregation & summary

**Verification Criteria**:
- Incremental builds skip unchanged docs (verify via logs)
- Parallel builds utilize all CPU cores (check `htop` during build)
- Failed builds rollback cleanly (no corrupt outputs)
- CLI commands work correctly (exit codes, help text)
- Progress bars update in real-time
- Error summaries clear and actionable

---

### Phase 6: Integration, Polish & Documentation

**Objective**: End-to-end testing, migration guide, documentation, final polish.

**Dependencies**: All previous phases

**Tasks**:

#### 6.1 End-to-End Pipeline Integration
- **Files to modify**:
  - `./build.py` - Integrate all components

- **Changes**:
  - Full pipeline for `build <doc-id>`:
    1. Validate metadata (Phase 1)
    2. Process images (Phase 2)
    3. Generate HTML (Phase 3)
    4. Generate PDF (Phase 4)
    5. Package release if status=Active (existing logic)
  - Error handling at each stage
  - Transaction-based (rollback on any failure)

- **Rationale**: Single command executes full workflow; robust error handling.

- **Verification**:
  ```bash
  python3 build.py build SOP-200
  # Check: HTML + PDF generated
  # Check: Release package created (if Active)
  ```

#### 6.2 Release Packager Integration
- **Files to modify**:
  - `./scripts/release_packager.py` (extend for web outputs)

- **Changes**:
  - Include HTML in release archives:
    ```
    releases/SOP/SOP-200_r1_20251201.zip
    ├── source/
    │   └── SOP-200.md
    ├── outputs/
    │   ├── SOP-200.pdf
    │   ├── SOP-200.html
    │   └── assets/ (images, CSS)
    ├── metadata/
    │   ├── SOP-200_metadata.json
    │   └── SOP-200_images.json
    ```
  - Timestamp format: `{doc_id}_r{revision}_{YYYYMMDD}.zip`

- **Rationale**: Complete release package includes all outputs + source.

- **Verification**:
  ```bash
  # Set doc status to Active
  python3 build.py build SOP-200
  unzip -l releases/SOP/SOP-200_r1_*.zip
  ```

#### 6.3 Testing Suite
- **Files to create**:
  - `./tests/test_metadata_validator.py` - Unit tests for validation
  - `./tests/test_image_processor.py` - Unit tests for images
  - `./tests/test_web_generator.py` - Unit tests for HTML
  - `./tests/test_pdf_generator.py` - Unit tests for PDF
  - `./tests/test_batch_processor.py` - Integration tests for batch builds
  - `./tests/fixtures/` - Sample Markdown, images, expected outputs
  - `./pytest.ini` - Pytest configuration

- **Changes**:
  - Unit tests for each module
  - Integration tests for full pipeline
  - Fixtures: sample docs w/ known-good outputs
  - Test coverage target: 70%+

- **Rationale**: Automated tests prevent regressions; confidence in refactors.

- **Verification**:
  ```bash
  pytest tests/ -v
  pytest tests/ --cov=scripts --cov-report=html
  ```

#### 6.4 Migration Guide
- **Files to create**:
  - `./docs/MIGRATION.md` - Step-by-step migration from Scribus

- **Changes**:
  - Document migration process:
    1. Backup existing Scribus outputs
    2. Install new dependencies (`pip install -r requirements.txt`)
    3. Configure `config/local.yaml` (paths, settings)
    4. Process images: `python build.py images --all`
    5. Test build one doc: `python build.py build SOP-001`
    6. Compare outputs: Scribus PDF vs WeasyPrint PDF
    7. Full migration: `python build.py build-all --full`
  - Troubleshooting common issues
  - Rollback procedure (if needed)

- **Rationale**: Smooth migration path; clear instructions reduce adoption friction.

- **Verification**:
  ```bash
  # Manual: Follow guide step-by-step with fresh environment
  ```

#### 6.5 User Documentation
- **Files to create**:
  - `./docs/USER_GUIDE.md` - End-user documentation
  - `./docs/ARCHITECTURE.md` - System architecture overview
  - `./docs/CONFIG.md` - Configuration reference
  - `./docs/TEMPLATES.md` - Template customization guide
  - `./docs/TROUBLESHOOTING.md` - Common issues & solutions

- **Changes**:
  - User guide:
    - Creating new documents
    - Metadata reference
    - Image directives
    - Building documents
    - Customizing templates
  - Architecture doc:
    - Component diagram
    - Data flow
    - Extension points
  - Config reference:
    - All config keys documented
    - Examples for each setting
  - Template guide:
    - Jinja2 syntax
    - Available variables
    - Custom filters
    - Creating new templates

- **Rationale**: Self-service documentation reduces support burden.

- **Verification**:
  ```bash
  # Manual: Review docs for clarity, accuracy, completeness
  ```

#### 6.6 README Update
- **Files to modify**:
  - `./README.md` - Update for new pipeline

- **Changes**:
  - Update workflow diagram (Markdown → Web/PDF)
  - Quick start guide
  - Link to detailed docs
  - Technology stack section
  - Contributing guidelines

- **Rationale**: README is first touchpoint; must reflect new system.

- **Verification**:
  ```bash
  # Manual: Review README with fresh eyes
  ```

#### 6.7 Configuration Examples
- **Files to create**:
  - `./config/examples/custom_fonts.yaml` - Custom font config
  - `./config/examples/high_quality_images.yaml` - Image quality settings
  - `./config/examples/fast_builds.yaml` - Speed-optimized config

- **Changes**:
  - Commented examples for common customizations
  - Use cases documented inline

- **Rationale**: Examples accelerate config customization.

- **Verification**:
  ```bash
  # Test each example config
  python3 build.py build SOP-001 --config config/examples/high_quality_images.yaml
  ```

#### 6.8 Performance Benchmarks
- **Files to create**:
  - `./benchmarks/benchmark.py` - Timing script

- **Changes**:
  - Benchmark:
    - Single doc build time
    - Batch build time (10, 50, 100 docs)
    - Image processing time
    - PDF generation time
  - Compare: Old (Scribus) vs New (WeasyPrint)
  - Document results in README

- **Rationale**: Quantify performance improvements; validate claims.

- **Verification**:
  ```bash
  python3 benchmarks/benchmark.py
  # Expected: 10-15x speedup for PDF generation
  ```

**Phase 6 Deliverables**:
- ✅ Fully integrated end-to-end pipeline
- ✅ Release packager w/ web outputs
- ✅ Test suite (unit + integration)
- ✅ Migration guide (Scribus → new system)
- ✅ User documentation (guide, architecture, config, templates, troubleshooting)
- ✅ Updated README
- ✅ Configuration examples
- ✅ Performance benchmarks

**Verification Criteria**:
- Full pipeline executes without errors
- Test suite passes (70%+ coverage)
- Migration guide successfully guides new user
- Documentation complete and accurate
- Performance benchmarks show 10-15x speedup

---

## 3. File Modification Plan

### 3.1 New Files

**Configuration & Core**:
- `./config/default.yaml` - System defaults
- `./config/profiles/sop.yaml` - SOP profile
- `./config/profiles/std.yaml` - STD profile
- `./config/profiles/ref.yaml` - REF profile
- `./config/profiles/app.yaml` - APP profile
- `./config/examples/custom_fonts.yaml` - Font config example
- `./config/examples/high_quality_images.yaml` - Image quality example
- `./config/examples/fast_builds.yaml` - Speed-optimized example
- `./scripts/core/config.py` - Config loader
- `./scripts/core/logging_config.py` - Logging setup
- `./scripts/core/registry.py` - Document registry builder
- `./scripts/core/dependency_tracker.py` - Build cache & hashing
- `./scripts/core/batch_processor.py` - Parallel build executor
- `./scripts/core/build_transaction.py` - Atomic builds w/ rollback
- `./document_registry.json` - Auto-generated doc ID registry
- `./.build_cache.json` - Build cache (gitignored)

**Validation**:
- `./schemas/sop_metadata.json` - SOP JSON Schema
- `./schemas/std_metadata.json` - STD JSON Schema
- `./schemas/ref_metadata.json` - REF JSON Schema
- `./schemas/app_metadata.json` - APP JSON Schema
- `./scripts/validators/metadata_validator.py` - Validation logic

**Image Processing**:
- `./scripts/processors/image_processor.py` - Image variant generation
- `./assets/images/master/.gitkeep` - Master images directory
- `./assets/images/print/.gitkeep` - Print variants directory
- `./assets/images/web/.gitkeep` - Web variants directory
- `./assets/xml/metadata/.gitkeep` - Image metadata directory

**Pandoc Filters**:
- `./filters/callouts.lua` - Callout transformation
- `./filters/wikilinks.lua` - Wikilink resolution
- `./filters/directives.lua` - Directive expansion
- `./filters/pagebreak.lua` - Page break handling

**Templates**:
- `./templates/html/base.html.j2` - Base HTML layout
- `./templates/html/sop.html.j2` - SOP layout
- `./templates/html/std.html.j2` - STD layout
- `./templates/html/ref.html.j2` - REF layout
- `./templates/html/app.html.j2` - APP layout
- `./templates/html/components/header.html.j2` - Header component
- `./templates/html/components/footer.html.j2` - Footer component
- `./templates/html/components/toc.html.j2` - TOC component
- `./templates/html/partials/callout.html.j2` - Callout partial
- `./templates/html/partials/figure.html.j2` - Figure partial
- `./scripts/renderers/template_renderer.py` - Jinja2 wrapper

**Converters & Renderers**:
- `./scripts/converters/web_generator.py` - Markdown → HTML
- `./scripts/renderers/pdf_generator.py` - HTML → PDF (WeasyPrint)
- `./scripts/renderers/layout_engine.py` - Layout engine abstraction

**Styles**:
- `./styles/web.css` - Main web stylesheet
- `./styles/pdf.css` - PDF-specific styles
- `./styles/components/callouts.css` - Callout styling
- `./styles/components/code.css` - Code block styling
- `./styles/components/tables.css` - Table styling
- `./styles/components/figures.css` - Figure styling

**Build System**:
- `./build.py` - Main build CLI (Click)

**Testing**:
- `./tests/test_metadata_validator.py` - Validation tests
- `./tests/test_image_processor.py` - Image tests
- `./tests/test_web_generator.py` - HTML tests
- `./tests/test_pdf_generator.py` - PDF tests
- `./tests/test_batch_processor.py` - Batch tests
- `./tests/fixtures/.gitkeep` - Test fixtures directory
- `./pytest.ini` - Pytest config

**Documentation**:
- `./docs/MIGRATION.md` - Migration guide
- `./docs/USER_GUIDE.md` - User documentation
- `./docs/ARCHITECTURE.md` - Architecture overview
- `./docs/CONFIG.md` - Config reference
- `./docs/TEMPLATES.md` - Template guide
- `./docs/TROUBLESHOOTING.md` - Troubleshooting guide

**Benchmarks**:
- `./benchmarks/benchmark.py` - Performance benchmarks

**Dependencies**:
- `./requirements.txt` - Python dependencies (new/updated)

### 3.2 Modified Files

**Existing Scripts**:
- `./scripts/release_packager.py` - Extend for web outputs, HTML inclusion

**README**:
- `./README.md` - Update workflow, quick start, tech stack

**Git Ignore**:
- `./.gitignore` - Add `.build_cache.json`, `config/local.yaml`, `logs/`

### 3.3 Deprecated Files

**Scribus Scripts** (preserve for reference, add deprecation notices):
- `./scripts/scribus_pipeline_simple.py` - Add deprecation warning
- `./scripts/scribus_pipeline_adv_v3.py` - Add deprecation warning
- `./scripts/layout_map.yaml` - Keep for reference (Scribus layouts)

---

## 4. Backwards Compatibility Strategy

### 4.1 Feature Flags

**Approach**: Config-driven feature toggles for gradual rollout.

**Implementation**:

```yaml
# config/default.yaml
features:
  use_weasyprint: true      # Toggle PDF engine (weasyprint vs scribus)
  use_new_validator: true   # Toggle metadata validation
  generate_web_output: true # Toggle HTML generation
  enable_batch_mode: true   # Toggle parallel builds
```

**Rationale**: Enable/disable new features independently; rollback if issues arise.

### 4.2 Dual-Path Support

**Approach**: Support both old (Scribus) and new (WeasyPrint) PDF paths during migration.

**Implementation**:

```python
# build.py
def generate_pdf(markdown_path, engine='weasyprint'):
    if engine == 'scribus':
        # Legacy path (existing script)
        return run_scribus_pipeline(markdown_path)
    else:
        # New path
        html_path = convert_markdown_to_html(markdown_path)
        return generate_pdf_from_html(html_path)
```

**Rationale**: Gradual migration; compare outputs side-by-side.

### 4.3 Graceful Degradation

**Missing Dependencies**: If WeasyPrint not installed, fall back to Scribus.

**Implementation**:

```python
try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False
    logging.warning("WeasyPrint not found, using Scribus fallback")

def generate_pdf(markdown_path):
    if HAS_WEASYPRINT and config.get('features.use_weasyprint'):
        return generate_pdf_weasyprint(markdown_path)
    else:
        return generate_pdf_scribus(markdown_path)
```

**Rationale**: System remains functional even if new dependencies missing.

### 4.4 Migration Path for Existing Documents

**Approach**: Existing documents work without modification.

**YAML Compatibility**: New schemas validate existing metadata (all new fields optional).

**Image Paths**: Support both old and new paths:

```python
# Check multiple image locations
image_paths = [
    f'assets/images/print/{doc_id}/{image_name}',  # New path
    f'assets/images/global/{image_name}',          # Old path
    f'assets/images/doc/{doc_id}/{image_name}'     # Old path
]

for path in image_paths:
    if Path(path).exists():
        return path
```

**Rationale**: No manual file moves required; works immediately.

### 4.5 Testing Strategy for Existing Documents

**Approach**: Validate all existing docs still build correctly.

**Implementation**:

```bash
# Test script
for doc in drafts/*.md; do
    echo "Testing $doc"
    python build.py build $(basename $doc .md)
    # Compare output to existing baseline
done
```

**Acceptance Criteria**:
- All existing docs build without errors
- Visual comparison: new PDFs match old PDFs (layout, content)

---

## 5. Testing & Verification Plan

### 5.1 Unit Tests

**Scope**: Individual modules in isolation.

**Coverage Target**: 70%+

**Test Files**:

```python
# tests/test_metadata_validator.py
def test_valid_metadata():
    result, errors = validate_metadata('tests/fixtures/valid_sop.md', 'schemas/sop_metadata.json')
    assert result is True
    assert len(errors) == 0

def test_invalid_metadata_missing_field():
    result, errors = validate_metadata('tests/fixtures/missing_title.md', 'schemas/sop_metadata.json')
    assert result is False
    assert any('title' in err for err in errors)

def test_cross_reference_validation():
    # ... test cross-ref logic ...
```

```python
# tests/test_image_processor.py
def test_generate_variants():
    master = 'tests/fixtures/images/test_image.png'
    variants = generate_image_variants(master, '/tmp', 'TEST-001')

    assert Path(variants['print']).exists()
    assert Path(variants['web']['640']).exists()

    # Check dimensions
    img = Image.open(variants['web']['640'])
    assert img.width == 640

def test_image_format_selection():
    fmt, quality, opts = select_image_format('web', has_transparency=False, is_photo=True)
    assert fmt == 'WEBP'
    assert quality == 85
```

**Run Tests**:

```bash
pytest tests/ -v --cov=scripts --cov-report=html
```

### 5.2 Integration Tests

**Scope**: Full pipeline workflows.

**Test Files**:

```python
# tests/test_batch_processor.py
def test_full_pipeline_single_doc():
    # Create temp document
    test_doc = create_test_document('TEST-001')

    # Run pipeline
    result = build_document(test_doc)

    # Verify outputs
    assert Path('published/web/TEST-001.html').exists()
    assert Path('published/pdf/TEST-001.pdf').exists()

    # Verify content
    html = Path('published/web/TEST-001.html').read_text()
    assert '<h1>Test Document</h1>' in html

def test_batch_build_incremental():
    # Build all docs
    results = batch_build(incremental=False)

    # Modify one doc
    touch('drafts/TEST-001.md')

    # Rebuild incrementally
    results = batch_build(incremental=True)

    # Verify only TEST-001 rebuilt
    assert len(results['built']) == 1
    assert 'TEST-001' in results['built'][0]
```

**Run Tests**:

```bash
pytest tests/test_batch_processor.py -v
```

### 5.3 End-to-End Tests

**Scope**: Complete workflows with real documents.

**Test Cases**:

1. **New Document Creation**:
   - Create SOP from boilerplate
   - Add metadata, content, images
   - Run `python build.py build SOP-999`
   - Verify HTML + PDF outputs

2. **Document Update**:
   - Modify existing SOP (increment revision)
   - Run incremental build
   - Verify only modified doc rebuilt
   - Verify release package created (if Active)

3. **Batch Build**:
   - Build all SOPs: `python build.py build-all --category SOP`
   - Verify all outputs generated
   - Check build time (should be <5min for 50 docs)

4. **Error Handling**:
   - Introduce metadata error
   - Run build
   - Verify clear error message
   - Verify rollback (no corrupt outputs)

**Run Tests**:

```bash
# Manual execution
pytest tests/test_e2e.py -v --slow
```

### 5.4 Performance Benchmarks

**Metrics**:

| Metric | Baseline (Scribus) | Target (WeasyPrint) |
|--------|-------------------|---------------------|
| Single doc build | 10-15s | 2-3s |
| Batch build (50 docs) | 500-750s | 100-150s |
| Image processing (10 images) | 30s (manual) | 3s (automated) |
| Incremental build (1 change) | 500s (full rebuild) | 2s (changed doc only) |

**Benchmark Script**:

```python
# benchmarks/benchmark.py
import time
from pathlib import Path

def benchmark_single_build():
    start = time.time()
    build_document('SOP-200')
    elapsed = time.time() - start
    print(f"Single build: {elapsed:.2f}s")

def benchmark_batch_build(doc_count=50):
    docs = list(Path('drafts').glob('*.md'))[:doc_count]

    start = time.time()
    batch_build(docs)
    elapsed = time.time() - start

    print(f"Batch build ({doc_count} docs): {elapsed:.2f}s")
    print(f"Average per doc: {elapsed/doc_count:.2f}s")

if __name__ == '__main__':
    benchmark_single_build()
    benchmark_batch_build(50)
```

**Run Benchmarks**:

```bash
python3 benchmarks/benchmark.py
```

### 5.5 Visual Regression Tests

**Scope**: PDF layout quality vs Scribus baseline.

**Approach**:

1. Generate PDFs with Scribus (baseline)
2. Generate PDFs with WeasyPrint (new)
3. Convert both to images (via `pdftoppm`)
4. Compare images (via `compare` from ImageMagick)

**Script**:

```bash
# tests/visual_regression.sh
#!/bin/bash

DOC_ID=$1

# Generate baseline
python scripts/scribus_pipeline_adv_v3.py $DOC_ID
mv published/pdf/${DOC_ID}.pdf published/pdf/${DOC_ID}_scribus.pdf

# Generate new
python build.py build $DOC_ID
mv published/pdf/${DOC_ID}.pdf published/pdf/${DOC_ID}_weasyprint.pdf

# Convert to images
pdftoppm published/pdf/${DOC_ID}_scribus.pdf /tmp/${DOC_ID}_scribus -png
pdftoppm published/pdf/${DOC_ID}_weasyprint.pdf /tmp/${DOC_ID}_weasyprint -png

# Compare
compare -metric RMSE /tmp/${DOC_ID}_scribus-1.png /tmp/${DOC_ID}_weasyprint-1.png /tmp/diff.png
```

**Acceptance**: RMSE < 10% (allow for font rendering differences)

---

## 6. Open Questions for Implementation

### 6.1 Deferred Decisions

**1. AVIF Image Support**:
- **Question**: Add AVIF support in addition to WebP?
- **Options**:
  - A) WebP only (97% browser support, faster decoding)
  - B) WebP + AVIF fallback (20-25% smaller files, 94% support)
- **Recommendation**: Defer to Phase 7 (future enhancement); WebP sufficient for now

**2. Paged.js for JavaScript Support**:
- **Question**: Implement Paged.js engine alongside WeasyPrint?
- **Use Case**: Interactive PDFs (forms, dynamic content)
- **Recommendation**: Defer unless specific need identified; WeasyPrint covers 95% of use cases

**3. Document Versioning System**:
- **Question**: Track full document history (git-like) or simple revision numbers?
- **Options**:
  - A) Simple revision numbers (existing approach)
  - B) Full version control (diffs, branches, merges)
- **Recommendation**: Keep simple revision numbers; use git for version control

**4. Multi-Language Support**:
- **Question**: Plan for internationalization (i18n)?
- **Current**: English only
- **Future**: Spanish, French translations?
- **Recommendation**: Design templates with i18n in mind (use translation keys), but defer implementation

### 6.2 Technical Clarifications Needed

**1. Image Storage Strategy**:
- **Question**: Store master images in repo or external storage?
- **Concern**: Large binary files bloat git repo
- **Options**:
  - A) Commit masters to repo (simple, self-contained)
  - B) Use Git LFS for large images
  - C) External storage (S3, NAS) with references
- **Recommendation**: Git LFS if repo size becomes issue (>500MB)

**2. PDF Security Settings**:
- **Question**: Enable PDF security (password protection, printing restrictions)?
- **Use Case**: Confidential SOPs
- **Recommendation**: Add as optional config flag (disabled by default)

**3. Watermarking for Draft/Review**:
- **Question**: Add "DRAFT" or "REVIEW" watermark to non-Active documents?
- **Implementation**: CSS `::after` pseudo-element or WeasyPrint overlay
- **Recommendation**: Implement via CSS for simplicity

**4. Change Tracking Between Revisions**:
- **Question**: Generate diff reports between revisions?
- **Use Case**: Highlight what changed in revision 2 vs revision 1
- **Recommendation**: Defer; use `git diff` for source tracking

### 6.3 Performance Optimization Decisions

**1. Pillow vs Pillow-SIMD**:
- **Question**: Use standard Pillow or install Pillow-SIMD?
- **Benefit**: Pillow-SIMD 40x faster with AVX2
- **Complexity**: Requires compilation (not pip-installable)
- **Recommendation**: Start with standard Pillow; document Pillow-SIMD upgrade path

**2. Parallel Worker Count**:
- **Question**: Default to CPU count or CPU count / 2?
- **Concern**: High CPU usage may impact other processes
- **Recommendation**: Default to CPU count; make configurable (`config.pipeline.batch.max_workers`)

**3. Cache Invalidation Strategy**:
- **Question**: When to invalidate build cache?
- **Options**:
  - A) Manual (`python build.py clean`)
  - B) Automatic (detect config/template changes)
  - C) Time-based (invalidate after 7 days)
- **Recommendation**: Automatic + manual; invalidate if config/template/schema modified

### 6.4 User Experience Decisions

**1. Error Message Verbosity**:
- **Question**: Verbose errors (full stack traces) or concise errors (summary only)?
- **Recommendation**: Concise by default; verbose with `--debug` flag

**2. Default Build Mode**:
- **Question**: Incremental or full builds by default?
- **Recommendation**: Incremental (faster); full with `--full` flag

**3. Template Selection**:
- **Question**: Auto-select template by document category or manual override?
- **Recommendation**: Auto-select (SOP → sop.html.j2); override via YAML: `template: custom.html.j2`

---

## 7. Success Criteria

### 7.1 Functional Requirements

**Must Have**:

1. ✅ **Metadata Validation**:
   - All document families (SOP, STD, REF, APP) validate against JSON schemas
   - Clear error messages for invalid metadata
   - Cross-reference validation (upstream/downstream APNs)

2. ✅ **Web Output**:
   - Generate responsive HTML from Markdown
   - Preserve all Markdown features (callouts, wikilinks, code blocks, tables)
   - WCAG 2.2 AA accessibility compliance

3. ✅ **PDF Output**:
   - Generate PDF from HTML via WeasyPrint
   - CSS Paged Media support (headers, footers, page numbers, page breaks)
   - 300 DPI images
   - Embedded metadata (title, author, keywords)

4. ✅ **Image Pipeline**:
   - Auto-generate print variants (300 DPI PNG)
   - Auto-generate web variants (WebP @ 640w, 1024w, 1920w)
   - Image registry with metadata

5. ✅ **Batch Processing**:
   - Build all documents: `python build.py build-all`
   - Incremental builds (skip unchanged docs)
   - Parallel execution (utilize all CPU cores)
   - Atomic transactions (rollback on error)

6. ✅ **Release Packaging**:
   - Timestamped archives for Active documents
   - Include source Markdown, HTML, PDF, images, metadata

### 7.2 Performance Requirements

**Targets**:

1. ✅ **Single Document Build**: <3 seconds (vs 10-15s Scribus)
2. ✅ **Batch Build (50 docs)**: <150 seconds (vs 500-750s Scribus)
3. ✅ **Image Processing (10 images)**: <3 seconds (vs 30s manual)
4. ✅ **Incremental Build (1 changed doc)**: <3 seconds (vs 500s full rebuild)

**Measurement**:

```bash
# Benchmark script
python3 benchmarks/benchmark.py

# Expected output:
Single build: 2.5s
Batch build (50 docs): 125s
Average per doc: 2.5s
Image processing (10 images): 2.1s
```

### 7.3 Quality Requirements

**Standards**:

1. ✅ **Code Quality**:
   - Pylint score: 8.0+
   - Type hints: 80%+ coverage
   - Docstrings: All public functions

2. ✅ **Test Coverage**:
   - Unit tests: 70%+
   - Integration tests: All critical paths
   - E2E tests: 5+ scenarios

3. ✅ **Accessibility**:
   - Lighthouse accessibility score: 90+
   - WCAG 2.2 AA: 0 violations (via axe DevTools)
   - Alt text: 100% of images

4. ✅ **Documentation**:
   - User guide: Complete
   - Migration guide: Step-by-step instructions
   - Architecture doc: Up-to-date diagrams
   - Inline code comments: All complex logic

### 7.4 Usability Requirements

**Ease of Use**:

1. ✅ **Single Command Build**: `python build.py build <doc-id>`
2. ✅ **Clear Error Messages**: Actionable feedback (e.g., "Missing 'approver' in metadata")
3. ✅ **Progress Feedback**: Progress bars for batch operations
4. ✅ **Self-Service Docs**: Users can create/modify documents without support

**Validation**:

- **User Testing**: 2-3 users successfully create new SOP without assistance
- **Error Recovery**: Users understand and fix validation errors on first attempt

---

## 8. Risk Mitigation

### 8.1 Technical Risks

**Risk 1: WeasyPrint Layout Differs from Scribus**

- **Likelihood**: Medium
- **Impact**: High (visual parity critical)
- **Mitigation**:
  - Visual regression tests (compare PDF renders)
  - Pilot migration (1 document family first)
  - Keep Scribus fallback for 2-3 releases
  - Accept minor font rendering differences (not layout differences)

**Risk 2: Image Processing Too Slow**

- **Likelihood**: Low (Pillow-SIMD benchmarked)
- **Impact**: Medium (user frustration)
- **Mitigation**:
  - Benchmark early (Phase 2)
  - Use Pillow-SIMD if needed (40x speedup)
  - Parallelize image processing across documents

**Risk 3: Lua Filters Too Complex**

- **Likelihood**: Low (Pandoc Lua API mature)
- **Impact**: Medium (feature loss)
- **Mitigation**:
  - Start with simple filters (callouts, wikilinks)
  - Extensive testing with edge cases
  - Fallback: Python post-processing if Lua insufficient

**Risk 4: Batch Builds Consume Too Much Memory**

- **Likelihood**: Low (Python multiprocessing isolates processes)
- **Impact**: Medium (system instability)
- **Mitigation**:
  - Limit max workers (configurable)
  - Monitor memory usage during tests
  - Implement memory profiling (via `memory_profiler`)

### 8.2 Process Risks

**Risk 1: Migration Takes Longer Than Expected**

- **Likelihood**: Medium (complex system)
- **Impact**: High (blocks adoption)
- **Mitigation**:
  - Phased rollout (validate, images, web, PDF separately)
  - Maintain Scribus fallback
  - Allocate buffer time (3-4 months vs 2 months)

**Risk 2: User Resistance to New Workflow**

- **Likelihood**: Low (automation reduces manual work)
- **Impact**: Medium (adoption delay)
- **Mitigation**:
  - Clear migration guide
  - Side-by-side comparison (old vs new outputs)
  - Training sessions / demos
  - Gradual rollout (pilot with 1 team)

**Risk 3: Breaking Changes in Dependencies**

- **Likelihood**: Low (mature libraries)
- **Impact**: High (pipeline breaks)
- **Mitigation**:
  - Pin dependency versions (`requirements.txt`)
  - Test on each dependency update
  - CI/CD pipeline (automated testing)

### 8.3 Data Risks

**Risk 1: Corrupt Outputs from Failed Builds**

- **Likelihood**: Low (atomic transactions implemented)
- **Impact**: High (data loss)
- **Mitigation**:
  - Build transactions with rollback
  - Backup before builds (optional config)
  - Version control (git) for all sources

**Risk 2: Image Variants Out of Sync with Masters**

- **Likelihood**: Medium (manual master updates)
- **Impact**: Medium (incorrect images in outputs)
- **Mitigation**:
  - Dependency tracking (rebuild if master changes)
  - Image registry checksums
  - Validation: warn if master newer than variants

---

## 9. Post-Implementation Roadmap

### Future Enhancements (Phase 7+)

**1. Advanced Features**:

- **AVIF Image Support**: 20-25% smaller than WebP
- **Paged.js Engine**: JavaScript support for interactive PDFs
- **Change Tracking**: Visual diff between revisions
- **Multi-Language Support**: i18n infrastructure

**2. Workflow Improvements**:

- **Live Preview**: Hot-reload HTML preview during authoring
- **Collaborative Editing**: Real-time multi-user Markdown editing (e.g., CRDTs)
- **Approval Workflow**: Built-in review/approval tracking (vs manual status updates)

**3. Integration Hooks**:

- **AMOS Integration**: Auto-import metadata from AMOS (Swiss-AS)
- **SharePoint Publishing**: Auto-upload outputs to SharePoint
- **Email Notifications**: Notify stakeholders on document updates

**4. Analytics & Reporting**:

- **Document Usage Metrics**: Track views, downloads
- **Build History Dashboard**: Visualize build times, failures
- **Compliance Reporting**: Generate audit logs (who changed what, when)

### Maintenance Plan

**Regular Tasks**:

1. **Dependency Updates** (monthly):
   - Run `pip list --outdated`
   - Test updates in dev environment
   - Update `requirements.txt`

2. **Schema Evolution** (as needed):
   - Add new metadata fields
   - Update JSON schemas
   - Maintain backwards compatibility

3. **Template Refinements** (quarterly):
   - Update CSS for design improvements
   - Add new components (e.g., data tables, flowcharts)

4. **Performance Tuning** (biannual):
   - Profile build times
   - Optimize bottlenecks
   - Update benchmarks

**Long-Term Support**:

- **LTS Branch**: Maintain stable branch for production (bug fixes only)
- **Feature Branch**: Active development for new features
- **Release Cycle**: Quarterly releases (minor versions), annual major versions

---

## 10. Appendix

### 10.1 Technology Reference

**Core Dependencies**:

```txt
# requirements.txt
pandoc>=3.6
PyYAML>=6.0
jsonschema>=4.0
Pillow>=10.0
weasyprint>=60.0
Jinja2>=3.1
click>=8.1
tqdm>=4.66
Pygments>=2.17
pypdf>=3.0
```

**Optional Dependencies**:

```txt
# requirements-dev.txt
pytest>=7.4
pytest-cov>=4.1
pylint>=3.0
black>=23.0
isort>=5.12
memory-profiler>=0.61
```

### 10.2 Glossary

**Terms**:

- **AST**: Abstract Syntax Tree (Pandoc's intermediate representation)
- **DocBook**: XML format (deprecated in new pipeline)
- **JSON Schema**: Validation standard for JSON/YAML data
- **Lua Filter**: Pandoc plugin for AST transformations
- **Paged Media**: CSS module for print layout (page sizes, headers, footers)
- **WCAG**: Web Content Accessibility Guidelines
- **WeasyPrint**: Python library for HTML → PDF rendering
- **WOFF2**: Web font format (compressed, variable font support)

### 10.3 Directory Structure (Final State)

```
SSP_Document_Publish_Pipeline/
├── assets/
│   ├── fonts/
│   │   ├── web/          # WOFF2 fonts
│   │   └── pdf/          # TTF fonts
│   ├── images/
│   │   ├── master/       # Original high-res images
│   │   ├── print/        # 300 DPI PNG variants
│   │   └── web/          # WebP variants (640w, 1024w, 1920w)
│   └── xml/
│       └── metadata/     # Image registries (JSON)
├── benchmarks/
│   └── benchmark.py      # Performance tests
├── config/
│   ├── default.yaml      # System defaults
│   ├── profiles/
│   │   ├── sop.yaml
│   │   ├── std.yaml
│   │   ├── ref.yaml
│   │   └── app.yaml
│   └── examples/         # Config examples
├── docs/
│   ├── MIGRATION.md
│   ├── USER_GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── CONFIG.md
│   ├── TEMPLATES.md
│   └── TROUBLESHOOTING.md
├── drafts/               # Source Markdown files
├── filters/              # Pandoc Lua filters
│   ├── callouts.lua
│   ├── wikilinks.lua
│   ├── directives.lua
│   └── pagebreak.lua
├── logs/                 # Build logs (gitignored)
├── plans/                # Implementation plans (this doc)
├── prompts/              # Planning prompts
├── published/
│   ├── pdf/              # Generated PDFs
│   └── web/              # Generated HTML
├── releases/             # Release archives (timestamped zips)
├── research/             # Research documents
├── schemas/              # JSON schemas for validation
│   ├── sop_metadata.json
│   ├── std_metadata.json
│   ├── ref_metadata.json
│   └── app_metadata.json
├── scripts/
│   ├── core/
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── registry.py
│   │   ├── dependency_tracker.py
│   │   ├── batch_processor.py
│   │   └── build_transaction.py
│   ├── validators/
│   │   └── metadata_validator.py
│   ├── processors/
│   │   └── image_processor.py
│   ├── converters/
│   │   └── web_generator.py
│   ├── renderers/
│   │   ├── template_renderer.py
│   │   ├── pdf_generator.py
│   │   └── layout_engine.py
│   ├── release_packager.py  # (updated)
│   └── [deprecated scribus scripts]
├── styles/
│   ├── web.css
│   ├── pdf.css
│   └── components/
│       ├── callouts.css
│       ├── code.css
│       ├── tables.css
│       └── figures.css
├── templates/
│   ├── html/
│   │   ├── base.html.j2
│   │   ├── sop.html.j2
│   │   ├── std.html.j2
│   │   ├── ref.html.j2
│   │   ├── app.html.j2
│   │   ├── components/
│   │   └── partials/
│   └── [existing Scribus templates]
├── tests/
│   ├── fixtures/         # Test data
│   ├── test_metadata_validator.py
│   ├── test_image_processor.py
│   ├── test_web_generator.py
│   ├── test_pdf_generator.py
│   └── test_batch_processor.py
├── build.py              # Main build CLI
├── requirements.txt      # Python dependencies
├── requirements-dev.txt  # Dev dependencies
├── pytest.ini            # Pytest config
├── .build_cache.json     # Build cache (gitignored)
└── document_registry.json # Auto-generated doc registry
```

---

**END OF IMPLEMENTATION PLAN**

*This plan is ready for execution by Claude Code (implementation stage).*

**Next Steps**:

1. Review plan for completeness
2. Confirm approach with user
3. Execute phase-by-phase via `/taches-cc-resources:run-plan` command
4. Report progress after each phase
5. Adapt as needed based on implementation discoveries
