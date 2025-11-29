# Scribus Python Pipeline – Advanced / Enterprise Version

This note describes the **advanced Scribus pipeline** implemented in `scripts/scribus_pipeline_advanced.py`.

Goals:

- Robust, **multi-page layout** with linked frames.
- Mapping **DocBook structure → Scribus styles and layout**.
- Per-family templates (SOP / STD / REF / APP).
- **Validation** of templates, frames, and styles before rendering.
- **Release-ready outputs** (PDF, HTML) with logging and error handling.

---

## 1. Inputs

1. **Job JSON** (created by an external driver script), containing:
   - `source_markdown` – path to the original Markdown.
   - `source_docbook` – path to the DocBook XML.
   - `family` – one of `SOP`, `STD`, `REF`, `APP`.
   - `sop_id` / `doc_id` – e.g., `SOP-001`.
   - `title`
   - `revision`
   - `effective_date`
   - `output_pdf`
   - `output_html` (optional)
   - `log_file`
2. Scribus template path selected based on `family`, e.g.:
   - SOP → `templates/sop_template.sla`
   - STD → `templates/std_template.sla`
   - REF → `templates/ref_template.sla`
   - APP → `templates/app_template.sla`

---

## 2. Template Validation

At script startup:

1. Open the `.sla` template.
2. Verify **required frames**:
   - For example:
     - `HeaderFrame`
     - `FooterFrame`
     - `BodyFrame1`
     - Optionally `SidebarFrame`, `LogoFrame`, `TOCFrame`
3. Verify **required styles**:
   - `BodyText`
   - `Heading1`, `Heading2`, `Heading3`
   - `TableHeader`, `TableCell`
   - `Callout`, `Warning`, etc.
4. If anything is missing:
   - Write an entry to the log.
   - Show a dialog in Scribus (for interactive runs).
   - Abort gracefully.

---

## 3. DocBook Parsing and Mapping

Using `xml.etree.ElementTree` or `lxml`:

- Parse the DocBook XML.
- Traverse sections in order:
  - Extract `<title>` for section headings.
  - Extract `<para>`, `<orderedlist>`, `<itemizedlist>`, `<table>`, `<note>`, etc.
- Build an internal representation of the document, such as:

```python
[
  {"type": "heading", "level": 1, "text": "Section Title"},
  {"type": "para", "text": "First paragraph."},
  {"type": "para", "text": "Second paragraph."},
  {"type": "table", "rows": [...], "header": [...]},
  {"type": "callout", "role": "warning", "text": "Important safety info."},
  ...
]
```

Then map these to Scribus:

- `heading` level 1 → style `Heading1`
- `heading` level 2 → style `Heading2`
- `para` → style `BodyText`
- `callout` → style `Callout`
- `table` → create a table frame or formatted text structure.

---

## 4. Multi-Page Text Flow

Options:

1. **Pre-created linked frames**:
   - Template contains linked `BodyFrame1_Page1`, `BodyFrame1_Page2`, etc.
   - Script finds them and flows text into this chain.
2. **Script-created pages and frames** (recommended for scale):
   - Start with `BodyFrame1` on page 1.
   - When there is more text than fits:
     - Add a page: `scribus.newPage()`.
     - Duplicate position/size of `BodyFrame1`.
     - Link frames (`scribus.linkTextFrames()`).
   - Continue flowing text until all content is placed.

The advanced script should use the second approach to avoid hard limits on page count.

---

## 5. Header, Footer, and Page Numbering

On each page:

- Header Frame:
  - Insert text like: `"{doc_id} – {title} – Rev {revision} – Eff {effective_date}"`.
- Footer Frame:
  - Insert e.g. `"{status} | Page %p of %n"` (Scribus supports automatic page number tokens).
- Ensure the header/footer elements are part of the **master page** to minimize script work.

The script only needs to fill **document-specific** parts if they are not already handled via variables or tokens.

---

## 6. Logos and Thumbnails

- Logos:
  - Place an image frame named `LogoFrame` on the master page.
  - The script can load an image from a configured path using `scribus.loadImage()` and `scribus.setScaleImageToFrame()`.
- Thumbnails:
  - After exporting the main PDF, the script can:
    - Export first page as an image (`File → Export → Save as Image`) via scripting.
    - Save to `published/web/thumbnails/` for use on intranet / SharePoint.

---

## 7. Table of Contents (TOC) Generation

Simplified approach:

1. While parsing DocBook, build a list of headings with levels.
2. Before or after body rendering, build a **TOC text block** from these headings:
   - Use a dedicated frame on a TOC page (`TOCFrame`).
   - Each TOC line is a paragraph with style `TOCEntry1`, `TOCEntry2`, etc.
3. Page numbers:
   - The simplest approach is to omit exact page numbers or generate the TOC on a second run.
   - For full automation with page numbers, you may need:
     - A two-pass approach (first pass: layout; second pass: read positions/page numbers and regenerate TOC).

In many SOP environments, a heading-only TOC is acceptable even without live page numbers.

---

## 8. Error Handling and Logging

The advanced script should:

- Maintain a `log` list in memory and write to a log file on disk.
- For each major step (parse XML, validate template, flow text, export PDF):
  - Log start and end, plus errors.
- In case of a fatal error:
  - Show a user-friendly message in Scribus if running interactively.
  - Exit with a non-zero code if running in a batch/headless context.

Log fields to consider:

- Timestamp
- Script version
- Doc ID
- Input file paths
- Output file paths
- Errors / warnings

---

## 9. Release Packaging

Once the PDF/HTML are successfully generated, a separate script (`release_packager.py`) can:

- Create a zip file in:
  - `releases/SOP/{doc_id}_rev{rev}_{yyyymmddHHMM}.zip`
- Include:
  - Source Markdown
  - DocBook XML
  - Job JSON
  - PDF, HTML
  - Logs
  - Optional thumbnails or auxiliary files

This gives you a **GitHub release–style artifact** for each SOP revision.

---

## 10. Next Steps

1. Implement and test `scribus_pipeline_advanced.py` against a few real SOPs.
2. Incrementally add support for tables, callouts, sidebars.
3. Capture every decision and mapping in the `styles/` folder so that the system is **documented, reproducible, and teachable**.
