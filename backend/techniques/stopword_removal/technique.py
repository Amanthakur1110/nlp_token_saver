
import re
from techniques.base import BaseTechnique

# Words that look like stopwords but change meaning – always keep them
ALWAYS_PROTECT = {
    "not", "no", "nor", "never", "neither", "without",
    "hardly", "barely", "scarcely", "n't",
}


def _load_stopwords() -> set:
    try:
        from nltk.corpus import stopwords
        return set(stopwords.words("english"))
    except Exception:
        # Minimal fallback if NLTK data is missing
        return {
            "a", "an", "the", "is", "in", "it", "of", "and", "or",
            "to", "that", "this", "was", "for", "on", "are", "with",
        }


class StopwordRemoval(BaseTechnique):
    id = "stopword_removal"
    name = "Stopword Removal"
    description = (
        "Removes common English stopwords using NLTK's list. "
        "Negations and numbers are always protected."
    )
    params_schema = [
        {
            "name": "protected_words",
            "type": "text",
            "label": "Extra words to protect (comma-separated)",
            "default": "",
        }
    ]

    def apply(self, text: str, params: dict) -> str:
        stopwords = _load_stopwords()

        # Parse user-supplied protected words
        extra_protected = set()
        raw = params.get("protected_words", "")
        if raw:
            extra_protected = {w.strip().lower() for w in raw.split(",") if w.strip()}

        protected = ALWAYS_PROTECT | extra_protected

        # Remove stopwords from stopword list that the user wants to protect
        effective_stops = stopwords - protected

        words = text.split(" ")
        result = []
        for word in words:
            # Strip punctuation for comparison but keep original form
            clean = re.sub(r"[^\w']", "", word).lower()
            if clean in effective_stops and clean not in protected:
                # Skip the stopword but keep the spacing logic intact
                continue
            result.append(word)

        return " ".join(result).strip()

