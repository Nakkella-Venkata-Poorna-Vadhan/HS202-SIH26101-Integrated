# SIH26101 — Official Statistics Competency Intelligence and Adaptive Learning Platform
## Integrated System (Source A Frontend + Source B Backend)

> **Problem Statement & Scope Disclosure:**  
> Problem Statement ID `SIH26101` is referenced in project workflow documents and public hackathon indices under MoSPI. However, its exact competition edition/year and formal gazetted wording are **not independently verified** against primary AICTE/MIC portal archives. All features are implemented within an agreed course-project prototype scope.


> **Third, Independent, Fully Integrated Project**  
> Location: `D:\Projects\SIH26101\SIH26101-Integrated\`  
> Integrates the rich user experience from **Source A (`HS202_SIH`)** with the authoritative competency intelligence engine, APIs, official datasets, and validation logic from **Source B (`SIH26101-Skill-Intelligence`)**.

---

## 1. Project Provenance & Architecture

This project unifies two distinct source codebases without modifying or relying upon the original source repositories:

| Component | Source Origin | Role in Integrated System | Core Technologies |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | **Source A (`HS202_SIH`)** | Determines **how the application looks, navigates, and interacts** | React 18, TypeScript, Vite, TailwindCSS, Lucide Icons, Recharts |
| **Backend & Core Engine** | **Source B (`SIH26101-Skill-Intelligence`)** | Determines **what the application knows, calculates, and displays** | Python 3.10+, FastAPI, Pydantic, PyMuPDF, Pytest, Uvicorn |

### Directory Architecture

```text
SIH26101-Integrated/
├── backend/                             # Authoritative Competency Engine (from Source B)
│   ├── competency_engine/               # Core intelligence services & FastAPI app
│   │   ├── api.py                       # REST API endpoints & CORS middleware
│   │   ├── models.py                    # Pydantic schemas (KCM, ACBP, Roles, Learners, Gaps)
│   │   ├── repository.py                # Dataset loader (KCM, ACBP, Roles, Learners)
│   │   ├── gap_analysis.py              # Competency gap calculation engine
│   │   └── recommendations.py           # Multi-factor explainable recommendation service
│   ├── data/
│   │   ├── processed/                   # Official extracted & validated datasets
│   │   │   ├── competencies_kcm.json    # 34 official KCM competencies (21 functional, 13 behavioural)
│   │   │   ├── courses_acbp.json        # 226 official MoSPI ACBP calendar courses (51 domain, 79 functional, 96 behavioural)
│   │   │   └── mappings_acbp_kcm.json   # 226 ACBP-to-KCM competency mappings (6 candidate, 220 unresolved)
│   │   ├── synthetic/                   # Civil service demonstration profiles & roles
│   │   │   ├── roles_civil_service.json # 5 demonstration roles (SSO, Director, DDG, DS, JSO)
│   │   │   └── learners_synthetic.json  # 4 demonstration learner profiles
│   │   └── source_register.json         # SHA-256 provenance checksums of raw gazettes/orders
│   ├── scripts/                         # Validation & extraction tooling
│   │   └── validate_competency_mappings.py # Integrity validator for ACBP-to-KCM linkages
│   ├── tests/                           # 203 automated regression & unit tests
│   ├── requirements.txt                 # Pinned Python dependencies
│   └── README.md                        # Backend architectural documentation
│
├── frontend/                            # Polished User Interface (from Source A)
│   ├── src/
│   │   ├── components/                  # Reusable presentation & visualization components
│   │   │   ├── common/                  # Header (with profile switcher), Sidebar, Footer
│   │   │   ├── dashboard/               # KPI cards, SkillProgressList, RecommendationPreview
│   │   │   ├── skillgap/                # RadarGapChart, PriorityGaps
│   │   │   ├── recommendations/         # LearningPathRoadmap, CourseCard, ExternalIntegrations
│   │   │   ├── competency/              # CompetencyCategories directory viewer
│   │   │   ├── admin/                   # Macro dataset counters & synthetic learner table
│   │   │   └── profile/                 # EmployeeProfileView with qualification details
│   │   ├── context/
│   │   │   └── AppContext.tsx           # Authoritative state manager connected to FastAPI
│   │   ├── services/
│   │   │   └── api.ts                   # Centralized Axios API client for FastAPI endpoints
│   │   ├── types/
│   │   │   └── index.ts                 # Full TypeScript interfaces reflecting real backend schemas
│   │   ├── pages/                       # Route views (Dashboard, SkillGap, Recommendations, etc.)
│   │   ├── App.tsx                      # Root application with offline detection banner
│   │   └── index.css                    # Tailwind design system tokens
│   ├── package.json                     # Frontend dependencies
│   ├── vite.config.ts                   # Vite bundler configuration
│   ├── .env                             # Active environment configuration (`VITE_API_BASE_URL`)
│   └── .env.example                     # Environment template
│
└── README.md                            # Comprehensive system documentation (this file)
```

---

### Relational Database Foundation (Phase 1)
- **Status:** Implemented and validated on PostgreSQL 15+ (PostgreSQL 18.6).
- **Package:** `backend/competency_engine/db/` (SQLAlchemy 2.x models, connection pooling, Alembic migrations).
- **Documentation & Setup:** Detailed setup guide available in [`docs/PHASE1_DATABASE_FOUNDATION.md`](docs/PHASE1_DATABASE_FOUNDATION.md).

---

## 2. Installation & Quick Start

### Prerequisites
- **Python**: `>= 3.10` (Tested on Python 3.10 - 3.14)
- **Node.js**: `>= 18.0` with `npm`

### Step 1: Install Backend Dependencies
Open a terminal in `D:\Projects\SIH26101\SIH26101-Integrated\backend`:
```powershell
cd D:\Projects\SIH26101\SIH26101-Integrated\backend
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies
Open a second terminal in `D:\Projects\SIH26101\SIH26101-Integrated\frontend`:
```powershell
cd D:\Projects\SIH26101\SIH26101-Integrated\frontend
npm install
```

