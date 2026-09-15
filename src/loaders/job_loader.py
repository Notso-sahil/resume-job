import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.schemas.models import (
    JDDeconstruction,
    ProjectSpec,
    ArchitecturalTradeOff,
    FailureModeAnalysis,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
JOBS_DIR = PROJECT_ROOT / "jobs"


def list_available_jobs() -> List[Dict[str, Any]]:
    if not JOBS_DIR.exists():
        return []

    jobs = []
    for json_file in sorted(JOBS_DIR.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            jobs.append({
                "slug": json_file.stem,
                "company_name": data.get("company_name", json_file.stem.capitalize()),
                "role_title": data.get("role_title", "Engineering Role"),
                "path": json_file,
            })
        except Exception:
            continue
    return jobs


def load_job_config(job_identifier: str | Path) -> Dict[str, Any]:
    target_path: Optional[Path] = None

    candidate_path = Path(job_identifier)
    if candidate_path.is_file():
        target_path = candidate_path
    elif (JOBS_DIR / candidate_path).is_file():
        target_path = JOBS_DIR / candidate_path
    elif (JOBS_DIR / f"{job_identifier}.json").is_file():
        target_path = JOBS_DIR / f"{job_identifier}.json"
    else:
        for item in list_available_jobs():
            if (
                item["slug"].lower() == str(job_identifier).strip().lower()
                or item["company_name"].lower() == str(job_identifier).strip().lower()
            ):
                target_path = item["path"]
                break

    if not target_path or not target_path.exists():
        raise FileNotFoundError(
            f"Job configuration '{job_identifier}' not found in {JOBS_DIR} or as a file."
        )

    with open(target_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    jd_analysis = JDDeconstruction(
        company_name=data.get("company_name", target_path.stem.capitalize()),
        role_title=data.get("role_title", "Software Engineer"),
        seniority_level=data.get("seniority_level", "Engineer"),
        domain=data.get("domain", "Distributed Systems"),
        primary_languages=data.get("primary_languages", ["Python"]),
        frameworks=data.get("frameworks", []),
        databases_and_storage=data.get("databases_and_storage", []),
        infrastructure_and_cloud=data.get("infrastructure_and_cloud", []),
        core_engineering_challenges=data.get("core_engineering_challenges", []),
        target_keywords=data.get("target_keywords", []),
        soft_skills=data.get("soft_skills", []),
    )

    fallback_projects: Optional[List[ProjectSpec]] = None
    if "fallback_projects" in data and data["fallback_projects"]:
        parsed_projects = []
        for p in data["fallback_projects"]:
            if isinstance(p, dict):
                trade_offs = [
                    ArchitecturalTradeOff(**t) if isinstance(t, dict) else t
                    for t in p.get("trade_offs", [])
                ]
                failure_modes = [
                    FailureModeAnalysis(**fm) if isinstance(fm, dict) else fm
                    for fm in p.get("failure_modes", [])
                ]
                proj_dict = dict(p)
                proj_dict["trade_offs"] = trade_offs
                proj_dict["failure_modes"] = failure_modes
                parsed_projects.append(ProjectSpec(**proj_dict))
            elif isinstance(p, ProjectSpec):
                parsed_projects.append(p)
        fallback_projects = parsed_projects

    return {
        "jd_analysis": jd_analysis,
        "tailored_summary_override": data.get("tailored_summary_override"),
        "experience_override": data.get("experience_override"),
        "fallback_projects": fallback_projects,
        "job_slug": target_path.stem,
        "job_config_path": str(target_path),
        "raw_config": data,
    }
