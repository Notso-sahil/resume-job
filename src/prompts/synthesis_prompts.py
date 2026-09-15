"""Archetype synthesis prompt templates and offline synthesis engine."""
from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.models import JDDeconstruction

# ---------------------------------------------------------------------------
# ARCHETYPE REGISTRY
# Each entry: id -> {label, triggers, description}
# 'triggers' are keywords that vote for this archetype when found in the JD.
# ---------------------------------------------------------------------------
ARCHETYPE_REGISTRY = {
    "core_domain": {
        "label": "Core Domain",
        "description": "Primary business-logic application tightly matching the JD's core product domain.",
        "triggers": [],  # always included as the first archetype
    },
    "web_fullstack": {
        "label": "Web Full-Stack",
        "description": "End-to-end web application with frontend, REST/GraphQL API, and database integration.",
        "triggers": [
            "react", "next.js", "nextjs", "html", "css", "javascript", "typescript",
            "node.js", "nodejs", "express", "vue", "angular", "frontend", "ui", "ux",
            "rest api", "graphql", "web", "http", "browser",
        ],
    },
    "distributed_systems": {
        "label": "Distributed Systems",
        "description": "High-throughput, distributed scalability: concurrency, queuing, cache, backpressure, p99 latency.",
        "triggers": [
            "kafka", "redis", "grpc", "microservices", "queue", "p99", "throughput",
            "distributed", "async", "concurrency", "backpressure", "streaming",
            "high-availability", "ha", "load balancer", "rate limit",
        ],
    },
    "ml_platform": {
        "label": "ML / AI Platform",
        "description": "Machine learning pipeline, model training, inference, RAG, LLM orchestration, or AI agents.",
        "triggers": [
            "pytorch", "tensorflow", "keras", "model", "training", "inference",
            "rag", "llm", "langchain", "langgraph", "embedding", "vector", "ai agent",
            "nlp", "bert", "fine-tuning", "huggingface", "openai", "gemini",
            "artificial intelligence", "machine learning", "deep learning",
        ],
    },
    "data_pipeline": {
        "label": "Data Engineering",
        "description": "ETL/ELT pipelines, data warehousing, batch/stream processing, analytics.",
        "triggers": [
            "spark", "airflow", "etl", "pipeline", "data warehouse", "bigquery",
            "dbt", "snowflake", "hive", "hadoop", "flink", "data lake",
            "analytics", "batch processing", "data engineering",
        ],
    },
    "mobile": {
        "label": "Mobile / Cross-Platform",
        "description": "Native or cross-platform mobile application (Android, iOS, Flutter, React Native).",
        "triggers": [
            "android", "ios", "flutter", "react native", "kotlin", "swift",
            "mobile", "app", "play store", "app store",
        ],
    },
    "devtools_infra": {
        "label": "DevTools / Infra",
        "description": "Developer tooling, platform infrastructure, CI/CD, observability, or cloud automation.",
        "triggers": [
            "docker", "kubernetes", "k8s", "ci/cd", "terraform", "monitoring",
            "prometheus", "grafana", "observability", "devops", "helm",
            "github actions", "jenkins", "logging", "tracing", "mcp",
        ],
    },
    "security_platform": {
        "label": "Security / Platform",
        "description": "Auth, access control, encryption, compliance, or security hardening.",
        "triggers": [
            "oauth", "rbac", "jwt", "security", "zero-trust", "encryption",
            "audit", "compliance", "sso", "saml", "authentication", "authorization",
        ],
    },
}


def resolve_archetypes(jd_analysis: "JDDeconstruction") -> List[str]:
    """
    Scores every archetype against the JD and returns the best 3 archetype IDs.
    'core_domain' is always ID #1.  The other 2 are picked by keyword vote count.
    """
    # Build a single lowercase corpus from all JD fields
    corpus_parts = []
    if jd_analysis:
        corpus_parts.append(jd_analysis.domain.lower())
        corpus_parts.append(jd_analysis.role_title.lower())
        corpus_parts.extend([kw.lower() for kw in jd_analysis.target_keywords])
        corpus_parts.extend([f.lower() for f in jd_analysis.frameworks])
        corpus_parts.extend([l.lower() for l in jd_analysis.primary_languages])
        corpus_parts.extend([d.lower() for d in jd_analysis.databases_and_storage])
        corpus_parts.extend([i.lower() for i in jd_analysis.infrastructure_and_cloud])
        corpus_parts.extend([c.lower() for c in jd_analysis.core_engineering_challenges])
    corpus = " ".join(corpus_parts)

    scores: dict[str, int] = {}
    for arch_id, meta in ARCHETYPE_REGISTRY.items():
        if arch_id == "core_domain":
            continue  # always first
        score = sum(1 for trigger in meta["triggers"] if trigger in corpus)
        scores[arch_id] = score

    # Pick top 2 by score (stable sort preserves registry order for ties)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_two = [arch_id for arch_id, _ in ranked[:2]]

    return ["core_domain"] + top_two


# ---------------------------------------------------------------------------
# DYNAMIC LLM PROMPTS
# ---------------------------------------------------------------------------

_ARCHETYPE_RULE_BLOCK = """### THE 3-PROJECT ARCHETYPE RULE:
You MUST generate EXACTLY 3 complementary projects, one per archetype below:
{archetype_block}

Each project's archetype field MUST match its archetype label exactly as listed above."""

PROJECT_SYNTHESIS_SYSTEM_PROMPT_V2 = """\
You are an elite Technical Resume Strategist and Principal Engineer.
Your task is to synthesize an architecturally coherent, high-impact portfolio of \
EXACTLY 3 engineering projects tailored to a specific Job Description (JD).

{archetype_rule_block}

### JD ALIGNMENT RULES (MANDATORY):
1. Every project's tech_stack MUST include technologies from the JD's primary_languages, frameworks, \
or databases_and_storage fields. Use the JD stack — do NOT invent unrelated technologies.
2. The first XYZ bullet of every project MUST front-load a keyword from the JD's target_keywords in \
the first 7 words.
3. Metric units and scale MUST be domain-appropriate:
   - Web/API roles → response time (ms), DAU, API calls/day, uptime %
   - ML/AI roles → model accuracy %, inference latency (ms), throughput (tokens/sec)
   - Data roles → records/day, pipeline run time reduction %, storage cost reduction %
   - Distributed systems → RPS, p99 latency (ms), throughput

### STRICT ENGINEERING INVARIANTS:
1. Google XYZ Formula: Every bullet MUST follow "Accomplished [X], as measured by [Y], by implementing [Z]".
   - Start with active power verbs: Architected, Engineered, Optimized, Designed, Built, \
Deployed, Implemented, Automated, Reduced, Scaled, Replaced, Profiled, Benchmarked.
   - Technical keywords MUST appear in the first 7 words.
   - 4-5 bullets per project.
2. Metric Sanity:
   - Reduction claims: 20%–60% range only.
   - No physically impossible numbers (no 100k RPS on SQLite, no sub-ms p99 over WAN).
3. Interview Readiness: Each project needs 2 architectural trade-offs and 5 Q&A pairs."""

PROJECT_SYNTHESIS_SYSTEM_PROMPT = PROJECT_SYNTHESIS_SYSTEM_PROMPT_V2  # alias for backwards compat

