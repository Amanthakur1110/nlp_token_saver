"""
technique.py – Phrase Substitution

Replaces verbose phrases with shorter equivalents.
The phrase list is a plain dict so it is easy to read and extend.
"""
import re
from techniques.base import BaseTechnique

# ── Phrase table ──────────────────────────────────────────────────────────────
# Keep this readable: wordy phrase -> short replacement
# Ordered longest-first to avoid partial replacements.
PHRASE_MAP = {
    "due to the fact that":            "because",
    "in spite of the fact that":       "although",
    "in the event that":               "if",
    "for the purpose of":              "to",
    "with the exception of":           "except",
    "in order to":                     "to",
    "in order for":                    "for",
    "on the occasion of":              "when",
    "at this point in time":           "now",
    "at the present time":             "now",
    "in the near future":              "soon",
    "in the process of":               "while",
    "it is important to note that":    "",
    "it should be noted that":         "",
    "it is worth noting that":         "",
    "needless to say":                 "",
    "as a matter of fact":             "in fact",
    "in light of the fact that":       "because",
    "prior to":                        "before",
    "subsequent to":                   "after",
    "a large number of":               "many",
    "a majority of":                   "most",
    "a small number of":               "few",
    "in the majority of cases":        "usually",
    "in close proximity to":           "near",
    "is able to":                      "can",
    "are able to":                     "can",
    "was able to":                     "could",
    "were able to":                    "could",
    "make use of":                     "use",
    "utilize":                         "use",
    "utilise":                         "use",
    "commence":                        "start",
    "terminate":                       "end",
    "approximately":                   "about",
    "at the current time":             "now",
    "conduct an investigation":        "investigate",
    "provide assistance to":           "help",
    "give consideration to":           "consider",
    "take into consideration":         "consider",
    "be in a position to":             "be able to",
    "on a regular basis":              "regularly",
    "in a timely manner":              "promptly",
    "in an effort to":                 "to",
}

# Sort longest phrase first to avoid replacing a substring of a longer match
_SORTED_PHRASES = sorted(PHRASE_MAP.keys(), key=len, reverse=True)


class PhraseSubstitution(BaseTechnique):
    id = "phrase_substitution"
    name = "Phrase Substitution"
    description = (
        "Replaces wordy multi-word phrases with shorter equivalents "
        "(e.g. 'in order to' → 'to'). Meaning-preserving."
    )
    params_schema = []  # no user-tunable params; phrase list is in the code

    def apply(self, text: str, params: dict) -> str:
        for phrase in _SORTED_PHRASES:
            replacement = PHRASE_MAP[phrase]
            # Case-insensitive replacement, preserve leading/trailing space
            pattern = re.compile(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", re.IGNORECASE)
            text = pattern.sub(replacement, text)

        # Clean up any double spaces left by empty replacements
        text = re.sub(r"  +", " ", text)
        # Clean up sentences that now start with a space
        text = re.sub(r"\n ", "\n", text)
        return text.strip()

