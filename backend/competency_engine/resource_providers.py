"""
Learning Resource Providers and Registry for SIH26101 (Stage 4.9 Hardened).

Provides a unified interface to retrieve learning resources from:
  1. MoSPI ACBP Local Catalogue (226 courses from official ACBP schedule).
  2. NSSTA Public Programme Information (verified official statistical curriculum manuals).
  3. iGOT Karmayogi Public Metadata (public civil service competency courses).

Strict Data Integrity Constraints:
  - is_live_integration is explicitly False for all providers.
  - Zero hallucination of live APIs, enrollment quotas, or restricted learner records.
  - No fabricated course durations or academic prerequisites.
  - Explicit distinction between directly extracted source facts and heuristic estimates.
  - Graceful degradation if any provider encounters an error.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LearningResource(BaseModel):
    """Standardized representation of a learning resource across any provider."""
    resource_id: str
    title: str
    resource_type: Literal["course", "programme", "curriculum_module", "training_manual"]
    provider_id: str
    provider_name: str
    cadre_role: str
    competency_category: str
    target_competency_id: Optional[str] = None
    target_competency_name: Optional[str] = None
    duration: str = "Not specified in source"
    creator_or_institution: str = "Official Public Source"
    mapping_status: Literal["validated", "candidate", "unresolved"] = "unresolved"
    mapping_type: str = "unresolved"
    mapping_evidence: Optional[str] = None
    difficulty_level: Optional[str] = None
    difficulty_provenance: Literal["extracted_from_source", "heuristic_cadre_estimate", "not_specified"] = "not_specified"
    prerequisites: List[str] = Field(default_factory=list)
    prerequisites_note: str = "Not specified in official source"
    enrollment_conditions: str = "Official ministerial nomination workflow"
    source_document_title: str = "Official MoSPI / CBC Document"
    source_record_id: Optional[str] = None
    source_url_or_path: Optional[str] = None
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    limitations: str = ""


class ProviderStatusSummary(BaseModel):
    """Operational health and provenance status of a learning resource provider."""
    provider_id: str
    provider_name: str
    provider_type: Literal["local_catalogue", "public_curriculum", "public_metadata"]
    status: Literal["available", "degraded", "offline"]
    is_live_integration: bool = False
    integration_note: str
    total_resources: int
    last_retrieved: str
    error: Optional[str] = None


class LearningResourceProvider(ABC):
    """Abstract base class for learning resource providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def provider_type(self) -> Literal["local_catalogue", "public_curriculum", "public_metadata"]:
        pass

    @property
    @abstractmethod
    def is_live_integration(self) -> bool:
        pass

    @property
    @abstractmethod
    def integration_note(self) -> str:
        pass

    @abstractmethod
    def get_status(self) -> ProviderStatusSummary:
        pass

    @abstractmethod
    def get_resources(self) -> List[LearningResource]:
        pass


