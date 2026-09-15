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
