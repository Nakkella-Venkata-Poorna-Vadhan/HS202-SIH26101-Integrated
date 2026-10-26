"""
Recommendation System Quantitative Evaluation Pipeline (Stage 4.9 Hardened).

Defensible Evaluation of Learning Recommendations:
  Method 1: Baseline 1 (Raw Catalogue Appearance Order)
  Method 2: Baseline 2 (Naive Competency Match without priority/difficulty/evidence weighting)
  Method 3: Proposed (Transparent Hybrid Explainable Ranking)

Integrity & Provenance Qualifications:
  - Synthetic offline Information Retrieval benchmark created for algorithmic verification.
  - Relevance grades (0-3) were manually authored based on domain keywords and cadre seniority.
  - Relevances DO NOT represent independent external SME adjudication, field trials, or real-world learner evaluations.
  - Latencies measure in-memory Python ranking functions only, excluding network/database I/O.
  - No statistical significance or real-world learning efficacy is claimed from this benchmark.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Tuple

# Set up project root
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from competency_engine.models import Learner, Role, SkillGap, SkillGapReport
from competency_engine.repository import CompetencyRepository
from competency_engine.resource_providers import (
    ACBPLocalCatalogueProvider,
    IGOTPublicMetadataProvider,
    NSSTAPublicProgrammeProvider,
    ResourceProviderRegistry,
)
from competency_engine.services import RecommendationEngine


def compute_dcg(relevances: List[int], k: int) -> float:
    """Compute Discounted Cumulative Gain at rank K."""
    dcg = 0.0
    for i, rel in enumerate(relevances[:k], start=1):
        if rel > 0:
            dcg += (math.pow(2, rel) - 1.0) / math.log2(i + 1)
    return dcg


def compute_ndcg(retrieved_ids: List[str], ground_truth: Dict[str, int], k: int) -> float:
    """Compute Normalized Discounted Cumulative Gain at rank K."""
    actual_relevances = [ground_truth.get(r_id, 0) for r_id in retrieved_ids[:k]]
    actual_dcg = compute_dcg(actual_relevances, k)

    ideal_relevances = sorted(list(ground_truth.values()), reverse=True)
    ideal_dcg = compute_dcg(ideal_relevances, k)

    if ideal_dcg == 0.0:
        return 1.0 if actual_dcg == 0.0 else 0.0
    return actual_dcg / ideal_dcg


def compute_precision_recall(
    retrieved_ids: List[str], ground_truth: Dict[str, int], k: int, threshold: int = 2
) -> Tuple[float, float]:
    """Compute Precision@K and Recall@K at a given binary relevance threshold."""
    retrieved_k = retrieved_ids[:k]
    if not retrieved_k:
        return 0.0, 0.0

    relevant_in_k = sum(1 for r_id in retrieved_k if ground_truth.get(r_id, 0) >= threshold)
    total_relevant = sum(1 for rel in ground_truth.values() if rel >= threshold)

    prec = relevant_in_k / float(len(retrieved_k))
    rec = (relevant_in_k / float(total_relevant)) if total_relevant > 0 else 0.0
    return prec, rec


def compute_mrr(retrieved_ids: List[str], ground_truth: Dict[str, int], threshold: int = 2) -> float:
    """Compute Reciprocal Rank of the first relevant item."""
    for rank, r_id in enumerate(retrieved_ids, start=1):
        if ground_truth.get(r_id, 0) >= threshold:
            return 1.0 / float(rank)
    return 0.0


def evaluate_method(
    engine: RecommendationEngine,
    scenarios: List[Dict[str, Any]],
    ranking_method: str,
    max_k: int = 5,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Evaluate a specific recommendation method across all benchmark scenarios."""
    prec_3_list = []
    prec_5_list = []
    rec_3_list = []
    rec_5_list = []
    ndcg_3_list = []
    ndcg_5_list = []
    mrr_list = []
    scenarios_covered = 0
    total_invalid_recs = 0
    total_recs_evaluated = 0
    complete_explanations_count = 0
    latencies_ms = []
    per_scenario_metrics = []

    for scn in scenarios:
        profile = scn["learner_profile"]
        gt = scn["ground_truth_relevance"]

        learner = Learner(
            learner_id=profile["learner_id"],
            name=profile["name"],
            cadre_role=profile["cadre_role"],
            role_id=profile["role_id"],
            department="Ministry of Statistics and Programme Implementation",
            assessed_competencies=[],
        )
        role = Role(
            role_id=profile["role_id"],
            role_name=profile["cadre_role"],
            cadre_role=profile["cadre_role"],
            description=f"Standard role profile for {profile['cadre_role']}",
            required_competencies=[],
        )

        gaps = [
            SkillGap(
                competency_id=g["competency_id"],
                competency_name=g["competency_name"],
                competency_type=g["competency_type"],
                required_level=3,
                estimated_level=1,
                gap=g["gap"],
                status="gap_identified",
                priority=g["priority"],
                explanation=f"Identified gap of {g['gap']} levels for {g['competency_name']}",
            )
            for g in scn["skill_gaps"]
        ]
        gap_report = SkillGapReport(
            learner_id=learner.learner_id,
            learner_name=learner.name,
            role_id=role.role_id,
            role_name=role.role_name,
            cadre_role=role.cadre_role,
            department=learner.department,
            scale_min=1,
            scale_max=5,
            scale_description="Levels 1 to 5",
            total_required_competencies=len(gaps),
            gap_count=len(gaps),
            competent_count=0,
            unassessed_count=0,
            gaps=gaps,
        )

        start_time = time.perf_counter()
        report = engine.recommend(
            learner=learner,
            role=role,
            gap_report=gap_report,
            include_unresolved=True,
            max_recommendations=max_k,
            ranking_method=ranking_method,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        latencies_ms.append(elapsed_ms)

        retrieved_ids = [r.course_id for r in report.recommendations]
        if retrieved_ids:
            scenarios_covered += 1

        p3, r3 = compute_precision_recall(retrieved_ids, gt, k=3, threshold=2)
        p5, r5 = compute_precision_recall(retrieved_ids, gt, k=5, threshold=2)
        ndcg3 = compute_ndcg(retrieved_ids, gt, k=3)
        ndcg5 = compute_ndcg(retrieved_ids, gt, k=5)
        mrr = compute_mrr(retrieved_ids, gt, threshold=2)

        prec_3_list.append(p3)
        prec_5_list.append(p5)
        rec_3_list.append(r3)
        rec_5_list.append(r5)
        ndcg_3_list.append(ndcg3)
        ndcg_5_list.append(ndcg5)
        mrr_list.append(mrr)

        per_scenario_metrics.append({
            "scenario_id": scn["scenario_id"],
            "title": scn["title"],
            "cadre_role": profile["cadre_role"],
            "retrieved_count": len(retrieved_ids),
            "precision_at_3": round(p3, 4),
            "precision_at_5": round(p5, 4),
            "recall_at_3": round(r3, 4),
            "recall_at_5": round(r5, 4),
            "ndcg_at_3": round(ndcg3, 4),
            "ndcg_at_5": round(ndcg5, 4),
            "mrr": round(mrr, 4),
            "latency_ms": round(elapsed_ms, 3),
        })

        for r in report.recommendations:
            total_recs_evaluated += 1
            if r.mapping_status == "unresolved" and ranking_method != "baseline_catalogue_order":
                total_invalid_recs += 1
            has_reason = bool(r.recommendation_reason and len(r.recommendation_reason.strip()) > 10)
            has_provider = bool(r.provider_source and len(r.provider_source.strip()) > 2)
            has_limitations = bool(r.limitations_or_uncertainties and len(r.limitations_or_uncertainties.strip()) > 5)
            if has_reason and has_provider and has_limitations:
                complete_explanations_count += 1

    total_scenarios = len(scenarios)
    avg_prec_3 = sum(prec_3_list) / total_scenarios if total_scenarios else 0.0
    avg_prec_5 = sum(prec_5_list) / total_scenarios if total_scenarios else 0.0
    avg_rec_3 = sum(rec_3_list) / total_scenarios if total_scenarios else 0.0
    avg_rec_5 = sum(rec_5_list) / total_scenarios if total_scenarios else 0.0
    avg_ndcg_3 = sum(ndcg_3_list) / total_scenarios if total_scenarios else 0.0
    avg_ndcg_5 = sum(ndcg_5_list) / total_scenarios if total_scenarios else 0.0
    avg_mrr = sum(mrr_list) / total_scenarios if total_scenarios else 0.0
    coverage_pct = (scenarios_covered / float(total_scenarios)) * 100.0 if total_scenarios else 0.0
    invalid_rate_pct = (total_invalid_recs / float(total_recs_evaluated)) * 100.0 if total_recs_evaluated else 0.0
    explanation_pct = (complete_explanations_count / float(total_recs_evaluated)) * 100.0 if total_recs_evaluated else 0.0
    avg_latency = sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0

    summary = {
        "method": ranking_method,
        "scenarios_evaluated": total_scenarios,
        "precision_at_3": round(avg_prec_3, 4),
        "precision_at_5": round(avg_prec_5, 4),
        "recall_at_3": round(avg_rec_3, 4),
        "recall_at_5": round(avg_rec_5, 4),
        "ndcg_at_3": round(avg_ndcg_3, 4),
        "ndcg_at_5": round(avg_ndcg_5, 4),
        "mrr": round(avg_mrr, 4),
        "coverage_percentage": round(coverage_pct, 1),
        "invalid_mapping_rate_percentage": round(invalid_rate_pct, 1),
        "explanation_completeness_percentage": round(explanation_pct, 1),
        "average_in_memory_latency_ms": round(avg_latency, 2),
        "provider_error_rate_percentage": 0.0,
    }
    return summary, per_scenario_metrics


def main() -> None:
    print("=" * 75)
    print("SIH26101 Stage 4.9: Recommendation Quantitative Evaluation (Hardened)")
    print("=" * 75)

    repo = CompetencyRepository()
    repo.load_all()

    data_dir = BACKEND_DIR / "data"
    registry = ResourceProviderRegistry([
        ACBPLocalCatalogueProvider(data_dir),
        NSSTAPublicProgrammeProvider(data_dir),
        IGOTPublicMetadataProvider(data_dir),
    ])

    engine = RecommendationEngine(repository=repo, provider_registry=registry)

    benchmark_path = data_dir / "synthetic" / "recommendation_benchmark_scenarios.json"
    if not benchmark_path.exists():
        print(f"ERROR: Benchmark file not found at {benchmark_path}")
        sys.exit(1)

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_manifest = json.load(f)

    scenarios = benchmark_manifest.get("scenarios", [])
    print(f"Loaded {len(scenarios)} benchmark scenarios (Version: {benchmark_manifest.get('version')})")
    print(f"Notice: {benchmark_manifest.get('warning', 'Synthetic offline benchmark')}\n")

    # Evaluate Baseline 1: Catalogue Appearance Order
    print("Evaluating Baseline 1 (Catalogue Appearance Order)...")
    b1_summary, b1_per_scn = evaluate_method(engine, scenarios, "baseline_catalogue_order")

    # Evaluate Baseline 2: Naive Gap Match
    print("Evaluating Baseline 2 (Naive Gap Match)...")
    b2_summary, b2_per_scn = evaluate_method(engine, scenarios, "baseline_naive_match")

    # Evaluate Proposed: Transparent Hybrid Explainable
    print("Evaluating Proposed (Transparent Hybrid Explainable)...")
    imp_summary, imp_per_scn = evaluate_method(engine, scenarios, "hybrid_explainable")

    # Compile comprehensive evaluation artifact
    eval_payload = {
        "benchmark_name": benchmark_manifest.get("benchmark_name"),
        "benchmark_version": benchmark_manifest.get("version"),
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_scenarios": len(scenarios),
        "provenance_and_integrity": {
            "label_provenance": benchmark_manifest.get("label_provenance"),
            "methodology": benchmark_manifest.get("methodology_and_construction"),
            "assumptions_and_limitations": benchmark_manifest.get("assumptions_and_limitations"),
            "latency_disclaimer": "Sub-millisecond latencies measure in-memory Python ranking functions and exclude network/database overhead.",
            "claims_qualification": "This benchmark measures information retrieval ranking accuracy against curated topic labels. It does NOT claim statistical significance, real-world skill acquisition, or validated learning efficacy.",
            "warning": benchmark_manifest.get("warning"),
        },
        "aggregate_comparison": {
            "baseline_1_catalogue_order": b1_summary,
            "baseline_2_naive_match": b2_summary,
            "proposed_hybrid_explainable": imp_summary,
            "deltas_vs_baseline_1": {
                "precision_at_3": round(imp_summary["precision_at_3"] - b1_summary["precision_at_3"], 4),
                "precision_at_5": round(imp_summary["precision_at_5"] - b1_summary["precision_at_5"], 4),
                "recall_at_3": round(imp_summary["recall_at_3"] - b1_summary["recall_at_3"], 4),
                "ndcg_at_3": round(imp_summary["ndcg_at_3"] - b1_summary["ndcg_at_3"], 4),
                "ndcg_at_5": round(imp_summary["ndcg_at_5"] - b1_summary["ndcg_at_5"], 4),
                "mrr": round(imp_summary["mrr"] - b1_summary["mrr"], 4),
            },
            "deltas_vs_baseline_2": {
                "precision_at_3": round(imp_summary["precision_at_3"] - b2_summary["precision_at_3"], 4),
                "precision_at_5": round(imp_summary["precision_at_5"] - b2_summary["precision_at_5"], 4),
                "recall_at_3": round(imp_summary["recall_at_3"] - b2_summary["recall_at_3"], 4),
                "ndcg_at_3": round(imp_summary["ndcg_at_3"] - b2_summary["ndcg_at_3"], 4),
                "ndcg_at_5": round(imp_summary["ndcg_at_5"] - b2_summary["ndcg_at_5"], 4),
                "mrr": round(imp_summary["mrr"] - b2_summary["mrr"], 4),
            },
        },
        "per_scenario_results": {
            "proposed_hybrid_explainable": imp_per_scn,
            "baseline_2_naive_match": b2_per_scn,
            "baseline_1_catalogue_order": b1_per_scn,
        },
    }

    # Save to both versioned v2 and canonical output path
    output_dir = data_dir / "interim"
    output_dir.mkdir(parents=True, exist_ok=True)
    v2_path = output_dir / "recommendation_evaluation_metrics_v2.json"
    canonical_path = output_dir / "recommendation_evaluation_metrics.json"

    with open(v2_path, "w", encoding="utf-8") as f:
        json.dump(eval_payload, f, indent=2, ensure_ascii=False)
    with open(canonical_path, "w", encoding="utf-8") as f:
        json.dump(eval_payload, f, indent=2, ensure_ascii=False)

    print(f"\nSaved versioned metrics to: {v2_path}")
    print(f"Updated canonical metrics: {canonical_path}\n")

    # Print 3-Way Aggregate Table
    print("| Evaluation Metric | Baseline 1 (Catalogue Order) | Baseline 2 (Naive Match) | Proposed (Hybrid Explainable) | Delta vs B1 | Delta vs B2 |")
    print("|---|---|---|---|---|---|")
    metrics_keys = [
        ("Precision@3", "precision_at_3"),
        ("Precision@5", "precision_at_5"),
        ("Recall@3", "recall_at_3"),
        ("Recall@5", "recall_at_5"),
        ("NDCG@3", "ndcg_at_3"),
        ("NDCG@5", "ndcg_at_5"),
        ("MRR", "mrr"),
        ("Coverage", "coverage_percentage"),
        ("Explanation Completeness", "explanation_completeness_percentage"),
        ("In-Memory Latency", "average_in_memory_latency_ms"),
    ]
    for label, k in metrics_keys:
        v_b1 = b1_summary[k]
        v_b2 = b2_summary[k]
        v_imp = imp_summary[k]
        if "percentage" in k or k == "coverage_percentage":
            s_b1, s_b2, s_imp = f"{v_b1}%", f"{v_b2}%", f"{v_imp}%"
            d1 = f"{v_imp - v_b1:+.1f}%"
            d2 = f"{v_imp - v_b2:+.1f}%"
        elif "latency" in k:
            s_b1, s_b2, s_imp = f"{v_b1:.2f} ms", f"{v_b2:.2f} ms", f"{v_imp:.2f} ms"
            d1 = f"{v_imp - v_b1:+.2f} ms"
            d2 = f"{v_imp - v_b2:+.2f} ms"
        else:
            s_b1, s_b2, s_imp = f"{v_b1:.4f}", f"{v_b2:.4f}", f"{v_imp:.4f}"
            d1 = f"{v_imp - v_b1:+.4f}"
            d2 = f"{v_imp - v_b2:+.4f}"
        print(f"| **{label}** | {s_b1} | {s_b2} | {s_imp} | {d1} | {d2} |")

    # Print Per-Scenario Breakdown for Proposed Method
    print("\n" + "=" * 75)
    print("Per-Scenario Results for Proposed Method (Hybrid Explainable):")
    print("=" * 75)
    print("| Scenario ID | Cadre / Focus | P@3 | P@5 | NDCG@3 | NDCG@5 | MRR | Latency |")
    print("|---|---|---|---|---|---|---|---|")
    for s in imp_per_scn:
        print(f"| {s['scenario_id']} | {s['cadre_role'][:30]} | {s['precision_at_3']:.4f} | {s['precision_at_5']:.4f} | {s['ndcg_at_3']:.4f} | {s['ndcg_at_5']:.4f} | {s['mrr']:.4f} | {s['latency_ms']:.2f} ms |")


if __name__ == "__main__":
    main()
