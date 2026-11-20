#!/usr/bin/env python3
"""make.fun entry: news-image-20261120.

Writes the pre-rendered entry.png shipped beside this file to
MAKEFUN_OUTPUT_DIR/entry.png (default /output). Before writing, the
file is checked: PNG magic bytes, at most 1 MiB, and at most
1024x1024 pixels (width/height read from the IHDR chunk). Standard
library only; the output is byte-identical on every run.
"""
import os
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024


def check(data):
    """Return (width, height) or exit with a plain error message."""
    if data[:8] != PNG_MAGIC:
        sys.exit("entry.png: bad PNG magic bytes")
    if len(data) > MAX_BYTES:
        sys.exit("entry.png: %d bytes exceeds 1 MiB" % len(data))
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        sys.exit("entry.png: %dx%d exceeds 1024x1024" % (width, height))
    return width, height


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(root, "entry.png")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "entry.png")

    with open(source, "rb") as fh:
        data = fh.read()
    width, height = check(data)

    with open(target, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (target, len(data), width, height))


if __name__ == "__main__":
    main()
