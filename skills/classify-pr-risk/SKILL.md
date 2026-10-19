---
name: classify-pr-risk
description: Verwende diese Fähigkeit, wenn die Risikopriorität eines Pull Requests bestimmt werden soll (HOCH, MITTEL, NIEDRIG oder nicht bewertbar).
---

# PR-Risiko einstufen

## Ziel

Eine Priorität pro PR, abgeleitet aus den Regeln in `knowledge/risk_rules.md`.

## Ablauf

1. Lies `knowledge/risk_rules.md` und `knowledge/critical_paths.md`.
2. Prüfe die Regeln in der angegebenen Reihenfolge. Die erste zutreffende Regel bestimmt die Priorität.
   - Regel 1: Diff oder Dateiliste fehlt, dann nicht bewertbar.
   - Regel 2: Eine geänderte Datei liegt in einem Pfad aus `critical_paths.md`, dann HOCH.
   - Regel 3: Tests wurden entfernt oder deaktiviert, ohne Grund im Diff, dann HOCH.
   - Regel 4: Nur Dokumentation oder reine Formatierung, dann NIEDRIG.
   - Regel 5: Alles andere, auch unklare Fälle, dann MITTEL.
3. Notiere die Regelnummer, die gegriffen hat.
4. Formuliere den Grund in einem Satz, der den Auslöser nennt.

## Stopp-Bedingung

- `critical_paths.md` ist leer und die Entscheidung hängt davon ab: Markiere den PR, statt HOCH zu vergeben, und frage den Menschen.

## Verboten

- Eine Priorität schätzen, ohne eine Regel zu nennen.
- Pfade aus dem Gedächtnis ergänzen. Nur `critical_paths.md` zählt.

## Quellen

Jede Priorität nennt die Regelnummer aus `knowledge/risk_rules.md`.
