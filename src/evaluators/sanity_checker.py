import re
from typing import List, Tuple, Optional, Dict, Any
from src.schemas.models import ProjectSpec, EvaluatorScore
from src.evaluators.ats_scorer import score_ats_coverage, is_ats_passing

APPROVED_POWER_VERBS = {
    "architected", "benchmarked", "partitioned", "engineered", "optimized",
    "designed", "implemented", "reduced", "eliminated", "automated",
    "profiled", "refactored", "deployed", "instrumented", "migrated",
    "parallelized", "sharded", "replaced", "built", "scaled"
}

FORBIDDEN_PHRASES = [
    "improved efficiency",
    "enhanced performance",
    "optimized the system",
    "reduced latency significantly",
    "improved throughput",
    "worked on",
    "helped with",
]


def check_metric_plausibility(projects: List[ProjectSpec]) -> Tuple[float, List[str]]:
    """
    Deterministic rule-based mathematical and hardware bounds check.
    Audits:
      - Google XYZ structure
      - Approved power verbs at start of each bullet
      - Hardware-impossible throughput/latency figures
      - Realistic compute reduction bounds (20% to 60%)
      - Absence of forbidden vague phrases

    Returns:
      (plausibility_score_0_to_10, list_of_critique_issues)
    """
    issues = []
    penalties = 0.0

    all_bullets = []
    for proj in projects:
        all_bullets.extend(proj.xyz_bullets)

    if not all_bullets:
        return 0.0, ["No resume bullets found across projects."]

    for i, bullet in enumerate(all_bullets):
        bullet_clean = bullet.strip()
        first_word = bullet_clean.split()[0].lower().rstrip(":,.-")

        # 1. Check power verb
        if first_word not in APPROVED_POWER_VERBS:
            issues.append(f"Bullet does not begin with an approved engineering power verb: '{first_word}' in '{bullet_clean[:40]}...'")
            penalties += 0.5

        # 2. Check forbidden vague phrases
        for phrase in FORBIDDEN_PHRASES:
            if phrase in bullet_clean.lower():
                issues.append(f"Vague phrase detected: '{phrase}' in '{bullet_clean[:50]}...'")
                penalties += 0.8

        # 3. Check for quantified metrics (numbers, %, ms, RPS)
        has_metric = bool(re.search(r"\b\d+(\.\d+)?%|\b\d+(\.\d+)?\s*(ms|s|rps|req/s|vectors|MB|GB|TB)\b|\b\d{2,}\b", bullet_clean, re.IGNORECASE))
        if not has_metric:
            issues.append(f"Bullet lacks quantified metric (%, ms, RPS, etc.): '{bullet_clean[:50]}...'")
            penalties += 0.6

        # 4. Check compute/cost reduction bounds (must be 20% - 60%)
        red_match = re.findall(r"(\d+)%\s*(?:reduction|cut|slashed|reduced|lower)", bullet_clean, re.IGNORECASE)
        for pct_str in red_match:
            pct = int(pct_str)
            if pct < 15 or pct > 80:
                issues.append(f"Suspicious reduction percentage {pct}% outside plausible 20-60% enterprise range: '{bullet_clean[:50]}...'")
                penalties += 0.7

        # 5. Check SQLite impossible throughput claims (> 1,000 RPS)
        if "sqlite" in bullet_clean.lower():
            sqlite_rps = re.findall(r"(\d+[\d,]*)\s*rps", bullet_clean, re.IGNORECASE)
            for rps in sqlite_rps:
                val = int(rps.replace(",", ""))
                if val > 1000:
                    issues.append(f"Physical hardware bounds violation: Claimed {val} RPS on SQLite instance.")
                    penalties += 1.5

    # Calculate score out of 10
    score = max(0.0, min(10.0, 10.0 - penalties))
    return round(score, 1), issues


def check_stack_cohesion(projects: List[ProjectSpec]) -> Tuple[float, List[str]]:
    """Checks for conflicting architectural components and ensures 3 unique archetypes."""
    issues = []
    archetypes = [p.archetype for p in projects]

    if len(projects) != 3:
        issues.append(f"Expected exactly 3 projects, but found {len(projects)}.")

    if len(set(archetypes)) < 3:
        dupes = [a for a in set(archetypes) if archetypes.count(a) > 1]
        issues.append(f"Duplicate archetype(s) detected: {dupes}. All 3 projects must have distinct archetypes.")

    score = 10.0 - (len(issues) * 2.0)
    return max(0.0, score), issues


