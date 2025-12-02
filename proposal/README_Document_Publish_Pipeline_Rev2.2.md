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
- ✅ **Preserve all Markdown features** (callouts, admonitions, wikilinks, images, tables, code blocks)
- ✅ Obsidian-quality PDF output (Visual parity with Obsidian's "Live Preview" styling) (GitHub Markdown + layout CSS)
- **Pandoc → DocBook XML** as the normalization step
- **Scribus (.sla)** as the layout engine
- **PDF + HTML** as the controlled output formats
- ✅ Easier maintenance + debugging
- ✅ Future-proof (pure web stack)

The pipeline is intended to support **SOP / STD / REF / APP** families with a shared standard:

- Unified front-matter (YAML in Markdown)
- Common revision model
- Consistent header/footer, logos, and layout rules
- Release packaging and long-term traceability

This revision also introduces a dedicated `/assets` tree for **centralized storage of all non-Markdown payloads** (images, XML, fonts, web assets, metadata), ensuring version consistency, traceability, and automation readiness.


---

## Core Architecture

```plaintext
Markdown (YAML front matter)
    ↓
Pandoc → JSON AST
    ↓
Python parser → block model
    ↓
HTML + CSS 
    ↓
WeasyPrint → PDF

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ DESIGN PHASE (One-Time, Manual)                                │
├─────────────────────────────────────────────────────────────────┤
│ 1. Design master pages in Scribus (visual GUI)                 │
│ 2. Define frame positions, margins, headers/footers            │
│ 3. Export .sla template                                        │
│ 4. Python parser extracts layout → CSS template (automated)    │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ PRODUCTION PHASE (Automated, Fast)                             │
├─────────────────────────────────────────────────────────────────┤
│ Markdown with YAML front matter                                │
│     ↓                                                           │
│ Pandoc → JSON AST (preserves EVERYTHING)                       │
│     ↓                                                           │
│ Python parser:                                                  │
│   • Load metadata from YAML                                    │
│   • Parse JSON AST → block model                               │
│   • Detect callouts, wikilinks, images, tables                 │
│   • Apply layout profile rules                                 │
│   • Generate HTML with inline CSS                              │
│     ↓                                                           │
│ WeasyPrint renderer:                                            │
│   • Apply Scribus-derived CSS layout                           │
│   • Apply GitHub/VSCode Markdown theme                         │
│   • Render to high-quality PDF                                 │
│     ↓                                                           │
│ PDF output (2-3 seconds, beautiful typography)                 │
└─────────────────────────────────────────────────────────────────┘
```


### Component Breakdown

#### 1. Scribus Layout Extractor (New Component)

**Purpose:** Parse `.sla` file once to extract layout specification


#### 2. Pandoc JSON Parser (Replace DocBook Parser)

**Purpose:** Convert Pandoc JSON AST to enriched block model

**Detects:**

- Headings (1-6) with proper hierarchy
- Paragraphs with inline formatting (bold, italic, links)
- Callouts/Admonitions (`> [!WARNING]`, `> [!DANGER]`, `> [!NOTE]`)
- Wikilinks (`[[REF-2201 | Display Text]]`)
- Images with captions (`![[image.png]]`)
- Tables (with proper column alignment)
- Code blocks (with syntax highlighting hints)
- Ordered/unordered lists (with nesting)
- Blockquotes

**Output:** Python block model (same structure as current `build_blocks()`)

#### 3. HTML Generator 

**Purpose:** Convert block model → HTML with obsidian Markdown styling

**Features:**

- Obsidian Markdown CSS theme
- Callout boxes with icons and colors
- Syntax-highlighted code blocks
- Proper table styling
- Image positioning and captions
- Wikilink handling (convert to internal anchors or external links)


---

## What Works Well (Keep This)

- ✅ YAML front matter metadata system
- ✅ Scribus visual layout designer (master pages, frame positioning)
- ✅ Layout profile JSON configuration
- ✅ Document state logic (active/draft/retired)
- ✅ Folder structure and organization
- ✅ Conditional output/logging system

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

- Treat `drafts/` as the **working area** for authors. (truth)
- `published/` holds **current live outputs** for PDF and web.
- `releases/` is **write-once, read-many**: each release is a timestamped zip of inputs + outputs.
- `/assets` is the **single hub** for everything the pipeline generates or needs besides Markdown.


---


### Problems Identified

1. **DocBook XML loses Markdown semantics**
    
    - Callouts (`> [!WARNING]`) → stripped or rendered as plain blockquotes
    - Wikilinks (`[[REF-2201 | Display Text]]`) → lost entirely
    - Images (`![[screenshot.png]]`) → not properly handled
    - Tables, code blocks → limited formatting
2. **Scribus rendering is problematic**
    
    - Slow (10-15 seconds per document)
    - Brittle overflow handling (complex frame linking logic)
    - Limited Python API (incomplete, hard to debug)
    - Poor typography (no OpenType features)
    - Not designed for automation

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
## 5. Image Resolution and Format Rules

| Output Type | Target Resolution | Scaling | Preferred Format | Notes |
|--------------|-------------------|----------|------------------|--------|
| **PDF** | 300 DPI | Full width (auto scaled) | PNG / TIFF | For print; master images downscaled |
| **Web (HTML)** | 96–150 DPI | 60–70% of full scale | WebP / PNG | Optimized for fast load, lazy-loaded |

High-resolution “master” images are stored under `assets/images/`. Derived formats (`print`, `web`) are automatically created during publication.

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




## 9. Release Packaging
When final approval is reached and document status is `Active`, automation zips together:
- Markdown source.
- XML. (if exists)
- Images (print + web variants).
- Fonts, diagrams, and references.
- Generated PDF + HTML.
- `job.json` and `images.json` metadata. (if exits)
- All other job, task and document related items.

All zips stored under `/releases/{SOP|STD|REF|APP}/` for audit traceability.


## Recreation Requirement

jobs can be recreated using this information if needed. 

---

## 10. Security and Compliance
- Strip EXIF metadata from all images.
- Watermark internal documents where required.
- Block inclusion of unapproved external images.
- Maintain copyright attribution for any licensed media.

---



## 5. 🧩 Special Formatting Controls 

  

Support a few **Markdown markers** that control

page behavior during PDF generation. These have no effect on web or text output


  

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



##  Assets, Images, and Media (Overview)

This pipeline treats **Markdown as the single source of truth for text**, and `/assets` as the single home for **all non-Markdown payloads**:

- **Job metadata and image registries** live in `assets/xml/metadata/`.
- **Images and diagrams** are organized by document ID and project in `assets/images/` and `assets/diagrams/`.
- **Web theming and scripts** live under `assets/web/`.
- **Fonts and other shared brand assets** live under `assets/fonts/`.
- **QR codes, barcodes, and attachments** live under `assets/misc/`.

For image-heavy SOPs:

- Authors reference images from Markdown using relative paths into `assets/images/...`.
- A separate standards document defines **good practices for image resolution, captions, and figure usage** for both PDF and web outputs.

The result is a pipeline that can support **dozens or hundreds of documents** while keeping layout, branding, and assets consistently managed and auditable.

---

##  Figure and Caption Handling Standards

The document pipeline uses **hidden comment directives** to define image formatting and captions in Markdown while keeping the source clean and preview-friendly.

###  Standard FIGURE Syntax

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

###  Example Output

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

###  Caption Logic Flow

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

## Suggested laout profile

```json
{
  "layout_profile": {
    "id": "sop_default",
    "label": "SOP Default Layout Profile",
    "version": "1.1.0",
    "document_category": "SOP",
    "description": "Layout, resources, style mapping, and frame semantics for SOP documents rendered via Scribus.",
    "resources": {
      "scribus_template": "templates/layouts/DTS_Master_Report_Template.sla",
      "pdf_directory": "published/pdf",
      "web_directory": "published/web"
    },
    "styles_map": {
      "docbook": {
        "heading": {
          "1": "Heading1",
          "2": "Heading2",
          "3": "Heading3",
          "4": "Heading4",
          "5": "Heading5",
          "6": "Heading6"
        },
        "paragraph": "BodyText"
      }
    },
    "outputs": {
      "pdf": {
        "mode": "ACTIVE_ONLY",
        "filename_pattern": "{document_id}_r{revision}.pdf",
        "target_directory": "published/pdf"
      },
      "web": {
        "mode": "DISABLED",
        "filename_pattern": "{document_id}_r{revision}.html",
        "target_directory": "published/web"
      },
      "release_bundle": {
        "mode": "DISABLED",
        "filename_pattern": "{document_id}_r{revision}_{timestamp_utc}.zip",
        "target_directory": "releases/{family}"
      }
    },
    "logging": {
      "enabled": true, 
      "level": "DEBUG", 
      "only_when_active": false, 

      "internal": {
        "enabled": true,
        "directory": "logs",
        "pattern": "{document_id}_pipeline.log"
      },
      "external": {
        "enabled": false,
        "only_when_active": true, 
        "directory": "releases/{family}/_logs",
        "pattern": "{document_id}_r{revision}_{pipeline_profile}_{timestamp_utc}.log"
      }
    },
    "scribus": {
      "masters": {
        "first_page": "MP_FIRST",
        "continuation_pages": "MP_CONT"
      },
      "required_styles": ["BodyText", "Heading1", "Heading2"]
    },
    "layout": {
      "pages": [
        {
          "page": 1,
          "frames": [
            {
              "name": "DownstreamApnMain",
              "type": "TextFrame",
              "x": 6.0223,
              "y": 1.7639,
              "width": 1.9498,
              "height": 0.3291,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "downstream_apn",
              "value": "{downstream_apn_joined}"
            },
            {
              "name": "UpstreamApnMain",
              "type": "TextFrame",
              "x": 4.0725,
              "y": 1.7639,
              "width": 1.9498,
              "height": 0.3291,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "upstream_apn",
              "value": "{upstream_apn_joined}"
            },
            {
              "name": "ApnMain",
              "type": "TextFrame",
              "x": 2.1227,
              "y": 1.7639,
              "width": 1.9499,
              "height": 0.3291,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "apn",
              "value": "{apn}"
            },
            {
              "name": "StatusMain",
              "type": "TextFrame",
              "x": 6.7583,
              "y": 10.15,
              "width": 1.15,
              "height": 0.1833,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "status",
              "value": "{status}"
            },
            {
              "name": "ApproverMain",
              "type": "TextFrame",
              "x": 5.4884,
              "y": 1.4139,
              "width": 2.46,
              "height": 0.3292,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "approver",
              "value": "{approver}"
            },
            {
              "name": "DepartmentMain",
              "type": "TextFrame",
              "x": 0.5,
              "y": 1.4139,
              "width": 2.5115,
              "height": 0.3292,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "department",
              "value": "{department}"
            },
            {
              "name": "OwnerMain",
              "type": "TextFrame",
              "x": 3.0115,
              "y": 1.4139,
              "width": 2.46,
              "height": 0.3292,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "owner",
              "value": "{owner}"
            },
            {
              "name": "AmosVersionMain",
              "type": "TextFrame",
              "x": 0.5,
              "y": 1.7639,
              "width": 1.6227,
              "height": 0.3291,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "amos_version",
              "value": "{amos_version}"
            },
            {
              "name": "TitleMain",
              "type": "TextFrame",
              "x": 2.0669,
              "y": 0.5,
              "width": 4.5997,
              "height": 0.8722,
              "font": "Trebuchet MS Regular",
              "fontsize": 22.0,
              "role": "title",
              "value": "{title}"
            },
            {
              "name": "BodyMain",
              "type": "TextFrame",
              "x": 0.5,
              "y": 2.1137,
              "width": 7.4721,
              "height": 7.8919,
              "font": null,
              "fontsize": null,
              "role": "body"
            },
            {
              "name": "DocIdMain",
              "type": "TextFrame",
              "x": 6.6843,
              "y": 0.5431,
              "width": 1.2747,
              "height": 0.2708,
              "font": null,
              "fontsize": null,
              "role": "meta",
              "meta_key": "document_id",
              "value": "{document_id}"
            },
            {
              "name": "RevisionMain",
              "type": "TextFrame",
              "x": 6.6843,
              "y": 0.8278,
              "width": 1.2747,
              "height": 0.2708,
              "font": null,
              "fontsize": null,
              "role": "meta",
              "meta_key": "revision",
              "value": "{revision}"
            },
            {
              "name": "EffectiveDateMain",
              "type": "TextFrame",
              "x": 6.6843,
              "y": 1.0973,
              "width": 1.2747,
              "height": 0.2708,
              "font": null,
              "fontsize": null,
              "role": "meta",
              "meta_key": "effective_date",
              "value": "{effective_date}"
            }
          ]
        },
        {
          "page": 2,
          "frames": [
            {
              "name": "BodyContinuation",
              "type": "TextFrame",
              "x": 0.5,
              "y": 1.3936,
              "width": 7.4721,
              "height": 8.612,
              "font": null,
              "fontsize": null,
              "role": "body"
            },
            {
              "name": "TitleContinuation",
              "type": "TextFrame",
              "x": 2.0669,
              "y": 0.5,
              "width": 4.5997,
              "height": 0.8722,
              "font": "Trebuchet MS Regular",
              "fontsize": 22.0,
              "role": "title",
              "value": "{title}"
            },
            {
              "name": "DocIdContinuation",
              "type": "TextFrame",
              "x": 6.6843,
              "y": 0.5431,
              "width": 1.2747,
              "height": 0.2708,
              "font": null,
              "fontsize": null,
              "role": "meta",
              "meta_key": "document_id",
              "value": "{document_id}"
            },
            {
              "name": "RevisionContinuation",
              "type": "TextFrame",
              "x": 6.6843,
              "y": 0.8278,
              "width": 1.2747,
              "height": 0.2708,
              "font": null,
              "fontsize": null,
              "role": "meta",
              "meta_key": "revision",
              "value": "{revision}"
            },
            {
              "name": "EffectiveDateContinuation",
              "type": "TextFrame",
              "x": 6.6843,
              "y": 1.0973,
              "width": 1.2747,
              "height": 0.2708,
              "font": null,
              "fontsize": null,
              "role": "meta",
              "meta_key": "effective_date",
              "value": "{effective_date}"
            },
            {
              "name": "StatusContinuation",
              "type": "TextFrame",
              "x": 6.7583,
              "y": 10.15,
              "width": 1.15,
              "height": 0.1833,
              "font": "Arial Regular",
              "fontsize": 11.0,
              "role": "meta",
              "meta_key": "status",
              "value": "{status}"
            }
          ]
        }
      ]
    }
  }
}

```
