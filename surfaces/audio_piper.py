"""Piper engine registration: the local, offline TTS backend (D-02, D-09).

Supply chain (Directive 4a, D-15): **recorded decision** -- the PyPI package
`piper-tts` (the only wheel-bearing pip distribution, 1.3.0+) is
GPL-3.0-or-later (the OHF-Voice/piper1-gpl fork), which cannot be imported
into this project. The MIT-licensed original (rhasspy/piper) has no clean
Windows wheels for the pinned Python. Per research A3 and the Phase 13
sidecar pattern, this engine therefore drives a **bundled piper binary plus
an MIT-licensed voice model** via subprocess -- never importing GPL code --
and converts WAV to MP3 through one pinned encoder, `lameenc==1.8.4`
(LGPL-3.0-or-later, Windows wheels for 3.10+), only when the container
setting says mp3. The decision and the artifact pins are recorded in
requirements.txt.

The binary, model, and encoder are all resolved lazily at call time and
never imported at module scope, so itembank stays dependency-free until a
local engine actually runs. A missing binary, model, or encoder is a named
refusal (D-04): the engine never silently substitutes another voice.
"""
import os
import subprocess
import tempfile

from surfaces.audio import EngineError, TTSEngine, register

LAMEENC_PIN = "lameenc==1.8.4"
PIPER_BINARY = "piper"
DEFAULT_VOICE = "en_US-lessac-medium"


def _to_mp3(wav_bytes):
    """The one engine-scoped MP3 encoder (D-09): decode the WAV frames with
    the stdlib `wave` reader, encode through the pinned lameenc, and return
    MP3 bytes. Only ever called when the container setting says mp3."""
    import io
    import wave

    import lameenc

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav:
        channels = wav.getnchannels()
        rate = wav.getframerate()
        pcm = wav.readframes(wav.getnframes())
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(128)
    encoder.set_in_sample_rate(rate)
    encoder.set_channels(channels)
    return encoder.encode(pcm) + encoder.flush()


class PiperEngine(TTSEngine):
    """Piper: WAV-native; MP3 via the pinned lameenc when the container
    setting says mp3, WAV passed through untouched when it says wav."""

    name = "piper"
    container = "wav"

    def __init__(self, binary=PIPER_BINARY, voice=DEFAULT_VOICE, model="",
                 runner=None):
        self.binary = binary
        self.voice = voice
        self.model = model
        self.runner = runner or self._run

    def configure(self, settings):
        """Read voice/model/container from settings (D-01/D-09)."""
        audio = (settings or {}).get("audio") or {}
        piper = audio.get("piper") or {}
        if piper.get("voice"):
            self.voice = piper["voice"]
        if piper.get("model"):
            self.model = piper["model"]
        self.target_container = audio.get("container") or "mp3"

    def _run(self, argv, text):
        """The one subprocess seam tests stub: invoke the bundled piper binary
        with the item text on stdin and check the exit status (shell=False)."""
        return subprocess.run(argv, input=text.encode("utf-8"),
                              capture_output=True, check=True)

    def available(self):
        if not self.model or not os.path.exists(self.model):
            return False
        return True

    def speak(self, text):
        if not self.model or not os.path.exists(self.model):
            raise EngineError(self.name, "missing model file: %r" % self.model)
        with tempfile.TemporaryDirectory() as td:
            out_wav = os.path.join(td, "out.wav")
            try:
                self.runner([self.binary, "--model", self.model,
                             "--output_file", out_wav], text)
                with open(out_wav, "rb") as fh:
                    wav = fh.read()
            except FileNotFoundError:
                raise EngineError(self.name, "piper binary %r not found"
                                  % self.binary)
            except subprocess.CalledProcessError as exc:
                raise EngineError(self.name, "piper invocation failed: %s"
                                  % exc)
            except OSError as exc:
                raise EngineError(self.name, "piper run failed: %s" % exc)
        if getattr(self, "target_container", "mp3") == "mp3":
            try:
                return _to_mp3(wav)
            except ImportError:
                raise EngineError(self.name, "pinned encoder %s is not "
                                  "installed" % LAMEENC_PIN)
            except Exception as exc:
                raise EngineError(self.name, "MP3 encode failed: %s" % exc)
        return wav


def piper_factory():
    return PiperEngine()


register("piper", piper_factory)
