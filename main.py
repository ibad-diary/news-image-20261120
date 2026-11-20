#!/usr/bin/env python3
"""Round-2 entry for make.fun news-image-20261120.

The front page is pre-rendered by generate_image.py and shipped as
entry.png next to this file. This program only copies that file into
the output directory make.fun requests, after verifying it is a real
PNG within the competition limits (no more than 1 MiB, no side longer
than 1024 pixels). Standard library only, no network access, so two
runs always produce byte-identical output.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = "entry.png"
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("main.py: " + message, file=sys.stderr)
    sys.exit(1)


def main():
    source = os.path.join(HERE, FILE)
    try:
        with open(source, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        fail("cannot read %s (%s)" % (FILE, exc))

    if blob[:8] != SIGNATURE:
        fail("%s does not start with the PNG signature" % FILE)
    if len(blob) > MAX_BYTES:
        fail("%s is %d bytes, over the 1 MiB limit" % (FILE, len(blob)))
    if len(blob) < 24 or blob[12:16] != b"IHDR":
        fail("%s has no PNG header chunk" % FILE)
    width, height = struct.unpack(">II", blob[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        fail("%s is %dx%d, over 1024x1024" % (FILE, width, height))

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, FILE)
    with open(target, "wb") as handle:
        handle.write(blob)
    print("copied %s -> %s (%dx%d, %d bytes)"
          % (FILE, target, width, height, len(blob)))


if __name__ == "__main__":
    main()
