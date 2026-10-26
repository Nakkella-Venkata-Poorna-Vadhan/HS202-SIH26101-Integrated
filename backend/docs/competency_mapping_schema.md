# Competency Mapping Schema & Data Dictionary Specification

> **Document Status:** Technical Specification Baseline  
> **Milestone:** SIH26101 — Stage 3.1: Design the Competency Mapping Framework  
> **Related Datasets:**  
> - `data/processed/acbp_courses.json` (`SRC-MOSPI-ACBP-2026-27`)  
> - `data/processed/competencies_kcm.json` (`SRC-CBC-KCM-2024`)  
> - `data/processed/acbp_kcm_candidate_mappings.json` (Stage 2B.2 Interim Baseline)  
> **Author:** Antigravity AI & SIH26101 Engineering Team  

---

## 1. Schema Architecture & Design Principles

The Competency Mapping Schema provides an auditable, machine-verifiable relational bridge between the **MoSPI ACBP Course Catalogue** and the **Karmayogi Competency Model (KCM)**.

The schema adheres to five strict architectural principles:
1. **Relational Referencing:** Course references must resolve to valid `record_id` entries in `acbp_courses.json`. Competency references must resolve to valid `competency_id` entries in `competencies_kcm.json` (or be explicitly `null`).
2. **First-Class Nullability for Unresolved Records:** Unresolved relationships must be explicitly representable without placeholder strings (e.g. `candidate_kcm_competency_id = null`, not `"N/A"` or `"None"`).
3. **Mandatory Dual-Source Provenance:** Every mapping must maintain exact, 1-indexed document provenance for both the source course and the cited competency.
4. **Decoupled Confidence & Method:** Confidence scores cannot be arbitrary heuristic decimals. If confidence is assigned, its mathematical derivation and semantic meaning must be documented.
5. **Permanent Audit History:** Rejections, revisions, and status transitions must record reviewer identity, role, timestamp, and explicit rationale.

---

## 2. Comprehensive Field Specification

