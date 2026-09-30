from pathlib import Path
from typing import Any, Dict, List
from jinja2 import Environment, FileSystemLoader

from src.config import TEMPLATES_DIR
from src.schemas.models import ResumeProjectPortfolio


def _build_dossier_context(portfolio: ResumeProjectPortfolio) -> Dict[str, Any]:
    """
    Builds the flat Jinja2 context required by interview_dossier.md.jinja2.

    Maps structured portfolio fields to the flat variable schema expected by the
    new template: company_name, role_title, domain, candidate_name, ats_score,
    target_keywords, core_engineering_challenges, projects (with is_anchor),
    and interview_questions.
    """
    jd = portfolio.jd_analysis
    candidate = portfolio.candidate_profile
    audit = portfolio.evaluator_audit

    # Flat JD fields
    company_name: str = getattr(jd, "company_name", "Target Company") if jd else "Target Company"
    role_title: str = getattr(jd, "role_title", "Software Engineer") if jd else "Software Engineer"
    domain: str = getattr(jd, "domain", "Distributed Systems") if jd else "Distributed Systems"
    target_keywords: List[str] = getattr(jd, "target_keywords", []) if jd else []
    core_engineering_challenges: List[str] = (
        getattr(jd, "core_engineering_challenges", []) if jd else []
    )

    # Candidate identity
    candidate_name: str = (
        getattr(candidate, "full_name", "Candidate") if candidate else "Candidate"
    )

    # ATS coverage score (coerced to int percentage string)
    ats_score: str = (
        str(int(getattr(audit, "ats_coverage_score", 92))) if audit else "92"
    )

    # Enrich each project dict with normalised is_anchor bool
    raw_projects = portfolio.projects if portfolio.projects else []
    projects: List[Any] = []
    for proj in raw_projects if isinstance(raw_projects, list) else [raw_projects]:
        if hasattr(proj, "model_dump"):
            proj_dict = proj.model_dump()
        elif isinstance(proj, dict):
            proj_dict = proj
        else:
            proj_dict = {}
        # Normalise anchor flag — field may be is_anchor_project or is_anchor
        proj_dict["is_anchor"] = proj_dict.get("is_anchor_project") or proj_dict.get(
            "is_anchor", False
        )
        projects.append(proj_dict)

    # Interview Q&A — sourced from per-project interview_defense_qna if present
    interview_questions: List[Any] = []
    for proj_dict in projects:
        qna_list = proj_dict.get("interview_defense_qna") or []
        interview_questions.extend(qna_list)

    return {
        "company_name": company_name,
        "role_title": role_title,
        "domain": domain,
        "candidate_name": candidate_name,
        "ats_score": ats_score,
        "target_keywords": target_keywords,
        "core_engineering_challenges": core_engineering_challenges,
        "projects": projects,
        "interview_questions": interview_questions,
    }


def render_dossier(
    portfolio: ResumeProjectPortfolio,
    output_path: str | Path,
) -> Path:
    """
    Renders the Interview Defense Dossier markdown document using Jinja2.

    Builds a flat context dict from the structured portfolio and passes it to
    interview_dossier.md.jinja2, which expects flat variables (company_name,
    role_title, candidate_name, ats_score, target_keywords, projects, etc.)
    rather than nested model objects.
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    template = env.get_template("interview_dossier.md.jinja2")

    context = _build_dossier_context(portfolio)
    rendered = template.render(**context)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(rendered)

    return out
