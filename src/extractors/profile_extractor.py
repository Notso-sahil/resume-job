import json
import re
import copy
from pathlib import Path
from typing import Optional
import pdfplumber

from src.config import get_llm, OUTPUT_DIR
from src.schemas.models import CandidateProfile, EducationEntry, ExperienceEntry
from src.extractors.project_loader import is_re_jadx_project
from src.prompts.experience_prompts import CANONICAL_RE_JADX_EXPERIENCE

CACHE_PATH = OUTPUT_DIR / "candidate_profile.json"


SECTION_LOOKAHEAD = r"(?=\n\s*(?:EDUCATION|TECHNICAL SKILLS|SKILLS|PROJECTS|ENGINEERING PROJECTS|EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|PUBLICATIONS|CERTIFICATIONS|AWARDS|LANGUAGES|ACHIEVEMENTS)\b|\Z)"


def clean_unicode_text(text: str) -> str:
    """Normalizes non-standard typography/dashes/bullets commonly extracted from PDFs."""
    replacements = {
        "\ufffd": " · ",
        "\u2013": "–",
        "\u2014": "—",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "•",
        "\u00b7": "·",
        "â€¢": "•",
        "Â·": "·",
        "â€“": "–",
        "â€”": "—",
        "â†’": "->",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def extract_raw_text(pdf_path: str | Path) -> str:
    """Extracts raw text from all pages of the given PDF using pdfplumber."""
    raw_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                raw_text += extracted + "\n"
    return clean_unicode_text(raw_text.strip())


def parse_profile_deterministic(text: str) -> CandidateProfile:
    """
    High-accuracy deterministic parser for resumes when LLM is in offline mode or as fallback.
    Extracts name, headline, phone, email, links, objective, education, and experience.
    """
    text = clean_unicode_text(text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    full_name = lines[0] if lines else "Candidate"
    title = lines[1] if len(lines) > 1 else "Software Engineer"

    # Extract email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    email = email_match.group(0) if email_match else "candidate@example.com"

    # Extract phone
    phone_match = re.search(r"(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}|\+?\d{10,13}", text)
    phone = phone_match.group(0) if phone_match else "+1-555-0100"

    # Extract LinkedIn
    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else None

    # Extract GitHub
    github_match = re.search(r"(https?://)?(www\.)?github\.com/[\w-]+", text, re.IGNORECASE)
    github = github_match.group(0) if github_match else None

    # Extract Objective / Summary
    objective = ""
    obj_match = re.search(
        r"(?:PROFESSIONAL OBJECTIVE|SUMMARY|PROFILE|OBJECTIVE)\s*\n+(.*?)" + SECTION_LOOKAHEAD,
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if obj_match:
        objective = " ".join(obj_match.group(1).split())
    else:
        # Fallback to paragraph around index 2-3
        if len(lines) > 3:
            objective = lines[3]

    # Extract Education
    education_entries = []
    edu_match = re.search(
        r"(?:EDUCATION)\s*\n+(.*?)" + SECTION_LOOKAHEAD,
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if edu_match:
        edu_text = edu_match.group(1).strip()
        edu_lines = [l.strip() for l in edu_text.splitlines() if l.strip()]
        if edu_lines:
            degree_line = edu_lines[0]
            year_match = re.search(r"\b(20\d\d\s*[-–—]\s*(?:20\d\d|Present|Expected|\(Expected\))|\d{4})\b", degree_line)
            year_range = year_match.group(0) if year_match else "2020 – 2024"
            clean_degree = re.sub(r"\b(20\d\d\s*[-–—]\s*(?:20\d\d|Present|Expected|\(Expected\))|\d{4})\b", "", degree_line).strip()

            institution = edu_lines[1] if len(edu_lines) > 1 else "University"
            details = None
            if "·" in institution:
                parts = institution.split("·")
                institution = parts[0].strip()
                details = parts[1].strip()

            if details:
                details = re.sub(r"\b2nd\s*Year\b", "3rd Year", details, flags=re.IGNORECASE)

            education_entries.append(
                EducationEntry(
                    degree=clean_degree or degree_line,
                    institution=institution,
                    year_range=year_range,
                    details=details,
                )
            )

    if not education_entries:
        education_entries.append(
            EducationEntry(
                degree="B.S. in Computer Science",
                institution="University",
                year_range="2020 – 2024",
                details="Undergraduate",
            )
        )

    # Extract Experience if an EXPERIENCE section exists
    experience_entries = []
    exp_match = re.search(
        r"(?:EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE)\s*\n+(.*?)" + SECTION_LOOKAHEAD,
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if exp_match:
        exp_chunk = exp_match.group(1).strip()
        exp_lines = [l.strip() for l in exp_chunk.split("\n") if l.strip()]
        if exp_lines:
            header_line = exp_lines[0]
            role = header_line
            org = "Company / Organization"
            if " at " in header_line:
                parts = header_line.split(" at ", 1)
                role = parts[0].strip()
                org = parts[1].strip()
            elif " | " in header_line:
                parts = header_line.split(" | ", 1)
                role = parts[0].strip()
                org = parts[1].strip()

            bullets = [
                l.lstrip("•-*· ").strip()
                for l in exp_lines[1:]
                if l.startswith(("•", "-", "*", "·")) or len(l) > 30
            ][:3]
            experience_entries.append(
                ExperienceEntry(
                    role=role,
                    organization=org,
                    period="Recent",
                    location=None,
                    bullets=bullets or ["Engineered backend services and software systems."],
                )
            )

    return CandidateProfile(
        full_name=full_name,
        title=title,
        phone=phone,
        email=email,
        linkedin=linkedin,
        github=github,
        professional_objective=objective or "Experienced Engineer passionate about scalable AI systems.",
        education=education_entries,
        experience=experience_entries,
    )


def ensure_re_jadx_in_experience(profile: CandidateProfile) -> CandidateProfile:
    """
    Verifies that RE-jadx is anchored in the experience/internship list
    and eradicated from any project lists.
    """
    # 1. Purge RE-jadx from projects if accidentally extracted from resume text
    if hasattr(profile, "projects") and profile.projects:
        clean_projects = [
            p for p in profile.projects 
            if not is_re_jadx_project(getattr(p, "title", getattr(p, "project_title", "")), getattr(p, "overview", ""))
        ]
        profile.projects = clean_projects

    if hasattr(profile, "real_projects") and profile.real_projects:
        profile.real_projects = [
            p for p in profile.real_projects 
            if not is_re_jadx_project(getattr(p, "title", getattr(p, "project_title", "")), getattr(p, "overview", ""))
        ]

    # 2. Check if the IFSO / Delhi Police internship entry is already present
    has_ifso = any(
        "delhi police" in (exp.company or exp.organization).lower() 
        or "ifso" in (exp.company or exp.organization).lower() 
        or "jadx" in exp.role.lower()
        for exp in profile.experience
    )

    if not has_ifso:
        # Prepend the canonical RE-jadx internship entry
        jadx_entry = ExperienceEntry(
            company=CANONICAL_RE_JADX_EXPERIENCE["company"],
            role=CANONICAL_RE_JADX_EXPERIENCE["role"],
            location=CANONICAL_RE_JADX_EXPERIENCE["location"],
            start_date=CANONICAL_RE_JADX_EXPERIENCE["start_date"],
            end_date=CANONICAL_RE_JADX_EXPERIENCE["end_date"],
            technologies=CANONICAL_RE_JADX_EXPERIENCE["technologies"],
            bullets=copy.deepcopy(CANONICAL_RE_JADX_EXPERIENCE["base_bullets"]),
            is_internship=True,
        )
        profile.experience.insert(0, jadx_entry)

    return profile


def parse_candidate_profile(text: str) -> CandidateProfile:
    """Deterministic parser with RE-jadx experience enforcement for candidate profile."""
    profile = parse_profile_deterministic(text)
    return ensure_re_jadx_in_experience(profile)


def extract_profile_from_pdf(pdf_path: str | Path) -> CandidateProfile:
    """
    Two-step extraction:
      1. pdfplumber  â†’ raw text string
      2. LLM / Parser â†’ CandidateProfile (structured output)

    Extracted fields: full_name, title, phone, email,
                      linkedin, github, professional_objective, education, experience
    """
    raw_text = extract_raw_text(pdf_path)

    llm = get_llm()
    # Try structured extraction via LLM if supported
    try:
        if hasattr(llm, "with_structured_output"):
            structured_llm = llm.with_structured_output(CandidateProfile)
            prompt = (
                "Extract the candidate's personal information from the following resume text.\n"
                "Extract: full name, professional title/headline, phone, email, "
                "LinkedIn URL, GitHub URL, professional objective/summary, education entries, and work experience.\n"
                "Ignore personal projects and standalone skills sections.\n\n"
                f"Resume text:\n{raw_text}"
            )
            result = structured_llm.invoke(prompt)
            if isinstance(result, CandidateProfile):
                profile = result
            elif isinstance(result, dict):
                profile = CandidateProfile(**result)
            if profile:
                for edu in profile.education:
                    if edu.details:
                        edu.details = re.sub(r"\b2nd\s*Year\b", "3rd Year", edu.details, flags=re.IGNORECASE)
                return profile
    except Exception:
        pass

    # Fallback to deterministic regex/NLP parser
    return parse_profile_deterministic(raw_text)


def find_candidate_resumes(search_dir: Path | None = None) -> list[Path]:
    """
    Scans the given directory (default: project root) for candidate resume PDFs,
    ignoring files inside output/ or old/.
    """
    if search_dir is None:
        search_dir = Path(__file__).resolve().parent.parent.parent

    candidates = []
    for p in search_dir.glob("*.pdf"):
        if "output" in p.parts or "old" in p.parts:
            continue
        candidates.append(p)
    return sorted(candidates, key=lambda x: x.name)


def load_or_extract_profile(pdf_path: str | Path | None) -> Optional[CandidateProfile]:
    """
    Main entry point called from main.py.

    - If output/candidate_profile.json exists â†’ load from cache (no re-extraction)
    - If pdf_path provided                   â†’ extract and cache
    - If pdf_path is None                    â†’ return None (renderers use placeholder header)
    """
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                profile = CandidateProfile(**data)
                for edu in profile.education:
                    if edu.details:
                        edu.details = re.sub(r"\b2nd\s*Year\b", "3rd Year", edu.details, flags=re.IGNORECASE)
                profile = ensure_re_jadx_in_experience(profile)
                return profile
        except Exception:
            pass

    if not pdf_path:
        return None

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        return None

    profile = extract_profile_from_pdf(pdf_file)
    profile = ensure_re_jadx_in_experience(profile)

    # Cache the result to output/candidate_profile.json
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        f.write(profile.model_dump_json(indent=2))

    return profile
