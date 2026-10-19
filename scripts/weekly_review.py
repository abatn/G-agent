"""Wochen-Review (Freitag). Liest runs/log.jsonl der letzten 7 Tage.

Output: reviews/weekly-JJJJ-MM-TT.md
Analysiert: Abbrüche je Code, nicht bewertbare PRs, Auslösungen je Regel,
Regeln ohne Auslösung. Die Datei enthält nur Vorschläge. knowledge/ und skills/
werden nicht verändert; die Entscheidung trifft der Mensch.
"""

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULE_NUMBERS = ["1", "2", "3", "4", "5"]
HINTS = {
    2: "critical_paths.md befüllen; ohne Einträge ist HOCH nicht prüfbar.",
    3: "GitHub-Token und Berechtigungen (pull-requests: read) prüfen.",
}


def load_week(today):
    path = ROOT / "runs" / "log.jsonl"
    if not path.exists():
        return []
    cutoff = (today - dt.timedelta(days=7)).isoformat()
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [e for e in entries if e.get("date", "") >= cutoff]


def analyze(entries):
    ok = [e for e in entries if e.get("status") == "ok"]
    aborts = [e for e in entries if e.get("status") == "abbruch"]
    rule_counts = {r: 0 for r in RULE_NUMBERS}
    not_eval = []
    for e in ok:
        for rule, n in e.get("rules", {}).items():
            rule_counts[rule] = rule_counts.get(rule, 0) + n
        not_eval += [f"{e['date']} #{n}" for n in e.get("not_evaluable", [])]
    return ok, aborts, rule_counts, not_eval


def suggestions(ok, aborts, rule_counts, not_eval):
    out = []
    for e in aborts:
        code = e.get("code")
        out.append(f"- Abbruch {e['date']} (Code {code}): {str(e.get('message', '')).rstrip('.')}. {HINTS.get(code, 'Ursache prüfen.')}")
    if ok:
        for rule, n in rule_counts.items():
            if n == 0:
                out.append(
                    f"- Regel {rule} hat diese Woche nie ausgelöst. Kandidat zum Prüfen, Ersetzen oder Löschen "
                    f"in knowledge/risk_rules.md."
                )
    if not_eval:
        out.append(f"- Nicht bewertbare PRs: {', '.join(not_eval)}. Diff-Abruf und Dateiliste prüfen.")
    if not out:
        out.append("- Keine Auffälligkeiten.")
    out.append(
        "- Hinweis: tests_removal_reason_in_diff wird nicht ausgewertet (immer False). "
        "Entfernte Tests lösen daher HOCH aus, auch mit Begründung."
    )
    return out


def main():
    today = dt.datetime.now(dt.timezone.utc).date()
    entries = load_week(today)
    lines = [f"# Wochen-Review {today.isoformat()}", ""]
    if not entries:
        lines.append("Keine Laufdaten der letzten 7 Tage.")
    else:
        ok, aborts, rule_counts, not_eval = analyze(entries)
        lines.append(f"Läufe erfolgreich: {len(ok)}, Abbrüche: {len(aborts)}")
        lines.append("Auslösungen je Regel: " + ", ".join(f"Regel {r}: {n}" for r, n in rule_counts.items()))
        lines += ["", "## Vorschläge"] + suggestions(ok, aborts, rule_counts, not_eval)
    out = ROOT / "reviews"
    out.mkdir(exist_ok=True)
    (out / f"weekly-{today.isoformat()}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
