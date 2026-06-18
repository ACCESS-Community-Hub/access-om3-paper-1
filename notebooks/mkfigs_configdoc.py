import nci_ipynb  # requires conda/analysis3-26.03 or later

import hashlib
import json
import os
import time

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
FIGSHARE_CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB


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
    """Upload PNG figures to a figshare article and return public download URLs.

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
        Directory where ``mkmd/`` PNGs and the manifest live.
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

    def upload_all_pngs(self):
        """Upload every PNG in ``self.mdfol`` and return a dict mapping
        filename → download URL.

        This is called at the end of ``mkfigs.sh`` (via
        ``figshare_upload_and_rewrite.py``) to do a bulk upload and then
        rewrite the markdown file so image references point to figshare.
        """
        results = {}
        pngs = sorted(
            f for f in os.listdir(self.mdfol) if f.lower().endswith(".png")
        )
        if not pngs:
            print("[figshare] No PNG files found in", self.mdfol)
            return results
        article_id = self._get_or_create_article()
        for fname in pngs:
            fpath = os.path.join(self.mdfol, fname)
            url = self._upload_file(article_id, fpath)
            results[fname] = url
            print(f"[figshare] {fname} → {url}")
        self._save_manifest()
        return results

    def rewrite_markdown(self, url_map):
        """Rewrite the experiment markdown file so local image paths are
        replaced with figshare download URLs.

        ``url_map`` is a dict mapping PNG filename → figshare download URL
        (as returned by ``upload_all_pngs``).

        The original markdown is backed up as ``<experiment>.md.bak``.
        """
        mdpath = os.path.join(self.mdfol, f"{self.experiment}.md")
        if not os.path.exists(mdpath):
            print(f"[figshare] Markdown file not found, skipping rewrite: {mdpath}")
            return

        with open(mdpath) as f:
            content = f.read()

        # Back up original
        with open(mdpath + ".bak", "w") as f:
            f.write(content)

        for fname, url in url_map.items():
            # The markdown uses the pattern:  ![...](/assets/experiments/<exp>/<fname>)
            # Replace with the figshare URL.
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
# Original mkfigs_configdoc helpers (unchanged API)
# ---------------------------------------------------------------------------


class MkmdWriter:
    """Class to keep track of exporting key Figures or Tables to a markdown file

    experiment: path to esm file, we just take the last folder to mean the experiment name
    nbname: name of notebook that this is being called from
    cwd: current working directory (will use this as the basis for plot folder)
    pm (default: False): being called by papermill?
    """

    def __init__(self, esm_file, nbname, cwd, pm=False):
        self.fignum = 1
        self.experiment = os.path.basename(os.path.dirname(esm_file))
        self.nbname = nbname
        self.cwd = cwd
        self.papermill = pm
        self.mdfol = self.cwd + "mkmd/"

    def savefig(self, figure,title, caption, dpi=dpi):
        """Save figure and append to markdown summary.

        figure: matplotlib's explicit figure object (the figure data remains anchored to your variable instead of relying on Matplotlib's global state machine)
        title: title of figure
        caption: caption of figure
        dpi (optional; default: 100): dpi for figure
        """
        if self.papermill:
            plot_fname = (
                self.nbname[:-6] + "_" + str(self.fignum).zfill(2) + ".png"
            )
            os.makedirs(self.mdfol, exist_ok=True)
            figure.savefig(self.mdfol + plot_fname, dpi=dpi, bbox_inches="tight")
            print("Saved", self.mdfol + plot_fname)
            mkmd(
                title,
                f"`{self.nbname}`: {caption}",
                self.experiment,
                plot_fname,
                self.mdfol,
                table="",
            )
            self.fignum += 1

    def table(self, title, table):
        """Append table to markdown summary.

        title: title of table
        table: markdown table strings (a list of strings where each string is a new line)
        """
        if self.papermill:
            mkmd(
                title,
                f"`{self.nbname}`: This is a table caption",
                self.experiment,
                "",
                self.mdfol,
                table,
            )


def mkmd(title, caption, experiment, plot_fname, mdfol, table=""):
    """Function to create a markdown file and add a figure or a table

    title: title for figure or table
    caption: caption for figure (not used when making a table)
    experiment: experiment name
    plot_fname: name of plot
    mdfol: directory to output markdown file and figures
    table (default: ''): if this is != '' then a table will be added rather than a figure
    """
    try:
        os.makedirs(mdfol, exist_ok=True)
    except OSError as e:
        print(f"An error occurred: {e}")

    mdpath = mdfol + experiment + ".md"
    print("Adding a figure to markdown doc: " + mdpath)

    if table != "":
        fig_or_table = table
        lines_to_append = [
            "<!-- push this file to documentation/docs/pages/experiments/"
            + experiment
            + " and the images to documentation/docs/assets/"
            + experiment
            + " -->"
            + "\n",
            "# " + experiment + "\n",
            " \n",
            "This page shows evaluation figures from ACCESS-OM3 experiment "
            + experiment
            + " for discussion and see plotting scripts have a look at "
            "[this repository](https://github.com/acCESS-Community-Hub/access-om3-paper-1/) "
            "and related [issues](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues).\n",
            " \n",
            getauthors(),
            " \n",
            "## " + title + "\n",
            " \n",
        ]
        for tableline in fig_or_table:
            lines_to_append.append(tableline + "\n")
    else:
        # Use a local-path placeholder; mkfigs.sh will rewrite to figshare URLs
        # after the bulk upload step via FigshareUploader.rewrite_markdown().
        fig_or_table = (
            "!["
            + caption
            + "](/assets/experiments/"
            + experiment
            + "/"
            + plot_fname
            + ") \n"
        )
        lines_to_append = [
            "<!-- push this file to documentation/docs/pages/experiments/"
            + experiment
            + " and the images to documentation/docs/assets/"
            + experiment
            + " -->"
            + "\n",
            "# " + experiment + "\n",
            " \n",
            "This page shows evaluation figures from ACCESS-OM3 experiment "
            + experiment
            + " for discussion and see plotting scripts have a look at "
            "[this repository](https://github.com/acCESS-Community-Hub/access-om3-paper-1/) "
            "and related [issues](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues).\n",
            " \n",
            getauthors(),
            " \n",
            "## " + title + "\n",
            " \n",
            fig_or_table,
            " \n",
            " Caption: " + caption + "\n",
            " \n",
        ]

    if os.path.exists(mdpath) and string_exists_in_file(mdpath, title):
        print(
            "This notebook has already added to the figure file, "
            "so this will add an additional figure."
        )
        lines_to_append = lines_to_append[8:]
        print(lines_to_append)
    elif os.path.exists(mdpath):
        lines_to_append = lines_to_append[7:]
        print(lines_to_append)

    try:
        with open(mdpath, "a") as file:
            file.writelines(lines_to_append)
        print(f"Lines appended to {mdpath} successfully.")
    except Exception:
        pass


def string_exists_in_file(filename, search_string):
    """Checks if a string exists in a file (case-sensitive)."""
    try:
        with open(filename, "r") as myfile:
            if search_string in myfile.read():
                return True
            else:
                return False
    except FileNotFoundError:
        print(
            f"Warning: First time this notebook has been included: '{filename}'."
        )
        return False


def getauthors(file_path="../CITATION.cff"):
    """Function to find authors from citation file and put them in the markdown file"""
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


# ---------------------------------------------------------------------------
# Convenience entry-point called by mkfigs.sh
# ---------------------------------------------------------------------------


def figshare_upload_and_rewrite(mdfol, experiment, token):
    """Upload all PNGs in *mdfol* to figshare and rewrite the experiment
    markdown so image tags point to figshare download URLs.

    Returns a dict mapping PNG filename → figshare download URL.
    """
    uploader = FigshareUploader(token=token, experiment=experiment, mdfol=mdfol)
    url_map = uploader.upload_all_pngs()
    uploader.rewrite_markdown(url_map)
    article_url = uploader.get_article_url()
    print(f"\n[figshare] Done! Article: {article_url}")
    print(f"[figshare] Uploaded {len(url_map)} file(s).")
    return url_map
