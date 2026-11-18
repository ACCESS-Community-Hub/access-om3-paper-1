#!/usr/bin/env python3
"""Static checks for access-om3-paper-1 notebooks (no Gadi, no data needed).

Checks that each notebook can be driven by papermill/mkfigs and flags patterns
that break across resolutions, forcings (RYF/IAF) and models (OM3/CM3).

    cd notebooks
    python check_notebooks.py                 # every notebook not marked to skip
    python check_notebooks.py A.ipynb B.ipynb # just these

ERRORs fail the check (exit 1). WARNs and INFOs are reported but never fail it.

To exclude a notebook that isn't meant for the mkfigs pipeline (exploratory work,
OM2-only analysis, one-off scripts), add this to its notebook metadata
(JupyterLab: Property Inspector > Advanced Tools > Notebook metadata):

    "mkfigs": {"skip": true, "reason": "OM2-only analysis"}
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=SyntaxWarning)

# Names every pipeline notebook's `parameters` cell must set (papermill injects these).
REQUIRED_PARAMS = {"esm_file", "papermill", "cwd", "nbname"}
# Averaging-window settings: should be in the `parameters` cell so a run can override them.
WINDOW_PARAMS = {"NYEARS", "averaging_period"}
# Saved image output above this size (bytes, base64) gets a warning. Tables/text are fine.
IMAGE_LIMIT = 1_000_000

MAGIC = re.compile(r"^\s*[%!].*$", re.M)
# Run paths written into the code (reference runs belong in one shared lookup).
RUN_PATH = re.compile(r"/(?:g/data|scratch)/\w+/(?:outputs/access-(?:om|cm|esm)\d|[\w/.-]*/archive/)[^\s'\"]*")
# Calendar-year literals in time selections: break RYF (model years 1900-19xx) and short runs.
YEAR_SLICE = re.compile(r"""(?:slice|sel)\([^)]*?['"]?(1[89]\d\d|20\d\d)(?:-\d\d)?(?:-\d\d)?['"]?""")
# Forcing/model guessed from the datastore path (see #184's `find('ryf') != 0` bug).
PATH_SNIFF = re.compile(r"""esm_file\.find\(\s*['"](ryf|iaf|cm3|om2|8km|25km|100km)['"]\s*\)""")


class Report:
    def __init__(self):
        self.rows: list[tuple[str, str, str]] = []

    def add(self, level, nb, msg):
        self.rows.append((level, nb, msg))


def code(cell):
    return "".join(cell.get("source", []))


def assigned_names(src):
    try:
        tree = ast.parse(MAGIC.sub("", src))
    except SyntaxError:
        return set()
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            for t in node.targets if isinstance(node, ast.Assign) else [node.target]:
                out |= {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}
    return out


def check(path: Path, rep: Report):
    name = path.name
    try:
        nb = json.loads(path.read_text())
    except Exception as e:  # noqa: BLE001
        rep.add("ERROR", name, f"not valid JSON: {e}")
        return
    skip = (nb.get("metadata", {}).get("mkfigs") or {})
    if skip.get("skip"):
        rep.add("INFO", name, f"skipped ({skip.get('reason', 'no reason given')})")
        return
    cells = nb.get("cells", [])
    codes = [(i, c) for i, c in enumerate(cells) if c["cell_type"] == "code"]

    # 1. parameters cell: exactly one, first code cell, sets the papermill names
    tagged = [i for i, c in codes if "parameters" in (c.get("metadata", {}).get("tags") or [])]
    if not tagged:
        rep.add("ERROR", name, "no cell tagged `parameters` (papermill can't pass in esm_file); "
                               "add one, or mark the notebook to skip")
        return
    if len(tagged) > 1:
        rep.add("ERROR", name, f"{len(tagged)} cells tagged `parameters`; papermill uses only one")
    p = tagged[0]
    if p != codes[0][0]:
        rep.add("WARN", name, "`parameters` cell isn't the first code cell")
    params = assigned_names(code(cells[p]))
    if missing := REQUIRED_PARAMS - params:
        rep.add("ERROR", name, f"`parameters` cell doesn't set {sorted(missing)}")
    body = [(i, code(c)) for i, c in codes if i > p]
    alltext = "\n".join(s for _, s in body)

    # 2-3. mkfigs plumbing
    if "MkmdWriter(" not in alltext:
        rep.add("ERROR", name, "no `MkmdWriter(...)` cell (copy cell 2 of 00_template_notebook)")
    if not any(re.search(r"^\s*mkmd\.(savefig|table)\(", s, re.M) for _, s in body):
        rep.add("ERROR", name, "no uncommented `mkmd.savefig`/`mkmd.table`, so nothing reaches the website")

    # 4. every code cell parses (catches merge debris, broken suggestion commits)
    for i, c in codes:
        try:
            ast.parse(MAGIC.sub("", code(c)))
        except SyntaxError as e:
            rep.add("ERROR", name, f"cell {i}: SyntaxError line {e.lineno}: {e.msg}")

    # 7. averaging window settable by papermill
    late = {var: i for var in sorted(WINDOW_PARAMS - params)
            for i, s in reversed(body) if var in assigned_names(s)}
    if late:
        where = ", ".join(f"`{v}` (cell {i})" for v, i in late.items())
        rep.add("WARN", name, f"{where} set outside the `parameters` cell, so papermill can't override")

    # 8. calendar years in time selections
    for i, s in body:
        years = sorted(set(YEAR_SLICE.findall(s)))
        if years:
            rep.add("WARN", name, f"cell {i}: literal years {years} in a time selection; "
                                  "breaks RYF/short runs (use years_window/NYEARS)")

    # 10. large saved images (tables and text outputs are fine)
    img = sum(len("".join(v) if isinstance(v, list) else v)
              for _, c in codes for o in c.get("outputs", [])
              for k, v in o.get("data", {}).items() if k.startswith("image/"))
    if img > IMAGE_LIMIT:
        rep.add("WARN", name, f"{img / 1e6:.1f} MB of saved images; please clear figure outputs")

    # 11-12. informational
    for i, s in body:
        for m in PATH_SNIFF.finditer(s):
            rep.add("INFO", name, f"cell {i}: forcing/model guessed from path via find('{m.group(1)}')")
        for m in RUN_PATH.finditer(s):
            rep.add("INFO", name, f"cell {i}: run path in code {m.group(0)[:60]}...")


