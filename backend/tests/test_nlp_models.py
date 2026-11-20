import os
import sys
import threading
import time
import types
from concurrent.futures import ThreadPoolExecutor

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import utils.nlp_models as nlp_models
from techniques.extractive_summary.technique import ExtractiveSummary
from techniques.grammar_based.technique import GrammarBased
from techniques.llmlingua2.technique import LLMLingua2
from techniques.semantic_dedup.technique import SemanticDedup


@pytest.mark.parametrize(
    ("technique", "possible_helper", "loader"),
    [
        (ExtractiveSummary, "sentence_model_possible", "get_sentence_model"),
        (SemanticDedup, "sentence_model_possible", "get_sentence_model"),
        (GrammarBased, "spacy_model_possible", "get_spacy_model"),
    ],
)
def test_availability_checks_do_not_load_models(
    monkeypatch, technique, possible_helper, loader
):
    monkeypatch.setattr(nlp_models, possible_helper, lambda: True)

    def unexpected_load():
        raise AssertionError(f"{loader} must not run in is_available()")

    monkeypatch.setattr(nlp_models, loader, unexpected_load)

    assert technique().is_available() == (True, "")


def test_llmlingua_availability_does_not_load_model(monkeypatch):
    import techniques.llmlingua2.technique as llmlingua_technique

    monkeypatch.setattr(
        llmlingua_technique.importlib.util,
        "find_spec",
        lambda name: object() if name == "llmlingua" else None,
    )
    monkeypatch.setattr(
        llmlingua_technique,
        "_get_llmlingua",
        lambda: pytest.fail("_get_llmlingua must not run in is_available()"),
    )

    assert LLMLingua2().is_available() == (True, "")


@pytest.mark.parametrize(
    ("model_attribute", "lock_attribute", "module_name", "class_name", "loader"),
    [
        (
            "_sentence_model",
            "_sentence_lock",
            "sentence_transformers",
            "SentenceTransformer",
            nlp_models.get_sentence_model,
        ),
        (
            "_spacy_model",
            "_spacy_lock",
            "spacy",
            "load",
            nlp_models.get_spacy_model,
        ),
    ],
)
def test_model_loaders_load_once_across_concurrent_requests(
    monkeypatch, model_attribute, lock_attribute, module_name, class_name, loader
):
    calls = []
    calls_lock = threading.Lock()

    def load_model(*args, **kwargs):
        time.sleep(0.03)
        with calls_lock:
            calls.append(1)
        return object()

    fake_module = types.ModuleType(module_name)
    setattr(fake_module, class_name, load_model)
    monkeypatch.setitem(sys.modules, module_name, fake_module)
    monkeypatch.setattr(nlp_models, model_attribute, None)
    monkeypatch.setattr(nlp_models, lock_attribute, threading.Lock())

    with ThreadPoolExecutor(max_workers=6) as executor:
        models = list(executor.map(lambda _: loader(), range(6)))

    assert len(calls) == 1
    assert all(model is models[0] for model in models)


def test_sentence_model_load_failure_raises_clear_error(monkeypatch):
    fake_module = types.ModuleType("sentence_transformers")

    def fail_to_load(*args, **kwargs):
        raise OSError("download unavailable")

    fake_module.SentenceTransformer = fail_to_load
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)
    monkeypatch.setattr(nlp_models, "_sentence_model", None)
    monkeypatch.setattr(nlp_models, "_sentence_lock", threading.Lock())

    with pytest.raises(
        nlp_models.ModelLoadError,
        match="Could not load the sentence-transformers",
    ):
        nlp_models.get_sentence_model()


def test_llmlingua_loader_loads_once_across_concurrent_requests(monkeypatch):
    import techniques.llmlingua2.technique as llmlingua_technique

    calls = []
    calls_lock = threading.Lock()

    def load_model(*args, **kwargs):
        time.sleep(0.03)
        with calls_lock:
            calls.append(1)
        return object()

    fake_module = types.ModuleType("llmlingua")
    fake_module.PromptCompressor = load_model
    monkeypatch.setitem(sys.modules, "llmlingua", fake_module)
    monkeypatch.setattr(llmlingua_technique, "_llmlingua", None)
    monkeypatch.setattr(llmlingua_technique, "_llmlingua_lock", threading.Lock())

    with ThreadPoolExecutor(max_workers=6) as executor:
        models = list(
            executor.map(
                lambda _: llmlingua_technique._get_llmlingua(),
                range(6),
            )
        )

    assert len(calls) == 1
    assert all(model is models[0] for model in models)


def test_metrics_do_not_load_sentence_model(monkeypatch):
    from pipeline.metrics import semantic_similarity

    monkeypatch.setattr(nlp_models, "_sentence_model", None)
    monkeypatch.setattr(
        nlp_models,
        "get_sentence_model",
        lambda: pytest.fail("metrics must not load the sentence model"),
    )

    assert semantic_similarity("Original text.", "Compressed text.") is None


def test_compression_api_returns_model_load_errors_as_json(monkeypatch):
    import app as flask_app
    import routes.compress_routes as compress_routes

    doc_id = "model-load-error-test"
    error_message = "Could not load the requested model."
    monkeypatch.setitem(flask_app.doc_store, doc_id, "Original text.")

    def fail_to_run(*args, **kwargs):
        raise nlp_models.ModelLoadError(error_message)

    monkeypatch.setattr(compress_routes, "run_techniques", fail_to_run)
    response = flask_app.app.test_client().post(
        "/api/compress",
        json={"doc_id": doc_id, "techniques": [{"id": "test", "params": {}}]},
    )

    assert response.status_code == 503
    assert response.get_json() == {"error": error_message}
