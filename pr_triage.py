"""Risikoklassifikation nach knowledge/risk_rules.md (Ansatz A: Regelkette)."""

DOC_SUFFIXES = (".md", ".rst", ".txt")


def evaluate(pr, critical_paths):
    files = pr.get("files_changed") or []
    if not pr.get("diff_available") or not files:
        return {"priority": None, "not_evaluable": True, "rule": 1}
    if any(f in critical_paths for f in files):
        return {"priority": "HOCH", "not_evaluable": False, "rule": 2}
    if pr.get("tests_removed") and not pr.get("tests_removal_reason_in_diff"):
        return {"priority": "HOCH", "not_evaluable": False, "rule": 3}
    if all(f.endswith(DOC_SUFFIXES) for f in files):
        return {"priority": "NIEDRIG", "not_evaluable": False, "rule": 4}
    return {"priority": "MITTEL", "not_evaluable": False, "rule": 5}
