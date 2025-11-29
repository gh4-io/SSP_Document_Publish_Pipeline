---
source:
  - "[[Document_Family_Standards]]"
  - "[[Scribus_Python_Pipeline]]"
  - "[[SOP_Templates_and_Standards]]"
title: Document Publish Pipeline
revision: 2
tags:
  - AMOS
  - Publishing_Pipeline
---


# Document Publish Pipeline – Scribus-Centered Implementation (Rev 2)

This document describes an **enterprise-grade SOP document factory** based on:

- **Markdown** as the single source of truth
- **Pandoc → DocBook XML** as the normalization step
- **Scribus (.sla)** as the layout engine
- **Scribus Python** scripts as the automation layer
- **PDF + HTML** as the controlled output formats

The pipeline is intended to support **SOP / STD / REF / APP** families with a shared standard:

- Unified front-matter (YAML in Markdown)
- Common revision model
- Consistent header/footer, logos, and layout rules
- Release packaging and long-term traceability

This revision also introduces a dedicated `/assets` tree for **centralized storage of all non-Markdown payloads** (images, XML, fonts, web assets, metadata), ensuring version consistency, traceability, and automation readiness.


---

## 1. Folder Layout and Assets Directory

```text
/Document_Publish_Pipeline/
├─ _boilerplate/              # Starter Markdown & YAML templates
├─ templates/                 # Scribus .sla and DocBook style templates
├─ drafts/                    # Markdown sources only (author working area)
├─ assets/                    # Central hub for all generated and external assets
│   ├─ images/
│   │   ├─ global/            # Logos, icons, standard symbols
│   │   ├─ doc/               # Document-specific images (SOP-###)
│   │   ├─ project/           # APN or aircraft-specific media
│   │   ├─ temp/              # WIP, cleanup-safe
│   │   ├─ master/            # Full-resolution originals (not embedded)
│   │   ├─ print/             # 300 DPI for PDF output
│   │   └─ web/               # Optimized for web rendering
│   ├─ xml/
│   │   ├─ docbook/           # Generated XML from Markdown
│   │   └─ metadata/          # Image registries, job configs, metadata JSON
│   ├─ diagrams/              # Draw.io, SVG, or CAD-based sources
│   ├─ web/                   # CSS, JS, and web-specific image overrides
│   ├─ fonts/                 # Fonts used by Scribus and web exports
│   └─ misc/                  # QR codes, barcodes, or attached files
├─ published/                 # Active exports (current live outputs)
│   ├─ pdf/
│   └─ web/
├─ releases/                  # Immutable, timestamped versioned packages
│   ├─ SOP/
│   ├─ STD/
│   ├─ REF/
│   └─ APP/
├─ styles/                    # Global style references, DocBook XSL, CSS
└─ scripts/                   # Automation scripts (Pandoc, Scribus, packagers)
```

Key principles:

- Treat `drafts/` as the **working area** for authors.
- `published/` holds **current live outputs** for PDF and web.
- `releases/` is **write-once, read-many**: each release is a timestamped zip of inputs + outputs.
- `/assets` is the **single hub** for everything the pipeline generates or needs besides Markdown.


---

## 2. Pipeline – Simple vs Advanced

### Simple Version (MVP)

1. **Author** in Markdown using a common boilerplate (see `_boilerplate/SOP_boilerplate.md`).
2. Run **Pandoc** to convert Markdown → DocBook XML (written under `assets/xml/docbook/`).
3. Open your **Scribus SOP template** (`templates/sop_template.sla`) manually.
4. Run **`scripts/scribus_pipeline_simple.py`** inside Scribus:
   - Asks for DocBook XML path.
   - Extracts metadata (SOP ID, title, revision, effective date).
   - Fills header/footer frames.
   - Flows body into the main frame.
   - Applies basic paragraph styles.
   - Exports a PDF, optionally HTML.
5. Manually copy outputs into `published/pdf` and `published/web` as needed.

### Advanced / Enterprise Version

1. **Author** in Markdown:
   - Standardized YAML front matter.
   - SOP / STD / REF / APP families share a core structure.
2. A **driver script** (outside Scribus) does:
   - Validate YAML metadata (revision increment, effective date, owner).
   - Run Pandoc Markdown → DocBook XML.
   - Generate a job JSON (where inputs/outputs go, what template to use).
