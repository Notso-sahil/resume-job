"""Critique and audit prompt templates for evaluator-optimizer loop."""

CRITIQUE_AUDIT_PROMPT = """You are a Principal Distributed Systems Architect and ATS Integrity Evaluator.
Audit the following synthesized resume project portfolio against strict engineering plausibility, mathematical consistency, and hardware constraints.

### AUDIT CHECKLIST:
1. Hardware Bounds:
   - Throughput (RPS): Are single-node database claims realistic? (SQLite <= 500 RPS; single PostgreSQL <= 5,000 RPS; Redis <= 50,000 RPS).
   - Latency: Are network boundary claims physically possible? (No sub-1ms p99 across remote multi-tenant network databases).
   - Percentages: Compute/cost reductions must be between 20% and 60%.
2. Google XYZ Structure:
   - Does every bullet follow: "Accomplished [X], as measured by [Y], by implementing [Z]"?
   - Does every bullet begin with an active engineering power verb?
   - Are technical keywords front-loaded in the first 7 words?
3. Stack Cohesion & Contradictions:
   - Are there contradictory architectural choices (e.g., claiming to use SQLite and Redis for the same concurrent high-throughput hot path)?
4. ATS Keyword Density:
   - Target keywords from JD: {target_keywords}

Project Portfolio to Audit:
{portfolio_json}

Evaluate and return:
- ats_coverage_score: float (0.0 to 100.0)
- metric_plausibility_score: float (0.0 to 10.0)
- stack_cohesion_score: float (0.0 to 10.0)
- passed_all_gates: bool (True if ats_coverage >= 85.0 AND plausibility >= 8.0 AND cohesion >= 8.0)
- critique_feedback: string or null (actionable architectural critique if failed)
"""
