#!/usr/bin/env python3
"""
check_mkfigs_issues.py

Pre-flight check to run *before* submitting notebooks/mkfigs.sh.

Cross-references the notebook `array=(...)` in mkfigs.sh against:
  1. mkfigs_issues.py's ISSUES dict, so nothing silently renders an
     empty "GitHub Issue(s)" cell on the docs site.
  2. The actual .ipynb files on disk, to catch naming bugs (e.g. an
     array entry accidentally including ".ipynb", which breaks
     mkfigs-run's path building and crashes the whole batch job).

It also prints, for every active notebook, exactly what
mkfigs_issues.py currently has on file for it — formatted so the
GitHub issue link(s) are easy to spot and copy, without having to go
open mkfigs_issues.py yourself. A green checkmark or red cross next
to each entry shows at a glance whether it's linked or missing.

Usage — run this from *inside* the notebooks/ directory itself
(where mkfigs.sh and mkfigs_issues.py actually live):

    cd notebooks
    python check_mkfigs_issues.py

You can still point it at a different directory if needed, e.g.:

    python check_mkfigs_issues.py /g/data/tm70/cyb561/repos/access-om3-paper-test/notebooks

Note: mkfigs_issues.py's ISSUES dict is defined using an f-string (it
interpolates a shared `_GH` base-URL variable), so this script loads
it as a real Python module rather than statically parsing it — this
is what fully resolves each value to its final displayable string.
mkfigs_issues.py is a small, trusted, team-maintained config file
(not user/network input), so this is expected to be safe; if you ever
point this script at an untrusted copy of the file, be aware its
top-level code will execute.

Exit code 0 if everything checks out, 1 if any problems were found
(so this can be dropped into a pre-submit alias/hook and it'll block
a bad submission).
"""

from __future__ import annotations

import difflib
import importlib.util
import re
import sys
from pathlib import Path

# ANSI colour codes, only applied when stdout is a real terminal —
# otherwise (e.g. output redirected to a log file) codes are left out
# so logs stay clean and grep-able rather than filling with escape chars.
_USE_COLOUR = sys.stdout.isatty()
_RED = "\033[91m" if _USE_COLOUR else ""
_GREEN = "\033[92m" if _USE_COLOUR else ""
_RESET = "\033[0m" if _USE_COLOUR else ""


def _emoji_supported() -> bool:
    """Best-effort check for whether stdout can actually display emoji.

    Some terminals (e.g. minimal/default terminal emulators in VM setups,
    or a non-UTF-8 locale) can't render "✅"/"❌" and instead show a blank,
    a box, or drop the character entirely — the byte stream is correct,
    there's just no glyph or encoding support on the receiving end. This
    checks whether stdout's encoding can even represent the characters;
    if not, plain ASCII markers are used instead so the output is always
    readable regardless of terminal/font/locale.
    """
    encoding = sys.stdout.encoding or "utf-8"
    try:
        "✅❌".encode(encoding)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


if _emoji_supported():
    CROSS = f"{_RED}❌{_RESET}"
    TICK = f"{_GREEN}✅{_RESET}"
else:
    CROSS = f"{_RED}[FAIL]{_RESET}"
    TICK = f"{_GREEN}[ OK ]{_RESET}"


def parse_mkfigs_array(mkfigs_sh: Path) -> tuple[list[str], list[str]]:
    """Extract the notebook array from mkfigs.sh.

    Reads the `array=( ... )` block in mkfigs.sh and splits its lines
    into two lists: notebooks that are actively enabled (uncommented),
    and notebooks that are present but commented out.

    Handles inline trailing comments (e.g. "SeaIce_area  # active for
    now") and multiple leading '#'s (e.g. "##   Foo"). Entries are
    returned as bare notebook stems, e.g. "SeaIce_area" (no .ipynb).

    Raises ValueError if no array=( ... ) block is found.
    """
    text = mkfigs_sh.read_text()

    match = re.search(r"^array=\(\s*\n(.*?)\n\)", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"Could not find an 'array=( ... )' block in {mkfigs_sh}")

    block = match.group(1)

    active: list[str] = []
    commented: list[str] = []

    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        is_commented = line.startswith("#")
        stripped = line.lstrip("#").strip()
        stripped = stripped.split("#", 1)[0].strip()  # drop inline trailing comments

        if not stripped:
            continue

        if is_commented:
            commented.append(stripped)
        else:
            active.append(stripped)

    return active, commented


def load_issues_dict(mkfigs_issues_py: Path) -> dict[str, str]:
    """Load the real, fully-resolved ISSUES dict from mkfigs_issues.py.

    Imports mkfigs_issues.py as a Python module (rather than statically
    parsing its source) so that its f-string values — which interpolate
    a shared `_GH` base-URL variable — come back as their final,
    human-readable strings (e.g. "[#15](https://.../15) Regional SLA...")
    instead of raw, unresolved source text.

    Raises ValueError if the module has no top-level ISSUES dict.
    """
    spec = importlib.util.spec_from_file_location("mkfigs_issues", mkfigs_issues_py)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    issues = getattr(module, "ISSUES", None)
    if not isinstance(issues, dict):
        raise ValueError(f"No top-level ISSUES dict found in {mkfigs_issues_py}")

    return issues


