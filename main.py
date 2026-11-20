#!/usr/bin/env python3
"""Copy the verified front-page image to the make.fun output directory.

Reads ``entry.png`` next to this script, checks that it really is a PNG
no larger than 1 MiB and no bigger than 1024x1024 pixels, then writes an
exact byte copy to ``$MAKEFUN_OUTPUT_DIR/entry.png``.

Only the standard library is used and no network access happens, so
running the script twice produces byte-identical output.
"""

import os
import struct
import sys

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MiB
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SOURCE_NAME = "entry.png"


def fail(message):
    """Print an error to stderr and exit non-zero."""
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def png_dimensions(data):
    """Return (width, height) parsed from the PNG IHDR chunk.

    The PNG layout is: 8-byte signature, then a 4-byte chunk length,
    the 4-byte chunk type (must be "IHDR"), then 13 bytes of header
    data whose first 8 bytes are the width and height as big-endian
    unsigned 32-bit integers.
    """
    header_size = 8 + 4 + 4 + 13
    if len(data) < header_size:
        fail("entry.png is too short to contain a PNG header")
    if data[12:16] != b"IHDR":
        fail("entry.png has no IHDR chunk where one is expected")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, SOURCE_NAME)

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not output_dir:
        fail("MAKEFUN_OUTPUT_DIR is not set")

    if not os.path.isfile(source_path):
        fail("missing " + source_path)

    with open(source_path, "rb") as handle:
        data = handle.read()

    if data[:8] != PNG_SIGNATURE:
        fail("entry.png does not start with the PNG magic bytes")

    if len(data) > MAX_FILE_SIZE:
        fail(
            "entry.png is %d bytes, over the 1 MiB limit" % len(data)
        )

    width, height = png_dimensions(data)
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        fail(
            "entry.png is %dx%d, over the 1024x1024 limit"
            % (width, height)
        )

    os.makedirs(output_dir, exist_ok=True)
    destination = os.path.join(output_dir, SOURCE_NAME)
    with open(destination, "wb") as handle:
        handle.write(data)

    print("ok: copied entry.png (%dx%d, %d bytes)" % (width, height, len(data)))


if __name__ == "__main__":
    main()
