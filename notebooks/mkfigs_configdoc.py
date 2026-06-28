import nci_ipynb  # requires conda/analysis3-26.03 or later

import hashlib
import json
import os

import matplotlib.pyplot as plt
import requests
from matplotlib import rcParams
from requests.exceptions import HTTPError

dpi = 100
rcParams["figure.dpi"] = dpi

# ---------------------------------------------------------------------------
# Figshare helpers
# ---------------------------------------------------------------------------

FIGSHARE_BASE_URL = "https://api.figshare.com/v2/{endpoint}"


def _figshare_headers(token):
    return {"Authorization": f"token {token}"}


def _figshare_request(method, url, token, data=None, binary=False, stream=False):
    """Thin wrapper around requests that raises on HTTP errors."""
    headers = _figshare_headers(token)
    if data is not None and not binary:
        data = json.dumps(data)
    response = requests.request(
        method, url, headers=headers, data=data, stream=stream
    )
    try:
        response.raise_for_status()
    except HTTPError as exc:
        print(f"Figshare HTTP error ({method} {url}): {exc}")
        print("Response body:", response.text[:500])
        raise
    try:
        return json.loads(response.content)
    except ValueError:
        return response.content


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class FigshareUploader:
    """Upload PNG figures and rendered notebooks to a figshare article.

    One article is created per experiment name (identified by ``experiment``).
    A local JSON manifest (``figshare_manifest.json`` inside ``mdfol``) tracks
    article IDs and per-file download URLs so that re-runs skip already-uploaded
    files and do not create duplicate articles.

    Parameters
    ----------
    token : str
        Figshare personal access token.
    experiment : str
        Experiment name (used as the article title and for the manifest key).
    mdfol : str
        Directory where per-notebook PNGs, markdown files, and the manifest live.
    article_title : str, optional
        Override the figshare article title (defaults to
        ``"ACCESS-OM3 evaluation figures – <experiment>"``).
    """

    MANIFEST_FNAME = "figshare_manifest.json"

    def __init__(self, token, experiment, mdfol, article_title=None):
        self.token = token
        self.experiment = experiment
        self.mdfol = mdfol
        self.article_title = article_title or (
            f"ACCESS-OM3 evaluation figures – {experiment}"
        )
        self._manifest_path = os.path.join(mdfol, self.MANIFEST_FNAME)
        self._manifest = self._load_manifest()

    # ------------------------------------------------------------------
    # Manifest helpers
    # ------------------------------------------------------------------

    def _load_manifest(self):
        if os.path.exists(self._manifest_path):
            with open(self._manifest_path) as f:
                return json.load(f)
        return {}

    def _save_manifest(self):
        os.makedirs(self.mdfol, exist_ok=True)
        with open(self._manifest_path, "w") as f:
            json.dump(self._manifest, f, indent=2)

    # ------------------------------------------------------------------
    # Article management
    # ------------------------------------------------------------------

    def _get_or_create_article(self):
        """Return the article_id for this experiment, creating if needed."""
        key = f"article_id_{self.experiment}"
        if key in self._manifest:
            article_id = self._manifest[key]
            print(f"[figshare] Reusing existing article {article_id} for {self.experiment}")
            return article_id

        # Search private articles for an existing one with the same title
        url = FIGSHARE_BASE_URL.format(endpoint="account/articles")
        existing = _figshare_request("GET", url, self.token)
        for art in existing:
            if art.get("title") == self.article_title:
                article_id = art["id"]
                print(f"[figshare] Found existing article {article_id} by title search")
                self._manifest[key] = article_id
                self._save_manifest()
                return article_id

        # Create a new private article
        data = {
            "title": self.article_title,
            "description": (
                f"Evaluation figures from ACCESS-OM3 experiment {self.experiment}. "
                "Generated automatically by mkfigs.sh / mkfigs_configdoc.py – "
                "https://github.com/ACCESS-Community-Hub/access-om3-paper-1"
            ),
            "keywords": ["ACCESS-OM3", "ocean model", self.experiment],
            "defined_type": "figure",
        }
        response = _figshare_request("POST", url, self.token, data=data)
        # POST /account/articles returns {"location": "https://.../articles/<id>"}
        article_id = int(response["location"].split("/")[-1])
        print(f"[figshare] Created new article {article_id}: {self.article_title}")
        self._manifest[key] = article_id
        self._save_manifest()
        return article_id

    # ------------------------------------------------------------------
    # File upload
    # ------------------------------------------------------------------

    def _upload_file(self, article_id, file_path):
        """Upload a single file and return its public download_url."""
        fname = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_md5 = _md5(file_path)

        # Check manifest for a previously uploaded version of the same file
        manifest_key = f"file_{fname}"
        if manifest_key in self._manifest:
            cached = self._manifest[manifest_key]
            if cached.get("md5") == file_md5:
                print(f"[figshare] Skipping {fname} (already uploaded, MD5 matches)")
                return cached["download_url"]
            else:
                print(f"[figshare] MD5 changed for {fname}, re-uploading")

        # Step 1 – initiate upload
        url = FIGSHARE_BASE_URL.format(
            endpoint=f"account/articles/{article_id}/files"
        )
        data = {"name": fname, "size": file_size, "md5": file_md5}
        resp = _figshare_request("POST", url, self.token, data=data)
        file_url = resp["location"]  # e.g. .../articles/<id>/files/<file_id>
        file_id = int(file_url.split("/")[-1])

        # Step 2 – get upload token + parts info
        file_info = _figshare_request("GET", file_url, self.token)
        upload_url = file_info["upload_url"]
        parts_info = _figshare_request("GET", upload_url, self.token)

        # Step 3 – upload parts
        with open(file_path, "rb") as fh:
            for part in parts_info["parts"]:
                part_no = part["partNo"]
                start = part["startOffset"]
                end = part["endOffset"] + 1
                fh.seek(start)
                chunk = fh.read(end - start)
                part_url = f"{upload_url}/{part_no}"
                requests.put(
                    part_url,
                    headers=_figshare_headers(self.token),
                    data=chunk,
                ).raise_for_status()
                print(f"[figshare]   Uploaded part {part_no} of {fname}")

        # Step 4 – complete upload
        complete_url = FIGSHARE_BASE_URL.format(
            endpoint=f"account/articles/{article_id}/files/{file_id}"
        )
        _figshare_request("POST", complete_url, self.token)
        print(f"[figshare] Completed upload of {fname}")

        # Retrieve public download URL
        file_details = _figshare_request("GET", complete_url, self.token)
        download_url = file_details.get(
            "download_url",
            f"https://figshare.com/articles/figure/{article_id}",
        )

        # Cache in manifest
        self._manifest[manifest_key] = {"md5": file_md5, "download_url": download_url}
        self._save_manifest()
        return download_url

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def upload(self, file_path):
        """Upload *file_path* to the experiment's figshare article.

        Returns the public download URL string.
        """
        article_id = self._get_or_create_article()
        download_url = self._upload_file(article_id, file_path)
        return download_url

    def upload_pngs_for_notebook(self, nb_name):
        """Upload every PNG in ``self.mdfol`` that belongs to *nb_name*.

        PNG files are named ``<nb_name>_<NN>.png`` (the pattern used by
        MkmdWriter.savefig).  Returns a dict mapping filename → download URL.
        """
        results = {}
        if not os.path.isdir(self.mdfol):
            print(f"[figshare] mdfol not found: {self.mdfol}")
            return results
        pngs = sorted(
            f for f in os.listdir(self.mdfol)
            if f.lower().endswith(".png") and f.startswith(f"{nb_name}_")
        )
        if not pngs:
            print(f"[figshare] No PNG files found for notebook {nb_name} in {self.mdfol}")
            return results
        article_id = self._get_or_create_article()
        for fname in pngs:
            fpath = os.path.join(self.mdfol, fname)
            url = self._upload_file(article_id, fpath)
            results[fname] = url
            print(f"[figshare] {fname} → {url}")
        self._save_manifest()
        return results

    def upload_notebook(self, nb_name: str, nb_path: str) -> str:
        """Upload the fully rendered notebook (with outputs intact) to figshare.

        Uses the manifest key ``notebook_<nb_name>`` so it is distinct from the
        PNG file entries and can be looked up independently.

        Parameters
        ----------
        nb_name : str
            Stem of the notebook (e.g. ``"SST"``).
        nb_path : str
            Path to the rendered ``.ipynb`` file (outputs must still be present).

        Returns
        -------
        str
            Public Figshare download URL for the notebook file.
        """
        article_id = self._get_or_create_article()

        file_md5 = _md5(nb_path)
        manifest_key = f"notebook_{nb_name}"
        if manifest_key in self._manifest:
            cached = self._manifest[manifest_key]
            if cached.get("md5") == file_md5:
                print(f"[figshare] Skipping notebook {nb_name} (already uploaded, MD5 matches)")
                return cached["download_url"]
            else:
                print(f"[figshare] MD5 changed for notebook {nb_name}, re-uploading")

        download_url = self._upload_file(article_id, nb_path)
        # Store under the notebook-specific key (upload_file also stores under
        # file_<fname> but we want a stable nb_name key for the URL manifest).
        self._manifest[manifest_key] = {"md5": file_md5, "download_url": download_url}
        self._save_manifest()
        print(f"[figshare] Notebook {nb_name} → {download_url}")
        return download_url

    def rewrite_markdown(self, url_map, nb_name=None):
        """Rewrite a per-notebook markdown file so local image paths are
        replaced with figshare download URLs.

        If *nb_name* is given, rewrites ``<mdfol>/<nb_name>.md``.
        ``url_map`` is a dict mapping PNG filename → figshare download URL.
        """
        stem = nb_name if nb_name else self.experiment
        mdpath = os.path.join(self.mdfol, f"{stem}.md")
        if not os.path.exists(mdpath):
            print(f"[figshare] Markdown file not found, skipping rewrite: {mdpath}")
            return

        with open(mdpath) as f:
            content = f.read()

        # Back up original
        with open(mdpath + ".bak", "w") as f:
            f.write(content)

        for fname, url in url_map.items():
            old_pattern = f"/assets/experiments/{self.experiment}/{fname}"
            content = content.replace(old_pattern, url)

        with open(mdpath, "w") as f:
            f.write(content)
        print(f"[figshare] Rewrote image URLs in {mdpath}")

    def get_article_url(self):
        """Return the human-readable figshare article URL (best-effort)."""
        key = f"article_id_{self.experiment}"
        article_id = self._manifest.get(key)
        if article_id:
            return f"https://figshare.com/articles/figure/{article_id}"
        return None