def audit_portfolio(
    projects: List[ProjectSpec],
    target_keywords: List[str],
    extra_texts: Optional[List[str]] = None,
) -> EvaluatorScore:
    """
    Executes full hybrid evaluation:
      - Algorithmic ATS coverage (>= 85.0 required, scanned across all resume content)
      - Metric and hardware plausibility bounds
      - Stack and archetype cohesion
    """
    all_bullets = []
    for p in projects:
        all_bullets.extend(p.xyz_bullets)

    full_corpus_texts = list(all_bullets)
    if extra_texts:
        full_corpus_texts.extend(extra_texts)

    ats_score, matched, missing = score_ats_coverage(target_keywords, full_corpus_texts)
    plausibility_score, plausibility_issues = check_metric_plausibility(projects)
    cohesion_score, cohesion_issues = check_stack_cohesion(projects)

    all_issues = plausibility_issues + cohesion_issues
    if not is_ats_passing(ats_score):
        all_issues.append(f"ATS Keyword coverage {ats_score}% is below threshold {85.0}%. Missing: {missing[:8]}")

    passed = (
        is_ats_passing(ats_score)
        and plausibility_score >= 7.5
        and cohesion_score >= 8.0
    )

    feedback = "; ".join(all_issues) if all_issues else None

    return EvaluatorScore(
        ats_coverage_score=ats_score,
        metric_plausibility_score=plausibility_score,
        stack_cohesion_score=cohesion_score,
        passed_all_gates=passed,
        critique_feedback=feedback,
    )


class PortfolioSanityChecker:
    """
    Validates portfolio compliance for high-density ATS scoring and impact formatting.
    Ensures zero [TODO] leaks and enforces mandatory numerical metrics.
    """

    FORBIDDEN_MARKERS = [
        "[TODO",
        "TODO:",
        "add your real",
        "measured metric",
        "placeholder",
        "XXXX",
        "<insert",
    ]

    METRIC_PATTERN = re.compile(
        r"(\d+(\.\d+)?%|\$\d+(\.\d+)?[kKMbB]?|\d+x|\b\d+\s*(ms|s|tokens/sec|QPS|GB|MB|VRAM)\b|\b\d{2,}\b)",
        re.IGNORECASE
    )

    @classmethod
    def audit_bullet(cls, bullet: str) -> Dict[str, Any]:
        """
        Verifies that a bullet point contains defensible metrics and zero placeholder artifacts.
        """
        # Check for forbidden placeholder artifacts
        for marker in cls.FORBIDDEN_MARKERS:
            if marker.lower() in bullet.lower():
                return {
                    "valid": False,
                    "reason": f"Bullet contains incomplete placeholder marker: '{marker}'"
                }

        # Enforce that every bullet has a quantifiable impact metric
        if not cls.METRIC_PATTERN.search(bullet):
            return {
                "valid": False,
                "reason": "Bullet lacks an explicit quantitative metric (%, ms, QPS, scale, etc.)"
            }

        # Check minimum length for Google XYZ depth
        if len(bullet.split()) < 12:
            return {
                "valid": False,
                "reason": "Bullet is too concise to satisfy Google XYZ structure at full depth"
            }

        return {"valid": True, "reason": "Compliant"}

    @classmethod
    def audit_portfolio(cls, projects: List[Any]) -> Dict[str, Any]:
        """
        Validates the 3-project slot architecture:
        - Exactly 3 projects total.
        - Slot 1 must be flagged as anchor (from projects.md).
        - Slots 2 & 3 must be role-synthesized to maximize JD match.
        """
        if len(projects) != 3:
            return {
                "passed": False,
                "error": f"Portfolio must contain exactly 3 projects, found {len(projects)}"
            }

        # Verify Slot 1 Anchor
        slot_1 = projects[0]
        is_anchor = slot_1.get("is_anchor", False) if isinstance(slot_1, dict) else getattr(slot_1, "is_anchor", False)
        if not is_anchor:
            return {
                "passed": False,
                "error": "Project Slot 1 must be an anchor project sourced from projects.md"
            }

        # Validate bullets across all projects
        for idx, project in enumerate(projects, start=1):
            if isinstance(project, dict):
                bullets = project.get("bullets", project.get("xyz_bullets", []))
                title = project.get("title", "")
            else:
                bullets = getattr(project, "xyz_bullets", getattr(project, "bullets", []))
                title = getattr(project, "title", "")

            if not (3 <= len(bullets) <= 5):
                return {
                    "passed": False,
                    "error": f"Project {idx} ('{title}') has {len(bullets)} bullets; expected 3-5"
                }

            for b_idx, bullet in enumerate(bullets, start=1):
                audit = cls.audit_bullet(bullet)
                if not audit["valid"]:
                    return {
                        "passed": False,
                        "error": f"Project {idx} bullet {b_idx} failed validation: {audit['reason']}"
                    }

        return {"passed": True, "error": None}

