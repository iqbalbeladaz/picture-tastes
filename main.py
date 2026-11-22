"""Picture Tastes entry: one perfect strawberry.

Reads the committed image.jpg next to this file and writes its bytes
to /output/entry.png (the sandbox output path required by make.fun).
Standard library only; no network access.
"""

import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "image.jpg")
    dest_dir = "/output"
    dest = os.path.join(dest_dir, "entry.png")

    if not os.path.isfile(source):
        print(f"error: source image not found: {source}", file=sys.stderr)
        return 1

    os.makedirs(dest_dir, exist_ok=True)
    shutil.copyfile(source, dest)
    print(f"wrote {dest} ({os.path.getsize(dest)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