3. Inside Scribus, run **`scripts/scribus_pipeline_advanced.py`**:
   - Reads the job JSON (paths, category, target revision).
   - Opens the correct `.sla` template (SOP vs STD vs REF vs APP).
   - Verifies that all required frames exist (header, footer, body, sidebar, etc.).
   - Parses DocBook:
     - Maps tags to Scribus styles.
     - Handles sections, tables, lists, callouts, admonitions.
     - Flows content across multiple pages and linked frames.
   - Adds header/footer with SOP ID, revision, and effective date.
   - Optionally builds a **Table of Contents**.
   - Inserts logo(s) and other branding elements.
   - Exports:
     - PDF to `published/pdf`
     - HTML (via Scribus exporter or alternative route) to `published/web`.
4. A separate **release packager** (`scripts/release_packager.py`) can then:
   - Create a timestamped zip under `releases/<family>/` with:
     - Original Markdown source
     - DocBook XML
     - Job JSON / metadata
     - Final PDF + HTML
     - Logs

---


---

## 3. Asset Automation Rules

All automation scripts shall:

- Auto-create required `/assets` subfolders per document or project.
- Overwrite existing DocBook or metadata JSON when rerun.
- Never modify `/releases/` contents.
- Copy all referenced image and attachment files into `/assets` during processing.

Each document has a unique identifier (e.g., `SOP-001`), used to name XML, image directories, and metadata files.

Example:
```text
assets/xml/docbook/SOP-001.docbook.xml
assets/images/doc/SOP-001/
assets/xml/metadata/SOP-001_images.json
```

---

## 4. Image Management and Referencing

### 4.1 Image Syntax in Markdown
Use standard Markdown image syntax:
```markdown
![Hydraulic Valve Assembly](../../assets/images/doc/SOP-001/SOP-001_02_valve.png)
```

To specify display attributes for Scribus and web:
```markdown
::: figure scale=0.7 border=true align=center shadow=false
![Hydraulic Valve Assembly](../../assets/images/doc/SOP-001/SOP-001_02_valve.png)
**Figure 2 — Hydraulic Valve Assembly**
:::
```

### 4.2 Automated Conversion to DocBook
Pandoc transforms Markdown figures into:
```xml
<mediaobject>
  <imageobject>
    <imagedata fileref="../../assets/images/doc/SOP-001/SOP-001_02_valve.png" width="70%"/>
  </imageobject>
  <caption>Hydraulic Valve Assembly</caption>
</mediaobject>
```
The pipeline’s XML interpreter extracts figure directives to drive Scribus layout properties.

### 4.3 Scribus Layout Integration

Each image reference becomes a Scribus frame dynamically inserted based on context:
- `ImgBody` — inline image in body flow
- `ImgSidebar` — floating right-aligned image
- `ImgFullWidth` — across entire content width
- `ImgCover` — for cover pages only
  
#### Behavior:
- Auto-scales image based on specified `scale` or layout width.
- Centers or aligns per metadata.
- Adds optional border/shadow.
- Uses `fitImageToFrame()` or native proportional scaling.

If the image is missing, the system inserts a placeholder frame (red border, text: *Missing image reference*).

---

## 5. Image Resolution and Format Rules

| Output Type | Target Resolution | Scaling | Preferred Format | Notes |
|--------------|-------------------|----------|------------------|--------|
| **PDF** | 300 DPI | Full width (auto scaled) | PNG / TIFF | For print; master images downscaled |
| **Web (HTML)** | 96–150 DPI | 60–70% of full scale | WebP / PNG | Optimized for fast load, lazy-loaded |

High-resolution “master” images are stored under `assets/images/master/`. Derived formats (`print`, `web`) are automatically created during publication.

---

## 6. Extended Asset Types

### 6.1 Diagrams
Store editable sources (`.drawio`, `.svg`, `.pdf`) under `assets/diagrams/`. The exported raster or vector copies used in documents should reference the `/images` directory.

### 6.2 Fonts
Fonts used in Scribus templates or web styling are version-locked under `assets/fonts/`. Each release includes checksums to prevent inconsistency.

### 6.3 Web Theme Assets
All CSS, JS, and web-optimized logos and icons reside under `/assets/web/`. These are used by the HTML publication scripts.

### 6.4 QR Codes, Attachments, and Miscellaneous Files
Documents can include references to auxiliary materials under `assets/misc/`. These are included in release zips if referenced in Markdown or metadata.

---