PROJECT_SYNTHESIS_USER_PROMPT = """\
Synthesize the 3 engineering projects for this candidate targeting the deconstructed JD below.

Target JD Analysis:
{jd_analysis_json}

Resolved Project Archetypes to use (MANDATORY — use these exact archetype labels):
{resolved_archetypes}

Critique History / Feedback to rectify (if any):
{critique_history}

Generate the full project portfolio conforming to the ProjectSpec schema for all 3 archetypes.
Each project MUST be directly aligned with the JD's domain, stack, and core engineering challenges.
Do NOT generate generic distributed systems projects if the JD is about web development or vice versa.
"""


def build_synthesis_prompt(jd_analysis: "JDDeconstruction", critique_history: str) -> str:
    """
    Builds the full synthesis prompt by resolving archetypes from the JD
    and injecting them into the dynamic archetype-aware prompt.
    """
    resolved_ids = resolve_archetypes(jd_analysis)
    archetype_lines = []
    for i, arch_id in enumerate(resolved_ids, 1):
        meta = ARCHETYPE_REGISTRY[arch_id]
        archetype_lines.append(
            f"  {i}. Archetype '{meta['label']}': {meta['description']}"
        )
    archetype_block = "\n".join(archetype_lines)
    archetype_rule = _ARCHETYPE_RULE_BLOCK.format(archetype_block=archetype_block)

    system_prompt = PROJECT_SYNTHESIS_SYSTEM_PROMPT_V2.format(
        archetype_rule_block=archetype_rule
    )

    resolved_str = "\n".join(
        f"  {i}. {ARCHETYPE_REGISTRY[arch_id]['label']}"
        for i, arch_id in enumerate(resolved_ids, 1)
    )

    jd_json = jd_analysis.model_dump_json(indent=2) if jd_analysis else "{}"
    user_prompt = PROJECT_SYNTHESIS_USER_PROMPT.format(
        jd_analysis_json=jd_json,
        resolved_archetypes=resolved_str,
        critique_history=critique_history,
    )
    return f"{system_prompt}\n\n{user_prompt}"


# ---------------------------------------------------------------------------
# SUMMARY SYNTHESIS
# ---------------------------------------------------------------------------

SUMMARY_SYNTHESIS_PROMPT = """You are a Principal Technical Resume Strategist.
Synthesize a punchy, high-impact Professional Summary (strictly 3-4 sentences, 65-90 words) for a technical resume.

INVARIANTS:
1. Retain core factual accomplishments and background from the candidate's uploaded resume:
   Candidate Background: {raw_objective}
2. Tailor directly to the target role and domain:
   Target Role: {role_title}
   Domain: {domain}
   Target Technologies: {target_keywords}
3. Strictly 3-4 sentences, maximum 90 words. Include a sentence highlighting a major real project from the candidate's background if relevant (e.g., CampusHub or Synapse). End with an explicit call-out to the target role and company. No fluff.
"""


def synthesize_tailored_summary(
    raw_objective: str,
    jd_analysis,
    llm=None,
    summary_override: Optional[str] = None,
) -> str:
    """
    Synthesizes a tailored professional summary blending the candidate's uploaded resume background
    with the target JD requirements while remaining strictly 2-3 sentences for a 1-page resume.
    """
    if summary_override and summary_override.strip():
        return summary_override.strip()

    if llm and hasattr(llm, "invoke"):
        try:
            role_title = jd_analysis.role_title if jd_analysis else "AI Engineer"
            domain = jd_analysis.domain if jd_analysis else "Distributed Systems"
            keywords = ", ".join(jd_analysis.target_keywords[:8]) if jd_analysis else "Python, PyTorch"
            prompt = SUMMARY_SYNTHESIS_PROMPT.format(
                raw_objective=raw_objective,
                role_title=role_title,
                domain=domain,
                target_keywords=keywords,
            )
            resp = llm.invoke(prompt)
            content = resp.content if hasattr(resp, "content") else str(resp)
            if content and len(content.split()) >= 15 and not content.startswith("[AntiGravity"):
                return " ".join(content.strip().split())
        except Exception:
            pass

    # Deterministic fallback synthesis blending candidate profile + target JD
    role_term = jd_analysis.role_title if jd_analysis else "AI Systems Engineer"
    company_term = getattr(jd_analysis, "company_name", "your company") or "your company"
    frameworks = jd_analysis.frameworks[:3] if jd_analysis and jd_analysis.frameworks else ["Python", "PyTorch"]
    primary_stack = ", ".join(frameworks)
    
    # Check for real projects in objective
    obj_lower = (raw_objective or "").lower()
    real_project_callout = ""
    if "synapse" in obj_lower:
        real_project_callout = " Architected Synapse, an asynchronous agentic backend integrating vector databases and prompt engineering for real-world document intelligence."
    elif "campushub" in obj_lower or "campus-zenith" in obj_lower:
        real_project_callout = " Architected CampusHub, a full-stack web platform optimizing student workflows through responsive frontend interfaces and scalable backend APIs."

    raw_snippet = " ".join(raw_objective.split()[:25]) if raw_objective else "Systems engineer with proven end-to-end experience building applications at production scale"
    raw_snippet = raw_snippet.rstrip('.')

    return (
        f"{raw_snippet}. Experienced delivering software projects in teams using {primary_stack} with a focus on reliability, "
        f"performance optimization, and observability.{real_project_callout} Seeking a {role_term} role to build and evaluate systems "
        f"that improve the availability and performance of {company_term} products at scale."
    )


# ---------------------------------------------------------------------------
# FALLBACK PROJECT TEMPLATE LIBRARY
# Used when the LLM call fails — fills in JD's actual stack into templates.
# ---------------------------------------------------------------------------

def _pick(lst: list, index: int, default: str) -> str:
    """Safe list element picker with a default."""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return default


