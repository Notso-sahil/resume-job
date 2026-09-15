import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from src.agents.graph import create_resume_graph
from src.schemas.models import OutputFormat, CandidateProfile, EducationEntry
from src.loaders.job_loader import load_job_config, list_available_jobs


def test_output_format_validation():
    # Valid formats
    assert OutputFormat(format="pdf").format == "pdf"
    assert OutputFormat(format="docx").format == "docx"
    assert OutputFormat(format="latex").format == "latex"
    assert OutputFormat().format == "pdf"  # default is pdf

    # "all" is removed and must raise ValidationError
    with pytest.raises(ValidationError):
        OutputFormat(format="all")


def test_pipeline_integration_docx(tmp_path, monkeypatch):
    import src.agents.nodes
    monkeypatch.setattr(src.agents.nodes, "OUTPUT_DIR", tmp_path)

    graph = create_resume_graph()
    candidate = CandidateProfile(
        full_name="Alex Rivera",
        title="AI Systems Engineer",
        phone="+1 (555) 019-2834",
        email="alex.rivera@example.com",
        professional_objective="Systems Engineer building distributed infrastructure.",
        education=[
            EducationEntry(
                degree="B.S. in Computer Science",
                institution="Tech University",
                year_range="2020 - 2024",
            )
        ],
    )
    raw_jd = (
        "Seeking Senior AI Platform Engineer with FastAPI, LangGraph, LangChain, "
        "PostgreSQL, Redis, Kafka, and Docker experience to scale multi-agent systems."
    )

    final_state = graph.invoke({
        "raw_jd": raw_jd,
        "output_format": OutputFormat(format="docx"),
        "candidate_profile": candidate,
        "iteration_count": 0,
        "critique_history": [],
    })

    # Structural invariants: 3 projects synthesized, output files written
    assert "candidate_projects" in final_state
    assert len(final_state["candidate_projects"]) == 3
    # All 3 project archetypes must be distinct
    archetypes = {p.archetype for p in final_state["candidate_projects"]}
    assert len(archetypes) == 3
    assert final_state["final_docx_path"] is not None
    assert final_state["final_dossier"] is not None

    slug = final_state.get("company_slug", "company")
    assert (tmp_path / f"{slug}_resume.docx").exists()
    assert (tmp_path / f"{slug}_ques.md").exists()

    # Invariant: No duplicate canonical files in output
    assert not (tmp_path / "resume.docx").exists()
    assert not (tmp_path / "resume.pdf").exists()
    assert not (tmp_path / "resume.tex").exists()
    assert not (tmp_path / "interview_defense_dossier.md").exists()


def test_slugify_company():
    from src.agents.nodes import slugify_company
    assert slugify_company("Naïve") == "naive"
    assert slugify_company("Google DeepMind") == "google_deepmind"
    assert slugify_company("Stripe, Inc.") == "stripe_inc"
    assert slugify_company(None) == "company"
    assert slugify_company("") == "company"


def test_archival_on_subsequent_run(tmp_path, monkeypatch):
    import src.agents.nodes
    monkeypatch.setattr(src.agents.nodes, "OUTPUT_DIR", tmp_path)

    old_dir = tmp_path / "old"
    old_dir.mkdir(parents=True, exist_ok=True)
    prior_file = old_dir / "prior_company_resume.pdf"
    prior_file.write_text("dummy prior resume")

    # First run generates a file in tmp_path
    first_resume = tmp_path / "first_company_resume.docx"
    first_resume.write_text("first resume content")
    first_ques = tmp_path / "first_company_ques.md"
    first_ques.write_text("first questions")

    # Run pipeline for second job
    state = {
        "raw_jd": "Job at Naïve for AI Research Intern with Python and PyTorch",
        "output_format": OutputFormat(format="docx"),
        "candidate_profile": None,
        "iteration_count": 0,
        "critique_history": [],
    }
    graph = create_resume_graph()
    res = graph.invoke(state)

    # Invariants:
    # 1. Prior file already in old/ was preserved
    assert prior_file.exists()
    # 2. Previous output files from tmp_path were moved to old/
    assert (old_dir / "first_company_resume.docx").exists()
    assert (old_dir / "first_company_ques.md").exists()
    # 3. New output exists in tmp_path
    assert (tmp_path / f"{res['company_slug']}_resume.docx").exists()
    assert (tmp_path / f"{res['company_slug']}_ques.md").exists()


def test_job_config_loading_and_execution(tmp_path, monkeypatch):
    import src.agents.nodes
    import src.loaders.job_loader
    monkeypatch.setattr(src.agents.nodes, "OUTPUT_DIR", tmp_path)

    # Create a fixture job config in tmp_path
    sample_jobs_dir = tmp_path / "jobs"
    sample_jobs_dir.mkdir()
    monkeypatch.setattr(src.loaders.job_loader, "JOBS_DIR", sample_jobs_dir)

    job_data = {
        "company_name": "Acme Corp",
        "role_title": "AI Systems Engineer",
        "seniority_level": "Senior",
        "domain": "Distributed Systems",
        "primary_languages": ["Python"],
        "frameworks": ["FastAPI", "PyTorch"],
        "databases_and_storage": ["Redis"],
        "infrastructure_and_cloud": ["Docker"],
        "core_engineering_challenges": ["Concurrency bottleneck"],
        "target_keywords": ["Python", "FastAPI"],
        "tailored_summary_override": "Custom summary for Acme.",
        "fallback_projects": None,
    }
    with open(sample_jobs_dir / "acme.json", "w", encoding="utf-8") as f:
        json.dump(job_data, f)

    # Load job config via loader
    job_cfg = load_job_config("acme")
    assert job_cfg["jd_analysis"].company_name == "Acme Corp"

    # Run pipeline with job_config in state
    graph = create_resume_graph()
    final_state = graph.invoke({
        "raw_jd": "",
        "output_format": OutputFormat(format="latex"),
        "candidate_profile": None,
        "job_config": job_cfg,
        "iteration_count": 0,
        "critique_history": [],
    })

    assert final_state["company_slug"] == "acme_corp"
    assert (tmp_path / "acme_corp_resume.tex").exists()
    assert (tmp_path / "acme_corp_ques.md").exists()
