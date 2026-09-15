"""JD deconstruction prompt templates."""

JD_EXTRACTION_PROMPT = """You are an expert Technical Resume Strategist and ATS Keyword Analyst.
Analyze the following Job Description (JD) and perform a precise deconstruction into structured attributes.

CRITICAL: Identify the ACTUAL domain of this JD (Web Development, Mobile, AI/ML, Data Engineering, Distributed Systems,
Security, DevOps, etc.). DO NOT assume it is a distributed-systems or AI role if it is not.

Deconstruct the JD into:
1. company_name: The hiring company name (or 'company' if not mentioned).
2. role_title: The exact or normalized job title from the JD.
3. seniority_level: Seniority level (e.g., 'Intern', 'Junior', 'Mid-Level', 'Senior', 'Staff / Principal').
4. domain: The specific business domain and technical context of this role.
   Examples:
   - Web/SaaS JD → 'Web Application Development & REST API Engineering'
   - Mobile JD → 'Mobile App Development (Android / iOS)'
   - AI JD → 'Agentic AI / LLM Orchestration'
   - Data JD → 'Data Engineering & Analytics Pipelines'
   Be specific and accurate — do NOT default to 'Distributed Systems' for every JD.
5. primary_languages: Programming languages explicitly mentioned in the JD.
6. frameworks: All frameworks, libraries, and platforms mentioned (frontend, backend, ML, etc.).
7. databases_and_storage: Storage technologies (databases, caches, queues, file storage).
8. infrastructure_and_cloud: Cloud services, containers, CI/CD tools, deployment platforms.
9. core_engineering_challenges: 3-5 specific technical problems or requirements described in the JD.
   These should reflect the ACTUAL domain (e.g., for a web JD: "Building responsive UIs", "Integrating third-party APIs";
   for an ML JD: "Fine-tuning models on domain data", "Reducing inference latency").
10. target_keywords: 20-30 high-priority ATS keywords extracted directly from the JD text.
    Include: technologies, tools, frameworks, methodologies, and concepts explicitly mentioned.

Target Job Description:
{raw_jd}
"""