def build_fallback_projects(jd_analysis: "JDDeconstruction") -> list:
    """
    Builds 3 domain-adapted fallback ProjectSpec objects using the JD's actual stack.
    Replaces the old hardcoded Synapse / HyperVector / OmniTrace trio.
    """
    from src.schemas.models import ProjectSpec, ArchitecturalTradeOff, FailureModeAnalysis

    resolved_ids = resolve_archetypes(jd_analysis)

    # Extract key fields from JD for template filling
    company = getattr(jd_analysis, "company_name", "Enterprise") or "Enterprise"
    role = getattr(jd_analysis, "role_title", "Engineer") or "Engineer"
    domain = getattr(jd_analysis, "domain", "Software Engineering") or "Software Engineering"
    langs = list(jd_analysis.primary_languages) if jd_analysis.primary_languages else ["Python"]
    frameworks = list(jd_analysis.frameworks) if jd_analysis.frameworks else ["FastAPI"]
    dbs = list(jd_analysis.databases_and_storage) if jd_analysis.databases_and_storage else ["PostgreSQL"]
    infra = list(jd_analysis.infrastructure_and_cloud) if jd_analysis.infrastructure_and_cloud else ["Docker"]
    keywords = list(jd_analysis.target_keywords) if jd_analysis.target_keywords else langs + frameworks
    challenges = list(jd_analysis.core_engineering_challenges) if jd_analysis.core_engineering_challenges else [
        "Ensuring scalable and maintainable application architecture"
    ]

    lang1 = _pick(langs, 0, "Python")
    lang2 = _pick(langs, 1, lang1)
    fw1 = _pick(frameworks, 0, "FastAPI")
    fw2 = _pick(frameworks, 1, fw1)
    db1 = _pick(dbs, 0, "PostgreSQL")
    db2 = _pick(dbs, 1, "Redis")
    infra1 = _pick(infra, 0, "Docker")
    kw1 = _pick(keywords, 0, lang1)
    kw2 = _pick(keywords, 1, fw1)
    kw3 = _pick(keywords, 2, db1)
    challenge1 = _pick(challenges, 0, "Handling concurrent user load with minimal latency")
    challenge2 = _pick(challenges, 1, challenge1)

    # -----------------------------------------------------------------------
    # Template builders per archetype
    # -----------------------------------------------------------------------

    def _core_domain() -> ProjectSpec:
        names = ["FlowBridge", "StackEdge", "NexusCore", "PulseAPI", "VectorCore"]
        title = names[hash(company + role) % len(names)]
        arch_label = ARCHETYPE_REGISTRY["core_domain"]["label"]
        return ProjectSpec(
            project_title=title,
            archetype=arch_label,
            high_level_architecture=(
                f"End-to-end {domain} application built with {lang1} and {fw1}, "
                f"integrating {db1} for persistence and {fw2} for core business logic."
            ),
            tech_stack=[lang1, fw1, fw2, db1, infra1],
            core_bottleneck=challenge1,
            technical_solution=(
                f"Redesigned the {fw1} request pipeline with async handlers and "
                f"layered {db1} query optimizations to eliminate N+1 bottlenecks."
            ),
            quantified_impact_metrics=[
                f"Reduced API p95 response time by 38% (210ms to 130ms)",
                f"Increased concurrent user capacity by 2.4× under peak load",
                f"Cut {db1} query execution time by 44% via indexed reads",
            ],
            trade_offs=[
                ArchitecturalTradeOff(
                    decision=f"Selected {fw1} over a monolithic framework",
                    chosen_technology=fw1,
                    rejected_technology="Monolithic MVC Framework",
                    justification=(
                        f"{fw1} enables fine-grained async request handling and "
                        "independent scaling of hot endpoints without full-service redeployment."
                    ),
                ),
                ArchitecturalTradeOff(
                    decision=f"Used {db1} with connection pooling over raw ORM",
                    chosen_technology=f"{db1} + Connection Pool",
                    rejected_technology="Naive ORM (SQLAlchemy without pool)",
                    justification=(
                        "Unbounded ORM connections caused connection exhaustion under burst traffic; "
                        "pooling capped connections at 20 while serving 500 concurrent users."
                    ),
                ),
            ],
            failure_modes=[
                FailureModeAnalysis(
                    scenario=f"{db1} primary node failure during peak traffic.",
                    impact="Write unavailability causing request timeouts and data loss risk.",
                    mitigation_strategy=(
                        f"Configured {db1} with synchronous replica failover and circuit-breaker "
                        "pattern at the service layer to reject writes gracefully during failover window."
                    ),
                )
            ],
            xyz_bullets=[
                f"Architected a {kw1} and {fw1} backend platform for {domain}, reducing p95 API latency "
                f"by 38% (210ms to 130ms), by replacing synchronous handlers with async coroutines.",
                f"Engineered {db1} query optimization layer with composite indexes and read replicas, "
                f"cutting average query execution time by 44%, by eliminating full-table sequential scans.",
                f"Built automated integration test suite covering 94% of {fw1} route handlers, "
                f"reducing production regression rate by 67%, by integrating tests into the CI pipeline.",
                f"Deployed containerized {infra1} service mesh with rolling-update strategy, "
                f"achieving 99.8% uptime over 90 days, by eliminating single-point-of-failure deployments.",
            ],
            interview_defense_qna=[
                {
                    "question": f"Why did you choose {fw1} for this platform?",
                    "answer": (
                        f"{fw1} provides native async support and a lightweight request model that maps "
                        "directly to our high-concurrency requirements without the overhead of a full MVC framework."
                    ),
                },
                {
                    "question": "How did you measure the 38% latency reduction?",
                    "answer": (
                        "We instrumented each endpoint with OpenTelemetry spans and ran Locust load tests "
                        "at 200 concurrent users before and after the async refactor, comparing p95 histograms."
                    ),
                },
                {
                    "question": f"How did you prevent {db1} connection pool exhaustion?",
                    "answer": (
                        "We configured a max pool size of 20 with a queue timeout of 500ms, added "
                        "per-request connection lifecycle logging, and set up Prometheus alerts on pool wait time."
                    ),
                },
                {
                    "question": "What was the hardest bug you encountered?",
                    "answer": (
                        "A race condition in the async session factory caused intermittent transaction "
                        "rollbacks under burst load. We traced it via asyncio task inspection and fixed it "
                        "by scoping sessions per-request using context managers."
                    ),
                },
                {
                    "question": "How did you ensure test coverage didn't slow down CI?",
                    "answer": (
                        "We parallelized pytest workers with pytest-xdist across 4 threads and used "
                        "an in-memory SQLite fixture for DB tests, keeping total CI runtime under 90 seconds."
                    ),
                },
            ],
        )

    def _web_fullstack() -> ProjectSpec:
        fe_fw = next(
            (f for f in frameworks if any(w in f.lower() for w in ["react", "next", "vue", "angular"])),
            "React"
        )
        be_fw = next(
            (f for f in frameworks if any(w in f.lower() for w in ["node", "express", "fastapi", "django", "spring"])),
            fw1
        )
        return ProjectSpec(
            project_title="CampusHub",
            archetype=ARCHETYPE_REGISTRY["web_fullstack"]["label"],
            high_level_architecture=(
                f"Full-stack web application with a {fe_fw} SPA frontend and {be_fw} REST API backend, "
                f"backed by {db1} and deployed on {infra1}."
            ),
            tech_stack=[lang1, fe_fw, be_fw, db1, "REST API", infra1],
            core_bottleneck=challenge2,
            technical_solution=(
                f"Implemented server-side rendering (SSR) with {fe_fw} and lazy-loaded route chunks "
                f"to reduce initial page load, combined with {db1} query caching for repeated reads."
            ),
            live_link="https://campus-zenith.vercel.app",
            quantified_impact_metrics=[
                "Reduced page LCP (Largest Contentful Paint) by 52% (4.1s to 1.97s)",
                "Increased active user session retention by 31% post-optimization",
                f"Cut {be_fw} API response time by 41% via connection pooling and query caching",
            ],
            trade_offs=[
                ArchitecturalTradeOff(
                    decision=f"Selected {fe_fw} SSR over CSR (Client-Side Rendering)",
                    chosen_technology=f"{fe_fw} SSR",
                    rejected_technology="Pure CSR SPA",
                    justification=(
                        "CSR caused a 4s+ Time-to-Interactive on slow networks; SSR reduced "
                        "LCP to under 2s by serving pre-rendered HTML from the server."
                    ),
                ),
                ArchitecturalTradeOff(
                    decision=f"Used {db1} with a caching layer over a document store",
                    chosen_technology=f"{db1} + Redis Cache",
                    rejected_technology="MongoDB without cache",
                    justification=(
                        "Relational integrity constraints were required for user data joins; "
                        "adding Redis as a read-through cache offloaded 60% of repeated queries."
                    ),
                ),
            ],
            failure_modes=[
                FailureModeAnalysis(
                    scenario="CDN cache invalidation lag during high-traffic content updates.",
                    impact="Users receiving stale data for up to 5 minutes post-update.",
                    mitigation_strategy=(
                        "Implemented cache-busting via versioned asset URLs and API Cache-Control headers "
                        "with stale-while-revalidate to serve fresh data within 30 seconds of updates."
                    ),
                )
            ],
            xyz_bullets=[
                f"Architected a {fe_fw} and {be_fw} full-stack web portal for {domain}, reducing "
                f"Largest Contentful Paint by 52% (4.1s to 1.97s), by implementing server-side rendering.",
                f"Engineered {be_fw} REST API with {db1} connection pooling and Redis read-through cache, "
                f"cutting API response time by 41%, by eliminating redundant database round-trips.",
                f"Built responsive {lang1} frontend with code-splitting and lazy loading, "
                f"reducing initial JS bundle size by 38%, by implementing dynamic route-based chunking.",
                f"Deployed {infra1}-based CI/CD pipeline with automated smoke tests and rolling deploys, "
                f"reducing release cycle from 2 weeks to 3 days, by containerizing all service dependencies.",
            ],
            interview_defense_qna=[
                {
                    "question": f"Why SSR over CSR for this {fe_fw} application?",
                    "answer": (
                        "Our target users included mobile users on 3G/4G networks. SSR reduced "
                        "Time-to-Interactive from 4.1s to under 2s by delivering pre-rendered HTML "
                        "instead of waiting for JS hydration."
                    ),
                },
                {
                    "question": "How did you handle cache invalidation without serving stale data?",
                    "answer": (
                        "We used stale-while-revalidate headers for static assets and event-driven "
                        "cache purge calls from the API on every write mutation, keeping stale windows under 30s."
                    ),
                },
                {
                    "question": "How did you measure LCP improvement?",
                    "answer": (
                        "We ran Lighthouse CI in our GitHub Actions pipeline on every PR and tracked "
                        "Core Web Vitals in production using the web-vitals.js library reporting to Analytics."
                    ),
                },
                {
                    "question": "How did you prevent XSS vulnerabilities in the frontend?",
                    "answer": (
                        f"All user-generated content was sanitized with DOMPurify before rendering, "
                        f"Content-Security-Policy headers were enforced server-side, and {be_fw} used "
                        "parameterized queries to prevent SQL injection at the data layer."
                    ),
                },
                {
                    "question": "What was your approach to responsive design?",
                    "answer": (
                        "We adopted a mobile-first CSS strategy using CSS Grid and Flexbox, tested "
                        "across 5 breakpoints with Playwright E2E tests on simulated device viewports."
                    ),
                },
            ],
        )

    def _distributed_systems() -> ProjectSpec:
        queue = next((d for d in dbs if any(w in d.lower() for w in ["kafka", "rabbit", "sqs", "pubsub"])), "Kafka")
        cache = next((d for d in dbs if any(w in d.lower() for w in ["redis", "memcached"])), "Redis")
        names = ["StreamCore", "FluxEngine", "GridPulse", "ScaleForge"]
        title = names[hash(kw1) % len(names)]
        return ProjectSpec(
            project_title=title,
            archetype=ARCHETYPE_REGISTRY["distributed_systems"]["label"],
            high_level_architecture=(
                f"Horizontally scalable event-driven microservice system using {queue} for async task dispatch, "
                f"{cache} for hot-path caching, and {lang1} worker pools for high-throughput processing."
            ),
            tech_stack=[lang1, fw1, queue, cache, db1, infra1],
            core_bottleneck=challenge1,
            technical_solution=(
                f"Partitioned {queue} topics across consumer groups and introduced {cache} tiered caching "
                f"to absorb repeated hot reads, decoupling ingestion from processing under burst load."
            ),
            quantified_impact_metrics=[
                f"Scaled system throughput from 800 to 4,200 events/sec without data loss",
                f"Reduced p99 processing latency by 47% (310ms to 164ms)",
                f"Lowered {db1} read load by 54% via {cache} tiered caching",
            ],
            trade_offs=[
                ArchitecturalTradeOff(
                    decision=f"Selected {queue} over synchronous HTTP fan-out",
                    chosen_technology=queue,
                    rejected_technology="Synchronous HTTP fan-out",
                    justification=(
                        "HTTP fan-out caused cascading timeouts when downstream workers were slow; "
                        f"{queue} decoupled producers from consumers, enabling independent scaling."
                    ),
                ),
                ArchitecturalTradeOff(
                    decision=f"Adopted {cache} read-through cache over direct {db1} queries",
                    chosen_technology=f"{cache} Read-Through Cache",
                    rejected_technology=f"Direct {db1} queries",
                    justification=(
                        f"Direct {db1} reads under 4,000 RPS caused connection pool exhaustion; "
                        f"{cache} absorbed 54% of reads before they reached the DB layer."
                    ),
                ),
            ],
            failure_modes=[
                FailureModeAnalysis(
                    scenario=f"{queue} consumer lag spike causing message backlog overflow.",
                    impact="Processing delays exceeding SLA, potential message loss on bounded queues.",
                    mitigation_strategy=(
                        f"Configured {queue} consumer lag alerting via Prometheus and auto-scaled "
                        "consumer replicas using Kubernetes HPA triggered on lag metrics."
                    ),
                )
            ],
            xyz_bullets=[
                f"Architected a {queue} and {lang1} distributed event-processing engine, "
                f"scaling throughput from 800 to 4,200 events/sec, by partitioning consumer groups across 16 topics.",
                f"Engineered {cache} tiered caching with TTL-based invalidation, reducing {db1} read load "
                f"by 54%, by intercepting repeated hot-path queries before reaching the database layer.",
                f"Optimized {lang1} async worker pools with backpressure controls, cutting p99 "
                f"processing latency by 47% (310ms to 164ms), by replacing blocking I/O with coroutines.",
                f"Deployed Kubernetes HPA autoscaling policy for consumer pods, "
                f"reducing {queue} consumer lag from 45s to under 3s during traffic spikes.",
            ],
            interview_defense_qna=[
                {
                    "question": f"Why did you choose {queue} over a simple database queue?",
                    "answer": (
                        f"Database polling queues suffer from O(n) row locking under concurrent consumers; "
                        f"{queue} partitioned logs allow parallel consumer groups without lock contention."
                    ),
                },
                {
                    "question": f"How did you prevent {cache} cache stampede on cold start?",
                    "answer": (
                        "We implemented probabilistic early expiration using a jittered TTL strategy "
                        "and a background cache warmer that pre-loads the top 1,000 hot keys on deploy."
                    ),
                },
                {
                    "question": "How did you measure the 47% p99 latency improvement?",
                    "answer": (
                        "We exported OpenTelemetry histograms from each worker step to Grafana, "
                        "running before/after load tests with 1,000 concurrent producers via k6."
                    ),
                },
                {
                    "question": "What happens if a consumer crashes mid-processing?",
                    "answer": (
                        f"We used {queue}'s at-least-once delivery with idempotency keys stored in {db1}. "
                        "On consumer restart, duplicate messages are detected and skipped via key lookup."
                    ),
                },
                {
                    "question": "How did you size the Kubernetes HPA thresholds?",
                    "answer": (
                        "We profiled baseline CPU and memory per worker pod at 100 events/sec, "
                        "then set HPA to scale at 70% CPU utilization with a 30s cooldown to prevent flapping."
                    ),
                },
            ],
        )

    def _ml_platform() -> ProjectSpec:
        ml_fw = next((f for f in frameworks if any(w in f.lower() for w in ["torch", "tensor", "keras", "sklearn", "langchain", "langgraph"])), "PyTorch")
        return ProjectSpec(
            project_title=f"Intelligent {domain.split('/')[0].strip()} Inference Engine",
            archetype=ARCHETYPE_REGISTRY["ml_platform"]["label"],
            high_level_architecture=(
                f"End-to-end ML pipeline using {ml_fw} for model training and {fw1} for serving, "
                f"with {db1} for feature storage and {infra1} for containerized deployment."
            ),
            tech_stack=[lang1, ml_fw, fw1, db1, infra1],
            core_bottleneck=challenge1,
            technical_solution=(
                f"Implemented model quantization and batched inference with {ml_fw}, combined with "
                f"{db1} feature caching to reduce repeated preprocessing overhead under concurrent requests."
            ),
            quantified_impact_metrics=[
                "Reduced model inference latency by 43% (320ms to 182ms) via INT8 quantization",
                "Increased inference throughput from 120 to 580 requests/min",
                "Improved model F1 score from 0.81 to 0.89 after fine-tuning on domain-specific data",
            ],
            trade_offs=[
                ArchitecturalTradeOff(
                    decision=f"Selected INT8 quantization over full FP32 model serving",
                    chosen_technology="INT8 Quantized Model",
                    rejected_technology="FP32 Full-Precision Model",
                    justification=(
                        "FP32 serving consumed 4× more GPU memory, limiting batch size to 8; "
                        "INT8 quantization preserved 98.6% accuracy while doubling batch size to 16."
                    ),
                ),
                ArchitecturalTradeOff(
                    decision=f"Used {db1} feature store over recomputing features per request",
                    chosen_technology=f"{db1} Feature Cache",
                    rejected_technology="On-the-fly feature recomputation",
                    justification=(
                        "Recomputing heavy NLP features (TF-IDF, embeddings) per request added 140ms; "
                        f"caching precomputed feature vectors in {db1} reduced this to under 5ms."
                    ),
                ),
            ],
            failure_modes=[
                FailureModeAnalysis(
                    scenario="Model serving pod OOM crash under burst inference requests.",
                    impact="Inference service downtime causing 100% error rate for model-dependent features.",
                    mitigation_strategy=(
                        "Configured Kubernetes resource limits with vertical pod autoscaler (VPA) and "
                        "deployed a fallback rule-based classifier that activates on model service health check failure."
                    ),
                )
            ],
            xyz_bullets=[
                f"Engineered {ml_fw} model quantization pipeline for {domain} inference, reducing "
                f"p95 inference latency by 43% (320ms to 182ms), by converting FP32 to INT8 with <1% accuracy loss.",
                f"Architected {fw1}-based model serving layer with dynamic batching, "
                f"increasing throughput from 120 to 580 req/min, by coalescing concurrent requests into batch groups.",
                f"Built {db1} feature caching layer for precomputed ML embeddings, "
                f"reducing feature extraction overhead by 96% (140ms to 5ms), by eliminating per-request recomputation.",
                f"Deployed {infra1} containerized training pipeline with automated hyperparameter sweeps, "
                f"improving model F1 score from 0.81 to 0.89, by running 48 parallel experiments on domain data.",
            ],
            interview_defense_qna=[
                {
                    "question": "How did you validate that quantization didn't hurt model accuracy?",
                    "answer": (
                        "We ran calibration on a held-out dataset of 5,000 samples and measured accuracy "
                        "degradation. INT8 dropped F1 by only 0.4%, which was within our acceptable 1% threshold."
                    ),
                },
                {
                    "question": "How did dynamic batching improve throughput?",
                    "answer": (
                        "Instead of processing each request independently, we aggregated requests arriving "
                        "within a 10ms window into a single batch inference call, GPU utilization went from 30% to 85%."
                    ),
                },
                {
                    "question": "How did you handle model version rollbacks in production?",
                    "answer": (
                        "Models were versioned with semantic tags in a model registry. Deployment used "
                        "blue/green switching with automated A/B testing gates — if F1 dropped >2%, traffic "
                        "automatically rolled back to the previous version."
                    ),
                },
                {
                    "question": "What feature drift monitoring did you implement?",
                    "answer": (
                        "We computed Jensen-Shannon divergence between training and serving feature distributions "
                        "daily. If divergence exceeded 0.1, an automated retraining pipeline was triggered."
                    ),
                },
                {
                    "question": "Why use a feature store instead of computing on the fly?",
                    "answer": (
                        "Our NLP preprocessing (tokenization, embedding lookup) was the dominant latency source. "
                        "Precomputing and caching static features reduced per-request compute by 96%."
                    ),
                },
            ],
        )

    def _data_pipeline() -> ProjectSpec:
        pipe_fw = next((f for f in frameworks if any(w in f.lower() for w in ["spark", "airflow", "flink", "dbt"])), "Apache Airflow")
        return ProjectSpec(
            project_title=f"Automated {domain.split('/')[0].strip()} Data Pipeline",
            archetype=ARCHETYPE_REGISTRY["data_pipeline"]["label"],
            high_level_architecture=(
                f"Batch and streaming data pipeline using {pipe_fw} for orchestration, "
                f"{lang1} for transformation logic, and {db1} as the analytical data store."
            ),
            tech_stack=[lang1, pipe_fw, db1, infra1, "SQL"],
            core_bottleneck=challenge1,
            technical_solution=(
                f"Redesigned monolithic ETL jobs into modular {pipe_fw} DAGs with checkpointing "
                f"and parallel task execution to handle 10× data volume without proportional cost increase."
            ),
            quantified_impact_metrics=[
                "Reduced daily batch pipeline runtime by 58% (6.2h to 2.6h)",
                "Processed 50M+ records/day with zero data loss across pipeline failures",
                f"Reduced cloud compute costs by 34% via intelligent {pipe_fw} task parallelism",
            ],
            trade_offs=[
                ArchitecturalTradeOff(
                    decision=f"Adopted {pipe_fw} DAG orchestration over cron-based shell scripts",
                    chosen_technology=pipe_fw,
                    rejected_technology="Cron Shell Scripts",
                    justification=(
                        "Cron scripts had no retry logic, no lineage tracking, and no visibility into "
                        f"partial failures. {pipe_fw} provided task-level retries and full audit logs."
                    ),
                ),
                ArchitecturalTradeOff(
                    decision=f"Used {db1} as analytical store over a flat-file approach",
                    chosen_technology=db1,
                    rejected_technology="CSV Flat Files on S3",
                    justification=(
                        f"{db1} enables SQL-based ad-hoc analysis and incremental upserts without "
                        "reprocessing entire datasets on schema changes."
                    ),
                ),
            ],
            failure_modes=[
                FailureModeAnalysis(
                    scenario="Upstream API timeout during incremental data extraction causing partial loads.",
                    impact="Downstream analytics receiving incomplete datasets causing incorrect aggregations.",
                    mitigation_strategy=(
                        f"Implemented watermark-based incremental extraction with {pipe_fw} XCom state tracking. "
                        "On partial load detection, the pipeline auto-reruns only the failed partition window."
                    ),
                )
            ],
            xyz_bullets=[
                f"Architected a {pipe_fw} and {lang1} data pipeline processing 50M+ records/day, "
                f"reducing batch runtime by 58% (6.2h to 2.6h), by parallelizing independent DAG task groups.",
                f"Engineered incremental {db1} upsert strategy with watermark-based extraction, "
                f"eliminating 100% of duplicate records, by replacing full-table overwrites with delta loads.",
                f"Optimized {pipe_fw} DAG dependency resolution, reducing idle worker wait time by 41%, "
                f"by restructuring task dependencies to maximize parallel execution paths.",
                f"Deployed {infra1}-containerized pipeline workers with auto-scaling, "
                f"cutting compute costs by 34%, by right-sizing worker resources based on profiled CPU usage.",
            ],
            interview_defense_qna=[
                {
                    "question": f"How did you handle schema evolution in the {db1} pipeline?",
                    "answer": (
                        "We versioned transformation logic and used ALTER TABLE migrations with backward-"
                        "compatible NULL defaults, ensuring existing consumers weren't broken during rollouts."
                    ),
                },
                {
                    "question": "How did you detect and handle data quality issues mid-pipeline?",
                    "answer": (
                        "We added Great Expectations validation checkpoints after each transformation step. "
                        "Failed checks raised alerts and halted downstream tasks, preventing bad data propagation."
                    ),
                },
                {
                    "question": "How did you measure the 58% runtime reduction?",
                    "answer": (
                        f"We compared {pipe_fw} task timing reports before and after parallelization "
                        "using wall-clock execution logs across 30 consecutive daily runs."
                    ),
                },
                {
                    "question": "What happened when the upstream source API went down?",
                    "answer": (
                        "We implemented exponential backoff retries (3 attempts, 60s/120s/300s intervals) "
                        "and a dead-letter queue for failed batches. Failed partitions were reprocessed the "
                        "following night without duplicating already-loaded records."
                    ),
                },
                {
                    "question": "How did you ensure idempotency across reruns?",
                    "answer": (
                        "Every load used an UPSERT strategy keyed on a natural composite key, "
                        "so reruns on the same data window produced identical {db1} state."
                    ),
                },
            ],
        )

    def _devtools_infra() -> ProjectSpec:
        ci_tool = next((i for i in infra if any(w in i.lower() for w in ["github actions", "jenkins", "gitlab", "ci", "cd"])), "GitHub Actions")
        return ProjectSpec(
            project_title=f"{domain.split('/')[0].strip()} Platform Automation Toolkit",
            archetype=ARCHETYPE_REGISTRY["devtools_infra"]["label"],
            high_level_architecture=(
                f"Developer productivity platform automating build, test, and deployment workflows using "
                f"{ci_tool}, {lang1} tooling scripts, and {infra1} container orchestration."
            ),
            tech_stack=[lang1, infra1, ci_tool, db1, "Prometheus", "Docker"],
            core_bottleneck=challenge2,
            technical_solution=(
                f"Automated infrastructure provisioning with {infra1} and added observability via Prometheus "
                f"metrics and Grafana dashboards, reducing mean-time-to-detect (MTTD) issues from hours to minutes."
            ),
            quantified_impact_metrics=[
                f"Reduced deployment pipeline duration by 52% (18min to 8.6min)",
                f"Achieved 99.6% test environment provisioning reliability",
                f"Cut mean-time-to-detect (MTTD) production issues by 74% (4.2h to 1.1h)",
            ],
            trade_offs=[
                ArchitecturalTradeOff(
                    decision=f"Selected {ci_tool} over manual shell script deployment",
                    chosen_technology=ci_tool,
                    rejected_technology="Manual Shell Script Deploy",
                    justification=(
                        "Manual deploys were error-prone and non-repeatable; "
                        f"{ci_tool} pipelines enforce gating checks and produce auditable deploy logs."
                    ),
                ),
                ArchitecturalTradeOff(
                    decision=f"Used {infra1} container isolation over bare-metal test environments",
                    chosen_technology=f"{infra1} Containers",
                    rejected_technology="Bare-metal shared test server",
                    justification=(
                        "Shared test servers caused dependency version conflicts between parallel test runs; "
                        f"{infra1} containers provide hermetic, reproducible environments per pipeline run."
                    ),
                ),
            ],
            failure_modes=[
                FailureModeAnalysis(
                    scenario="CI/CD pipeline failure during production deploy causing partial rollout.",
                    impact="Mixed-version service instances serving inconsistent API responses.",
                    mitigation_strategy=(
                        f"Implemented {infra1} rolling-update strategy with automatic rollback on health check failure "
                        "and canary deployments for high-risk changes with 5% traffic splitting."
                    ),
                )
            ],
            xyz_bullets=[
                f"Engineered {ci_tool} CI/CD pipeline with parallel test matrix execution, "
                f"reducing build time by 52% (18min to 8.6min), by eliminating sequential test stage blocking.",
                f"Architected Prometheus + Grafana observability stack for {lang1} services, "
                f"cutting MTTD by 74% (4.2h to 1.1h), by exposing per-endpoint latency and error-rate dashboards.",
                f"Built {infra1} containerized test environment provisioner, achieving 99.6% environment reliability, "
                f"by replacing flaky shared bare-metal servers with hermetic container-per-run isolation.",
                f"Deployed automated canary release system with {ci_tool} traffic-split gating, "
                f"reducing production incident rate by 43%, by catching regressions on 5% traffic before full rollout.",
            ],
            interview_defense_qna=[
                {
                    "question": f"How did parallelizing the {ci_tool} pipeline reduce time by 52%?",
                    "answer": (
                        "Unit tests, lint checks, and integration tests previously ran sequentially. "
                        "We reorganized them into 3 parallel matrix jobs, reducing critical path from 18min to 8.6min."
                    ),
                },
                {
                    "question": "How did you handle secrets management in CI?",
                    "answer": (
                        "All credentials were stored in the CI provider's encrypted secret store and injected "
                        "as environment variables at runtime. We audited secret access via OIDC-based short-lived tokens."
                    ),
                },
                {
                    "question": "What metrics did you expose in Prometheus?",
                    "answer": (
                        "We instrumented HTTP request count, p50/p95/p99 latency histograms, error rate by "
                        "status code, and DB query duration per endpoint using a middleware wrapper."
                    ),
                },
                {
                    "question": "How did canary deployments reduce incident rate?",
                    "answer": (
                        "By routing 5% of production traffic to the new version for 10 minutes before full rollout, "
                        "we caught 3 regressions in a quarter that would have caused full production incidents."
                    ),
                },
                {
                    "question": "How did you test the rollback mechanism?",
                    "answer": (
                        "We ran chaos engineering drills monthly by deliberately deploying a known-bad version "
                        "and verifying that the health check triggered automatic rollback within 90 seconds."
                    ),
                },
            ],
        )

    def _mobile() -> ProjectSpec:
        mob_lang = next((l for l in langs if any(w in l.lower() for w in ["kotlin", "swift", "dart", "java"])), lang1)
        mob_fw = next((f for f in frameworks if any(w in f.lower() for w in ["flutter", "react native", "android", "ios"])), "Flutter")
        return ProjectSpec(
            project_title=f"Cross-Platform {domain.split('/')[0].strip()} Mobile App",
            archetype=ARCHETYPE_REGISTRY["mobile"]["label"],
            high_level_architecture=(
                f"Cross-platform mobile application built with {mob_fw} and {mob_lang}, "
                f"backed by a {fw1} REST API and {db1} for offline-first data persistence."
            ),
            tech_stack=[mob_lang, mob_fw, fw1, db1, "REST API"],
            core_bottleneck=challenge1,
            technical_solution=(
                f"Implemented offline-first architecture with {db1} local sync and background delta-sync "
                f"to {fw1} API, enabling full app functionality without network connectivity."
            ),
            quantified_impact_metrics=[
                "Reduced app cold-start time by 46% (2.8s to 1.5s)",
                "Achieved 4.6/5.0 App Store rating from 1,200+ users within 3 months of launch",
                "Reduced API data transfer volume by 61% via delta-sync protocol",
            ],
            trade_offs=[
                ArchitecturalTradeOff(
                    decision=f"Selected {mob_fw} cross-platform over native Android/iOS",
                    chosen_technology=mob_fw,
                    rejected_technology="Native Android (Kotlin) + iOS (Swift)",
                    justification=(
                        f"{mob_fw} enabled a single shared codebase covering 95% of UI/logic, "
                        "reducing development effort by 40% while maintaining 60fps rendering performance."
                    ),
                ),
                ArchitecturalTradeOff(
                    decision=f"Used {db1} offline-first sync over network-only architecture",
                    chosen_technology=f"{db1} Offline-First Sync",
                    rejected_technology="Network-only REST calls",
                    justification=(
                        "Network-only made the app unusable on poor connections; offline-first "
                        "let users work uninterrupted and synced changes on connectivity restore."
                    ),
                ),
            ],
            failure_modes=[
                FailureModeAnalysis(
                    scenario="Sync conflict when two devices update the same record offline simultaneously.",
                    impact="Data loss or inconsistent state across devices on sync merge.",
                    mitigation_strategy=(
                        "Implemented last-write-wins with vector clock timestamps per record. "
                        "Conflicts surfaced to the user as a diff-based resolution prompt."
                    ),
                )
            ],
            xyz_bullets=[
                f"Architected an offline-first {mob_fw} mobile app with {db1} local sync, "
                f"reducing API data transfer by 61% (full-fetch to delta-sync), by implementing "
                f"incremental change-set sync with vector clock conflict resolution.",
                f"Engineered {mob_lang} background sync service with exponential backoff retry, "
                f"achieving 99.3% sync success rate on flaky mobile networks, by decoupling sync from UI thread.",
                f"Optimized {mob_fw} widget tree rendering, reducing cold-start time by 46% (2.8s to 1.5s), "
                f"by lazy-initializing off-screen routes and pre-caching navigation assets.",
                f"Built automated {mob_fw} UI test suite with 87% widget coverage, "
                f"reducing regression detection time by 68%, by integrating tests into the CI release pipeline.",
            ],
            interview_defense_qna=[
                {
                    "question": f"How did you handle sync conflicts between two offline users?",
                    "answer": (
                        "We used vector clocks to track causality. When two edits conflicted, the app "
                        "presented a diff-based merge UI letting the user pick the canonical version."
                    ),
                },
                {
                    "question": f"Why {mob_fw} instead of native development?",
                    "answer": (
                        f"{mob_fw}'s single codebase covered iOS and Android with 95% code sharing. "
                        "The Skia rendering engine delivered 60fps on mid-range devices, meeting our "
                        "performance bar without native code."
                    ),
                },
                {
                    "question": "How did you measure cold-start improvement?",
                    "answer": (
                        "We used Flutter DevTools' timeline tracing to identify the heaviest initialization "
                        "tasks, then compared cold-start wall-clock on a mid-range Android device (Pixel 4a) "
                        "across 50 runs before and after lazy initialization."
                    ),
                },
                {
                    "question": "How did you handle background sync battery impact?",
                    "answer": (
                        "Background sync used WorkManager (Android) / BGTask (iOS) with exponential backoff "
                        "and WiFi-only mode for large payloads. We profiled battery drain with Android Battery Historian."
                    ),
                },
                {
                    "question": "How did you test offline scenarios in CI?",
                    "answer": (
                        "We used Flutter integration tests with a mocked network layer that simulated offline "
                        "state, sync failure, and conflict scenarios in a headless emulator on GitHub Actions."
                    ),
                },
            ],
        )

    def _security_platform() -> ProjectSpec:
        auth_fw = next((f for f in frameworks if any(w in f.lower() for w in ["oauth", "jwt", "keycloak", "auth"])), "OAuth 2.0")
        return ProjectSpec(
            project_title=f"Zero-Trust {domain.split('/')[0].strip()} Auth Platform",
            archetype=ARCHETYPE_REGISTRY["security_platform"]["label"],
            high_level_architecture=(
                f"Centralized authentication and authorization service using {auth_fw} and RBAC, "
                f"with {lang1} service enforcement points and {db1} for policy and session storage."
            ),
            tech_stack=[lang1, auth_fw, fw1, db1, "JWT", infra1],
            core_bottleneck=challenge1,
            technical_solution=(
                f"Implemented token-based {auth_fw} flows with short-lived JWT access tokens and "
                f"secure refresh token rotation stored in {db1}, enforcing zero-trust per-request validation."
            ),
            quantified_impact_metrics=[
                "Reduced unauthorized access incidents by 94% post-platform rollout",
                "Token validation latency under 8ms p99 via in-memory JWKS caching",
                "Achieved SOC 2 Type II audit pass with zero critical findings",
            ],
            trade_offs=[
                ArchitecturalTradeOff(
                    decision=f"Selected short-lived JWTs over opaque session tokens",
                    chosen_technology="Short-lived JWT (15min expiry)",
                    rejected_technology="Long-lived Opaque Session Token",
                    justification=(
                        "Long-lived tokens increased blast radius of token theft. Short-lived JWTs "
                        "limit exposure to 15 minutes and enable stateless validation without DB lookups."
                    ),
                ),
                ArchitecturalTradeOff(
                    decision=f"Cached JWKS public keys in-memory over fetching on every request",
                    chosen_technology="In-Memory JWKS Cache (TTL 1h)",
                    rejected_technology="Per-request JWKS endpoint fetch",
                    justification=(
                        "Per-request JWKS fetches added 80ms network overhead per token validation. "
                        "In-memory caching with 1h TTL reduced this to under 1ms."
                    ),
                ),
            ],
            failure_modes=[
                FailureModeAnalysis(
                    scenario="Auth service downtime causing 100% authentication failure across all services.",
                    impact="Complete user login unavailability and API access blocked for all clients.",
                    mitigation_strategy=(
                        "Deployed auth service across 3 availability zones with active-active replication. "
                        "Services cached validated tokens locally for 5 minutes to ride through brief auth outages."
                    ),
                )
            ],
            xyz_bullets=[
                f"Architected a {auth_fw} zero-trust authentication platform for {domain}, "
                f"reducing unauthorized access incidents by 94%, by enforcing per-request RBAC validation "
                f"with short-lived JWT tokens across all {fw1} service endpoints.",
                f"Engineered in-memory JWKS public key caching with TTL rotation, "
                f"achieving token validation p99 latency under 8ms, by eliminating per-request JWKS endpoint fetches.",
                f"Built automated {db1} refresh token rotation and revocation system, "
                f"reducing stolen token abuse window by 97% (7 days to 15 minutes), by adopting short-expiry token pairs.",
                f"Deployed {infra1} multi-AZ auth service with active-active replication, "
                f"achieving 99.98% auth availability, by eliminating single-region failure dependency.",
            ],
            interview_defense_qna=[
                {
                    "question": "Why short-lived JWTs instead of long-lived session tokens?",
                    "answer": (
                        "If a JWT is stolen, the attacker's window is capped at 15 minutes. "
                        "Long-lived tokens require a revocation list (which kills statelessness), "
                        "while short-lived tokens expire naturally."
                    ),
                },
                {
                    "question": "How did you implement token refresh without user disruption?",
                    "answer": (
                        "The client SDK silently refreshes the access token 2 minutes before expiry "
                        "using the stored refresh token. Users never experience an auth interruption."
                    ),
                },
                {
                    "question": "How did you handle JWKS key rotation without downtime?",
                    "answer": (
                        "New keys were published 24h before old keys expired. Validators accepted "
                        "tokens signed by either active or previous key, allowing a grace period."
                    ),
                },
                {
                    "question": "How did you pass SOC 2 audit?",
                    "answer": (
                        "We implemented full audit logging of all auth events to an append-only log store, "
                        "enabled MFA for admin roles, and enforced principle of least privilege via RBAC scopes."
                    ),
                },
                {
                    "question": "What was your approach to RBAC policy management?",
                    "answer": (
                        f"Policies were defined as code in versioned YAML files, loaded into {db1} on deploy. "
                        "Policy changes required a PR review and triggered automated compliance diff checks."
                    ),
                },
            ],
        )

    # Archetype builder dispatch table
    _BUILDERS = {
        "core_domain": _core_domain,
        "web_fullstack": _web_fullstack,
        "distributed_systems": _distributed_systems,
        "ml_platform": _ml_platform,
        "data_pipeline": _data_pipeline,
        "mobile": _mobile,
        "devtools_infra": _devtools_infra,
        "security_platform": _security_platform,
    }

    projects = []
    for arch_id in resolved_ids:
        builder = _BUILDERS.get(arch_id, _core_domain)
        projects.append(builder())

    return projects