| Field Name | Data Type | Nullable | Permitted Values / Constraints | Description & Verification Invariants |
| :--- | :--- | :---: | :--- | :--- |
| `mapping_id` | String | No | Regex: `^MAP-ACBP-KCM-[0-9]{3,}$` | Stable unique mapping identifier (e.g., `MAP-ACBP-KCM-001`). Immutable primary key. |
| `course_record_id` | String | No | Regex: `^ACBP-CRS-[0-9]{3}$` | Foreign key resolving to `record_id` in `acbp_courses.json` (`ACBP-CRS-001` to `ACBP-CRS-226`). |
| `cadre_role` | String | No | Exact string match from `acbp_courses.json` | Denormalized cadre/role title for rapid filtering without secondary joins. |
| `course_name` | String | No | Exact string match from `acbp_courses.json` | Denormalized official course title as extracted from the ACBP source document. |
| `acbp_competency_category` | String | No | Enum: `["Domain", "Functional", "Behavioural"]` | Curricular classification as printed in Annexure I of the ACBP document. |
| `candidate_kcm_competency_id` | String | **Yes** | Regex: `^KCM-(BEH\|FUNC)-[0-9]{2}$` or `null` | Foreign key resolving to `competency_id` in `competencies_kcm.json`. Strictly `null` if unresolved. |
| `candidate_kcm_competency_name` | String | **Yes** | Exact string match from `competencies_kcm.json` or `null` | Denormalized official KCM competency name. Must match `candidate_kcm_competency_id`. |
| `candidate_kcm_subtheme` | String | **Yes** | String or `null` | Specific KCM sub-theme title from `behaviours` array in `competencies_kcm.json` (if applicable). |
| `candidate_kcm_competency_type` | String | **Yes** | Enum: `["behavioural", "functional", null]` | Standardized KCM competency type. Must match `candidate_kcm_competency_id`. |
| `mapping_type` | String | No | Enum: `["source_stated", "exact_title_reference", "curated_candidate", "model_suggested", "validated", "unresolved"]` | Canonical classification of the relationship concept (as defined in Framework Section 2). |
| `mapping_method` | String | No | Enum: `["author_statement", "verbatim_title_containment", "expert_curricular_review", "dense_semantic_similarity", "llm_evidence_extraction", "unresolved_no_match", "unresolved_domain_gap"]` | Specific operational technique used to propose or evaluate the relationship. |
| `evidence_or_rationale` | String | No | Non-empty string (min length: 20 chars) | Auditable rationale explaining the connection or detailing why the record remains unresolved. |
| `course_source_id` | String | No | Fixed: `"SRC-MOSPI-ACBP-2026-27"` | Source register identifier for the MoSPI ACBP document. |
| `course_source_page` | Integer | No | Range: `[2, 12]` | 1-indexed source PDF page number where course is listed. |
| `course_source_row` | String | No | String (e.g. `"1"`, `"17"`, `"H"`) | Source table row identifier as recorded in `acbp_courses.json`. |
| `kcm_source_id` | String | **Yes** | Fixed: `"SRC-CBC-KCM-2024"` or `null` | Source register identifier for the KCM document. `null` if unresolved. |
| `kcm_source_page_def` | Integer | **Yes** | Range: `[39, 106]` or `null` | 1-indexed PDF page of the KCM competency definition. `null` if unresolved. |
| `kcm_source_page_sub` | Integer | **Yes** | Range: `[40, 107]` or `null` | 1-indexed PDF page of the KCM sub-theme panel. `null` if unresolved. |
| `confidence_score` | Float | **Yes** | Range: `[0.0, 1.0]` or `null` | Methodologically defined score (e.g., semantic cosine similarity). Strictly `null` unless mathematically defined. |
| `confidence_metric` | String | **Yes** | Enum: `["cosine_similarity", "token_jaccard", "calibrated_posterior", null]` | Specific mathematical formulation of `confidence_score`. `null` if no score assigned. |
| `validation_status` | String | No | Enum: `["pending_review", "validated", "rejected", "unresolved"]` | Formal institutional verification flag. |
| `reviewer_id` | String | **Yes** | String or `null` | Institutional ID or username of the reviewer who signed off or rejected the mapping. |
| `reviewer_role` | String | **Yes** | String or `null` | Official capacity of reviewer (e.g., `"MoSPI Nodal Officer"`, `"NSSTA Faculty"`, `"Curriculum SME"`). |
| `reviewed_at` | String | **Yes** | ISO-8601 UTC timestamp or `null` | Timestamp when the validation status was formally updated. |
| `reviewer_notes` | String | No | String (empty string permitted) | Reviewer notes, directives, or caveats regarding syllabus coverage and cadre relevance. |
| `creation_method` | String | No | Enum: `["automated_pipeline", "human_expert", "hybrid_review"]` | Entity and process that initially generated the mapping record. |
| `pipeline_version` | String | No | Semantic versioning string (e.g., `"3.1.0"`) | Pipeline release tag under which the record was generated or updated. |
| `created_at` | String | No | ISO-8601 UTC timestamp | Record generation timestamp. |
| `source_hash_course` | String | No | SHA-256 hex string (64 characters) | Cryptographic hash of `data/processed/acbp_courses.json`. |
| `source_hash_kcm` | String | No | SHA-256 hex string (64 characters) | Cryptographic hash of `data/processed/competencies_kcm.json`. |

---

## 3. Mandatory vs. Permitted Null Fields by Mapping Type

Not all fields are valid for every mapping type. The matrix below defines field applicability across the six canonical concepts:

