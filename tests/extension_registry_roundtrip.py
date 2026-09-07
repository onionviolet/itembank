"""Roundtrip checks for validated first-party extension registration."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from extension_registry import RegistrationError, build_registry
import source_adapters

def fail(message):
    print("FAIL: " + message); sys.exit(1)
def handler(raw, options): return raw, options
def row(name="alpha", registered_handler=handler):
    return {"name": name, "version": "1.2.3", "handler": registered_handler,
            "capability": "Handle synthetic input.", "fallback": "Refuse synthetic input by name.",
            "check": "python3 tests/extension_registry_roundtrip.py"}
def expect(entries, needle):
    try: build_registry(entries)
    except RegistrationError as exc:
        if needle not in str(exc): fail("error %r did not name %r" % (str(exc), needle))
    else: fail("invalid declaration did not raise for %s" % needle)
def main():
    entries=[row("alpha"),row("beta")]; h,v,d=build_registry(entries)
    if list(h)!=["alpha","beta"] or h["alpha"] is not handler or list(v.values())!=["1.2.3","1.2.3"]: fail("valid registry mismatch")
    if d["alpha"] != {k:x for k,x in entries[0].items() if k != "handler"}: fail("description mismatch")
    d["alpha"]["capability"]="changed"
    if entries[0]["capability"] == "changed": fail("metadata was not copied")
    if build_registry([]) != ({},{},{}): fail("empty registry mismatch")
    expect([None],"entry 0"); x=row(); del x["fallback"]; expect([x],"fallback")
    x=row(); x["priority"]="x"; expect([x],"priority"); expect([row("a"),row("a")],"a")
    for bad in ("Alpha","two-words","2alpha",""): expect([row(bad)],"name")
    for bad in ("1","1.2","1.2.3.4","v1.2.3",123): x=row(); x["version"]=bad; expect([x],"version")
    x=row(); x["handler"]="x"; expect([x],"handler")
    for field in ("capability","fallback","check"):
        for bad in (""," ",None): x=row(); x[field]=bad; expect([x],field)
    def never(raw, options): raise AssertionError("handler executed")
    bad=row("bad",never); bad["version"]="invalid"; expect([row("new",never),bad],"entry 1")
    before,_,_=build_registry([row()]); extended,_,_=build_registry([row(),row("stub",lambda raw,opt:(raw.decode(),opt["suffix"]))])
    if before["alpha"](b"x",{}) != (b"x",{}) or extended["stub"](b"x",{"suffix":"!"}) != ("x","!"): fail("dispatch mismatch")
    raw=b"first line\nsecond line\n"
    if source_adapters.ADAPTER_REGISTRY["text"](raw,{}) != source_adapters._extract_text(raw,{}): fail("text adapter mismatch")
    names=("markdown","text","pdf","docx","pptx","web","transcript","ocr","epub","asr")
    if tuple(source_adapters.ADAPTER_REGISTRY) != names or tuple(source_adapters.ADAPTER_VERSIONS.values()) != ("1.0.0",)*9+("0.0.0",): fail("built-in compatibility mismatch")
    print("ok: extension registry roundtrip")
if __name__ == "__main__": main()
