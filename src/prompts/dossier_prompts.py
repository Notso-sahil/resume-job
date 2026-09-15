"""Interview Defense Dossier prompt templates."""

DOSSIER_GENERATION_PROMPT = """You are a Principal Engineering Director preparing an elite candidate for a technical interview defense based on the synthesized resume projects.

Generate an exhaustive, technically rigorous Interview Defense Dossier.

For each of the 3 projects in the portfolio:
1. Deep Dive on Architectural Trade-offs ("Why X over Y?"):
   - Justify the chosen tech stack over popular alternatives.
   - Explain what was traded away (e.g. latency vs consistency, operational simplicity vs scalability).
2. Disaster Recovery & Failure Modes:
   - Detail a realistic production failure scenario (e.g. connection pool saturation, split-brain partition, memory leak).
   - Explain how the system detects the issue and recovers.
3. 5 Probing Technical Interview Questions:
   - Deep questions that a Principal Architect would ask to stress-test authenticity.
   - Scripted, highly articulate model answers that the candidate can study.

Portfolio context:
{portfolio_json}

Target JD Context:
{jd_context}
"""
