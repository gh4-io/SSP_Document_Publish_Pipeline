---
title: SOP Writing Standards – PDF Publications
revision: 0
tags:
  - SOP_Standards
  - PDF
  - Technical_Writing
---

# SOP Writing Standards – PDF Publications

This document defines **writing and content standards** for SOP-style documents intended to be published as **paginated PDFs** via the Document Publish Pipeline (Markdown → DocBook → Scribus → PDF).

It focuses on:

- How authors should structure content in Markdown.
- How to write clear, safe, and maintainable procedures.
- How to support reliable layout in Scribus (page-based output).

These standards apply to **SOP**, **STD**, **REF**, and **APP** families unless otherwise noted.

---

## 1. Purpose and Scope

PDF outputs are the **authoritative, controlled copies** of procedures. They may be printed, attached to AMOS, or distributed as frozen revisions.

Therefore, PDF-oriented SOPs must:

- Be **unambiguous** and **step-driven**.
- Be optimized for **page-based reading** (front-to-back).
- Maintain **stable pagination** across revisions when possible (for cross-references).
- Present **figures, warnings, and notes** in a way that supports print use.

Markdown is still the **single source of truth**, but authors should think in terms of **pages and spreads** when designing PDFs.

---

## 2. Document Anatomy (PDF-focused)

Each SOP-family document should follow the same high-level structure:

1. **YAML Front Matter** (machine-readable metadata)
2. **Title Block** (SOP ID, title, revision, effective date, owner)
3. **Purpose & Scope**
4. **Responsibilities / Applicability** (who uses this)
5. **Prerequisites & Safety**
6. **Procedure** (step-by-step)
7. **Checks / Acceptance Criteria**
8. **References & Related Documents**
9. **Revision History** (optional, or managed elsewhere)

### 2.1. YAML Front Matter Template

```yaml
---
doc_id: SOP-XXX
title: SHORT, ACTION-ORIENTED TITLE
family: SOP        # SOP | STD | REF | APP
revision: 0
status: Draft      # Draft | Active | Retired
effective_date: 2025-01-01
owner: "Role or Department"
approver: "Approver Name / Title"
tags:
  - AMOS
  - CVG145
  - Scheduling
---
```

Front matter must be:

- Present on **every document**.
- Strictly formatted as YAML (no tabs, consistent indentation).
- Updated **whenever revision changes**.

---

## 3. Heading Levels and Numbering

### 3.1. Recommended Heading Hierarchy

- `#`   – Document title (single per file).
- `##`  – Top-level sections (Purpose, Scope, Procedure, etc.).
- `###` – Subsections (per major task or phase).
- `####` – Optional sub-subsections (only when clearly needed).

Avoid going deeper than `####` in PDF-focused SOPs; deeply nested headings are harder to read on paper.

### 3.2. Manual vs Automatic Numbering

- Let the pipeline control **section numbering** where possible.
- Use **ordered lists** (`1.`, `2.`, `3.`) for steps instead of manually typing “Step 1”, “Step 2”, etc.
- Inside a step, use nested lists for sub-steps rather than new headings.

Example:

```markdown
### 4. Procedure

1. Verify aircraft status in AMOS.
2. Open the workpackage:
   1. Navigate to the Workpackage module.
   2. Search by workorder number.
   3. Confirm registration and APN.
3. Record the initial ground time.
```

---

## 4. Writing Style and Tone

### 4.1. General Style

- Use **imperative voice**: “Click…”, “Verify…”, “Confirm…”.
- Be **specific**, not vague: “Select the **CVG145_Schedule** list” instead of “Open the schedule”.
- Avoid slang, humor, or casual phrasing in final SOPs.

### 4.2. Clarity and Safety

- One **action per step** whenever possible.
- Precede risky steps with **warnings** or **notes**.
- Use consistent terminology with AMOS and operational language (e.g., “Workpackage”, “Ground Time”, “APN”).

### 4.3. Tense and Person

- Default: **imperative** and **second person implied**:
  - “Enter the workorder number.”
  - “Verify that the registration matches the request.”

---

## 5. Layout Considerations for PDF

Although authors work in Markdown, they must keep **page layout** in mind:

### 5.1. Page Breaks

Use the special directive when a **new major section** should start on a new page:

```markdown
::: pagebreak
:::
```

Good use cases:

- Before “Procedure” in a long SOP.
- Before “Revision History”.
- Before a dense figure collection.

### 5.2. Keep Sections Together