| Field Name | `source_stated` | `exact_title_reference` | `curated_candidate` | `model_suggested` | `validated` | `unresolved` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `mapping_id` | **M** | **M** | **M** | **M** | **M** | **M** |
| `course_record_id` | **M** | **M** | **M** | **M** | **M** | **M** |
| `cadre_role` | **M** | **M** | **M** | **M** | **M** | **M** |
| `course_name` | **M** | **M** | **M** | **M** | **M** | **M** |
| `acbp_competency_category` | **M** | **M** | **M** | **M** | **M** | **M** |
| `candidate_kcm_competency_id` | **M** | **M** | **M** | **M** | **M** | **Forbidden (`null`)** |
| `candidate_kcm_competency_name` | **M** | **M** | **M** | **M** | **M** | **Forbidden (`null`)** |
| `candidate_kcm_subtheme` | Optional | Optional | Optional | Optional | Optional | **Forbidden (`null`)** |
| `candidate_kcm_competency_type` | **M** | **M** | **M** | **M** | **M** | **Forbidden (`null`)** |
| `mapping_type` | **M** | **M** | **M** | **M** | **M** | **M** |
| `mapping_method` | **M** | **M** | **M** | **M** | **M** | **M** |
| `evidence_or_rationale` | **M** | **M** | **M** | **M** | **M** | **M** |
| `course_source_id` | **M** | **M** | **M** | **M** | **M** | **M** |
| `course_source_page` | **M** | **M** | **M** | **M** | **M** | **M** |
| `course_source_row` | **M** | **M** | **M** | **M** | **M** | **M** |
| `kcm_source_id` | **M** | **M** | **M** | **M** | **M** | **Forbidden (`null`)** |
| `kcm_source_page_def` | **M** | **M** | **M** | **M** | **M** | **Forbidden (`null`)** |
| `kcm_source_page_sub` | **M** | **M** | **M** | **M** | **M** | **Forbidden (`null`)** |
| `confidence_score` | Optional | **Forbidden (`null`)** | Optional | **M** | Optional | **Forbidden (`null`)** |
| `confidence_metric` | Optional | **Forbidden (`null`)** | Optional | **M** | Optional | **Forbidden (`null`)** |
| `validation_status` | `pending_review` | `pending_review` | `pending_review` | `pending_review` | **`validated`** | **`unresolved`** |
| `reviewer_id` | Optional | Optional | Optional | Optional | **M** | Optional |
| `reviewer_role` | Optional | Optional | Optional | Optional | **M** | Optional |
| `reviewed_at` | Optional | Optional | Optional | Optional | **M** | Optional |
| `reviewer_notes` | Optional | Optional | Optional | Optional | **M** | Optional |
| `creation_method` | **M** | **M** | **M** | **M** | **M** | **M** |
| `pipeline_version` | **M** | **M** | **M** | **M** | **M** | **M** |
| `created_at` | **M** | **M** | **M** | **M** | **M** | **M** |
| `source_hash_course` | **M** | **M** | **M** | **M** | **M** | **M** |
| `source_hash_kcm` | **M** | **M** | **M** | **M** | **M** | **M** |

*Legend:*  
- **M**: Mandatory (must be non-null and satisfy schema validation rules).  
- **Forbidden (`null`)**: Must strictly be serialized as `null` (or empty string in CSV).  
- **Optional**: Permitted to be `null` if data is unavailable or not applicable.

---

## 4. Formal JSON Schema Specification (Draft 2020-12)

