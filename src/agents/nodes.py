import json
import re
import shutil
import unicodedata
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.config import get_llm, MAX_ITERATIONS, OUTPUT_DIR
from src.schemas.models import (
    JDDeconstruction,
    ProjectSpec,
    EvaluatorScore,
    ResumeProjectPortfolio,
)
from src.agents.state import AgentState
from src.prompts.extraction_prompts import JD_EXTRACTION_PROMPT
from src.prompts.synthesis_prompts import (
    build_synthesis_prompt,
    build_fallback_projects,
    fallback_synthesize,
    resolve_archetypes,
    ARCHETYPE_REGISTRY,
)
from src.evaluators.sanity_checker import audit_portfolio


def slugify_company(company_name: Optional[str]) -> str:
    """
    Normalizes company name to a safe filename slug.
    e.g. 'Naïve' -> 'naive', 'Google DeepMind' -> 'google_deepmind'.
    Defaults to 'company' if empty or None.
    """
    if not company_name:
        return "company"
    text = unicodedata.normalize("NFKD", str(company_name)).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return slug or "company"


def deconstruct_jd_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: JD Deconstruction & Leveler.
    Extracts tech stack, implicit scale, seniority, and high-priority ATS keywords.
    """
    DEFAULT_SOFT_SKILLS = [
        "Cross-Functional Collaboration",
        "High Ownership & Craft",
        "First-Principles Problem Solving",
        "Fast Prototyping",
        "Root Cause Analysis",
    ]

    # If a pre-configured job was provided in state, use it directly
    job_config = state.get("job_config")
    if job_config and "jd_analysis" in job_config:
        jd_analysis = job_config["jd_analysis"]
        if not getattr(jd_analysis, "soft_skills", None):
            jd_analysis.soft_skills = DEFAULT_SOFT_SKILLS
        return {"jd_analysis": jd_analysis}

    raw_jd = state.get("raw_jd", "")
    llm = get_llm()

    try:
        if hasattr(llm, "with_structured_output"):
            structured_llm = llm.with_structured_output(JDDeconstruction)
            prompt = JD_EXTRACTION_PROMPT.format(raw_jd=raw_jd)
            jd_analysis = structured_llm.invoke(prompt)
            if isinstance(jd_analysis, dict):
                jd_analysis = JDDeconstruction(**jd_analysis)
            if not getattr(jd_analysis, "soft_skills", None):
                jd_analysis.soft_skills = DEFAULT_SOFT_SKILLS
            return {"jd_analysis": jd_analysis}
    except Exception:
        pass

    # Fallback/Native deconstruction
    fallback_analysis = fallback_synthesize(raw_jd, JDDeconstruction)
    if not getattr(fallback_analysis, "soft_skills", None):
        fallback_analysis.soft_skills = DEFAULT_SOFT_SKILLS
    return {"jd_analysis": fallback_analysis}


def synthesize_projects_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Archetype Mapping & Cohesion Synthesis.
    Resolves the best 3 project archetypes for the JD domain, then generates
    deep architectural specs & XYZ bullets via LLM or JD-adaptive fallback.
    Incorporates critique history if self-correcting.
    """
    iteration_count = state.get("iteration_count", 0) + 1

    # If a pre-configured job provided fallback projects, use them directly
    job_config = state.get("job_config")
    if job_config and job_config.get("fallback_projects"):
        return {
            "candidate_projects": job_config["fallback_projects"],
            "iteration_count": iteration_count,
        }

    jd_analysis = state.get("jd_analysis")
    critique_history = state.get("critique_history", [])
    critiques_formatted = "\n".join(f"- {c}" for c in critique_history) if critique_history else "None (Initial iteration)"

    llm = get_llm()

    try:
        if hasattr(llm, "with_structured_output"):
            from pydantic import BaseModel
            class ProjectsContainer(BaseModel):
                projects: List[ProjectSpec]

            structured_llm = llm.with_structured_output(ProjectsContainer)
            # Build JD-aware dynamic prompt (resolves archetypes, injects JD stack)
            full_prompt = build_synthesis_prompt(jd_analysis, critiques_formatted)
            result = structured_llm.invoke(full_prompt)
            if hasattr(result, "projects") and len(result.projects) == 3:
                return {
                    "candidate_projects": result.projects,
                    "iteration_count": iteration_count,
                }
    except Exception:
        pass

    # JD-adaptive fallback: builds domain-specific projects from JD stack
    fallback_projects = build_fallback_projects(jd_analysis)
    return {
        "candidate_projects": fallback_projects,
        "iteration_count": iteration_count,
    }


