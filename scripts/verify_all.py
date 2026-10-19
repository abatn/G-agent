"""Pflicht-Gate: prüft das gesamte Projekt. rc=0 nur, wenn alle Prüfungen grün sind.

Aufruf:  python3 scripts/verify_all.py
Ausgabe: je Prüfung eine Zeile OK oder FEHLER mit Details.
rc=0  alles grün
rc=1  mindestens eine Prüfung rot
"""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"
sys.path.insert(0, str(ROOT))

RULE_LINE = re.compile(r"^(\d+)\. \*\*(.+?):\*\*")
PRIORITIES = ("HOCH", "MITTEL", "NIEDRIG")
CODE_RULE = re.compile(r'"rule": (\d+)\}')
CODE_PRIORITY = re.compile(r'"priority": "(\w+)"')


def load_module(path):
    spec = importlib.util.spec_from_file_location(f"verify_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


# --- Syntax & Import, Tests ----------------------------------------------------

def check_compile():
    result = run([sys.executable, "-m", "compileall", "-q", "."])
    if result.returncode != 0:
        return [f"compileall rc={result.returncode}: {(result.stdout + result.stderr).strip()[:500]}"]
    return []


def check_tests():
    result = run([sys.executable, "-m", "pytest", "test_evaluation.py", "-q"])
    if result.returncode != 0:
        tail = (result.stdout + result.stderr).strip().splitlines()[-5:]
        return [f"pytest rc={result.returncode}: " + " | ".join(tail)]
    return []


# --- Wissens-Konsistenz --------------------------------------------------------

def load_md_rules():
    rules = {}
    for line in (KNOWLEDGE / "risk_rules.md").read_text(encoding="utf-8").splitlines():
        match = RULE_LINE.match(line)
        if not match:
            continue
        number, label = int(match.group(1)), match.group(2)
        priority = next((p for p in PRIORITIES if p in line), None)
        rules.setdefault(number, {
            "label": label,
            "priority": priority,
            "not_evaluable": label.startswith("Nicht bewertbar"),
        })
    return rules


def check_risk_rules():
    errors = []
    md_rules = load_md_rules()
    if not md_rules:
        return ["risk_rules.md enthält keine nummerierten Regeln"]
    code_lines = {}
    for line in (ROOT / "pr_triage.py").read_text(encoding="utf-8").splitlines():
        match = CODE_RULE.search(line)
        if match:
            code_lines.setdefault(int(match.group(1)), line)
    for number, spec in md_rules.items():
        line = code_lines.get(number)
        if line is None:
            errors.append(f"Regel {number} ({spec['label']}) kommt in pr_triage.py nicht vor")
        elif spec["not_evaluable"]:
            if '"not_evaluable": True' not in line:
                errors.append(f"Regel {number}: risk_rules.md sagt nicht bewertbar, Code nicht")
        elif spec["priority"] is None:
            errors.append(f"Regel {number} ({spec['label']}) nennt keine Priorität")
        elif f'"priority": "{spec["priority"]}"' not in line:
            code_prio = CODE_PRIORITY.search(line)
            errors.append(
                f"Regel {number}: risk_rules.md sagt {spec['priority']}, "
                f"Code sagt {code_prio.group(1) if code_prio else '?'}"
            )
    for number in code_lines:
        if number not in md_rules:
            errors.append(f"pr_triage.py verwendet Regel {number}, die risk_rules.md nicht definiert")
    return errors


def check_critical_paths():
    # Gleiche Regel wie der Morgenlauf: Einträge "<pfad> – <Grund>", Kommentare ignoriert.
    text = (KNOWLEDGE / "critical_paths.md").read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    paths = [m.group(1) for m in re.finditer(r"^(\S+) – \S", text, flags=re.M)]
    if not paths:
        return ["critical_paths.md hat keine Einträge im Format '<pfad> – <Grund>'"]
    return [f"Pfad existiert nicht: {p}" for p in paths if not (ROOT / p).exists()]


def check_markdown(name):
    path = KNOWLEDGE / name
    if not path.is_file():
        return [f"{name} fehlt"]
    lines = path.read_text(encoding="utf-8").splitlines()
    errors = []
    if not any(line.strip() for line in lines):
        errors.append(f"{name} ist leer")
    if sum(1 for line in lines if line.lstrip().startswith("```")) % 2:
        errors.append(f"{name}: ungerade Anzahl Code-Fences")
    if not any(line.startswith("#") for line in lines):
        errors.append(f"{name}: keine Überschrift")
    return errors


# --- Skills --------------------------------------------------------------------

def check_skills():
    errors = []
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skill_files:
        return ["keine SKILL.md in skills/ gefunden"]
    names = set()
    for path in skill_files:
        lines = path.read_text(encoding="utf-8").splitlines()
        label = str(path.relative_to(ROOT))
        if not lines or lines[0].strip() != "---" or "---" not in lines[1:]:
            errors.append(f"{label}: kein geschlossenes Frontmatter")
            continue
        end = lines.index("---", 1)
        try:
            meta = yaml.safe_load("\n".join(lines[1:end]))
        except yaml.YAMLError as exc:
            errors.append(f"{label}: YAML ungültig ({exc})")
            continue
        if not isinstance(meta, dict):
            errors.append(f"{label}: Frontmatter ist kein Schlüssel-Wert-Block")
            continue
        for key in ("name", "description"):
            if not isinstance(meta.get(key), str) or not meta[key].strip():
                errors.append(f"{label}: Feld '{key}' fehlt oder ist leer")
        if meta.get("name") != path.parent.name:
            errors.append(f"{label}: name '{meta.get('name')}' passt nicht zum Ordner")
        names.add(path.parent.name)
    required = re.findall(r"^- Skill: `([\w-]+)`", (ROOT / "PROJECT_IDENTITY.md").read_text(encoding="utf-8"), re.M)
    if not required:
        errors.append("PROJECT_IDENTITY.md nennt keine Skills (Zeilen '- Skill: `name`')")
    for name in required:
        if name not in names:
            errors.append(f"in PROJECT_IDENTITY.md genannter Skill '{name}' fehlt in skills/")
    return errors


# --- Scoring Set ---------------------------------------------------------------

def check_scoring_set():
    errors = []
    try:
        data = json.loads((ROOT / "scoring_set.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"scoring_set.json ist kein gültiges JSON: {exc}"]
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list) or not cases:
        return ["scoring_set.json hat keine Liste 'cases'"]
    from pr_triage import evaluate

    covered = set()
    for case in cases:
        try:
            covered.add(evaluate(case["pr"], case["critical_paths"])["rule"])
        except (KeyError, TypeError) as exc:
            errors.append(f"Fall {case.get('id', '?')}: {type(exc).__name__}: {exc}")
    for number in sorted(set(load_md_rules()) - covered):
        errors.append(f"Regel {number} hat keinen Testfall im Scoring Set")
    return errors


# --- Skripte und Dokumentation -------------------------------------------------

def check_scripts():
    errors = []
    scripts = sorted((ROOT / "scripts").glob("*.py"))
    if not scripts:
        return ["keine Skripte in scripts/ gefunden"]
    for path in scripts:
        try:
            load_module(path)
        except Exception as exc:  # Fehler melden, nicht verschlucken
            errors.append(f"{path.relative_to(ROOT)}: {type(exc).__name__}: {exc}")
    return errors


def check_docs():
    errors = []
    for name in ("README.md", "LICENSE"):
        path = ROOT / name
        if not path.is_file():
            errors.append(f"{name} fehlt")
        elif not path.read_text(encoding="utf-8", errors="replace").strip():
            errors.append(f"{name} ist leer")
    return errors


CHECKS = [
    ("Syntax (compileall)", check_compile),
    ("Tests (pytest)", check_tests),
    ("Wissen: risk_rules.md gegen pr_triage.py", check_risk_rules),
    ("Wissen: critical_paths.md", check_critical_paths),
    ("Wissen: charters.md", lambda: check_markdown("charters.md")),
    ("Wissen: connectors.md", lambda: check_markdown("connectors.md")),
    ("Wissen: migration-notes.md", lambda: check_markdown("migration-notes.md")),
    ("Skills (Frontmatter, PROJECT_IDENTITY)", check_skills),
    ("Scoring Set (JSON, Regeln 1-5)", check_scoring_set),
    ("Skripte (importierbar)", check_scripts),
    ("Dokumentation (README, LICENSE)", check_docs),
]


def main():
    failed = 0
    for name, check in CHECKS:
        try:
            errors = check()
        except Exception as exc:  # unerwarteter Fehler zählt als rot
            errors = [f"unerwarteter Fehler: {type(exc).__name__}: {exc}"]
        if errors:
            failed += 1
            print(f"FEHLER  {name}")
            for error in errors:
                print(f"          - {error}")
        else:
            print(f"OK      {name}")
    print(f"\n{len(CHECKS) - failed}/{len(CHECKS)} Prüfungen grün.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