## 7. Automation and Metadata

Each document in the pipeline generates:
- `SOP-###.docbook.xml` — converted from Markdown.
- `SOP-###_job.json` — defines processing parameters (template, revision, language), e.g. `assets/xml/metadata/SOP-001_job.json`.
- `SOP-###_images.json` — auto-generated registry of all images, captions, and attributes, e.g. `assets/xml/metadata/SOP-001_images.json`.

This registry ensures:
- Image checksum validation.
- Traceability of usage.
- Packaging integrity when exporting releases.

---


---

## 8. Publication Workflows

### 8.1 PDF Publication (via Scribus)
1. Load `.sla` template from `/templates/`.
2. Python script reads XML + metadata from `/assets/xml/`.
3. Populates text frames and inserts images.
4. Applies paragraph and image styles automatically.
5. Exports to `/published/pdf/`.

### 8.2 Web Publication (via Pandoc / CSS)
1. Uses the same Markdown source.
2. Converts via Pandoc → HTML using `/assets/web/css/sop_theme.css`.
3. Loads web-optimized images from `/assets/images/web/`.
4. Generates table of contents, collapsible sections, and search index.
5. Output saved to `/published/web/`.

---


---

## 9. Release Packaging
When final approval is reached and document status is `Active`, automation zips together:
- Markdown source.
- DocBook XML.
- Images (print + web variants).
- Fonts, diagrams, and references.
- Generated PDF + HTML.
- `job.json` and `images.json` metadata.

All zips stored under `/releases/{SOP|STD|REF|APP}/` for audit traceability.

---

## 10. Security and Compliance
- Strip EXIF metadata from all images.
- Watermark internal documents where required.
- Block inclusion of unapproved external images.
- Maintain copyright attribution for any licensed media.

---


---

## 5. 🧩 Special Formatting Controls for Scribus Output

  

The Scribus publishing pipeline supports a few **Markdown markers** that control

page behavior during PDF generation. These have no effect on web or text output

— they are honored only by the **DocBook → Scribus** stage.

  

### 5.1. Force a Page Break

Insert this marker wherever you want a new page to begin **in the Scribus PDF**:
  
```
<!-- ::PAGEBREAK -->
```

When the Scribus automation script encounters this token, it will:

1. Finish writing the current frame.

2. Create and link a new continuation page using the `MP_CONT` master.

3. Resume inserting text on the new page.
 

These markers are ignored by all other converters (Pandoc → HTML, etc.).


---

  

### 5.2. Keep a Section Together

  

Wrap a section of content in a fenced block labeled `keep-together`

to discourage page breaks within that section.

  
```
<!-- ::KEEP-TOGETHER -->
### Important Safety Notes

The following steps should stay on the same page when possible:

1. Disconnect power before servicing.
2. Verify all tools are clear before engine start.
3. Confirm that maintenance tags are visible.
<!-- ::: -->
```

  

During the DocBook → Scribus stage, the parser treats this entire block as a

single “atomic” unit. If it doesn’t fully fit on the current page, it moves the

whole section to the next page before placement.

  

---

  

### 5.3. Combining Both

  

You can mix these directives for complex layouts:

  
```
<!-- ::PAGEBREAK -->
<!-- ::KEEP-TOGETHER -->
#### Inspection Checklist
| Item | Description              |
|------|--------------------------|
| 1    | Visual surface check     |
| 2    | Verify fastener torque   |
| 3    | Record serial number     |
<!-- ::: -->
```

  

This example:
- Forces a new page.
- Keeps the checklist table together.

  

---

  

### 5.4. Summary

  

| Marker                     | Purpose                    | Applies To          |
|----------------------------|----------------------------|---------------------|
| `<!-- ::PAGEBREAK -->` | Start a new page            | Scribus output only |
| `<!-- ::KEEP-TOGETHER -->`  | Keep section on one page   | Scribus output only |

These directives are optional but recommended for maintaining professional

layout control across variable-length SOP documents.

---


---

## 3. Scribus vs Word – Short Comparison

See `pipeline_scribus_vs_alternatives.md` for more detail. In short:

- **Scribus** shines where you want **repeatable, scripted layout** and are willing to invest in a custom pipeline.
- **Word** excels for **ad-hoc, human-edited docs** but is weak for long-term, code-driven consistency at scale.
- For a document factory, Scribus + DocBook + Pandoc is more maintainable, versionable, and automatable.

