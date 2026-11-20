
import time
from techniques.registry import get_technique_by_id
from pipeline.metrics import compute_metrics
from pipeline.diff import build_diff


def _apply_one(technique_obj, text: str, params: dict) -> dict:
    """Apply a single technique and return a result dict."""
    start = time.time()
    output_text = technique_obj.apply(text, params)
    elapsed_ms = round((time.time() - start) * 1000, 1)

    metrics = compute_metrics(text, output_text, elapsed_ms)
    diff = build_diff(text, output_text)

    return {
        "technique_id": technique_obj.id,
        "technique_name": technique_obj.name,
        "input_text": text,
        "output_text": output_text,
        "metrics": metrics,
        "diff": diff,
    }


def run_techniques(cleaned_text: str, techniques: list[dict], mode: str) -> dict:
    """
    techniques: list of {id, params}
    Returns a dict with keys "individual" and/or "chain" depending on mode.
    """
    results = {}

    if mode in ("individual", "both"):
        individual = []
        for spec in techniques:
            t = get_technique_by_id(spec["id"])
            if t is None:
                continue
            available, reason = t.is_available()
            if not available:
                individual.append({
                    "technique_id": spec["id"],
                    "technique_name": spec["id"],
                    "skipped": True,
                    "reason": reason,
                })
                continue
            result = _apply_one(t, cleaned_text, spec.get("params", {}))
            individual.append(result)
        results["individual"] = individual

    if mode in ("chain", "both"):
        chain_steps = []
        current_text = cleaned_text
        chain_techniques = [
            spec for spec in techniques if spec["id"] != "alias_substitution"
        ] + [
            spec for spec in techniques if spec["id"] == "alias_substitution"
        ]
        for spec in chain_techniques:
            t = get_technique_by_id(spec["id"])
            if t is None:
                continue
            available, reason = t.is_available()
            if not available:
                chain_steps.append({
                    "technique_id": spec["id"],
                    "skipped": True,
                    "reason": reason,
                })
                continue
            result = _apply_one(t, current_text, spec.get("params", {}))
            chain_steps.append(result)
            # Feed output into the next technique
            current_text = result["output_text"]
        results["chain"] = chain_steps
        results["chain_final_text"] = current_text

    return results
