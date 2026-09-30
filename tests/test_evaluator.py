import pytest
from src.evaluators.ats_scorer import score_ats_coverage, is_ats_passing
from src.evaluators.sanity_checker import (
    check_metric_plausibility,
    check_stack_cohesion,
    audit_portfolio,
)
from src.prompts.synthesis_prompts import fallback_synthesize, build_fallback_projects
from src.schemas.models import ProjectSpec, JDDeconstruction


def test_ats_scorer_full_match():
    keywords = ["FastAPI", "LangGraph", "Kafka", "PostgreSQL", "Redis"]
    bullets = [
        "Architected an asynchronous FastAPI and LangGraph pipeline.",
        "Partitioned Kafka streams and optimized PostgreSQL queries with Redis caching.",
    ]
    score, matched, missing = score_ats_coverage(keywords, bullets)
    assert score == 100.0
    assert len(matched) == 5
    assert len(missing) == 0
    assert is_ats_passing(score)


def test_ats_scorer_partial_match():
    keywords = ["FastAPI", "Kubernetes", "Rust", "C++", "Terraform"]
    bullets = ["Engineered a FastAPI service deployed with Docker."]
    score, matched, missing = score_ats_coverage(keywords, bullets)
    assert score == 20.0  # 1 of 5
    assert not is_ats_passing(score)
    assert "Kubernetes" in missing


def _make_distributed_jd():
    """Shared JD fixture with distributed-systems keywords for evaluator tests."""
    return JDDeconstruction(
        company_name="TestCo",
        role_title="Senior AI Platform Engineer",
        seniority_level="Senior",
        domain="Agentic AI Systems & Distributed Backend",
        primary_languages=["Python"],
        frameworks=["FastAPI", "LangGraph"],
        databases_and_storage=["PostgreSQL", "Redis", "Kafka", "Qdrant"],
        infrastructure_and_cloud=["Docker"],
        core_engineering_challenges=["Managing distributed state", "High-throughput vector indexing"],
        target_keywords=["FastAPI", "LangGraph", "Python", "Redis", "Kafka", "Qdrant", "PostgreSQL"],
    )


def test_sanity_checker_valid_portfolio():
    projects = build_fallback_projects(_make_distributed_jd())
    assert len(projects) == 3
    # All 3 archetypes must be distinct
    archetypes = {p.archetype for p in projects}
    assert len(archetypes) == 3

    score, issues = check_metric_plausibility(projects)
    assert score >= 8.0
    assert len(issues) == 0


def test_sanity_checker_invalid_power_verb():
    projects = build_fallback_projects(_make_distributed_jd())
    # Mutate first bullet with unapproved verb
    projects[0].xyz_bullets[0] = "Assisted with building an agent pipeline, improving metrics by 20%."
    score, issues = check_metric_plausibility(projects)
    assert any("approved engineering power verb" in i for i in issues)


def test_sanity_checker_forbidden_phrase():
    projects = build_fallback_projects(_make_distributed_jd())
    projects[0].xyz_bullets[0] = "Architected a system which improved efficiency by 30% by refactoring queries."
    score, issues = check_metric_plausibility(projects)
    assert any("Vague phrase detected" in i for i in issues)


def test_audit_portfolio_end_to_end():
    # Use build_fallback_projects with a JD that matches the keywords being tested
    jd = _make_distributed_jd()
    projects = build_fallback_projects(jd)
    keywords = ["FastAPI", "LangGraph", "Python", "Redis", "Kafka", "Qdrant", "PostgreSQL"]
    # Pass JD stack fields as extra_texts so ATS scoring includes the known-good stack
    extra_texts = (
        jd.primary_languages
        + jd.frameworks
        + jd.databases_and_storage
        + jd.infrastructure_and_cloud
    )
    audit = audit_portfolio(projects, keywords, extra_texts=extra_texts)

    assert audit.ats_coverage_score >= 85.0
    assert audit.metric_plausibility_score >= 8.0
    assert audit.passed_all_gates is True


from src.evaluator.sanity_checker import PortfolioSanityChecker


def test_sanity_checker_rejects_todo_placeholders():
    """Ensure bullets containing [TODO] or placeholder strings fail validation."""
    invalid_bullet = "Developed an autonomous agent, achieving [TODO: add your real measured metric here] by using LangGraph."
    result = PortfolioSanityChecker.audit_bullet(invalid_bullet)
    assert result["valid"] is False
    assert "placeholder marker" in result["reason"]


def test_sanity_checker_requires_explicit_metrics():
    """Ensure bullets without quantitative metrics fail validation."""
    unquantified_bullet = "Engineered a low-latency neural ranking pipeline with PyTorch and deployed it via Docker containers."
    result = PortfolioSanityChecker.audit_bullet(unquantified_bullet)
    assert result["valid"] is False
    assert "lacks an explicit quantitative metric" in result["reason"]


def test_sanity_checker_accepts_valid_xyz_bullet():
    """Ensure fully quantified Google XYZ bullets pass validation."""
    valid_bullet = "Engineered an asynchronous hybrid RAG pipeline using Qdrant and Cohere Rerank, cutting p95 query latency to <180 ms while boosting document recall by 24%."
    result = PortfolioSanityChecker.audit_bullet(valid_bullet)
    assert result["valid"] is True


def test_sanity_checker_validates_three_slot_structure():
    """Verify that portfolio validation strictly enforces Slot 1 Anchor + Slots 2 & 3 Synthesized."""
    valid_portfolio = [
        {
            "title": "Omni-Channel D2C Sales Agent",
            "is_anchor": True,
            "bullets": [
                "Architected multi-turn conversational sales workflows using LangGraph and Redis, sustaining 1,400 QPS under peak traffic.",
                "Engineered Shopify Storefront GraphQL integrations, driving a 26.4% cart recovery rate across 8,500 test sessions.",
                "Integrated Pydantic v2 validation guardrails, reducing invalid JSON schema outputs to <0.4% across production runs.",
            ],
        },
        {
            "title": "Distributed Multi-Agent Consensus Platform",
            "is_anchor": False,
            "is_synthesized": True,
            "bullets": [
                "Built a Raft consensus orchestration layer in Python and gRPC, achieving fault tolerance across 15 active nodes.",
                "Optimized state serialization routines via Protocol Buffers, cutting inter-agent communication latency by 42%.",
                "Constructed an automated Chaos Engineering testing harness, validating zero state corruption over 100,000 injected failures.",
            ],
        },
        {
            "title": "Low-Latency Vector Feature Pipeline",
            "is_anchor": False,
            "is_synthesized": True,
            "bullets": [
                "Architected a streaming vector embedding engine with Kafka and Faiss, processing 12,000 events/sec at sub-50 ms latency.",
                "Configured INT8 quantization with ONNX Runtime, reducing peak inference memory overhead by 62%.",
                "Automated drift detection alerts using Feast feature stores, maintaining feature freshness within a 5-second window.",
            ],
        },
    ]
    audit = PortfolioSanityChecker.audit_portfolio(valid_portfolio)
    assert audit["passed"] is True
    assert audit["error"] is None

