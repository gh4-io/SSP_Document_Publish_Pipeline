---
title: Create Workackage Sequencing Type
tags:
  - AMOS
category: SOP
document_id: SOP-200
owner: Jason Grace
approver:
effective_date:
status: Draft
amos_version: "25.6"
apn: "2201"
downstream-apn:
  - "58"
upstream-apn:
department: Planning
pipeline_profile: dts_master_report
revision: 0
---

# Create Workpackage Sequencing Type

> - Create a new sequencing type and define its ordering attributes used in View/Edit Workpackage.

## 1. Scope

AMOS interface under [Aircraft] → [WP Sequencing], window titled “Workpackage Configuration (APN:2201).”

## 2. Prerequisites

- **Access:** User has permission to edit sequencing configuration.
- **Context:** You are in `[Aircraft] → [WP Sequencing]`, and the window title shows “Workpackage Configuration (APN:XXXX).”
- **Baseline:** Identify whether existing sequence type does not exist before proceeding, review all policies to avoid duplication.

## 3. Definitions

- **Tabs:** Navigation elements at the top of the window (e.g., `[Aircraft]`, `[WP Sequencing]`). These are not menus or data fields.
- **Name column:** Text field in the table where you type the label of the new sequencing type.
- **Ordering columns:** Dropdown menus labeled First Ordering, Second Ordering, Third Ordering, and Fourth Ordering.

## 4. Procedure

1. **Navigate to the correct tab**
	- Open APN 2201 Workpackage Configuration.
	- Click  the `[Aircraft]` tab, then select the `[WP Sequencing]` sub‑tab.

2. **Sequencing Type Creation**
	- Scroll to the bottom the the sequencing table.
	- Click into the first empty row under **Name** column.
	- Type the name for the sequencing type (e.g., `EventChain - Priority`).

3. **Ordering Configuration**
	- Click the dropdown in the **First Ordering** column.
	- Select the primary attribute (e.g., `Priority`, `Expected Date`, `Event Chain`).
	- Click the dropdown in the **Second Ordering** column.
	- Select the secondary attribute.
	- (Optional) Configure **Third Ordering** and **Fourth Ordering** if needed
4. **Ordering Configuration**
	- Click the dropdown in the First Ordering column.
	- Select the primary attribute (e.g., , , ).
	- Click the dropdown in the Second Ordering column.
	- Select the secondary attribute.
	- (Optional) Configure Third Ordering and Fourth Ordering if needed

[[WARNING]] This is a standard warning message.

> [!DANGER] 
> This is a standard danger message
	  
<!-- ::FIGURE caption="APN 2201 Workpackage Configuration" -->
![[Screenshot 2025-11-28 133129.png]]
**APN 2201 Workpackage Configuration**


## 5. References

- [[REF-2201_Workpackage_Configuration | REF-2201 Workpackage Configuration]]