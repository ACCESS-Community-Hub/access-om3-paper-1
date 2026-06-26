#!/usr/bin/env python3
"""
mkfigs_pushit.sh  –  Check mkfigs.sh results and prepare for GitHub upload.

Run from anywhere; paths are resolved relative to this script's location.

Usage:
    python3 mkfigs_pushit.sh [--dry-run]
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE      = Path(__file__).resolve().parent          # notebooks/
REPO      = HERE.parent                              # repo root
MKFIGS_SH = HERE / "mkfigs.sh"

# ---------------------------------------------------------------------------
# Parse mkfigs.sh for ENAME and notebook array
# ---------------------------------------------------------------------------
def parse_mkfigs(path: Path):
    text = path.read_text()

    # Last uncommented ENAME= line wins
    ename = None
    for line in text.splitlines():
        m = re.match(r"^\s*ENAME=(.+)", line)
        if m:
            ename = m.group(1).strip().strip('"').strip("'")

    # Notebook array  (uncommented entries between 'array=(' and ')')
    notebooks = []
    in_array = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^array=\(", stripped):
            in_array = True
            continue
        if in_array:
            if stripped == ")":
                break
            if stripped and not stripped.startswith("#"):
                notebooks.append(stripped)

    return ename, notebooks


# ---------------------------------------------------------------------------
# Check a single notebook
# ---------------------------------------------------------------------------
def check_notebook(nb: str, ofol: Path, mkmd: Path):
    rendered = ofol / f"{nb}_rendered.ipynb"
    pngs     = sorted(mkmd.glob(f"{nb}_*.png"))

    if not rendered.exists():
        return "NOT RUN", []

    # If the notebook was stripped (outputs cleared), we can't check for error
    # cells, so rely on PNGs as the success signal.
    if pngs:
        return "OK", pngs

    # No PNGs — inspect rendered notebook for error outputs as a diagnostic
    try:
        nb_data = json.loads(rendered.read_text())
        for cell in nb_data["cells"]:
            for out in cell.get("outputs", []):
                if out.get("output_type") == "error":
                    return "FAILED (error in notebook)", []
    except Exception:
        pass

    return "FAILED (no PNGs produced)", []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be done without copying files")
    args = parser.parse_args()

    ename, notebooks = parse_mkfigs(MKFIGS_SH)
    if not ename:
        sys.exit("ERROR: Could not parse ENAME from mkfigs.sh")
    if not notebooks:
        sys.exit("ERROR: Could not parse notebook array from mkfigs.sh")

    ofol  = HERE   / f"mkfigs_output_{ename}"
    mkmd  = ofol   / "mkmd"
    md_src = mkmd  / f"{ename}.md"
    md_dst = REPO  / "documentation" / "docs" / "pages" / "index.md"

    print(f"Experiment : {ename}")
    print(f"Output dir : {ofol}")
    print(f"Dry run    : {args.dry_run}")
    print()

    # ------------------------------------------------------------------
    # Check each notebook
    # ------------------------------------------------------------------
    succeeded, failed, not_run = [], [], []

    print(f"{'Notebook':<45}  {'Status':<35}  PNGs")
    print("-" * 90)
    for nb in notebooks:
        status, pngs = check_notebook(nb, ofol, mkmd)
        png_names = ", ".join(p.name for p in pngs) if pngs else "—"
        print(f"{nb:<45}  {status:<35}  {png_names}")
        if status == "OK":
            succeeded.append(nb)
        elif status == "NOT RUN":
            not_run.append(nb)
        else:
            failed.append(nb)

    print()
    print(f"Results: {len(succeeded)} OK  |  {len(failed)} failed  |  {len(not_run)} not yet run")
    print()

    # ------------------------------------------------------------------
    # Check markdown
    # ------------------------------------------------------------------
    if md_src.exists():
        print(f"Markdown OK : {md_src.relative_to(REPO)}")
    else:
        print(f"WARNING     : Markdown not found: {md_src.relative_to(REPO)}")
    print()

    if not succeeded:
        print("No successful notebooks to copy — nothing to do.")
        return

    # ------------------------------------------------------------------
    # Copy stripped rendered notebooks → source notebooks/
    # ------------------------------------------------------------------
    print(f"Copying {len(succeeded)} rendered (output-stripped) notebook(s) back to notebooks/ ...")
    copied_nbs = []
    for nb in succeeded:
        src = ofol / f"{nb}_rendered.ipynb"
        dst = HERE / f"{nb}.ipynb"
        if args.dry_run:
            print(f"  [dry-run] {src.relative_to(REPO)}  →  {dst.relative_to(REPO)}")
        else:
            shutil.copy2(src, dst)
            print(f"  {src.name}  →  {dst.relative_to(REPO)}")
        copied_nbs.append(dst)

    # ------------------------------------------------------------------
    # Copy markdown → documentation
    # ------------------------------------------------------------------
    print()
    if md_src.exists():
        if args.dry_run:
            print(f"[dry-run] {md_src.relative_to(REPO)}  →  {md_dst.relative_to(REPO)}")
        else:
            md_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md_src, md_dst)
            print(f"Markdown copied: {md_dst.relative_to(REPO)}")
    print()

    # ------------------------------------------------------------------
    # Suggested git commands
    # ------------------------------------------------------------------
    today = datetime.now()
    tag   = f"docs-{ename}-{today.year}.{today.month:02d}.000"

    nb_paths = " \\\n    ".join(f"notebooks/{nb}.ipynb" for nb in succeeded)

    print("=" * 70)
    print("Suggested git commands (run from repo root):")
    print("=" * 70)
    print()
    print(f"cd {REPO}")
    print()
    print(f"git add \\\n    {nb_paths} \\\n    documentation/docs/pages/index.md")
    print()
    print(f'git commit -m "docs: render evaluation figures for {ename}"')
    print()
    print(f"git tag {tag}")
    print(f"git push origin main --tags")
    print()

    if failed:
        print(f"NOTE: {len(failed)} notebook(s) failed and were NOT copied:")
        for nb in failed:
            print(f"  - {nb}")
    if not_run:
        print(f"NOTE: {len(not_run)} notebook(s) have not run yet:")
        for nb in not_run:
            print(f"  - {nb}")


if __name__ == "__main__":
    main()
