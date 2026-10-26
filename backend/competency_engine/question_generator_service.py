"""
Dynamic Source-Grounded Question Generation, Verification, and Review Pipeline (Stage 4.7)
Generates MCQ drafts from uploaded documents, strictly verifies citations and option integrity,
manages trainer human review (approve/reject/edit), and publishes approved items to the Question Bank.
"""

from __future__ import annotations

import difflib
import json
import logging
import os
import re
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from competency_engine.config import DRAFT_QUESTIONS_PATH, QUESTION_BANK_DIR
from competency_engine.document_service import DocumentService
from competency_engine.models import (
    DocumentPageChunk,
    DraftQuestion,
    DraftQuestionReviewRequest,
    SourceQuestion,
)
from competency_engine.quiz_generator import QuestionBank, QuestionValidationError, QuestionValidator

logger = logging.getLogger(__name__)


class QuestionVerificationError(Exception):
    """Raised when a generated question fails source ground truth or consistency checks."""
    pass


class QuestionVerifier:
    """Rigorous verification of generated questions against source text and psychometric rules."""

    def __init__(self):
        self.validator = QuestionValidator()

    def verify_question(
        self,
        question: DraftQuestion,
        page_text: Any,
        existing_questions: Any,
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify a draft question against:
        1. Structural schema (4 distinct non-empty options, valid correct answer).
        2. Exact verbatim excerpt presence on the cited page.
        3. Answer consistency: correct answer concept must be present in the supporting excerpt.
        4. Duplicate avoidance: question text must not duplicate existing questions.
        """
        # Resolve page text
        actual_page_text = ""
        if isinstance(page_text, str):
            actual_page_text = page_text
        elif isinstance(page_text, list):
            # Could be list of DocumentPageChunk or objects with page_number and text
            chunks_on_page = [
                c.text for c in page_text
                if getattr(c, "page_number", None) == question.source_page
            ]
            actual_page_text = " ".join(chunks_on_page) if chunks_on_page else " ".join(c.text for c in page_text if hasattr(c, "text"))

        # Resolve existing question texts
        existing_texts: List[str] = []
        if isinstance(existing_questions, list):
            for item in existing_questions:
                if isinstance(item, str):
                    existing_texts.append(item)
                elif hasattr(item, "question_text"):
                    existing_texts.append(item.question_text)

        # 1. Structural schema
        sq = SourceQuestion(
            question_id=question.question_id,
            competency_id=question.competency_id,
            competency_name=question.competency_name,
            question_text=question.question_text,
            options=question.options,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            source_document_id=question.source_document_id,
            source_page=question.source_page,
            source_excerpt=question.source_excerpt,
            difficulty=question.difficulty,
            provenance=question.provenance,
            validation_status=question.validation_status,
        )
        try:
            self.validator.validate_question(sq)
        except QuestionValidationError as e:
            return False, f"Structural validation failed: {e}"

        # 2. Verbatim excerpt presence
        norm_excerpt = re.sub(r"\s+", " ", question.source_excerpt.strip().lower())
        norm_page = re.sub(r"\s+", " ", actual_page_text.strip().lower())
        if norm_excerpt not in norm_page:
            return False, f"Source excerpt does not appear verbatim in cited page {question.source_page} text."

        # 3. Answer consistency check
        # The correct answer option's content or key terms must have defensible grounding in the excerpt
        correct_text = question.options[question.correct_answer].strip().lower()
        norm_correct_clean = re.sub(r"[^\w\s]", " ", correct_text)
        norm_excerpt_clean = re.sub(r"[^\w\s]", " ", norm_excerpt)
        words = [w for w in norm_correct_clean.split() if len(w) >= 2]

        if words:
            # Check numbers/quantifiers: if answer specifies a number or quantifier, it MUST appear in excerpt
            number_words = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "first", "second", "third"}
            answer_numbers = [w for w in words if w in number_words or w.isdigit()]
            for num in answer_numbers:
                if num not in norm_excerpt_clean:
                    return False, f"Quantitative assertion '{num}' in correct answer is not supported by source excerpt."

            # Check general substantive terms grounding
            substantive_words = [w for w in words if w not in {"the", "and", "for", "with", "from", "that", "this", "which"}]
            if substantive_words:
                matched = sum(1 for w in substantive_words if w in norm_excerpt_clean)
                match_ratio = matched / len(substantive_words)
                if match_ratio < 0.6 and correct_text not in norm_excerpt:
                    return False, f"Correct answer '{correct_text}' lacks sufficient textual grounding ({match_ratio:.0%} matched) in excerpt."

        # 4. Duplicate avoidance: Compare substantive question content
        norm_q = re.sub(r"\s+", " ", question.question_text.strip().lower())
        def _strip_boilerplate(s: str) -> str:
            s = re.sub(r"^(according to [^,]+,|based on [^,]+,|in the context of [^,]+,|in official [^,]+,|which of the following [^?]+\?|regarding|concerning)\s*", "", s, flags=re.IGNORECASE)
            s = re.sub(r"\(page \d+\)", "", s, flags=re.IGNORECASE)
            return s.strip()

        clean_q = _strip_boilerplate(norm_q)
        for existing in existing_texts:
            norm_ex = re.sub(r"\s+", " ", existing.strip().lower())
            if norm_q == norm_ex:
                return False, "Identical question text already exists in question bank or review queue."
            clean_ex = _strip_boilerplate(norm_ex)
            if clean_q and clean_ex:
                similarity = difflib.SequenceMatcher(None, clean_q, clean_ex).ratio()
                if similarity > 0.90:
                    return False, f"Substantive question content is too similar ({similarity:.0%}) to an existing question."

        return True, None


class QuestionReviewStore:
    """Manages draft questions pending trainer review and publication."""

    def __init__(self, drafts_path: Path = DRAFT_QUESTIONS_PATH):
        self.drafts_path = drafts_path
        self._drafts: Dict[str, DraftQuestion] = {}
        self._ensure_storage()
        self.load_drafts()

    def _ensure_storage(self) -> None:
        self.drafts_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.drafts_path.exists():
            self._write_json(self.drafts_path, {"draft_questions": []})

    def load_drafts(self) -> None:
        if self.drafts_path.exists():
            try:
                with open(self.drafts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._drafts = {
                    item["question_id"]: DraftQuestion(**item)
                    for item in data.get("draft_questions", [])
                }
            except Exception as e:
                logger.error("Failed to load draft questions: %s", e)
                self._drafts = {}

    def save_drafts(self) -> None:
        data = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_drafts": len(self._drafts),
            "draft_questions": [q.model_dump() for q in self._drafts.values()],
        }
        self._write_json(self.drafts_path, data)

    def _write_json(self, path: Path, data: Any) -> None:
        temp = path.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp.replace(path)

    def add_drafts(self, drafts: List[DraftQuestion]) -> None:
        for d in drafts:
            self._drafts[d.question_id] = d
        self.save_drafts()

    def list_drafts(
        self,
        status: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> List[DraftQuestion]:
        res = list(self._drafts.values())
        if status:
            res = [q for q in res if q.status == status]
        if document_id:
            res = [q for q in res if q.document_id == document_id]
        return sorted(res, key=lambda q: q.created_at, reverse=True)

    def get_draft(self, question_id: str) -> Optional[DraftQuestion]:
        return self._drafts.get(question_id)

    def review_draft(
        self,
        question_id: str,
        review: DraftQuestionReviewRequest,
    ) -> DraftQuestion:
        draft = self._drafts.get(question_id)
        if not draft:
            raise KeyError(f"Draft question '{question_id}' not found.")

        now_iso = datetime.now(timezone.utc).isoformat()
        draft.reviewed_by = review.reviewed_by
        draft.reviewed_at = now_iso

        if review.action == "approve":
            draft.status = "approved"
            draft.validation_status = "verified"
            draft.rejection_reason = None
        elif review.action == "reject":
            draft.status = "rejected"
            draft.rejection_reason = review.rejection_reason or "Rejected by trainer during review."
        elif review.action == "edit":
            if review.edited_question:
                for k, v in review.edited_question.items():
                    if hasattr(draft, k) and k not in {"question_id", "document_id", "created_at"}:
                        setattr(draft, k, v)
            draft.status = "approved"
            draft.validation_status = "verified"
            draft.rejection_reason = None

        self._drafts[question_id] = draft
        self.save_drafts()
        return draft

    def publish_approved(
        self,
        question_bank: QuestionBank,
        question_ids: Optional[List[str]] = None,
        published_by: str = "trainer_admin",
    ) -> List[SourceQuestion]:
        """Publish approved questions into the live assessment question bank."""
        candidates = [
            q for q in self._drafts.values()
            if q.status == "approved" and (question_ids is None or q.question_id in question_ids)
        ]

        if not candidates:
            return []

        published_source_questions: List[SourceQuestion] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for d in candidates:
            sq = SourceQuestion(
                question_id=d.question_id,
                competency_id=d.competency_id,
                competency_name=d.competency_name,
                question_text=d.question_text,
                options=d.options,
                correct_answer=d.correct_answer,
                explanation=d.explanation,
                source_document_id=d.source_document_id,
                source_page=d.source_page,
                source_excerpt=d.source_excerpt,
                difficulty=d.difficulty,
                provenance="trainer_verified_published",
                validation_status="verified",
            )
            published_source_questions.append(sq)
            # Update draft state to published
            d.status = "published"
            d.reviewed_at = now_iso
            d.reviewed_by = published_by

        # Commit to question bank
        question_bank.add_published_questions(published_source_questions)
        self.save_drafts()

        return published_source_questions


class DynamicQuestionGenerator:
    """Orchestrates document chunk extraction, LLM/heuristic generation, and rigorous verification."""

    def __init__(
        self,
        doc_service: Optional[DocumentService] = None,
        review_store: Optional[QuestionReviewStore] = None,
        question_bank: Optional[QuestionBank] = None,
        repository: Optional[Any] = None,
    ):
        self.doc_service = doc_service or DocumentService()
        self.review_store = review_store or QuestionReviewStore()
        self.question_bank = question_bank or QuestionBank()
        self.repository = repository
        self.verifier = QuestionVerifier()

    def generate_drafts_from_chunks(
        self,
        chunks: List[DocumentPageChunk],
        document_id: str,
        source_document_id: Optional[str] = None,
        competency_id: str = "KCM-UNRESOLVED",
        competency_name: str = "Unresolved Domain Competency",
        target_count: int = 3,
        difficulty: str = "operational",
        existing_texts: Optional[List[str]] = None,
    ) -> List[DraftQuestion]:
        """Convenience method to generate drafts directly from in-memory chunks."""
        existing = existing_texts or []
        drafts, _ = self._generate_with_heuristic(
            chunks=chunks,
            document_id=document_id,
            competency_id=competency_id,
            competency_name=competency_name,
            question_count=target_count,
            difficulty=difficulty,
            existing_texts=existing,
        )
        return drafts

    def generate_questions_from_document(
        self,
        document_id: str,
        competency_id: Optional[str] = None,
        question_count: int = 3,
        difficulty: Optional[Literal["foundation", "operational", "advanced"]] = None,
        focus_pages: Optional[List[int]] = None,
    ) -> Tuple[List[DraftQuestion], List[str]]:
        """
        Generate source-grounded MCQ drafts from an uploaded document.
        Returns (generated_drafts, rejection_reasons).
        """
        doc = self.doc_service.get_document(document_id)
        if not doc:
            raise ValueError(f"Document '{document_id}' not found.")

        if doc.extraction_status == "ocr_required":
            raise ValueError(f"Document '{document_id}' is a scanned PDF requiring OCR. Digital text extraction is unavailable.")

        # Determine competency
        target_comp_id = competency_id or "KCM-UNRESOLVED"
        target_comp_name = "Unresolved Domain Competency"
        if target_comp_id != "KCM-UNRESOLVED":
            official = None
            if self.repository is not None:
                official = self.repository.get_competency(target_comp_id) or self.repository.get_competency(
                    target_comp_id.upper().strip()
                )
            if official is not None:
                target_comp_id = official.competency_id
                target_comp_name = official.competency_name
            else:
                comp_topics = {t.competency_id: t.competency_name for t in self.question_bank.get_topics()}
                target_comp_name = comp_topics.get(target_comp_id, f"Competency {target_comp_id}")

        # Fetch chunks
        chunks = self.doc_service.get_document_chunks(document_id)
        if focus_pages:
            chunks = [c for c in chunks if c.page_number in focus_pages]

        if not chunks:
            raise ValueError(f"No usable text chunks available for document '{document_id}'.")

        # Collect all existing question texts to avoid duplicate questions
        existing_texts = [q.question_text for q in self.question_bank.get_all_questions()]
        existing_texts += [d.question_text for d in self.review_store.list_drafts()]

        # Check if LLM provider is configured
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model = os.getenv("LLM_MODEL")

        if not base_url:
            if os.getenv("GEMINI_API_KEY") and not (os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")):
                base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
                model = model or "gemini-1.5-flash"
            else:
                base_url = "https://api.openai.com/v1"
                model = model or "gpt-4o-mini"
        else:
            model = model or "gpt-4o-mini" 

        drafts: List[DraftQuestion] = []
        rejections: List[str] = []

        if api_key:
            drafts, rejections = self._generate_with_llm(
                chunks=chunks,
                document_id=document_id,
                competency_id=target_comp_id,
                competency_name=target_comp_name,
                question_count=question_count,
                difficulty=difficulty or "operational",
                api_key=api_key,
                base_url=base_url,
                model=model,
                existing_texts=existing_texts,
            )
        else:
            # Deterministic, authentic source-grounded heuristic extractor
            drafts, rejections = self._generate_with_heuristic(
                chunks=chunks,
                document_id=document_id,
                competency_id=target_comp_id,
                competency_name=target_comp_name,
                question_count=question_count,
                difficulty=difficulty or "operational",
                existing_texts=existing_texts,
            )

        # Save generated drafts to review store
        if drafts:
            self.review_store.add_drafts(drafts)

        return drafts, rejections

    def _generate_with_heuristic(
        self,
        chunks: List[DocumentPageChunk],
        document_id: str,
        competency_id: str,
        competency_name: str,
        question_count: int,
        difficulty: str,
        existing_texts: List[str],
    ) -> Tuple[List[DraftQuestion], List[str]]:
        """
        Deterministic, offline extraction from actual source chunks.
        Extracts factual assertions and definitions directly from the document.
        """
        drafts: List[DraftQuestion] = []
        rejections: List[str] = []

        # Find candidate sentences across chunks
        candidate_items: List[Dict[str, Any]] = []

        for chunk in chunks:
            text = chunk.text
            # Extract sentences of reasonable length (60 to 220 chars)
            sentences = [
                s.strip()
                for s in re.split(r"(?<=[.!?])\s+", text)
                if 50 <= len(s.strip()) <= 240 and not s.strip().startswith(("http", "www", "File", "Page"))
            ]

            for s in sentences:
                # Look for definitive, informational statements
                is_informative = any(
                    marker in s.lower()
                    for marker in [
                        " is ", " are ", " defined as ", " includes ", " covers ",
                        " provides ", " established ", " accordance with ", " method ",
                        " framework ", " statistical ", " policy ", " objective ", " data "
                    ]
                )
                if is_informative:
                    candidate_items.append({
                        "sentence": s,
                        "page_number": chunk.page_number,
                        "chunk_text": chunk.text,
                    })

        if not candidate_items:
            rejections.append("Source document does not contain suitable declarative factual sentences.")
            return drafts, rejections

        diff_levels = ["foundation", "operational", "advanced"]
        assigned_diff = difficulty if difficulty in diff_levels else "operational"

        # Formulate MCQ drafts from top candidate items
        for idx, item in enumerate(candidate_items[: question_count * 2]):
            if len(drafts) >= question_count:
                break

            sentence = item["sentence"]
            page_num = item["page_number"]
            q_id = f"DRFT-{document_id[:12]}-P{page_num}-{uuid.uuid4().hex[:4].upper()}"

            # Construct question based on the sentence
            # Example: "According to the publication, which statement accurately reflects the documented principle?"
            question_text = (
                f"According to the source documentation (Page {page_num}), which of the following is correct regarding "
                f"'{sentence.split()[0]} {sentence.split()[1] if len(sentence.split()) > 1 else ''}'?"
            )

            correct_option_text = sentence.rstrip(".")

            # Synthesize distinct, plausible contrastive options
            foils = [
                f"The principle is strictly discretionary and not applied to standard statistical procedures.",
                f"It was deprecated following the implementation of state-level decentralized accounting frameworks.",
                f"The methodology is confined exclusively to commercial export licensing and speculative valuation.",
            ]

            # Assign options with random-looking deterministic position (e.g. B or A)
            correct_slot = ["B", "A", "C", "D"][idx % 4]
            options: Dict[str, str] = {}
            foil_idx = 0
            for slot in ["A", "B", "C", "D"]:
                if slot == correct_slot:
                    options[slot] = correct_option_text
                else:
                    options[slot] = foils[foil_idx % len(foils)]
                    foil_idx += 1

            draft = DraftQuestion(
                question_id=q_id,
                document_id=document_id,
                source_document_id=document_id,
                competency_id=competency_id,
                competency_name=competency_name,
                question_text=question_text,
                options=options,
                correct_answer=correct_slot,  # type: ignore
                explanation=f"Official publication (Page {page_num}) explicitly states: '{sentence}'.",
                source_page=page_num,
                source_excerpt=sentence,
                difficulty=assigned_diff,  # type: ignore
                status="draft",
                provenance="dynamic_heuristic_source_grounded",
                validation_status="flagged_for_review",
                verification_notes="Generated via deterministic source extraction. Awaiting trainer review.",
            )

            # Rigorous verification
            valid, reason = self.verifier.verify_question(draft, item["chunk_text"], existing_texts)
            if valid:
                drafts.append(draft)
                existing_texts.append(question_text)
            else:
                rejections.append(f"Rejected candidate from page {page_num}: {reason}")

        return drafts, rejections

    def _generate_with_llm(
        self,
        chunks: List[DocumentPageChunk],
        document_id: str,
        competency_id: str,
        competency_name: str,
        question_count: int,
        difficulty: str,
        api_key: str,
        base_url: str,
        model: str,
        existing_texts: List[str],
    ) -> Tuple[List[DraftQuestion], List[str]]:
        """
        Generate questions using configured OpenAI-compatible API.
        Verifies every LLM-generated question against source text.
        """
        drafts: List[DraftQuestion] = []
        rejections: List[str] = []

        system_prompt = (
            "You are a psychometric assessment specialist for Indian Civil Services and MoSPI statistical cadres.\n"
            "Create multiple-choice questions grounded STRICTLY and EXCLUSIVELY in the provided source passage.\n"
            "RULES:\n"
            "1. Every question must be fully answerable from the verbatim text provided.\n"
            "2. Provide exactly four distinct options labelled A, B, C, D.\n"
            "3. Exactly one option must be correct.\n"
            "4. Provide the exact verbatim supporting excerpt from the text.\n"
            "5. Return a strict JSON object with a 'questions' array."
        )

        # Use up to 3 chunks to assemble sufficient context
        context_chunks = chunks[:3]
        for chunk in context_chunks:
            if len(drafts) >= question_count:
                break

            user_prompt = (
                f"Document: {document_id} (Page {chunk.page_number})\n"
                f"Competency: {competency_id} - {competency_name}\n"
                f"Target Difficulty: {difficulty}\n"
                f"Count: {min(2, question_count - len(drafts))}\n\n"
                f"SOURCE PASSAGE:\n\"\"\"\n{chunk.text[:2500]}\n\"\"\"\n\n"
                "Return JSON with format:\n"
                "{\n"
                "  \"questions\": [\n"
                "    {\n"
                "      \"question_text\": \"...\",\n"
                "      \"options\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"},\n"
                "      \"correct_answer\": \"A\",\n"
                "      \"explanation\": \"...\",\n"
                "      \"source_excerpt\": \"exact verbatim excerpt from passage\",\n"
                "      \"difficulty\": \"operational\"\n"
                "    }\n"
                "  ]\n"
                "}"
            )

            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"},
                }

                req = urllib.request.Request(
                    f"{base_url.rstrip('/')}/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    content = resp_json["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    raw_questions = parsed.get("questions", [])

                for q_dict in raw_questions:
                    q_id = f"DRFT-{document_id[:12]}-P{chunk.page_number}-{uuid.uuid4().hex[:4].upper()}"
                    draft = DraftQuestion(
                        question_id=q_id,
                        document_id=document_id,
                        source_document_id=document_id,
                        competency_id=competency_id,
                        competency_name=competency_name,
                        question_text=q_dict.get("question_text", ""),
                        options=q_dict.get("options", {}),
                        correct_answer=q_dict.get("correct_answer", "A"),
                        explanation=q_dict.get("explanation", ""),
                        source_page=chunk.page_number,
                        source_excerpt=q_dict.get("source_excerpt", ""),
                        difficulty=q_dict.get("difficulty", difficulty),
                        status="draft",
                        provenance="llm_source_generated_unverified",
                        validation_status="flagged_for_review",
                        verification_notes="Generated via LLM provider. Awaiting trainer review.",
                    )

                    # Verification against chunk text
                    valid, reason = self.verifier.verify_question(draft, chunk.text, existing_texts)
                    if valid:
                        drafts.append(draft)
                        existing_texts.append(draft.question_text)
                    else:
                        rejections.append(f"LLM draft rejected: {reason}")

            except Exception as e:
                logger.error("LLM Provider call failed: %s", e)
                rejections.append(f"Provider failure: {e}")

        # If LLM failed to produce sufficient valid questions, fallback to heuristic extraction
        if len(drafts) < question_count:
            logger.info("Supplementing with source-grounded heuristic generation.")
            supp_drafts, supp_rejections = self._generate_with_heuristic(
                chunks=chunks,
                document_id=document_id,
                competency_id=competency_id,
                competency_name=competency_name,
                question_count=question_count - len(drafts),
                difficulty=difficulty,
                existing_texts=existing_texts,
            )
            drafts.extend(supp_drafts)
            rejections.extend(supp_rejections)

        return drafts, rejections
