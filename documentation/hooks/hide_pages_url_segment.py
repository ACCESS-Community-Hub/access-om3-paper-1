# Strip the leading "pages/" segment from every file that lives under docs/pages/,
# so that pages/index.md serves at the site root, pages/experiments/... serves at
# experiments/..., etc.
#
# on_files fires once after all File objects are collected — including NotebookFile
# objects that mkdocs-jupyter has already created — and before any page rendering or
# link resolution.  Doing the path rewrite here ensures every file's output URL is
# correct before MkDocs resolves relative links between pages.
#
# Implementation note: we only modify dest_uri (the output path) and clear any
# cached derivatives from __dict__.  We do NOT set f.url directly because
# mkdocs-jupyter's NotebookFile may define url as a read-only @property; setting it
# would raise AttributeError.  In MkDocs 1.6+ url is a cached_property derived from
# dest_uri, so clearing "__dict__['url']" (a no-op when it is a @property) and
# clearing "__dict__['abs_dest_path']" is sufficient.
def on_files(files, *, config):
    for f in files:
        if not f.dest_uri.startswith("pages/"):
            continue
        f.dest_uri = f.dest_uri.removeprefix("pages/")
        f.__dict__.pop("abs_dest_path", None)   # cached_property — recompute from dest_uri
        f.__dict__.pop("url", None)             # cached_property — recompute from dest_uri
    return files