---


---

## 4. How to Use These Notes in Obsidian

- Treat this vault as **design documentation + snippets**.
- Start with:
  - `scribus/Scribus_Template_Guide.md`
  - `scribus/Scribus_Python_Pipeline_Simple.md`
  - `scribus/Scribus_Python_Pipeline_Advanced.md`
- As you implement the pipeline on your machine, add:
  - Local paths
  - Actual template filenames
  - Real script locations

---


---

## 6. Next Steps

1. Build and save your **SOP template** in Scribus (.sla).
2. Wire up `scribus_pipeline_simple.py` and test one SOP end-to-end.
3. Gradually adopt the advanced script and multi-page flows.
4. Extend to STD, REF, APP families with their own templates and style sets.

---

## 12. Assets, Images, and Media (Overview)

This pipeline treats **Markdown as the single source of truth for text**, and `/assets` as the single home for **all non-Markdown payloads**:

- **DocBook XML** from Pandoc lives in `assets/xml/docbook/`.
- **Job metadata and image registries** live in `assets/xml/metadata/`.
- **Images and diagrams** are organized by document ID and project in `assets/images/` and `assets/diagrams/`.
- **Web theming and scripts** live under `assets/web/`.
- **Fonts and other shared brand assets** live under `assets/fonts/`.
- **QR codes, barcodes, and attachments** live under `assets/misc/`.

For image-heavy SOPs:

- Authors reference images from Markdown using relative paths into `assets/images/...`.
- The DocBook + metadata layer maps those references into **Scribus image frames** for PDF and into appropriate `<img>` tags for HTML.
- A separate standards document defines **good practices for image resolution, captions, and figure usage** for both PDF and web outputs.

The result is a pipeline that can support **dozens or hundreds of documents** while keeping layout, branding, and assets consistently managed and auditable.

---

## 13. Figure and Caption Handling Standards

The document pipeline uses **hidden comment directives** to define image formatting and captions in Markdown while keeping the source clean and preview-friendly.

### 13.1. Standard FIGURE Syntax

Example:

```markdown
<!-- ::FIGURE scale=0.7 align=center border shadow caption="Hydraulic Valve Assembly" -->
![Hydraulic Valve Assembly](../../assets/images/doc/SOP-001/SOP-001_02_valve.png)
**Figure 2 — Hydraulic Valve Assembly**
```

- The `<!-- ::FIGURE ... -->` comment holds all layout and style attributes.
- The following image reference defines the media path.
- The bold caption is **optional** and may be used for human readability.

### 13.2. Caption Handling (Hybrid Model)

| Source | Priority | Description |
|--------|-----------|-------------|
| `caption="..."` in FIGURE comment | 1 | Used as authoritative caption text |
| Bold text below image (e.g., `**Figure 2 — ...**`) | 2 | Used if no caption attribute provided |
| Image alt text (from `![Alt text]`) | 3 | Fallback if no caption or bold text found |
| None found | 4 | Caption left blank, log warning |

This ensures captions appear consistently in both **PDF and web outputs** without cluttering the Markdown preview.

### 13.3. Example Output

Converted to DocBook:

```xml
<mediaobject role="figure">
  <imageobject>
    <imagedata fileref="assets/images/doc/SOP-001/SOP-001_02_valve.png" width="70%" align="center"/>
  </imageobject>
  <caption>Hydraulic Valve Assembly</caption>
</mediaobject>
```

Or to Scribus (via Python script):

```markdown
::: figure scale=0.7 align=center border=true shadow=true
![Hydraulic Valve Assembly](../../assets/images/doc/SOP-001/SOP-001_02_valve.png)
**Figure — Hydraulic Valve Assembly**
:::
```

### 13.4. Caption Logic Flow

1. Detect `<!-- ::FIGURE ... -->` comment.  
2. Parse attributes (scale, align, caption, etc.).  
3. Locate the next image reference and optional caption line.  
4. Prioritize caption sources as listed above.  
5. Write results into metadata JSON for traceability.

Example metadata entry:

```json
{
  "id": "SOP-001_02_valve",
  "caption": "Hydraulic Valve Assembly",
  "source": "../../assets/images/doc/SOP-001/SOP-001_02_valve.png",
  "scale": 0.7,
  "align": "center",
  "border": true,
  "shadow": true
}
```

This **hybrid caption approach** combines Markdown readability with full automation control.
