#!/usr/bin/env python3
"""
mkfigs_restore.py — rebuild mkfigs_output_{ENAME}/ from previously committed content.

Run this BEFORE qsub mkfigs.sh when adding notebooks to (or re-running notebooks
for) an experiment that was previously pushed.  It downloads the rendered notebooks
from Figshare and copies the summary markdown files from the docs tree, so
mkfigs_pushit.py sees them as already-committed notebooks alongside any new ones
you run.  New or re-run notebooks take priority over the restored versions.

Usage:
    cd /g/data/tm70/.../repos/access-om3-paper-1/notebooks
    python3 mkfigs_restore.py
    python3 mkfigs_restore.py --ename MC_25km_jra_iaf+wombatlite-test3v2-00532b88
    python3 mkfigs_restore.py --force   # re-download even if already present

After restoring, edit the notebook array in mkfigs.sh to include new/changed
notebooks, then submit:  qsub mkfigs.sh
"""

from __future__ import annotations

try:
    import nci_ipynb  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.exit(
        "ERROR: nci_ipynb not found.\n"
        "Please load the conda environment before running this script:\n\n"
        "  module purge\n"
        "  module use /g/data/xp65/public/modules\n"
        "  module load conda/analysis3\n"
    )

import argparse
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DOCS_PAGES = REPO / "documentation" / "docs" / "pages"


def _parse_ename_from_mkfigs_sh() -> str:
    sh = HERE / "mkfigs.sh"
    ename = None
    for line in sh.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = re.match(r"^ENAME=([^\s#]+)", stripped)
        if m:
            ename = m.group(1)
    if not ename:
        sys.exit("ERROR: could not find ENAME in mkfigs.sh")
    return ename


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--ename", default=None,
                   help="Override experiment name (default: parsed from mkfigs.sh)")
    p.add_argument("--force", action="store_true",
                   help="Re-download notebooks even if already present locally")
    args = p.parse_args()

    ename = args.ename or _parse_ename_from_mkfigs_sh()
    experiment_docs_dir = DOCS_PAGES / "experiments" / ename
    ofol  = HERE / f"mkfigs_output_{ename}"
    mdfol = ofol / "mkmd"

    print()
    print("=" * 56)
    print("mkfigs_restore.py")
    print(f"  Experiment : {ename}")
    print(f"  Output dir : {ofol}")
    print("=" * 56)
    print()

    urls_json = experiment_docs_dir / "notebooks_urls.json"
    if not urls_json.exists():
        sys.exit(
            f"ERROR: {urls_json} not found.\n"
            "This experiment has not been pushed yet — nothing to restore.\n"
            "Run mkfigs_pushit.py first."
        )

    notebook_urls: dict[str, str] = {
        k: v for k, v in json.loads(urls_json.read_text()).items()
        if not k.startswith("_")
    }
    if not notebook_urls:
        sys.exit("No notebook URLs in notebooks_urls.json — nothing to restore.")

    ofol.mkdir(exist_ok=True)
    mdfol.mkdir(exist_ok=True)

    n_downloaded = 0
    n_skipped    = 0
    n_md_copied  = 0

    for nb_name, url in notebook_urls.items():
        dest_nb = ofol / f"{nb_name}_rendered.ipynb"
        if dest_nb.exists() and not args.force:
            print(f"  {nb_name}_rendered.ipynb  already present — skipping (use --force to re-download)")
            n_skipped += 1
        else:
            print(f"  {nb_name}_rendered.ipynb  <-  {url}")
            try:
                urllib.request.urlretrieve(url, dest_nb)
                n_downloaded += 1
            except Exception as exc:
                print(f"    ERROR: {exc}", file=sys.stderr)
                continue

        src_md = experiment_docs_dir / f"{nb_name}.md"
        dst_md = mdfol / f"{nb_name}.md"
        if src_md.exists():
            shutil.copy2(src_md, dst_md)
            print(f"  {nb_name}.md              copied from docs tree")
            n_md_copied += 1
        else:
            print(f"  WARNING: {src_md} not found — .md not restored")

    print()
    print(f"Done: {n_downloaded} downloaded, {n_skipped} already present, {n_md_copied} .md files copied.")
    print()
    print("Now edit the notebook array in mkfigs.sh to include new/changed notebooks,")
    print("then submit:  qsub mkfigs.sh")
    print()


if __name__ == "__main__":
    main()
