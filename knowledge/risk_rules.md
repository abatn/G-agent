# Risikoregeln

Die Regeln werden in dieser Reihenfolge angewendet. Die erste zutreffende Regel bestimmt die Priorität.

1. **Nicht bewertbar:** Diff nicht lesbar oder Dateiliste fehlt. Keine Priorität, Eintrag in `Nicht bewertbar:`. Diese Regel gilt vor allen anderen. Ist der Diff nicht lesbar, ist der PR nicht bewertbar, auch wenn Dateien gelistet sind.
2. **HOCH:** Mindestens eine geänderte Datei liegt in einem Pfad aus `critical_paths.md`.
3. **HOCH:** Tests wurden entfernt oder deaktiviert, ohne dass der Grund im Diff steht.
4. **NIEDRIG:** Alle geänderten Dateien sind reine Dokumentation (z. B. `.md`) oder reine Formatierung.
5. **MITTEL:** Alle übrigen Fälle.
6. **MITTEL:** Unklare Fälle. Der Grund nennt den fehlenden Datenpunkt.

## Begründung

Der Grund ist ein Satz und nennt den Auslöser der Regel, z. B. „berührt kritischen Pfad <Pfad>“ oder „Tests entfernt“.
