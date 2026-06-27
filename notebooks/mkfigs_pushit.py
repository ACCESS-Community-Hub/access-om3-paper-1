#!/usr/bin/env python3
"""
mkfigs_pushit.py – check mkfigs.sh results, upload figures to Figshare, and
prepare the git commit.

Run interactively on a login node (not via qsub — compute nodes have no
internet access) after mkfigs.sh completes:

    cd /g/data/tm70/cyb561/repos/access-om3-paper-1/notebooks
    python3 mkfigs_pushit.py
    python3 mkfigs_pushit.py --dry-run          # preview: nothing written or uploaded
    python3 mkfigs_pushit.py --skip-figshare    # copy files + git commands, but skip upload
    python3 mkfigs_pushit.py --ename MC_25km_jra_iaf+wombatlite-test3v2-00532b88

Figshare token: set FIGSHARE_TOKEN env var, or store in ~/.figshare_token.
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent   # notebooks/
REPO = HERE.parent                       # repo root


# ---------------------------------------------------------------------------
# Parse mkfigs.sh to get ENAME and notebook list
# ---------------------------------------------------------------------------
def parse_mkfigs_sh() -> tuple[str, list[str]]:
    sh = HERE / "mkfigs.sh"
    text = sh.read_text()

    # Last uncommented ENAME= line
    ename = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = re.match(r'^ENAME=([^\s#]+)', stripped)
        if m:
            ename = m.group(1)
    if not ename:
        sys.exit("ERROR: could not find ENAME in mkfigs.sh")

    # Notebook array=(...)
    m = re.search(r'array=\(([^)]*)\)', text, re.DOTALL)
    if not m:
        sys.exit("ERROR: could not find array=(...) in mkfigs.sh")
    notebooks = []
    for line in m.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        notebooks.append(stripped)

    return ename, notebooks


# ---------------------------------------------------------------------------
# Figshare token resolution
# ---------------------------------------------------------------------------
def resolve_figshare_token() -> str:
    token = os.environ.get("FIGSHARE_TOKEN", "")
    if token:
        return token
    token_file = Path.home() / ".figshare_token"
    if token_file.exists():
        token = token_file.read_text().strip()
        print(f"[figshare] Loaded token from {token_file}")
    return token


# ---------------------------------------------------------------------------
# Figshare upload
# ---------------------------------------------------------------------------
def upload_figshare(mdfol: Path, ename: str, token: str) -> None:
    sys.path.insert(0, str(HERE))
    try:
        from mkfigs_configdoc import figshare_upload_and_rewrite
    except ImportError as exc:
        print(f"[figshare] ERROR: could not import mkfigs_configdoc: {exc}")
        return

    print()
    print("=" * 56)
    print("Uploading figures to Figshare")
    print(f"  Experiment : {ename}")
    print(f"  Source dir : {mdfol}")
    print("=" * 56)

    try:
        url_map = figshare_upload_and_rewrite(
            mdfol=str(mdfol), experiment=ename, token=token,
        )
    except Exception as exc:
        print(f"[figshare] ERROR: upload raised an exception: {exc}")
        return

    if url_map:
        print("[figshare] Upload summary:")
        for fname, url in sorted(url_map.items()):
            print(f"  {fname}")
            print(f"    {url}")
    else:
        print("[figshare] No files uploaded (nothing new or no PNGs found).")

    manifest = mdfol / "figshare_manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text())
        art_id = data.get(f"article_id_{ename}")
        if art_id:
            print(f"[figshare] Article: https://figshare.com/articles/figure/{art_id}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--dry-run", action="store_true",
                   help="Report results and echo git commands without copying files")
    p.add_argument("--skip-figshare", action="store_true",
                   help="Skip Figshare upload even if a token is available")
    p.add_argument("--ename", default=None,
                   help="Override experiment name (default: parsed from mkfigs.sh)")
    args = p.parse_args()

    ename, notebooks = parse_mkfigs_sh()
    if args.ename:
        ename = args.ename
    ofol  = HERE / f"mkfigs_output_{ename}"
    mdfol = ofol / "mkmd"

    print()
    print("=" * 56)
    print("mkfigs_pushit.py")
    print(f"  Experiment : {ename}")
    print(f"  Output dir : {ofol}")
    if args.dry_run:
        print("  Mode       : DRY RUN (no files will be copied)")
    print("=" * 56)
    print()

    # -----------------------------------------------------------------------
    # Check each notebook
    # -----------------------------------------------------------------------
    ok_nbs:      list[str] = []
    failed_nbs:  list[str] = []
    not_run_nbs: list[str] = []

    for nb in notebooks:
        rendered = ofol / f"{nb}_rendered.ipynb"
        pngs = list(mdfol.glob(f"{nb}_*.png")) if mdfol.exists() else []
        if not rendered.exists():
            not_run_nbs.append(nb)
            status = "NOT RUN"
        elif not pngs:
            failed_nbs.append(nb)
            status = "FAILED  (no PNGs)"
        else:
            ok_nbs.append(nb)
            status = f"OK      ({len(pngs)} PNG{'s' if len(pngs) != 1 else ''})"
        print(f"  {status:<34}  {nb}")

    print()
    print(f"  OK: {len(ok_nbs)}   FAILED: {len(failed_nbs)}   NOT RUN: {len(not_run_nbs)}")
    print()

    if not ok_nbs:
        print("No successful notebooks — nothing to push.")
        return

    # -----------------------------------------------------------------------
    # Figshare upload
    # -----------------------------------------------------------------------
    if args.dry_run:
        print(f"[figshare] DRY RUN: would upload PNGs from {mdfol}")
    elif args.skip_figshare:
        print("[figshare] Upload skipped (--skip-figshare).")
    else:
        token = resolve_figshare_token()
        if token:
            upload_figshare(mdfol, ename, token)
        else:
            print("[figshare] No token found — skipping upload.")
            print("           Set FIGSHARE_TOKEN or store token in ~/.figshare_token")

    # -----------------------------------------------------------------------
    # Copy files
    # -----------------------------------------------------------------------
    print()
    if args.dry_run:
        print("DRY RUN: would copy the following files:")
    else:
        print("Copying files:")

    for nb in ok_nbs:
        src = ofol / f"{nb}_rendered.ipynb"
        dst = HERE / f"{nb}.ipynb"
        print(f"  {src.name}  ->  notebooks/{nb}.ipynb")
        if not args.dry_run:
            shutil.copy2(src, dst)

    md_src = mdfol / f"{ename}.md"
    md_dst = REPO / "documentation" / "docs" / "pages" / "index.md"
    if md_src.exists():
        print(f"  mkmd/{ename}.md  ->  documentation/docs/pages/index.md")
        if not args.dry_run:
            md_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md_src, md_dst)
    else:
        print(f"  WARNING: {md_src} not found — skipping markdown copy")

    # -----------------------------------------------------------------------
    # Git commands
    # -----------------------------------------------------------------------
    today = date.today()
    tag = f"docs-{ename}-{today.strftime('%Y.%m')}.000"

    added_files = [f"notebooks/{nb}.ipynb" for nb in ok_nbs]
    if md_src.exists():
        added_files.append("documentation/docs/pages/index.md")

    print()
    print("Run from the repo root to commit and tag:")
    print()
    print(f"  git add {' '.join(added_files)}")
    print(f'  git commit -m "docs: render evaluation figures for {ename}"')
    print(f"  git tag {tag}")
    print( "  git push origin main --tags")
    print()


if __name__ == "__main__":
    main()
