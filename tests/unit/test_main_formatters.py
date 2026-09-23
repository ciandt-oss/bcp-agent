from src.main import format_results_json, format_results_text


def test_format_results_json_structure():
    results = {
        "story_name": "Story",
        "total_bcp": 45,
        "breakdown": {"business_rules": 8, "interface_elements": 11, "nfr": 3},
        "maturity": {"complexity": 3, "invest": 4},
        "cells": {
            "functional_business_rules": {"score": 8, "raw_output": {"summary": "2 rules"}},
            "complexity_maturity": {"score": 3, "raw_output": {"classification": "Meets Basic Standards"}},
        },
    }
    out = format_results_json(results)
    assert '"total_bcp": 45' in out
    assert '"breakdown"' in out
    assert '"maturity"' in out
    assert '"cells"' in out


def test_format_results_text_contains_sections():
    results = {
        "story_name": "Test Story",
        "total_bcp": 42,
        "breakdown": {"business_rules": 8, "nfr": 3},
        "maturity": {"complexity": 3, "invest": 4},
        "cells": {
            "functional_business_rules": {"score": 8, "raw_output": {}},
        },
    }
    out = format_results_text(results)
    assert "=== TOTAL BCP ===" in out
    assert "Total: 42" in out
    assert "=== DIMENSION BREAKDOWN ===" in out
    assert "=== MATURITY ===" in out
