# AntiGravity Resume Engine & Autonomous Job Application System
## Comprehensive System Architecture, Operational Context & AI Agent Directives

> **Notice for AI Models & Agents**: This document is the definitive master context for the `resume-job` repository. It contains everything required to understand the codebase, orchestrate resume generation, adhere to candidate ground-truth constraints, interact with browser discovery pipelines, enforce the 3-project allocation hierarchy, and respect operational invariants without needing to inspect internal source code.

---

## 1. Executive Summary

The **AntiGravity Resume Engine** is an autonomous, agent-driven platform designed to automate technical job search, resume customization, and job application workflows:

1. **Autonomous Resume Synthesis & ATS Optimization**:
   - Built on **Python 3.10+**, **LangGraph**, and **Pydantic v2**.
   - Ingests target Job Descriptions (JDs) either via CLI flags, browser tabs, or pre-configured JSON files.
   - Synthesizes 3 hyper-tailored, architecturally sound engineering project archetypes matching the JD's exact tech stack.
   - Enforces the **Google XYZ formula** (*"Accomplished [X], as measured by [Y], by implementing [Z]"*) with front-loaded engineering power verbs.
   - Executes an **Evaluator-Optimizer critique loop** verifying $\ge 85\%$ ATS keyword coverage and mathematical/hardware plausibility bounds (e.g. 20%–60% compute/latency reductions, realistic memory figures).
   - Produces clean, single-format exports (silent **PDF default**, `.docx`, or LaTeX `.tex`) and automatically generates a companion **Technical Interview Defense Dossier** (`<company>_ques.md`).

2. **Live Browser Automation & Job Application (`finder/`, `BrowseAI/`)**:
   - Integrates with a custom Model Context Protocol (MCP) bridge and Chrome MV3 extension (**BrowseAI**) to inspect live browser tabs.
   - Discovers open job postings across LinkedIn, Internshala, Wellfound/AngelList, etc.
   - Enforces a minimum stipend threshold of **₹20,000/month** and prioritizes AI/ML roles.
   - Triggers the resume builder pipeline to compile matching single-page PDF resumes.
   - Automates web form input fields in the browser, halting safely before the final submission button for human review.

---

## 2. Master Candidate Profile & Ground Truth Identity