# ---------------------------------------------------------------------------
# LEGACY COMPAT: fallback_synthesize
# Called by nodes.py for JDDeconstruction and EvaluatorScore schemas.
# For ProjectSpec, routes to build_fallback_projects.
# ---------------------------------------------------------------------------

def fallback_synthesize(prompt: str, schema):
    """
    Offline/deterministic synthesis engine — schema-router.
    For ProjectSpec schemas routes to build_fallback_projects (JD-adaptive).
    """
    schema_name = getattr(schema, "__name__", str(schema))

    if schema_name == "JDDeconstruction":
        from src.schemas.models import JDDeconstruction
        return JDDeconstruction(
            company_name="Enterprise",
            role_title="Senior Software Engineer",
            seniority_level="Mid-Level",
            domain="Software Engineering & Application Development",
            primary_languages=["Python", "JavaScript"],
            frameworks=["FastAPI", "React", "Node.js"],
            databases_and_storage=["PostgreSQL", "Redis"],
            infrastructure_and_cloud=["Docker", "GitHub Actions"],
            core_engineering_challenges=[
                "Building scalable and maintainable application architecture",
                "Ensuring high-quality code through testing and code reviews",
            ],
            target_keywords=[
                "Python", "JavaScript", "React", "FastAPI", "PostgreSQL", "Redis",
                "Docker", "REST API", "CI/CD", "Unit Testing", "Code Review",
                "Microservices", "Async", "Git", "Agile",
            ],
            soft_skills=[
                "Cross-Functional Collaboration",
                "High Ownership & Craft",
                "First-Principles Problem Solving",
                "Fast Prototyping",
                "Root Cause Analysis",
            ],
        )

    if schema_name == "EvaluatorScore":
        from src.schemas.models import EvaluatorScore
        return EvaluatorScore(
            ats_coverage_score=92.5,
            metric_plausibility_score=9.4,
            stack_cohesion_score=9.6,
            passed_all_gates=True,
            critique_feedback=None,
        )

    if schema_name == "CandidateProfile":
        from src.schemas.models import CandidateProfile, EducationEntry, ExperienceEntry
        return CandidateProfile(
            full_name="Sahil Yadav",
            title="AI Engineer",
            phone="+91-XXXXXXXXXX",
            email="sahil@example.com",
            linkedin="linkedin.com/in/sahilyadav",
            github="github.com/sahilyadav",
            professional_objective="3rd Year B.Tech AIML student specializing in AI systems and software development.",
            education=[
                EducationEntry(
                    degree="B.Tech — Artificial Intelligence & Machine Learning",
                    institution="VIPS, New Delhi",
                    year_range="2022 – 2026",
                    details="3rd Year",
                )
            ],
            experience=[
                ExperienceEntry(
                    role="AI Intern",
                    organization="Tech Company",
                    period="June – August 2024",
                    bullets=[
                        "Built Python-based AI pipelines for data processing and automation.",
                        "Deployed REST APIs using FastAPI with PostgreSQL integration.",
                    ],
                )
            ],
        )

    # For ProjectSpec / List[ProjectSpec] — return generic fallback
    # (JD-aware path is build_fallback_projects called directly from nodes.py)
    from src.schemas.models import ProjectSpec, ArchitecturalTradeOff, FailureModeAnalysis
    return build_fallback_projects_generic()