class ACBPLocalCatalogueProvider(LearningResourceProvider):
    """
    Retrieves official MoSPI Annual Capacity Building Plan (ACBP) courses.
    Source: data/processed/acbp_courses.json and acbp_kcm_mappings.json.
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.courses_path = data_dir / "processed" / "acbp_courses.json"
        self.mappings_path = data_dir / "processed" / "acbp_kcm_mappings.json"
        self._cached_resources: Optional[List[LearningResource]] = None
        self._last_error: Optional[str] = None
        self._last_retrieval: str = ""

    @property
    def provider_id(self) -> str:
        return "provider-acbp-local"

    @property
    def provider_name(self) -> str:
        return "MoSPI ACBP Local Catalogue"

    @property
    def provider_type(self) -> Literal["local_catalogue"]:
        return "local_catalogue"

    @property
    def is_live_integration(self) -> bool:
        return False

    @property
    def integration_note(self) -> str:
        return (
            "Static catalogue imported from official MoSPI ACBP FY 2026-27 schedule (OM dated 13-08-2024). "
            "No live LMS synchronization."
        )

    def _infer_difficulty(self, cadre: str, course_name: str) -> str:
        cadre_lower = cadre.lower()
        title_lower = course_name.lower()
        if any(term in cadre_lower for term in ["joint secretary", "deputy director general", "higher administrative"]):
            return "executive"
        if any(term in cadre_lower for term in ["director", "deputy secretary"]) or any(term in title_lower for term in ["strategic", "leadership", "advanced"]):
            return "advanced"
        if any(term in cadre_lower for term in ["clerk", "stenographer", "multi tasking"]) or any(term in title_lower for term in ["basics", "orientation", "introduction", "overview"]):
            return "foundational"
        return "operational"

    def get_resources(self) -> List[LearningResource]:
        if self._cached_resources is not None:
            return self._cached_resources

        if not self.courses_path.exists():
            self._last_error = f"Courses file missing at {self.courses_path}"
            return []

        try:
            with open(self.courses_path, "r", encoding="utf-8") as f:
                raw_courses = json.load(f)
            courses_raw = raw_courses.get("records", []) if isinstance(raw_courses, dict) else raw_courses

            mappings_by_course = {}
            if self.mappings_path.exists():
                with open(self.mappings_path, "r", encoding="utf-8") as f:
                    raw_mappings = json.load(f)
                mappings_raw = raw_mappings.get("mappings", []) if isinstance(raw_mappings, dict) else raw_mappings
                for m in mappings_raw:
                    c_id = m.get("course_record_id")
                    if c_id and c_id not in mappings_by_course:
                        mappings_by_course[c_id] = m

            resources: List[LearningResource] = []
            now_iso = datetime.now(timezone.utc).isoformat()

            for c in courses_raw:
                c_id = c.get("record_id", "")
                mapping = mappings_by_course.get(c_id)

                m_type = mapping.get("mapping_type", "unresolved") if mapping else "unresolved"
                val_status = mapping.get("validation_status", "unresolved") if mapping else "unresolved"

                if val_status == "validated":
                    m_status = "validated"
                    evidence = "Validated against curriculum syllabus by expert SME adjudication."
                    limitations = "Validated curriculum linkage."
                elif m_type in ("exact_title_reference", "curated_candidate"):
                    m_status = "candidate"
                    evidence = f"Exact title reference in official ACBP Schedule (Evidence citation: {mapping.get('evidence_citation', 'ACBP OM pp.3-13') if mapping else 'ACBP Schedule'})."
                    limitations = "Candidate mapping based on exact title match in ACBP schedule; unverified pending formal SME syllabus review."
                else:
                    m_status = "unresolved"
                    evidence = None
                    limitations = "Unresolved mapping: course categorized under broad cadre/category schedule only. No 1-to-1 KCM alignment exists in official registry."

                target_comp = mapping.get("target_competency_id") if mapping else None
                target_comp_name = mapping.get("target_competency_name") if mapping else None

                # Clean duration handling
                duration_raw = c.get("duration")
                if not duration_raw or duration_raw.strip() in ("", "00.00.00", "00:00:00"):
                    duration = "Not specified in source"
                else:
                    duration = duration_raw.strip()

                difficulty_estimate = self._infer_difficulty(c.get("cadre_role", ""), c.get("course_name", ""))

                resources.append(
                    LearningResource(
                        resource_id=c_id,
                        title=c.get("course_name", "Untitled ACBP Course"),
                        resource_type="course",
                        provider_id=self.provider_id,
                        provider_name=self.provider_name,
                        cadre_role=c.get("cadre_role", "All Cadres"),
                        competency_category=c.get("competency_category", "Functional"),
                        target_competency_id=target_comp,
                        target_competency_name=target_comp_name,
                        duration=duration,
                        creator_or_institution=c.get("course_creator") or "MoSPI / Partner Institute",
                        mapping_status=m_status,
                        mapping_type=m_type,
                        mapping_evidence=evidence,
                        difficulty_level=difficulty_estimate,
                        difficulty_provenance="heuristic_cadre_estimate",
                        prerequisites=[],  # Do not invent prerequisites
                        prerequisites_note="No prerequisites stated in MoSPI ACBP schedule.",
                        enrollment_conditions="Requires nomination under MoSPI Annual Capacity Building Plan.",
                        source_document_title="MoSPI Annual Capacity Building Plan (ACBP) FY 2026-27 (OM dated 13-08-2024)",
                        source_record_id=c_id,
                        source_url_or_path="data/processed/acbp_courses.json",
                        retrieval_timestamp=now_iso,
                        limitations=limitations,
                    )
                )

            self._cached_resources = resources
            self._last_retrieval = now_iso
            self._last_error = None
            return resources
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"ACBPLocalCatalogueProvider error: {e}")
            return []

    def get_status(self) -> ProviderStatusSummary:
        resources = self.get_resources()
        status_val: Literal["available", "degraded", "offline"] = "available"
        if self._last_error:
            status_val = "degraded" if resources else "offline"

        return ProviderStatusSummary(
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            provider_type=self.provider_type,
            status=status_val,
            is_live_integration=self.is_live_integration,
            integration_note=self.integration_note,
            total_resources=len(resources),
            last_retrieved=self._last_retrieval or datetime.now(timezone.utc).isoformat(),
            error=self._last_error,
        )


class NSSTAPublicProgrammeProvider(LearningResourceProvider):
    """
    Retrieves verified public statistical training programmes and manuals from NSSTA.
    Source: data/interim/course_evidence_ledger.json (NSSTA-sourced curriculum records).
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.ledger_path = data_dir / "interim" / "course_evidence_ledger.json"
        self._cached_resources: Optional[List[LearningResource]] = None
        self._last_error: Optional[str] = None
        self._last_retrieval: str = ""

    @property
    def provider_id(self) -> str:
        return "provider-nssta-public"

    @property
    def provider_name(self) -> str:
        return "NSSTA Public Programmes & Curriculum"

    @property
    def provider_type(self) -> Literal["public_curriculum"]:
        return "public_curriculum"

    @property
    def is_live_integration(self) -> bool:
        return False

    @property
    def integration_note(self) -> str:
        return (
            "Public curriculum programmes and training manuals published by National Statistical Systems "
            "Training Academy (NSSTA), Greater Noida. Derived from official MoSPI/NSSTA public training calendars."
        )

    def get_resources(self) -> List[LearningResource]:
        if self._cached_resources is not None:
            return self._cached_resources

        if not self.ledger_path.exists():
            self._last_error = f"Ledger file missing at {self.ledger_path}"
            return []

        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)

            records = ledger.get("records", [])
            resources: List[LearningResource] = []
            now_iso = datetime.now(timezone.utc).isoformat()

            for r in records:
                inst = r.get("source_institution", "")
                if "NSSTA" in inst or "MoSPI" in inst or "Industrial Statistics" in inst:
                    r_id = f"NSSTA-{r.get('course_record_id', 'PROG')}"
                    title = r.get("course_name", "NSSTA Statistical Programme")
                    cadre = r.get("cadre_role", "Statistical Cadres")
                    evidence_doc = r.get("source_document_title", "NSSTA Training Calendar")
                    evidence_type = r.get("evidence_type", "official_curriculum_manual")

                    # Do NOT assign target competency based on broad title keyword without explicit heuristic label
                    is_title_stat_keyword = ("Official Statistics" in title or "Index" in title)
                    target_comp = "KCM-DOM-01" if is_title_stat_keyword else None
                    target_comp_name = (
                        "Official Statistics & National Accounting Frameworks (Heuristic Suggestion)"
                        if is_title_stat_keyword else None
                    )
                    mapping_type = "heuristic_title_keyword" if is_title_stat_keyword else "unresolved"

                    resources.append(
                        LearningResource(
                            resource_id=r_id,
                            title=f"{title} (NSSTA Curriculum Module)",
                            resource_type="programme",
                            provider_id=self.provider_id,
                            provider_name=self.provider_name,
                            cadre_role=cadre,
                            competency_category="Domain",
                            target_competency_id=target_comp,
                            target_competency_name=target_comp_name,
                            duration="Not specified in source",
                            creator_or_institution=inst,
                            mapping_status="candidate" if target_comp else "unresolved",
                            mapping_type=mapping_type,
                            mapping_evidence=f"Documented in {evidence_doc} (Evidence Type: {evidence_type})",
                            difficulty_level="operational" if "Officer" in cadre else "advanced",
                            difficulty_provenance="heuristic_cadre_estimate",
                            prerequisites=[],  # Do not invent prerequisites
                            prerequisites_note="No academic prerequisites specified in published calendar entry.",
                            enrollment_conditions="NSSTA curriculum schedule; registration requires official ministerial cadre nomination.",
                            source_document_title=evidence_doc,
                            source_record_id=r.get("course_record_id"),
                            source_url_or_path="data/interim/course_evidence_ledger.json",
                            retrieval_timestamp=now_iso,
                            limitations=(
                                "NSSTA public training calendar module. Target competency suggested heuristically "
                                "by title keywords ('Official Statistics'); unverified pending SME syllabus adjudication."
                                if is_title_stat_keyword else
                                "NSSTA curriculum schedule; registration requires ministerial cadre nomination."
                            ),
                        )
                    )

            self._cached_resources = resources
            self._last_retrieval = now_iso
            self._last_error = None
            return resources
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"NSSTAPublicProgrammeProvider error: {e}")
            return []

    def get_status(self) -> ProviderStatusSummary:
        resources = self.get_resources()
        status_val: Literal["available", "degraded", "offline"] = "available"
        if self._last_error:
            status_val = "degraded" if resources else "offline"

        return ProviderStatusSummary(
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            provider_type=self.provider_type,
            status=status_val,
            is_live_integration=self.is_live_integration,
            integration_note=self.integration_note,
            total_resources=len(resources),
            last_retrieved=self._last_retrieval or datetime.now(timezone.utc).isoformat(),
            error=self._last_error,
        )


