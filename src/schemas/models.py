import re
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional, Literal, Any

# ---------------------------------------------------------------------------
# Candidate Profile — extracted from the user's resume PDF
# ---------------------------------------------------------------------------

class EducationEntry(BaseModel):
    degree: str                  # e.g. "B.Tech — Artificial Intelligence & Machine Learning"
    institution: str             # e.g. "University / College"
    year_range: str              # e.g. "2020 – 2024"
    details: Optional[str] = None  # e.g. "Honors / Focus Area"


class ExperienceEntry(BaseModel):
    role: str                    # e.g. "Software Engineering Intern"
    company: str = ""            # Primary field
    organization: str = ""       # Alias — kept for renderer & template compat
    location: Optional[str] = "New Delhi, India"
    start_date: str = ""
    end_date: str = ""
    period: str = ""             # Alias — kept for renderer & template compat
    technologies: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)
    is_internship: bool = True

    @model_validator(mode="before")
    @classmethod
    def sync_experience_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        company = data.get("company") or data.get("organization") or ""
        data["company"] = company
        data["organization"] = company

        start_date = data.get("start_date") or ""
        end_date = data.get("end_date") or ""
        period = data.get("period") or ""

        if start_date and end_date and not period:
            data["period"] = f"{start_date} – {end_date}"
        elif period and (not start_date or not end_date):
            parts = re.split(r"\s*[–—-]\s*", period, maxsplit=1)
            if len(parts) == 2:
                data["start_date"] = parts[0].strip()
                data["end_date"] = parts[1].strip()
            else:
                data["start_date"] = period
                data["end_date"] = ""

        return data


# ---------------------------------------------------------------------------
# Project & Architecture Specs
# ---------------------------------------------------------------------------

class ArchitecturalTradeOff(BaseModel):
    decision: str
    chosen_technology: str
    rejected_technology: str
    justification: str


class FailureModeAnalysis(BaseModel):
    scenario: str
    impact: str
    mitigation_strategy: str


class ProjectSpec(BaseModel):
    project_title: str = ""
    title: str = ""
    archetype: str = "Core Domain"  # "Core Domain" | "Distributed Systems" | "DevTools / Infra"
    high_level_architecture: str = ""
    tech_stack: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    core_bottleneck: str = ""
    technical_solution: str = ""
    live_link: Optional[str] = None
    quantified_impact_metrics: List[str] = Field(default_factory=list)
    trade_offs: List[ArchitecturalTradeOff] = Field(default_factory=list)
    failure_modes: List[FailureModeAnalysis] = Field(default_factory=list)
    xyz_bullets: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)
    interview_defense_qna: List[Dict[str, str]] = Field(default_factory=list)
    overview: str = ""
    is_anchor: bool = False
    is_anchor_project: bool = False
    is_synthesized: bool = True

    @model_validator(mode="before")
    @classmethod
    def sync_project_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        title = data.get("title") or data.get("project_title") or ""
        data["title"] = title
        data["project_title"] = title

        tech = data.get("tech_stack") or data.get("technologies") or []
        data["tech_stack"] = tech
        data["technologies"] = tech

        bullets = data.get("xyz_bullets") or data.get("bullets") or []
        data["xyz_bullets"] = bullets
        data["bullets"] = bullets

        is_anchor = bool(data.get("is_anchor_project") or data.get("is_anchor") or False)
        data["is_anchor"] = is_anchor
        data["is_anchor_project"] = is_anchor

        return data


class CandidateProfile(BaseModel):
    """
    Extracted and enriched candidate profile.
    """
    full_name: str = ""
    name: str = ""
    title: str = ""                           # professional headline from resume header
    phone: str = ""
    email: str = ""
    linkedin: Optional[str] = None
    github: Optional[str] = None
    professional_objective: str = ""          # base summary / objective paragraph from uploaded resume
    tailored_summary: Optional[str] = None  # dynamically synthesized summary blending candidate background + target JD
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectSpec] = Field(default_factory=list)
    real_projects: Optional[List[ProjectSpec]] = Field(
        default_factory=list,
        description="Verified projects loaded from projects.md used for Slot 1 anchor selection; RE-jadx strictly excluded.",
    )

    @model_validator(mode="before")
    @classmethod
    def sync_profile_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        name = data.get("name") or data.get("full_name") or ""
        data["name"] = name
        data["full_name"] = name
        return data


# ---------------------------------------------------------------------------
# JD Deconstruction Schema
# ---------------------------------------------------------------------------

class JDDeconstruction(BaseModel):
    company_name: str = "company"
    role_title: str
    seniority_level: str
    domain: str
    primary_languages: List[str]
    frameworks: List[str]
    databases_and_storage: List[str]
    infrastructure_and_cloud: List[str]
    core_engineering_challenges: List[str]
    target_keywords: List[str]
    soft_skills: Optional[List[str]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Evaluation & Audit
# ---------------------------------------------------------------------------

class EvaluatorScore(BaseModel):
    ats_coverage_score: float = Field(description="Percentage between 0.0 and 100.0")
    metric_plausibility_score: float = Field(description="Score between 0.0 and 10.0")
    stack_cohesion_score: float = Field(description="Score between 0.0 and 10.0")
    passed_all_gates: bool
    critique_feedback: Optional[str] = None


class OutputFormat(BaseModel):
    format: Literal["docx", "pdf", "latex"] = "pdf"


# ---------------------------------------------------------------------------
# Final Resume Portfolio Aggregation
# ---------------------------------------------------------------------------

class ResumeProjectPortfolio(BaseModel):
    jd_analysis: JDDeconstruction
    projects: List[ProjectSpec]
    evaluator_audit: EvaluatorScore
    candidate_profile: Optional[CandidateProfile] = None
    tailored_summary: Optional[str] = None    # dynamically tailored professional summary
    docx_output_path: Optional[str] = None    # path to generated .docx
    pdf_output_path: Optional[str] = None     # path to generated .pdf
    latex_output_path: Optional[str] = None   # path to generated .tex (Jake's Resume)
    dossier_output_path: Optional[str] = None # path to generated company question dossier .md
    archive_pdf_path: Optional[str] = None    # archived path in output/old/
    archive_dossier_path: Optional[str] = None# archived path in output/old/
    markdown_summary: str
    portfolio_json_path: Optional[str] = None
