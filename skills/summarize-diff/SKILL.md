---
name: summarize-diff
description: Verwende diese Fähigkeit, wenn ein einzelner Pull Request in einem Satz zusammengefasst werden soll, etwa im Rahmen der PR-Triage.
---

# Diff zusammenfassen

## Ziel

Ein Satz, der beschreibt, was der Diff tatsächlich ändert.

## Ablauf

1. Prüfe, ob ein lesbarer Diff vorliegt. Wenn nicht: Markiere den PR als nicht bewertbar und schreibe keine Zusammenfassung.
2. Lies die geänderten Dateien und die Hunks im Diff.
3. Formuliere einen Satz im Muster: Was wurde geändert, und in welchem Bereich. Beispiel für die Form: „Ändert die Ablaufzeit einer Sitzung in der Anmeldelogik.“
4. Prüfe den Satz gegen den Diff. Jede Aussage muss im Diff stehen.

## Verboten

- Absichten, Gründe oder Auswirkungen erraten, die nicht im Diff oder in der PR-Beschreibung stehen.
- Füllwörter wie „verbessert“ oder „optimiert“, wenn der Diff das nicht zeigt.

## Quellen

Nenne hinter dem Satz die geänderten Dateien, auf die er sich stützt.
