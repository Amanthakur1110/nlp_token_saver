"""
nlp_models.py – lazy, thread-safe singletons for heavy NLP models.

Availability checks only inspect installed packages. Models are loaded on
first use and load failures are raised so the API can report them to the UI.
"""
import importlib.util
import threading

_spacy_model = None
_spacy_lock = threading.Lock()

_sentence_model = None
_sentence_lock = threading.Lock()


class ModelLoadError(RuntimeError):
    """Raised when a requested NLP model cannot be loaded or used."""


def sentence_model_possible() -> bool:
    """Return whether sentence-transformers is installed, without loading it."""
    return importlib.util.find_spec("sentence_transformers") is not None


def spacy_model_possible() -> bool:
    """Return whether spaCy and its English model package are installed."""
    return (
        importlib.util.find_spec("spacy") is not None
        and importlib.util.find_spec("en_core_web_sm") is not None
    )


def get_spacy_model():
    """Load and return the spaCy model once, raising a clear error on failure."""
    global _spacy_model
    if _spacy_model is not None:
        return _spacy_model
    with _spacy_lock:
        if _spacy_model is not None:
            return _spacy_model
        try:
            import spacy
            _spacy_model = spacy.load("en_core_web_sm")
        except Exception as exc:
            raise ModelLoadError(
                "Could not load spaCy's en_core_web_sm model. "
                "Install the spaCy English model and try again."
            ) from exc
        return _spacy_model


def get_sentence_model():
    """Load and return the sentence model once, raising a clear error on failure."""
    global _sentence_model
    if _sentence_model is not None:
        return _sentence_model
    with _sentence_lock:
        if _sentence_model is not None:
            return _sentence_model
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
        except Exception as exc:
            raise ModelLoadError(
                "Could not load the sentence-transformers MiniLM model. "
                "Check model download access or the Hugging Face cache, then retry."
            ) from exc
        return _sentence_model


def get_loaded_sentence_model():
    """Return the already-loaded sentence model without starting a model load."""
    return _sentence_model


def get_loaded_spacy_model():
    """Return the already-loaded spaCy model without starting a model load."""
    return _spacy_model
