---
title: SOP Writing Standards – Web Publications
revision: 0
tags:
  - SOP_Standards
  - Web
  - Technical_Writing
---

# SOP Writing Standards – Web Publications

This document defines **writing and content standards** for SOP-style documents optimized for **web-based consumption** (HTML output) via the Document Publish Pipeline.

It assumes the same Markdown source as PDF-oriented SOPs, but emphasizes:

- Scanability and readability on screens.
- Accessibility (alt text, headings, links).
- Responsiveness and modular content.

---

## 1. Purpose and Scope

Web outputs are ideal for:

- Day-to-day reference on desktops or tablets.
- Quick searching and linking from other systems (SharePoint, AMOS records).
- Embedding into knowledge bases or portals.

Because users may enter at any section (via search, deep links, or TOC), the writing style must:

- Support **non-linear reading** (jumping between sections).
- Provide enough context in each section to stand alone.
- Use **shorter paragraphs** and **more headings**.

---

## 2. Document Anatomy (Web-focused)

The basic structure matches PDF SOPs, but for web:

1. YAML front matter.
2. Title and short summary (optional, but recommended).
3. Sectioned content with more granular headings.
4. Links and cross-references built using Markdown links and anchors.

### 2.1. Short Summary

At the top of the document (after the title), include a 1–3 sentence **summary**:

```markdown
> This SOP describes how CVG145 Scheduling creates and maintains ground time records in AMOS for CVG-based operations.
```

This appears early in the web page and helps users quickly judge relevance.

---

## 3. Headings, TOC, and Navigation

### 3.1. Granular Headings

For web, prefer **more frequent headings**:

- Break long procedures into logical subsections.
- Use headings to separate “Overview”, “Steps”, “Exceptions”, “Examples”.

Example:

```markdown
## 5. Procedure

### 5.1. Standard Ground Time Updates
### 5.2. Same-Day Revisions
### 5.3. Historical Corrections
```

### 3.2. Linkable Anchors

The pipeline can convert headings into anchors. To support stable links:

- Avoid changing heading text unnecessarily across revisions.
- Avoid duplicate headings at the same level (e.g., two `### Procedure` headings).

You can also define explicit anchors when needed:

```markdown
<a id="historical-corrections"></a>
### 5.3. Historical Corrections
```

---

## 4. Writing Style and Tone for Web

### 4.1. Chunked Content

- Keep paragraphs **short** (2–4 sentences).
- Use **bulleted lists** for conditions, options, or criteria.
- Use **ordered lists** only for true sequences of steps.

### 4.2. Inline Links

Use Markdown links to:

- Refer to related SOPs or references.
- Link to external systems (SharePoint, AMOS help, etc.), where appropriate.

Example:

```markdown
See [REF-145-020 – Ground Time Calculation Rules](../REF/REF-145-020.md) for calculation details.
```

Avoid raw URLs; always give them human-readable link text.

---

## 5. Images and Web Considerations

### 5.1. Referencing Web-Optimized Images

Web output should use **web-optimized** variants when available:

```markdown
::: figure scale=0.7 align=center
![AMOS Ground Time Screen](../../assets/images/doc/SOP-001/SOP-001_4.2_01__groundtime_screen.png)
**Figure 3 — AMOS Ground Time Screen**
:::
```

The pipeline can map this to a `web` variant (e.g., WebP) in HTML.

### 5.2. Alt Text and Accessibility

Alt text is **required** for web:

- Describe what the user needs to know, not every pixel.
- If the image is a pure decoration, use a short alt or consider omitting it.

Bad alt text:

> `alt="screenshot"`

Better:

> `alt="AMOS ground time screen showing arrival and departure fields"`

### 5.3. Responsive Layout

Avoid:

- Very wide tables that require horizontal scrolling.
- Fixed-width images that exceed viewport width.

Prefer:

- Tables with 2–4 columns.
- Images scaled by percentage (`scale=0.6`, `scale=0.7`) so they adapt to screen width.

---

## 6. Admonitions and Callouts (Web)

Admonition blocks render especially well on the web. Use them consistently:

```markdown
> [!WARNING]
> Updating ground time for closed flights requires supervisor approval.

> [!NOTE]
> Times shown in screenshots are examples.
```

On the web, these can be styled with color and icons for fast visual scanning.

---

## 7. Linking, Cross-References, and External Systems

### 7.1. Internal Links

For links to other SOPs or refs within the same repository:

- Prefer **relative paths** so the same Markdown works locally and in web views.
- Reference by ID and title: `SOP-145-001 – CVG145 Ground Time`.

Example:

```markdown
For ground time business rules, see [REF-145-020 – Ground Time Calculation Rules](../REF/REF-145-020.md).
```

### 7.2. External Links

When linking to:

- SharePoint pages,
- AMOS docs,
- External vendor documentation,

ensure:

- The destination is accessible to your intended audience.
- Sensitive or internal-only links are clearly marked if exported outside the network.

---

## 8. Searchability and Keywords

To improve search:

- Use consistent terminology (e.g., “ground time” vs “GT”).
- Include important terms at least once in headings or summary.
- Avoid overly creative synonyms for critical concepts.

Example summary optimized for search:

```markdown
> This SOP describes how CVG145 Scheduling creates, validates, and updates ground time records in AMOS for DHL and Kalitta Air operations at CVG.
```

---

## 9. Examples – Web-Optimized SOP Skeleton

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
  - CVG145
---

# Creating and Updating CVG145 Ground Time Records

> This SOP describes how CVG145 Scheduling creates, validates, and updates ground time records in AMOS for CVG-based operations.

## 1. Purpose

Explain the goals of maintaining accurate ground time in AMOS for CVG operations.

## 2. Scope

Applies to all CVG145 Schedulers working in the CVG145 AMOS environment.

## 3. Responsibilities

- CVG145 Schedulers:
  - Maintain accurate ground time records.
  - Escalate discrepancies to Maintenance Management.
- CVG145 Station Supervisor:
  - Reviews adherence to this SOP.
  - Approves changes to this SOP.

## 4. Prerequisites

- AMOS access with Scheduler role.
- Current CVG145 flight schedule.

## 5. Procedure

### 5.1. Locate the Flight

1. Open AMOS and navigate to the Flight module.
2. Filter by station **CVG** and the relevant date.
3. Identify the correct flight using flight number and registration.

> [!NOTE]
> You can bookmark the Flight module URL in your browser for quicker access.

### 5.2. Update Ground Time

1. Open the flight record.
2. Edit arrival and departure times as required.
3. Confirm that calculated ground time matches DHL schedule data.
4. Save the record.

::: figure scale=0.7 align=center
![AMOS Ground Time Screen](../../assets/images/doc/SOP-145-001/SOP-145-001_5.2_01__groundtime_screen.png)
**Figure 1 — AMOS Ground Time Screen**
:::

## 6. References

- [REF-145-020 – Ground Time Calculation Rules](../REF/REF-145-020.md)

```

This pattern ensures the same Markdown works well as a **web page**, with good headings, searchability, and accessibility, while remaining compatible with the PDF pipeline.