---

## 3. Running the Integrated Application

### Start the Authoritative Backend (Terminal 1)
```powershell
cd D:\Projects\SIH26101\SIH26101-Integrated\backend
python -m uvicorn competency_engine.api:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API Base URL**: `http://127.0.0.1:8000`
- **Swagger Interactive API Documentation**: `http://127.0.0.1:8000/docs`
- **Health & Provenance Endpoint**: `http://127.0.0.1:8000/health`

### Start the Integrated Frontend (Terminal 2)
```powershell
cd D:\Projects\SIH26101\SIH26101-Integrated\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
- **Frontend Web Application**: `http://localhost:5173`

---

## 4. Truthful Data Provenance Register

Every data record displayed in the application is strictly partitioned and labeled by source provenance:

| Category | Dataset Name | Records | Provenance Classification | Truthful Scope & Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Competencies** | `competencies_kcm.json` | **34** | **Official Public Source** | Extracted directly from official Karmayogi Competency Model (KCM) documentation (21 Functional, 13 Behavioural). |
| **Courses** | `courses_acbp.json` | **226** | **Official Public Source** | Extracted directly from the MoSPI Annual Capacity Building Plan (ACBP 2026-27: 51 Domain, 79 Functional, 96 Behavioural). |
| **Mappings** | `mappings_acbp_kcm.json` | **226** | **Curated Baseline** | 6 candidate mappings linked to KCM competencies; 220 unresolved courses (unresolved domain statistical gaps and curriculum gaps). |
| **Roles** | `roles_civil_service.json`| **5** | **Synthetic Demonstration**| Structured demonstration cadre profiles (e.g., Senior Statistical Officer, Joint Director, Deputy Director General). |
| **Learners** | `learners_synthetic.json` | **4** | **Synthetic Demonstration**| Demonstration officers: `LEARNER-001` (Arun Kumar), `LEARNER-002` (Dr. Meenakshi), `LEARNER-003` (Pooja Verma - unassessed recruit), `LEARNER-004` (Rajesh Sharma). |

### Mission Karmayogi Prototype 5-Level Scale
Proficiency levels are rendered on a **1 to 5 prototype scale** derived from Mission Karmayogi competency guidelines:
- **Level 1**: Foundation / Awareness
- **Level 2**: Novice / Guided Practice
- **Level 3**: Operational / Proficient
- **Level 4**: Advanced / Autonomous
- **Level 5**: Expert / Strategic
- **Unassessed**: Displayed explicitly as `Unassessed` (never assigned fabricated scores).

