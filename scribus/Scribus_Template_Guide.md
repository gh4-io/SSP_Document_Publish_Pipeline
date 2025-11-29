# Scribus Template Guide – Frames, Styles, and Linking to Python

This guide explains how to build a **SOP template** in Scribus that works cleanly with your Python automation.

The goal is to have a `.sla` template that:

- Has **named frames** (for header, footer, body, sidebar, logo, etc.).
- Has **paragraph styles** that map to DocBook tags.
- Is robust against changes (script can detect missing frames and fail with a clear error).

---

## 1. Creating a Valid `.sla` Template in Scribus

1. **Launch Scribus** and create a new document:
   - Choose page size (e.g., Letter 8.5×11 or A4).
   - Set margins appropriate for SOPs (e.g., 0.75″ all around, or per your SOP standards).
2. Set **Master Pages**:
   - Open **Edit → Master Pages**.
   - Create a master page called `SOP_Master`.
   - This will contain your header/footer and any recurring elements.
3. Configure **Document Properties** (File → Document Setup):
   - Set measurement units (e.g., millimeters or inches).
   - Set default fonts and baseline grid if desired.
4. Save the template:
   - `File → Save As` → `templates/sop_template.sla` (or similar path).

> Important: Always edit styles and master-page elements in the template file, not in each generated document. The script will **copy** or **instantiate** from this starting point.

---

## 2. Naming Frames for Automation

Your Python script needs to locate frames by name. Plan a naming scheme such as:

- `HeaderFrame`
- `FooterFrame`
- `BodyFrame1`
- `BodyFrame2` (if wrapped or multi-column)
- `SidebarFrame`
- `LogoFrame`

### How to Name a Frame

1. Draw a text frame: **Insert → Text Frame** (or toolbar icon).
2. With the frame selected, open **Windows → Properties** and look at the **X, Y, Z** tab.
3. In the **Name** field, type something like `BodyFrame1`.
4. Repeat for each important frame.

The Python script will use functions like `scribus.getPageItems()` and `scribus.getObjectName()` to find these frames.

---

## 3. Defining Paragraph Styles

You want a finite set of paragraph styles that map to DocBook tags. Example mapping:

- `BodyText` ← paragraph elements (`<para>`)
- `Heading1` ← `<section><title>` at top level
- `Heading2` ← nested section titles
- `CodeBlock` ← `<programlisting>`
- `TableHeader` / `TableCell` ← `<thead>` / `<tbody>` cells
- `Callout` ← `<note>`, `<warning>`, etc.

### Creating Styles

1. Open **Edit → Styles…**.
2. Click **New → Paragraph Style**.
3. Set **Name** to e.g. `BodyText`.
4. Configure:
   - Font family / size
   - Line spacing
   - Indents, spacing before/after
5. Click **Apply** then **Done** or create additional styles.

Remember to **only use these styles** in your automation; avoid ad hoc manual styling when possible.

---

## 4. Layout Considerations

To make the script’s job easier:

- Keep **one main text frame** per page for normal body flow (`BodyFrame1`).
- If using multi-column layouts, consider using **linked frames** with clear names (`BodyFrame1_Page1`, `BodyFrame1_Page2`, etc.) or let the script **create extra pages** and frames as needed.
- Avoid overlapping frames that might confuse text flow.

A simple layout:

- Header: a frame across the top with placeholders for:
  - Logo (image frame)
  - SOP ID
  - Title
  - Revision / Effective Date
- Footer: a frame across the bottom with:
  - Page number (`Page %` via Scribus Page → Insert → Character → Page Number)
  - Document status (e.g., “Active”, “Draft”)
- Body: large text frame `BodyFrame1` between header and footer.

---

## 5. Linking the Template to Python

Scribus Python scripts run in the **Scribus Scripter** environment. The script expects:

- A document open (your template) or path to one to open.
- Frames with known names.
- Styles with known names.

### Basic Workflow

1. Open Scribus.
2. Open `templates/sop_template.sla`.
3. Run `Scripts → Execute Script…` and choose `scripts/scribus_pipeline_simple.py`.
4. The script will:
   - Ask for DocBook XML file and output locations (or read a job JSON).
   - Fill in frames and styles.
   - Export PDF/HTML.

### Binding the Script to a Menu

To make it easy for users:

1. Place your scripts in a directory Scribus knows about:
   - On some platforms: `~/.config/scribus/scripts` or similar.
2. Use **Scripter → Show Console** to test imports.
3. Optionally create a simple launcher script that just calls your main pipeline script with a default configuration.

---

## 6. Template Validation Strategy

Because templates evolve over time, build checks into the script:

- At startup, the script verifies:
  - All **required frames** exist (e.g., `HeaderFrame`, `FooterFrame`, `BodyFrame1`).
  - All **required styles** are defined (e.g., `BodyText`, `Heading1`, `Heading2`).
- If something is missing, the script:
  - Shows an error dialog.
  - Writes to a log file.
  - Exits without producing a partial or broken PDF.

This prevents “silent drift” where someone modifies the template and breaks automation.

---

## 7. Multi-Template Support (SOP vs STD vs REF vs APP)

You can either:

1. Use **one master template** with conditional elements, or
2. Create **separate .sla templates** per family, e.g.:
   - `sop_template.sla`
   - `std_template.sla`
   - `ref_template.sla`
   - `app_template.sla`

The advanced script can choose the template based on metadata (e.g., `family: SOP` in Markdown YAML).

---

## 8. Next Steps

1. Build your **SOP template** following the above conventions.
2. Add frame names + paragraph styles.
3. Save under `templates/`.
4. Start wiring up `scribus_pipeline_simple.py` and adjust the script if frame names or style names change.
