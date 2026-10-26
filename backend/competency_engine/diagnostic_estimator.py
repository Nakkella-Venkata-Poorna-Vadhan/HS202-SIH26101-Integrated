"""
Diagnostic Competency Estimator and Adaptive Question Selection Service.
Implements an explainable, deterministic baseline heuristic for updating provisional
competency levels based on source-grounded diagnostic assessment evidence.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from competency_engine.models import ProvisionalEstimate, SourceQuestion

logger = logging.getLogger(__name__)


# ============================================================================
# Transparent Diagnostic Competency Estimator
# ============================================================================

class DiagnosticEstimator:
    """
    Transparent diagnostic estimator for calculating provisional competency levels.
    
    ESTIMATOR RULES AND ALGORITHM:
    ------------------------------
    1. Evidence Threshold: A minimum of 3 relevant questions must be attempted before
       a provisional level is established. Under 3 questions, the status is strictly
       flagged as 'insufficient_evidence', preserving unassessed status.
    2. Difficulty-Tiered Scoring:
       - 'foundation' questions test Level 1 (Awareness) -> Level 2 (Novice) transition.
       - 'operational' questions test Level 2 (Novice) -> Level 3 (Operational) transition.
       - 'advanced' questions test Level 3 (Operational) -> Level 4/5 (Autonomous/Strategic).
    3. Evaluation Heuristics:
       - Advanced Accuracy >= 66% AND Overall Accuracy >= 75%:
         * Level 5 (Expert) if 100% correct with >= 5 questions.
         * Level 4 (Autonomous) otherwise.
       - Operational Accuracy >= 66% OR Overall Accuracy >= 60%:
         * Level 3 (Operational / Proficient).
       - Foundation Accuracy >= 66% OR Overall Accuracy >= 40%:
         * Level 2 (Novice / Guided Practice).
       - Overall Accuracy < 40%:
         * Level 1 (Foundation / Awareness).
    4. Confidence Metric:
       - Under 3 questions: 0.0 - 0.29 (Insufficient).
       - 3 to 4 questions: 0.60 - 0.75 (Moderate Diagnostic Evidence).
       - 5+ questions: 0.80 - 1.00 (High Diagnostic Evidence).
    5. Prototype Disclaimer:
       All provisional estimates are strictly developmental indicators on the
       Mission Karmayogi Prototype 5-Level Scale and do NOT constitute statutory
       government certification standards.
    """

    MIN_EVIDENCE_QUESTIONS: int = 3

    def estimate_provisional_competency(
        self,
        competency_id: str,
        competency_name: str,
        graded_questions: List[Tuple[SourceQuestion, bool]],
        previous_level: Optional[int] = None,
    ) -> ProvisionalEstimate:
        """
        Compute an explainable provisional estimate given a list of (SourceQuestion, is_correct) tuples.
        """
        evidence_count = len(graded_questions)

        # Rule 1: Insufficient evidence guardrail
        if evidence_count < self.MIN_EVIDENCE_QUESTIONS:
            confidence = round((evidence_count / self.MIN_EVIDENCE_QUESTIONS) * 0.25, 2)
            return ProvisionalEstimate(
                competency_id=competency_id,
                competency_name=competency_name,
                estimated_level=previous_level,
                previous_level=previous_level,
                confidence_score=confidence,
                evidence_count=evidence_count,
                sufficiency_status="insufficient_evidence",
                diagnostic_summary=(
                    f"Insufficient assessment evidence ({evidence_count}/{self.MIN_EVIDENCE_QUESTIONS} questions). "
                    f"Competency '{competency_name}' remains provisional pending completion of diagnostic assessment."
                ),
                scale_min=1,
                scale_max=5,
                is_statutory_standard=False,
            )

        # Tally counts by difficulty tier
        tier_stats: Dict[str, Dict[str, int]] = {
            "foundation": {"total": 0, "correct": 0},
            "operational": {"total": 0, "correct": 0},
            "advanced": {"total": 0, "correct": 0},
        }

        total_correct = 0
        for question, is_correct in graded_questions:
            diff = question.difficulty
            if diff in tier_stats:
                tier_stats[diff]["total"] += 1
                if is_correct:
                    tier_stats[diff]["correct"] += 1
            if is_correct:
                total_correct += 1

        overall_acc = total_correct / evidence_count

        def acc(tier: str) -> float:
            tot = tier_stats[tier]["total"]
            return (tier_stats[tier]["correct"] / tot) if tot > 0 else 0.0

        adv_acc = acc("advanced")
        op_acc = acc("operational")
        fnd_acc = acc("foundation")

        # Determine provisional level
        if (adv_acc >= 0.66 and overall_acc >= 0.75) or (tier_stats["advanced"]["total"] >= 2 and adv_acc == 1.0):
            if overall_acc == 1.0 and evidence_count >= 5:
                estimated_level = 5
                level_desc = "Level 5 (Expert / Strategic)"
            else:
                estimated_level = 4
                level_desc = "Level 4 (Advanced / Autonomous)"
        elif op_acc >= 0.66 or overall_acc >= 0.60:
            estimated_level = 3
            level_desc = "Level 3 (Operational / Proficient)"
        elif fnd_acc >= 0.66 or overall_acc >= 0.40:
            estimated_level = 2
            level_desc = "Level 2 (Novice / Guided Practice)"
        else:
            estimated_level = 1
            level_desc = "Level 1 (Foundation / Awareness)"

        # Confidence calculation
        confidence = min(1.0, round(0.50 + min(0.50, (evidence_count / 8.0) * 0.50), 2))

        summary = (
            f"Demonstrated {total_correct}/{evidence_count} ({int(overall_acc*100)}%) accuracy across "
            f"{tier_stats['foundation']['total']} foundation, {tier_stats['operational']['total']} operational, "
            f"and {tier_stats['advanced']['total']} advanced source-grounded questions. "
            f"Provisional diagnostic level estimated at {level_desc} with confidence {confidence}."
        )

        return ProvisionalEstimate(
            competency_id=competency_id,
            competency_name=competency_name,
            estimated_level=estimated_level,
            previous_level=previous_level,
            confidence_score=confidence,
            evidence_count=evidence_count,
            sufficiency_status="sufficient",
            diagnostic_summary=summary,
            scale_min=1,
            scale_max=5,
            is_statutory_standard=False,
        )


# ============================================================================
# Deterministic Adaptive Question Selector
# ============================================================================

class AdaptiveQuestionSelector:
    """
    Deterministic adaptive sequence selector.
    Selects the next question from an available pool based on previous answer accuracy.
    """

    def select_initial_questions(
        self,
        pool: List[SourceQuestion],
        count: int = 5,
    ) -> List[SourceQuestion]:
        """
        Select a balanced initial diagnostic battery starting at operational difficulty.
        """
        by_diff: Dict[str, List[SourceQuestion]] = {
            "foundation": [q for q in pool if q.difficulty == "foundation"],
            "operational": [q for q in pool if q.difficulty == "operational"],
            "advanced": [q for q in pool if q.difficulty == "advanced"],
        }

        # Sequence: Operational -> Foundation/Operational -> Operational -> Advanced -> Advanced
        sequence_targets = ["operational", "foundation", "operational", "advanced", "advanced"]
        selected: List[SourceQuestion] = []
        used_ids = set()

        for target in sequence_targets[:count]:
            candidates = [q for q in by_diff.get(target, []) if q.question_id not in used_ids]
            if candidates:
                choice = candidates[0]
            else:
                # Fallback to any unused question in pool
                unused = [q for q in pool if q.question_id not in used_ids]
                if not unused:
                    break
                choice = unused[0]

            selected.append(choice)
            used_ids.add(choice.question_id)

        return selected

    def select_next_adaptive_question(
        self,
        pool: List[SourceQuestion],
        answered_ids: List[str],
        last_was_correct: bool,
    ) -> Optional[SourceQuestion]:
        """
        Dynamically branch to harder (advanced) or easier (foundation) question.
        """
        used = set(answered_ids)
        target_diff = "advanced" if last_was_correct else "foundation"

        candidates = [q for q in pool if q.question_id not in used and q.difficulty == target_diff]
        if candidates:
            return candidates[0]

        # Fallback to operational or any unused question
        fallback = [q for q in pool if q.question_id not in used and q.difficulty == "operational"]
        if fallback:
            return fallback[0]

        any_unused = [q for q in pool if q.question_id not in used]
        return any_unused[0] if any_unused else None
