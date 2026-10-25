"""
technique.py – LLMLingua-2

Uses Microsoft's LLMLingua-2 token classification model to compress text.
is_available() returns False gracefully if the library or model cannot be loaded.
"""
from techniques.base import BaseTechnique

_llmlingua = None
_llmlingua_loaded = False


def _get_llmlingua():
    """Lazy-load LLMLingua once; return None on failure."""
    global _llmlingua, _llmlingua_loaded
    if _llmlingua_loaded:
        return _llmlingua
    _llmlingua_loaded = True
    try:
        from llmlingua import PromptCompressor
        # Use the smaller multilingual BERT variant for reasonable CPU performance
        _llmlingua = PromptCompressor(
            model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
            use_llmlingua2=True,
            device_map="cpu",
        )
    except Exception as e:
        print(f"[llmlingua2] Model load failed: {e}")
        _llmlingua = None
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
        compressor = _get_llmlingua()
        if compressor is not None:
            return True, ""
        return False, "LLMLingua-2 model could not be loaded (check HuggingFace cache)."

    def apply(self, text: str, params: dict) -> str:
        compressor = _get_llmlingua()
        if compressor is None:
            return text  # fail-safe

        rate = float(params.get("rate", 0.5))
        try:
            result = compressor.compress_prompt(text, rate=rate, force_tokens=["\n"])
            return result.get("compressed_prompt", text)
        except Exception as e:
            print(f"[llmlingua2] Compression failed: {e}")
            return text

