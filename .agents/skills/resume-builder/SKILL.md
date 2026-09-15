---
name: resume-builder
description: Generates high-impact ATS-optimized resumes and interview defense dossiers for any target job description using the AntiGravity Resume Engine.
---

# AntiGravity Resume Engine — Skill

Use this skill whenever the user provides a Job Description (JD), company name, or asks to generate a tailored resume for any role.

> [!IMPORTANT]
> **TOKEN-SAVER DIRECTIVE FOR AGENTS:**
> **DO NOT scan, grep, list, or view source files in `src/`, `templates/`, or `tests/`.**
> The engine is 100% complete, fully implemented, and automated. Reading the codebase wastes tokens.
> Follow the strict 2-step protocol below.

---

## The 2-Step Protocol

### Step 1: Create the Job Config File
When the user provides a Job Description (JD) or company name:
1. Deconstruct the JD into: role title, company name, domain, tech stack keywords (languages, frameworks, DBs, cloud/tools), and soft skills.
2. Save the job configuration JSON at `jobs/<company_slug>.json`.

**Job Config Schema:**
```json
{
  "company_name": "Target Company",
  "role_title": "AI Platform Engineer",
  "seniority_level": "Senior",
  "domain": "Autonomous AI Agents & Distributed Systems",
  "primary_languages": ["Python", "C++", "CUDA"],
  "frameworks": ["PyTorch", "vLLM", "LangGraph", "FastAPI"],
  "databases_and_storage": ["Redis", "PostgreSQL", "Kafka", "Qdrant"],
  "infrastructure_and_cloud": ["Docker", "Kubernetes", "AWS Cloud GPUs", "Triton"],
  "core_engineering_challenges": [
    "High-throughput vector indexing and sub-10ms similarity search under concurrent load",
    "Optimizing KV-cache footprint and speculative decoding for multi-agent loops"
  ],
  "target_keywords": [
    "Python", "PyTorch", "vLLM", "LangGraph", "CUDA", "FastAPI", "Docker", "RAG",
    "Speculative Decoding", "Continuous Batching", "KV-Cache", "Distributed Systems"
  ],
  "soft_skills": [
    "Engineering Ownership", "Cross-functional Collaboration", "Fast Iteration", "Technical Communication"
  ],
  "tailored_summary_override": "High-impact 2-3 sentence tailored summary blending candidate background with the target role.",
  "fallback_projects": null
}
```
*(Note: `fallback_projects` can be `null` — the engine automatically synthesizes 3 archetypes and XYZ bullets using the keywords and domain).*

---

### Step 2: Execute the Pipeline via Terminal
Run the command directly using your shell/command execution tool.

**Standard invocation (saves in output/):**
```bash
# Default: generates high-quality 1-page PDF resume + interview prep dossier
python main.py --job <company_slug>
```

---

## Generated Outputs Location

- Resume: `output/<company_slug>_resume.pdf` (or `.docx` / `.tex`)
- Interview Prep Dossier: `output/<company_slug>_ques.md`
- Cached Profile: `output/candidate_profile.json`
- Historical Generations: cleanly archived in `output/old/`

Report the generated file paths directly to the user when finished.

---

## Agent Invariants (Strict Rules)

1. **Zero Source Code Modifications**: NEVER edit or mutate files in `src/`, `templates/`, or root (`main.py`, `config.py`, etc.). Resumes are configured **exclusively via `jobs/<company>.json`**.
2. **Do Not Prompt for Format**: Always default to PDF silently unless the user explicitly requested docx or latex.
3. **Candidate Resume Missing**: If the candidate profile is missing, instruct the user to copy their resume PDF into the root directory.
4. **Candidate Profile Standing**: The candidate (Sahil Yadav) is currently in **3rd Year** of B.Tech in Artificial Intelligence & Machine Learning (AIML) at Vivekananda Institute of Professional Studies (VIPS), New Delhi. Always reflect 3rd Year standing in education details.
