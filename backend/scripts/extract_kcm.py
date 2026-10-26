"""
SIH26101 - Stage 2A: Karmayogi Competency Model (KCM) Extraction Engine
======================================================================
Extracts official Behavioural and Functional competencies, definitions, and
associated behaviours/sub-themes from the KCM document (data/raw/KCM-Output_RestructuredOct17.pdf).

Strict Data Integrity Rules:
1. Extract only competencies explicitly supported by the KCM document.
2. Distinguish behavioural and functional competencies according to source.
3. Domain competencies are outside KCM scope (never invented).
4. Do not invent descriptions, behaviours, or level scales.
5. All 34 competencies are marked 'pending_review' with source provenance 'official_public'.
6. Export to data/processed/competencies_kcm.json, data/processed/competencies_kcm.csv,
   and docs/kcm_extraction_notes.md.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PDF_PATH = PROJECT_ROOT / "data" / "raw" / "KCM-Output_RestructuredOct17.pdf"
INTERIM_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "SRC-CBC-KCM-2024.json"
PROCESSED_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
PROCESSED_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.csv"
DOCS_NOTES_PATH = PROJECT_ROOT / "docs" / "kcm_extraction_notes.md"

SOURCE_ID = "SRC-CBC-KCM-2024"
PROVENANCE = "official_public"
VALIDATION_STATUS = "pending_review"

REQUIRED_FIELDS = [
    "competency_id",
    "competency_name",
    "competency_type",
    "description",
    "behaviours",
    "level_information",
    "source_id",
    "source_page",
    "provenance",
    "validation_status",
    "extraction_notes",
]

ALLOWED_TYPES = {"behavioural", "functional"}


@dataclass
class CompetencyRecord:
    competency_id: str
    competency_name: str
    competency_type: str
    description: str
    behaviours: List[str]
    level_information: Optional[str]
    source_id: str
    source_page: List[int]
    provenance: str
    validation_status: str
    extraction_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Comprehensive catalog of all 34 competencies in KCM with their source page pairs and sub-themes
COMPETENCY_DEFINITIONS = [
    # -------------------------------------------------------------------------
    # BEHAVIOURAL COMPETENCIES: CORE (1 to 8)
    # -------------------------------------------------------------------------
    {
        "id": "KCM-BEH-01",
        "name": "Self-Awareness",
        "type": "behavioural",
        "category": "Core Behavioural Competency",
        "p_def": 39,
        "p_sub": 40,
        "notes": "Core competency mapped to virtue Svādhyāya (Self). Defines 4 sub-themes.",
    },
    {
        "id": "KCM-BEH-02",
        "name": "Personal Effectiveness",
        "type": "behavioural",
        "category": "Core Behavioural Competency",
        "p_def": 41,
        "p_sub": 42,
        "notes": "Core competency mapped to virtue Svādhyāya (Self). Defines 3 sub-themes.",
    },
    {
        "id": "KCM-BEH-03",
        "name": "Solution Orientation",
        "type": "behavioural",
        "category": "Core Behavioural Competency",
        "p_def": 43,
        "p_sub": 44,
        "notes": "Core competency mapped to virtue Svādhyāya (Self). Defines 3 sub-themes.",
    },
    {
        "id": "KCM-BEH-04",
        "name": "Communication",
        "type": "behavioural",
        "category": "Core Behavioural Competency",
        "p_def": 45,
        "p_sub": 46,
        "notes": "Core competency mapped to virtue Sahakāryatā (Team/Collaboration). Defines 4 sub-themes.",
    },
    {
        "id": "KCM-BEH-05",
        "name": "Outcome Orientation",
        "type": "behavioural",
        "category": "Core Behavioural Competency",
        "p_def": 47,
        "p_sub": 48,
        "notes": "Core competency mapped to virtue Sahakāryatā (Team/Collaboration). Defines 4 sub-themes.",
    },
    {
        "id": "KCM-BEH-06",
        "name": "Collaboration",
        "type": "behavioural",
        "category": "Core Behavioural Competency",
        "p_def": 49,
        "p_sub": 50,
        "notes": "Core competency mapped to virtue Sahakāryatā (Team/Collaboration). Defines 3 sub-themes.",
    },
    {
        "id": "KCM-BEH-07",
        "name": "Service Orientation",
        "type": "behavioural",
        "category": "Core Behavioural Competency",
        "p_def": 51,
        "p_sub": 52,
        "notes": "Core competency mapped to virtue Svadharma (Citizen). Defines 3 sub-themes.",
    },
    {
        "id": "KCM-BEH-08",
        "name": "Operational Excellence",
        "type": "behavioural",
        "category": "Core Behavioural Competency",
        "p_def": 53,
        "p_sub": 54,
        "notes": "Core competency mapped to virtue Rājyakarma (Workplace/Systems). Defines 4 sub-themes.",
    },
    # -------------------------------------------------------------------------
    # BEHAVIOURAL COMPETENCIES: LEADERSHIP (9 to 13)
    # -------------------------------------------------------------------------
    {
        "id": "KCM-BEH-09",
        "name": "Creativity & Innovation",
        "type": "behavioural",
        "category": "Leadership Behavioural Competency",
        "p_def": 55,
        "p_sub": 56,
        "notes": "Leadership competency mapped to virtue Svādhyāya. Defines 2 sub-themes.",
    },
    {
        "id": "KCM-BEH-10",
        "name": "Strategic Leadership",
        "type": "behavioural",
        "category": "Leadership Behavioural Competency",
        "p_def": 57,
        "p_sub": 58,
        "notes": "Leadership competency mapped to virtue Svadharma. Defines 4 sub-themes.",
    },
    {
        "id": "KCM-BEH-11",
        "name": "Collaborative Leadership",
        "type": "behavioural",
        "category": "Leadership Behavioural Competency",
        "p_def": 59,
        "p_sub": 60,
        "notes": "Leadership competency mapped to virtue Sahakāryatā. Defines 2 sub-themes.",
    },
    {
        "id": "KCM-BEH-12",
        "name": "Team Leadership",
        "type": "behavioural",
        "category": "Leadership Behavioural Competency",
        "p_def": 61,
        "p_sub": 62,
        "notes": "Leadership competency mapped to virtue Sahakāryatā. Defines 3 sub-themes.",
    },
    {
        "id": "KCM-BEH-13",
        "name": "Decision Making",
        "type": "behavioural",
        "category": "Leadership Behavioural Competency",
        "p_def": 63,
        "p_sub": 64,
        "notes": "Leadership competency mapped to virtue Rājyakarma. Defines 2 sub-themes.",
    },
    # -------------------------------------------------------------------------
    # FUNCTIONAL COMPETENCIES (1 to 21)
    # -------------------------------------------------------------------------
    {
        "id": "KCM-FUNC-01",
        "name": "Citizen Centricity",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 66,
        "p_sub": 67,
        "notes": "Functional competency mapped to Svadharma. Defines 3 sub-themes.",
    },
    {
        "id": "KCM-FUNC-02",
        "name": "Policy Architecture",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 68,
        "p_sub": 69,
        "notes": "Functional competency mapped to Svadharma. Defines 4 sub-themes.",
    },
    {
        "id": "KCM-FUNC-03",
        "name": "Cabinet Note Preparation",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 70,
        "p_sub": 71,
        "notes": "Functional competency mapped to Rājyakarma. Defines 2 sub-themes.",
    },
    {
        "id": "KCM-FUNC-04",
        "name": "Govt Program Formulation",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 72,
        "p_sub": 73,
        "notes": "Heading reads 'Govt Program Formulation' on page 72; listed as 'Government Program Formulation' on summary pages 29 and 34. Defines 4 sub-themes.",
    },
    {
        "id": "KCM-FUNC-05",
        "name": "Project Management",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 74,
        "p_sub": 75,
        "notes": "Functional competency mapped to Rājyakarma. Defines 4 sub-themes.",
    },
    {
        "id": "KCM-FUNC-06",
        "name": "Public Procurement (GFR)",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 76,
        "p_sub": 77,
        "notes": "Functional competency mapped to Rājyakarma. Defines 4 sub-themes.",
    },
    {
        "id": "KCM-FUNC-07",
        "name": "Material Management (GFR)",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 78,
        "p_sub": 79,
        "notes": "Functional competency mapped to Rājyakarma. Defines 2 sub-themes.",
    },
    {
        "id": "KCM-FUNC-08",
        "name": "Monitoring & Evaluation",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 80,
        "p_sub": 81,
        "notes": "Functional competency mapped to Rājyakarma. Defines 2 sub-themes.",
    },
    {
        "id": "KCM-FUNC-09",
        "name": "Financial Management",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 82,
        "p_sub": 83,
        "notes": "Functional competency mapped to Rājyakarma. Defines 4 sub-themes.",
    },
    {
        "id": "KCM-FUNC-10",
        "name": "Digital Fluency",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 84,
        "p_sub": 85,
        "notes": "Functional competency mapped to Rājyakarma. Defines 2 detailed sub-theme panels on page 85.",
    },
    {
        "id": "KCM-FUNC-11",
        "name": "Data Analytics",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 86,
        "p_sub": 87,
        "notes": "Functional competency mapped to Rājyakarma. Defines 4 sub-themes.",
    },
    {
        "id": "KCM-FUNC-12",
        "name": "Establishment & HR",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 88,
        "p_sub": 89,
        "notes": "Functional competency mapped to Rājyakarma. Defines 5 sub-themes.",
    },
    {
        "id": "KCM-FUNC-13",
        "name": "Office Management",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 90,
        "p_sub": 91,
        "notes": "Verbatim definition text matches Handling Parliamentary Matters (p92) and Handling RTI Matters (p94) due to source document authoring reuse of Central Secretariat Manual of Office Procedures (CSMOP) text. Sub-themes on p91 are distinct (5 sub-themes).",
    },
    {
        "id": "KCM-FUNC-14",
        "name": "Handling Parliamentary Matters",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 92,
        "p_sub": 93,
        "notes": "Verbatim definition text is identical to Office Management (p90) in the original document. Defines 2 distinct sub-themes on p93.",
    },
    {
        "id": "KCM-FUNC-15",
        "name": "Handling RTI Matters",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 94,
        "p_sub": 95,
        "notes": "Verbatim definition text is identical to Office Management (p90) in the original document. Defines 2 distinct sub-themes on p95.",
    },
    {
        "id": "KCM-FUNC-16",
        "name": "Grievance Redressal",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 96,
        "p_sub": 97,
        "notes": "Functional competency mapped to Svadharma. Defines 2 sub-themes.",
    },
    {
        "id": "KCM-FUNC-17",
        "name": "Vigilance Administration",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 98,
        "p_sub": 99,
        "notes": "Header on sub-theme page reads 'Vigilance Administration Matters Sub-Themes'. Defines 5 sub-themes.",
    },
    {
        "id": "KCM-FUNC-18",
        "name": "Litigation Management",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 100,
        "p_sub": 101,
        "notes": "Functional competency mapped to Rājyakarma. Defines 3 sub-themes.",
    },
    {
        "id": "KCM-FUNC-19",
        "name": "Information & Communication Management",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 102,
        "p_sub": 103,
        "notes": "Functional competency mapped to Sahakāryatā. Defines 3 sub-themes.",
    },
    {
        "id": "KCM-FUNC-20",
        "name": "Change Management",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 104,
        "p_sub": 105,
        "notes": "Functional competency mapped to Rājyakarma. Defines 3 sub-themes.",
    },
    {
        "id": "KCM-FUNC-21",
        "name": "Administration Matters",
        "type": "functional",
        "category": "Functional Competency",
        "p_def": 106,
        "p_sub": 107,
        "notes": "Source anomaly: Sub-theme page 107 errantly carries the header title 'Change Management Sub-Themes' instead of 'Administration Matters Sub-Themes'. Content details 4 sub-themes (Allowances, Leave/Travel, Misc, Official Language).",
    },
]


def extract_definition_from_page(page: pymupdf.Page) -> str:
    """Extract official definition paragraph from the definition page."""
    text = page.get_text("text")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if "Definition" not in lines:
        raise ValueError("Definition marker not found on page.")
    def_idx = lines.index("Definition")
    remaining = lines[def_idx + 1 :]
    def_lines = []
    for l in remaining:
        # Stop at document footer / page decoration markers
        if (
            "Competencies with Definitions" in l
            or l in ["C", "O", "M", "P", "E", "T", "N", "Y", "L", "D"]
            or l.isdigit()
            or l == "Karmayogī"
        ):
            break
        def_lines.append(l)
    return " ".join(def_lines).strip()


def parse_subthemes_for_page(page: pymupdf.Page, comp_id: str) -> List[str]:
    """
    Extract sub-theme titles and their associated behavioural indicator descriptions.
    Uses typography (font family, weight, and size) and column-aligned horizontal bounds
    to correctly assemble multi-line titles and pair each sub-theme header with its description.
    Avoids geometric midpoint clustering that previously merged multi-title banners into
    a single column or created sentence-fragment pseudo-titles.
    """
    d = page.get_text("dict")

    title_lines: List[Tuple[Tuple[float, float, float, float], str]] = []
    desc_lines: List[Tuple[Tuple[float, float, float, float], str]] = []

    for b in d.get("blocks", []):
        if "lines" not in b:
            continue
        for line in b["lines"]:
            text = "".join(s["text"] for s in line["spans"]).strip()
            if not text:
                continue
            if "C O M P E T E N C Y" in text or "Karmayogī" in text or "Sub-Themes" in text:
                continue
            if text.isdigit() and len(text) <= 3:
                continue

            bbox = line["bbox"]
            if bbox[1] < 300:  # skip running headers
                continue

            fonts = [s["font"] for s in line["spans"]]
            sizes = [s["size"] for s in line["spans"]]

            is_title = any("Bold" in f for f in fonts) and any(sz >= 30.0 for sz in sizes)
            if is_title:
                title_lines.append((bbox, text))
            else:
                desc_lines.append((bbox, text))

    title_lines = sorted(title_lines, key=lambda item: (item[0][0], item[0][1]))

    # Cluster title lines into distinct columns by their left margin (x0) alignment
    columns: List[Dict[str, Any]] = []
    for bbox, text in title_lines:
        placed = False
        line_x0 = bbox[0]
        line_x1 = bbox[2]
        for col in columns:
            col_x0 = col["x0"]
            col_x1 = col["x1"]
            # Multi-line titles in the same column share the same left margin within 35 pt
            if abs(line_x0 - col_x0) < 35:
                col["title_lines"].append((bbox, text))
                col["x0"] = min(col["x0"], line_x0)
                col["x1"] = max(col["x1"], line_x1)
                placed = True
                break
        if not placed:
            columns.append({
                "title_lines": [(bbox, text)],
                "x0": line_x0,
                "x1": line_x1,
            })

    # Sort columns left-to-right
    columns = sorted(columns, key=lambda c: c["x0"])

    # Assemble titles
    for col in columns:
        col["title_lines"] = sorted(col["title_lines"], key=lambda item: item[0][1])
        title = " ".join(item[1] for item in col["title_lines"])
        col["title"] = " ".join(title.split())
        col["desc_lines"] = []

    # Associate description lines to closest column by horizontal center
    for bbox, text in desc_lines:
        line_x_center = (bbox[0] + bbox[2]) / 2.0
        best_col = None
        min_dist = float("inf")
        for col in columns:
            c_center = (col["x0"] + col["x1"]) / 2.0
            dist = abs(line_x_center - c_center)
            if dist < min_dist:
                min_dist = dist
                best_col = col
        if best_col is not None:
            best_col["desc_lines"].append((bbox, text))

    # Format behaviours as List[str] with format "{title}: {description}"
    behaviours: List[str] = []
    for col in columns:
        col["desc_lines"] = sorted(col["desc_lines"], key=lambda item: (item[0][1], item[0][0]))
        desc = " ".join(item[1] for item in col["desc_lines"])
        desc = " ".join(desc.split())
        behaviours.append(f"{col['title']}: {desc}")

    return behaviours


def extract_all_kcm_competencies(pdf_path: Path) -> List[CompetencyRecord]:
    """Execute complete extraction for all 34 KCM competencies."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"KCM PDF not found at: {pdf_path}")

    doc = pymupdf.open(str(pdf_path))
    records: List[CompetencyRecord] = []

    for meta in COMPETENCY_DEFINITIONS:
        cid = meta["id"]
        cname = meta["name"]
        ctype = meta["type"]
        p_def = meta["p_def"]
        p_sub = meta["p_sub"]

        # 1. Extract definition
        page_def = doc[p_def - 1]
        definition = extract_definition_from_page(page_def)

        # 2. Extract sub-themes & behaviours
        page_sub = doc[p_sub - 1]
        behaviours = parse_subthemes_for_page(page_sub, cid)

        # Level information: KCM source does NOT define explicit level scales
        level_info = None

        record = CompetencyRecord(
            competency_id=cid,
            competency_name=cname,
            competency_type=ctype,
            description=definition,
            behaviours=behaviours,
            level_information=level_info,
            source_id=SOURCE_ID,
            source_page=[p_def, p_sub],
            provenance=PROVENANCE,
            validation_status=VALIDATION_STATUS,
            extraction_notes=meta["notes"],
        )
        records.append(record)

    doc.close()
    return records


