#!/usr/bin/env python3
"""The one way this codebase resolves a bundled non-Python resource.

A path computed from `__file__` names a real file in a checkout and names a
member inside an archive when the same code runs from a `.pyz` -- and
`open()` cannot read the second. `surfaces/settings.py` and
`surfaces/protocol_cli.py` both used to compute their own `__file__`-relative
path to `schemas/*.json`; both raised `FileNotFoundError` from inside a
`zipapp` archive. This module is the one reader both now go through instead.

Kept dependency-free apart from `os` and `zipfile` -- nothing in the
four-layer model (`model`/`runtime`/`server`/`surfaces`) may import it in the
other direction.
"""
import os
import zipfile

# In a checkout this is the repository root; inside a .pyz this is the
# archive's own path, because resources.py sits at the archive's top level.
ROOT = os.path.dirname(os.path.abspath(__file__))


def archive_path():
    """Return the running `.pyz`'s path when this code is executing inside
    one, or `None` from a plain checkout. The updater answers "am I running
    from a .pyz, and where is it" through this function.
    """
    if zipfile.is_zipfile(ROOT):
        return ROOT
    return None


def read_bytes(relpath):
    """Read `relpath` (forward-slash-separated, relative to the repository
    root / archive top level) as bytes, whether this process is running from
    a checkout or from inside a `.pyz`.
    """
    direct = os.path.join(ROOT, relpath)
    if os.path.exists(direct):
        return open(direct, "rb").read()
    archive = archive_path()
    if archive is not None:
        with zipfile.ZipFile(archive) as zf:
            return zf.read(relpath)
    raise FileNotFoundError(direct)


def read_text(relpath):
    return read_bytes(relpath).decode("utf-8")
