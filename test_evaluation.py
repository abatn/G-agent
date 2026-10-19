"""Maßstab für die PR-Triage. Prüft Wissensdateien, Scoring Set und (später) die Lösung."""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
KNOWLEDGE = ROOT / "knowledge"
SCORING_SET = ROOT / "scoring_set.json"
ALLOWED_PRIORITIES = {"HOCH", "MITTEL", "NIEDRIG"}
REQUIRED_CASE_KEYS = {"id", "synthetic", "beschreibung", "critical_paths", "pr", "expected"}


def load_scoring_set():
    return json.loads(SCORING_SET.read_text(encoding="utf-8"))["cases"]


# --- Project Knowledge ---------------------------------------------------------

@pytest.mark.parametrize("name", ["review_checklist.md", "risk_rules.md", "critical_paths.md"])
def test_knowledge_file_exists_and_nonempty(name):
    path = KNOWLEDGE / name
    assert path.is_file(), f"{path} fehlt"
    assert path.read_text(encoding="utf-8").strip(), f"{path} ist leer"


def test_risk_rules_define_every_priority():
    text = (KNOWLEDGE / "risk_rules.md").read_text(encoding="utf-8")
    for priority in ALLOWED_PRIORITIES:
        assert priority in text, f"risk_rules.md definiert {priority} nicht"


def test_critical_paths_entries_have_reason():
    # Jede Eintragszeile: "<pfad> – <satz>". Kommentare und Überschriften werden ignoriert.
    lines = (KNOWLEDGE / "critical_paths.md").read_text(encoding="utf-8").splitlines()
    entries = [
        line for line in lines
        if line.strip()
        and not line.startswith(("#", "<!--", "Format:", "Status:", "Beispielzeile"))
        and not line.strip().startswith("-->")
    ]
    for entry in entries:
        assert re.match(r"^\S+ – \S.*$", entry), f"Eintrag ohne Pfad/Grund: {entry!r}"


# --- Scoring Set ---------------------------------------------------------------

def test_scoring_set_is_wellformed():
    cases = load_scoring_set()
    assert cases, "Scoring Set ist leer"
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids)), "doppelte Fall-IDs"
    for case in cases:
        assert REQUIRED_CASE_KEYS <= case.keys(), f"{case.get('id')}: Schlüssel fehlen"
        assert case["synthetic"] is True, f"{case['id']}: Fälle sind derzeit nur synthetisch"
        expected = case["expected"]
        if expected["not_evaluable"]:
            assert expected["priority"] is None, f"{case['id']}: nicht bewertbar darf keine Priorität haben"
        else:
            assert expected["priority"] in ALLOWED_PRIORITIES, f"{case['id']}: ungültige Priorität"


def test_scoring_set_covers_every_rule():
    # Jede Regel aus risk_rules.md braucht mindestens einen Fall.
    expected = [case["expected"] for case in load_scoring_set()]
    assert any(e["not_evaluable"] for e in expected), "Regel 1 (nicht bewertbar) nicht abgedeckt"
    assert any(e["priority"] == "HOCH" for e in expected), "HOCH nicht abgedeckt"
    assert any(e["priority"] == "NIEDRIG" for e in expected), "NIEDRIG nicht abgedeckt"
    assert any(e["priority"] == "MITTEL" for e in expected), "MITTEL nicht abgedeckt"


# --- Lösung gegen Maßstab ------------------------------------------------------

@pytest.mark.parametrize("case", load_scoring_set(), ids=lambda c: c["id"])
def test_solution_matches_scoring_set(case):
    # Erwartet die Funktion evaluate(pr, critical_paths) -> {"priority": ..., "not_evaluable": ...}.
    # Scheitert bis zur Implementierung absichtlich (ModuleNotFoundError).
    from pr_triage import evaluate

    result = evaluate(case["pr"], case["critical_paths"])
    assert result["not_evaluable"] == case["expected"]["not_evaluable"]
    assert result["priority"] == case["expected"]["priority"]
