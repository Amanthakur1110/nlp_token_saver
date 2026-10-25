"""
technique.py – Grammar-Based Compression

Uses spaCy POS tags and dependency labels to remove words by strictness level.
Rules are expressed as a readable table, not buried logic.
"""
import re
from techniques.base import BaseTechnique

# ── Rule table ────────────────────────────────────────────────────────────────
# What gets removed at each strictness level.
# ALWAYS KEPT regardless of level: negations, numbers, named entities, quoted words.

RULES = {
    1: {
        "description": "Remove fillers and fluff words",
        # Remove tokens whose LOWER form is in this set
        "filler_words": {
            "very", "basically", "actually", "really", "just", "quite",
            "rather", "somewhat", "fairly", "pretty", "simply", "literally",
            "honestly", "frankly", "clearly", "obviously", "certainly",
            "definitely", "absolutely", "totally", "completely", "entirely",
        },
        # Remove by POS tag
        "remove_pos": set(),
    },
    2: {
        "description": "Also remove articles, auxiliaries, most adverbs",
        "filler_words": set(),  # inherit level-1 fillers too
        "remove_pos": {"DET", "AUX", "ADV"},
        # But do NOT remove ADV tokens that are negations (handled in _is_protected)
    },
    3: {
        "description": "Keep only NOUN, PROPN, VERB, NUM, negations",
        "filler_words": set(),
        # Remove everything that is NOT in this keep set
        "keep_pos": {"NOUN", "PROPN", "VERB", "NUM"},
    },
}

# Negation words always protected at every level
NEGATIONS = {"not", "no", "never", "neither", "nor", "n't", "without", "hardly", "barely"}


def _is_protected(token) -> bool:
    """Return True if this token must be kept no matter what."""
    low = token.lower_
    # Negations
    if low in NEGATIONS or token.dep_ == "neg":
        return True
    # Numbers
    if token.like_num or token.pos_ == "NUM":
        return True
    # Named entities
    if token.ent_type_:
        return True
    # Inside quotes (spaCy marks these)
    if token.is_quote:
        return True
    return False


def _should_remove(token, level: int) -> bool:
    """Return True if the token should be dropped at this level."""
    if _is_protected(token):
        return False

    if level == 1:
        return token.lower_ in RULES[1]["filler_words"]

    if level == 2:
        if token.lower_ in RULES[1]["filler_words"]:
            return True
        # Remove by POS but never remove negation adverbs
        if token.pos_ in RULES[2]["remove_pos"]:
            return True
        return False

    if level == 3:
        # Keep only the allow-listed POS tags
        return token.pos_ not in RULES[3]["keep_pos"]

    return False


class GrammarBased(BaseTechnique):
    id = "grammar_based"
    name = "Grammar-Based Compression"
    description = (
        "Uses spaCy POS tags to remove words by strictness level. "
        "Level 1: fillers. Level 2: also articles/adverbs. Level 3: nouns+verbs only."
    )
    params_schema = [
        {
            "name": "strictness",
            "type": "select",
            "label": "Strictness level",
            "default": 1,
            "options": [
                {"value": 1, "label": "1 – Remove fillers"},
                {"value": 2, "label": "2 – Also articles & adverbs"},
                {"value": 3, "label": "3 – Nouns & verbs only"},
            ],
        }
    ]

    def is_available(self) -> tuple[bool, str]:
        try:
            from utils.nlp_models import get_spacy_model
            m = get_spacy_model()
            return (True, "") if m is not None else (False, "spaCy model not loaded")
        except Exception as e:
            return False, str(e)

    def apply(self, text: str, params: dict) -> str:
        from utils.nlp_models import get_spacy_model
        nlp = get_spacy_model()
        if nlp is None:
            return text  # fail safe: return unchanged

        level = int(params.get("strictness", 1))
        doc = nlp(text)

        kept_tokens = []
        for token in doc:
            if token.is_space:
                kept_tokens.append(token.text)
            elif not _should_remove(token, level):
                kept_tokens.append(token.text_with_ws)

        result = "".join(kept_tokens)
        # Clean up double spaces introduced by removed words
        return re.sub(r"  +", " ", result).strip()

