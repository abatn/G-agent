# Kritische Pfade

Format: ein Pfad pro Zeile, danach ` – ` und ein Satz, warum er wichtig ist.

Status: **aus dem Repo abgeleitet, vom Team zu bestätigen.** Die Pfade beschreiben die Dateien, die über die Priorität der PRs entscheiden oder den Morgenlauf steuern. Sie sind keine Vorgabe des Teams. Ändert sich einer davon, sollte die Priorisierung neu geprüft werden.

pr_triage.py – Enthält die Regelkette, die jede PR-Priorität bestimmt. Ein Fehler hier verfälscht alle Warteschlangen.
scripts/pr_triage_morning.py – Ruft die GitHub-API ab, bewertet PRs und schreibt Queue und Log. Fehler hier betreffen jeden Morgenlauf.
.github/workflows/pr-triage-morning.yml – Legt Zeitplan, Berechtigungen und Schreibrechte des Morgenlaufs fest. Ein Fehler kann Daten lesen oder Commits in den Branch schreiben lassen.
knowledge/risk_rules.md – Definiert die Regeln, nach denen die Priorität vergeben wird. Eine Änderung verändert das Ergebnis aller PRs.

<!-- Beispielzeile (nicht gültig, nur Format):
path/to/file – Warum dieser Pfad kritisch ist, in einem Satz.
-->
