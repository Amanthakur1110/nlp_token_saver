"""
report.py – Stage 6: assemble the final JSON response from pipeline outputs.

Keeps the JSON shape stable so the frontend always knows what to expect.
"""
from utils.tokenizer import count_tokens
from pipeline.diff import build_diff


def _format_result(r: dict) -> dict:
    """Turn a runner result dict into a clean API-safe dict."""
    if r.get("skipped"):
        return {
            "technique_id": r["technique_id"],
            "skipped": True,
            "reason": r.get("reason", "Unavailable"),
        }
    return {
        "technique_id": r["technique_id"],
        "technique_name": r["technique_name"],
        "skipped": False,
        "output_text": r["output_text"],
        "metrics": r["metrics"],
        "diff": r["diff"],
    }


def build_report(doc_id: str, cleaned_text: str, results: dict, mode: str) -> dict:
    """
    Assemble the full response dict.
    results comes from runner.run_techniques().
    """
    report = {
        "doc_id": doc_id,
        "original_tokens": count_tokens(cleaned_text),
        "mode": mode,
    }

    if "individual" in results:
        report["individual"] = [_format_result(r) for r in results["individual"]]

    if "chain" in results:
        chain_final = results.get("chain_final_text", cleaned_text)
        report["chain"] = [_format_result(r) for r in results["chain"]]
        report["chain_summary"] = {
            "final_text": chain_final,
            "tokens_after": count_tokens(chain_final),
            "tokens_before": count_tokens(cleaned_text),
            "diff": build_diff(cleaned_text, chain_final),
        }

    return report