def validate_records(records: List[CompetencyRecord]) -> List[str]:
    """Run comprehensive validation checks against extracted competency records."""
    errors: List[str] = []
    seen_ids = set()

    for r in records:
        # Check required fields
        for f in REQUIRED_FIELDS:
            val = getattr(r, f)
            if f != "level_information" and (val is None or (isinstance(val, (str, list)) and len(val) == 0)):
                errors.append(f"[{r.competency_id}] Missing required field: '{f}'")

        # Unique ID
        if r.competency_id in seen_ids:
            errors.append(f"Duplicate competency_id: {r.competency_id}")
        seen_ids.add(r.competency_id)

        # Allowed competency type
        if r.competency_type not in ALLOWED_TYPES:
            errors.append(f"[{r.competency_id}] Invalid competency_type: '{r.competency_type}'")

        # Non-empty name
        if not r.competency_name.strip():
            errors.append(f"[{r.competency_id}] Competency name is empty.")

        # Valid source ID
        if r.source_id != SOURCE_ID:
            errors.append(f"[{r.competency_id}] Invalid source_id: '{r.source_id}'")

        # Valid page numbers
        for p in r.source_page:
            if not (1 <= p <= 107):
                errors.append(f"[{r.competency_id}] Invalid page number: {p}")

    return errors


