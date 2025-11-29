---
document_id: STD-001
title: DTS NAMING CONVENTIONS AND FILE STRUCTURE STANDARDS
category: Standards
revision: 0
date_effective: 2025-11-26
author: Jason Grace
approver: Michael Osterhout
status: Draft
related_documents:
  - SOP-001 Workpackage Handling
  - REF-001 Folder Structure Guide
---

# 1. Purpose
To define standardized naming, file, and folder conventions for AMOS and DTS Scheduling systems to ensure consistency, traceability, and automation compatibility across all digital assets.

# 2. Scope
This document applies to all personnel generating, storing, or sharing digital records related to DTS Line Maintenance, including AMOS exports, SharePoint assets, and local work package archives.

# 3. General Standards
| Field | Standard | Example |
|-------|-----------|----------|
| Date Format | ISO 8601 | `2025-11-26` |
| Time Format | Zulu (UTC) | `2025-11-26T13:00Z` |
| Revision Tag | Two-digit rev counter | `rev01` |
| Customer Prefix | Uppercase IATA code | `DHK`, `CKS`, `21A` |
| File Extension | Based on output type | `.pdf`, `.xml`, `.xlsx` |

# 4. File Naming Schema
Use the following pattern for all exported or uploaded artifacts:

```
YYYYMMDD_AircraftReg_WorkOrder_Desc_rev##
```

**Example:**
```
20251126_GDHLM_WO181714_LMRReport_rev00.pdf
```

# 5. Folder Structure Schema
All work packages and reference materials must follow this directory layout:

```
/CVG145/
├─ Customer/
│  ├─ DHL/
│  │  └─ 2025/
│  │     ├─ 11_November/
│  │     │  ├─ G-DHLM/
│  │     │  │  ├─ WO_181714/
│  │     │  │  │  ├─ Form0117.pdf
│  │     │  │  │  ├─ LMR_1383.pdf
│  │     │  │  │  └─ Photos/
│  │     │  │  │     ├─ Engine_1.jpg
│  │     │  │  │     └─ Panel_2.jpg
│  │     │  │  └─ Logs/
│  │     │  │     └─ AMOS_Export.xml
│  │     │  └─ Summary/
│  │     │     └─ Daily_Report_20251126.xlsx
```

# 6. AMOS Export Standards
| Field | AMOS Element | Expected Format | Example |
|-------|---------------|-----------------|----------|
| Aircraft Registration | `aircraftRegistration` | Uppercase | `G-DHLM` |
| Work Order | `workOrderNumber` | Numeric | `181714` |
| Description | `description` | Title Case | `Hydraulic Leak Check` |

# 7. Version Control
All revisions must include:
- Updated revision number in filename  
- Metadata update in document header  
- Entry in `Document_Control_Log.xlsx`  

# 8. Responsibilities
| Role | Responsibility |
|------|----------------|
| Scheduler | Adheres to naming and folder standards when exporting files |
| Supervisor | Reviews compliance before archive or upload |
| Planner | Verifies that all work orders follow schema before AMOS import |

# 9. References
- SOP-001 Workpackage Handling  
- APP-001 Technical Appendix  
- SharePoint List: “CVG145 Workpackage Assets”

---

# 🔧 Pipeline Integration Example

```
/SOP_Publish_Pipeline/
│
├─ templates/
│   ├─ SOP_Template.xml
│   ├─ STD_Template.xml
│   ├─ REF_Template.xml
│   └─ APP_Template.xml
│
├─ drafts/
│   ├─ SOP_001_Workpackage_Handling.md
│   ├─ STD_001_Naming_Conventions.md
│   └─ REF_001_Folder_Structure.md
│
├─ output/
│   ├─ SOP_001_Workpackage_Handling.pdf
│   ├─ STD_001_Naming_Conventions.pdf
│   └─ REF_001_Folder_Structure.pdf
│
└─ scripts/
    └─ generate_doc.py
```

The `generate_doc.py` script reads Markdown headers, merges data into the XML template, applies Scribus layout styles, and exports version-controlled PDFs. All outputs maintain enterprise metadata, revision control, and uniform design standards.

