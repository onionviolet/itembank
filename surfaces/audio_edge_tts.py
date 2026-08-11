"""edge-tts engine registration: the network, MP3-native TTS backend (D-02,
D-09, D-16).

Supply chain (Directive 4a, D-15): pinned `edge-tts==7.2.8`, license read
from the pinned version's LICENSE at vendoring time -- **LGPL-3.0** (MIT only
for `src/edge_tts/srt_composer.py`). The PyPI classifier is LGPLv3, which
resolves research A2's "GPL-3.0 reported" ambiguity in favor of the usable
LGPL posture; the posture is recorded in requirements.txt beside the pin.

The library is imported lazily inside `speak()`, never at module scope, so
itembank stays dependency-free until an engine actually runs. A missing
library or an unreachable endpoint is a named refusal (D-04): the engine
never transcribes, never retries another voice, and never silently falls
back.
"""
import asyncio
import io
import socket

from surfaces.audio import EngineError, TTSEngine, register

# The network endpoint item text is sent to (D-16). Named in the command's
# own help text and in the disclosure string the roundtrip suite asserts.
EDGE_ENDPOINT_HOST = "speech.platform.bing.com"
EDGE_ENDPOINT_PORT = 443
EDGE_PIN = "edge-tts==7.2.8"

# The default voice, recorded in the settings schema (audio.edge_tts.voice).
DEFAULT_VOICE = "en-US-GuyNeural"


def _endpoint_reachable(timeout=3.0):
    """A conservative reachability probe for `available()`: a TCP connect to
    the Microsoft endpoint with a short timeout. Tests replace this with a
    stub so the engine path stays offline in the roundtrip suite."""
    try:
        with socket.create_connection(
                (EDGE_ENDPOINT_HOST, EDGE_ENDPOINT_PORT), timeout=timeout):
            return True
    except OSError:
        return False


class EdgeTTSEngine(TTSEngine):
    """edge-tts: streams MP3 natively, no encoder (research section 2)."""

    name = "edge-tts"
    container = "mp3"

    def __init__(self, voice=DEFAULT_VOICE, probe=None):
        self.voice = voice
        self.probe = probe or _endpoint_reachable

    def configure(self, settings):
        """Read the voice from settings (D-01: engine choice is a settings
        entry; the --engine flag overrides only the name)."""
        audio = (settings or {}).get("audio") or {}
        voice = (audio.get("edge_tts") or {}).get("voice")
        if voice:
            self.voice = voice

    def available(self):
        try:
            import edge_tts  # noqa: F401  (lazy: the pin may not be installed)
        except ImportError:
            return False
        return self.probe()

    def speak(self, text):
        try:
            import edge_tts
        except ImportError:
            raise EngineError(self.name, "pinned dependency %s is not "
                                          "installed" % EDGE_PIN)
        if not self.probe():
            raise EngineError(self.name, "endpoint %s:%d unreachable" %
                              (EDGE_ENDPOINT_HOST, EDGE_ENDPOINT_PORT))

        async def _stream():
            communicate = edge_tts.Communicate(text, voice=self.voice)
            chunks = []
            async for chunk in communicate.stream():
                if chunk.get("type") == "audio":
                    chunks.append(chunk["data"])
            return b"".join(chunks)

        try:
            return asyncio.run(_stream())
        except EngineError:
            raise
        except Exception as exc:
            raise EngineError(self.name,
                              "edge-tts stream failed: %s" % exc) from exc


def edge_tts_factory():
    return EdgeTTSEngine()


register("edge-tts", edge_tts_factory)
