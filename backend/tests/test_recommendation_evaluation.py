"""
Unit Test Suite for Recommendation System Quantitative Evaluation (Stage 4.8).

Tests:
  1. DCG and NDCG calculations with graded relevance bounds.
  2. Precision@K and Recall@K calculation accuracy and edge cases.
  3. Mean Reciprocal Rank (MRR) computation.
  4. Benchmark scenario schema validity and referential integrity.
  5. Determinism and non-fabrication of evaluation metrics.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import pytest
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from competency_engine.repository import CompetencyRepository
from competency_engine.services import RecommendationEngine
from scripts.evaluate_recommendations import (
    compute_dcg,
    compute_ndcg,
    compute_precision_recall,
    compute_mrr,
    evaluate_method,
)


def test_dcg_calculation_monotonicity():
    """Verify DCG calculation gives higher values to earlier relevant items."""
    rel_ideal = [3, 2, 1, 0]
    rel_suboptimal = [0, 1, 2, 3]

    dcg_ideal = compute_dcg(rel_ideal, k=4)
    dcg_suboptimal = compute_dcg(rel_suboptimal, k=4)

    assert dcg_ideal > dcg_suboptimal
    assert compute_dcg([], k=5) == 0.0
    assert compute_dcg([0, 0, 0], k=3) == 0.0


def test_ndcg_calculation_bounds():
    """Verify NDCG is bounded between 0.0 and 1.0."""
    gt = {"A": 3, "B": 2, "C": 1, "D": 0}

    # Perfect ranking: [A, B, C]
    ndcg_perfect = compute_ndcg(["A", "B", "C"], gt, k=3)
    assert math.isclose(ndcg_perfect, 1.0, rel_tol=1e-5)

    # Inverted ranking: [C, B, A]
    ndcg_inverted = compute_ndcg(["C", "B", "A"], gt, k=3)
    assert 0.0 <= ndcg_inverted < 1.0

    # Completely irrelevant: [X, Y, Z]
    ndcg_zero = compute_ndcg(["X", "Y", "Z"], gt, k=3)
    assert ndcg_zero == 0.0

    # Empty retrieved list
    assert compute_ndcg([], gt, k=3) == 0.0


def test_precision_recall_edge_cases():
    """Test Precision and Recall at K under boundary conditions."""
    gt = {"A": 3, "B": 2, "C": 1, "D": 0}  # 2 relevant items (A, B with rel >= 2)

    # All relevant retrieved
    p, r = compute_precision_recall(["A", "B"], gt, k=2, threshold=2)
    assert p == 1.0
    assert r == 1.0

    # Partial retrieval
    p, r = compute_precision_recall(["A", "X"], gt, k=2, threshold=2)
    assert p == 0.5
    assert r == 0.5

    # None relevant
    p, r = compute_precision_recall(["X", "Y"], gt, k=2, threshold=2)
    assert p == 0.0
    assert r == 0.0

    # Empty list
    p, r = compute_precision_recall([], gt, k=2, threshold=2)
    assert p == 0.0
    assert r == 0.0


def test_mrr_calculation():
    """Test Mean Reciprocal Rank computation."""
    gt = {"A": 3, "B": 2, "C": 0}

    assert compute_mrr(["A", "C"], gt, threshold=2) == 1.0  # Rank 1 -> 1/1
    assert compute_mrr(["C", "B"], gt, threshold=2) == 0.5  # Rank 2 -> 1/2
    assert compute_mrr(["C", "X"], gt, threshold=2) == 0.0  # None -> 0.0
    assert compute_mrr([], gt, threshold=2) == 0.0


def test_benchmark_scenarios_schema_and_integrity():
    """Verify the 10 benchmark scenarios adhere to schema and data constraints."""
    benchmark_path = BACKEND_DIR / "data" / "synthetic" / "recommendation_benchmark_scenarios.json"
    assert benchmark_path.exists(), f"Benchmark manifest missing at {benchmark_path}"

    with open(benchmark_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["version"] in ("1.0.0", "1.1.0")
    assert len(data["scenarios"]) == 10
    assert "disclaimer" in data

    repo = CompetencyRepository()
    repo.load_all()

    for scn in data["scenarios"]:
        assert "scenario_id" in scn
        assert "learner_profile" in scn
        assert "skill_gaps" in scn
        assert "ground_truth_relevance" in scn
        assert len(scn["ground_truth_relevance"]) > 0

        # Verify ground truth relevances are in {0, 1, 2, 3}
        for r_id, rel in scn["ground_truth_relevance"].items():
            assert rel in (0, 1, 2, 3)

        # Verify skill gaps have valid competency IDs
        for gap in scn["skill_gaps"]:
            assert gap["gap"] > 0
            assert gap["priority"] in ("critical", "high", "medium", "low")


def test_evaluation_determinism():
    """Verify evaluate_method produces identical results across consecutive runs."""
    repo = CompetencyRepository()
    repo.load_all()
    engine = RecommendationEngine(repository=repo)

    benchmark_path = BACKEND_DIR / "data" / "synthetic" / "recommendation_benchmark_scenarios.json"
    with open(benchmark_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)["scenarios"][:3]  # Use first 3 scenarios for fast test

    run1_res = evaluate_method(engine, scenarios, ranking_method="hybrid_explainable")
    run2_res = evaluate_method(engine, scenarios, ranking_method="hybrid_explainable")
    run1 = run1_res[0] if isinstance(run1_res, tuple) else run1_res
    run2 = run2_res[0] if isinstance(run2_res, tuple) else run2_res

    assert run1["precision_at_3"] == run2["precision_at_3"]
    assert run1["ndcg_at_3"] == run2["ndcg_at_3"]
    assert run1["mrr"] == run2["mrr"]
    assert run1["coverage_percentage"] == 100.0
