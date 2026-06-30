# Change the URL segment for pages in MkDocs to hide the "/pages" prefix, so that pages inside the
# "pages" directory are served directly at the root URL.
#
# on_files fires once after all File objects are collected, before any page rendering or link
# resolution. Modifying dest_uri here ensures every file's output path is correct before MkDocs
# computes relative links between pages — in particular, before pages/index.md's links to
# pages/experiments/... are resolved. Using on_page_markdown instead would only fix the current
# page's dest_uri, leaving target pages with stale pages/-prefixed paths when the home page (first
# in nav) resolves its links.
def on_files(files, *, config):
    for f in files:
        if f.url.startswith("pages/"):
            f.url = f.url.removeprefix("pages/")
            f.dest_uri = f.dest_uri.removeprefix("pages/")
            # abs_dest_path is a cached_property computed from dest_uri; clear the
            # cache so it is recomputed from the updated dest_uri on next access.
            f.__dict__.pop("abs_dest_path", None)
    return files
