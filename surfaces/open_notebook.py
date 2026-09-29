"""Local Open Notebook companion link for a course's Sources area."""

import json
import os
import urllib.error
import urllib.request

from surfaces import presentation


def _port(name, default):
    value = os.environ.get(name, str(default))
    try:
        port = int(value)
    except ValueError:
        return None
    return port if 1 <= port <= 65535 else None


def panel():
    """Show a loopback-only companion without transferring course material."""
    api_port = _port("ITEMBANK_OPEN_NOTEBOOK_API_PORT", 5055)
    ui_port = _port("ITEMBANK_OPEN_NOTEBOOK_UI_PORT", 8502)
    if api_port is None or ui_port is None:
        status = "Open Notebook ports are invalid. Set ports between 1 and 65535."
        link = ""
    else:
        request = urllib.request.Request(
            "http://127.0.0.1:%d/health" % api_port,
            headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=0.5) as response:
                payload = json.load(response)
            available = isinstance(payload, dict) and payload.get("status") in {"healthy", "ok"}
        except (OSError, ValueError, urllib.error.URLError):
            available = False
        if available:
            status = "The local Open Notebook API is responding."
            link = ('<p><a href="http://127.0.0.1:%d/" target="_blank" '
                    'rel="noopener noreferrer">Open Notebook in a new tab</a></p>'
                    % ui_port)
        else:
            status = "Open Notebook is unavailable on this computer. Start its local service to use the companion."
            link = ""
    return ('<section class="course-detail" aria-labelledby="open-notebook-title">'
            '<h3 id="open-notebook-title">Open Notebook companion</h3>'
            '<p role="status">%s</p>%s'
            '<p>Research and notes stay in Open Notebook. Choose any copy into '
            'this course explicitly after reviewing its source and rights.</p>'
            '</section>' % (presentation.esc(status), link))
