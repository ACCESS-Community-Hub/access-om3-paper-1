#!/usr/bin/env python3
"""
mkfigs_pushit.py – check mkfigs.sh results, upload figures and rendered
notebooks to Figshare, copy per-notebook markdown files into the docs tree,
update mkdocs.yml nav, and print the git commands needed to commit everything.

Run interactively on a login node (not via qsub — compute nodes have no
internet access) after mkfigs.sh completes:

    cd /g/data/tm70/cyb561/repos/access-om3-paper-1/notebooks
    python3 mkfigs_pushit.py
    python3 mkfigs_pushit.py --dry-run               # preview: nothing written or uploaded
    python3 mkfigs_pushit.py --skip-figshare         # copy files, but skip upload
    python3 mkfigs_pushit.py --ename MC_25km_...     # override experiment name
    python3 mkfigs_pushit.py --check-figshare-upload # verify URLs public, print git commands

Suggested workflow:
  1. python3 mkfigs_pushit.py               — upload to Figshare, copy docs files
  2. Publish the Figshare article
  3. python3 mkfigs_pushit.py --check-figshare-upload  — verify URLs, get git commands

Figshare token: set FIGSHARE_TOKEN env var, or store in ~/.figshare_token.
"""

from __future__ import annotations

#not technically needed here but we've put it in because it is in mkfigs_run.py
try:
    import nci_ipynb  # noqa: F401  – only present under conda/analysis3
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
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, date, timezone
from pathlib import Path

import yaml  # PyYAML – available in conda/analysis3
from mkfigs_configdoc import NOTEBOOK_ISSUES

HERE = Path(__file__).resolve().parent   # notebooks/
REPO = HERE.parent                       # repo root
DOCS_PAGES = REPO / "documentation" / "docs" / "pages"
MKDOCS_YML = REPO / "documentation" / "mkdocs.yml"



# ---------------------------------------------------------------------------
# Parse mkfigs.sh to get ENAME, ESMDIR, and notebook list
# ---------------------------------------------------------------------------
def parse_mkfigs_sh() -> tuple[str, str, list[str]]:
    sh = HERE / "mkfigs.sh"
    text = sh.read_text()

    ename  = None
    esmdir = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = re.match(r'^ENAME=([^\s#]+)', stripped)
        if m:
            ename = m.group(1)
        m = re.match(r'^ESMDIR=([^\s#]+)', stripped)
        if m:
            esmdir = m.group(1)

    if not ename:
        sys.exit("ERROR: could not find ENAME in mkfigs.sh")

    m = re.search(r'array=\(([^)]*)\)', text, re.DOTALL)
    if not m:
        sys.exit("ERROR: could not find array=(...) in mkfigs.sh")
    notebooks = []
    for line in m.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        notebooks.append(stripped)

    return ename, esmdir or "(unknown)", notebooks


# ---------------------------------------------------------------------------
# Author list from CITATION.cff
# ---------------------------------------------------------------------------
def get_authors_md() -> str:
    """Return a markdown attribution string from CITATION.cff, or ''."""
    cff = REPO / "CITATION.cff"
    try:
        lines = cff.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return ""

    given = None
    family = None
    coauthors = []
    for line in lines:
        line = line.strip()
        if "given-names:" in line:
            given = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("family-names:"):
            family = line.split(":", 1)[1].strip().strip('"')
        if given and family:
            coauthors.append(f"{family}, {given}")
            given = None
            family = None

    if not coauthors:
        return ""
    return (
        "**authors (alphabetically):** "
        + "; ".join(sorted(coauthors))
        + "."
    )


