from typing import TypedDict, List, Optional
from src.schemas.models import (
    JDDeconstruction,
    ProjectSpec,
    EvaluatorScore,
    OutputFormat,
    CandidateProfile,
)


class AgentState(TypedDict):
    raw_jd: str
    output_format: OutputFormat          # "docx" | "pdf" | "latex"
    candidate_profile: Optional[CandidateProfile]  # extracted from resume PDF; used by all renderers
    jd_analysis: Optional[JDDeconstruction]
    candidate_projects: Optional[List[ProjectSpec]]
    evaluation_result: Optional[EvaluatorScore]
    iteration_count: int
    critique_history: List[str]
    job_config: Optional[dict]           # loaded from jobs/<company>.json if present
    job_config_path: Optional[str]       # path to the job config JSON file if used
    final_docx_path: Optional[str]       # set if format is "docx"
    final_pdf_path: Optional[str]        # set if format is "pdf"
    final_latex_path: Optional[str]      # set if format is "latex"
    final_dossier: Optional[str]
    company_slug: Optional[str]
    archived_pdf_path: Optional[str]
    archived_dossier_path: Optional[str]
