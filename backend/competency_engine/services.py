"""
Domain Services: Skill Gap Computation and Explainable Course Recommendations.
Deterministic, transparent logic without black-box ML or LLM hallucinations.
"""

from __future__ import annotations

from typing import List, Optional

from competency_engine.config import (
    DEFAULT_MAX_LEVEL,
    DEFAULT_MIN_LEVEL,
    LEVEL_SCALE_DESCRIPTION,
)
from competency_engine.models import (
    CourseRecommendation,
    Learner,
    RecommendationReport,
    Role,
    SkillGap,
    SkillGapReport,
)
from competency_engine.repository import CompetencyRepository
from competency_engine.resource_providers import (
    ResourceProviderRegistry,
    ACBPLocalCatalogueProvider,
    NSSTAPublicProgrammeProvider,
    IGOTPublicMetadataProvider,
)


class SkillGapEngine:
    """Computes explainable competency gaps between a learner's profile and their role."""

    def __init__(
        self,
        scale_min: int = DEFAULT_MIN_LEVEL,
        scale_max: int = DEFAULT_MAX_LEVEL,
        scale_description: str = LEVEL_SCALE_DESCRIPTION,
    ):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.scale_description = scale_description

    def compute_skill_gaps(
        self,
        learner: Learner,
        role: Role,
        repository: CompetencyRepository,
    ) -> SkillGapReport:
        """
        Compute skill gaps for a learner against role requirements.
        Formula: gap = max(0, R - E) for assessed competencies.
        Unassessed competencies are explicitly marked as unassessed (gap=None).
        """
        # Map learner's assessed competencies by ID
        assessment_map = {a.competency_id: a for a in learner.assessed_competencies}

        gaps: List[SkillGap] = []
        gap_count = 0
        competent_count = 0
        unassessed_count = 0

        for req in role.required_competencies:
            comp = repository.get_competency(req.competency_id)
            comp_name = comp.competency_name if comp else req.competency_name
            comp_type = comp.competency_type if comp else "unknown"

            assessment = assessment_map.get(req.competency_id)

            if not assessment or assessment.estimated_level is None or assessment.assessment_status == "unassessed":
                # Unassessed case
                unassessed_count += 1
                gaps.append(
                    SkillGap(
                        competency_id=req.competency_id,
                        competency_name=comp_name,
                        competency_type=comp_type,
                        required_level=req.required_level,
                        estimated_level=None,
                        gap=None,
                        status="unassessed",
                        priority=req.priority,
                        confidence=assessment.confidence if assessment else 0.0,
                        evidence_sources=assessment.evidence_sources if assessment else [],
                        is_synthetic_estimate=True,
                        explanation=(
                            f"No assessment evidence recorded for '{comp_name}'. "
                            f"Required at Level {req.required_level} for {role.role_name}. "
                            f"Marked as unassessed on prototype {self.scale_min}-{self.scale_max} scale."
                        ),
                    )
                )
            else:
                # Assessed case
                e_level = assessment.estimated_level
                r_level = req.required_level
                calculated_gap = max(0, r_level - e_level)
                is_prov = bool(
                    getattr(assessment, "is_provisional", False)
                    or assessment.assessment_method == "diagnostic_quiz_assessment"
                )
                prov_prefix = "[Provisional Quiz Estimate] " if is_prov else ""

                if calculated_gap > 0:
                    gap_count += 1
                    status = "gap_identified"
                    explanation = (
                        f"{prov_prefix}Required Level {r_level} for {role.role_name}; "
                        f"estimated at Level {e_level} ({assessment.confidence * 100:.0f}% confidence). "
                        f"Skill gap: {calculated_gap} level{'s' if calculated_gap > 1 else ''}."
                    )
                else:
                    competent_count += 1
                    status = "competent"
                    explanation = (
                        f"{prov_prefix}Estimated at Level {e_level}, meeting or exceeding "
                        f"the required Level {r_level} for {role.role_name}. Competent."
                    )

                gaps.append(
                    SkillGap(
                        competency_id=req.competency_id,
                        competency_name=comp_name,
                        competency_type=comp_type,
                        required_level=r_level,
                        estimated_level=e_level,
                        gap=calculated_gap,
                        status=status,
                        priority=req.priority,
                        confidence=assessment.confidence,
                        evidence_sources=assessment.evidence_sources,
                        is_synthetic_estimate=True,
                        is_provisional=is_prov,
                        explanation=explanation,
                    )
                )

        return SkillGapReport(
            learner_id=learner.learner_id,
            learner_name=learner.name,
            role_id=role.role_id,
            role_name=role.role_name,
            cadre_role=role.cadre_role,
            department=learner.department,
            scale_min=self.scale_min,
            scale_max=self.scale_max,
            scale_description=self.scale_description,
            total_required_competencies=len(role.required_competencies),
            gap_count=gap_count,
            competent_count=competent_count,
            unassessed_count=unassessed_count,
            gaps=gaps,
        )


