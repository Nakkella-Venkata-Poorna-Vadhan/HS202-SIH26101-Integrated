"""
Unit Test Suite for Learning Resource Providers and Registry (Stage 4.8).

Tests:
  1. ACBPLocalCatalogueProvider retrieval, count (226), and mapping fidelity.
  2. NSSTAPublicProgrammeProvider retrieval from verified curriculum records.
  3. IGOTPublicMetadataProvider retrieval and non-claim of private live LMS integration.
  4. ResourceProviderRegistry fault isolation, status reporting, and graceful degradation.
  5. Immutability of underlying frozen datasets.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from competency_engine.resource_providers import (
    ACBPLocalCatalogueProvider,
    IGOTPublicMetadataProvider,
    LearningResourceProvider,
    NSSTAPublicProgrammeProvider,
    ProviderStatusSummary,
    ResourceProviderRegistry,
)


def test_acbp_local_provider():
    """Verify ACBPLocalCatalogueProvider correctly loads official 226 courses."""
    data_dir = BACKEND_DIR / "data"
    provider = ACBPLocalCatalogueProvider(data_dir)

    assert provider.provider_id == "provider-acbp-local"
    assert provider.provider_type == "local_catalogue"
    assert provider.is_live_integration is False
    assert "MoSPI ACBP FY 2026-27" in provider.integration_note

    status = provider.get_status()
    assert status.status == "available"
    assert status.total_resources == 226
    assert status.is_live_integration is False

    resources = provider.get_resources()
    assert len(resources) == 226
    sample = resources[0]
    assert sample.resource_id.startswith("ACBP-CRS-")
    assert sample.resource_type == "course"
    assert sample.mapping_status in ("validated", "candidate", "unresolved")


def test_nssta_public_provider():
    """Verify NSSTAPublicProgrammeProvider loads curriculum modules from evidence ledger."""
    data_dir = BACKEND_DIR / "data"
    provider = NSSTAPublicProgrammeProvider(data_dir)

    assert provider.provider_id == "provider-nssta-public"
    assert provider.provider_type == "public_curriculum"
    assert provider.is_live_integration is False
    assert "National Statistical Systems Training Academy" in provider.integration_note

    status = provider.get_status()
    assert status.status == "available"
    assert status.total_resources >= 4

    resources = provider.get_resources()
    assert len(resources) >= 4
    for r in resources:
        assert r.resource_id.startswith("NSSTA-")
        assert r.resource_type == "programme"
        assert r.competency_category == "Domain"
        assert "NSSTA" in r.creator_or_institution or "MoSPI" in r.creator_or_institution


def test_igot_public_provider():
    """Verify IGOTPublicMetadataProvider loads public directory records without claiming live SSO."""
    data_dir = BACKEND_DIR / "data"
    provider = IGOTPublicMetadataProvider(data_dir)

    assert provider.provider_id == "provider-igot-public"
    assert provider.provider_type == "public_metadata"
    assert provider.is_live_integration is False
    assert "Parichay SSO" in provider.integration_note

    status = provider.get_status()
    assert status.status == "available"
    assert status.total_resources >= 10

    resources = provider.get_resources()
    assert len(resources) >= 10
    for r in resources:
        assert r.resource_id.startswith("IGOT-")
        assert "Parichay SSO" in r.limitations or "portal.igotkarmayogi.gov.in" in r.limitations


class MockFailingProvider(LearningResourceProvider):
    """Simulated provider that throws runtime exceptions to test fault tolerance."""

    @property
    def provider_id(self) -> str:
        return "provider-mock-failing"

    @property
    def provider_name(self) -> str:
        return "Mock Failing Provider"

    @property
    def provider_type(self) -> str:
        return "public_metadata"

    @property
    def is_live_integration(self) -> bool:
        return False

    @property
    def integration_note(self) -> str:
        return "Simulated failure provider"

    def get_status(self) -> ProviderStatusSummary:
        raise ConnectionError("Simulated provider network timeout")

    def get_resources(self):
        raise RuntimeError("Simulated upstream service error")


def test_registry_graceful_degradation():
    """Verify ResourceProviderRegistry handles failing provider without failing whole system."""
    data_dir = BACKEND_DIR / "data"
    healthy_provider = ACBPLocalCatalogueProvider(data_dir)
    failing_provider = MockFailingProvider()

    registry = ResourceProviderRegistry([healthy_provider, failing_provider])

    # Status reporting should report offline for failing provider
    statuses = registry.list_provider_statuses()
    assert len(statuses) == 2

    status_map = {s.provider_id: s for s in statuses}
    assert status_map["provider-acbp-local"].status == "available"
    assert status_map["provider-mock-failing"].status == "offline"
    assert "Simulated provider network timeout" in status_map["provider-mock-failing"].error

    # Resource aggregation should return healthy resources and gracefully ignore failing provider
    resources = registry.get_all_resources()
    assert len(resources) == 226