# ---------------------------------------------------------------------------
# MkmdWriter – per-notebook markdown writer (called from inside notebooks)
# ---------------------------------------------------------------------------


class MkmdWriter:
    """Keep track of exporting key figures or tables to a per-notebook markdown file.

    Each notebook writes its own ``<nb_stem>.md`` inside ``mdfol`` so that
    mkfigs_pushit.py can copy them to separate pages in the documentation.

    experiment: path to esm file; the last directory component is used as the
                experiment name.
    nbname: filename of the notebook (e.g. ``"SST.ipynb"``).
    cwd: current working directory (used as the base for the plot folder).
    pm (default: False): True when called by papermill.
    """

    def __init__(self, esm_file, nbname, cwd, pm=False):
        self.fignum = 1
        self.experiment = os.path.basename(os.path.dirname(esm_file))
        self.nbname = nbname
        self.nb_stem = nbname[:-6] if nbname.endswith(".ipynb") else nbname
        self.cwd = cwd
        self.papermill = pm
        self.mdfol = self.cwd + "mkmd/"

    def savefig(self, figure, title, caption, dpi=dpi):
        """Save figure and append to the per-notebook markdown summary.

        figure: matplotlib figure object
        title: title of figure
        caption: caption of figure
        dpi (optional; default: 100): dpi for figure
        """
        if self.papermill:
            plot_fname = (
                self.nb_stem + "_" + str(self.fignum).zfill(2) + ".png"
            )
            os.makedirs(self.mdfol, exist_ok=True)
            figure.savefig(self.mdfol + plot_fname, dpi=dpi, bbox_inches="tight")
            print("Saved", self.mdfol + plot_fname)
            _mkmd_notebook(
                title=title,
                caption=f"`{self.nbname}`: {caption}",
                experiment=self.experiment,
                nb_stem=self.nb_stem,
                plot_fname=plot_fname,
                mdfol=self.mdfol,
                table="",
            )
            self.fignum += 1

    def table(self, title, table):
        """Append a table to the per-notebook markdown summary.

        title: title of table
        table: list of strings, one per markdown table row
        """
        if self.papermill:
            _mkmd_notebook(
                title=title,
                caption=f"`{self.nbname}`: This is a table caption",
                experiment=self.experiment,
                nb_stem=self.nb_stem,
                plot_fname="",
                mdfol=self.mdfol,
                table=table,
            )


