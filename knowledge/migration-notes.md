# Migrationsnotizen: AGENTS.md (altes Projekt) → PR-Triage-Agent

Stand: 19.10.2026. Quelle: `AGENTS.md` aus `km-hr-agent`. Dieses Projekt enthält nur die Teile, die hier tatsächlich existieren.

## Übernommen

| Regel aus AGENTS.md | Ziel in diesem Projekt | Begründung |
|---|---|---|
| „Keine Erfindungen“ | `review_checklist.md` | Gilt für die Triage direkt (PROJECT_IDENTITY: „Erfinde niemals Daten“). |
| „Keine Behauptung ohne Beweis“ | `review_checklist.md` | Jede Aussage über einen PR muss auf gelesene Daten zurückführbar sein. |
| „Ein Fakt steht an genau einem Ort“ | `review_checklist.md` | Verhindert doppelte Regeln zwischen `risk_rules.md` und Checkliste. |
| „Konsistenz: bei Abweichung MD korrigieren, nicht den Code“ | Nur als Prinzip; Umsetzung durch Tests in `test_evaluation.py` | `risk_rules.md` ist maßgeblich. Weicht `pr_triage.py` ab, wird zuerst geprüft, ob die Regel korrekt ist. |
| Testbefehl `python3 -m pytest` | Prüfkette (siehe unten) | Einziger Test-Befehl, der hier existiert. |

## Bewusst weggelassen

| Inhalt aus AGENTS.md | Grund |
|---|---|
| Streamlit, NiceGUI, `webui/`, `start-webui.sh`, `app.py`, `.env*`-Dateien | Existieren in diesem Projekt nicht. |
| `scripts/agent-runner.py`, `connectors/`, `ergebnisse/` | Existieren nicht. |
| `.venv-streamlit`, `staledocs`, `docrot-cli`, pyflakes-Ausnahmeliste, bandit, gitleaks | Keine dieser Tools sind eingerichtet. |
| E2E/Playwright, i18n-Kataloge, `.bak`-Retention, Deploy auf Contabo VPS | Gehören nicht zur PR-Triage. |
| Live-DB `data/feedback.db`, Seed-Passwort-Restrisiko | Hier gibt es keine Datenbank. |
| Changelog-Pflicht über `ergebnisse/entscheidungen.md` | Datei existiert nicht. Diese Notizen ersetzen sie für die Migration. |
| Zitat-Regel „Datei:Zeile ist kein stabiler Verweis“ | Derzeit gibt es keine Zitate aus Code in Berichten. Bei Bedarf nachziehen. |

## Kritische Pfade

Keine Übernahme aus dem alten Projekt. Die Einträge in `critical_paths.md` stammen aus den Dateien dieses Projekts, nicht aus AGENTS.md. Die alten Pfade (`webui/db.py`, `webui/logic.py`, `scripts/agent-runner.py`) existieren hier nicht.

## Skills

Keine neue `SKILL.md` angelegt.
- „Test-Ausführung“ ist ein einzelner Befehl, kein wiederkehrender Ablauf mit Entscheidungen. Er steht in dieser Notiz.
- „Doku-Prüfung“ (staledocs/docrot) kommt in diesem Projekt nicht vor.

## Prüfkette für dieses Projekt

1. `python3 -m pytest test_evaluation.py` (Tests)
2. `python3 -m py_compile pr_triage.py scripts/*.py` (Syntax)

Beide Befehle laufen ohne Venv, weil das Projekt keine eigene Umgebung hat.