To avoid instructions splitting awkwardly across pages, wrap them in `keep-together`:

```markdown
::: keep-together
### 4.2. Confirm Ground Time

1. Open AMOS flight record…
2. Verify arrival and departure UTC…
3. Cross-check with DHL schedule…
:::
```

Use this for:

- Short procedures (2–8 steps).
- Critical warning + step groupings.

### 5.3. Tables

When including tables:

- Keep them **narrow enough** to avoid tiny fonts in PDF.
- Prefer **fewer columns** with clear headings.
- Keep explanatory text **outside** the table where possible.

Example:

```markdown
| Field           | Description                              |
|-----------------|------------------------------------------|
| APN             | AMOS Project Number                      |
| Workorder No.   | Unique identifier for the workpackage    |
| Registration    | Aircraft registration (e.g., G-DHLM)     |
```

---

## 6. Figures, Images, and Captions (PDF)

For PDF, figures need to be **print-ready** and readable at target size.

### 6.1. Referencing Images in Markdown

```markdown
::: figure scale=0.7 border=true align=center
![AMOS Ground Time Screen](../../assets/images/doc/SOP-001/SOP-001_4.2_01__groundtime_screen.png)
**Figure 3 — AMOS Ground Time Screen**
:::
```

Guidelines:

- Always provide a **caption** and **meaningful alt text**.
- Use `scale` to keep images comfortably within margins.
- Use `border=true` when images sit on white background and need visual separation.

### 6.2. Content of Figures

- Only include **necessary UI elements**; crop out irrelevant areas.
- Use callouts or annotations sparingly to avoid clutter.
- Ensure text labels are legible when printed (minimum font size equivalent ~8–9 pt).

### 6.3. Placement

- Place figures **near the relevant text**, after the step where they’re first referenced.
- Reference them explicitly:  
  “See **Figure 3 — AMOS Ground Time Screen**.”

---

## 7. Safety, Warnings, and Callouts

Use **admonition-style blocks** to flag important information. For PDF, these will map to visually distinct boxes.

Example:

```markdown
> [!WARNING]
> Ensure the aircraft is fully de-fueled before proceeding with this task.

> [!NOTE]
> Ground time values shown are examples only.
```

Types:

- `[!WARNING]` – Risk of damage, safety-critical.
- `[!CAUTION]` – Potential for error or rework.
- `[!NOTE]` – Helpful information, context.
- `[!TIP]` – Efficiency boosters, shortcuts.

---

## 8. Examples – Putting It All Together

A minimal “good” PDF-oriented SOP skeleton:

```markdown
---
doc_id: SOP-145-001
title: Creating and Updating CVG145 Ground Time Records
family: SOP
revision: 1
status: Active
effective_date: 2025-01-01
owner: "CVG145 Scheduling"
approver: "CVG145 Station Supervisor"
tags:
  - AMOS
  - GroundTime
---

# Creating and Updating CVG145 Ground Time Records

## 1. Purpose

Describe how CVG145 Scheduling creates, validates, and updates ground time records in AMOS for CVG operations.

## 2. Scope

Applies to all CVG145 Schedulers working in the CVG145 AMOS environment.

## 3. Responsibilities

- CVG145 Schedulers:
  - Maintain accurate ground time records.
  - Communicate discrepancies to Maintenance Management.
- CVG145 Station Supervisor:
  - Reviews adherence to this SOP.
  - Approves changes to this SOP.

## 4. Prerequisites and Safety

> [!WARNING]
> Do not modify ground time for flights that are already closed in AMOS without authorization.

- Access to AMOS with Scheduler role.
- Current CVG145 flight schedule.

::: pagebreak
:::

## 5. Procedure

### 5.1. Locate the Flight

1. Open AMOS and navigate to the Flight module.
2. Filter by station **CVG** and the target date.
3. Identify the correct flight using flight number and registration.

::: figure scale=0.7 border=true align=center
![AMOS Flight List](../../assets/images/doc/SOP-145-001/SOP-145-001_5.1_01__flight_list.png)
**Figure 1 — AMOS Flight List Filtered for CVG**
:::

### 5.2. Update Ground Time

1. Open the flight record.
2. Edit the arrival and departure times as required.
3. Confirm that the calculated ground time matches DHL schedule data.
4. Save the record.

## 6. References

- REF-145-010 – CVG145 AMOS Access Standards
- REF-145-020 – Ground Time Calculation Rules

```

This pattern can be reused for all PDF-targeted SOPs to maintain a consistent, enterprise-grade style.
