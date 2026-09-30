---
name: resume-builder
description: Generates high-impact ATS-optimized resumes and interview defense dossiers for any target job description using the AntiGravity Resume Engine.
---

# AntiGravity Resume Engine — Skill

Use this skill whenever a Job Description (JD), job link, or company name is provided to generate an ATS-optimized resume and technical interview defense dossier.

> [!IMPORTANT]
> **TOKEN-SAVER DIRECTIVE FOR AGENTS:**
> **DO NOT scan, grep, list, or view source files in `src/`, `templates/`, or `tests/`.**[cite: 5]
> The engine is fully implemented[cite: 5]. Resumes are configured **exclusively via `jobs/<company_slug>.json`**.
> Follow the strict 2-step protocol below[cite: 5].

---

## Candidate Profile & Ground-Truth Context

* **Name**: Sahil Yadav
* **Email**: sahillyaadav@gmail.com[cite: 7]
* **Phone**: +91 8700122453[cite: 7]
* **Location**: New Delhi, India[cite: 7]
* **LinkedIn**: linkedin.com/in/sahil-yadav-1ab468249[cite: 7]
* **GitHub**: github.com/Notso-sahil[cite: 7]
* **Education**: Bachelor of Technology (B.Tech) in Artificial Intelligence & Machine Learning (AIML) at Vivekananda Institute of Professional Studies (VIPS), New Delhi (2024 – 2028 Expected)[cite: 7].
* **Academic Standing Invariant**: Always specify **3rd Year** undergraduate standing across all education summaries.

---

## The 2-Step Protocol

### Step 1: Create the Job Config File (`jobs/<company_slug>.json`)
When provided with a target Job Description (JD) or company requirements:
1. Deconstruct the JD into: target role title, company name, technical domain, primary programming languages, frameworks, datastores, cloud/infrastructure tooling, and core engineering challenges.
2. Identify at least 15+ high-density technical keywords matching the role requirements[cite: 6, 7].
3. Apply the **3-Project Portfolio Rule**:
   - **Slot #1 (Anchor Project from `projects.md`)**: Inspect the 10 candidate projects in `projects.md`. Select the single project that best matches the target role's technical stack and domain. If none of the 10 projects match natively, select the most technically demanding project from `projects.md` (e.g., *Omni-Channel Autonomous D2C AI Sales Agent* or *Enterprise Self-Reflective RAG Engine*) and place it at Slot #1[cite: 3]. Set `"is_anchor_project": true`.
   - **Slots #2 & #3 (Role-Targeted Custom Synthesized Projects)**: Synthesize 2 targeted engineering projects custom-built around the job description's exact technical stack, architecture, and bottlenecks[cite: 6, 7]. Set `"is_anchor_project": false`.
   - **Experience Invariant (RE-jadx)**: The **RE-jadx** project must **NEVER** be placed in the `fallback_projects` list[cite: 3]. It belongs strictly in the Work Experience / Internship section under the candidate's tenure as an AI Forensic Intern at IFSO (Special Cell), Delhi Police.
4. Format all bullet points using the **Google XYZ formula**: *"Accomplished [X], as measured by [Y], by implementing [Z]"*[cite: 7]. Front-load with active engineering verbs (*Architected, Benchmarked, Partitioned, Profiled, Deployed, Engineered, Orchestrated*)[cite: 7]. Never suppress metrics with `[TODO]` or placeholders; supply defensible, mathematically plausible metrics within realistic 20%–60% bounds[cite: 2, 7].
5. Write the configuration directly to `jobs/<company_slug>.json` using the schema below.