# ---------------------------------------------------------------------------
# Run-summary builder (shared between stdout and index.md)
# ---------------------------------------------------------------------------
def build_run_summary(
    ename: str,
    esmdir: str,
    ok_nbs: list[str],
    failed_nbs: list[str],
    not_run_nbs: list[str],
    prev_committed_nbs: list[str],
    run_time: datetime,
) -> tuple[str, str]:
    """Return (plain_text_summary, markdown_summary).

    Both contain the same information; the markdown version uses a table and
    bullet list suitable for embedding directly in pages/index.md.
    """
    ts = run_time.strftime("%Y-%m-%d %H:%M UTC")

    # Plain text for stdout
    rows = (
        [f"  OK                  {nb}" for nb in ok_nbs]
        + [f"  FAILED             {nb}" for nb in failed_nbs]
        + [f"  NOT RUN            {nb}" for nb in not_run_nbs]
        + [f"  PREV COMMITTED     {nb}" for nb in prev_committed_nbs]
    )
    plain = "\n".join([
        f"  Experiment      : {ename}",
        f"  ESMDIR          : {esmdir}",
        f"  Run time        : {ts}",
        f"  OK: {len(ok_nbs)}   FAILED: {len(failed_nbs)}   NOT RUN: {len(not_run_nbs)}   PREV COMMITTED: {len(prev_committed_nbs)}",
        "",
    ] + rows)

    # Markdown for pages/index.md — links included in table so no separate Sections block needed
    exp_dir = f"experiments/{ename}"
    md_rows = (
        [f"| `{nb}` | ✅ OK | {NOTEBOOK_ISSUES.get(nb, '')} | [Summary Figures]({exp_dir}/{nb}.md) · [Full Notebook]({exp_dir}/notebooks/{nb}/) |"
         for nb in ok_nbs]
        + [f"| `{nb}` | ❌ FAILED | {NOTEBOOK_ISSUES.get(nb, '')} | |"  for nb in failed_nbs]
        + [f"| `{nb}` | ⏭ NOT RUN | {NOTEBOOK_ISSUES.get(nb, '')} | |" for nb in not_run_nbs]
        + [f"| `{nb}` | ✅ Previously committed | {NOTEBOOK_ISSUES.get(nb, '')} | [Summary Figures]({exp_dir}/{nb}.md) · [Full Notebook]({exp_dir}/notebooks/{nb}/) |"
           for nb in prev_committed_nbs]
    )
    md = (
        "| Notebook | Status | GitHub Issue(s) | Links |\n"
        "|---|---|---|---|\n"
        + "\n".join(md_rows)
        + f"\n\n- **ESM datastore:** `{esmdir}`\n"
        f"- **Run time:** {ts}\n"
    )

    return plain, md


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
# Figshare upload (per notebook: PNGs + rendered notebook with outputs)
# ---------------------------------------------------------------------------
def upload_figshare_for_notebook(
    mdfol: Path, ofol: Path, ename: str, nb_name: str, token: str
) -> str | None:
    """Upload PNGs + the fully rendered notebook for *nb_name* to figshare.

    The rendered notebook (``<ofol>/<nb_name>_rendered.ipynb``) still has its
    cell outputs intact at this point — mkfigs_run.py strips them only for the
    copy that goes back into ``notebooks/``.  We upload the output-bearing copy
    so ReadTheDocs can download and display it via mkdocs-jupyter without
    needing to re-execute anything on the build server.

    Returns the figshare download URL for the notebook, or None on failure.
    """
    sys.path.insert(0, str(HERE))
    try:
        from mkfigs_configdoc import figshare_upload_and_rewrite
    except ImportError as exc:
        print(f"[figshare] ERROR: could not import mkfigs_configdoc: {exc}")
        return None

    nb_path = ofol / f"{nb_name}_rendered.ipynb"
    if not nb_path.exists():
        print(f"[figshare] WARNING: rendered notebook not found: {nb_path}")
        nb_path = None

    print()
    print("=" * 56)
    print(f"Uploading to Figshare: {nb_name}")
    print(f"  Experiment : {ename}")
    print(f"  Source dir : {mdfol}")
    if nb_path:
        print(f"  Notebook   : {nb_path.name}")
    print("=" * 56)

    try:
        url_map = figshare_upload_and_rewrite(
            mdfol=str(mdfol),
            experiment=ename,
            token=token,
            nb_name=nb_name,
            nb_path=str(nb_path) if nb_path else None,
        )
    except Exception as exc:
        print(f"[figshare] ERROR: upload raised an exception: {exc}")
        return None

    if url_map:
        print("[figshare] Upload summary:")
        for fname, url in sorted(url_map.items()):
            if not fname.startswith("_"):
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

    return url_map.get("_notebook")


