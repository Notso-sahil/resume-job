import re
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader

from src.config import TEMPLATES_DIR
from src.schemas.models import ResumeProjectPortfolio, CandidateProfile


def escape_latex(text: str) -> str:
    """Escapes characters that have special meaning in LaTeX."""
    if not isinstance(text, str):
        return str(text)

    # Protect backslashes first, then escape other specials
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for orig, repl in replacements:
        text = text.replace(orig, repl)
    return text


def sanitize_project_for_latex(proj):
    """Sanitizes project fields for LaTeX output."""
    copy_proj = proj.model_copy(deep=True)
    copy_proj.project_title = escape_latex(copy_proj.project_title)
    copy_proj.tech_stack = [escape_latex(s) for s in copy_proj.tech_stack]
    copy_proj.xyz_bullets = [escape_latex(b) for b in copy_proj.xyz_bullets]
    return copy_proj


def render_latex(
    portfolio: ResumeProjectPortfolio,
    candidate: Optional[CandidateProfile],
    output_path: str | Path,
) -> Path:
    """
    Renders Jake's Resume LaTeX template into output/resume.tex using Jinja2.
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        comment_start_string="/*%",
        comment_end_string="%*/",
        autoescape=False,
    )
    template = env.get_template("jakes_resume.tex.jinja2")

    # Sanitize candidate profile if available
    sanitized_candidate = None
    if candidate:
        sanitized_candidate = candidate.model_copy(deep=True)
        sanitized_candidate.full_name = escape_latex(sanitized_candidate.full_name)
        sanitized_candidate.title = escape_latex(sanitized_candidate.title)
        sanitized_candidate.professional_objective = escape_latex(sanitized_candidate.professional_objective)
        if portfolio.tailored_summary:
            sanitized_candidate.tailored_summary = escape_latex(portfolio.tailored_summary)
        elif sanitized_candidate.tailored_summary:
            sanitized_candidate.tailored_summary = escape_latex(sanitized_candidate.tailored_summary)
        for edu in sanitized_candidate.education:
            edu.degree = escape_latex(edu.degree)
            edu.institution = escape_latex(edu.institution)
            edu.year_range = escape_latex(edu.year_range)
            if edu.details:
                edu.details = escape_latex(edu.details)
        for exp in sanitized_candidate.experience:
            exp.role = escape_latex(exp.role)
            exp.organization = escape_latex(exp.organization)
            exp.period = escape_latex(exp.period)
            if exp.location:
                exp.location = escape_latex(exp.location)
            exp.bullets = [escape_latex(b) for b in exp.bullets]

    sanitized_projects = [sanitize_project_for_latex(p) for p in portfolio.projects]

    rendered_code = template.render(
        candidate=sanitized_candidate,
        projects=sanitized_projects,
        jd_analysis=portfolio.jd_analysis,
        portfolio=portfolio,
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(rendered_code)

    return out
