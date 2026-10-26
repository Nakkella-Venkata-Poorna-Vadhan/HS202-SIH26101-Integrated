"""
Configuration module for the Competency Intelligence Engine.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directory paths
DATA_DIR = PROJECT_ROOT / "data"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_SYNTHETIC_DIR = DATA_DIR / "synthetic"
DATA_INTERIM_DIR = DATA_DIR / "interim"

# Canonical file paths
KCM_COMPETENCIES_PATH = DATA_PROCESSED_DIR / "competencies_kcm.json"
ACBP_COURSES_PATH = DATA_PROCESSED_DIR / "acbp_courses.json"
ACBP_MAPPINGS_PATH = DATA_PROCESSED_DIR / "acbp_kcm_mappings.json"
# Synthetic seed paths
SYNTHETIC_ROLES_PATH = DATA_SYNTHETIC_DIR / "roles.json"
SYNTHETIC_LEARNERS_PATH = DATA_SYNTHETIC_DIR / "learners.json"

# Assessment and Question Bank paths (Stage 4.4 - 4.7)
QUESTION_BANK_DIR = DATA_DIR / "questions"
QUESTION_BANK_PATH = QUESTION_BANK_DIR / "question_bank.json"
DRAFT_QUESTIONS_PATH = QUESTION_BANK_DIR / "draft_questions.json"
ASSESSMENTS_DIR = DATA_DIR / "assessments"
ATTEMPTS_PATH = ASSESSMENTS_DIR / "attempts.json"
PROVISIONAL_ESTIMATES_PATH = ASSESSMENTS_DIR / "provisional_estimates.json"

# Trainer Upload & Material Ingestion paths (Stage 4.7)
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADED_DOCS_DIR = UPLOADS_DIR / "documents"
UPLOADED_EXTRACTED_DIR = UPLOADS_DIR / "extracted"
UPLOADED_REGISTRY_PATH = UPLOADS_DIR / "registry.json"

# Configurable prototype level scale
# Mission Karmayogi Competency Model (KCM) currently defines competencies and sub-themes
# without explicit quantitative numeric bounds in the official PDF.
# We establish a standard 5-point prototype scale (Level 1 to 5) for evaluation.
DEFAULT_MIN_LEVEL: int = 1
DEFAULT_MAX_LEVEL: int = 5
LEVEL_SCALE_NAME: str = "Mission Karmayogi Prototype 5-Level Scale"
LEVEL_SCALE_DESCRIPTION: str = (
    "Prototype 5-level proficiency scale: "
    "1 = Foundation/Awareness, 2 = Novice/Guided Practice, "
    "3 = Operational/Proficient, 4 = Advanced/Autonomous, "
    "5 = Expert/Strategic. Unassessed competencies are explicitly marked as unassessed."
)
