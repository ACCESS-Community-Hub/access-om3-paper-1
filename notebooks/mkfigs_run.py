#!/usr/bin/env python3
"""
mkfigs_run.py – run evaluation notebooks and convert to markdown.

Called by mkfigs.sh after modules are loaded. Receives ENAME, ESMDIR and
WFOLDER as command-line arguments.

Usage (via mkfigs.sh):
    qsub mkfigs.sh
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent   # notebooks/
REPO = HERE.parent                       # repo root

# Notebook list is defined in mkfigs.sh (array=(...)) and passed via MKFIGS_NOTEBOOKS env var.


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--ename",   required=True, help="Experiment name (ENAME)")
    p.add_argument("--esmdir",  required=True, help="Path to ESM datastore JSON")
    p.add_argument("--wfolder", required=True, help="Repo root folder")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Logging: stdout + mkmd/mkfigs_run.log
# ---------------------------------------------------------------------------
def setup_logging(log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    fmt = "%(asctime)s %(levelname)-8s %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file)),
        ],
    )
    return logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Notebook execution
# ---------------------------------------------------------------------------
def run_notebook(nb: str, esmdir: str, ofol: Path) -> bool:
    """Strip outputs, run via papermill, convert to markdown. Returns True on success."""
    # Strip existing outputs before papermill run
    subprocess.run(
        ["python3", str(HERE / "run_nb.py"), f"{nb}.ipynb"],
        cwd=str(HERE), check=False,
    )
    rendered = str(ofol / f"{nb}_rendered.ipynb")
    result = subprocess.run(
        [
            "papermill", f"{nb}.ipynb", rendered,
            "-p", "esm_file", esmdir,
            "-p", "papermill", "True",
            "-p", "cwd", str(ofol) + "/",
            "-p", "nbname", f"{nb}.ipynb",
        ],
        cwd=str(HERE),
    )
    # Always convert to markdown for diagnostics, even on failure
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "markdown", rendered],
        check=False,
    )
    if result.returncode == 0:
        subprocess.run(
            ["jupyter", "nbconvert", "--clear-output", "--to", "notebook",
             "--inplace", rendered],
            check=False,
        )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args = parse_args()

    ename   = args.ename
    esmdir  = args.esmdir

    ofol  = HERE / f"mkfigs_output_{ename}"
    mdfol = ofol / "mkmd"
    mdfol.mkdir(parents=True, exist_ok=True)

    log = setup_logging(mdfol / "mkfigs_run.log")

    log.info("Experiment : %s", ename)
    log.info("ESMDIR     : %s", esmdir)
    log.info("Output dir : %s", ofol)
    log.info("Log file   : %s", mdfol / "mkfigs_run.log")

    # -----------------------------------------------------------------------
    # Notebook execution
    # -----------------------------------------------------------------------
    notebooks_env = os.environ.get("MKFIGS_NOTEBOOKS", "")
    if not notebooks_env:
        sys.exit("ERROR: MKFIGS_NOTEBOOKS not set — run via mkfigs.sh")
    notebooks = notebooks_env.split(":")

    succeeded: list[str] = []
    failed:    list[str] = []

    log.info("")
    log.info("Running %d notebooks ...", len(notebooks))
    log.info("")
    for nb in notebooks:
        log.info("START  %s", nb)
        ok = run_notebook(nb, esmdir, ofol)
        if ok:
            succeeded.append(nb)
            log.info("OK     %s", nb)
        else:
            failed.append(nb)
            log.error("FAILED %s", nb)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    log.info("")
    log.info("=" * 56)
    log.info("Run complete")
    log.info("=" * 56)
    log.info("Output folder : %s", ofol)
    log.info("Markdown dir  : %s", mdfol)
    log.info("Log file      : %s", mdfol / "mkfigs_run.log")

    if succeeded:
        log.info("Succeeded (%d): %s", len(succeeded), ", ".join(succeeded))
    if failed:
        log.error("FAILED    (%d): %s", len(failed), ", ".join(failed))
        log.error("Check the PBS error log and rendered notebooks for details.")

    print()
    print("Next step – check results, upload to Figshare, and prepare the git commit:")
    print(f"  python3 {HERE / 'mkfigs_pushit.py'}")
    print()


if __name__ == "__main__":
    main()
