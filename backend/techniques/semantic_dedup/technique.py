"""
technique.py – Semantic Deduplication

Encodes each sentence with sentence-transformers, then drops any sentence
whose cosine similarity to an already-kept sentence exceeds the threshold.
"""
import re
from techniques.base import BaseTechnique


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


class SemanticDedup(BaseTechnique):
    id = "semantic_dedup"
    name = "Semantic Deduplication"
    description = (
        "Removes semantically similar sentences using embedding cosine similarity. "
        "Lower threshold = more aggressive dedup."
    )
    params_schema = [
        {
            "name": "threshold",
            "type": "slider",
            "label": "Similarity threshold (higher = only remove near-identical)",
            "default": 0.85,
            "min": 0.5,
            "max": 1.0,
            "step": 0.05,
        }
    ]

    def is_available(self) -> tuple[bool, str]:
        from utils.nlp_models import sentence_model_possible
        if not sentence_model_possible():
            return False, "sentence-transformers package is not installed"
        return True, ""

    def apply(self, text: str, params: dict) -> str:
        import numpy as np
        from utils.nlp_models import get_sentence_model

        threshold = float(params.get("threshold", 0.85))
        sentences = _split_sentences(text)

        if len(sentences) <= 1:
            return text

        model = get_sentence_model()

        embeddings = model.encode(sentences)

        def cosine(a, b):
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

        kept_indices = []
        kept_embeddings = []

        for i, emb in enumerate(embeddings):
            # Check similarity against every already-kept sentence
            too_similar = any(
                cosine(emb, kept_emb) >= threshold
                for kept_emb in kept_embeddings
            )
            if not too_similar:
                kept_indices.append(i)
                kept_embeddings.append(emb)

        return " ".join(sentences[i] for i in kept_indices)
