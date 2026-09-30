# AntiGravity Resume Engine — Agent Directives & Operational Guide

> [!IMPORTANT]
> **TOKEN-SAVER DIRECTIVE FOR AGENTS:**
> **DO NOT scan, grep, list, or view source files in `src/`, `templates/`, or `tests/`.**
> The engine is complete, fully implemented, and automated. Resumes are configured **exclusively via `jobs/<company_slug>.json`**.
> When asked to generate a resume or target a job, follow the strict 2-step protocol below.

---

## Candidate Profile & Ground-Truth Context

* **Name**: Sahil Yadav
* **Email**: sahillyaadav@gmail.com[cite: 7]
* **Phone**: +91 8700122453[cite: 7]
* **Location**: New Delhi, India[cite: 7]
* **LinkedIn**: linkedin.com/in/sahil-yadav-1ab468249[cite: 7]
* **GitHub**: github.com/Notso-sahil[cite: 7]
* **Education**: Bachelor of Technology (B.Tech) in Artificial Intelligence & Machine Learning (AIML) at Vivekananda Institute of Professional Studies (VIPS), New Delhi (2024 – 2028 Expected)[cite: 7].
* **Academic Standing Invariant**: Always reflect **3rd Year** undergraduate standing across all education blocks[cite: 5, 7].

---

## In-Chat Orchestration & Native Operations
You operate as an **in-chat orchestrator** using native context[cite: 4, 6]. Do NOT call external API keys (`.env`) or run ad-hoc scripts (`force_*.py`)[cite: 4, 6]. Native browser connectivity runs via the `nexus-bridge` Model Context Protocol (MCP) server[cite: 2, 7].

### Chat Triggers
When the user issues intent triggers such as:
- *"find the jobs opened in my chrome browser"*
- *"find jobs"*
- *"apply to jobs in my open tabs"*

Execute the discovery and resume pipeline in sequence:
1. Enumerate and inspect open Chrome browser tabs via `nexus-bridge` MCP tools (`get_tabs`, `read_page`).
2. Apply strict eligibility criteria:
   - **Stipend Threshold**: Enforce $\ge \text{₹}20,000/\text{month}$ (or $\ge \text{₹}2.4\text{ LPA}$ equivalent)[cite: 4, 7]. Skip non-qualifying or unpaid listings[cite: 4, 7].
   - **Role Prioritization**: Process AI/ML, GenAI, Agentic Systems, and Python Backend listings first[cite: 4, 7].
3. For each eligible role, extract the company name, role title, and raw job description[cite: 7].
4. Synthesize the configuration payload into `jobs/<company_slug>.json` adhering to the **3-Project Portfolio Rule**[cite: 3, 6].
5. Execute the pipeline locally via terminal to generate artifacts[cite: 5, 6].
6. Display a concise markdown status table detailing inspected tabs, eligibility verdicts, generated resume paths, and application status[cite: 6].

---

## The 2-Step Protocol for Generating a Resume

### Step 1: Create the Job Config File (`jobs/<company_slug>.json`)
When provided with a Job Description (JD) or company link:
1. Deconstruct the JD into: target role title, company name, domain, core engineering challenges, and technical stack[cite: 5, 6].
2. Identify at least 15+ relevant technical keywords for ATS match density ($\ge 85\%$).
3. Apply the **Project Allocation Hierarchy**:
   - **Slot #1 (Core Portfolio Anchor — Mandatory)**:
     - Must be drawn directly from the candidate's verified project catalog (`projects.md`).
     - Select the project that best matches the role's primary domain and tools.
     - *Fallback*: If none match directly, select the most technically demanding project (e.g., *Omni-Channel Autonomous D2C AI Sales Agent* or *Enterprise Self-Reflective RAG Engine*) and place it at Slot #1[cite: 3].
     - Flag with `"is_anchor_project": true`.
   - **Slots #2 & #3 (Role-Targeted Custom Architectures)**:
     - Synthesize 2 targeted engineering project architectures custom-tailored to solve the target company's exact engineering bottlenecks and tech stack[cite: 6, 7].
     - These do not need to exist in `projects.md`; design them to maximize interview selection[cite: 3, 6].
     - Flag with `"is_anchor_project": false`.
   - **RE-jadx Confinement Rule**:
     - **RE-jadx** must **NEVER** appear in `fallback_projects`[cite: 3].
     - It is reserved exclusively for the Work Experience section under the candidate's verified tenure as an AI Forensic Intern at IFSO (Special Cell), Delhi Police.
4. Format all bullet points using the **Google XYZ formula**: *"Accomplished [X], as measured by [Y], by implementing [Z]"*[cite: 7]. Front-load with active power verbs (*Architected, Benchmarked, Partitioned, Profiled, Deployed, Engineered, Orchestrated*)[cite: 7].
5. Prohibit metric suppression: never insert `[TODO]` or empty brackets. Provide realistic, defensible engineering metrics within 20%–60% bounds[cite: 2, 7].
6. Write the configuration file to `jobs/<company_slug>.json` using this schema[cite: 6]:

```json
{
  "company_name": "Target Company",
  "role_title": "AI Platform Engineer",
  "seniority_level": "Intern / Junior / Mid-Level",
  "domain": "Autonomous AI Agents & Distributed Systems",
  "primary_languages": ["Python", "C++", "TypeScript"],
  "frameworks": ["PyTorch", "vLLM", "FastAPI", "LangGraph"],
  "databases_and_storage": ["Redis", "PostgreSQL", "Qdrant"],
  "infrastructure_and_cloud": ["Docker", "Kubernetes", "AWS Cloud GPUs", "Triton"],
  "core_engineering_challenges": [
    "High-throughput vector indexing and sub-10ms similarity search under concurrent load",
    "Optimizing KV-cache footprint and speculative decoding for multi-agent loops"
  ],
  "target_keywords": [
    "Python", "PyTorch", "vLLM", "LangGraph", "FastAPI", "Docker", "RAG",
    "Speculative Decoding", "Continuous Batching", "KV-Cache", "Distributed Systems",
    "Vector Search", "Qdrant", "Redis", "Kubernetes"
  ],
  "soft_skills": [
    "Engineering Ownership", "Systems Architecture", "Cross-functional Collaboration"
  ],
  "tailored_summary_override": "High-impact 3-4 sentence tailored summary aligning candidate background with target company challenges.",
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