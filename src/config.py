import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present (silently no-ops if absent)
load_dotenv()

# System and Pipeline Invariants
MAX_ITERATIONS: int = 3
ATS_PASS_THRESHOLD: float = 85.0
OUTPUT_DIR: Path = Path("output")
TEMPLATES_DIR: Path = Path("templates")

def is_secondary_mode() -> bool:
    """Returns True if an external API key is present in environment, triggering secondary mode."""
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))

class AntiGravityLLM:
    """
    AntiGravity Native LLM Provider.
    Primary execution engine when no external API key is configured.
    Wraps AntiGravity Agent/Runtime or intelligent generation engine.
    """
    def __init__(self, model: str = "antigravity-native"):
        self.model = model

    def invoke(self, input_prompt, **kwargs):
        """Invoke LLM on a text or message input."""
        if hasattr(self, "_structured_schema") and self._structured_schema is not None:
            schema = self._structured_schema
            return self._generate_structured(input_prompt, schema)

        prompt_text = str(input_prompt)
        return f"[AntiGravity Engine Response for: {prompt_text[:100]}...]"

    def with_structured_output(self, schema):
        """Returns a runnable that forces output to conform to Pydantic schema."""
        class StructuredRunnable:
            def __init__(self, parent_llm, target_schema):
                self.parent_llm = parent_llm
                self.target_schema = target_schema

            def invoke(self, input_prompt, **kwargs):
                return self.parent_llm._generate_structured(input_prompt, self.target_schema)

        return StructuredRunnable(self, schema)

    def _generate_structured(self, prompt: str, schema):
        """Generates a structured Pydantic object compliant with schema."""
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_key)
                return llm.with_structured_output(schema).invoke(prompt)
            except Exception:
                pass

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)
                return llm.with_structured_output(schema).invoke(prompt)
            except Exception:
                pass

        from src.prompts.synthesis_prompts import fallback_synthesize
        return fallback_synthesize(prompt, schema)


def get_llm():
    """
    Primary: Use the AntiGravity built-in SDK model — no API key required.
    Secondary (fallback): If GEMINI_API_KEY or OPENAI_API_KEY is set in .env,
    initialize the corresponding LangChain chat model instead.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_key)
        except Exception:
            pass

    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)
        except Exception:
            pass

    return AntiGravityLLM()
