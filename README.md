<div align="center">

# AntiGravity Autonomous Resume Engine 🚀

**Autonomous Agentic Pipeline for Tailored 1-Page Resumes & Interview Defense Dossiers**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Pydantic v2](https://img.shields.io/badge/Validation-Pydantic%20v2-e92063.svg)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Tests-17%2F17%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

*Deconstructs target job descriptions, synthesizes architecturally sound engineering projects across 3 complementary archetypes, rigorously enforces the Google XYZ formula, self-audits metric plausibility, and exports single-format resumes (.pdf, .docx, .tex) with zero duplicate files.*

</div>

---

## 🌟 Key Capabilities

- **🧠 Smart Candidate Profile Caching**: Extracts contact details, education, and work experience from your uploaded resume PDF. Automatically caches to `output/candidate_profile.json` so repeat runs execute instantly without prompts.
- **🎯 3-Project Archetype System**:
  1. **Core Domain**: Solves the primary business domain and functional workflows using the JD's exact stack.
  2. **Distributed Systems & Scale**: Demonstrates high-throughput concurrency, backpressure, distributed caching, and p99 latency optimization.
  3. **DevTools / Platform Infra / MCP**: Demonstrates developer tooling, telemetry, and Model Context Protocol (MCP) servers.
- **📐 Google XYZ Formula Enforced**: Every bullet strictly follows:
  > *"Accomplished [X], as measured by [Y], by implementing [Z]"*
  Front-loaded with approved engineering power verbs (Architected, Benchmarked, Partitioned, Profiled, etc.).
- **🛡️ Evaluator-Optimizer Critique Loop**:
  - Deterministic ATS keyword scoring targeting $\ge 85\%$ match rate.
  - Plausibility & hardware bound enforcement (20%–60% compute/cost reductions, realistic latency numbers, no impossible hardware claims).
- **💼 Job-Aligned Experience Tailoring**: Dynamically refines work experience bullets to highlight keywords, metrics, and systems requested by the target company while preserving 100% of the candidate's genuine accomplishments and factual truth.
- **📄 Clean Single-Format Export**: Generates **only** the requested format (silent **PDF default**, or `.docx`, or `.tex`) with **zero duplicate files**.
- **📁 Non-Destructive Archival**: Automatically moves prior generation outputs to `output/old/` so historical resumes and dossiers are permanently preserved.
- **🎙️ Interview Defense Dossier**: Generates `<company>_ques.md` containing architectural trade-offs ("Why not alternative X?"), failure mode analyses, and 5 probing technical questions with model answers.
- **🤖 Agent-Ready (`AGENTS.md`)**: Pre-configured with token-saving guardrails and direct instructions for AI coding agents (Antigravity, Cursor, Claude Code).

---

## 🏗️ Architecture Pipeline

```
                                  [ Candidate Resume PDF ]
                                             │
                                             ▼
                                  [ Profile Extractor ]
                                 (Cached to output/*.json)
                                             │
                                             ▼
[ Target Job Description ] ────► [ JD Deconstruction Node ]
(or jobs/<company>.json)                 │
                                         ▼
                             [ Archetype Synthesis Node ]
                            (Core + Distributed + DevTools)
                                         │
                                         ▼
                            [ Evaluator-Optimizer Loop ] ◄──┐
                            (ATS Keyword & Plausibility)    │ (Auto-critique if failed)
                                         │                  │
                                     [Passed?] ─────────────┘
                                         │ Yes
                                         ▼
                             [ Artifact & Archival Engine ]
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
[ <company>_resume.pdf ]      [ <company>_ques.md ]           [ output/old/ ]
(Clean 1-Page Resume)        (Interview Defense Dossier)     (Historical Archive)
```

---

## ⚡ Quick Start

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/Notso-sahil/resume-builder.git
cd resume-builder
pip install -r requirements.txt
```

### 2. Add Your Resume

Copy your existing resume PDF into the project root directory:

```bash
# Example
copy path\to\your_resume.pdf .
```

On your first run, the engine auto-discovers your resume, extracts your profile, and caches it to `output/candidate_profile.json`. Future runs load from cache automatically.

### 3. (Optional) Set Environment Variables

```bash
cp .env.example .env
```

- **Primary Mode (Default)**: Uses the built-in native model. No external API key required.
- **Secondary Mode**: Add `GEMINI_API_KEY` or `OPENAI_API_KEY` to `.env` to use external models.

---

## 💻 Usage & CLI Flags

### Interactive Mode (Default)
Prompted only for target job selection; silently defaults to PDF format:
```bash
python main.py
```

### Non-Interactive Company Target
Target a pre-configured job in `jobs/<company>.json`:
```bash
python main.py --job sample_job
```

### Specify Output Format
Generate `.docx` or Jake's Resume `.tex` source instead of PDF:
```bash
python main.py --job sample_job --format docx
python main.py --job sample_job --format latex
```

### Provide Custom Job Description via File
```bash
python main.py --jd path/to/job_description.txt
```

---

## 🛠️ Adding Custom Target Companies (`jobs/`)

To target a new company without modifying any source code, create a JSON file in `jobs/<company_slug>.json`:

```json
{
  "company_name": "Acme Corp",
  "role_title": "Senior AI Systems Engineer",
  "seniority_level": "Senior",
  "domain": "Autonomous AI Infrastructure & Distributed Serving",
  "primary_languages": ["Python", "C++", "CUDA"],
  "frameworks": ["PyTorch", "vLLM", "FastAPI", "LangGraph"],
  "databases_and_storage": ["Redis", "PostgreSQL", "Kafka", "Qdrant"],
  "infrastructure_and_cloud": ["Docker", "Kubernetes", "AWS Cloud GPUs", "Triton"],
  "core_engineering_challenges": [
    "Minimizing p99 latency overhead in multi-agent tool execution loops",
    "GPU memory fragmentation and KV-cache optimization under burst queries"
  ],
  "target_keywords": [
    "Python", "PyTorch", "vLLM", "CUDA", "FastAPI", "LangGraph", "Docker",
    "Continuous Batching", "Speculative Decoding", "KV-Cache", "RAG"
  ],
  "tailored_summary_override": null,
  "fallback_projects": null
}
```

Then run:
```bash
python main.py --job acme_corp
```

---

## 📂 Output Artifacts

All outputs are written cleanly to `output/`:

| Artifact | File Path | Description |
|---|---|---|
| **Tailored Resume** | `output/<company>_resume.pdf` | Strict 1-page layout, ATS-optimized, high-density |
| **Interview Dossier** | `output/<company>_ques.md` | Trade-offs ("Why not X?"), failure modes & 5 interview Q&As |
| **Candidate Profile** | `output/candidate_profile.json` | Structured candidate data extracted from your resume |
| **Structured Data** | `output/portfolio_data.json` | Full JSON payload of all synthesized projects and metrics |
| **Archive Folder** | `output/old/` | Prior generated resumes and dossiers (never deleted) |

---

## 🧪 Testing

Run the automated test suite with pytest:

```bash
python -m pytest tests/ -v
```

```
tests/test_evaluator.py::test_ats_scorer_full_match PASSED               [  5%]
tests/test_evaluator.py::test_ats_scorer_partial_match PASSED            [ 11%]
tests/test_evaluator.py::test_sanity_checker_valid_portfolio PASSED      [ 17%]
tests/test_evaluator.py::test_sanity_checker_invalid_power_verb PASSED   [ 23%]
tests/test_evaluator.py::test_sanity_checker_forbidden_phrase PASSED     [ 29%]
tests/test_evaluator.py::test_audit_portfolio_end_to_end PASSED          [ 35%]
tests/test_pipeline.py::test_output_format_validation PASSED             [ 41%]
tests/test_pipeline.py::test_pipeline_integration_docx PASSED            [ 47%]
tests/test_pipeline.py::test_slugify_company PASSED                      [ 52%]
tests/test_pipeline.py::test_archival_on_subsequent_run PASSED           [ 58%]
tests/test_pipeline.py::test_job_config_loading_and_execution PASSED     [ 64%]
tests/test_profile_extractor.py::test_parse_profile_deterministic_no_hardcoded_leak PASSED [ 70%]
tests/test_profile_extractor.py::test_find_candidate_resumes PASSED      [ 76%]
tests/test_profile_extractor.py::test_extract_profile_from_resume_pdf PASSED [ 82%]
tests/test_renderers.py::test_render_docx PASSED                         [ 88%]
tests/test_renderers.py::test_render_latex PASSED                        [ 94%]
tests/test_renderers.py::test_render_dossier PASSED                      [100%]

============================= 17 passed in 0.95s ==============================
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
