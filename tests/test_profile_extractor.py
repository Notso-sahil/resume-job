from pathlib import Path
from src.extractors.profile_extractor import (
    extract_profile_from_pdf,
    load_or_extract_profile,
    parse_profile_deterministic,
    find_candidate_resumes,
)
from src.schemas.models import CandidateProfile


def test_parse_profile_deterministic_no_hardcoded_leak():
    sample_text = (
        "ALEX RIVERA\n"
        "Lead Distributed Systems Architect\n"
        "+1 (555) 234-5678 | alex.rivera@example.com | linkedin.com/in/alex-rivera | github.com/arivera\n"
        "PROFESSIONAL OBJECTIVE\n"
        "Seasoned systems architect specializing in high-throughput event streaming and distributed consensus.\n"
        "EDUCATION\n"
        "M.S. in Computer Science  2018 – 2020\n"
        "Cornell University · Magna Cum Laude\n"
    )
    profile = parse_profile_deterministic(sample_text)
    assert profile.full_name == "ALEX RIVERA"
    assert profile.title == "Lead Distributed Systems Architect"
    assert "alex.rivera@example.com" in profile.email
    assert len(profile.education) > 0
    assert "Cornell" in profile.education[0].institution
    # Ensure no Sahil or IFSO leaks into generic profiles
    assert "sahil" not in profile.full_name.lower()
    for exp in profile.experience:
        assert "delhi police" not in exp.organization.lower()


def test_find_candidate_resumes(tmp_path):
    # Setup test PDFs in tmp_path
    (tmp_path / "my_resume.pdf").write_text("%PDF-1.4 dummy")
    (tmp_path / "other_doc.txt").write_text("dummy")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "generated_resume.pdf").write_text("%PDF-1.4 dummy")

    found = find_candidate_resumes(tmp_path)
    assert len(found) == 1
    assert found[0].name == "my_resume.pdf"


def test_extract_profile_from_resume_pdf():
    # If a workspace resume PDF exists, verify extraction
    pdfs = find_candidate_resumes()
    if not pdfs:
        return

    profile = extract_profile_from_pdf(pdfs[0])
    assert isinstance(profile, CandidateProfile)
    assert len(profile.full_name) > 0
    assert "@" in profile.email


def test_parse_profile_with_uppercase_org_and_bullets():
    sample_text = (
        "JANE DOE\n"
        "AI Security Engineer\n"
        "jane.doe@example.com | +1 555 123 4567 | linkedin.com/in/janedoe | github.com/janedoe\n"
        "PROFESSIONAL OBJECTIVE\n"
        "Security researcher focusing on automated vulnerability analysis.\n"
        "WORK EXPERIENCE\n"
        "AI Intern at IFSO (Intelligence Fusion & Strategic Operations)\n"
        "• Autonomous Static Analysis Pipeline: Engineered an automated reverse-engineering agent to decompile APKs.\n"
        "• Sensitive Asset & Credential Discovery: Implemented targeted pattern-matching engines to extract secrets.\n"
        "• Automated Threat Vector Analysis: Synthesized forensic intelligence into reports mapped to OWASP.\n"
        "EDUCATION\n"
        "B.S. in Computer Science 2020 - 2024\n"
        "State University\n"
    )
    profile = parse_profile_deterministic(sample_text)
    assert profile.full_name == "JANE DOE"
    assert len(profile.experience) == 1
    assert "IFSO" in profile.experience[0].organization
    assert len(profile.experience[0].bullets) == 3
    assert "Autonomous Static Analysis" in profile.experience[0].bullets[0]
    assert len(profile.education) == 1
    assert "State University" in profile.education[0].institution


def test_experience_tailoring_preserves_facts_and_enriches_jd():
    from src.schemas.models import ExperienceEntry, JDDeconstruction
    from src.prompts.experience_prompts import synthesize_tailored_experience

    entry = ExperienceEntry(
        role="AI Intern",
        organization="IFSO, Delhi Police",
        period="June - August 2025",
        bullets=[
            "Engineered an automated reverse-engineering agent to decompile and inspect Android APKs.",
            "Implemented targeted pattern-matching engines to extract hardcoded API keys and secrets.",
            "Synthesized extracted forensic intelligence into actionable reports mapped to OWASP.",
        ],
    )
    jd = JDDeconstruction(
        company_name="Microsoft",
        role_title="Software Engineer: AI/ML & LLM Intern",
        seniority_level="Intern",
        domain="AI/ML Platform Engineering, LLM Inference",
        primary_languages=["Python", "C++"],
        frameworks=["PyTorch", "FastAPI", "Large Language Models (LLMs)"],
        databases_and_storage=["Redis", "Vector Databases"],
        infrastructure_and_cloud=["Azure", "Docker"],
        core_engineering_challenges=["Low latency inference", "Automated evaluation"],
        target_keywords=["LLM", "Inference", "Latency", "PyTorch", "Docker", "RAG"],
    )

    tailored = synthesize_tailored_experience([entry], jd)
    assert len(tailored) == 1
    bullets = tailored[0].bullets
    assert len(bullets) == 3
    # Check that factual APK / binary / credential core is preserved
    assert any("apk" in b.lower() or "android" in b.lower() or "binaries" in b.lower() for b in bullets)
    assert any("pattern-matching" in b.lower() or "credential" in b.lower() or "secret" in b.lower() for b in bullets)
    assert any("owasp" in b.lower() or "threat" in b.lower() or "forensic" in b.lower() for b in bullets)


def test_fallback_synthesize_candidate_profile():
    from src.prompts.synthesis_prompts import fallback_synthesize
    profile = fallback_synthesize("", CandidateProfile)
    assert isinstance(profile, CandidateProfile)
    assert len(profile.full_name) > 0
    assert len(profile.education) > 0
    assert len(profile.experience) > 0


def test_profile_normalizes_2nd_year_to_3rd_year():
    text_with_2nd_year = (
        "SAHIL YADAV\n"
        "AI Systems Engineer\n"
        "sahil@example.com | +91 8700122453\n"
        "EDUCATION\n"
        "B.Tech in Artificial Intelligence & Machine Learning (AIML) 2024 – 2028 (Expected)\n"
        "Vivekananda Institute of Professional Studies (VIPS), New Delhi · 2nd Year · Core Focus: Deep Learning\n"
    )
    profile = parse_profile_deterministic(text_with_2nd_year)
    assert len(profile.education) == 1
    edu = profile.education[0]
    assert "3rd Year" in edu.details
    assert "2nd Year" not in edu.details


