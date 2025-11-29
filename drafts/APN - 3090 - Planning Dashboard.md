---
apn: "3090"
level: "tertiary"
title: "Planning Dashboard (BETA)"
related_apn:
  - "[[2201]]"
  - "[[1600]]"
sop_ref: "CVG145-SOP-DASHBOARD"
tags:
  - "AMOS"
  - "tertiary_apn"
  - "dashboard"
  - "MaintenancePlanning"
---


# APN-3090 – Planning Dashboard (BETA)
## Overview
This AMOS module provides a **graphical overview of all future and past workpackages**, grouped by:
- **Station** (vertical axis)
- **Time Period** (horizontal axis)

The dashboard summarizes matching workpackages in both **table** and **chart** formats.  
These are defined under:

Report Designer → Report Browser → AMOS System Reports → reports → dashboard → Planning

Available reports:
- `PlanningDashboardChart`
- `PlanningDashboardTable`:contentReference[oaicite:1]{index=1}

---

## Configuration
- Path: `Applications/Production/Planning Dashboard`
- Supports a **Settings tab** to select between table or chart view.
- Time periods can align with **shift groups** — matching group IDs and colors are displayed; otherwise greyed out.
- Uses `Generate Dashboard` and `Reload` buttons to refresh data.

---

## Usage & Cautions
- This is a **BETA program** — not to be used productively.  
  Functionality and documentation may change at any time.  
- There is **no support or warranty** for BETA programs; use for visualization or analysis only:contentReference[oaicite:2]{index=2}.
- Data reflects accuracy of upstream APNs:
  - [[APN-2201 – Workpackage Handling]]
  - [[APN-1600 – Resource Planning]]

---

## SOP Link
While no operational SOP exists for APN-3090 (view-only function), it may be referenced in the **Dashboard SOP** for internal training:
- **SOP Name:** CVG145-SOP-DASHBOARD  
- **Purpose:** Defines how Planning staff use dashboard data for shift turnover, report summaries, or management reviews.

---

## Notes
- Suggested cross-reference in your **Power BI “Planning View” dashboard** to ensure data consistency.
- Future consideration: integrate color scheme logic or time filters from AMOS shift group data.
- Keep this note under `/AMOS/Tertiary` folder in your vault.

