import tempfile
from pathlib import Path
from src.schemas.models import (
    ResumeProjectPortfolio,
    CandidateProfile,
    EducationEntry,
    JDDeconstruction,
    EvaluatorScore,
    ProjectSpec,
)
from src.prompts.synthesis_prompts import fallback_synthesize
from src.renderers.docx_renderer import render_docx
from src.renderers.latex_renderer import render_latex
from src.renderers.dossier_renderer import render_dossier


def get_test_portfolio():
    candidate = CandidateProfile(
        full_name="Alex Rivera",
        title="AI Engineer",
        phone="+1 (555) 234-5678",
        email="alex.rivera@example.com",
        linkedin="linkedin.com/in/alexrivera",
        github="github.com/alexrivera",
        professional_objective="Passionate AI Engineer building agentic systems.",
        education=[
            EducationEntry(
                degree="B.S. - Computer Science",
                institution="State University",
                year_range="2020 - 2024",
            )
        ],
    )
    jd_analysis = fallback_synthesize("", JDDeconstruction)
    projects = fallback_synthesize("", ProjectSpec)
    eval_audit = EvaluatorScore(
        ats_coverage_score=94.0,
        metric_plausibility_score=9.2,
        stack_cohesion_score=9.5,
        passed_all_gates=True,
    )
    portfolio = ResumeProjectPortfolio(
        jd_analysis=jd_analysis,
        projects=projects,
        evaluator_audit=eval_audit,
        candidate_profile=candidate,
        markdown_summary="Test portfolio",
    )
    return portfolio, candidate


def test_render_docx():
    portfolio, candidate = get_test_portfolio()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "test_resume.docx"
        res = render_docx(portfolio, candidate, out_file)
        assert res.exists()
        assert res.stat().st_size > 1000


def test_render_latex():
    portfolio, candidate = get_test_portfolio()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "test_resume.tex"
        res = render_latex(portfolio, candidate, out_file)
        assert res.exists()
        with open(res, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Alex Rivera" in content
            # Assert structural LaTeX macros exist (not specific project names)
            assert r"\resumeSubheading" in content
            assert r"\resumeProjectHeading" in content


def test_render_dossier():
    portfolio, _ = get_test_portfolio()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "test_dossier.md"
        res = render_dossier(portfolio, out_file)
        assert res.exists()
        with open(res, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Technical Interview Defense Dossier" in content
            assert "Architectural Trade-offs" in content
            assert "5 Probing Interview Questions" in content


def test_renderers_fallback_with_no_candidate_profile():
    jd = fallback_synthesize("", JDDeconstruction)
    projects = fallback_synthesize("", ProjectSpec)
    eval_score = fallback_synthesize("", EvaluatorScore)
    portfolio = ResumeProjectPortfolio(
        jd_analysis=jd,
        projects=projects,
        evaluator_audit=eval_score,
        candidate_profile=None,
        tailored_summary="Passionate systems engineer.",
        markdown_summary="Summary",
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "test.tex"
        docx_path = Path(tmpdir) / "test.docx"
        render_latex(portfolio, None, tex_path)
        render_docx(portfolio, None, docx_path)

        tex_content = tex_path.read_text(encoding="utf-8")
        assert "FIRST LAST" in tex_content
        assert "+1 (555) 012-3456" in tex_content
        assert "candidate@example.com" in tex_content
        assert "sahil" not in tex_content.lower()
        assert "8700122453" not in tex_content
        assert "ifso" not in tex_content.lower()