**Job Config Schema:**
```json
{
  "company_name": "Target Company",
  "role_title": "Target Role Title",
  "seniority_level": "Intern / Junior / Mid-Level",
  "domain": "Target Technical Domain",
  "primary_languages": ["Python", "TypeScript", "C++"],
  "frameworks": ["PyTorch", "vLLM", "FastAPI", "LangGraph"],
  "databases_and_storage": ["Redis", "PostgreSQL", "Qdrant"],
  "infrastructure_and_cloud": ["Docker", "Kubernetes", "AWS"],
  "core_engineering_challenges": [
    "Primary technical bottleneck or latency constraint",
    "Secondary scaling or reliability challenge"
  ],
  "target_keywords": [
    "Keyword 1", "Keyword 2", "Keyword 3", "Keyword 4", "Keyword 5",
    "Keyword 6", "Keyword 7", "Keyword 8", "Keyword 9", "Keyword 10",
    "Keyword 11", "Keyword 12", "Keyword 13", "Keyword 14", "Keyword 15"
  ],
  "soft_skills": [
    "Engineering Ownership", "Systems Architecture", "Cross-Functional Collaboration"
  ],
  "tailored_summary_override": "Dense 3-4 sentence professional summary aligning candidate's background with target company challenges.",
  "fallback_projects": [
    {
      "project_title": "Project Title from projects.md (Slot 1)",
      "archetype": "Core Domain Anchor",
      "high_level_architecture": "Architectural breakdown of the project...",
      "tech_stack": ["Python", "FastAPI", "Qdrant", "Docker"],
      "core_bottleneck": "Primary performance bottleneck addressed...",
      "technical_solution": "Concrete technical mechanism deployed...",
      "live_link": null,
      "quantified_impact_metrics": [
        "Reduced p95 latency by 38%",
        "Increased document recall by 24%"
      ],
      "trade_offs": [
        {
          "decision": "Vector Store Selection",
          "chosen_technology": "Qdrant",
          "rejected_technology": "Pinecone",
          "justification": "On-prem containerization and native hybrid search support."
        }
      ],
      "failure_modes": [
        {
          "scenario": "Upstream API timeout under burst load",
          "impact": "Worker queue starvation",
          "mitigation_strategy": "Asynchronous fallback routing with exponential backoff"
        }
      ],
      "xyz_bullets": [
        "Architected an end-to-end retrieval pipeline using Qdrant and Reciprocal Rank Fusion, improving technical document recall by 24% under concurrent queries.",
        "Engineered asynchronous FastAPI microservices with Redis caching, sustaining sub-45ms responses and reducing downstream model overhead by 34%.",
        "Benchmarked cross-encoder reranking models with Cohere Rerank 3, cutting prompt token overhead by 45% while achieving 0.94 answer faithfulness."
      ],
      "is_anchor_project": true
    },
    {
      "project_title": "Custom Role-Tailored Architecture 1 (Slot 2)",
      "archetype": "Distributed Systems & Scale",
      "high_level_architecture": "Targeted architecture matching company requirements...",
      "tech_stack": ["Python", "PyTorch", "vLLM", "Redis"],
      "core_bottleneck": "Concurrency or throughput constraint...",
      "technical_solution": "Distributed caching and model serving optimization...",
      "live_link": null,
      "quantified_impact_metrics": [
        "Increased throughput from 120 to 380 QPS",
        "Cut GPU memory allocation by 35%"
      ],
      "trade_offs": [],
      "failure_modes": [],
      "xyz_bullets": [
        "Deployed a distributed inference gateway utilizing vLLM and PagedAttention, cutting p99 generation latency by 42% across 500+ concurrent requests.",
        "Engineered real-time telemetry pipelines using Redis Streams and Prometheus, isolating memory leaks across multi-worker clusters."
      ],
      "is_anchor_project": false
    },
    {
      "project_title": "Custom Role-Tailored Architecture 2 (Slot 3)",
      "archetype": "Platform Tooling & MCP",
      "high_level_architecture": "Infrastructure and tooling architecture...",
      "tech_stack": ["TypeScript", "Python", "Docker", "PostgreSQL"],
      "core_bottleneck": "Tool serialization latency and schema validation failures...",
      "technical_solution": "Asynchronous Model Context Protocol (MCP) server integration...",
      "live_link": null,
      "quantified_impact_metrics": [
        "Eliminated schema validation errors to 0%",
        "Reduced end-to-end execution time by 54%"
      ],
      "trade_offs": [],
      "failure_modes": [],
      "xyz_bullets": [
        "Engineered an asynchronous Model Context Protocol (MCP) server in Python, exposing custom forensic utilities with deterministic Pydantic v2 schemas.",
        "Containerized local worker environments using multi-stage Docker builds, trimming deployment image footprint by 48%."
      ],
      "is_anchor_project": false
    }
  ]
}