class IGOTPublicMetadataProvider(LearningResourceProvider):
    """
    Retrieves public course metadata and CBC foundation courses from iGOT Karmayogi directory.
    Source: data/interim/course_evidence_ledger.json (iGOT / CBC / ISTM public directory records).
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.ledger_path = data_dir / "interim" / "course_evidence_ledger.json"
        self._cached_resources: Optional[List[LearningResource]] = None
        self._last_error: Optional[str] = None
        self._last_retrieval: str = ""

    @property
    def provider_id(self) -> str:
        return "provider-igot-public"

    @property
    def provider_name(self) -> str:
        return "iGOT Karmayogi Public Directory Metadata"

    @property
    def provider_type(self) -> Literal["public_metadata"]:
        return "public_metadata"

    @property
    def is_live_integration(self) -> bool:
        return False

    @property
    def integration_note(self) -> str:
        return (
            "Public course directory metadata published under Mission Karmayogi (CBC / DoPT). "
            "Live user enrollment and completion tracking are restricted behind Parichay SSO and not implemented."
        )

    def get_resources(self) -> List[LearningResource]:
        if self._cached_resources is not None:
            return self._cached_resources

        if not self.ledger_path.exists():
            self._last_error = f"Ledger file missing at {self.ledger_path}"
            return []

        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)

            records = ledger.get("records", [])
            resources: List[LearningResource] = []
            now_iso = datetime.now(timezone.utc).isoformat()

            for r in records:
                inst = r.get("source_institution", "")
                if any(k in inst for k in ["iGOT", "CBC", "ISTM", "AJ-NIFM", "GeM"]):
                    r_id = f"IGOT-{r.get('course_record_id', 'CRS')}"
                    title = r.get("course_name", "iGOT Karmayogi Course")
                    cadre = r.get("cadre_role", "All Central Civil Services")
                    cat = r.get("acbp_competency_category", "Behavioural")
                    evidence_doc = r.get("source_document_title", "iGOT Course Directory")

                    # Extract duration from verbatim excerpt if available
                    excerpt = r.get("evidence_excerpt_verbatim", "")
                    duration = "Not specified in source"
                    if "Duration:" in excerpt:
                        try:
                            duration = excerpt.split("Duration:")[1].split(".")[0].strip()
                        except Exception:
                            duration = "Not specified in source"

                    resources.append(
                        LearningResource(
                            resource_id=r_id,
                            title=f"{title} (iGOT Karmayogi Online Course)",
                            resource_type="course",
                            provider_id=self.provider_id,
                            provider_name=self.provider_name,
                            cadre_role=cadre,
                            competency_category=cat,
                            target_competency_id=None,
                            target_competency_name=None,
                            duration=duration,
                            creator_or_institution=inst,
                            mapping_status="candidate",
                            mapping_type="curated_candidate",
                            mapping_evidence=f"Catalogued in {evidence_doc} via public directory entry.",
                            difficulty_level="foundational" if "Conduct" in title or "Noting" in title else "operational",
                            difficulty_provenance="heuristic_cadre_estimate",
                            prerequisites=[],  # Do not invent prerequisites
                            prerequisites_note="No academic prerequisites specified in public directory entry.",
                            enrollment_conditions="Public directory metadata. Access requires authenticated Government of India Parichay SSO login on portal.igotkarmayogi.gov.in.",
                            source_document_title=evidence_doc,
                            source_record_id=r.get("course_record_id"),
                            source_url_or_path="https://portal.igotkarmayogi.gov.in (Public Directory)",
                            retrieval_timestamp=now_iso,
                            limitations="Public directory metadata only (portal.igotkarmayogi.gov.in). Access requires official Parichay SSO authentication; does not confirm current active enrollment availability, seat quota, or live progress tracking.",
                        )
                    )

            self._cached_resources = resources
            self._last_retrieval = now_iso
            self._last_error = None
            return resources
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"IGOTPublicMetadataProvider error: {e}")
            return []

    def get_status(self) -> ProviderStatusSummary:
        resources = self.get_resources()
        status_val: Literal["available", "degraded", "offline"] = "available"
        if self._last_error:
            status_val = "degraded" if resources else "offline"

        return ProviderStatusSummary(
            provider_id=self.provider_id,
            provider_name=self.provider_name,
            provider_type=self.provider_type,
            status=status_val,
            is_live_integration=self.is_live_integration,
            integration_note=self.integration_note,
            total_resources=len(resources),
            last_retrieved=self._last_retrieval or datetime.now(timezone.utc).isoformat(),
            error=self._last_error,
        )


class ResourceProviderRegistry:
    """
    Central registry aggregating multiple learning resource providers with
    fault tolerance and graceful degradation.
    """

    def __init__(self, providers: Optional[List[LearningResourceProvider]] = None):
        self.providers: Dict[str, LearningResourceProvider] = {}
        if providers:
            for p in providers:
                self.register_provider(p)

    def register_provider(self, provider: LearningResourceProvider) -> None:
        self.providers[provider.provider_id] = provider

    def get_provider(self, provider_id: str) -> Optional[LearningResourceProvider]:
        return self.providers.get(provider_id)

    def list_provider_statuses(self) -> List[ProviderStatusSummary]:
        statuses: List[ProviderStatusSummary] = []
        for p in self.providers.values():
            try:
                statuses.append(p.get_status())
            except Exception as e:
                statuses.append(
                    ProviderStatusSummary(
                        provider_id=p.provider_id,
                        provider_name=p.provider_name,
                        provider_type=p.provider_type,
                        status="offline",
                        is_live_integration=p.is_live_integration,
                        integration_note=p.integration_note,
                        total_resources=0,
                        last_retrieved=datetime.now(timezone.utc).isoformat(),
                        error=str(e),
                    )
                )
        return statuses

    def get_all_resources(self) -> List[LearningResource]:
        """Retrieve consolidated resources from all available providers with fault isolation."""
        consolidated: List[LearningResource] = []
        for p_id, p in self.providers.items():
            try:
                res = p.get_resources()
                consolidated.extend(res)
            except Exception as e:
                logger.error(f"Provider {p_id} failed during resource aggregation: {e}")
                continue
        return consolidated