def evaluate_portfolio_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: Evaluator-Optimizer Critique Loop.
    Executes hybrid deterministic ATS calculation and hardware sanity audit.
    """
    candidate_projects = state.get("candidate_projects", [])
    jd_analysis = state.get("jd_analysis")
    target_keywords = jd_analysis.target_keywords if jd_analysis else []

    candidate_profile = state.get("candidate_profile")
    extra_texts = []
    if candidate_profile:
        if candidate_profile.tailored_summary:
            extra_texts.append(candidate_profile.tailored_summary)
        elif candidate_profile.professional_objective:
            extra_texts.append(candidate_profile.professional_objective)
        for exp in candidate_profile.experience:
            extra_texts.extend(exp.bullets)
    if jd_analysis:
        extra_texts.extend(jd_analysis.primary_languages)
        extra_texts.extend(jd_analysis.frameworks)
        extra_texts.extend(jd_analysis.databases_and_storage)
        extra_texts.extend(jd_analysis.infrastructure_and_cloud)

    eval_score = audit_portfolio(candidate_projects, target_keywords, extra_texts=extra_texts)

    critique_history = list(state.get("critique_history", []))
    if eval_score.critique_feedback:
        critique_history.append(eval_score.critique_feedback)

    return {
        "evaluation_result": eval_score,
        "critique_history": critique_history,
    }


def generate_artifacts_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 4: Resume Artifact Engine.
    Dispatches to docx_renderer, pdf_renderer, or latex_renderer based on output_format.
    Only generates the single requested format (defaults to pdf).
    Archives existing outputs to output/old/ before generating new files.
    Also produces the Interview Defense Dossier and structured JSON dump.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    old_dir = OUTPUT_DIR / "old"
    old_dir.mkdir(parents=True, exist_ok=True)

    # 1. Archive prior generation files to output/old/
    # Moves any existing *_resume.* and *_ques.md from output/ into output/old/
    for old_file in list(OUTPUT_DIR.glob("*_resume.*")) + list(OUTPUT_DIR.glob("*_ques.md")):
        if old_file.is_file() and not old_file.name.endswith("_temp.docx"):
            target = old_dir / old_file.name
            if target.exists():
                try:
                    target.unlink()
                except Exception:
                    pass
            try:
                shutil.move(str(old_file), str(target))
            except Exception:
                pass

    # Clean up legacy duplicate canonical files if present
    for legacy in ["resume.docx", "resume.pdf", "resume.tex", "interview_defense_dossier.md"]:
        legacy_path = OUTPUT_DIR / legacy
        if legacy_path.is_file():
            try:
                legacy_path.unlink()
            except Exception:
                pass

    jd_analysis = state.get("jd_analysis")
    candidate_projects = state.get("candidate_projects", [])
    evaluation_result = state.get("evaluation_result")
    candidate_profile = state.get("candidate_profile")
    output_format_obj = state.get("output_format")

    selected_format = output_format_obj.format if output_format_obj else "pdf"

    # Synthesize tailored professional summary (2-3 sentences, blending background + JD)
    tailored_summary = None
    if candidate_profile:
        from src.prompts.synthesis_prompts import synthesize_tailored_summary
        from src.prompts.experience_prompts import synthesize_tailored_experience

        job_config = state.get("job_config") or {}
        summary_override = job_config.get("tailored_summary_override")
        tailored_summary = synthesize_tailored_summary(
            candidate_profile.professional_objective,
            jd_analysis,
            llm=get_llm(),
            summary_override=summary_override,
        )
        candidate_profile.tailored_summary = tailored_summary

        # Dynamically tailor work experience bullets to align with target JD
        exp_override = job_config.get("experience_override")
        candidate_profile.experience = synthesize_tailored_experience(
            candidate_profile.experience,
            jd_analysis,
            llm=get_llm(),
            experience_override=exp_override,
        )

    # Assemble portfolio model
    portfolio = ResumeProjectPortfolio(
        jd_analysis=jd_analysis,
        projects=candidate_projects,
        evaluator_audit=evaluation_result,
        candidate_profile=candidate_profile,
        tailored_summary=tailored_summary,
        markdown_summary=f"Portfolio synthesized for {jd_analysis.role_title if jd_analysis else 'Role'}",
    )

    from src.renderers.docx_renderer import render_docx
    from src.renderers.pdf_renderer import render_pdf
    from src.renderers.latex_renderer import render_latex
    from src.renderers.dossier_renderer import render_dossier

    company_slug = slugify_company(getattr(jd_analysis, "company_name", None))

    company_docx_path = OUTPUT_DIR / f"{company_slug}_resume.docx"
    company_pdf_path = OUTPUT_DIR / f"{company_slug}_resume.pdf"
    company_latex_path = OUTPUT_DIR / f"{company_slug}_resume.tex"
    company_dossier_path = OUTPUT_DIR / f"{company_slug}_ques.md"

    docx_path = None
    pdf_path = None
    latex_path = None

    # Render ONLY requested format
    if selected_format == "docx":
        docx_path = render_docx(portfolio, candidate_profile, company_docx_path)
        portfolio.docx_output_path = str(company_docx_path)

    elif selected_format == "pdf":
        temp_docx_path = OUTPUT_DIR / f"{company_slug}_resume_temp.docx"
        render_docx(portfolio, candidate_profile, temp_docx_path)
        pdf_path = render_pdf(temp_docx_path, company_pdf_path)
        if temp_docx_path.exists():
            try:
                temp_docx_path.unlink()
            except Exception:
                pass
        portfolio.pdf_output_path = str(company_pdf_path)

    elif selected_format == "latex":
        latex_path = render_latex(portfolio, candidate_profile, company_latex_path)
        portfolio.latex_output_path = str(company_latex_path)

    # Render Interview Defense Dossier
    dossier_path = render_dossier(portfolio, company_dossier_path)
    portfolio.dossier_output_path = str(company_dossier_path)

    # Save full structured JSON
    json_path = OUTPUT_DIR / "portfolio_data.json"
    portfolio.portfolio_json_path = str(json_path)
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(portfolio.model_dump_json(indent=2))

    return {
        "company_slug": company_slug,
        "final_docx_path": str(company_docx_path) if docx_path else None,
        "final_pdf_path": str(company_pdf_path) if pdf_path else None,
        "final_latex_path": str(company_latex_path) if latex_path else None,
        "final_dossier": str(company_dossier_path),
        "archived_pdf_path": str(old_dir / f"{company_slug}_resume.pdf") if (old_dir / f"{company_slug}_resume.pdf").exists() else None,
        "archived_dossier_path": str(old_dir / f"{company_slug}_ques.md") if (old_dir / f"{company_slug}_ques.md").exists() else None,
    }
