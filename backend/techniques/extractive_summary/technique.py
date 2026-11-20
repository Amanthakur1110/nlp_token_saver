"""
technique.py – Extractive Summary

Scores sentences by cosine similarity to the document centroid embedding
(mean of all sentence embeddings) and keeps the top-k% in ORIGINAL order.

Two safety rules:
- Headings are always kept.
- Optionally, sentences with numbers or quotes are always kept (protect_facts),
  because the centroid method tends to drop specific facts and keep generic text.

Needs sentence-transformers. If the model is missing, is_available() reports it
and the UI greys the technique out.
"""
import math
import re

from techniques.base import BaseTechnique
from utils.sentences import split_sentences

_QUOTES = ('"', "“", "”")


def _is_heading(line: str) -> bool:
    """Short line with no sentence-ending punctuation = heading."""
    line = line.strip()
    return len(line.split()) <= 8 and not line.endswith((".", "!", "?", '"'))


def _is_protected(sentence: str) -> bool:
    """Sentences with numbers or quotes carry facts, so they are never dropped."""
    has_number = any(c.isdigit() for c in sentence)
    has_quote = any(q in sentence for q in _QUOTES)
    return has_number or has_quote


class ExtractiveSummary(BaseTechnique):
    id = "extractive_summary"
    name = "Extractive Summary"
    description = (
        "Scores sentences by semantic relevance to the document centroid "
        "and keeps the top-k% in their original order. Headings are kept. "
        "Sentences with numbers or quotes can be protected."
    )
    params_schema = [
        {
            "name": "keep_pct",
            "type": "slider",
            "label": "Keep % of sentences",
            "default": 50,
            "min": 10,
            "max": 90,
            "step": 5,
        },
        {
            "name": "protect_facts",
            "type": "select",
            "label": "Always keep sentences with numbers or quotes",
            "default": "yes",
            "options": ["yes", "no"],
        },
    ]

    def is_available(self) -> tuple[bool, str]:
        from utils.nlp_models import sentence_model_possible
        if not sentence_model_possible():
            return False, "sentence-transformers package is not installed"
        return True, ""

    def apply(self, text: str, params: dict) -> str:
        import numpy as np
        from utils.nlp_models import get_sentence_model

        keep_pct = float(params.get("keep_pct", 50)) / 100.0
        protect = params.get("protect_facts", "yes") == "yes"

        # 1. Break the text into units: (line number, sentence, is_heading)
        lines = text.split("\n")
        units = []
        for n, line in enumerate(lines):
            if not line.strip():
                continue
            if _is_heading(line):
                units.append((n, line.strip(), True))
            else:
                units.extend((n, s, False) for s in split_sentences(line))

        # indexes (into units) of the sentences that can be scored
        body = [i for i, u in enumerate(units) if not u[2]]
        if len(body) <= 2:
            return text

        model = get_sentence_model()

        # 2. Embed body sentences; cosine = dot product after normalising
        emb = model.encode([units[i][1] for i in body], normalize_embeddings=True)
        centroid = emb.mean(axis=0)
        centroid /= np.linalg.norm(centroid) + 1e-9
        scores = emb @ centroid

        # 3. Protected sentences (numbers / quotes) are always kept
        protected = set()
        if protect:
            protected = {j for j, i in enumerate(body) if _is_protected(units[i][1])}

        # 4. The top-k quota is filled from the remaining sentences
        n_keep = max(1, math.ceil(len(body) * keep_pct))
        quota = max(0, n_keep - len(protected))
        others = [j for j in np.argsort(-scores) if j not in protected]
        best = protected | set(others[:quota])
        keep = {body[j] for j in best}

        # 5. Rebuild the text in original order, keeping the line structure
        kept_by_line = {}
        for i, (n, sentence, is_heading) in enumerate(units):
            if is_heading or i in keep:
                kept_by_line.setdefault(n, []).append(sentence)

        out = []
        for n, line in enumerate(lines):
            if not line.strip():
                out.append("")                         # paragraph break
            elif n in kept_by_line:
                out.append(" ".join(kept_by_line[n]))  # lines with nothing kept vanish
        return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()