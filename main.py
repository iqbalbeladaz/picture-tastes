"""Picture Tastes entry: one perfect strawberry.

How it works (step by step)
----------------------------
1. Locate ``image.jpg`` in the same directory as this file
   (``os.path.dirname(os.path.abspath(__file__))``) — the entry
   image must sit next to ``main.py`` in the repo, not in the
   current working directory.
2. Check the source exists and is really a JPEG (magic bytes
   ``0xFFD8`` ... ``0xFFD9``); otherwise print a clear error and exit 1.
3. Parse the image dimensions from the JPEG header: walk the
   marker segments after SOI until a Start Of Frame (SOF) segment
   is found and read its width/height fields.
4. Copy its bytes unchanged to ``/output/entry.png`` — the sandbox
   output path required by make.fun — creating ``/output`` if needed.
5. Verify the written file: it must be at most 1,048,576 bytes and
   carry valid JPEG magic bytes, then print a one-line summary
   including the size and the parsed dimensions (e.g. 1024x1024).

Errors
------
- ``image.jpg`` missing: the program prints the exact absolute path
  it looked for and a hint to place the entry image next to
  ``main.py`` (run from the repo root or copy the file there),
  then exits 1 — no output file is written.
- Source not a JPEG / output too large / bad magic bytes: a
  one-line ``error: ...`` message on stderr and exit 1.

Standard library only; no network access. The entry image itself is
never modified, only copied.
"""

import os
import shutil
import sys


def _is_jpeg(path: str) -> bool:
    """Return True if the file starts with FFD8 and ends with FFD9."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(2)
            fh.seek(-2, os.SEEK_END)
            tail = fh.read(2)
    except OSError:
        return False
    return head == b"\xff\xd8" and tail == b"\xff\xd9"


_SOF_MARKERS = frozenset(
    [0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
     0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF]
)


def _jpeg_dimensions(path: str):
    """Parse width/height from the JPEG SOF marker header.

    Walks the marker segments after the SOI marker until a Start Of
    Frame segment is found; its payload is precision (1 byte), height
    (2 bytes, big-endian), width (2 bytes, big-endian). Returns
    ``(width, height)`` or ``None`` if no SOF segment is found.
    """
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        return None
    pos = 2
    while pos + 1 < len(data):
        if data[pos] != 0xFF:
            pos += 1
            continue
        marker = data[pos + 1]
        # Skip padding / fill bytes and standalone markers.
        if marker == 0xFF:
            pos += 1
            continue
        if marker in (0x00, 0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        if pos + 4 > len(data):
            return None
        seg_len = int.from_bytes(data[pos + 2:pos + 4], "big")
        if marker in _SOF_MARKERS:
            if pos + 9 > len(data):
                return None
            height = int.from_bytes(data[pos + 5:pos + 7], "big")
            width = int.from_bytes(data[pos + 7:pos + 9], "big")
            return (width, height)
        pos += 2 + seg_len
    return None


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "image.jpg")
    dest_dir = "/output"
    dest = os.path.join(dest_dir, "entry.png")

    if not os.path.isfile(source):
        print(
            f"error: source image not found: {source}\n"
            f"  hint: place image.jpg next to main.py in {here} "
            f"(the entry image must be in the same directory as this script)",
            file=sys.stderr,
        )
        return 1
    if not _is_jpeg(source):
        print(f"error: source is not a valid JPEG: {source}", file=sys.stderr)
        return 1

    os.makedirs(dest_dir, exist_ok=True)
    shutil.copyfile(source, dest)

    # Verify the output: size limit and JPEG magic bytes (SOI ... EOI).
    size = os.path.getsize(dest)
    if size > 1_048_576:
        print(f"error: output too large: {size} bytes (limit 1048576)", file=sys.stderr)
        return 1
    with open(dest, "rb") as fh:
        head = fh.read(2)
        fh.seek(-2, os.SEEK_END)
        tail = fh.read(2)
    if head != b"\xff\xd8" or tail != b"\xff\xd9":
        print("error: output is not a valid JPEG (bad magic bytes)", file=sys.stderr)
        return 1
    dims = _jpeg_dimensions(dest)
    dims_text = f", {dims[0]}x{dims[1]}" if dims else ", dimensions unknown"
    print(f"wrote {dest} ({size} bytes, JPEG OK{dims_text})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