> **Important Truthfulness Rules Enforced:**
> 1. Prototype competency levels are **not** represented as statutory government standards.
> 2. Synthetic demonstration profiles are **visibly labeled** across headers, profile views, and administration tables.
> 3. External government platforms (such as iGOT Karmayogi Bharat SSO or NSSTA LMS) are **not claimed as connected live services**; they are referenced as destination catalogs.
> 4. If the backend server becomes unreachable, the UI **does not silently fall back to imaginary numbers**. Instead, it renders an amber disconnection banner with a retry button.

---

## 5. API Endpoints Integrated into Frontend

The centralized API client in `frontend/src/services/api.ts` connects the React application directly to the FastAPI engine:

| Endpoint | Method | Purpose in Integrated Frontend |
| :--- | :--- | :--- |
| `/health` | `GET` | System health check, dataset inventory verification, and offline detection. |
| `/api/competencies` | `GET` | Loads all 52 KCM competencies with functional/behavioural filtering. |
| `/api/courses` | `GET` | Loads all 226 ACBP training calendar courses. |
| `/api/roles` | `GET` | Loads civil service role specifications and required competency benchmarks. |
| `/api/learners` | `GET` | Loads synthetic demonstration learner profiles for the officer switcher. |
| `/api/learners/{id}` | `GET` | Retrieves granular learner profile and demonstrated competency levels. |
| `/api/learners/{id}/skill-gaps` | `GET` | Computes dynamic gap analysis between current proficiencies and role benchmarks. |
| `/api/learners/{id}/recommendations` | `GET` | Returns explainable ACBP course recommendations ranked by gap urgency and cadre match. |
| `/api/assessment/topics` | `GET` | Lists available competencies for source-grounded diagnostic assessment. |
| `/api/assessment/start` | `POST` | Initiates an assessment session, delivering questions scrubbed of answers. |
| `/api/assessment/{attempt_id}/submit` | `POST` | Grades answers server-side, produces provisional estimate, and updates learner profile. |
| `/api/assessment/attempts/{attempt_id}` | `GET` | Retrieves full attempt record with questions feedback and source citations. |
| `/api/assessment/learner/{id}/history` | `GET` | Retrieves all assessment attempts for a learner. |
| `/api/assessment/learner/{id}/estimates` | `GET` | Retrieves active provisional diagnostic estimates for a learner. |

---

## 6. Stage 4.4 — Source-Grounded Diagnostic Assessment

### Overview & Methodology
The diagnostic assessment module enables civil servants to take source-grounded assessments derived directly from official Ministry documentation:
- **`SRC-CSO-NAS-SM-2012`**: *National Accounts Statistics: Sources and Methods (CSO 2012)* — Data Analytics (`KCM-FUNC-11`).
- **`SRC-CBC-KCM-2024`**: *Karmayogi Competency Model (CBC 2024)* — Project Management (`KCM-FUNC-05`), Collaboration (`KCM-BEH-06`), and Strategic Leadership (`KCM-BEH-10`).

### Core Architecture & Guarantees
1. **Source Provenance**: Every question is tied to an official publication ID, exact page number, and verbatim excerpt. No invented page citations.
2. **Answer Secrecy**: The `/api/assessment/start` endpoint strictly strips out correct answers, explanations, and verbatim excerpts before sending questions to the browser.
3. **Server-Side Grading & Validation**: Submissions are graded exclusively on the server against the question bank. Submissions are checked for valid attempt IDs and duplicate submissions are rejected.
4. **Transparent Diagnostic Estimator**:
   - **3-Question Minimum Evidence Threshold**: Under 3 questions, a competency remains provisional/unassessed.
   - **Difficulty-Tiered Scoring**: Foundation (Levels 1–2), Operational (Level 3), Advanced (Levels 4–5).
   - **Confidence Metric**: Clearly reported separately from estimated levels (e.g. 75% confidence).
   - **Disclaimers**: Explicitly labelled as prototype demonstration heuristics without psychometric validity claims.
5. **Data Isolation**: Attempt records and provisional estimates are safely persisted in `data/assessments/attempts.json` and `data/assessments/provisional_estimates.json`, leaving official KCM and ACBP source datasets completely untouched.