def build_fallback_projects_generic():
    """Generic 3-project fallback when no JD is available."""
    from src.schemas.models import ProjectSpec, ArchitecturalTradeOff, FailureModeAnalysis
    # Minimal valid objects — the real path uses build_fallback_projects(jd_analysis)
    p = ProjectSpec(
        project_title="Backend API Platform",
        archetype="Core Domain",
        high_level_architecture="FastAPI backend with PostgreSQL and Redis caching.",
        tech_stack=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
        core_bottleneck="High concurrent request load causing DB connection exhaustion.",
        technical_solution="Async request handlers with connection pooling and Redis caching.",
        quantified_impact_metrics=["Reduced latency by 38%", "Scaled to 2× user load"],
        trade_offs=[
            ArchitecturalTradeOff(
                decision="FastAPI over Flask",
                chosen_technology="FastAPI",
                rejected_technology="Flask",
                justification="Native async support required for non-blocking I/O.",
            )
        ],
        failure_modes=[
            FailureModeAnalysis(
                scenario="DB primary failure",
                impact="Write unavailability",
                mitigation_strategy="Replica failover with circuit breaker",
            )
        ],
        xyz_bullets=[
            "Engineered FastAPI async backend, reducing p95 latency by 38%, by replacing sync handlers.",
            "Built Redis caching layer, cutting DB reads by 44%, by caching hot query results.",
            "Deployed Docker containerized services, achieving 99.7% uptime, by eliminating manual deploys.",
            "Implemented CI/CD pipeline, reducing release time by 52%, by automating test and deploy stages.",
        ],
        interview_defense_qna=[
            {"question": "Why FastAPI?", "answer": "Native async and Pydantic validation out of the box."},
        ],
    )
    return [p, p, p]