def print_issue_report(active: list[str], issues: dict[str, str]) -> None:
    """Print a readable, copy-pasteable summary of mkfigs_issues.py's entry for each active notebook.

    For every notebook currently active in mkfigs.sh's array, shows:
      - a green tick or red cross next to the notebook name, depending
        on whether it has an ISSUES entry at all,
      - the exact value stored in ISSUES (as it would render on the
        docs site), or a clear "(no entry)" marker if missing.
    The value already contains full "[#N](https://...)" markdown
    links, so the URLs are directly copyable from that line as-is.
    """
    print("== mkfigs_issues.py entries for active notebooks ==")
    for entry in active:
        value = issues.get(entry)
        marker = TICK if value is not None else CROSS
        print(f"\n{marker} {entry}")
        print(f"  {value}" if value is not None else "  (no entry in ISSUES)")
    print()


def check(notebooks_dir: Path) -> bool:
    """Run all checks against a notebooks/ directory and print the results.

    Loads mkfigs.sh's array and mkfigs_issues.py's ISSUES dict, then:
      1. prints the readable issue-link report for every active notebook,
      2. verifies every active notebook resolves to a real .ipynb file
         on disk (catching things like an accidental ".ipynb" suffix
         in the array),
      3. verifies every active notebook has a matching ISSUES entry,
         suggesting a likely typo/rename target via fuzzy matching
         when one is missing,
      4. lists (informationally, non-blocking) any commented-out
         entries that are also missing an ISSUES entry.

    Every failure is printed with a red cross, every pass with a
    green tick, so the overall result is scannable at a glance.

    Returns True if no problems were found, False otherwise.
    """
    mkfigs_sh = notebooks_dir / "mkfigs.sh"
    mkfigs_issues_py = notebooks_dir / "mkfigs_issues.py"

    for required in (mkfigs_sh, mkfigs_issues_py):
        if not required.exists():
            print(f"{CROSS} ERROR: expected file not found: {required}")
            return False

    active, commented = parse_mkfigs_array(mkfigs_sh)
    issues = load_issues_dict(mkfigs_issues_py)

    problems_found = False

    print(f"Checked array in {mkfigs_sh}")
    print(f"  {len(active)} active entr{'y' if len(active) == 1 else 'ies'}, "
          f"{len(commented)} commented out\n")

    print_issue_report(active, issues)

    # --- Check 1: does the notebook file actually exist? ---
    print("== Checking notebook files exist on disk ==")
    file_problems = False
    for entry in active:
        if entry.endswith(".ipynb"):
            print(f"  {CROSS} {entry!r} includes a '.ipynb' suffix in the array — "
                  f"this will break mkfigs-run's path building "
                  f"(expected bare stem, e.g. {entry[:-6]!r}).")
            file_problems = True
            continue

        nb_path = notebooks_dir / f"{entry}.ipynb"
        if not nb_path.exists():
            print(f"  {CROSS} {entry!r}: no such file {nb_path}")
            file_problems = True

    if file_problems:
        problems_found = True
    else:
        print(f"  {TICK} all active entries resolve to real .ipynb files.")
    print()

    # --- Check 2: does each active entry have an ISSUES entry? ---
    print("== Checking active notebooks are linked in mkfigs_issues.py ==")
    missing_or_mismatched = False
    for entry in active:
        if entry in issues:
            continue

        missing_or_mismatched = True
        problems_found = True

        close = difflib.get_close_matches(entry, issues.keys(), n=1, cutoff=0.6)
        if close:
            print(f"  {CROSS} {entry!r} has no ISSUES entry — did you mean the existing "
                  f"key {close[0]!r}? (possible rename/typo drift)")
        else:
            print(f"  {CROSS} {entry!r} has no ISSUES entry at all — add one to "
                  f"{mkfigs_issues_py.name}.")

    if not missing_or_mismatched:
        print(f"  {TICK} every active notebook has a matching ISSUES entry.")
    print()

    # --- Informational: commented-out entries missing issues too ---
    commented_missing = [e for e in commented if e not in issues and not e.endswith(".ipynb")]
    if commented_missing:
        print("== FYI: commented-out entries with no ISSUES entry (not blocking) ==")
        for entry in commented_missing:
            print(f"  - {entry!r}")
        print()

    if problems_found:
        print(f"{CROSS} RESULT: problems found — fix before submitting mkfigs.sh.")
    else:
        print(f"{TICK} RESULT: all clear.")

    return not problems_found


def main() -> int:
    """CLI entry point.

    Defaults to checking the current directory, since this script is
    meant to be run from inside notebooks/ itself (where mkfigs.sh and
    mkfigs_issues.py live). Pass a path as argv[1] to point it
    elsewhere instead, e.g. at a different working copy on Gadi.
    """
    notebooks_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    ok = check(notebooks_dir)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
