"""Picture Tastes entry: one perfect strawberry.

How it works
------------
1. Locate ``image.jpg`` in the same directory as this file.
2. Check the source exists and is really a JPEG (magic bytes
   ``0xFFD8`` ... ``0xFFD9``); otherwise print a clear error and exit 1.
3. Copy its bytes unchanged to ``/output/entry.png`` — the sandbox
   output path required by make.fun — creating ``/output`` if needed.
4. Verify the written file: it must be at most 1,048,576 bytes and
   carry valid JPEG magic bytes, then print a one-line summary.

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


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "image.jpg")
    dest_dir = "/output"
    dest = os.path.join(dest_dir, "entry.png")

    if not os.path.isfile(source):
        print(f"error: source image not found: {source}", file=sys.stderr)
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
    print(f"wrote {dest} ({size} bytes, JPEG OK)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
