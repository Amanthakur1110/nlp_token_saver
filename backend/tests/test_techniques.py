"""
test_techniques.py – one tiny test per technique with a sample sentence.
Run inside Docker: docker compose exec backend python -m pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest


SAMPLE = (
    "In order to effectively utilize the available resources, "
    "it is important to note that the team must at this point in time "
    "conduct an investigation into the matter. "
    "The results were very clearly quite significant. "
    "The results were very clearly quite significant."  # duplicate
)


# ── 1. Whitespace Cleanup ─────────────────────────────────────────────────────
def test_whitespace_cleanup_collapses_blanks():
    from techniques.whitespace_cleanup.technique import WhitespaceCleanup
    t = WhitespaceCleanup()
    text = "Hello\n\n\n\n\nWorld"
    result = t.apply(text, {})
    assert "\n\n\n" not in result


# ── 2. Deduplication ──────────────────────────────────────────────────────────
def test_deduplication_removes_exact_dup():
    from techniques.deduplication.technique import Deduplication
    t = Deduplication()
    text = "The cat sat on the mat. The cat sat on the mat."
    result = t.apply(text, {"threshold": 0.9})
    assert result.count("cat") == 1


# ── 3. Phrase Substitution ────────────────────────────────────────────────────
def test_phrase_substitution_replaces():
    from techniques.phrase_substitution.technique import PhraseSubstitution
    t = PhraseSubstitution()
    result = t.apply("In order to succeed, you must try.", {})
    assert "in order to" not in result.lower()
    assert "to succeed" in result.lower()


def test_phrase_substitution_full_sample():
    from techniques.phrase_substitution.technique import PhraseSubstitution
    t = PhraseSubstitution()
    result = t.apply(SAMPLE, {})
    assert len(result) < len(SAMPLE), "Should be shorter after substitutions"


# ── 4. Grammar-based ──────────────────────────────────────────────────────────
def test_grammar_based_level1_removes_fillers():
    from techniques.grammar_based.technique import GrammarBased
    t = GrammarBased()
    avail, _ = t.is_available()
    if not avail:
        pytest.skip("spaCy model not loaded")
    result = t.apply("The results were very clearly quite significant.", {"strictness": 1})
    assert "very" not in result.lower()
    assert "quite" not in result.lower()


# ── 5. Stopword Removal ───────────────────────────────────────────────────────
def test_stopword_removal_keeps_negations():
    from techniques.stopword_removal.technique import StopwordRemoval
    t = StopwordRemoval()
    result = t.apply("This is not a good idea.", {"protected_words": ""})
    assert "not" in result.lower()


def test_stopword_removal_removes_common():
    from techniques.stopword_removal.technique import StopwordRemoval
    t = StopwordRemoval()
    result = t.apply("The cat sat on the mat.", {"protected_words": ""})
    assert "the" not in [w.lower() for w in result.split()]


# ── 6. TF-IDF Pruning ─────────────────────────────────────────────────────────
def test_tfidf_pruning_reduces_length():
    from techniques.tfidf_pruning.technique import TfidfPruning
    t = TfidfPruning()
    text = "Machine learning is a field of artificial intelligence. It learns from data. Apples are red fruit."
    result = t.apply(text, {"keep_pct": 50})
    assert len(result) <= len(text)


# ── 7. Extractive Summary ─────────────────────────────────────────────────────
def test_extractive_summary(monkeypatch):
    import numpy as np
    from techniques.extractive_summary.technique import ExtractiveSummary

    class FakeModel:
        def encode(self, sentences, normalize_embeddings=False):
            return np.tile(np.array([[1.0, 0.0]]), (len(sentences), 1))

    monkeypatch.setattr("utils.nlp_models.get_sentence_model", lambda: FakeModel())
    t = ExtractiveSummary()
    text = "Artificial intelligence transforms technology. Machine learning powers it. The blue sky is high."
    result = t.apply(text, {"keep_pct": 50})
    assert len(result) <= len(text)


# ── 8. Semantic Dedup ─────────────────────────────────────────────────────────
def test_semantic_dedup(monkeypatch):
    import numpy as np
    from techniques.semantic_dedup.technique import SemanticDedup

    class FakeModel:
        def encode(self, sentences):
            return np.tile(np.array([[1.0, 0.0]]), (len(sentences), 1))

    monkeypatch.setattr("utils.nlp_models.get_sentence_model", lambda: FakeModel())
    t = SemanticDedup()
    text = "The quick brown fox jumps over the dog. A fast brown fox leaps over a dog. The sky is dark tonight."
    result = t.apply(text, {"threshold": 0.80})
    assert len(result) <= len(text)


# ── 9. LLMLingua-2 ────────────────────────────────────────────────────────────
def test_llmlingua2_availability():
    from techniques.llmlingua2.technique import LLMLingua2
    t = LLMLingua2()
    avail, reason = t.is_available()
    # It must never crash, returns bool and reason
    assert isinstance(avail, bool)
    assert isinstance(reason, str)


# ── 10. Abstractive LLM ───────────────────────────────────────────────────────
def test_abstractive_llm_availability_without_key():
    from techniques.abstractive_llm.technique import AbstractiveLLM
    t = AbstractiveLLM()
    avail, reason = t.is_available()
    # Without API key, is_available must return False gracefully
    if not os.getenv("ANTHROPIC_API_KEY"):
        assert avail is False
        assert "ANTHROPIC_API_KEY" in reason


# ── 11. Alias Substitution ────────────────────────────────────────────────────
def test_alias_substitution_is_lossless():
    from techniques.alias_substitution.technique import AliasSubstitution, expand_aliases

    text = " ".join(["alexander@example.com"] * 10)
    result = AliasSubstitution().apply(text, {"min_occurrences": 2, "max_aliases": 1})

    assert result.startswith("[Legend: ")
    assert expand_aliases(result) == text


def test_alias_substitution_leaves_unprofitable_text_unchanged():
    from techniques.alias_substitution.technique import AliasSubstitution

    text = "A repeated phrase appears twice: exceptionally-long-phrase exceptionally-long-phrase"
    result = AliasSubstitution().apply(text, {"min_occurrences": 2, "max_aliases": 1})

    assert result == text


def test_expand_aliases_does_not_confuse_numbered_aliases():
    from techniques.alias_substitution.technique import expand_aliases

    text = "[Legend: §1 = first phrase | §10 = tenth phrase]\n\n§1 then §10"

    assert expand_aliases(text) == "first phrase then tenth phrase"


def test_alias_substitution_runs_last_in_chain(monkeypatch):
    from pipeline import runner

    class FakeTechnique:
        def __init__(self, technique_id):
            self.id = technique_id

        def is_available(self):
            return True, ""

    techniques = {
        "alias_substitution": FakeTechnique("alias_substitution"),
        "stopword_removal": FakeTechnique("stopword_removal"),
    }
    applied = []

    monkeypatch.setattr(runner, "get_technique_by_id", techniques.get)

    def apply_one(technique, text, params):
        applied.append(technique.id)
        return {"output_text": text, "technique_id": technique.id}

    monkeypatch.setattr(runner, "_apply_one", apply_one)
    result = runner.run_techniques(
        "input",
        [{"id": "alias_substitution"}, {"id": "stopword_removal"}],
        "chain",
    )

    assert applied == ["stopword_removal", "alias_substitution"]
    assert [step["technique_id"] for step in result["chain"]] == applied