# ---------------------------------------------------------------------------
# Internal per-notebook markdown writer
# ---------------------------------------------------------------------------


def _mkmd_notebook(title, caption, experiment, nb_stem, plot_fname, mdfol, table=""):
    """Write (or append) a figure/table entry to ``<mdfol>/<nb_stem>.md``.

    Each notebook gets its own markdown file named after the notebook stem
    (e.g. ``SST.md``, ``MLD.md``).  The header is written only on the first
    call; subsequent calls from the same notebook append just the new section.
    """
    try:
        os.makedirs(mdfol, exist_ok=True)
    except OSError as e:
        print(f"An error occurred: {e}")

    mdpath = os.path.join(mdfol, f"{nb_stem}.md")
    print(f"Adding entry to per-notebook markdown: {mdpath}")

    first_write = not os.path.exists(mdpath)
    title_already_present = (
        False if first_write else string_exists_in_file(mdpath, title)
    )

    if table != "":
        content_lines = ["\n", "## " + title + "\n", " \n"]
        for tableline in table:
            content_lines.append(tableline + "\n")
    else:
        img_ref = (
            "!["
            + caption
            + "](/assets/experiments/"
            + experiment
            + "/"
            + plot_fname
            + ") \n"
        )
        content_lines = [
            "\n",
            "## " + title + "\n",
            " \n",
            img_ref,
            " \n",
            " Caption: " + caption + "\n",
            " \n",
        ]

    if first_write:
        from pathlib import Path as _Path
        _repo_root = _Path(__file__).resolve().parent.parent
        _authors = get_notebook_authors(nb_stem, _repo_root)
        _authors_str = ", ".join(_authors) if _authors else "unknown"
        header = [
            f"<!-- auto-generated by mkfigs_configdoc.py – do not edit manually -->\n",
            f"# {nb_stem}\n",
            " \n",
            (
                f"Evaluation figures from ACCESS-OM3 experiment **{experiment}**"
                f" produced by notebook `{nb_stem}.ipynb`."
                f" Co-authors for this notebook: {_authors_str}."
                f" [View rendered notebook](notebooks/{nb_stem}.ipynb)\n"
            ),
            " \n",
        ]
        lines_to_write = header + content_lines
    elif title_already_present:
        print(
            "This title already exists in the notebook markdown – "
            "appending an additional figure."
        )
        lines_to_write = content_lines
    else:
        lines_to_write = content_lines

    try:
        with open(mdpath, "a") as f:
            f.writelines(lines_to_write)
        print(f"Lines appended to {mdpath} successfully.")
    except Exception as exc:
        print(f"WARNING: could not write to {mdpath}: {exc}")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def string_exists_in_file(filename, search_string):
    """Checks if a string exists in a file (case-sensitive)."""
    try:
        with open(filename, "r") as myfile:
            return search_string in myfile.read()
    except FileNotFoundError:
        print(f"Warning: First time this notebook has been included: '{filename}'.")
        return False


