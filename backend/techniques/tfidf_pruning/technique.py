"""
technique.py – TF-IDF Pruning

Treats every sentence as a tiny document and scores it by how many rare,
informative words it contains (TF-IDF). The lowest-scoring sentences are
dropped until the keep% target is met. Sentences stay in ORIGINAL order.

Scoring: sum of the sentence's TF-IDF values / sqrt(number of terms).
(A plain mean favours short sentences, a plain sum favours long ones.)

Safety rules: headings are always kept; optionally sentences with numbers
or quotes are always kept (protect_facts).
"""
import math
import re

from techniques.base import BaseTechnique
from utils.sentences import split_sentences, is_heading, is_protected


class TfidfPruning(BaseTechnique):
    id = "tfidf_pruning"
    name = "TF-IDF Pruning"
    description = (
        "Ranks sentences by TF-IDF importance and drops the lowest-scoring ones. "
        "Headings are kept. Sentences with numbers or quotes can be protected."
    )
    params_schema = [
        {
            "name": "keep_pct",
            "type": "slider",
            "label": "Keep % of sentences",
            "default": 60,
            "min": 10,
            "max": 100,
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

    def apply(self, text: str, params: dict) -> str:
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer

        keep_pct = float(params.get("keep_pct", 60)) / 100.0
        protect = params.get("protect_facts", "yes") == "yes"

        # 1. Break the text into units: (line number, sentence, is_heading)
        lines = text.split("\n")
        units = []
        for n, line in enumerate(lines):
            if not line.strip():
                continue
            if is_heading(line):
                units.append((n, line.strip(), True))
            else:
                units.extend((n, s, False) for s in split_sentences(line))

        # indexes (into units) of the sentences that can be scored
        body = [i for i, u in enumerate(units) if not u[2]]
        if len(body) <= 2:
            return text  # too short to prune

        # 2. TF-IDF over body sentences. norm=None stops short sentences
        #    from getting an unfair score boost.
        vectorizer = TfidfVectorizer(stop_words="english", norm=None, sublinear_tf=True)
        try:
            matrix = vectorizer.fit_transform([units[i][1] for i in body]).tocsr()
        except ValueError:
            return text  # nothing to score (e.g. only stopwords)

        # 3. Score = sum of TF-IDF values / sqrt(number of terms)
        sums = np.asarray(matrix.sum(axis=1)).ravel()
        n_terms = np.diff(matrix.indptr)  # non-zero terms per row
        scores = np.where(n_terms > 0, sums / np.sqrt(np.maximum(n_terms, 1)), 0.0)

        # 4. Protected sentences (numbers / quotes) are always kept
        protected = set()
        if protect:
            protected = {j for j, i in enumerate(body) if is_protected(units[i][1])}

        # 5. The top-k quota is filled from the remaining sentences
        n_keep = max(1, math.ceil(len(body) * keep_pct))
        quota = max(0, n_keep - len(protected))
        others = [j for j in np.argsort(-scores) if j not in protected]
        best = protected | set(others[:quota])
        keep = {body[j] for j in best}

        # 6. Rebuild the text in original order, keeping the line structure
        kept_by_line = {}
        for i, (n, sentence, heading) in enumerate(units):
            if heading or i in keep:
                kept_by_line.setdefault(n, []).append(sentence)

        out = []
        for n, line in enumerate(lines):
            if not line.strip():
                out.append("")                         # paragraph break
            elif n in kept_by_line:
                out.append(" ".join(kept_by_line[n]))  # lines with nothing kept vanish
        return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()