"""Prompt templates for resume engine."""
from src.prompts.extraction_prompts import JD_EXTRACTION_PROMPT
from src.prompts.synthesis_prompts import (
    PROJECT_SYNTHESIS_SYSTEM_PROMPT,
    PROJECT_SYNTHESIS_USER_PROMPT,
    fallback_synthesize,
    synthesize_tailored_summary,
)
from src.prompts.critique_prompts import CRITIQUE_AUDIT_PROMPT
from src.prompts.dossier_prompts import DOSSIER_GENERATION_PROMPT

__all__ = [
    "JD_EXTRACTION_PROMPT",
    "PROJECT_SYNTHESIS_SYSTEM_PROMPT",
    "PROJECT_SYNTHESIS_USER_PROMPT",
    "fallback_synthesize",
    "synthesize_tailored_summary",
    "CRITIQUE_AUDIT_PROMPT",
    "DOSSIER_GENERATION_PROMPT",
]
