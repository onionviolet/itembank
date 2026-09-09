#!/usr/bin/env python3
"""Generate the minimal shell icon (a solid default-accent square).

Tauri's Windows bundle consumes the ICO while its Rust context macro consumes
the PNG for the tray icon. Keep both outputs derived from one stdlib-only
source. A brand icon is out of scope for this phase (D-15: no new UI).
"""
import os, struct, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(ROOT, "src-tauri", "icons")
ICO_OUT = os.path.join(ICON_DIR, "icon.ico")
PNG_OUT = os.path.join(ICON_DIR, "icon.png")


def png_chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def make_png(size, pixel):
    raw = b"".join(b"\x00" + pixel * size for _ in range(size))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr)
            + png_chunk(b"IDAT", zlib.compress(raw))
            + png_chunk(b"IEND", b""))


def main():
    size = 32
    pixel = struct.pack("4B", 14, 110, 98, 255)     # the default accent #0e6e62
    png = make_png(size, pixel)
    ico = (struct.pack("<HHH", 0, 1, 1)
           + struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(png), 22)
           + png)
    os.makedirs(ICON_DIR, exist_ok=True)
    with open(PNG_OUT, "wb") as f:
        f.write(png)
    with open(ICO_OUT, "wb") as f:
        f.write(ico)
    print("wrote %s (%d bytes)" % (PNG_OUT, len(png)))
    print("wrote %s (%d bytes)" % (ICO_OUT, len(ico)))


if __name__ == "__main__":
    main()
