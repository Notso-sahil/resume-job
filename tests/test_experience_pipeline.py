import pytest
from pathlib import Path
from src.schemas.models import CandidateProfile, ExperienceEntry, ProjectSpec
from src.extractors.project_loader import is_re_jadx_project, load_eligible_projects_from_markdown
from src.extractors.profile_extractor import ensure_re_jadx_in_experience
from src.evaluator.sanity_checker import PortfolioSanityChecker


def test_re_jadx_detection_heuristics():
    """Verify that all variations of RE-jadx project titles and overviews are caught."""
    assert is_re_jadx_project("RE-jadx: Autonomous JADX AI Reverse-Engineering Agent") is True
    assert is_re_jadx_project("Android Decompilation Agent using JADX and MCP") is True
    assert is_re_jadx_project("Omni-Channel Autonomous Sales Agent") is False
    assert is_re_jadx_project("NexusAI: In-Browser Copilot") is False


def test_load_eligible_projects_excludes_re_jadx(tmp_path: Path):
    """Ensure project loader ignores RE-jadx when parsing projects.md."""
    sample_projects_md = tmp_path / "projects.md"
    sample_projects_md.write_text(
        """
## 1. Omni-Channel Autonomous D2C AI Sales & Conversion Agent
**Technologies:** Python, FastAPI, LangGraph
**Overview:** Autonomous conversational sales agent.
* **Graph**: Stateful workflows.

## 5. RE-jadx: Autonomous JADX AI Reverse-Engineering Agent
**Technologies:** Java, Python, MCP, JADX
**Overview:** Autonomous AI forensic agent.
* **MCP**: Built async MCP server.
        """,
        encoding="utf-8",
    )

    projects = load_eligible_projects_from_markdown(sample_projects_md)
    assert len(projects) == 1
    assert projects[0]["title"] == "Omni-Channel Autonomous D2C AI Sales & Conversion Agent"
    assert not any("jadx" in p["title"].lower() for p in projects)


def test_re_jadx_migrated_to_experience_and_purged_from_projects():
    """Verify profile sanitization removes RE-jadx from projects and ensures placement in experience."""
    profile = CandidateProfile(
        name="Sahil Yadav",
        email="test@example.com",
        phone="8700122453",
        experience=[],
        projects=[
            ProjectSpec(
                title="RE-jadx AI Forensic Agent",
                technologies=["Python", "JADX"],
                bullets=["Bullet 1 achieving 20% uplift by doing XYZ."],
            ),
            ProjectSpec(
                title="NexusAI Browser Copilot",
                technologies=["TypeScript"],
                bullets=["Bullet 1 achieving 40% speedup by doing XYZ."],
            ),
        ],
    )

    sanitized = ensure_re_jadx_in_experience(profile)

    # Assert RE-jadx removed from projects
    assert len(sanitized.projects) == 1
    assert sanitized.projects[0].title == "NexusAI Browser Copilot"
    assert not any("jadx" in p.title.lower() for p in sanitized.projects)

    # Assert RE-jadx added to experience
    assert len(sanitized.experience) >= 1
    assert "Special Cell, Delhi Police" in sanitized.experience[0].company
    assert sanitized.experience[0].is_internship is True
    assert len(sanitized.experience[0].bullets) >= 3