def mkfigs_array(nbdir: Path):
    m = re.search(r"^array=\(\n(.*?)^\)", (nbdir / "mkfigs.sh").read_text(), re.S | re.M)
    names = []
    for line in m.group(1).splitlines() if m else []:
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line.split("#")[0].split()[0])
    return names


def check_array(nbdir: Path, rep: Report):
    enabled = mkfigs_array(nbdir)
    # 5. array entries point at real notebooks
    for n in enabled:
        if n.endswith(".ipynb"):
            rep.add("ERROR", "mkfigs.sh", f"array entry `{n}` must not include .ipynb")
        elif not (nbdir / f"{n}.ipynb").exists():
            rep.add("ERROR", "mkfigs.sh", f"array entry `{n}` has no notebook")
    # 6. issue links (mkfigs_issues.py is a trusted in-repo config, loaded as a module)
    spec = importlib.util.spec_from_file_location("mkfigs_issues", nbdir / "mkfigs_issues.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for n in enabled:
        if not getattr(mod, "ISSUES", {}).get(n):
            rep.add("WARN", n + ".ipynb", "no GitHub issue linked in mkfigs_issues.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notebooks", nargs="*")
    ap.add_argument("--dir", default=".")
    ap.add_argument("--markdown", help="also append a markdown table here (e.g. $GITHUB_STEP_SUMMARY)")
    ap.add_argument("--comment", help="write a short PR-comment body here: errors/warnings for changed notebooks only")
    ap.add_argument("--changed-file", help="file listing the notebooks the PR changed, one per line (for --comment)")
    a = ap.parse_args()
    nbdir = Path(a.dir)
    rep = Report()

    check_array(nbdir, rep)
    targets = [nbdir / Path(n).name for n in a.notebooks] or sorted(nbdir.glob("*.ipynb"))
    for t in targets:
        if t.exists():
            check(t, rep)

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    rep.rows.sort(key=lambda r: (order[r[0]], r[1]))
    gha = os.environ.get("GITHUB_ACTIONS") == "true"
    for level, nb, msg in rep.rows:
        print(f"{level:5s} {nb}: {msg}")
        if gha and level != "INFO":  # inline annotations on the PR's Files tab
            kind = "error" if level == "ERROR" else "warning"
            print(f"::{kind} file=notebooks/{nb}::{msg}")
    counts = {k: sum(r[0] == k for r in rep.rows) for k in order}
    print(f"\n{len(targets)} notebooks checked: {counts}")
    icon = {"ERROR": "❌", "WARN": "⚠️", "INFO": "ℹ️"}

    def table(rows):
        return "| | Notebook | Finding |\n|---|---|---|\n" + "".join(
            f"| {icon[l]} | `{n}` | {m.replace('|', '/')} |\n" for l, n, m in rows)

    if a.markdown:
        with open(a.markdown, "a") as f:
            f.write(f"### Notebook checks: {counts}\n\n{table(rep.rows)}")
    if a.comment:
        write_comment(a, rep, table)
    sys.exit(1 if counts["ERROR"] else 0)


def write_comment(a, rep, table):
    changed = []
    if a.changed_file and Path(a.changed_file).exists():
        changed = sorted({Path(l.strip()).name for l in Path(a.changed_file).read_text().splitlines() if l.strip()})
    mine = [r for r in rep.rows if r[0] != "INFO" and (r[1] in changed or r[1] == "mkfigs.sh")]
    other_errors = sum(r[0] == "ERROR" and r not in mine for r in rep.rows)
    env = os.environ
    run = (f"{env['GITHUB_SERVER_URL']}/{env['GITHUB_REPOSITORY']}/actions/runs/{env['GITHUB_RUN_ID']}"
           if "GITHUB_RUN_ID" in env else None)

    n_err = sum(r[0] == "ERROR" for r in mine)
    n_warn = sum(r[0] == "WARN" for r in mine)
    lines = ["### Notebook checks", ""]
    if not changed:
        lines.append("This PR doesn't change any notebooks.")
    elif not mine:
        lines.append(f"✅ No errors or warnings in the {len(changed)} notebook(s) this PR changes.")
    else:
        lines += [f"Notebooks changed by this PR: {n_err} error(s) ❌, {n_warn} warning(s) ⚠️. "
                  "Errors fail the check; warnings are suggestions.", "", table(mine)]
    if other_errors:
        lines += ["", f"❌ Plus {other_errors} error(s) in notebooks this PR doesn't change (see the full report)."]
    lines += ["", "<sub>Updated on every push. "
              + (f"[Full report for all notebooks]({run}). " if run else "")
              + "Rules and how to skip a notebook: `notebooks/check_notebooks.py`.</sub>"]
    Path(a.comment).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
