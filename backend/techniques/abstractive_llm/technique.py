"""
technique.py – Abstractive LLM Compression (optional)

Rewrites the text concisely using the Anthropic Claude API.
Requires ANTHROPIC_API_KEY environment variable.
Note: this technique itself consumes tokens from your API quota.
"""
from techniques.base import BaseTechnique
from config import Config


class AbstractiveLLM(BaseTechnique):
    id = "abstractive_llm"
    name = "Abstractive LLM (Claude)"
    description = (
        "Rewrites the text concisely using Anthropic's Claude API. "
        "⚠ This technique itself spends API tokens. Requires ANTHROPIC_API_KEY."
    )
    params_schema = [
        {
            "name": "target_ratio",
            "type": "slider",
            "label": "Target length ratio (0.3 = 30% of original length)",
            "default": 0.4,
            "min": 0.1,
            "max": 0.8,
            "step": 0.05,
        }
    ]

    def is_available(self) -> tuple[bool, str]:
        if not Config.ANTHROPIC_API_KEY:
            return False, "ANTHROPIC_API_KEY environment variable is not set."
        try:
            import anthropic  # noqa: F401
            return True, ""
        except ImportError:
            return False, "anthropic package not installed."

    def apply(self, text: str, params: dict) -> str:
        import anthropic

        ratio = float(params.get("target_ratio", 0.4))
        target_words = max(20, int(len(text.split()) * ratio))

        client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

        prompt = (
            f"Compress the following text to about {target_words} words while "
            f"preserving all key information, facts, and named entities. "
            f"Return ONLY the compressed text, no explanations.\n\n{text}"
        )

        try:
            message = client.messages.create(
                model="claude-3-haiku-20240307",  # cheapest/fastest Claude model
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"[abstractive_llm] API call failed: {e}")
            return text