### LLM Provider Configuration
The question pipeline supports two modes:
1. **No-Key Demonstration Mode (Default)**:
   - Uses `DemoLLMProvider`, which requires **no external API keys** and operates completely offline.
   - Serves 14 verified, source-grounded demonstration questions extracted directly from `SRC-CSO-NAS-SM-2012` and `SRC-CBC-KCM-2024`.
2. **Optional OpenAI-Compatible Provider**:
   - Set environment variables to enable dynamic question generation via an external LLM:
     ```powershell
     $env:LLM_PROVIDER="openai"
     $env:LLM_API_KEY="your-api-key-here"
     $env:LLM_BASE_URL="https://api.openai.com/v1"  # Or local Ollama / vLLM endpoint
     $env:LLM_MODEL="gpt-4o-mini"
     ```
   - Generated questions are passed through `QuestionValidator` to ensure 4 options, valid keys, non-empty explanations, and verbatim support from source excerpts.

---

## 7. Verification & Test Results

### 1. Backend Regression Suite (Pytest)
Ran in `D:\Projects\SIH26101\SIH26101-Integrated\backend`:
```powershell
python -m pytest
```
- **Result**: `260 passed, 1 warning in 9.19s` (100% test pass rate across all 20 test modules).
- Verified via targeted demo gate regression suite (`tests/test_final_gate_checks.py`), diagnostic assessment tests, recommendation security checks, and persistent state tests.
- Includes 10 dedicated diagnostic assessment tests in `test_diagnostic_assessment.py`:
  - `test_question_bank_loads_verified_questions`
  - `test_question_validator_rejects_malformed_questions`
  - `test_correct_answers_not_leaked_at_assessment_start`
  - `test_server_grades_submission_truthfully`
  - `test_reject_duplicate_and_unknown_submissions`
  - `test_estimator_flags_insufficient_evidence`
  - `test_estimator_assigns_level_4_for_advanced_mastery`
  - `test_estimator_assigns_level_1_for_poor_performance`
  - `test_deterministic_adaptive_branching`
  - `test_unassessed_learner_receives_provisional_estimate_and_updates_skill_gaps`

### 2. Competency Mapping Validator
Ran in `D:\Projects\SIH26101\SIH26101-Integrated\backend`:
```powershell
python scripts/validate_competency_mappings.py
```
- **Result**: `VALIDATION PASSED` across all 226 ACBP-to-KCM linkage records.

### 3. Frontend Production Build
Ran in `D:\Projects\SIH26101\SIH26101-Integrated\frontend`:
```powershell
npm run build
```
- **Result**: `vite v6.4.3 building for production... ✓ built in 22.23s` with 0 TypeScript or build errors.

### 4. End-to-End Browser Flow Verification
Tested automated browser interaction on `http://127.0.0.1:5173`:
- Navigation to `/quiz` portal.
- Selection of **Data Analytics & National Accounts Estimation (`KCM-FUNC-11`)**.
- Successful completion and server-side grading of 4 questions.
- Verified display of **Provisional Competency Assessment Recorded** banner (Level 4, 100% score).
- Verified question-by-question review with exact source title (`SRC-CSO-NAS-SM-2012`), page citations (Page 5, Page 19, Page 20), and verbatim excerpts.
- Verified live sync with learner profile and persistence in `data/assessments/attempts.json`.



---

## 8. Whole-Project Completion Audit & Documentation

Comprehensive project-level audits and logs are maintained in `docs/`:
- **[`docs/COMPLETION_AUDIT.md`](docs/COMPLETION_AUDIT.md)**: Requirement-by-requirement verification matrix mapping all official SIH26101 problem statement mandates to source code, API routes, UI components, and test evidence.
- **[`docs/REMEDIATION_LOG.md`](docs/REMEDIATION_LOG.md)**: Targeted engineering remediations, verified test counts, and disclosed operational boundaries.
- **Demo State Reset**: To return demonstration records and Pooja Verma (`LEARNER-003`) to an initial unassessed state:
  ```powershell
  cd D:\Projects\SIH26101\SIH26101-Integrated\backend
  python scripts/reset_demo_state.py
  ```
