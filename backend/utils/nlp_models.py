"""
nlp_models.py – lazy singletons for heavy NLP models.

Models are loaded once on first use (not at import time) so the server
starts fast and only pays the load cost when a technique actually needs them.
If a model fails to load, the getter returns None and callers return null metrics.
"""

_spacy_model = None
_spacy_loaded = False

_sentence_model = None
_sentence_loaded = False


def get_spacy_model():
    """Return the spaCy en_core_web_sm model, or None if unavailable."""
    global _spacy_model, _spacy_loaded
    if _spacy_loaded:
        return _spacy_model
    _spacy_loaded = True
    try:
        import spacy
        _spacy_model = spacy.load("en_core_web_sm")
    except Exception:
        _spacy_model = None
    return _spacy_model


def get_sentence_model():
    """Return the sentence-transformers MiniLM model, or None if unavailable."""
    global _sentence_model, _sentence_loaded
    if _sentence_loaded:
        return _sentence_model
    _sentence_loaded = True
    try:
        from sentence_transformers import SentenceTransformer
        # multilingual MiniLM – small and fast on CPU
        _sentence_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    except Exception:
        _sentence_model = None
    return _sentence_model

