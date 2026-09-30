import re
from pathlib import Path
from typing import List, Dict, Any

RE_JADX_PATTERNS = [
    r"\bre-?jadx\b",
    r"\bjadx\b",
    r"\bapk\s+forensic\b",
    r"\breverse[- ]engineering\s+agent\b",
]


def is_re_jadx_project(title: str, overview: str = "") -> bool:
    """
    Deterministically identifies if a project entry corresponds to the RE-jadx project.
    """
    combined_text = f"{title} {overview}".lower()
    for pattern in RE_JADX_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return True
    return False


def load_eligible_projects_from_markdown(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parses projects.md and returns strictly non-internship projects.
    RE-jadx is explicitly filtered out of this candidate list.
    """
    content = file_path.read_text(encoding="utf-8")
    project_blocks = re.split(r"\n##\s+\d+\.\s+", content)

    eligible_projects = []

    for block in project_blocks:
        if not block.strip() or block.startswith("#"):
            continue

        lines = block.strip().split("\n")
        raw_title = re.sub(r"^#+\s*(\d+\.\s*)?", "", lines[0]).strip()

        # Extraction logic for technologies, overview, metrics
        tech_match = re.search(r"\*\*Technologies:\*\*\s*(.+)", block)
        technologies = [t.strip() for t in tech_match.group(1).split(",") if t.strip()] if tech_match else []

        overview_match = re.search(r"\*\*Overview:\*\*\s*\n*(.+?)(?=\n\*\*|\n\*|\Z)", block, re.DOTALL)
        overview = overview_match.group(1).strip() if overview_match else ""

        # Bullet extraction
        raw_bullets = re.findall(r"\*\s+\*\*([^*]+)\*\*:\s*(.+)", block)
        bullets = [f"**{title}**: {desc.strip()}" for title, desc in raw_bullets]
        if not bullets:
            bullets = [line.strip().lstrip("* ") for line in lines if line.strip().startswith("* ")]

        # Hard isolation check: Reject RE-jadx from candidate project list
        if is_re_jadx_project(raw_title, overview):
            continue

        eligible_projects.append({
            "title": raw_title,
            "technologies": technologies,
            "tech_stack": technologies,
            "overview": overview,
            "bullets": bullets,
            "xyz_bullets": bullets,
            "is_re_jadx": False,
            "is_anchor": False,
            "is_synthesized": False,
        })

    return eligible_projects


def score_project_for_jd(project: Dict[str, Any], jd: Any) -> float:
    """
    Scores a projects.md entry against a target JD for Slot 1 anchor selection.
    Returns a float 0.0 - 100.0 representing role-fit density.
    """
    score = 0.0
    # 1. Tech stack overlap (40 points max)
    primary_languages = getattr(jd, "primary_languages", []) or []
    frameworks = getattr(jd, "frameworks", []) or []
    databases_and_storage = getattr(jd, "databases_and_storage", []) or []
    infrastructure_and_cloud = getattr(jd, "infrastructure_and_cloud", []) or []

    jd_stack = set(
        kw.lower()
        for kw in (
            primary_languages
            + frameworks
            + databases_and_storage
            + infrastructure_and_cloud
        )
    )
    proj_tech = set(t.lower() for t in project.get("technologies", []))
    overlap = jd_stack & proj_tech
    score += min(40.0, len(overlap) * 5.0)

    # 2. Keyword density in overview + bullets (40 points max)
    corpus = (
        project.get("overview", "")
        + " "
        + " ".join(project.get("bullets", []))
    ).lower()
    target_keywords = getattr(jd, "target_keywords", []) or []
    kw_hits = sum(1 for kw in target_keywords if kw.lower() in corpus)
    score += min(40.0, kw_hits * 2.5)

    # 3. Domain alignment bonus (20 points max)
    domain_val = getattr(jd, "domain", "") or ""
    domain_terms = domain_val.lower().split()
    domain_hits = sum(1 for t in domain_terms if len(t) > 2 and t in corpus)
    score += min(20.0, domain_hits * 4.0)

    return round(score, 2)


def select_anchor_project(jd: Any, projects_md_path: Path) -> Dict[str, Any]:
    """
    Loads all eligible projects from projects.md (excluding RE-jadx),
    scores each against the JD, and returns the highest-scoring project
    formatted as a dict compatible with ProjectSpec.
    Falls back to project #1 (Omni-Channel D2C Agent) if scoring is flat.
    """
    projects = load_eligible_projects_from_markdown(projects_md_path)
    if not projects:
        return {}  # caller handles fallback
    scored = [(score_project_for_jd(p, jd), p) for p in projects]
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_project = scored[0]
    best_project["is_anchor"] = True
    best_project["is_synthesized"] = False
    return best_project
