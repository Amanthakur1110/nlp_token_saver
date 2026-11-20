"""
technique.py – LLMLingua-2

Uses Microsoft's LLMLingua-2 token classification model to compress text.
is_available() returns False gracefully if the library or model cannot be loaded.
"""
import importlib.util
import threading

from techniques.base import BaseTechnique
from utils.nlp_models import ModelLoadError

_llmlingua = None
_llmlingua_lock = threading.Lock()


def _get_llmlingua():
    """Load LLMLingua once on demand and report failures to the caller."""
    global _llmlingua
    if _llmlingua is not None:
        return _llmlingua
    with _llmlingua_lock:
        if _llmlingua is not None:
            return _llmlingua
        try:
            from llmlingua import PromptCompressor
            _llmlingua = PromptCompressor(
                model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
                use_llmlingua2=True,
                device_map="cpu"
                 )
        except Exception as exc:
            raise ModelLoadError(
                print("Failed to load LLMLingua-2 model.")
                "Could not load the LLMLingua-2 model. "
                "Check model download access or the Hugging Face cache, then retry."
            ) from exc
        return _llmlingua


class LLMLingua2(BaseTechnique):
    id = "llmlingua2"
    name = "LLMLingua-2"
    description = (
        "Token-level compression using Microsoft's LLMLingua-2 model. "
        "Learns which tokens to drop from meeting transcripts."
    )
    params_schema = [
        {
            "name": "rate",
            "type": "slider",
            "label": "Target compression rate (lower = shorter output)",
            "default": 0.5,
            "min": 0.1,
            "max": 0.9,
            "step": 0.05,
        }
    ]

    def is_available(self) -> tuple[bool, str]:
        if importlib.util.find_spec("llmlingua") is None:
            return False, "llmlingua package is not installed"
        return True, ""

    def apply(self, text: str, params: dict) -> str:
        compressor = _get_llmlingua()

        rate = float(params.get("rate", 0.5))
        try:
            result = compressor.compress_prompt(text, rate=rate, force_tokens=["\n"])
            return result.get("compressed_prompt", text)
        except Exception as e:
            raise ModelLoadError(f"LLMLingua-2 compression failed: {e}") from e
