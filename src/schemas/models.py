from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

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
    organization: str            # e.g. "Tech Systems Inc."
    period: str                  # e.g. "June - August"
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class CandidateProfile(BaseModel):
    """
    Extracted and enriched candidate profile.
    Example:
      full_name              = "Jane Doe"
      title                  = "AI Systems Engineer"
      phone                  = "+1 (555) 012-3456"
      email                  = "jane.doe@example.com"
      linkedin               = "linkedin.com/in/janedoe"
      github                 = "github.com/janedoe"
      professional_objective = "Systems engineer specializing in distributed architectures..."
      education              = [EducationEntry(...)]
      experience             = [ExperienceEntry(role="AI Engineering Intern", organization="Tech Systems Inc.", period="June - August")]
    """
    full_name: str
    title: str                           # professional headline from resume header
    phone: str
    email: str
    linkedin: Optional[str] = None
    github: Optional[str] = None
    professional_objective: str          # base summary / objective paragraph from uploaded resume
    tailored_summary: Optional[str] = None  # dynamically synthesized summary blending candidate background + target JD
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)

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
    project_title: str
    archetype: str  # "Core Domain" | "Distributed Systems" | "DevTools / Infra"
    high_level_architecture: str
    tech_stack: List[str]
    core_bottleneck: str
    technical_solution: str
    live_link: Optional[str] = None
    quantified_impact_metrics: List[str]
    trade_offs: List[ArchitecturalTradeOff]
    failure_modes: List[FailureModeAnalysis]
    xyz_bullets: List[str]
    interview_defense_qna: List[Dict[str, str]]

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
