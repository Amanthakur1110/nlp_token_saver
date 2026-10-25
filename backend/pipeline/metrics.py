"""
metrics.py – Stage 4: one small function per metric.

All metrics compare the original (input_text) with the compressed version
(output_text). Any metric whose dependency is missing returns None gracefully.
"""
import re
from utils.tokenizer import count_tokens


# ── Token counts ──────────────────────────────────────────────────────────────

def tokens_before(text: str) -> int:
    return count_tokens(text)


def tokens_after(text: str) -> int:
    return count_tokens(text)


def percent_saved(before: int, after: int) -> float:
    if before == 0:
        return 0.0
    return round((1 - after / before) * 100, 2)


# ── Semantic similarity ───────────────────────────────────────────────────────

def semantic_similarity(original: str, compressed: str):
    """Cosine similarity of sentence embeddings. Returns None if unavailable."""
    try:
        from utils.nlp_models import get_sentence_model
        import numpy as np
        model = get_sentence_model()
        if model is None:
            return None
        emb = model.encode([original, compressed])
        # cosine similarity
        a, b = emb[0], emb[1]
        sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        return round(sim, 4)
    except Exception:
        return None


# ── Entity retention ──────────────────────────────────────────────────────────

def entity_retention(original: str, compressed: str):
    """% of spaCy named entities from original still present in compressed."""
    try:
        from utils.nlp_models import get_spacy_model
        nlp = get_spacy_model()
        if nlp is None:
            return None
        orig_ents = {ent.text.lower() for ent in nlp(original).ents}
        if not orig_ents:
            return 100.0  # nothing to lose
        kept = sum(1 for e in orig_ents if e in compressed.lower())
        return round(kept / len(orig_ents) * 100, 2)
    except Exception:
        return None


# ── Number retention ──────────────────────────────────────────────────────────

def number_retention(original: str, compressed: str) -> float:
    """% of numeric tokens from the original still present in compressed."""
    nums_orig = set(re.findall(r"\b\d[\d,.]*\b", original))
    if not nums_orig:
        return 100.0
    kept = sum(1 for n in nums_orig if n in compressed)
    return round(kept / len(nums_orig) * 100, 2)


# ── ROUGE-L ───────────────────────────────────────────────────────────────────

def rouge_l(original: str, compressed: str) -> float:
    """ROUGE-L F1 score between original and compressed."""
    try:
        from rouge_score import rouge_scorer
        scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
        score = scorer.score(original, compressed)
        return round(score["rougeL"].fmeasure, 4)
    except Exception:
        return 0.0


# ── Aggregator ────────────────────────────────────────────────────────────────

def compute_metrics(original: str, compressed: str, elapsed_ms: float) -> dict:
    """Run all metrics and return a single dict."""
    tb = tokens_before(original)
    ta = tokens_after(compressed)
    return {
        "tokens_before": tb,
        "tokens_after": ta,
        "percent_saved": percent_saved(tb, ta),
        "semantic_similarity": semantic_similarity(original, compressed),
        "entity_retention": entity_retention(original, compressed),
        "number_retention": number_retention(original, compressed),
        "rouge_l": rouge_l(original, compressed),
        "time_ms": elapsed_ms,
    }

