from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from src.config import TEMPLATES_DIR
from src.schemas.models import ResumeProjectPortfolio


def render_dossier(
    portfolio: ResumeProjectPortfolio,
    output_path: str | Path,
) -> Path:
    """
    Renders the Interview Defense Dossier markdown document using Jinja2.
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    template = env.get_template("interview_dossier.md.jinja2")

    rendered = template.render(
        candidate=portfolio.candidate_profile,
        projects=portfolio.projects,
        jd_analysis=portfolio.jd_analysis,
        audit=portfolio.evaluator_audit,
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(rendered)

    return out
