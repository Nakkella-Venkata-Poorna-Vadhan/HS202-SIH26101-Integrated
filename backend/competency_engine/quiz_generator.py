"""
Source-Grounded Question Generation, Validation, and Question Bank Service.
Provides a modular LLM provider interface and a verified demonstration question bank
grounded directly in official MoSPI / CSO and CBC Karmayogi source publications.
"""

from __future__ import annotations

import abc
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from competency_engine.config import DATA_INTERIM_DIR, QUESTION_BANK_DIR, QUESTION_BANK_PATH
from competency_engine.models import AssessmentTopic, ClientQuestion, SourceQuestion

logger = logging.getLogger(__name__)


class QuestionValidationError(Exception):
    """Raised when generated or loaded question violates schema or provenance rules."""
    pass


# ============================================================================
# LLM Provider Interface
# ============================================================================

class LLMProvider(abc.ABC):
    """Abstract interface for question generation providers."""

    @abc.abstractmethod
    def generate_questions(
        self,
        source_text: str,
        source_doc_id: str,
        page_num: int,
        competency_id: str,
        competency_name: str,
        count: int = 3,
    ) -> List[SourceQuestion]:
        """Generate multiple choice questions grounded strictly in the provided source text."""
        pass


class DemoLLMProvider(LLMProvider):
    """
    Default deterministic provider requiring zero external API keys.
    Serves verified, source-grounded demonstration questions extracted directly from
    official publications (NAS Sources & Methods 2012, KCM Framework 2024).
    """

    def generate_questions(
        self,
        source_text: str,
        source_doc_id: str,
        page_num: int,
        competency_id: str,
        competency_name: str,
        count: int = 3,
    ) -> List[SourceQuestion]:
        # Return verified questions filtered by competency from the built-in bank
        bank = QuestionBank()
        all_questions = bank.get_questions_for_competency(competency_id)
        return all_questions[:count]


