# Project knowledge

Dieses Projekt gibt Freebuff Kontext: Ziel, Befehle, Regeln und Stolperfallen.

Rolle dieser Datei: operativ (Setup, Befehle, Prüfkette, Regeln, Gotchas) und Zeiger auf die Quellen. Keine Detail-Specs hier. Details stehen in `knowledge/` und `skills/*/SKILL.md`. Diese Datei ist die Doku-Authority für Setup und Prüfkette. Bei Widerspruch zu anderen Dateien gilt, was hier steht, bis die Abweichung korrigiert ist.

## Ziel

Generischer Agent-Baukasten aus Shared Engine, Skills und Knowledge. Er lässt sich auf jedes Ziel anwenden. Das konkrete Ziel beschreibt `PROJECT_IDENTITY.md`. Die Beispiele in diesem Repo (PR-Triage) zeigen eine Anwendung, sind aber kein fester Bestandteil des Baukastens.

## Projektstruktur

| Pfad | Zweck |
|---|---|
| `AGENTS.md` | Diese Datei: Setup, Befehle, Prüfkette, Regeln, Gotchas (Doku-Authority) |
| `README.md`, `LICENSE` | Projektbeschreibung und Lizenz |
| `PROJECT_IDENTITY.md` | Rolle, Output-Format und Guardrails des Agenten |
| `knowledge/*.md` | Wissen: Regeln, Checklisten, Pfade, Konnektoren, Übernahmen |
| `knowledge/migration-notes.md` | Protokoll, was aus Vorgänger-Projekten übernommen oder verworfen wurde |
| `skills/*/SKILL.md` | Fähigkeiten mit YAML-Frontmatter (`name`, `description`) |
| `scoring_set.json` | Testfälle, die Regeln gegen erwartete Ergebnisse prüfen |
| `test_evaluation.py` | Tests gegen Wissen, Scoring Set und Lösung |
| `scripts/verify_all.py` | Pflicht-Gate: führt die gesamte Prüfkette aus |
| `scripts/*.py` | Ausführbare Skripte (Beispiele: `pr_triage_morning.py`, `weekly_review.py`) |
| `pr_triage.py` | Lösungsbeispiel: Regelkette zur Einstufung |
| `.github/workflows/` | Optional: Zeitpläne und CI (Beispiele: `pr-triage-morning.yml`, `weekly-review.yml`, `verify.yml`) |
| `.pre-commit-config.yaml` | Optional: Git-Hook für das Gate |

## Setup

- Kein Venv eingerichtet. Befehle laufen mit `python3` (3.12 in CI).
- Abhängigkeiten: `pytest` für Tests, `pyyaml` für das Gate. Die Skripte brauchen sonst keine externen Pakete.
- **Optional, nur bei GitHub-Nutzung:** `GITHUB_TOKEN` und `GITHUB_REPOSITORY` als Umgebungsvariablen. In GitHub Actions setzt Actions das `GITHUB_TOKEN` selbst. Ohne GitHub-Nutzung sind beide nicht nötig.

## Befehle

- Prüfkette (alles): `python3 scripts/verify_all.py`
- Tests: `python3 -m pytest test_evaluation.py`
- Syntax: `python3 -m compileall -q .`
- Beispiel, optional mit GitHub-Variablen: `python3 scripts/pr_triage_morning.py`
- Beispiel: `python3 scripts/weekly_review.py`

## Lab-Prinzipien (verbindlich)

1. **Quelle oder Kennzeichnung:** Jede Zahl und jede Regel hat eine Quelle oder wird als „Design-Entscheidung“ gekennzeichnet.
2. **MD zuerst:** Logik gehört in `knowledge/` und `skills/`. Python nur, wo Markdown nicht reicht (API-Abruf, Auswertung).
3. **Konsistenz:** Weicht Code von `knowledge/risk_rules.md` ab, wird zuerst das Markdown geprüft. Korrigiert wird das Markdown, nicht der Test.
4. **Transparenz:** Entscheidungen werden in `knowledge/migration-notes.md` oder einer Datei unter `knowledge/` festgehalten.
5. **Iteration:** Ein Skill nach dem anderen.

## Regeln (verbindlich)

- Keine Erfindungen. Keine Testfixtures als Projektwissen eintragen.
- Keine Behauptung ohne Beweis.
- Ein Fakt steht an genau einem Ort.
- Kein Code, wo Markdown reicht.
- Keine Tokens oder Geheimnisse in Dateien oder Commits.

## Prüfkette (Pflicht vor jedem Commit)

Das Gate `python3 scripts/verify_all.py` führt alle Punkte aus. Jeder Punkt muss `rc=0` liefern:

| # | Prüfung | Inhalt |
|---|---|---|
| 1 | Syntax & Import | `compileall` über das ganze Projekt, Skripte importierbar |
| 2 | Tests | `pytest test_evaluation.py`, alle grün |
| 3 | Konsistenz Wissen ↔ Code | Regeln in `knowledge/risk_rules.md` kommen im Code vor und stimmen; `critical_paths.md` im Format `<pfad> – <Begründung>`; Markdown-Dateien gültig |
| 4 | Skills | Jede `skills/*/SKILL.md` hat gültiges YAML-Frontmatter; jede in `PROJECT_IDENTITY.md` genannte Fähigkeit existiert |
| 5 | Scoring Set | `scoring_set.json` ist gültiges JSON; jede Regel hat mindestens einen Testfall |
| 6 | Dokumentation | `README.md` und `LICENSE` existieren und sind nicht leer |

Ein roter oder fehlender Punkt heißt: kein Commit und kein Push. Das Gate endet dann mit rc=1.

Hinweis: Die Punkte 3 und 5 prüfen die Regeln aus `knowledge/risk_rules.md` gegen `pr_triage.py` (Beispiel-Lösung). Ist der Baukasten auf ein anderes Ziel angewendet, müssen diese beiden Prüfungen an die neue Lösung angepasst werden. Sonst meldet das Gate zu Recht rot.

## Gotchas

Beispiel-Gotchas aus dem PR-Triage-Fall. Sie gelten nur, wenn der jeweilige Teil genutzt wird.

- **`knowledge/critical_paths.md` leer = Abbruch (Beispiel).** Der Morgenlauf endet mit Exit 2, weil HOCH nicht prüfbar ist. Die Beispielzeile im HTML-Kommentar wird ignoriert.
- **Exit 3 (Beispiel):** fehlendes Token, fehlende Umgebungsvariable oder API-Fehler. Der Lauf bricht ab und schreibt einen Log-Eintrag.
- **Workflows pushen direkt (Beispiel).** Bei geschützten Branches braucht der Bot Schreibrechte.
- **Zusammenfassungen fehlen (Beispiel).** Ist der Summarizer nicht gebaut, zeigt die Warteschlange „nicht erzeugt“.
- **Tests nicht anpassen, um Grün zu erreichen.** Ist ein Test rot, wird zuerst die Wissensdatei geprüft.

## Zeiger

| Gebiet | Quelle |
|---|---|
| Doku-Authority (Setup, Prüfkette) | `AGENTS.md` (diese Datei) |
| Rolle und Output-Format | `PROJECT_IDENTITY.md` |
| Regeln und wissensbasierte Entscheidungen | `knowledge/*.md` |
| Übernahme aus Vorgänger-Projekten | `knowledge/migration-notes.md` |
| Fähigkeiten | `skills/*/SKILL.md` |