# ---------------------------------------------------------------------------
# Figshare URL accessibility check  (--check-figshare-upload mode)
# ---------------------------------------------------------------------------
def _check_figshare_urls(all_urls: dict[str, str]) -> bool:
    """Return True if every Figshare URL responds with HTTP 200/206.

    A 403 means the article has not been published yet.  Uses a Range request
    so the full file is not downloaded.
    """
    import urllib.request
    import urllib.error

    all_ok = True
    for label, url in all_urls.items():
        try:
            req = urllib.request.Request(url, headers={"Range": "bytes=0-99"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                ok = resp.status in (200, 206)
        except urllib.error.HTTPError as exc:
            ok = exc.code in (200, 206)
        except Exception:
            ok = False
        mark = "✓" if ok else "✗  NOT ACCESSIBLE"
        print(f"  {mark}  {label}")
        if not ok:
            all_ok = False
    return all_ok


def check_figshare_upload_mode(ename: str) -> None:
    """--check-figshare-upload: verify all Figshare URLs then print git commands.

    Run this after publishing the Figshare article.  Reads notebook URLs from
    notebooks_urls.json and image URLs embedded in the per-notebook .md files,
    checks every URL is publicly accessible, and only then prints the full git
    commit/tag/push commands needed to finish the workflow.
    """
    experiment_docs_dir = DOCS_PAGES / "experiments" / ename
    all_urls: dict[str, str] = {}
    seen: set[str] = set()

    def _add(label: str, url: str) -> None:
        if url not in seen:
            seen.add(url)
            all_urls[label] = url

    urls_json = experiment_docs_dir / "notebooks_urls.json"
    if urls_json.exists():
        for nb_name, url in json.loads(urls_json.read_text()).items():
            _add(f"notebook  {nb_name}", url)
    else:
        print(f"WARNING: {urls_json} not found — run mkfigs_pushit.py first.")

    for md_file in sorted(experiment_docs_dir.glob("*.md")):
        for url in re.findall(
            r'https://ndownloader\.figshare\.com/files/\d+', md_file.read_text()
        ):
            file_id = url.rsplit("/", 1)[-1]
            _add(f"image     {md_file.stem}/{file_id}", url)

    if not all_urls:
        print("No Figshare URLs found. Run mkfigs_pushit.py first.")
        sys.exit(1)

    print(f"\nChecking {len(all_urls)} Figshare URL(s) for {ename}...\n")
    all_ok = _check_figshare_urls(all_urls)

    if not all_ok:
        print("\n*** Some URLs are not accessible — is the Figshare article published? ***")
        print("Publish it, then re-run:")
        print("  python3 mkfigs_pushit.py --check-figshare-upload")
        sys.exit(1)

    print("\nAll Figshare URLs are publicly accessible.\n")

    # Reconstruct the git commands.
    _, esmdir, notebooks = parse_mkfigs_sh()
    ofol = HERE / f"mkfigs_output_{ename}"
    ok_nbs = [
        nb for nb in notebooks
        if (ofol / f"{nb}_rendered.ipynb").exists()
        and (experiment_docs_dir / f"{nb}.md").exists()
    ]

    today = date.today()
    tag = f"docs-{ename}-{today.strftime('%Y.%m')}.000"
    rtd_slug = re.sub(r'[^a-z0-9-]+', '-', tag.lower()).strip('-')
    rtd_url  = f"https://access-om3-paper-1.readthedocs.io/en/{rtd_slug}/"
    tag_msg  = f"Evaluation figures for {ename}. Rendered site (after RTD builds tag): {rtd_url}"

    urls_json_rel = f"documentation/docs/pages/experiments/{ename}/notebooks_urls.json"
    added_files = [f"notebooks/{nb}.ipynb" for nb in ok_nbs]
    added_files += [
        str((experiment_docs_dir / f"{nb}.md").relative_to(REPO))
        for nb in ok_nbs
        if (experiment_docs_dir / f"{nb}.md").exists()
    ]
    added_files += [
        urls_json_rel,
        "documentation/docs/pages/index.md",
        "documentation/mkdocs.yml",
        ".readthedocs.yaml",
    ]

    print("Run the following to commit, tag, and push:\n")
    print(f"  cd {REPO}")
    print(f"  git add {' '.join(added_files)}")
    print( "  #")
    print( "  #  Recommended that you -- git add mkfigs.sh too")
    print( "  #")
    print(f'  git commit -m "docs: render evaluation figures for {ename}"')
    print(f"  git tag -a {tag} -m '{tag_msg}'")
    print( "  git push origin main --tags")
    print( "  git push")
    print( "\n  Horray!")
    print()


# ---------------------------------------------------------------------------
# mkdocs.yml helpers
# ---------------------------------------------------------------------------

class _YamlPythonTag:
    """Preserves !!python/name: (and similar) tags through a load→dump round-trip.

    yaml.SafeLoader strips these tags; we capture them as this placeholder so
    that _save_mkdocs_yml can re-emit the original !!python/name:... form.
    Without this, tags like !!python/name:material.extensions.emoji.twemoji
    silently become '' and break pymdownx.emoji at build time.
    """
    def __init__(self, tag: str, value: str) -> None:
        self.tag = tag    # full canonical tag, e.g. tag:yaml.org,2002:python/name:foo
        self.value = value


def _load_mkdocs_yml() -> dict:
    # mkdocs.yml uses:
    #   !ENV [VAR, default]          – resolve to env var value or default
    #   !!python/name:some.module    – preserve as _YamlPythonTag (re-emitted on save)
    def _tag_constructor(loader, tag, node):
        import os as _os
        # Preserve !!python/name: and similar Python-object tags so _save_mkdocs_yml
        # can emit them back unchanged (otherwise they silently become '').
        if "python/" in tag:
            scalar = loader.construct_scalar(node) if isinstance(node, yaml.ScalarNode) else ""
            return _YamlPythonTag(tag, scalar)
        # !ENV scalar or !ENV [VAR, default] sequence
        if isinstance(node, yaml.ScalarNode):
            return _os.environ.get(loader.construct_scalar(node), "")
        items = loader.construct_sequence(node)
        var = items[0] if items else ""
        default = items[1] if len(items) > 1 else ""
        return _os.environ.get(str(var), str(default))

    class _PermissiveLoader(yaml.SafeLoader):
        pass
    _PermissiveLoader.add_multi_constructor("", _tag_constructor)
    with open(MKDOCS_YML) as f:
        return yaml.load(f, Loader=_PermissiveLoader)


def _save_mkdocs_yml(data: dict) -> None:
    """Surgically replace only the nav: block in mkdocs.yml.

    A full PyYAML round-trip strips all comments and resolves special tags
    like !ENV (e.g. !ENV [SITE_URL, "..."] becomes a plain string),
    permanently altering the file.  We serialise only the nav list and
    splice it back into the original text so everything else is preserved.

    Note: if _ensure_mkdocs_jupyter_plugin made a change to data["plugins"],
    that change is NOT written by this function.  The plugin is expected to
    already be present in mkdocs.yml; add it manually if starting fresh.
    """
    nav_yaml = yaml.dump(
        {"nav": data["nav"]},
        Dumper=yaml.SafeDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    original = MKDOCS_YML.read_text()
    # Match the nav: block — "nav:" followed by all indented/dash/blank lines.
    nav_re = re.compile(r'^nav:\n(?:[ \t-][^\n]*\n|\n)*', re.MULTILINE)
    m = nav_re.search(original)
    if m:
        tail = original[m.end():]
        sep = '' if tail.startswith('\n') else '\n'
        MKDOCS_YML.write_text(original[:m.start()] + nav_yaml + sep + tail)
    else:
        MKDOCS_YML.write_text(original.rstrip('\n') + '\n\n' + nav_yaml)


def _ensure_mkdocs_jupyter_plugin(data: dict) -> dict:
    """Add mkdocs-jupyter to the plugins list if not already present."""
    plugins = data.get("plugins", [])
    has_jupyter = any(
        (isinstance(p, str) and p == "mkdocs-jupyter")
        or (isinstance(p, dict) and "mkdocs-jupyter" in p)
        for p in plugins
    )
    if not has_jupyter:
        plugins.append({
            "mkdocs-jupyter": {
                "execute": False,         # use pre-rendered outputs; don't re-run
                "include_source": True,   # show source code alongside outputs
                "ignore_h1_titles": True,
                # PurePath.match checks abs_src_path, so leading path components
                # like "pages/experiments/" fail on absolute paths in Python 3.12.
                "include": ["**/*.ipynb"],
            }
        })
        data["plugins"] = plugins
        print("[mkdocs] Added mkdocs-jupyter plugin config")
    return data


def update_mkdocs_nav(ename: str, ok_nbs: list[str], dry_run: bool = False) -> None:
    """Add (or replace) per-notebook nav entries in mkdocs.yml.

    Each notebook gets a top-level entry with summary and notebook sub-pages:

      - <nb>:
          - summary:  pages/experiments/<ename>/<nb>.md
          - notebook: pages/experiments/<ename>/notebooks/<nb>.ipynb

    Notebooks live in a notebooks/ subdirectory to avoid URL collision with the
    summary .md (the hide_pages hook strips 'pages/' from both, so same-stem
    files in the same dir would resolve to the same URL).

    Existing entries for the same notebook name are replaced in-place.
    The mkdocs-jupyter plugin is injected into the plugins list if absent.
    """
    data = _load_mkdocs_yml()
    data = _ensure_mkdocs_jupyter_plugin(data)
    nav = data.get("nav", [])

    exp_dir = f"pages/experiments/{ename}"

    def _is_experiment_entry(item: dict) -> bool:
        """True for old-style 'Evaluation figures' sections and per-notebook entries
        whose paths belong to pages/experiments/ (from any previous run)."""
        if "Evaluation figures" in item:
            return True
        for sub in item.values():
            if isinstance(sub, list):
                for child in sub:
                    if isinstance(child, dict):
                        for v in child.values():
                            if isinstance(v, str) and "pages/experiments/" in v:
                                return True
        return False

    # Remove all stale experiment entries (old structure or previous runs).
    nav = [item for item in nav if not (isinstance(item, dict) and _is_experiment_entry(item))]

    # Append fresh entries in notebook order.
    for nb in ok_nbs:
        nav.append({nb: [
            {"Summary":  f"{exp_dir}/{nb}.md"},
            {"Notebook": f"{exp_dir}/notebooks/{nb}.ipynb"},
        ]})

    data["nav"] = nav

    if dry_run:
        print(f"[mkdocs] DRY RUN: would update nav in {MKDOCS_YML}")
        print(f"[mkdocs] Would add/replace entries for: {ok_nbs}")
    else:
        _save_mkdocs_yml(data)
        print(f"[mkdocs] Updated nav in {MKDOCS_YML}")
        print(f"[mkdocs] {len(ok_nbs)} notebook(s) added/updated in nav")


# ---------------------------------------------------------------------------
# Top-level pages/index.md update
# ---------------------------------------------------------------------------

def update_top_index(
    ename: str,
    ok_nbs: list[str],
    failed_nbs: list[str],
    not_run_nbs: list[str],
    run_summary_md: str,
    authors_md: str,
    dry_run: bool = False,
) -> None:
    """Append or replace an experiment block in the top-level pages/index.md.

    Each block contains everything a reader needs for an experiment: the author
    list, run summary table, and links to every section page.  There is no
    separate per-experiment index page.

    Blocks are delimited by HTML comments so re-runs update in-place without
    creating duplicates.
    """
    top_index = DOCS_PAGES / "index.md"
    top_index.parent.mkdir(parents=True, exist_ok=True)

    preamble = (
        f"# ACCESS-OM3 Evaluation Figures: {ename}\n\n"
        "Diagnostic figures from ACCESS-OM3 experiments, generated by the\n"
        "[access-om3-paper-1](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/)\n"
        f"analysis notebooks for {ename}. See navigation on the left to browse diagnostics as"
        " delineated by notebook. The website is intended to help users discover and"
        " compare diagnostics. All discussion of the diagnostics occurs on GitHub issues"
        " (see links in Figure captions).\n\n"
        + (f"`ACCESS-community-Hub/access-om3-paper-1/` {authors_md}\n\n" if authors_md else "")
        + "<!-- experiments -->\n"
    )

    # Always refresh the canonical preamble; preserve only the experiment blocks
    # that follow the <!-- experiments --> anchor.
    anchor = "<!-- experiments -->"
    if top_index.exists():
        old = top_index.read_text()
        after = old[old.index(anchor) + len(anchor):] if anchor in old else ""
    else:
        after = ""
    content = preamble + after

    incomplete_block = ""
    if failed_nbs or not_run_nbs:
        incomplete_block = "\n#### Incomplete notebooks\n\n"
        incomplete_block += "\n".join(
            f"- `{nb}` — **failed**" for nb in failed_nbs
        )
        if failed_nbs and not_run_nbs:
            incomplete_block += "\n"
        incomplete_block += "\n".join(
            f"- `{nb}` — **not run**" for nb in not_run_nbs
        )
        incomplete_block += "\n"

    block_start = f"<!-- experiment:{ename} -->"
    block_end   = f"<!-- /experiment:{ename} -->"
    block = (
        f"{block_start}\n\n"
        f"## Analysis run summary {ename}\n\n"
        + run_summary_md + "\n"
        + incomplete_block
        + f"{block_end}\n"
    )

    # Wipe all existing experiment blocks so a new ENAME doesn't accumulate
    # alongside old ones (mirrors update_mkdocs_nav which also resets all entries).
    content = re.sub(
        r"\n*<!-- experiment:[^>]+ -->.*?<!-- /experiment:[^>]+ -->\n?",
        "",
        content,
        flags=re.DOTALL,
    )

    if "<!-- experiments -->" in content:
        content = content.replace("<!-- experiments -->", f"<!-- experiments -->\n\n{block}")
    else:
        content = content.rstrip("\n") + f"\n\n{block}"

    if dry_run:
        print(f"[top-index] DRY RUN: would update {top_index} for {ename}")
    else:
        top_index.write_text(content)
        print(f"[top-index] Updated {top_index} for experiment {ename}")


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
    p.add_argument("--check-figshare-upload", action="store_true",
                   help="Verify all Figshare URLs are public, then print git commands")
    args = p.parse_args()

    ename, esmdir, notebooks = parse_mkfigs_sh()
    if args.ename:
        ename = args.ename

    if args.check_figshare_upload:
        check_figshare_upload_mode(ename)
        return

    ofol  = HERE / f"mkfigs_output_{ename}"
    mdfol = ofol / "mkmd"
    run_time = datetime.now(timezone.utc)

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
        pngs     = list(mdfol.glob(f"{nb}_*.png")) if mdfol.exists() else []
        nb_md    = mdfol / f"{nb}.md"
        if not rendered.exists():
            not_run_nbs.append(nb)
            status = "NOT RUN"
        elif not pngs and not nb_md.exists():
            failed_nbs.append(nb)
            status = "FAILED  (no PNGs or markdown)"
        else:
            ok_nbs.append(nb)
            n_png = len(pngs)
            status = f"OK      ({n_png} PNG{'s' if n_png != 1 else ''})"
        print(f"  {status:<34}  {nb}")

    # Load previously committed notebook URLs to merge with this run's results.
    experiment_docs_dir = DOCS_PAGES / "experiments" / ename
    urls_json_path = experiment_docs_dir / "notebooks_urls.json"
    urls_json_rel  = f"documentation/docs/pages/experiments/{ename}/notebooks_urls.json"
    existing_urls: dict[str, str] = {}
    if not args.dry_run and urls_json_path.exists():
        try:
            existing_urls = json.loads(urls_json_path.read_text())
        except Exception as exc:
            print(f"WARNING: could not read existing {urls_json_path}: {exc}")
    # Notebooks committed in a previous run not being re-run (or replaced) now.
    prev_committed_nbs = [nb for nb in existing_urls if nb not in ok_nbs]

    print()
    plain_summary, md_summary = build_run_summary(
        ename, esmdir, ok_nbs, failed_nbs, not_run_nbs, prev_committed_nbs, run_time
    )
    print(plain_summary)

    if not ok_nbs and not prev_committed_nbs:
        print("No successful or previously committed notebooks — nothing to push.")
        return

    authors_md = get_authors_md()

    # -----------------------------------------------------------------------
    # Figshare upload (per-notebook: PNGs + rendered notebook with outputs)
    # -----------------------------------------------------------------------
    # notebook_urls maps nb_name -> figshare download URL for the .ipynb file.
    # Written to notebooks_urls.json; consumed by .readthedocs.yaml pre_build.
    notebook_urls: dict[str, str] = {}

    if args.dry_run:
        print(f"[figshare] DRY RUN: would upload PNGs + rendered notebooks from {mdfol} / {ofol}")
    elif args.skip_figshare:
        print("[figshare] Upload skipped (--skip-figshare).")
    else:
        token = resolve_figshare_token()
        if token:
            for nb in ok_nbs:
                nb_url = upload_figshare_for_notebook(mdfol, ofol, ename, nb, token)
                if nb_url:
                    notebook_urls[nb] = nb_url
        else:
            print("[figshare] No token found — skipping upload.")
            print("           Set FIGSHARE_TOKEN or store token in ~/.figshare_token")

    # Merge: new-run URLs take priority over previously committed.
    all_notebook_urls = {**existing_urls, **notebook_urls}
    # Nav includes all notebooks with valid URLs, except those that failed this run.
    failed_set = set(failed_nbs)
    all_nav_nbs = ok_nbs + [nb for nb in prev_committed_nbs if nb not in failed_set]

    # -----------------------------------------------------------------------
    # Copy files into docs tree
    # -----------------------------------------------------------------------
    print()
    if args.dry_run:
        print("DRY RUN: would copy the following files:")
    else:
        print("Copying files:")

    # Rendered notebooks back into notebooks/ (outputs stripped here, after Figshare upload)
    for nb in ok_nbs:
        src = ofol / f"{nb}_rendered.ipynb"
        dst = HERE / f"{nb}.ipynb"
        print(f"  {src.name}  ->  notebooks/{nb}.ipynb  (outputs stripped for git)")
        if not args.dry_run:
            shutil.copy2(src, dst)
            subprocess.run(
                ["jupyter", "nbconvert", "--clear-output", "--to", "notebook", "--inplace", str(dst)],
                check=False,
            )

    # Per-notebook markdown files -> docs
    copied_mds: list[Path] = []
    for nb in ok_nbs:
        src_md = mdfol / f"{nb}.md"
        if src_md.exists():
            dst_md = experiment_docs_dir / f"{nb}.md"
            print(f"  mkmd/{nb}.md  ->  {dst_md.relative_to(REPO)}")
            if not args.dry_run:
                dst_md.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_md, dst_md)
            copied_mds.append(dst_md)
        else:
            print(f"  WARNING: {src_md} not found — skipping")

    # Write notebooks_urls.json so .readthedocs.yaml can download notebooks
    # at build time (notebooks are too large to commit to git).
    if args.dry_run:
        print(f"  [notebooks_urls] DRY RUN: would write {urls_json_path}")
        if all_notebook_urls:
            for nb, url in all_notebook_urls.items():
                print(f"    {nb}: {url}")
        else:
            print("    (no notebook URLs yet — run without --dry-run with a figshare token)")
    else:
        experiment_docs_dir.mkdir(parents=True, exist_ok=True)
        urls_json_path.write_text(json.dumps(all_notebook_urls, indent=2) + "\n")
        print(f"  notebooks_urls.json  ->  {urls_json_rel}")
        for nb, url in all_notebook_urls.items():
            print(f"    {nb}: {url}")

    # -----------------------------------------------------------------------
    # Update top-level pages/index.md (authors, run summary, section links)
    # -----------------------------------------------------------------------
    update_top_index(
        ename=ename,
        ok_nbs=ok_nbs,
        failed_nbs=failed_nbs,
        not_run_nbs=not_run_nbs,
        run_summary_md=md_summary,
        authors_md=authors_md,
        dry_run=args.dry_run,
    )

    # -----------------------------------------------------------------------
    # Update mkdocs.yml nav (+ ensure mkdocs-jupyter plugin present)
    # -----------------------------------------------------------------------
    update_mkdocs_nav(ename=ename, ok_nbs=all_nav_nbs, dry_run=args.dry_run)

    # -----------------------------------------------------------------------
    # Next step: publish on Figshare, then get git commands
    # -----------------------------------------------------------------------
    print()
    print("Files uploaded to Figshare and copied into the docs tree.")
    print()
    print("Next steps:")
    print("  1. Go to Figshare and PUBLISH the article so all URLs become public.")
    print("  2. Verify and get git commands by running:")
    print("       python3 mkfigs_pushit.py --check-figshare-upload")
    print()


if __name__ == "__main__":
    main()
