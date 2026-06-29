# Change the URL segment for pages in MkDocs to hide the "/pages" prefix, so that pages inside the
# "pages" directory are served directly at the root URL.
from mkdocs.plugins import event_priority

@event_priority(-100)
def on_page_markdown(markdown, *, page, config, files):
    if page.file.url.startswith("pages/"):
        page.file.url = page.file.url.removeprefix("pages/")
        page.file.dest_uri = page.file.dest_uri.removeprefix("pages/")
        # abs_dest_path is a cached_property computed from dest_uri; clear the
        # cache so it is recomputed from the updated dest_uri on next access.
        # This matters for mkdocs-jupyter notebook pages, which may access
        # abs_dest_path before on_page_markdown fires and cache the old value.
        page.file.__dict__.pop("abs_dest_path", None)
