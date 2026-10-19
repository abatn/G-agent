---
name: pr-triage-scan
description: Verwende diese Fähigkeit, wenn der Nutzer die offenen Pull Requests sichten, die Review-Warteschlange erstellen oder eine priorisierte PR-Liste will.
---

# PR-Triage-Scan

## Ziel

Eine priorisierte Review-Warteschlange aller offenen Pull Requests, im Format aus `PROJECT_IDENTITY.md`.

## Ablauf

1. Lies `knowledge/connectors.md`, `knowledge/charters.md`, `knowledge/risk_rules.md` und `knowledge/review_checklist.md`.
2. Rufe über den GitHub-Connector alle offenen Pull Requests ab. Notiere die Anzahl. Der Abruf gilt nur als vollständig, wenn alle Seiten geladen wurden.
3. Erfasse pro PR: Nummer, Titel, geänderte Dateien, Diff (ja/nein), Review-Kommentare und Zeitstempel.
4. Fehlt ein Datenpunkt, markiere ihn ausdrücklich. Erfinde ihn nicht.
5. Wende die Schritte aus `skill: classify-pr-risk` auf jeden PR an.
6. Erstelle pro PR die Ein-Satz-Zusammenfassung nach `skill: summarize-diff`.
7. Sortiere nach Priorität: HOCH, dann MITTEL, dann NIEDRIG. Innerhalb einer Priorität ältere PRs zuerst.
8. Gib die Liste im Format aus `PROJECT_IDENTITY.md` aus. Nicht bewertbare PRs stehen im Block `Nicht bewertbar:`.

## Stopp-Bedingungen

- Der Connector meldet einen Authentifizierungs- oder Berechtigungsfehler: Melde den Fehler und frage den Menschen. Nicht über den Browser ausweichen.
- Der Abruf ist unvollständig: Melde, welche Seiten fehlen.

## Quellen

Jede Zeile nennt die PR-Nummer. Jede Priorität nennt die Regelnummer aus `knowledge/risk_rules.md`.
