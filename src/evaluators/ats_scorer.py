import re
from typing import List, Dict, Tuple
from src.config import ATS_PASS_THRESHOLD


def normalize_token(text: str) -> str:
    """Normalizes string for keyword matching (lowercase, alphanumeric)."""
    return re.sub(r"[^\w\s\+]", "", text).lower().strip()


def score_ats_coverage(
    target_keywords: List[str], bullets: List[str]
) -> Tuple[float, List[str], List[str]]:
    """
    Algorithmic keyword coverage calculation against generated resume bullets.

    Returns:
      (coverage_percentage, matched_keywords, missing_keywords)
    """
    if not target_keywords:
        return 100.0, [], []

    # Aggregate and normalize all bullet text
    corpus = " ".join(bullets).lower()

    matched = []
    missing = []

    for kw in target_keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue

        # 1. Exact phrase match
        pattern = r"\b" + re.escape(kw_clean.lower()) + r"\b"
        if re.search(pattern, corpus) or kw_clean.lower() in corpus:
            matched.append(kw_clean)
            continue

        # 2. Multi-word phrase matching (all constituent tokens present in corpus)
        words = [w for w in re.split(r"[\s/_-]+", kw_clean.lower()) if len(w) > 1]
        if len(words) > 1 and all(re.search(r"\b" + re.escape(w.rstrip("s|ing|ed")) + r"\w*\b", corpus) for w in words):
            matched.append(kw_clean)
            continue

        # 3. Stemming/plural fallback (e.g. 'caching' <-> 'cache', 'microservices' <-> 'microservice')
        stem = kw_clean.lower().rstrip("s").rstrip("ing").rstrip("ed")
        if len(stem) >= 3 and re.search(r"\b" + re.escape(stem) + r"\w*\b", corpus):
            matched.append(kw_clean)
        else:
            missing.append(kw_clean)

    total = len(matched) + len(missing)
    coverage = (len(matched) / total * 100.0) if total > 0 else 100.0
    return round(coverage, 2), matched, missing


def is_ats_passing(score: float) -> bool:
    """Checks whether the ATS score meets or exceeds the required threshold."""
    return score >= ATS_PASS_THRESHOLD
