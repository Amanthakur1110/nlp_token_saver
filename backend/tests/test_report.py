import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pipeline.report import build_report
from pipeline.diff import build_diff


def test_word_diff_highlights_removed_words_and_preserves_original_text():
    original = "This is a very useful sentence."
    compressed = "This is useful sentence."

    diff = build_diff(original, compressed)

    assert "".join(segment["text"] for segment in diff["segments"]) == original
    assert diff["removed_list"] == ["a very"]
    assert any(
        segment == {"text": "a very", "status": "removed"}
        for segment in diff["segments"]
    )


def test_chain_summary_diff_compares_original_with_final_output():
    original = "Keep this. Remove this first. Remove this second."
    intermediate = "Keep this. Remove this second."
    final = "Keep this."
    results = {
        "individual": [
            {
                "technique_id": "first",
                "technique_name": "First",
                "input_text": original,
                "output_text": intermediate,
                "metrics": {},
                "diff": build_diff(original, intermediate),
            }
        ],
        "chain": [
            {
                "technique_id": "first",
                "technique_name": "First",
                "input_text": original,
                "output_text": intermediate,
                "metrics": {},
                "diff": {
                    "segments": [
                        {"text": "Keep this.", "status": "kept"},
                        {"text": "Remove this first.", "status": "removed"},
                        {"text": "Remove this second.", "status": "kept"},
                    ],
                    "removed_list": ["Remove this first."],
                },
            },
            {
                "technique_id": "second",
                "technique_name": "Second",
                "input_text": intermediate,
                "output_text": final,
                "metrics": {},
                "diff": {
                    "segments": [
                        {"text": "Keep this.", "status": "kept"},
                        {"text": "Remove this second.", "status": "removed"},
                    ],
                    "removed_list": ["Remove this second."],
                },
            },
        ],
        "chain_final_text": final,
    }

    report = build_report("test-doc", original, results, "chain")

    assert report["chain_summary"]["diff"]["removed_list"] == [
        "Remove this first.",
        "Remove this second.",
    ]
    assert "".join(
        segment["text"]
        for segment in report["chain_summary"]["diff"]["segments"]
    ) == original
    assert "".join(
        segment["text"]
        for segment in report["individual"][0]["diff"]["segments"]
    ) == original