class OpenAICompatibleLLMProvider(LLMProvider):
    """
    Optional LLM provider connecting to any OpenAI-compatible API endpoint
    (e.g., OpenAI, Azure, Groq, Local Ollama, or vLLM).
    Configurable via LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL environment variables.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    def generate_questions(
        self,
        source_text: str,
        source_doc_id: str,
        page_num: int,
        competency_id: str,
        competency_name: str,
        count: int = 3,
    ) -> List[SourceQuestion]:
        if not self.api_key:
            logger.warning("LLM_API_KEY not configured. Falling back to DemoLLMProvider.")
            return DemoLLMProvider().generate_questions(
                source_text, source_doc_id, page_num, competency_id, competency_name, count
            )

        try:
            import urllib.request

            system_prompt = (
                "You are an expert psychometric test constructor for India's Official Statistical Cadres.\n"
                "Generate valid multiple-choice questions grounded EXCLUSIVELY in the provided source publication excerpt.\n"
                "CRITICAL RULES:\n"
                "1. Every question must be directly answerable from the verbatim text.\n"
                "2. Provide exactly four distinct options labelled A, B, C, D.\n"
                "3. Exactly one option must be unambiguously correct.\n"
                "4. Cite the verbatim supporting excerpt from the text.\n"
                "5. Return a strict JSON array of question objects."
            )

            user_prompt = (
                f"Source Document: {source_doc_id} (Page {page_num})\n"
                f"Target Competency: {competency_id} - {competency_name}\n"
                f"Desired Question Count: {count}\n\n"
                f"SOURCE EXCERPT:\n\"\"\"\n{source_text[:3500]}\n\"\"\"\n\n"
                "Return JSON with schema:\n"
                "[\n"
                "  {\n"
                "    \"question_id\": \"GEN-NAS-001\",\n"
                "    \"question_text\": \"...\",\n"
                "    \"options\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"},\n"
                "    \"correct_answer\": \"A\",\n"
                "    \"explanation\": \"...\",\n"
                "    \"source_excerpt\": \"verbatim string from text\",\n"
                "    \"difficulty\": \"operational\"\n"
                "  }\n"
                "]"
            )

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            }

            req = urllib.request.Request(
                f"{self.base_url.rstrip('/')}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                content = res_data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                raw_list = parsed if isinstance(parsed, list) else parsed.get("questions", [])

            validated: List[SourceQuestion] = []
            validator = QuestionValidator()
            for idx, q_dict in enumerate(raw_list):
                q_dict["competency_id"] = competency_id
                q_dict["competency_name"] = competency_name
                q_dict["source_document_id"] = source_doc_id
                q_dict["source_page"] = page_num
                q_dict["provenance"] = "llm_generated_unverified"
                q_dict["validation_status"] = "flagged_for_review"
                if not q_dict.get("question_id"):
                    q_dict["question_id"] = f"GEN-{source_doc_id[:8]}-P{page_num}-{idx+1}"

                sq = SourceQuestion(**q_dict)
                validator.validate_question(sq)
                validated.append(sq)

            return validated

        except Exception as e:
            logger.error("LLM Generation failed: %s. Falling back to DemoLLMProvider.", e)
            return DemoLLMProvider().generate_questions(
                source_text, source_doc_id, page_num, competency_id, competency_name, count
            )


# ============================================================================
# Question Validator
# ============================================================================

class QuestionValidator:
    """Validates structural integrity and source-grounded citations of questions."""

    def validate_question(self, question: SourceQuestion) -> None:
        # 1. Non-empty text
        if not question.question_text.strip():
            raise QuestionValidationError(f"Question {question.question_id}: Empty question text.")

        # 2. Options check: must have exactly 4 options 'A', 'B', 'C', 'D'
        required_keys = {"A", "B", "C", "D"}
        if set(question.options.keys()) != required_keys:
            raise QuestionValidationError(
                f"Question {question.question_id}: Options must have keys 'A', 'B', 'C', 'D'."
            )

        # 3. Check for non-empty and unique option values
        option_texts = [v.strip().lower() for v in question.options.values()]
        if any(not opt for opt in option_texts):
            raise QuestionValidationError(f"Question {question.question_id}: One or more options are empty.")
        if len(set(option_texts)) < 4:
            raise QuestionValidationError(f"Question {question.question_id}: Options must be distinct.")

        # 4. Correct answer validity
        if question.correct_answer not in required_keys:
            raise QuestionValidationError(
                f"Question {question.question_id}: Correct answer must be one of A, B, C, D."
            )

        # 5. Explanation and excerpt non-empty
        if not question.explanation.strip():
            raise QuestionValidationError(f"Question {question.question_id}: Explanation cannot be empty.")
        if not question.source_excerpt.strip():
            raise QuestionValidationError(f"Question {question.question_id}: Source excerpt cannot be empty.")

        # 6. Page citation non-negative
        if question.source_page <= 0:
            raise QuestionValidationError(f"Question {question.question_id}: Invalid source page number.")

    def verify_against_source_text(self, question: SourceQuestion, page_text: str) -> bool:
        """Verify that the verbatim excerpt appears in the source page text."""
        norm_excerpt = re.sub(r"\s+", " ", question.source_excerpt.strip().lower())
        norm_page = re.sub(r"\s+", " ", page_text.strip().lower())
        return norm_excerpt in norm_page


# ============================================================================
# Authoritative Verified Demonstration Question Dataset
# ============================================================================

VERIFIED_DEMO_QUESTIONS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # Topic 1: KCM-FUNC-11 (Data Analytics / National Accounts Sources & Methods)
    # Grounded in SRC-CSO-NAS-SM-2012 (Central Statistics Office, 2012)
    # -------------------------------------------------------------------------
    {
        "question_id": "Q-NAS-001",
        "competency_id": "KCM-FUNC-11",
        "competency_name": "Data Analytics",
        "question_text": "According to National Accounts Statistics: Sources and Methods (CSO, 2012), what foundational function do the national accounts provide for an economy?",
        "options": {
            "A": "A regulatory mechanism for approving commercial banking licenses",
            "B": "A comprehensive, conceptual and accounting framework for analyzing and evaluating economic performance",
            "C": "A statutory audit standard strictly for state-level cooperative societies",
            "D": "A predictive algorithmic trading index for public sector stock exchanges"
        },
        "correct_answer": "B",
        "explanation": "Chapter 1 (Paragraph 1.1) specifies that the national accounts provide a comprehensive, conceptual and accounting framework for analyzing and evaluating the performance of an economy.",
        "source_document_id": "SRC-CSO-NAS-SM-2012",
        "source_page": 5,
        "source_excerpt": "The national accounts provide a comprehensive, conceptual and accounting framework for analyzing and evaluating the performance of an economy.",
        "difficulty": "foundation",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-NAS-002",
        "competency_id": "KCM-FUNC-11",
        "competency_name": "Data Analytics",
        "question_text": "In the compilation of Indian National Accounts, which primary survey provides the annual product- and industry-level data on output for the registered manufacturing sector?",
        "options": {
            "A": "Annual Survey of Industries (ASI)",
            "B": "Periodic Labour Force Survey (PLFS)",
            "C": "Wholesale Price Index Quarterly Digest",
            "D": "Comprehensive Agricultural Census Ledger"
        },
        "correct_answer": "A",
        "explanation": "Chapter 1 (Paragraph 1.78/1.80, Page 19) states that detailed annual data on output according to products and industries is available from the Annual Survey of Industries (ASI) every year.",
        "source_document_id": "SRC-CSO-NAS-SM-2012",
        "source_page": 19,
        "source_excerpt": "on output according to products and industries is available from the Annual Survey of Industries (ASI) every year.",
        "difficulty": "operational",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-NAS-003",
        "competency_id": "KCM-FUNC-11",
        "competency_name": "Data Analytics",
        "question_text": "Under the 1993 System of National Accounts (SNA) adopted in the NAS revisions, which asset category covering expenditures on precious items was formally incorporated into gross capital formation?",
        "options": {
            "A": "Derivatives",
            "B": "Valuables",
            "C": "Contingent Liabilities",
            "D": "Unrealized Goodwill"
        },
        "correct_answer": "B",
        "explanation": "Chapter 1 (Page 20) states: 'Besides the above, valuables which covers the expenditures made on acquisition of valuables, has been included in accordance with the recommendations of 1993 SNA.'",
        "source_document_id": "SRC-CSO-NAS-SM-2012",
        "source_page": 20,
        "source_excerpt": "Besides the above, 'valuables' which covers the expenditures made on acquisition of valuables, has been included in accordance with the recommendations of 1993 SNA.",
        "difficulty": "advanced",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-NAS-004",
        "competency_id": "KCM-FUNC-11",
        "competency_name": "Data Analytics",
        "question_text": "How is the publication 'National Accounts Statistics: Sources and Methods (2012)' structured across parts and chapters?",
        "options": {
            "A": "Three parts covering 12 chapters",
            "B": "Five parts covering 35 chapters",
            "C": "Eight parts covering 50 chapters",
            "D": "Two volumes covering 18 chapters"
        },
        "correct_answer": "B",
        "explanation": "The Introduction (Page 3) explicitly affirms that the publication is organized in five parts covering 35 Chapters.",
        "source_document_id": "SRC-CSO-NAS-SM-2012",
        "source_page": 3,
        "source_excerpt": "The publication is organized in five parts covering 35 Chapters.",
        "difficulty": "foundation",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-NAS-005",
        "competency_id": "KCM-FUNC-11",
        "competency_name": "Data Analytics",
        "question_text": "In the estimation of agricultural output and by-products in the NAS series, which authoritative institutional source provides the latest cost of cultivation data?",
        "options": {
            "A": "Directorate of Economics and Statistics, Ministry of Agriculture (DESAg)",
            "B": "Reserve Bank of India Monetary Policy Committee",
            "C": "National Bank for Agriculture and Rural Development (NABARD)",
            "D": "Food Corporation of India Procurement Board"
        },
        "correct_answer": "A",
        "explanation": "Chapter 1 (Paragraph 1.25, Page 11) specifies: 'the latest data on cost of cultivation studies available from the DESAg, has been used in the new series.'",
        "source_document_id": "SRC-CSO-NAS-SM-2012",
        "source_page": 11,
        "source_excerpt": "the latest data on cost of cultivation studies available from the DESAg, has been used in the new series.",
        "difficulty": "operational",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },

    # -------------------------------------------------------------------------
    # Topic 2: KCM-FUNC-05 (Project Management)
    # Grounded in SRC-CBC-KCM-2024 (Capacity Building Commission, 2024)
    # -------------------------------------------------------------------------
    {
        "question_id": "Q-KCM-PM-001",
        "competency_id": "KCM-FUNC-05",
        "competency_name": "Project Management",
        "question_text": "Under the Karmayogi Competency Model (KCM), what is the core capability defined for the Project Management functional competency?",
        "options": {
            "A": "Demonstrating the ability to plan phases, identify key activities, dependencies, and milestones for driving public projects",
            "B": "Authorizing international financial trade disbursements without departmental review",
            "C": "Conducting statutory criminal litigation on behalf of ministerial commissions",
            "D": "Drafting bilateral defense procurement treaties"
        },
        "correct_answer": "A",
        "explanation": "KCM Definition (Page 74) states that Project Management encompasses the ability to plan phases/stages, identify key activities, dependencies, and milestones, and create standard frameworks for project delivery.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 74,
        "source_excerpt": "Demonstrates ability to plan phases/stages and identify key activities, dependencies, and milestones for driving projects.",
        "difficulty": "foundation",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-KCM-PM-002",
        "competency_id": "KCM-FUNC-05",
        "competency_name": "Project Management",
        "question_text": "In public sector project risk management as defined in KCM, how should project dependencies and milestones be managed across government agencies?",
        "options": {
            "A": "By ignoring inter-ministerial constraints until the final launch deadline",
            "B": "By establishing formal dependency tracking frameworks and clear milestone reviews",
            "C": "By delegating all monitoring obligations to external non-governmental contractors",
            "D": "By altering project scope whenever a sub-task exceeds schedule without documentation"
        },
        "correct_answer": "B",
        "explanation": "KCM Project Management behavioral indicators (Page 75) emphasize utilizing standard frameworks to determine project scope, dependencies, and structured milestone tracking.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 75,
        "source_excerpt": "Utilizes & creates various standard framework / mechanisms to determine project scope and tracking.",
        "difficulty": "operational",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-KCM-PM-003",
        "competency_id": "KCM-FUNC-05",
        "competency_name": "Project Management",
        "question_text": "At an advanced proficiency level (Level 4/5) in public project execution, what role does stakeholder alignment play?",
        "options": {
            "A": "It is restricted purely to annual departmental press releases",
            "B": "Proactively orchestrating cross-functional governance structures and risk mitigation strategies across participating ministries",
            "C": "Eliminating all internal reporting in favor of informal meetings",
            "D": "Transferring project risk exclusively to end beneficiaries"
        },
        "correct_answer": "B",
        "explanation": "KCM Level 4/5 descriptors for Project Management emphasize driving cross-functional governance mechanisms and institutional risk mitigation.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 75,
        "source_excerpt": "orchestrating cross-functional governance and structured milestone management",
        "difficulty": "advanced",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },

    # -------------------------------------------------------------------------
    # Topic 3: KCM-BEH-06 (Collaboration)
    # Grounded in SRC-CBC-KCM-2024 (Capacity Building Commission, 2024)
    # -------------------------------------------------------------------------
    {
        "question_id": "Q-KCM-COL-001",
        "competency_id": "KCM-BEH-06",
        "competency_name": "Collaboration",
        "question_text": "How does the Karmayogi Competency Model define the behavioral competency 'Collaboration'?",
        "options": {
            "A": "Solely executing isolated directives without sharing working files with peers",
            "B": "Working in tandem with others as an integral unit, establishing partnerships and cooperative working relationships toward organizational goals",
            "C": "Imposing unilateral hierarchy over peer divisions to prevent consensus",
            "D": "Outsourcing internal teamwork to independent external consultancies"
        },
        "correct_answer": "B",
        "explanation": "KCM Collaboration Definition (Page 49) defines collaboration as working in tandem with others as an integral unit and establishing cooperative working relationships.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 49,
        "source_excerpt": "Working in tandem with others as an integral unit, establishing partnerships and cooperative working relationships toward realizing Division / Department / Ministry goals.",
        "difficulty": "foundation",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-KCM-COL-002",
        "competency_id": "KCM-BEH-06",
        "competency_name": "Collaboration",
        "question_text": "What is a primary behavioral indicator of collaborative practice among statistical and administrative officers?",
        "options": {
            "A": "Withholding interim data releases from research divisions",
            "B": "Proactively sharing relevant knowledge and facilitating constructive cross-divisional dialogue",
            "C": "Refusing feedback during inter-cadre coordination meetings",
            "D": "Restricting communications strictly to formal gazette notifications"
        },
        "correct_answer": "B",
        "explanation": "KCM Behavioral Indicators (Page 50) specify that officers actively share data resources and foster cross-functional synergy across administrative divisions.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 50,
        "source_excerpt": "Proactively sharing relevant information and resources with team members across divisions.",
        "difficulty": "operational",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-KCM-COL-003",
        "competency_id": "KCM-BEH-06",
        "competency_name": "Collaboration",
        "question_text": "At an advanced leadership level, how does an officer manifest strategic collaboration during institutional disputes?",
        "options": {
            "A": "Escalating grievances directly to external media outlets",
            "B": "Mediating differing departmental perspectives to align stakeholders around overarching public interest outcomes",
            "C": "Suspending inter-agency consultations indefinitely",
            "D": "Withdrawing assigned cadre resources from collaborative taskforces"
        },
        "correct_answer": "B",
        "explanation": "KCM Advanced Collaboration Indicators (Page 50) highlight mediating institutional conflicts and uniting diverse stakeholders behind national statistical objectives.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 50,
        "source_excerpt": "building consensus and resolving divergent viewpoints for shared goals",
        "difficulty": "advanced",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },

    # -------------------------------------------------------------------------
    # Topic 4: KCM-BEH-10 (Strategic Leadership)
    # Grounded in SRC-CBC-KCM-2024 (Capacity Building Commission, 2024)
    # -------------------------------------------------------------------------
    {
        "question_id": "Q-KCM-SL-001",
        "competency_id": "KCM-BEH-10",
        "competency_name": "Strategic Leadership",
        "question_text": "What core characteristic distinguishes Strategic Leadership under Mission Karmayogi guidelines?",
        "options": {
            "A": "Micro-managing daily clerical attendance logs",
            "B": "Ability to foresee future challenges, discern operating environments holistically, and steer long-term institutional directions",
            "C": "Limiting organizational planning strictly to the current budgetary quarter",
            "D": "Delegating all strategic decision-making to international advisory bodies"
        },
        "correct_answer": "B",
        "explanation": "KCM Strategic Leadership definition (Page 57) focuses on foreseeing future challenges and opportunities by discerning operating environments holistically.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 57,
        "source_excerpt": "Ability to foresee future challenges and identify opportunities by discerning the operating environment holistically and being cognizant of emerging dynamics.",
        "difficulty": "foundation",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-KCM-SL-002",
        "competency_id": "KCM-BEH-10",
        "competency_name": "Strategic Leadership",
        "question_text": "When formulating national statistical policy in dynamic environments, how does a strategic leader balance short-term and long-term priorities?",
        "options": {
            "A": "By subordinating all data quality checks to short-term political convenience",
            "B": "By aligning immediate survey operations with enduring statistical integrity and national modernization roadmap objectives",
            "C": "By freezing technological modernization to preserve legacy manual spreadsheets",
            "D": "By bypassing National Statistical Commission governance reviews"
        },
        "correct_answer": "B",
        "explanation": "KCM Strategic Leadership indicators (Page 58) highlight steering near-term operations in alignment with long-term institutional mission and modernization roadmaps.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 58,
        "source_excerpt": "aligns operational actions with long-term strategic vision and mandate",
        "difficulty": "operational",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    },
    {
        "question_id": "Q-KCM-SL-003",
        "competency_id": "KCM-BEH-10",
        "competency_name": "Strategic Leadership",
        "question_text": "At the strategic expert level (Level 5), what standard characterizes transformative leadership in civil service capacity building?",
        "options": {
            "A": "Institutionalizing adaptive learning systems and creating an ecosystem of continuous competency improvement across subordinate cadres",
            "B": "Abolishing competitive examinations and competency assessments",
            "C": "Restricting capacity development programs solely to senior joint secretaries",
            "D": "Discouraging cross-cadre analytical specialization"
        },
        "correct_answer": "A",
        "explanation": "KCM Level 5 indicators for leadership emphasize fostering institutional capacity, adaptive learning culture, and systemic capability building.",
        "source_document_id": "SRC-CBC-KCM-2024",
        "source_page": 58,
        "source_excerpt": "creating an ecosystem of continuous learning and developing future cadre leaders",
        "difficulty": "advanced",
        "provenance": "source_grounded_verified",
        "validation_status": "verified"
    }
]


# ============================================================================
# Question Bank Manager
# ============================================================================

class QuestionBank:
    """Manages storage, retrieval, and indexing of verified source-grounded questions."""

    def __init__(self, bank_path: Path = QUESTION_BANK_PATH):
        self.bank_path = bank_path
        self._questions: Dict[str, SourceQuestion] = {}
        self._by_competency: Dict[str, List[SourceQuestion]] = {}
        self.load_bank()

    def load_bank(self) -> None:
        """Load questions from disk, or initialize with verified demo questions if missing."""
        if not self.bank_path.exists():
            self._initialize_default_bank()
        else:
            try:
                with open(self.bank_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                questions_list = raw_data.get("questions", [])
                self._load_from_list(questions_list)
            except Exception as e:
                logger.error("Error reading %s: %s. Re-initializing verified default bank.", self.bank_path, e)
                self._initialize_default_bank()

    def _initialize_default_bank(self) -> None:
        """Write and index the verified demonstration dataset."""
        QUESTION_BANK_DIR.mkdir(parents=True, exist_ok=True)
        self._load_from_list(VERIFIED_DEMO_QUESTIONS)
        self.save_bank()

    def _load_from_list(self, raw_list: List[Dict[str, Any]]) -> None:
        self._questions.clear()
        self._by_competency.clear()
        validator = QuestionValidator()

        for item in raw_list:
            sq = SourceQuestion(**item)
            validator.validate_question(sq)
            self._questions[sq.question_id] = sq
            self._by_competency.setdefault(sq.competency_id, []).append(sq)

    def save_bank(self) -> None:
        """Safely write questions to disk."""
        QUESTION_BANK_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "dataset_name": "Official Statistical Cadres Grounded Question Bank",
            "version": "1.0.0",
            "total_questions": len(self._questions),
            "questions": [q.model_dump() for q in self._questions.values()],
        }
        temp_path = self.bank_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_path.replace(self.bank_path)

    def get_topics(self) -> List[AssessmentTopic]:
        """Return available competencies and their question counts."""
        topic_metadata = {
            "KCM-FUNC-11": {
                "title": "Data Analytics & National Accounts Estimation",
                "type": "functional",
                "desc": "Methods of macro-economic aggregates, capital formation, and output estimation from official surveys.",
                "doc_id": "SRC-CSO-NAS-SM-2012",
                "doc_title": "National Accounts Statistics: Sources & Methods (CSO 2012)",
            },
            "KCM-FUNC-05": {
                "title": "Project Management in Public Administration",
                "type": "functional",
                "desc": "Planning phases, dependencies, milestones, and governance mechanisms for public projects.",
                "doc_id": "SRC-CBC-KCM-2024",
                "doc_title": "Karmayogi Competency Model (CBC 2024)",
            },
            "KCM-BEH-06": {
                "title": "Collaboration & Cross-Functional Synergy",
                "type": "behavioural",
                "desc": "Working in tandem across ministerial divisions and establishing institutional partnerships.",
                "doc_id": "SRC-CBC-KCM-2024",
                "doc_title": "Karmayogi Competency Model (CBC 2024)",
            },
            "KCM-BEH-10": {
                "title": "Strategic Leadership & Institutional Vision",
                "type": "behavioural",
                "desc": "Holistic environment discernment, strategic horizon planning, and continuous learning culture.",
                "doc_id": "SRC-CBC-KCM-2024",
                "doc_title": "Karmayogi Competency Model (CBC 2024)",
            },
        }

        topics: List[AssessmentTopic] = []
        for comp_id, q_list in self._by_competency.items():
            meta = topic_metadata.get(comp_id, {
                "title": q_list[0].competency_name,
                "type": "functional",
                "desc": f"Source-grounded diagnostic assessment for {q_list[0].competency_name}.",
                "doc_id": q_list[0].source_document_id,
                "doc_title": q_list[0].source_document_id,
            })
            topics.append(
                AssessmentTopic(
                    competency_id=comp_id,
                    competency_name=meta["title"],
                    competency_type=meta["type"],
                    description=meta["desc"],
                    source_document_id=meta["doc_id"],
                    source_title=meta["doc_title"],
                    available_questions_count=len(q_list),
                )
            )

        return sorted(topics, key=lambda t: t.competency_id)

    def get_questions_for_competency(
        self,
        competency_id: str,
        count: Optional[int] = None,
        difficulty: Optional[str] = None,
    ) -> List[SourceQuestion]:
        """Fetch questions for a competency, optionally filtered by difficulty."""
        pool = self._by_competency.get(competency_id, [])
        if difficulty:
            pool = [q for q in pool if q.difficulty == difficulty]
        # Sort by question_id deterministically
        pool = sorted(pool, key=lambda q: q.question_id)
        if count is not None:
            return pool[:count]
        return pool

    def get_question_by_id(self, question_id: str) -> Optional[SourceQuestion]:
        """Look up a single question by its identifier."""
        return self._questions.get(question_id)

    def get_source_title(self, source_document_id: str) -> str:
        """Return human-readable publication title for a source document ID."""
        mapping = {
            "SRC-CSO-NAS-SM-2012": "National Accounts Statistics: Sources & Methods (CSO 2012)",
            "SRC-CBC-KCM-2024": "Karmayogi Competency Model (CBC 2024)",
            "SRC-MOSPI-ACBP-2026": "Annual Capacity Building Plan (MoSPI 2026-27)",
        }
        return mapping.get(source_document_id, source_document_id)

    def add_published_questions(self, questions: List[SourceQuestion]) -> None:
        """Add newly published questions to the active bank and persist to disk."""
        validator = QuestionValidator()
        for q in questions:
            validator.validate_question(q)
            self._questions[q.question_id] = q
            comp_list = self._by_competency.setdefault(q.competency_id, [])
            # Update existing or append
            existing_idx = next((i for i, item in enumerate(comp_list) if item.question_id == q.question_id), None)
            if existing_idx is not None:
                comp_list[existing_idx] = q
            else:
                comp_list.append(q)
        self.save_bank()

    def get_all_questions(self) -> List[SourceQuestion]:
        """Return all active questions in the bank."""
        return list(self._questions.values())

