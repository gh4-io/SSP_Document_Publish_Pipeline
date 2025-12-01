# SSP Project Status & Roadmap (Updated 2025-11-30)

## 📍 Current Focus

**Phase:** 8 — Layout Helpers (Scribus + CSS) ✅ COMPLETE
**Completed:** Scribus .sla parser + CSS generator for WeasyPrint layouts.
**Next Up:** Phase 9 (Final Documentation + Integration Testing).

---

## 📅 Roadmap

### 🗺️ Roadmap Legend

[x]  Completed — The task or phase is fully finished and validated.  
[~]  In Progress — Currently being worked on or under review.  
[ ]  Planned — Not yet started; pending dependency or future milestone.  
🧪  Milestone Test — A checkpoint where functionality or process should be tested before proceeding.  
⚙️  Automation Step — A scripted or repeatable pipeline operation.  
🗃️  Deliverable — A key file, document, or artifact expected as an output of the phase.

* [x] **Phase 0: Initialization**

  * [x] Define PRP and Core Specs
  * [x] Set up repo structure and `uv` environment
  * [x] Add CLAUDE project configuration and documentation (`SSP_PRP_CORE.md`, `SSP_Document_Publish_Pipeline_CORE.md`)
  * [x] 🧪 **Milestone Test:** Confirm PRP and CLAUDE policy ingestion successful

* [x] **Phase 1: Environment & Bootstrap**

  * [x] Initialize `pyproject.toml` and dependency environment
  * [x] Add and verify `ruff`, `pytest`, `weasyprint`
  * [x] Validate project folder structure and imports
  * [x] 🧪 **Milestone Test:** Verify environment readiness with `uv run ruff --version` and `pytest -q`

* [x] **Phase 2: Stub and Structure Setup**

  * [x] Create Python modules under `scripts/ssp_pipeline/`
  * [x] Add function/class shells with type hints and TODOs
  * [x] Verify all stubs pass linting
  * [x] 🧪 **Milestone Test:** Confirm module import order and base structure with no syntax errors

* [x] **Phase 3: Documentation & Comment Pass**

  * [x] Add module-level docstrings
  * [x] Add inline comments and detailed TODOs
  * [x] Ensure code readability and documentation parity
  * [x] 🧪 **Milestone Test:** Review readability — ensure all modules self-explanatory with no logic yet

* [x] **Phase 4: Utils Layer Implementation**

  * [x] Implement logging system (daily rotation, structured output)
  * [x] Implement file operations (directory creation, archiving, asset resolution)
  * [x] Implement validators (frontmatter, CSS, layout profile checks)
  * [x] 🧪 **Milestone Test:** Run test scripts verifying log creation, directory management, and validation errors ✅
  * [x] 🗃️ **Deliverable:** `documentation/milestones/P04_Utilities_Core.md`

* [x] **Phase 5: Parsers (Pandoc AST)**

  * [x] Implement `pandoc_ast.py` (JSON → Internal Block Model conversion)
  * [x] Implement `callouts.py` (Obsidian callout documentation)
  * [x] Implement `tables.py` (Pandoc table structure mapping)
  * [x] Implement `wikilinks.py` (internal reference resolution)
  * [x] Implement `images.py` (image path resolution)
  * [x] 🧪 **Milestone Test:** Validate JSON → Block Model translation with test Pandoc AST sample ✅
  * [x] 🗃️ **Deliverable:** `documentation/milestones/P05_Parsers_PandocAST.md`

* [x] **Phase 6: Renderers (HTML + PDF)**

  * [x] Build HTML Generator (`html_generator.py`)
  * [x] Implement WeasyPrint Renderer (`weasyprint_renderer.py`)
  * [ ] Integrate CSS builder for layout styling (deferred to Phase 8)
  * [x] 🧪 **Milestone Test:** Render sample Block Model → HTML → PDF ✅
  * [x] 🗃️ **Deliverable:** `documentation/milestones/P06_Renderers_HTML_PDF.md`

* [x] **Phase 7: Core Integration (Pipeline)**

  * [x] Implement `config.py` layout loader (157 lines)
  * [x] Implement `metadata.py` schema handling (184 lines)
  * [x] Implement `pipeline.py` orchestrator (231 lines)
  * [x] Implement `watch.py` (File monitor for live HTML preview/WYSIWYG-ish behavior) (185 lines)
  * [x] 🧪 **Milestone Test:** Execute Markdown → PDF end-to-end using command line ✅
  * [x] 🗃️ **Deliverable:** `documentation/milestones/P07_Core_Pipeline.md`

* [x] **Phase 8: Layout Helpers**

  * [x] Implement `scribus_extractor.py` (geometry extraction) (271 lines)
  * [x] Implement `css_builder.py` (profile-to-style conversion) (265 lines)
  * [x] 🧪 **Milestone Test:** Extract frames from .sla + generate CSS ✅
  * [x] 🗃️ **Deliverable:** `documentation/milestones/P08_Layouts_ScribusCSS.md`

