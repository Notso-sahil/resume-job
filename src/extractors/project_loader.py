import re
from pathlib import Path
from typing import List, Dict, Any

RE_JADX_PATTERNS = [
    r"\bre-?jadx\b",
    r"\bjadx\b",
    r"\breverse[- ]engineering agent\b",
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
        raw_title = lines[0].strip()

        # Extraction logic for technologies, overview, metrics
        tech_match = re.search(r"\*\*Technologies:\*\*\s*(.+)", block)
        technologies = [t.strip() for t in tech_match.group(1).split(",")] if tech_match else []

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
            "overview": overview,
            "bullets": bullets,
            "is_anchor": False,
            "is_synthesized": False,
        })

    return eligible_projects