def save_dataset(records: List[CompetencyRecord], json_path: Path, csv_path: Path) -> None:
    """Serialize records to JSON and CSV formats."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Save JSON
    raw_dicts = [r.to_dict() for r in records]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_dicts, f, indent=2, ensure_ascii=False)

    # 2. Save CSV
    fieldnames = REQUIRED_FIELDS
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            row = r.to_dict()
            # Serialize list fields as valid JSON strings for unambiguous CSV representation
            row["behaviours"] = json.dumps(row["behaviours"], ensure_ascii=False)
            row["source_page"] = json.dumps(row["source_page"])
            row["level_information"] = "" if row["level_information"] is None else row["level_information"]
            writer.writerow(row)


def generate_notes_markdown(records: List[CompetencyRecord], output_path: Path) -> None:
    """Generate comprehensive extraction notes documentation."""
    beh_count = sum(1 for r in records if r.competency_type == "behavioural")
    func_count = sum(1 for r in records if r.competency_type == "functional")
    total_behaviours = sum(len(r.behaviours) for r in records)

    lines = [
        "# Karmayogi Competency Model (KCM) — Extraction Notes & Review Report",
        "",
        "## 1. Executive Summary",
        f"- **Source Document:** `data/raw/KCM-Output_RestructuredOct17.pdf`",
        f"- **Stable Source ID:** `{SOURCE_ID}`",
        f"- **Total Competencies Extracted:** {len(records)}",
        f"  - **Behavioural Competencies:** {beh_count} (8 Core + 5 Leadership)",
        f"  - **Functional Competencies:** {func_count}",
        f"- **Total Sub-Themes / Behaviours Extracted:** {total_behaviours}",
        f"- **Explicit Competency Levels Defined in Source:** **None** (Explicitly confirmed)",
        f"- **Validation Status:** All records marked `{VALIDATION_STATUS}`",
        "",
        "---",
        "",
        "## 2. Structure and Organization of the Source Document",
        "",
        "The Karmayogi Competency Model (KCM) is structured as follows:",
        "1. **Core Virtues (Guṇas):** The foundational philosophical framework defines four virtues:",
        "   - *Svādhyāya* (Self)",
        "   - *Sahakāryatā* (Team / Collaboration)",
        "   - *Rājyakarma* (Workplace / Systems)",
        "   - *Svadharma* (Citizen / Public Good)",
        "2. **Three Spheres of Competency:**",
        "   - **Behavioural Competencies:** Key traits expected across all civil service roles.",
        "   - **Functional Competencies:** Cross-cutting knowledge and skills common across ministries.",
        "   - **Domain Competencies:** Explicitly declared as **OUTSIDE THE SCOPE** of KCM (Page 4, Page 24). In accordance with data integrity rules, no domain competencies were fabricated.",
        "3. **Two-Page Layout Convention in Annexures (Pages 38 to 107):**",
        "   - **Odd Page (Definition):** Full competency title, official Definition paragraph, and category.",
        "   - **Even Page (Sub-Themes):** Sub-theme titles and detailed behavioural indicator statements.",
        "",
        "---",
        "",
        "## 3. Explicit Competency Level Scale Findings",
        "",
        "> [!IMPORTANT]",
        "> **Finding on Competency Levels:**",
        "> The KCM source PDF does **NOT** define graded proficiency levels (e.g., Level 1 to 5, Beginner, Intermediate, Advanced).",
        "> While occasional descriptive phrases like 'highest level of proficiency' appear in descriptive text, there is no level hierarchy or scale.",
        "> In strict compliance with extraction rules ('Do not invent descriptions, behaviours, competency levels or assessment criteria'), `level_information` is set to `null` across all records.",
        "",
        "---",
        "",
        "## 4. Source Layout Anomalies & Extraction Notes",
        "",
        "| Competency ID | Competency Name | Source Pages | Anomaly / Layout Note |",
        "| :--- | :--- | :--- | :--- |",
        "| `KCM-FUNC-04` | Govt Program Formulation | 72, 73 | Definition heading reads `'Govt Program Formulation'`, while summary pages (p29, p34) read `'Government Program Formulation'`. The verbatim title from the definition page was retained. |",
        "| `KCM-FUNC-05` | Project Management | 74, 75 | Summary page 30 lists 3 bullets (`Project Planning`, `Project Implementation`, `Project Evaluation & Monitoring`). Detailed Annexure page 75 presents 4 distinct panels (`Project Planning`, `Project Implementation`, `Project Evaluation`, `Project KPIs Monitoring`). All 4 distinct source panels were preserved. |",
        "| `KCM-FUNC-13` | Office Management | 90, 91 | Definition text on page 90 is identical to pages 92 and 94 due to source document authoring reuse of Central Secretariat Manual of Office Procedures (CSMOP) text. Sub-themes on page 91 are distinct. |",
        "| `KCM-FUNC-14` | Handling Parliamentary Matters | 92, 93 | Definition text on page 92 is identical to Office Management (page 90). The 2 sub-themes on page 93 are distinct. |",
        "| `KCM-FUNC-15` | Handling RTI Matters | 94, 95 | Definition text on page 94 is identical to Office Management (page 90). The 2 sub-themes on page 95 are distinct. |",
        "| `KCM-FUNC-21` | Administration Matters | 106, 107 | **Document Header Error:** Page 107 errantly carries the header title `'Change Management Sub-Themes'` copied from page 105. However, the sub-themes listed are Allowances & Reimbursements, Leave & Travel, Misc Matters, and Official Language, matching Administration Matters. |",
        "",
        "---",
        "",
        "## 5. Ingested Competencies Inventory",
        "",
        "| ID | Competency Name | Type | Sub-Themes Count | Source Pages | Status |",
        "| :--- | :--- | :--- | :---: | :---: | :---: |",
    ]

    for r in records:
        lines.append(
            f"| `{r.competency_id}` | {r.competency_name} | `{r.competency_type}` | {len(r.behaviours)} | `{r.source_page}` | `{r.validation_status}` |"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def run_kcm_extraction() -> int:
    """CLI runner function for KCM competency extraction."""
    print("=" * 80)
    print("SIH26101 — Stage 2A: Karmayogi Competency Model (KCM) Extraction Pipeline")
    print("=" * 80)
    print(f"Source PDF  : {RAW_PDF_PATH.resolve()}")
    print(f"Output JSON : {PROCESSED_JSON_PATH.resolve()}")
    print(f"Output CSV  : {PROCESSED_CSV_PATH.resolve()}")
    print(f"Notes Doc   : {DOCS_NOTES_PATH.resolve()}")
    print("-" * 80)

    print("[1/4] Extracting competencies from KCM source PDF...")
    records = extract_all_kcm_competencies(RAW_PDF_PATH)
    print(f"  Extracted {len(records)} competencies.")

    print("[2/4] Validating extracted records...")
    val_errors = validate_records(records)
    if val_errors:
        print("ERROR: Validation failed:")
        for err in val_errors:
            print(f"  - {err}")
        return 1
    print("  Validation passed successfully (0 errors).")

    print("[3/4] Serializing to JSON and CSV...")
    save_dataset(records, PROCESSED_JSON_PATH, PROCESSED_CSV_PATH)
    print(f"  Saved JSON : {PROCESSED_JSON_PATH}")
    print(f"  Saved CSV  : {PROCESSED_CSV_PATH}")

    print("[4/4] Generating review notes documentation...")
    generate_notes_markdown(records, DOCS_NOTES_PATH)
    print(f"  Saved Notes: {DOCS_NOTES_PATH}")

    print("-" * 80)
    beh_count = sum(1 for r in records if r.competency_type == "behavioural")
    func_count = sum(1 for r in records if r.competency_type == "functional")
    total_behaviours = sum(len(r.behaviours) for r in records)
    print(f"Total Competencies Extracted : {len(records)}")
    print(f"  - Behavioural Competencies : {beh_count} (8 Core + 5 Leadership)")
    print(f"  - Functional Competencies  : {func_count}")
    print(f"Total Sub-Themes/Behaviours  : {total_behaviours}")
    print(f"Explicit Level Scale Defined : None")
    print("STAGE 2A EXTRACTION COMPLETE.")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(run_kcm_extraction())