* [ ] **Phase 9: Documentation & Testing**

  * [ ] Generate `SSP_Technical_Design.md` (Architecture + Flow)
  * [ ] Create `Authoring_Guide.md` (Obsidian setup & Live Preview instructions) <-- ADD THIS
  * [ ] Update PRP and build notes with latest process updates
  * [ ] Add CLI usage examples and automation notes
  * [ ] 🧪 **Milestone Test:** Run full publishing cycle from Markdown draft → archived PDF release

---

## 🧠 Decision Log ("Windy Road" Tracker)

* **2025-11-29:** Adopted WeasyPrint as rendering engine.
* **2025-11-30:** Combined PRP and CLAUDE contexts for unified automation.
* **2025-11-30:** Separated layout logic into individual helpers for modularity.
* **2025-11-30:** Enforced <500-line guideline for maintainability.
* **2025-11-30:** [Documentation] Added retroactive milestone documentation for Phase 4 (Utils). Reason: Maintain verification standards for all phases.
* **2025-11-30:** [Parsers] Implemented Pandoc JSON AST parser with specialized handlers for callouts, images, wikilinks, tables. Reason: Core requirement for Markdown → PDF pipeline. Error strategy: log warnings for unsupported types, continue parsing (never crash).
* **2025-11-30:** [Wikilink Resolution] Changed from "defer to render time" to "resolve during parsing". Reason: Fail-early detection of broken references improves debugging.
* **2025-11-30:** [Renderers] Implemented HTML generator (361 lines) and WeasyPrint renderer (175 lines). Reason: Complete Phase 6 (Block Model → HTML → PDF). Error-tolerant rendering logs warnings but continues on non-fatal errors.
* **2025-11-30:** [HTML Generation] Used inline CSS class mapping instead of post-processing. Reason: Simpler architecture, classes applied during block rendering.
* **2025-11-30:** [WeasyPrint Integration] Metadata embedded via HTML meta tags, not post-processed. Reason: WeasyPrint handles metadata during rendering natively.
* **2025-11-30:** [Phase 7 Core Pipeline] Implemented complete end-to-end orchestration (757 LOC across 4 modules). Added watchdog dependency for live authoring. Reason: Enable full Markdown → PDF workflow with real-time rebuild capability.
* **2025-11-30:** [Configuration] Default rendering_engine to "weasyprint" if not specified in profile. Reason: WeasyPrint is new standard; Scribus is legacy fallback only.
* **2025-11-30:** [Metadata Parsing] Built simple stdlib-only YAML parser (no PyYAML). Reason: Frontmatter structure is simple key:value pairs; avoids external dependency.
* **2025-11-30:** [Watch Mode] Implemented 2-second debounce for file changes. Reason: Editors trigger multiple save events; prevents rapid wasteful rebuilds.
* **2025-11-30:** [Pandoc Integration] 60-second timeout for subprocess calls. Reason: Prevent hung processes on malformed/large documents.
* **2025-11-30:** [Phase 8 Layout Helpers] Implemented Scribus .sla parser (271 LOC) + CSS generator (265 LOC). stdlib-only XML parsing. Reason: Provide tooling for converting Scribus designs → WeasyPrint CSS layouts without external dependencies.
* **2025-11-30:** [XML Parsing] Used stdlib xml.etree.ElementTree instead of lxml. Reason: Read-only .sla parsing doesn't require lxml features; avoid external dependency.
* **2025-11-30:** [Unit Conversion] Convert Scribus points to inches in extractor, not CSS builder. Reason: Consistent unit system (inches) across pipeline; CSS builder agnostic to input units.
* **2025-11-30:** [CSS Positioning] Generate CSS with absolute positioning for frames. Reason: WeasyPrint handles absolute positioning well for PDF; matches Scribus frame paradigm.
* **2025-11-30:** [Layout Helper Integration] Phase 8 modules NOT integrated into pipeline.py yet. Reason: Standalone utilities for authors/designers; future enhancement for automatic CSS generation.

---

## 🚧 Known Constraints

* Must adhere to PRP/CLAUDE version parity.
* Only `weasyprint` allowed as external dependency.
* `uv` required for dependency management.
* Scribus reference only; WeasyPrint handles actual rendering.

---

## ⚡ Active Context

**Latest Summary:** Phase 8 (Layout Helpers) complete ✅. Scribus .sla parser + CSS generator implemented. Standalone utilities for converting Scribus designs → WeasyPrint CSS.

**Critical Technical State:**
- Layout Helpers: scribus_extractor.py (271), css_builder.py (265)
- Total Phase 8: 536 lines across 2 modules
- All ruff checks passing ✅
- Stdlib-only dependencies (xml.etree.ElementTree)
- Frame extraction from .sla PAGEOBJECT elements
- CSS generation with absolute positioning + @page rules
- Unit conversion (points → inches/mm/cm/px)

**Carry-Over Notes:**
- Use Project Mode for all multi-file operations
- Maintain <500 lines per file (current max: 361 from Phase 6)
- Phase 9 next: Final documentation, integration testing, CLI tools
- Layout helpers NOT yet integrated into pipeline.py (future enhancement)
- Known limitation: Scribus rendering engine not yet implemented (stub only)

---

### Summary

