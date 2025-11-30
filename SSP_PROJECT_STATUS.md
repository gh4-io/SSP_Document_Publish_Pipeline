# SSP Project Status & Roadmap (Updated 2025-11-30)

## 📍 Current Focus

**Phase:** 5 — Parser Implementation and Core Integration
**Active Tasks:** Finalize `pandoc_ast.py` and begin initial testing with `pipeline.py`.
**Next Up:** Begin renderer phase (HTML + WeasyPrint) following AST validation.

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
  * [ ] 🧪 **Milestone Test:** Run test scripts verifying log creation, directory management, and validation errors

* [ ] **Phase 5: Parsers (Pandoc AST)**

  * [ ] Implement `pandoc_ast.py` (JSON → Internal Block Model conversion)
  * [ ] Implement `callouts.py` (admonition parsing)
  * [ ] Implement `tables.py` (Pandoc table structure mapping)
  * [ ] Implement `wikilinks.py` (internal reference resolution)
  * [ ] 🧪 **Milestone Test:** Validate JSON → Block Model translation with test Pandoc AST sample

* [ ] **Phase 6: Renderers (HTML + PDF)**

  * [ ] Build HTML Generator (`html_generator.py`)
  * [ ] Implement WeasyPrint Renderer (`weasyprint_renderer.py`)
  * [ ] Integrate CSS builder for layout styling
  * [ ] 🧪 **Milestone Test:** Render sample Markdown → HTML → PDF and validate visual fidelity

* [ ] **Phase 7: Core Integration (Pipeline)**

  * [ ] Finalize `config.py` layout loader and `metadata.py` schema handling
  * [ ] Connect utils, parsers, and renderers via `pipeline.py`
  * [ ] Add CLI entry point for full automation
  * [ ] 🧪 **Milestone Test:** Execute Markdown → PDF end-to-end using command line

* [ ] **Phase 8: Layout Helpers**

  * [ ] Implement `scribus_extractor.py` (geometry extraction)
  * [ ] Implement `css_builder.py` (profile-to-style conversion)
  * [ ] 🧪 **Milestone Test:** Compare extracted Scribus layout with WeasyPrint output alignment

* [ ] **Phase 9: Documentation & Testing**

  * [ ] Generate `SSP_Technical_Design.md` (Architecture + Flow)
  * [ ] Update PRP and build notes with latest process updates
  * [ ] Add CLI usage examples and automation notes
  * [ ] 🧪 **Milestone Test:** Run full publishing cycle from Markdown draft → archived PDF release

---

## 🧠 Decision Log ("Windy Road" Tracker)

* **2025-11-29:** Adopted WeasyPrint as rendering engine.
* **2025-11-30:** Combined PRP and CLAUDE contexts for unified automation.
* **2025-11-30:** Separated layout logic into individual helpers for modularity.
* **2025-11-30:** Enforced <500-line guideline for maintainability.

---

## 🚧 Known Constraints

* Must adhere to PRP/CLAUDE version parity.
* Only `weasyprint` allowed as external dependency.
* `uv` required for dependency management.
* Scribus reference only; WeasyPrint handles actual rendering.

---

### Summary