class RecommendationEngine:
    """
    Deterministic, explainable course recommendation engine.
    Ranks courses from ACBP catalogue and public providers by gap relevance,
    role/cadre match, verified evidence, difficulty fit, and mapping status.
    Strictly flags candidate vs unresolved mappings with zero hallucination.
    """

    def __init__(
        self,
        repository: CompetencyRepository,
        provider_registry: Optional[ResourceProviderRegistry] = None,
    ):
        self.repository = repository
        if provider_registry is None:
            data_dir = repository.kcm_path.parent.parent
            self.provider_registry = ResourceProviderRegistry([
                ACBPLocalCatalogueProvider(data_dir),
                NSSTAPublicProgrammeProvider(data_dir),
                IGOTPublicMetadataProvider(data_dir),
            ])
        else:
            self.provider_registry = provider_registry

    def _infer_course_difficulty(self, cadre: str, course_name: str) -> str:
        cadre_lower = cadre.lower()
        title_lower = course_name.lower()
        if any(term in cadre_lower for term in ["joint secretary", "deputy director general", "higher administrative"]):
            return "executive"
        if any(term in cadre_lower for term in ["director", "deputy secretary"]) or any(term in title_lower for term in ["strategic", "leadership", "advanced"]):
            return "advanced"
        if any(term in cadre_lower for term in ["clerk", "stenographer", "multi tasking"]) or any(term in title_lower for term in ["basics", "orientation", "introduction", "overview"]):
            return "foundational"
        return "operational"

    def _compute_difficulty_fit(self, target_gap: int, difficulty: str) -> tuple[float, str]:
        """Compute alignment score and unambiguous label between learner gap level and heuristic course difficulty."""
        if target_gap <= 2:
            if difficulty == "foundational":
                return 10.0, "Heuristic Cadre Seniority Alignment: Foundational Level matches initial gap"
            elif difficulty == "operational":
                return 6.0, "Heuristic Cadre Seniority Alignment: Moderate Fit (Operational slightly above initial gap)"
            else:
                return 2.0, "Heuristic Cadre Seniority Alignment: Stretch (Course level exceeds current gap)"
        elif target_gap == 3:
            if difficulty == "operational":
                return 10.0, "Heuristic Cadre Seniority Alignment: Operational Level matches moderate gap"
            elif difficulty in ("foundational", "advanced"):
                return 6.0, "Heuristic Cadre Seniority Alignment: Acceptable Fit (Provides complementary depth)"
            else:
                return 3.0, "Heuristic Cadre Seniority Alignment: High Level (Executive orientation)"
        else:  # target_gap >= 4
            if difficulty in ("advanced", "executive"):
                return 10.0, "Heuristic Cadre Seniority Alignment: Advanced / Executive Level matches critical gap"
            elif difficulty == "operational":
                return 5.0, "Heuristic Cadre Seniority Alignment: Baseline (Operational grounding)"
            else:
                return 1.0, "Heuristic Cadre Seniority Alignment: Low Fit (Foundational material may be insufficient for large gap)"

    def recommend(
        self,
        learner: Learner,
        role: Role,
        gap_report: SkillGapReport,
        include_unresolved: bool = False,
        max_recommendations: int = 10,
        ranking_method: str = "hybrid_explainable",
    ) -> RecommendationReport:
        """
        Generate ranked course recommendations for an identified skill gap profile.
        Supports:
          - 'hybrid_explainable': transparent multi-factor ranking with verified evidence & difficulty fit.
          - 'baseline_catalogue_order': simple catalogue ordering without gap/cadre weighting.
          - 'baseline_naive_match': simple gap matching without difficulty or priority weighting.
        """
        # Identify competencies requiring training (gaps > 0 or unassessed with high/critical priority)
        priority_weights = {"critical": 1.5, "high": 1.2, "medium": 1.0, "low": 0.8}

        target_competencies = {}
        for g in gap_report.gaps:
            if g.status == "gap_identified" and g.gap is not None and g.gap > 0:
                target_competencies[g.competency_id] = {
                    "gap": g.gap,
                    "priority": g.priority,
                    "weight": g.gap * priority_weights.get(g.priority, 1.0),
                    "name": g.competency_name,
                    "type": g.competency_type,
                    "status": "gap",
                }
            elif g.status == "unassessed" and g.priority in ("critical", "high"):
                # Treat unassessed critical/high competencies as potential need
                target_competencies[g.competency_id] = {
                    "gap": 1,
                    "priority": g.priority,
                    "weight": 1.0 * priority_weights.get(g.priority, 1.0),
                    "name": g.competency_name,
                    "type": g.competency_type,
                    "status": "unassessed_priority",
                }

        recommendations: List[CourseRecommendation] = []
        filtered_unresolved_count = 0
        seen_course_ids = set()

        # Mode A: Baseline Catalogue Order
        if ranking_method == "baseline_catalogue_order":
            all_courses = self.repository.list_courses()
            for course in all_courses:
                if course.record_id in seen_course_ids:
                    continue
                # Simple filter: check if course matches category of any target gap or learner cadre
                cat_match = any(
                    comp_meta["type"].lower() == course.competency_category.lower()
                    for comp_meta in target_competencies.values()
                )
                if cat_match:
                    seen_course_ids.add(course.record_id)
                    recommendations.append(
                        CourseRecommendation(
                            rank=0,
                            course_id=course.record_id,
                            course_name=course.course_name,
                            cadre_role=course.cadre_role,
                            target_cadre_match=(course.cadre_role.strip().lower() == learner.cadre_role.strip().lower()),
                            target_competency_id=None,
                            target_competency_name=None,
                            competency_category=course.competency_category,
                            duration=course.duration,
                            course_creator=course.course_creator,
                            mapping_type="catalogue_order",
                            mapping_status="unresolved",
                            is_verified_mapping=False,
                            provenance=course.provenance,
                            score=1.0,
                            recommendation_reason=f"Listed in ACBP catalogue under {course.competency_category} category.",
                            resource_type="course",
                            provider_source="MoSPI ACBP (Local)",
                            mapping_evidence=None,
                            difficulty_fit="Catalogue Default",
                            difficulty_provenance="unspecified",
                            prerequisite_fit="Not specified in official source. Syllabi review recommended before enrollment.",
                            limitations_or_uncertainties="Baseline ranking by raw catalogue appearance order.",
                        )
                    )
            for idx, rec in enumerate(recommendations[:max_recommendations], start=1):
                rec.rank = idx
            return RecommendationReport(
                learner_id=learner.learner_id,
                learner_name=learner.name,
                role_id=role.role_id,
                total_gaps_addressed=len(target_competencies),
                recommendations=recommendations[:max_recommendations],
                filtered_unresolved_count=filtered_unresolved_count,
                include_unresolved_requested=include_unresolved,
                ranking_method=ranking_method,
            )

        # Mode B: Baseline Naive Gap Match
        if ranking_method == "baseline_naive_match":
            for comp_id, comp_meta in target_competencies.items():
                mappings = self.repository.get_mappings_for_competency(comp_id)
                for m in mappings:
                    course = self.repository.get_course(m.course_record_id)
                    if not course or course.record_id in seen_course_ids:
                        continue
                    seen_course_ids.add(course.record_id)
                    recommendations.append(
                        CourseRecommendation(
                            rank=0,
                            course_id=course.record_id,
                            course_name=course.course_name,
                            cadre_role=course.cadre_role,
                            target_cadre_match=(course.cadre_role.strip().lower() == learner.cadre_role.strip().lower()),
                            target_competency_id=comp_id,
                            target_competency_name=comp_meta["name"],
                            competency_category=course.competency_category,
                            duration=course.duration,
                            course_creator=course.course_creator,
                            mapping_type=m.mapping_type,
                            mapping_status="candidate" if m.mapping_type in ("exact_title_reference", "curated_candidate") else "unresolved",
                            is_verified_mapping=(m.validation_status == "validated"),
                            provenance=course.provenance,
                            score=10.0,
                            recommendation_reason=f"Mapped to gap '{comp_meta['name']}'.",
                            resource_type="course",
                            provider_source="MoSPI ACBP (Local)",
                            mapping_evidence=None,
                            difficulty_fit="Baseline Match",
                            difficulty_provenance="unspecified",
                            prerequisite_fit="Not specified in official source. Syllabi review recommended before enrollment.",
                            limitations_or_uncertainties="Naive baseline matching without priority or difficulty weighting.",
                        )
                    )
            recommendations.sort(key=lambda r: (r.course_id,))
            for idx, rec in enumerate(recommendations[:max_recommendations], start=1):
                rec.rank = idx
            return RecommendationReport(
                learner_id=learner.learner_id,
                learner_name=learner.name,
                role_id=role.role_id,
                total_gaps_addressed=len(target_competencies),
                recommendations=recommendations[:max_recommendations],
                filtered_unresolved_count=filtered_unresolved_count,
                include_unresolved_requested=include_unresolved,
                ranking_method=ranking_method,
            )

        # Mode C: Transparent Hybrid Explainable Ranking (Default)
        for comp_id, comp_meta in target_competencies.items():
            mappings = self.repository.get_mappings_for_competency(comp_id)

            for m in mappings:
                course = self.repository.get_course(m.course_record_id)
                if not course or course.record_id in seen_course_ids:
                    continue

                seen_course_ids.add(course.record_id)

                # Cadre match check
                cadre_match = (
                    course.cadre_role.strip().lower() == learner.cadre_role.strip().lower()
                    or course.cadre_role.strip().lower() == role.cadre_role.strip().lower()
                )

                # Determine mapping status & evidence
                if m.validation_status == "validated":
                    m_status = "validated"
                    is_verified = True
                    status_score = 50.0
                    evidence_citation = "Verified syllabus curriculum from official training manual."
                    limitation_note = "Validated mapping verified against institutional course syllabus."
                elif m.mapping_type in ("exact_title_reference", "curated_candidate"):
                    m_status = "candidate"
                    is_verified = False
                    status_score = 30.0
                    evidence_citation = "Exact title match in official MoSPI ACBP FY 2026-27 schedule."
                    limitation_note = "Candidate mapping (exact title reference; unverified pending formal SME adjudication). Public directory entry does not confirm active cohort availability or automated enrollment."
                else:
                    m_status = "unresolved"
                    is_verified = False
                    status_score = 5.0
                    evidence_citation = None
                    limitation_note = "Unresolved mapping: inferred from category only."

                # Calculate difficulty alignment
                course_diff = self._infer_course_difficulty(course.cadre_role, course.course_name)
                diff_score, diff_label = self._compute_difficulty_fit(comp_meta["gap"], course_diff)

                # Calculate composite deterministic score
                score = 0.0
                # 1. Competency gap size and priority
                score += comp_meta["weight"] * 25.0
                # 2. Cadre alignment
                if cadre_match:
                    score += 25.0
                else:
                    score += 10.0  # Partial credit for cross-cadre relevance
                # 3. Mapping status
                score += status_score
                # 4. Course metadata quality
                if course.duration and course.duration != "00.00.00":
                    score += 5.0
                if course.course_creator:
                    score += 5.0
                # 5. Difficulty alignment
                score += diff_score

                # Formulate explainable reason
                reason_parts = [
                    f"Directly addresses skill gap in '{comp_meta['name']}' ({comp_meta['gap']} level gap, {comp_meta['priority']} priority)."
                ]
                if cadre_match:
                    reason_parts.append(f"Tailored for learner's cadre ('{learner.cadre_role}').")
                else:
                    reason_parts.append(f"Listed in ACBP for '{course.cadre_role}' (cross-cadre utility).")

                if m_status == "candidate":
                    reason_parts.append("Candidate mapping (exact title reference; unverified pending SME adjudication).")
                elif m_status == "validated":
                    reason_parts.append("Validated mapping (verified against curriculum syllabus).")

                recommendations.append(
                    CourseRecommendation(
                        rank=0,  # Assigned after sorting
                        course_id=course.record_id,
                        course_name=course.course_name,
                        cadre_role=course.cadre_role,
                        target_cadre_match=cadre_match,
                        target_competency_id=comp_id,
                        target_competency_name=comp_meta["name"],
                        competency_category=course.competency_category,
                        duration=course.duration,
                        course_creator=course.course_creator,
                        mapping_type=m.mapping_type,
                        mapping_status=m_status,
                        is_verified_mapping=is_verified,
                        provenance=course.provenance,
                        score=round(score, 2),
                        recommendation_reason=" ".join(reason_parts),
                        resource_type="course",
                        provider_source="MoSPI ACBP (Local)",
                        mapping_evidence=evidence_citation,
                        difficulty_fit=diff_label,
                        difficulty_provenance="heuristic_cadre_estimate",
                        prerequisite_fit="Not specified in official source. Syllabi review recommended before enrollment.",
                        limitations_or_uncertainties=limitation_note,
                    )
                )

        # Handle category-level or cadre courses that are currently unresolved
        all_courses = self.repository.list_courses()
        for course in all_courses:
            if course.record_id in seen_course_ids:
                continue

            cadre_match = (
                course.cadre_role.strip().lower() == learner.cadre_role.strip().lower()
            )

            # Check if this course belongs to a category where learner has gaps
            has_relevant_category_gap = any(
                comp_meta["type"].lower() == course.competency_category.lower()
                for comp_meta in target_competencies.values()
            )

            if cadre_match and has_relevant_category_gap:
                if not include_unresolved:
                    filtered_unresolved_count += 1
                    continue

                seen_course_ids.add(course.record_id)
                course_diff = self._infer_course_difficulty(course.cadre_role, course.course_name)
                # Take highest gap in this category
                cat_gaps = [
                    comp_meta["gap"] for comp_meta in target_competencies.values()
                    if comp_meta["type"].lower() == course.competency_category.lower()
                ]
                rep_gap = max(cat_gaps) if cat_gaps else 1
                diff_score, diff_label = self._compute_difficulty_fit(rep_gap, course_diff)

                score = 15.0  # Baseline for unresolved category match
                if course.duration and course.duration != "00.00.00":
                    score += 5.0
                score += diff_score

                reason = (
                    f"Cadre match for '{learner.cadre_role}' in ACBP '{course.competency_category}' category. "
                    "NOTICE: Unresolved mapping. No confirmed KCM competency mapping exists in official registry."
                )

                recommendations.append(
                    CourseRecommendation(
                        rank=0,
                        course_id=course.record_id,
                        course_name=course.course_name,
                        cadre_role=course.cadre_role,
                        target_cadre_match=cadre_match,
                        target_competency_id=None,
                        target_competency_name=None,
                        competency_category=course.competency_category,
                        duration=course.duration,
                        course_creator=course.course_creator,
                        mapping_type="unresolved",
                        mapping_status="unresolved",
                        is_verified_mapping=False,
                        provenance=course.provenance,
                        score=round(score, 2),
                        recommendation_reason=reason,
                        resource_type="course",
                        provider_source="MoSPI ACBP (Local)",
                        mapping_evidence=None,
                        difficulty_fit=diff_label,
                        difficulty_provenance="heuristic_cadre_estimate",
                        prerequisite_fit="Not specified in official source. Syllabi review recommended before enrollment.",
                        limitations_or_uncertainties="Unresolved mapping: course categorized by cadre/category only. No official KCM linkage in registry.",
                    )
                )

        # Sort recommendations by score DESC, then course_id ASC for deterministic tie-breaking
        recommendations.sort(key=lambda r: (-r.score, r.course_id))

        # Assign ranks
        for idx, rec in enumerate(recommendations[:max_recommendations], start=1):
            rec.rank = idx

        return RecommendationReport(
            learner_id=learner.learner_id,
            learner_name=learner.name,
            role_id=role.role_id,
            total_gaps_addressed=len(target_competencies),
            recommendations=recommendations[:max_recommendations],
            filtered_unresolved_count=filtered_unresolved_count,
            include_unresolved_requested=include_unresolved,
            ranking_method=ranking_method,
        )
