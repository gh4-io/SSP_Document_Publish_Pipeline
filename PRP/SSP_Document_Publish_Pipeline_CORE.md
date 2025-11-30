---
project: SSP_Document_Publish_Pipeline
version: unified-core-2025.11
author: Jason Grace
status: Active
---

# SSP Document Publishing Pipeline – Unified Core Specification

## 1. Executive Summary

This pipeline modernizes SOP/STD/REF/APP publishing by replacing DocBook + Scribus rendering with a Markdown-native system using **Pandoc JSON AST → HTML + CSS → WeasyPrint**.  
Scribus remains a **visual layout designer only** for master pages and CSS extraction.

### Benefits
- ✅ 100% Markdown fidelity (callouts, wikilinks, images, code, tables)
- ✅ VSCode-quality PDF output (GitHub Markdown + layout CSS)
- ✅ 5× faster rendering, human-readable JSON AST
- ✅ Easier maintenance + debugging
- ✅ Future-proof (pure web stack)

---

## 2. Core Architecture

```plaintext
Markdown (YAML front matter)
    ↓
Pandoc → JSON AST
    ↓
Python parser → block model
    ↓
HTML + CSS (GitHub + layout CSS)
    ↓
WeasyPrint → PDF
```

Scribus workflow (one-time design phase):
1. Create master pages, frames, styles.
2. Export `.sla`.
3. Run `scripts/extract_scribus_layout.py` → generates matching CSS layout.

---

## 3. Folder Layout

```plaintext
/SSP_Document_Publish_Pipeline/
├─ _boilerplate/      # Starter Markdown templates
├─ drafts/            # Author working area
├─ templates/
│  ├─ layouts/        # Scribus masters + extracted CSS
│  └─ profiles/       # layout_profile_*.json
├─ assets/
│  ├─ images/         # logos, doc-specific, print/web
│  ├─ fonts/
│  ├─ web/
│  └─ xml/metadata/
├─ styles/            # Global CSS themes
├─ published/
│  ├─ pdf/
│  └─ web/
├─ releases/          # Timestamped immutable bundles
│  ├─ SOP/ STD/ REF/ APP/
└─ scripts/
   └─ ssp_pipeline/   # Python modules (below)
```

Key rules:
- `drafts/` = truth  
- `published/` = current live  
- `releases/` = write-once snapshots  

---

## 4. Module Overview (v4 Implementation)

| Module | Purpose |
|--------|----------|
| **config.py** | Load layout profile JSON; select rendering engine. |
| **metadata.py** | Parse + normalize YAML front matter. |
| **parsers/pandoc_ast.py** | Parse Pandoc JSON → block list (heading, paragraph, list, table, code, callout, wikilink, image). |
| **renderers/html_generator.py** | Generate HTML body + metadata frames using CSS classes. |
| **renderers/weasyprint_renderer.py** | Render HTML → PDF with WeasyPrint; apply layout CSS + metadata. |
| **layouts/scribus_extractor.py** | Extract frame geometry → CSS template. |
| **utils/** | logging / file_ops / validators. |
| **pipeline.py** | Orchestrate full workflow (Markdown→PDF). |

---

## 5. Layout Profile Schema (Example)

```json
{
  "layout_profile": {
    "rendering_engine": "weasyprint",
    "resources": {
      "scribus_template": "templates/layouts/DTS_Master_Report_Template.sla",
      "css_template": "templates/layouts/dts_master_report.css",
      "markdown_theme": "styles/github-markdown.css",
      "pdf_directory": "published/pdf",
      "web_directory": "published/web"
    },
    "styles_map": {
      "pandoc": {
        "heading": {"1": "Heading1", "2": "Heading2"},
        "paragraph": "BodyText",
        "callout": {
          "WARNING": "callout-warning",
          "DANGER": "callout-danger",
          "NOTE": "callout-note",
          "TIP": "callout-tip"
        },
        "code": "CodeBlock",
        "table": "table-standard"
      }
    }
  }
}
```

---

## 6. Supported Markdown Features

- Obsidian callouts (`> [!WARNING]`) → styled boxes  
- Wikilinks (`[[REF-2201 | Workpackage Config]]`) → internal hyperlinks  
- Images (`![[Screenshot.png]]`) auto-resolved from `assets/images/...`  
- Tables / lists / code blocks rendered with GitHub Markdown theme  

### 6.1 Authoring Recommendations
- **Editor:** Obsidian (Live Preview mode recommended).
- **Compatibility:** The pipeline natively supports Obsidian-flavored syntax (Callouts, Wikilinks, Image embedding).
- **Validation:** Authors should use the "Watch Mode" (see Section 10) to verify layout compliance, as the editor view is for content structure only, not final print layout.

---

## 7. Scribus Guidelines (Design Only)

- Define consistent frame naming (`TitleMain`, `BodyMain`, etc.)  
- Use guides + relative positioning for CSS predictability  
- Keep master pages minimal (frames + styles only)  
- Commit `.sla` to Git; tag layout revisions  
- Document layout decisions inside Scribus  

---

## 8. Migration & Compatibility

- Old DocBook + Scribus pipeline remains fallback (`rendering_engine: "scribus"`)  
- All new docs use WeasyPrint  
- Maintain shared metadata, release, and logging standards  

---

## 9. Development Standards (From CLAUDE.md)

- KISS / YAGNI / Single Responsibility  
- ≤ 500 lines per file; ≤ 50 lines per function  
- Use `uv` for env + deps; never edit `pyproject.toml` directly  
- Commands:

```bash
uv venv && uv sync
uv run ruff check .
uv run pytest
```

- Prefer `rg` over `grep`  
- Tests live beside modules  

---

## 10. Minimal Usage Flow

```bash
# Generate JSON AST
pandoc drafts/SOP-200.md -t json -o assets/xml/metadata/SOP-200.json

# Run pipeline
uv run python scripts/ssp_pipeline/pipeline.py drafts/SOP-200.md

# Interactive Authoring (Watch Mode)
# Monitors drafts/ for changes and auto-rebuilds HTML/PDF
uv run python scripts/ssp_pipeline/watch.py drafts/SOP-200.md
```

Result:  
`published/pdf/SOP-200.pdf` and `published/web/SOP-200.html`

---

## 11. Governance Rules for Agents

- Never edit `.sla` XML directly  
- Respect folder layout and metadata  
- Keep Markdown as sole source of truth  
- Log each run to `/logs/`  
- Prefer WeasyPrint; Scribus = fallback  

---

## 12. Future Expansion

- Add HTML export with search index  
- Optional REST API for document queueing  
- Integrate metadata validation via schema  
- Multi-tenant pipeline profiles (CVG / DTS / AMOS)