The JSON Schema definition below provides machine-verifiable constraints for mapping datasets:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://mospi.gov.in/sih26101/schemas/competency_mapping.schema.json",
  "title": "MoSPI ACBP to Karmayogi Competency Model Mapping Schema",
  "description": "Defines the auditable relational mapping record between MoSPI ACBP courses and CBC KCM competencies.",
  "type": "object",
  "required": [
    "dataset_name",
    "course_source_id",
    "kcm_source_id",
    "pipeline_version",
    "generation_timestamp",
    "total_courses_evaluated",
    "mapped_records_count",
    "unresolved_records_count",
    "mappings"
  ],
  "properties": {
    "dataset_name": { "type": "string" },
    "course_source_id": { "type": "string", "const": "SRC-MOSPI-ACBP-2026-27" },
    "kcm_source_id": { "type": "string", "const": "SRC-CBC-KCM-2024" },
    "pipeline_version": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "generation_timestamp": { "type": "string", "format": "date-time" },
    "total_courses_evaluated": { "type": "integer", "const": 226 },
    "mapped_records_count": { "type": "integer", "minimum": 0 },
    "unresolved_records_count": { "type": "integer", "minimum": 0 },
    "mappings": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/mapping_record"
      }
    }
  },
  "$defs": {
    "mapping_record": {
      "type": "object",
      "required": [
        "mapping_id",
        "course_record_id",
        "cadre_role",
        "course_name",
        "acbp_competency_category",
        "candidate_kcm_competency_id",
        "candidate_kcm_competency_name",
        "candidate_kcm_competency_type",
        "mapping_type",
        "mapping_method",
        "evidence_or_rationale",
        "course_source_id",
        "course_source_page",
        "course_source_row",
        "validation_status",
        "creation_method",
        "pipeline_version",
        "created_at",
        "source_hash_course",
        "source_hash_kcm"
      ],
      "properties": {
        "mapping_id": {
          "type": "string",
          "pattern": "^MAP-ACBP-KCM-[0-9]{3,}$"
        },
        "course_record_id": {
          "type": "string",
          "pattern": "^ACBP-CRS-[0-9]{3}$"
        },
        "cadre_role": { "type": "string" },
        "course_name": { "type": "string" },
        "acbp_competency_category": {
          "type": "string",
          "enum": ["Domain", "Functional", "Behavioural"]
        },
        "candidate_kcm_competency_id": {
          "type": ["string", "null"],
          "pattern": "^KCM-(BEH|FUNC)-[0-9]{2}$"
        },
        "candidate_kcm_competency_name": { "type": ["string", "null"] },
        "candidate_kcm_subtheme": { "type": ["string", "null"] },
        "candidate_kcm_competency_type": {
          "type": ["string", "null"],
          "enum": ["behavioural", "functional", null]
        },
        "mapping_type": {
          "type": "string",
          "enum": [
            "source_stated",
            "exact_title_reference",
            "curated_candidate",
            "model_suggested",
            "validated",
            "unresolved"
          ]
        },
        "mapping_method": {
          "type": "string",
          "enum": [
            "author_statement",
            "verbatim_title_containment",
            "expert_curricular_review",
            "dense_semantic_similarity",
            "llm_evidence_extraction",
            "unresolved_no_match",
            "unresolved_domain_gap"
          ]
        },
        "evidence_or_rationale": { "type": "string", "minLength": 20 },
        "course_source_id": { "type": "string", "const": "SRC-MOSPI-ACBP-2026-27" },
        "course_source_page": { "type": "integer", "minimum": 2, "maximum": 12 },
        "course_source_row": { "type": "string" },
        "kcm_source_id": { "type": ["string", "null"] },
        "kcm_source_page_def": { "type": ["integer", "null"], "minimum": 39, "maximum": 106 },
        "kcm_source_page_sub": { "type": ["integer", "null"], "minimum": 40, "maximum": 107 },
        "confidence_score": { "type": ["number", "null"], "minimum": 0.0, "maximum": 1.0 },
        "confidence_metric": {
          "type": ["string", "null"],
          "enum": ["cosine_similarity", "token_jaccard", "calibrated_posterior", null]
        },
        "validation_status": {
          "type": "string",
          "enum": ["pending_review", "validated", "rejected", "unresolved"]
        },
        "reviewer_id": { "type": ["string", "null"] },
        "reviewer_role": { "type": ["string", "null"] },
        "reviewed_at": { "type": ["string", "null"], "format": "date-time" },
        "reviewer_notes": { "type": "string" },
        "creation_method": {
          "type": "string",
          "enum": ["automated_pipeline", "human_expert", "hybrid_review"]
        },
        "pipeline_version": { "type": "string" },
        "created_at": { "type": "string", "format": "date-time" },
        "source_hash_course": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "source_hash_kcm": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
      }
    }
  }
}
```

---

## 5. Serialization & Tabular CSV Parity Rules

To maintain exact 1-to-1 parity between JSON records and CSV tabular releases (standard in government auditing), the following formatting rules apply to `data/processed/acbp_kcm_mappings.csv`:

1. **Header Order:** Exactly matches the property sequence defined in Section 2.
2. **Null Representation:** `null` values serialize as empty strings `""` in CSV.
3. **Encoding:** Explicit UTF-8 with RFC 4180 standard escaping for text containing quotes, commas, or newlines.
4. **Devanagari & IAST Characters:** Verbatim UTF-8 preservation for terms like *Sahakaryata*, *Sadharanikarana*, *Rajadharma*, *Seva-Bhava*.
5. **Float Precision:** If `confidence_score` is present, it must be formatted to exactly 4 decimal places (e.g. `0.8521`).