The engine grounds all tailored resumes on verified candidate data cached at [`output/candidate_profile.json`](file:///c:/Users/elite/Desktop/resume-job/output/candidate_profile.json):

- **Candidate Name**: **Sahil Yadav**
- **Contact Details**: 
  - Phone: `+91 8700122453`
  - Email: `sahillyaadav@gmail.com`
  - LinkedIn: `linkedin.com/in/sahil-yadav-1ab468249`
  - GitHub: `github.com/Notso-sahil`
- **Education**: 
  - Degree: B.Tech in Artificial Intelligence & Machine Learning (AIML)
  - Institution: Vivekananda Institute of Professional Studies (VIPS), New Delhi (2024 – 2028 Expected)
  - **CRITICAL INVARIANT**: The candidate is currently in their **3rd Year**. Always reflect 3rd Year undergraduate standing across all education blocks.
- **Core Technical Focus**:
  - AI Systems Engineering, Agentic Workflows (LangGraph, LangChain, MCP).
  - Transformer inference optimization (vLLM, continuous batching, PagedAttention, KV-cache tuning, speculative decoding, CUDA/PyTorch).
  - Full-stack Python/FastAPI microservices, distributed caching (Redis), vector databases (Qdrant, Pinecone), containerization (Docker, Kubernetes).
- **Verified Work Experience**:
  - **Role**: AI Intern at IFSO (Intelligence Fusion & Strategic Operations), Special Cell, Delhi Police (June 2025 – August 2025).
  - **Key Highlights**: Built autonomous agentic triage pipelines using MCP tool-calling and retrieval systems across 20,000+ decompiled Android APK binaries; optimized asynchronous FastAPI inference routines reducing forensic latency by 62%.
  - **RE-jadx Confinement Rule**: **RE-jadx** must **NEVER** appear in `fallback_projects`. It is reserved exclusively for the Work Experience section under this verified tenure.

---

## 3. System Architecture & Core Subsystems

```
                                  [In-Chat Trigger / Prompt]
                                               │
                                               ▼
                                 ┌───────────────────────────┐
                                 │    .antigravity/rules.md  │
                                 │  • Native Chat Context    │
                                 │  • Stipend Floor ≥ ₹20k   │
                                 │  • Atomic Git (No Push)   │
                                 └─────────────┬─────────────┘
                                               │
                        ┌──────────────────────┴──────────────────────┐
                        ▼                                             ▼
          ┌───────────────────────────┐                 ┌───────────────────────────┐
          │         AGENTS.md         │                 │         SKILL.md          │
          │  • Browser Tab Triggers   │                 │  • Terminal Invocation    │
          │  • Eligibility Assessment │                 │  • Output Path Routing    │
          │  • JD Deconstruction      │                 │  • Profile Standings      │
          └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                        │                                             │
                        └──────────────────────┬──────────────────────┘
                                               │
                                               ▼
                              ┌──────────────────────────────────┐
                              │     Project Slot Hierarchy       │
                              │ • Slot 1: projects.md Anchor     │
                              │ • Slots 2 & 3: Custom Synthesis  │
                              │ • Experience: RE-jadx Internship │
                              └────────────────┬─────────────────┘
                                               │
                                               ▼
                              ┌──────────────────────────────────┐
                              │       Atomic Local Git Log       │
                              │  git add jobs/<slug>.json        │
                              │  git commit -m "config(...)"     │
                              └──────────────────────────────────┘
```

### Component 1: The Core Resume Engine (`main.py`, `src/`)
- Orchestrated as a stateful cyclic LangGraph.
- Automatically discovers existing candidate resumes in the root workspace on first launch and parses them into `output/candidate_profile.json`.
- Maintains strict visual page-budget constraints for 1-page PDF resumes (preventing multi-page overflow).
- Non-destructively archives any existing resume or dossier for that company into `output/old/` before writing new artifacts.

### Component 2: BrowseAI Monorepo (`BrowseAI/`)
- A TypeScript monorepo providing browser connectivity to LLMs and agents via the Model Context Protocol (MCP).
- Consists of:
  - `packages/extension`: Chrome MV3 browser extension that captures DOM state, handles navigation, and executes form interactions.
  - `packages/bridge`: Fastify server listening on `http://127.0.0.1:12307/mcp` communicating over stdio or SSE.
  - `scripts/install-host.mjs`: Windows Native Messaging Host registry installer (`com.nexusai.browserhost`).

### Component 3: Job Finder & Form Filler (`finder/`)
- Python package (`finder/finder_cli.py`) automating the job hunting cycle:
  - `BrowserClient`: Connects to BrowseAI MCP to enumerate active Chrome tabs.
  - `JobScraper`: Detects supported job boards (LinkedIn, Internshala, Wellfound, etc.) and scrapes job title, company name, raw stipend, and JD text.
  - `stipend_parser`: Regex-based parser enforcing the **₹20,000/month minimum stipend** threshold.
  - `StateTracker`: Manages SQLite database (`applications.db`) with state progression: `DISCOVERED` -> `TAILORED` -> `FILLED` -> `APPLIED`.
  - `ResumeIntegrator`: Calls `main.py --job <slug>` to generate the corresponding PDF resume.
  - `FormFiller`: Automatically fills application input fields in the browser tab and halts before submission.

---

## 4. Markdown (`.md`) Files Read by the Agent

| Markdown File | Role & Information Read by the Agent |
|---|---|
| [`AGENTS.md`](file:///c:/Users/elite/Desktop/resume-job/AGENTS.md) | **Primary Agent Instructions & Operational Directives**: Contains the strict **Token-Saver Directive** forbidding inspection of `src/`, `templates/`, or `tests/`. Defines in-chat orchestration triggers, the 2-step resume synthesis protocol, schema specification for `jobs/<company_slug>.json`, project allocation hierarchy, and agent invariants. |
| [`.agents/skills/resume-builder/SKILL.md`](file:///c:/Users/elite/Desktop/resume-job/.agents/skills/resume-builder/SKILL.md) | **Skill Definition File**: Registered skill for Antigravity/agent runtimes. Outlines invocation parameters, default PDF behavior, `projects.md` Slot #1 anchor rules, and candidate standing invariants. |
| [`.antigravity/rules.md`](file:///c:/Users/elite/Desktop/resume-job/.antigravity/rules.md) | **Project Operational Rules**: Requires native chat model context (prohibits external API keys or ad-hoc runner scripts), enforces strict ₹20,000/month stipend filter, mandates AI role prioritization, and forbids silent fallback to hardcoded placeholders. |
| [`projects.md`](file:///c:/Users/elite/Desktop/resume-job/projects.md) | **Candidate Project Catalog**: Contains 10 verified, production-grade engineering projects with benchmarks, trade-offs, and failure modes. Serves as ground truth for **Slot #1 (Anchor Project)**. |
| [`README.md`](file:///c:/Users/elite/Desktop/resume-job/README.md) | **Master Documentation**: Explains the 3-project archetype philosophy, Google XYZ formula enforcement, Evaluator-Optimizer critique criteria, setup steps for BrowseAI Chrome Extension, and CLI usage. |
| [`BrowseAI/SETUP.md`](file:///c:/Users/elite/Desktop/resume-job/BrowseAI/SETUP.md) | **Browser Extension Setup Guide**: Detailed setup and troubleshooting guide for the Native Messaging Host (`com.nexusai.browserhost`), Chrome MV3 extension setup, extension ID registration, and Fastify MCP bridge on `http://127.0.0.1:12307/mcp`. |
| [`output/<company>_ques.md`](file:///c:/Users/elite/Desktop/resume-job/output/hasamex_ques.md) | **Generated Markdown Artifact**: Produced on each run alongside the resume. Contains architectural trade-offs (*"Why chosen technology X over rejected technology Y?"*), failure modes/recovery runbooks, and 5 technical interview Q&As with defense answers. |

---

## 5. How the Agent Generates a Resume: The 2-Step Protocol

When provided with a target Job Description (JD) or company requirements:

### Step 1: Synthesize the Job Config File (`jobs/<company_slug>.json`)
1. Deconstruct the JD into: target role title, company name, domain, core engineering challenges, and technical stack.
2. Identify at least **15+ relevant technical keywords** for ATS match density ($\ge 85\%$).
3. Apply the **Project Allocation Hierarchy**:
   - **Slot #1 (Core Portfolio Anchor — Mandatory)**:
     - Must be drawn directly from the candidate's verified project catalog ([`projects.md`](file:///c:/Users/elite/Desktop/resume-job/projects.md)).
     - Select the project that best matches the role's primary domain and tools.
     - *Fallback*: If none match directly, select the most technically demanding project (e.g., *Omni-Channel Autonomous D2C AI Sales Agent* or *Enterprise Self-Reflective RAG Engine*) and place it at Slot #1.
     - Flag with `"is_anchor_project": true`.
   - **Slots #2 & #3 (Role-Targeted Custom Architectures)**:
     - Synthesize 2 targeted engineering project architectures custom-tailored to solve the target company's exact engineering bottlenecks and tech stack.
     - These do not need to exist in `projects.md`; design them to maximize interview selection.
     - Flag with `"is_anchor_project": false`.
   - **RE-jadx Confinement Rule**:
     - **RE-jadx** must **NEVER** appear in `fallback_projects`. It is reserved exclusively for the Work Experience section under the candidate's tenure at IFSO, Delhi Police.
4. Format all bullet points using the **Google XYZ formula**: *"Accomplished [X], as measured by [Y], by implementing [Z]"*, front-loaded with active power verbs (*Architected, Benchmarked, Partitioned, Profiled, Deployed, Engineered, Orchestrated*). Never insert `[TODO]` or empty brackets; provide realistic engineering metrics within 20%–60% bounds.
5. Write the configuration file to `jobs/<company_slug>.json` using this exact schema:

```json
{
  "company_name": "Target Company",
  "role_title": "Target Role Title",
  "seniority_level": "Intern / Junior / Mid-Level",
  "domain": "Target Technical Domain",
  "primary_languages": ["Python", "TypeScript", "C++"],
  "frameworks": ["PyTorch", "vLLM", "FastAPI", "LangGraph"],
  "databases_and_storage": ["Redis", "PostgreSQL", "Qdrant"],
  "infrastructure_and_cloud": ["Docker", "Kubernetes", "AWS Cloud GPUs", "Triton"],
  "core_engineering_challenges": [
    "Primary technical bottleneck or latency constraint",
    "Secondary scaling or reliability challenge"
  ],
  "target_keywords": [
    "Python", "PyTorch", "vLLM", "LangGraph", "FastAPI", "Docker", "RAG",
    "Speculative Decoding", "Continuous Batching", "KV-Cache", "Distributed Systems",
    "Vector Search", "Qdrant", "Redis", "Kubernetes"
  ],
  "soft_skills": [
    "Engineering Ownership", "Systems Architecture", "Cross-Functional Collaboration"
  ],
  "tailored_summary_override": "Dense 3-4 sentence professional summary aligning candidate background with target company challenges.",
  "fallback_projects": [
    {
      "project_title": "Selected Project Title from projects.md (Slot 1)",
      "archetype": "Core Domain Anchor",
      "high_level_architecture": "End-to-end architecture description solving the primary business challenge...",
      "tech_stack": ["Python", "FastAPI", "Redis", "Docker"],
      "core_bottleneck": "Primary throughput or latency bottleneck addressed...",
      "technical_solution": "Concrete architectural implementation addressing the bottleneck...",
      "live_link": null,
      "quantified_impact_metrics": [
        "Reduced p95 latency by 38%",
        "Maintained 99.6% intent-action accuracy"
      ],
      "trade_offs": [
        {
          "decision": "State Storage Selection",
          "chosen_technology": "Redis",
          "rejected_technology": "PostgreSQL Session Storage",
          "justification": "Sub-millisecond multi-turn memory retrieval across concurrent web sessions."
        }
      ],
      "failure_modes": [
        {
          "scenario": "Webhook delivery failure under traffic bursts",
          "impact": "Dropped conversational events",
          "mitigation_strategy": "Asynchronous dead-letter queue with exponential retry backoff"
        }
      ],
      "xyz_bullets": [
        "Architected an omni-channel conversational engine using LangGraph and Redis, reducing multi-turn state retrieval latency by 38% under 500+ concurrent sessions.",
        "Engineered deterministic tool-calling microservices in FastAPI with strict Pydantic v2 validation, achieving a 99.6% intent execution accuracy rate.",
        "Integrated asynchronous webhook pipelines deployed in Docker, maintaining a p95 response time under 820ms across 8,500+ interactions."
      ],
      "is_anchor_project": true
    },
    {
      "project_title": "Custom Role-Tailored Architecture 1 (Slot 2)",
      "archetype": "Distributed Systems & Scale",
      "high_level_architecture": "Distributed architecture matching target company systems...",
      "tech_stack": ["Python", "PyTorch", "vLLM", "CUDA"],
      "core_bottleneck": "High token generation latency during peak concurrency...",
      "technical_solution": "Continuous batching and speculative decoding optimization...",
      "live_link": null,
      "quantified_impact_metrics": [
        "Cut p99 generation latency by 42%",
        "Increased throughput from 120 to 380 QPS"
      ],
      "trade_offs": [],
      "failure_modes": [],
      "xyz_bullets": [
        "Engineered a distributed LLM serving gateway using vLLM and PagedAttention, reducing p99 latency by 42% under 500+ concurrent requests.",
        "Benchmarked speculative decoding pipelines in PyTorch, accelerating average token throughput by 35% without degrading output fidelity."
      ],
      "is_anchor_project": false
    },
    {
      "project_title": "Custom Role-Tailored Architecture 2 (Slot 3)",
      "archetype": "Platform Tooling & MCP",
      "high_level_architecture": "Infrastructure and tool execution architecture...",
      "tech_stack": ["TypeScript", "Python", "Docker", "Qdrant"],
      "core_bottleneck": "Unstructured tool parsing errors and token window overhead...",
      "technical_solution": "Standardized Model Context Protocol (MCP) server implementation...",
      "live_link": null,
      "quantified_impact_metrics": [
        "Reduced prompt token overhead by 45%",
        "Attained 0.94 answer faithfulness"
      ],
      "trade_offs": [],
      "failure_modes": [],
      "xyz_bullets": [
        "Architected an asynchronous Model Context Protocol (MCP) server exposing specialized vector retrieval primitives with deterministic JSON schemas.",
        "Containerized distributed worker nodes using multi-stage Docker builds, trimming deployment image size by 48%."
      ],
      "is_anchor_project": false
    }
  ]
}
```

---

### Step 2: Execute the Pipeline via Terminal & Atomic Versioning
The agent triggers the execution command:

```bash
# Default: Generates clean 1-page PDF resume + interview dossier
python main.py --job <company_slug>

# Or if an alternative format is explicitly requested:
python main.py --job <company_slug> --format docx
python main.py --job <company_slug> --format latex
```

Following creation of `jobs/<company_slug>.json`, execute atomic version control locally:
```bash
git add jobs/<company_slug>.json
git commit -m "config(jobs): generate tailored portfolio for <company_slug>"
```
*(Note: Never auto-push commits to remote).*

---

## 6. The Evaluator-Optimizer Critique Loop

The LangGraph pipeline features an automated evaluation gate:

| Evaluation Check | Criteria & Threshold | Failure Action |
|---|---|---|
| **ATS Keyword Coverage** | Scans resume content against `target_keywords`. Must achieve **$\ge 85\%$ match rate**. | Loops back to Optimizer to inject missing keywords into project descriptions and experience bullets. |
| **Metric Plausibility Bounds** | All percentage improvements must fall within **20% to 60%** (e.g. latency, cost, compute reduction). Claims like "1000% speedup" or impossible hardware claims fail immediately. | Optimizer rewrites metrics to realistic engineering bounds. |
| **Formula & Verbs** | Every project bullet must follow the Google XYZ formula and begin with an approved engineering power verb. | Strips forbidden phrases (*"helped", "worked with"*) and re-structures bullets. |
| **Page Budget Invariant** | Resume content must fit on exactly **1 page** without text truncation or multi-page spillover. | Tightens spacing and formats dense text blocks to preserve single-page layout. |

---

## 7. The Technical Interview Defense Dossier (`<company>_ques.md`)

Each generation produces a companion interview prep document containing:
1. **Executive Architectural Summary**: Role and domain overview, ATS coverage, and plausibility score.
2. **Architectural Trade-offs ("Why Not X?")**: Concrete justification for why technology A was selected over technology B (e.g., Pinecone vs Elasticsearch, vLLM vs TGI, Redis vs Memcached).
3. **Simulated Failure Modes & Disaster Recovery**: Blast radius analysis and automated mitigation runbooks (e.g., KV-cache OOM under burst concurrency, vector DB timeouts).
4. **5 Probing Technical Questions & Model Defense Answers**: Deep-dive questions testing the implementation details of the synthesized projects, complete with battle-tested technical answers.

---

## 8. Browser Automation & Job Application (`finder/` & `BrowseAI/`)

When instructed to find jobs from open browser tabs (e.g., *"find the jobs opened in my chrome browser"*):

1. **Tab Inspection**: `finder/browser_client.py` calls the BrowseAI MCP server (`http://127.0.0.1:12307/mcp`) to retrieve open Chrome tabs.
2. **Platform & Detail Detection**: `finder/job_scraper.py` detects active job postings (LinkedIn, Internshala, Wellfound, etc.) and extracts company, role, stipend, and raw JD text.
3. **Filtering**:
   - **Stipend Filter**: Enforces $\ge \text{₹}20,000/\text{month}$. Postings below this threshold or unpaid internships are skipped.
   - **Role Priority**: Classifies and prioritizes AI/ML roles (AI Engineer, ML Engineer, Agentic Architect) over generic listings.
4. **Deduplication**: `finder/state_tracker.py` computes a unique job ID and checks SQLite `applications.db` to prevent duplicate processing.
5. **Resume Integration**: `finder/resume_integrator.py` dynamically writes `jobs/<company_slug>.json` and runs `main.py --job <slug>` to compile `output/<company_slug>_resume.pdf`.
6. **Form Filling**: `finder/form_filler.py` maps candidate information into web form fields.
7. **Human Gate**: Execution halts before clicking the final submission button, allowing the user to review all fields.

---

## 9. Cross-File Operational Alignment Audit & Version Recovery Playbook

### 9.1 Cross-File Operational Alignment Audit

The operational directive updates across `.antigravity/rules.md`, `.agents/skills/resume-builder/SKILL.md`, and `AGENTS.md` establish a unified, non-conflicting protocol for the Antigravity agent:

| Operational Dimension | `.antigravity/rules.md` | `.agents/skills/resume-builder/SKILL.md` | `AGENTS.md` | Verification Status |
| --- | --- | --- | --- | --- |
| **Execution Context** | Native chat context; no external `.env` API keys; no ad-hoc `force_*.py` scripts. | Invoked natively via chat triggers and registered terminal entry points. | In-chat orchestrator binding `nexus-bridge` MCP tools without external scripts. | **Synchronized & Enforced** |
| **Comp Floor & Filters** | Strict ₹20,000/month minimum; AI/ML role priority; no silent overrides. | Inherits rules; targets technical roles using 15+ keywords. | Evaluates tabs against ₹20,000/month stipend and AI prioritization. | **Synchronized & Enforced** |
| **Version Control** | Mandatory atomic commit per file; conventional commit format; zero auto-push. | Atomic local commit immediately following `jobs/<company_slug>.json` creation. | Atomic commit step integrated into the 2-step resume generation lifecycle. | **Synchronized & Enforced** |
| **Project Slot #1** | Must be selected from `projects.md`; fallback to highest-rigor project if no match. | Sourced from `projects.md`; marked with `"is_anchor_project": true`. | Evaluates `projects.md` for best role fit; sets `"is_anchor_project": true`. | **Synchronized & Enforced** |
| **Project Slots #2 & #3** | Hyper-tailored role synthesis; unconstrained by `projects.md`; metric-dense. | Custom architectures matching target company challenges; `"is_anchor_project": false`. | Targeted engineering architectures built around JD stack; `"is_anchor_project": false`. | **Synchronized & Enforced** |
| **RE-jadx Confinement** | Strictly placed in Work Experience under IFSO Delhi Police; forbidden in Projects. | Confined to Experience block; forbidden in `fallback_projects`. | Placed exclusively in Work Experience; excluded from project slots. | **Synchronized & Enforced** |
| **Metric Generation** | Google XYZ formula; front-loaded verbs; no `[TODO]` tags; 20%–60% plausible bounds. | Metric suppression forbidden; concrete Google XYZ impact numbers required. | Google XYZ formula; active verbs; realistic quantified metrics. | **Synchronized & Enforced** |
| **Candidate Standing** | 3rd Year B.Tech AIML at VIPS, New Delhi. | Invariant: Always reflect 3rd Year standing. | Invariant: Always reflect 3rd Year standing. | **Synchronized & Enforced** |

---

### 9.2 End-to-End Execution Trace

When a job discovery or resume request is initiated in chat, the integrated pipeline executes through six deterministic stages:

```
[Stage 1: Ingestion]  ──► Enumerate Chrome tabs via BrowseAI MCP (finder/browser_client.py)
[Stage 2: Filtration] ──► Parse stipend (≥ ₹20,000/mo) and prioritize AI/ML domain (finder/job_scraper.py)
[Stage 3: Parsing]    ──► Deconstruct JD into 15+ target keywords & architecture bottlenecks
[Stage 4: Selection]  ──► Allocate Slot 1 from projects.md; synthesize Slots 2 & 3; format RE-jadx in Experience
[Stage 5: Generation] ──► Compile output/<slug>_resume.pdf & output/<slug>_ques.md via main.py
[Stage 6: Versioning] ──► Execute atomic git add and git commit locally without pushing
```

1. **Discovery & Browser Inspection**:
   - The agent invokes `nexus-bridge` MCP tools (`get_tabs`, `read_page`) to inspect all active browser tabs.
   - Postings below ₹20,000/month or unpaid are logged as `SKIPPED` in `applications.db` and bypassed.

2. **Job Description Deconstruction**:
   - Role title, company name, domain, languages, frameworks, DBs, and tools are extracted.
   - Minimum 15 technical keywords isolated for $\ge 85\%$ ATS alignment.

3. **Project Slot Allocation & Experience Formatting**:
   - **Slot 1 (`is_anchor_project: true`)**: Inspects `projects.md`:
     - *Direct/Partial Match*: E.g., CV -> *Synapse Ledger*; RAG/LLM -> *Enterprise Self-Reflective RAG Engine*; E-commerce/Agent -> *Omni-Channel Autonomous D2C AI Sales Agent*.
     - *No Direct Match*: Fallback to *Omni-Channel Autonomous D2C AI Sales Agent* or *Enterprise Self-Reflective RAG Engine*.
   - **Slots 2 & 3 (`is_anchor_project: false`)**: Synthesizes two custom architectures matching the target company's challenges.
   - **Work Experience**: Candidate's work on **RE-jadx** is placed under Work Experience as the AI Forensic Internship at IFSO, Delhi Police. Omitted from `fallback_projects`.

4. **Document Compilation**:
   - Writes `jobs/<company_slug>.json` and executes `python main.py --job <company_slug>`.
   - Generates 1-page `output/<company_slug>_resume.pdf` and dossier `output/<company_slug>_ques.md`.

5. **Atomic Version Control**:
   - Stages and commits configuration locally:
     ```bash
     git add jobs/<company_slug>.json
     git commit -m "config(jobs): generate tailored portfolio for <company_slug>"
     ```

---

### 9.3 Version Recovery Playbook (Local Git Diagnostics & Restoration)

Because all file changes are committed locally per atomic step, the repository provides complete rollback safety.

#### Scenario A: Recovering an Accidentally Deleted or Corrupted File
If a file in the workspace (e.g., `projects.md`, `AGENTS.md`, or a script in `src/`) is deleted or corrupted:
```bash
# Verify the deletion or modification status
git status --short

# Restore the file immediately from the last local commit
git restore <path/to/file>

# For legacy Git versions (< 2.23):
git checkout HEAD -- <path/to/file>
```

#### Scenario B: Inspecting Atomic Commit History
To view the per-file commit history and verify changes were staged independently:
```bash
# View the last 10 atomic commits with changed file statistics
git log -n 10 --oneline --stat

# Inspect the exact diff introduced by the latest commit
git show HEAD

# Inspect the exact diff of a specific commit hash
git show <commit_hash>
```

#### Scenario C: Rolling Back a Job Configuration
If a generated `jobs/<company_slug>.json` needs to be reverted to its previous version:
```bash
# Revert the specific file to the state of the previous commit
git checkout HEAD~1 -- jobs/<company_slug>.json

# Re-commit the restoration cleanly
git commit -m "revert(jobs): restore previous configuration for <company_slug>"
```

#### Scenario D: Undoing a Commit While Preserving File Content
If a commit was made with an inaccurate message or before a file was completely edited:
```bash
# Soft reset moves HEAD back one commit, keeping all changes staged in the index
git reset --soft HEAD~1

# Make adjustments, then re-commit
git commit -m "refactor(<scope>): <corrected commit message>"
```

#### Scenario E: Complete Branch Health & Uncommitted File Sanity Check
Before and after automated agent runs, verify that no untracked modifications or uncommitted changes remain:
```bash
# Check for any unstaged or untracked changes
git status

# If clean, the output will confirm:
# "nothing to commit, working tree clean"
```

---

## 10. Agent Invariants & Operational Rules

Any AI agent interacting with this repository must follow these rules:

1. **Token-Saver Directive**:
   - **NEVER** scan, grep, list, or view source files inside `src/`, `templates/`, or `tests/`.
   - The engine is fully implemented. Resumes are configured **exclusively via `jobs/<company_slug>.json`**.
2. **Zero Source Code Modification**:
   - Do not edit files in `src/`, `templates/`, or root (`main.py`, `config.py`).
3. **Silent PDF Default**:
   - Always default to PDF output. Do not prompt the user for output format unless explicitly requested.
4. **Native Context Execution**:
   - All resume and job operations execute natively within chat context. Do not create one-off runner scripts (e.g., `force_*.py`).
5. **Candidate Profile Standing**:
   - Sahil Yadav is in the **3rd Year** of B.Tech in AIML at VIPS, New Delhi. Always preserve this academic standing.
6. **Strict Thresholds & Confinements**:
   - Enforce the ₹20,000/month stipend minimum and prioritize AI roles without exception.
   - Slot 1 must be from `projects.md`. RE-jadx is strictly confined to Work Experience.
7. **Atomic Git Commits**:
   - Commit generated job files locally with conventional commit messages. Never execute `git push`.

---

## 11. Repository File & Directory Map

```text
resume-job/
├── PROJECT_CONTEXT.md         # Master context document for AI models
├── AGENTS.md                  # Main AI agent operational guide & directives
├── README.md                  # Comprehensive architectural guide & setup instructions
├── projects.md                # 10 production-grade anchor projects catalog
├── main.py                    # Core CLI entry point & LangGraph runner
├── requirements.txt           # Python dependencies
├── applications.db            # SQLite database tracking job applications
│
├── .agents/
│   └── skills/
│       └── resume-builder/
│           └── SKILL.md       # AntiGravity resume-builder skill definition
│
├── .antigravity/
│   └── rules.md               # Operational guardrails (native context, filters)
│
├── jobs/                      # Pre-configured & dynamically generated job specs
│   ├── sample_job.json
│   ├── hasamex.json
│   ├── pindrop.json
│   └── ... (<company_slug>.json)
│
├── output/                    # Generated resume artifacts
│   ├── candidate_profile.json # Cached candidate master data
│   ├── <company>_resume.pdf   # Single-page ATS-optimized resume (default)
│   ├── <company>_ques.md      # Technical interview defense dossier
│   ├── portfolio_data.json    # Structured JSON dump of synthesized projects
│   └── old/                   # Non-destructive historical archives
│
├── finder/                    # Browser automation & job scraping package
│   ├── finder_cli.py          # Job-finder CLI & daemon runner
│   ├── browser_client.py      # MCP client communicating with BrowseAI
│   ├── job_scraper.py         # Job portal scrapers & tier classifiers
│   ├── stipend_parser.py      # ₹20k threshold parser
│   ├── state_tracker.py       # SQLite state manager for applications.db
│   ├── resume_integrator.py   # Automated bridge between finder and main.py
│   └── form_filler.py         # Automated DOM form filler
│
└── BrowseAI/                  # Monorepo for Chrome Extension & Fastify Native Host
    ├── SETUP.md               # Setup & connection troubleshooting guide
    ├── packages/
    │   ├── extension/         # Chrome MV3 extension source & output
    │   └── bridge/            # Fastify MCP stdio/SSE server
    └── scripts/               # Host registration and build scripts
```
