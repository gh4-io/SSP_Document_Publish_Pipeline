---
tilte: Workpackage Configuration & Sequencing Reference
tags:
  - AMOS
category: REF
document_id: REF-2201
owner: Jason Grace
approver:
effective_date:
status: Draft
amos_version: "25.6"
apn: "2201"
dapn:
  - "58"
---
# Workpackage Configuration & Sequencing Reference

## 1. Purpose
This Reference (REF) document provides a comprehensive, structured explanation of **AMOS APN 2201 – Workpackage Configuration**, including Workpackage Status, Actions, Sequencing, Component Workpackages, and all associated configuration elements.

It consolidates the official AMOS content from the *Workpackage Configuration* manual (pages 1–15) into a clear, aviation‑operations‑friendly reference for CVG 145 Scheduling and Planning teams.  

---

## 2. Scope
This REF applies to:
- Aircraft Workpackages  
- Component Workpackages  
- Workpackage Status Configuration  
- Action Permissions  
- Workpackage Sequencing (primary focus)  
- WP Configuration behaviors visible in View/Edit Workpackage  
- Integration with CVG Workpackage workflows, SOPs, and training  

It does *not* describe how to execute maintenance tasks; those procedures are documented in SOP series.

---

## 3. Definitions
**Workpackage (WP)** – A structured container in AMOS containing events, work orders, jobcards, and related tasks.  

**WP Configuration** – APN 2201 program responsible for defining statuses, actions, sequencing, component WP behavior, and related logic.  

**Sequencing** – AMOS logic controlling the ordering, grouping, and sorting of maintenance events inside a WP.

**Event** – A task, finding, jobcard, or maintenance action assigned to a workpackage.

---

## 4. APN 2201 – Overview
According to pages 4–6 of the source document, APN 2201 is located at:

**Applications → Planning → Workpackages → Workpackage Configuration**

This module controls:
- Aircraft Workpackage status & permitted actions  
- Component Workpackage status & permitted actions  
- Workpackage sequencing types  
- Filters, ordering, and event grouping rules  
- Access to WP-related licenses  

---

## 5. Aircraft Workpackage Configuration

#### 5.1 WP Status (Aircraft)
From pages 4–6:

The *WP Status tab* controls which actions are available in View/Edit Workpackage for each Workpackage Status.

###### WP Status Table Structure
**Columns include:**
- Name  
- Icon  
- Resource Allocation Done (boolean)  
- Is Closed (boolean)  

###### Purpose
These determine whether a status:
- is visible  
- is allowed to trigger resource allocation  
- counts as a *closed* workpackage  

---

#### 5.2 Action Permissions (Aircraft)
Pages 5–6 list the full Action permission set.

Actions include (partial list):
- Add Customer Requirement  
- Add Jobcard  
- Add Remark  
- Add Time to Staff Resource Request  
- Administrative Close  
- Approval  
- Assign / Deassign  
- Collect Events, Jobcards, Panels  
- Create Finding  
- Create Scheduled Workorder  
- Export / Import / Print / Release to Service  
- Reserve Resources  
- Sequence  
- Set Critical Event  
- Time Booking  
- Undo/Unprint, etc.  

Each WP Status must explicitly enable these using checkboxes.

---

## 6. WP Sequencing (Primary Focus)

Pages 6–7 describe the WP Sequencing tab.

#### 6.1 Sequencing Type Fields
**Columns:**
- Name  
- First Ordering  
- Second Ordering  
- Third Ordering  
- Fourth Ordering  

These define **sorting priority**, forming the final sequence inside a Workpackage.

Example:
```
First Ordering: Expected Date
Second Ordering: Event Type
Third Ordering: ATA Chapter
Fourth Ordering: Taskcard
```

---

#### 6.2 Filter Section
From page 7:

**Fields:**
- "Reuse existing sequence numbers"  
- Enable/Disable  
- Select by default “Sequence on Assignment”  
- Include non-executable events  