def getauthors(file_path="../CITATION.cff"):
    """Find authors from CITATION.cff and return a markdown attribution string."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

    given = None
    family = None
    coauthors = []
    for line in lines:
        line = line.strip()
        if "given-names:" in line:
            given = line.split(":", 1)[1].strip().strip('"').rstrip()
        elif line.startswith("family-names:"):
            family = line.split(":", 1)[1].strip().strip('"').rstrip()
        if given and family:
            coauthors.append(family + ", " + given + ".")
            given = None
            family = None

    return (
        "Co-authors (alphabetically) for the notebooks that created these figures: "
        + ", ".join(sorted(coauthors))
    )


def get_notebook_authors(nb_stem, repo_root):
    """Return authors for a notebook from git history.

    First commit author (notebook creator) is listed first; remaining authors
    sorted by number of commits (proxy for lines contributed), descending.
    """
    import subprocess
    from collections import Counter
    nb_path = f"notebooks/{nb_stem}.ipynb"
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--format=%an", "--", nb_path],
            capture_output=True, text=True, cwd=str(repo_root),
        )
        authors = [a.strip() for a in result.stdout.splitlines() if a.strip()]
    except Exception:
        return []
    if not authors:
        return []
    first_author = authors[-1]  # oldest commit = notebook creator
    counts = Counter(authors)
    others = sorted(
        (a for a in counts if a != first_author),
        key=lambda a: counts[a],
        reverse=True,
    )
    return [first_author] + list(others)


# ---------------------------------------------------------------------------
# Convenience entry-point called by mkfigs_pushit.py
# ---------------------------------------------------------------------------


def figshare_upload_and_rewrite(mdfol, experiment, token, nb_name=None, nb_path=None):
    """Upload PNGs (and optionally the rendered notebook) to figshare and
    rewrite the corresponding markdown so image tags point to figshare URLs.

    If *nb_name* is given, only PNGs belonging to that notebook are uploaded
    and ``<nb_name>.md`` is rewritten.

    If *nb_path* is given, the fully rendered notebook at that path is also
    uploaded.  Its figshare download URL is returned as ``url_map["_notebook"]``.

    Returns a dict mapping PNG filename → figshare download URL, plus the
    optional ``"_notebook"`` key for the notebook URL.
    """
    uploader = FigshareUploader(token=token, experiment=experiment, mdfol=mdfol)

    if nb_name:
        url_map = uploader.upload_pngs_for_notebook(nb_name)
        uploader.rewrite_markdown(url_map, nb_name=nb_name)
    else:
        # Legacy: upload all PNGs in mdfol (no per-notebook split)
        pngs = sorted(f for f in os.listdir(mdfol) if f.lower().endswith(".png"))
        url_map = {}
        if not pngs:
            print("[figshare] No PNG files found in", mdfol)
        else:
            article_id = uploader._get_or_create_article()
            for fname in pngs:
                url = uploader._upload_file(article_id, os.path.join(mdfol, fname))
                url_map[fname] = url
            uploader._save_manifest()
        uploader.rewrite_markdown(url_map)

    if nb_path and nb_name:
        nb_url = uploader.upload_notebook(nb_name, nb_path)
        url_map["_notebook"] = nb_url

    article_url = uploader.get_article_url()
    print(f"\n[figshare] Done! Article: {article_url}")
    n_pngs = sum(1 for k in url_map if not k.startswith("_"))
    print(f"[figshare] Uploaded {n_pngs} PNG(s)" + (" + notebook." if "_notebook" in url_map else "."))
    return url_map
