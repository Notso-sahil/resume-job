import sys
from src.evaluators import sanity_checker

# Register submodule alias in sys.modules for backward-compatible imports
sys.modules[__name__ + ".sanity_checker"] = sanity_checker

from src.evaluators.sanity_checker import (
    PortfolioSanityChecker,
    check_metric_plausibility,
    check_stack_cohesion,
    audit_portfolio,
)

__all__ = [
    "PortfolioSanityChecker",
    "check_metric_plausibility",
    "check_stack_cohesion",
    "audit_portfolio",
]