These modify how sequences update during:
- Recreate Sequence  
- Assignment  
- Event addition  

---

## 7. Component Workpackage Configuration
Pages 8–10 detail Component WP Status and Actions.

###### Status Permissions (Component)
Same structure as Aircraft WPs:
- Name  
- Icon  
- Resource Allocation Done  
- Is Closed  

###### Actions include:
- Add Component Requirement  
- Add Remark  
- Add Shopcard  
- Assign / Deassign  
- Close / Reopen  
- Collect Shopcards  
- Create Workstep  
- Print / Barcode  
- Release Component  
- Scrap  
- Sequence  
- Sync Revision  
- Time Booking  
- Undo / Unprint  

###### Sequencing (Component)
Works identically to Aircraft Sequencing:
- First/Second/Third/Fourth Ordering  
- Filters  
- Reuse / Recreate options  

---

## 8. Workpackage Sequence Matrix

#### Purpose
To provide a quick reference for which **sequencing attributes** apply to which **Sequencing Types** across common operational check types.

#### Sequence Matrix

| Attribute                    | Phase Check | A-Check | Transit Check | OOP Check |
| :--------------------------- | :---------: | :-----: | :-----------: | :-------: |
| Priority - Workorder Number  |             |         |       ☑       |           |
| Priority - Expected Date     |             |         |       ☑       |           |
| Expected Date                |      ☑      |    ☑    |       ☑       |     ☑     |
| Workorder Number             |      ☑      |    ☑    |       ☑       |     ☑     |
| Dimension - To Go            |             |    ☑    |               |     ☑     |
| Sched / Unsched - Exp. Date  |             |    ☑    |       ☑       |     ☑     |
| Event Type - Exp. Date       |      ☑      |    ☑    |               |     ☑     |
| Group Event Type - Exp. Date |      ☑      |    ☑    |               |     ☑     |
| ATA-Chapter                  |      ☑      |    ☑    |               |     ☑     |
| Taskcard                     |      ☑      |    ☑    |               |     ☑     |
| Area - Taskcard              |      ☑      |    ☑    |               |     ☑     |
| Sequence Code - Taskcard     |      ☑      |    ☑    |               |     ☑     |
| Event Chain Tree             |      ☑      |    ☑    |               |     ☑     |

---

## 9. Sequence Attribute Definitions

###### Expected Date  
Primary due-date driven ordering.

###### Workorder Number  
Sorts tasks in numerical document order.

###### Dimension – To Go  
Sorts by remaining life (FH/FC/Days).

###### Sched/Unsched – Expected Date  
Includes scheduling class + expected date.

###### Event Type – Expected Date  
Orders based on event categories (Phase, MPD, CPCP, etc.).

###### Group Event Type  
Bundles related event types for combined sorting.

###### ATA Chapter  
Groups tasks technically.

###### Area  
Groups by aircraft zone.

###### Taskcard  
Sorts tasks numerically/alphabetically.

###### Sequence Code  
Custom AMOS taskcard sequencing code.

###### Event Chain Tree  
Orders based on dependency relationships.

---

## 10. Usage Notes
- Choose a sequencing type based on the maintenance event being prepared.  
- Transit Checks usually require minimal, date-driven priority.  
- A-Checks frequently require To-Go calculations plus ATA grouping.  
- OOP Checks depend heavily on Dimension-To-Go and Event Chain logic.  

---

## 11. Related Documents
- AMOS APN 2201 Workpackage Configuration (Source PDF)  
- [[SOP_501_APN58_WORKPACKAGE_CREATEION_REV00|SOP – Workpackage Creation]]
- REF – Customer Profiles  
- APP – Sequencing Examples  

---

## 12. Revision History
| Rev | Date | Description | Author |
|-----|------|-------------|--------|
| 00  | 2025-11-27 | Initial creation from APN 2201 source | Documentation Team |

