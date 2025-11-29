# Scribus Python Pipeline – Simple Version

This note explains the **simple Scribus Python pipeline** implemented in `scripts/scribus_pipeline_simple.py`.

The aim is to:

- Assume a single SOP template (`sop_template.sla`).
- Ask the user for a DocBook XML file.
- Import metadata and body text.
- Apply basic paragraph styles.
- Export a PDF.
- Optionally export HTML (if desired / supported).

---

## 1. Assumptions

- Template file: `templates/sop_template.sla`
- Named frames:
  - `HeaderFrame`
  - `FooterFrame`
  - `BodyFrame1`
- Paragraph styles:
  - `BodyText`
  - `Heading1`
  - `Heading2`
- The DocBook XML has at least:
  - `<title>`
  - `<info>` block with metadata (`<revnumber>`, `<date>`, maybe custom elements)
  - `<section>` elements for body content.

---

## 2. Flow Overview

1. Prompt the user for the **DocBook XML file**.
2. Parse the XML (using Python’s `xml.etree.ElementTree` or `lxml` if available).
3. Extract metadata:
   - SOP ID (e.g., from `<info><keywordset>` or a custom element).
   - Title (`<title>`).
   - Revision number (`<revnumber>`).
   - Effective date (`<date>` or custom).
4. Fill the header frame with a formatted string, e.g.:
   - `"{sop_id} – {title} (Rev {rev}, Eff {date})"`
5. Build a plain-text body:
   - Concatenate section titles and paragraphs.
6. Insert body text into `BodyFrame1`.
7. Apply basic styles:
   - First-level titles as `Heading1`.
   - Paragraphs as `BodyText`.
8. Export PDF to a file chosen by the user.

This simple flow does not yet handle:
- Multi-page text flow.
- Tables.
- Nested lists.
- Complex DocBook features.

Those are addressed in the advanced pipeline.

---

## 3. User Experience

From inside Scribus:

1. Open the template (`sop_template.sla`).
2. Run `Scripts → Execute Script… → scribus_pipeline_simple.py`.
3. The script prompts you:
   - File dialog: “Select DocBook XML”.
   - File dialog: “Select output PDF path”.
4. After processing, you get a single PDF based on the template + XML.

---

## 4. Where to Customize

Inside the script:

- **Mapping of XML → metadata fields**:
  - Adjust how SOP ID, revision, and effective date are extracted.
- **Header template**:
  - Customize how text is formatted in `HeaderFrame`.
- **Style application**:
  - Adjust the logic that decides which lines get `Heading1` vs `BodyText`.

---

## 5. Next Steps

1. Implement, test, and refine the simple script.
2. Once reliable, promote the logic to `scribus_pipeline_advanced.py` and start adding features:
   - Multi-page flow.
   - Tables and lists.
   - Sidebars and callout boxes.
   - Per-family template selection.
