"""Morgen-Triage (deterministisch, ohne LLM).

Input:  GITHUB_TOKEN und GITHUB_REPOSITORY (vom Actions-Runner gesetzt),
        knowledge/critical_paths.md
Output: reviews/queue-JJJJ-MM-TT.md und eine Zeile in runs/log.jsonl

Abbruch (kein Queue-File, Fehler im Log):
  2 = critical_paths.md hat keine Einträge, HOCH ist nicht prüfbar
  3 = GitHub-API-Fehler, unvollständiger Abruf oder fehlende Umgebungsvariablen

Heuristik: tests_removed ist True, wenn eine Datei mit "test" im Namen den Status
"removed" hat. Ob der Grund im Diff steht, ist nicht ermittelbar; er gilt als
fehlend (konservativ, also HOCH).
Zusammenfassungen entstehen hier nicht, weil sie den Summarizer brauchen.
"""

import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pr_triage import evaluate

API = "https://api.github.com"
PRIORITY_ORDER = {"HOCH": 0, "MITTEL": 1, "NIEDRIG": 2}


class AbortError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def read_critical_paths():
    text = (ROOT / "knowledge" / "critical_paths.md").read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # Beispielzeilen ignorieren
    paths = [m.group(1) for m in re.finditer(r"^(\S+) – \S", text, flags=re.M)]
    if not paths:
        raise AbortError(2, "critical_paths.md hat keine Einträge. HOCH ist nicht prüfbar.")
    return paths


def api_get_all(url, token):
    items = []
    while url:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                items.extend(json.load(resp))
                link = resp.headers.get("Link", "")
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise AbortError(3, f"GitHub-API-Fehler bei {url}: {exc}") from exc
        match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = match.group(1) if match else None
    return items


def build_pr(pr, token, repo):
    files = api_get_all(f"{API}/repos/{repo}/pulls/{pr['number']}/files?per_page=100", token)
    names = [f["filename"] for f in files]
    removed_tests = [f for f in files if f.get("status") == "removed" and "test" in f["filename"].lower()]
    return {
        "number": pr["number"],
        "title": pr["title"],
        "created_at": pr["created_at"],
        "diff_available": bool(names),
        "files_changed": names,
        "tests_removed": bool(removed_tests),
        "tests_removal_reason_in_diff": False,
    }


def write_queue(rows, today):
    rows.sort(key=lambda r: (PRIORITY_ORDER.get(r[1]["priority"], 3), r[0]["created_at"]))
    evaluable = [r for r in rows if not r[1]["not_evaluable"]]
    not_evaluable = [r for r in rows if r[1]["not_evaluable"]]
    lines = [f"# Review-Warteschlange {today}", ""]
    if not rows:
        lines.append("Keine offenen PRs.")
    for i, (data, res) in enumerate(evaluable, 1):
        lines.append(
            f"{i}. [{res['priority']}] #{data['number']} {data['title']} – "
            f"Zusammenfassung: nicht erzeugt (Summarizer fehlt) – Grund: Regel {res['rule']}"
        )
    lines += ["", "Nicht bewertbar:"]
    lines += [f"- #{data['number']}: Diff nicht lesbar" for data, _ in not_evaluable] or ["- keine"]
    out = ROOT / "reviews"
    out.mkdir(exist_ok=True)
    (out / f"queue-{today}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_log(entry):
    path = ROOT / "runs" / "log.jsonl"
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    try:
        if not token or not repo:
            raise AbortError(3, "GITHUB_TOKEN oder GITHUB_REPOSITORY fehlt.")
        critical = read_critical_paths()
        prs = api_get_all(f"{API}/repos/{repo}/pulls?state=open&per_page=100", token)
        rows = []
        for pr in prs:
            data = build_pr(pr, token, repo)
            rows.append((data, evaluate(data, critical)))
    except AbortError as exc:
        print(f"Abbruch ({exc.code}): {exc}", file=sys.stderr)
        append_log({"date": today, "status": "abbruch", "code": exc.code, "message": str(exc)})
        return exc.code

    write_queue(rows, today)
    counts, rules, not_eval = {}, {}, []
    for data, res in rows:
        if res["not_evaluable"]:
            not_eval.append(data["number"])
        else:
            counts[res["priority"]] = counts.get(res["priority"], 0) + 1
        rules[str(res["rule"])] = rules.get(str(res["rule"]), 0) + 1
    append_log({
        "date": today, "status": "ok", "pr_count": len(rows),
        "priorities": counts, "rules": rules, "not_evaluable": not_eval,
    })
    print(f"Queue geschrieben: {len(rows)} PRs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
