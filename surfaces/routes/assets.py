"""Assets routes; daemon-owned helpers are imported at request time."""
import resources


def handle_marker(handler):
    """`GET /__itembank__` -- the identifying response plan 02-06's
    detect-and-attach probe looks for.
    """
    handler.send_json({"itembank": True})


def handle_katex_asset(handler, name):
    """`GET /assets/katex/<name>` -- the one static-asset route (09-04).
    The name is resolved through the closed `KATEX_ASSETS` map (a URL suffix
    to a vendored archive-relative path and MIME type) and the bytes come
    from `resources.read_bytes()`, the same checkout/archive reader every
    other bundled resource uses. The name is never joined to a filesystem
    path: an unknown, encoded, nested, traversal, or query-manipulated name
    is a plain 404, and only names the reviewed CSS actually references
    exist in the map (T-09-09).
    """
    from surfaces.daemon import (
        KATEX_ASSETS,
    )

    entry = KATEX_ASSETS.get(name)
    if entry is None:
        handler.send_not_found(name)
        return
    relpath, mime = entry
    try:
        body = resources.read_bytes(relpath)
    except OSError:
        handler.send_not_found(name)
        return
    handler.send_bytes(body, mime)


def handle_font_asset(handler, name):
    """`GET /assets/fonts/<name>` -- the vendored reading faces, built
    exactly like `handle_katex_asset`: the name is resolved through the
    closed `FONT_ASSETS` map (a URL suffix to an archive-relative path and
    a MIME type) and the bytes come from `resources.read_bytes()`, so the
    checkout, the .pyz and the frozen build all serve the same files. The
    name is never joined to a filesystem path: an unknown, encoded, nested,
    traversal, or query-manipulated name is a plain 404 (T-e2m-01).
    """
    from surfaces.daemon import (
        FONT_ASSETS,
    )

    entry = FONT_ASSETS.get(name)
    if entry is None:
        handler.send_not_found(name)
        return
    relpath, mime = entry
    try:
        body = resources.read_bytes(relpath)
    except OSError:
        handler.send_not_found(name)
        return
    handler.send_bytes(body, mime)

