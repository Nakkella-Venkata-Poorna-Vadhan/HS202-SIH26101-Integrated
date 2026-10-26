# MoSPI ACBP Structured Dataset: Data Dictionary & Schema

## Overview
This document defines the schema, field specifications, and provenance invariants for the structured **MoSPI Annual Capacity Building Plan (ACBP) FY 2026–27** datasets generated under Stage 2B.2.

- **Primary Course Dataset**: [`data/processed/acbp_courses.json`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/processed/acbp_courses.json) & [`.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/processed/acbp_courses.csv)
- **Nodal Directory Dataset**: [`data/processed/acbp_nodal_officers.json`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/processed/acbp_nodal_officers.json) & [`.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/processed/acbp_nodal_officers.csv)
- **KCM Candidate Mappings**: [`data/processed/acbp_kcm_candidate_mappings.json`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/processed/acbp_kcm_candidate_mappings.json)
- **Source Document ID**: `SRC-MOSPI-ACBP-2026-27`
- **Source PDF SHA-256**: `73ee47e6809982b63ffe928e95e86e4084d33865d325876e0cb9ff755a634205`
- **Provenance Classification**: `official_public`
- **Validation Status**: `pending_review`

---

## 1. ACBP Course Dataset Schema (`acbp_courses.json`)

| Field Name | Type | Permitted Null | Description & Validation Rule |
| :--- | :--- | :---: | :--- |
| `record_id` | String | No | Unique stable record identifier (`ACBP-CRS-001` to `ACBP-CRS-226`). |
| `interim_record_id` | String | No | Traceable identifier from interim table stage (`ACBP-P02-R01` to `ACBP-P12-R20`). |
| `cadre_role` | String | No | Official cadre/role title exactly as stated in Annexure I headers. |
| `course_name` | String | No | Official training course name recovered via OCR. |
| `competency_category` | String | No | Source category: strictly `Domain`, `Functional`, or `Behavioural`. |
| `duration` | String | No | Official duration string as printed (e.g. `00:46:21`, `01:10.00`). |
| `course_creator` | String | No | Training course provider/institution (e.g. `NeGD`, `CBC`, `DoPT`, `IIT Kanpur`). |
| `source_id` | String | No | Stable source register ID: `SRC-MOSPI-ACBP-2026-27`. |
| `source_page` | Integer | No | 1-indexed source PDF page number (range: `2` to `12`). |
| `source_row` | String | No | Source table serial number (or sequence index). |
| `provenance` | String | No | Fixed classification: `official_public`. |
| `validation_status` | String | No | Fixed verification flag: `pending_review`. |
| `raw_ocr_values` | Object | No | Verbatim raw values extracted from OCR prior to normalization. |
| `is_uncertain` | Boolean | No | Flag indicating whether any field contains OCR noise or low confidence. |
| `uncertainty_flags` | List[String] | No | Diagnostic list of reasons for uncertainty (e.g. `unconventional_duration_format`). |
| `review_notes` | String | No | Audit instructions or human verification directives. |

---

## 2. Division Nodal Officers Directory Schema (`acbp_nodal_officers.json`)

| Field Name | Type | Permitted Null | Description & Validation Rule |
| :--- | :--- | :---: | :--- |
| `record_id` | String | No | Unique stable record identifier (`ACBP-NODAL-001` to `ACBP-NODAL-030`). |
| `source_id` | String | No | Stable source register ID: `SRC-MOSPI-ACBP-2026-27`. |
| `source_page` | Integer | No | Fixed to page `13` (Annexure II). |
| `sr_no` | String | No | Serial number as printed in source notice (`1` to `30`). |
| `division` | String | No | Official MoSPI administrative division, zonal office, or institute unit. |
| `officer_name` | String | No | Full name of designated nodal officer. |
| `designation` | String | Yes | Official designation (blank if omitted in official notice printout). |
| `email` | String | No | Contact email address as printed in source. |
| `provenance` | String | No | Fixed classification: `official_public`. |
| `validation_status` | String | No | Fixed verification flag: `pending_review`. |
| `raw_ocr_values` | Object | No | Verbatim raw values extracted from OCR. |
| `is_uncertain` | Boolean | No | Flag indicating OCR noise in email or blank designation. |
| `uncertainty_flags` | List[String] | No | Diagnostic reasons (e.g. `email_ocr_noise`, `missing_or_blank_designation`). |
| `review_notes` | String | No | Directives for administrative confirmation. |

---

## 3. Candidate KCM Competency Mappings Schema (`acbp_kcm_candidate_mappings.json`)

| Field Name | Type | Permitted Null | Description & Validation Rule |
| :--- | :--- | :---: | :--- |
| `course_record_id` | String | No | Reference to `acbp_courses.json` `record_id`. |
| `cadre_role` | String | No | Target cadre designation. |
| `course_name` | String | No | Official course title. |
| `acbp_competency_category` | String | No | Category from source (`Domain`, `Functional`, `Behavioural`). |
| `candidate_kcm_competency_id` | String | Yes | KCM ID (`KCM-BEH-xx` or `KCM-FUNC-xx`), or `null` if unresolved. |
| `candidate_kcm_competency_name` | String | Yes | Official KCM name, or `null` if unresolved. |
| `candidate_kcm_competency_type` | String | Yes | KCM type (`behavioural` / `functional`), or `null` if unresolved. |
| `mapping_method` | String | No | Method: `exact_title_match`, `explicit_title_reference`, or `unresolved`. |
| `evidence_or_rationale` | String | No | Concrete source rationale supporting the mapping or stating non-resolution. |
| `source_references` | List[String] | No | Cross-document references to page and section. |
| `confidence` | Float | Yes | Score between `0.85` and `1.00` for explicit matches; `null` if unresolved. |
| `validation_status` | String | No | Fixed: `pending_review`. |
