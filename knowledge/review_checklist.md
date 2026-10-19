# Review-Checkliste

Diese Datei wird bei jeder Aufgabe geladen. Sie definiert, was ein gutes Ergebnis ausmacht.

## Was ein gutes Ergebnis ausmacht

- Jeder PR, der offen ist, erscheint genau einmal in der Liste.
- Die Priorität ist aus den Regeln in `risk_rules.md` ableitbar und nicht geschätzt.
- Die Ein-Satz-Zusammenfassung beschreibt nur, was im gelesenen Diff steht.
- Der Grund nennt den konkreten Auslöser (z. B. berührter kritischer Pfad, fehlende Tests).
- Fehlende Daten (Diff, Kommentare, Zeitstempel) stehen im Block `Nicht bewertbar:` und nicht in einer Bewertung.

## Was einen PR blockiert (Priorität HOCH, Review sofort)

- Änderungen an einem Pfad aus `critical_paths.md`.
- Entfernte oder deaktivierte Tests, ohne dass der Grund im Diff steht.
- Änderungen an Zugriffs-, Berechtigungs- oder Geheimnis-Logik.

## Was einen PR als Routine kennzeichnet (Priorität NIEDRIG)

- Ausschließlich Dokumentation oder Kommentare.
- Ausschließlich Formatierung ohne Logikänderung.

## Was nicht bewertbar ist

- Kein lesbarer Diff.
- Keine Angabe zu geänderten Dateien.
- Zeitstempel fehlen und sind für die Priorität nötig.
