# © ENG.YSWEF — yswefalhmzy@gmail.com
"""Write deterministic SHA256SUMS.txt for a flat folder of release artifacts."""

import argparse
import hashlib
import os
from pathlib import Path
import re
import sys
import tempfile


def make_sha256sums(folder):
    folder = Path(folder)
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("provide a real, flat release directory")
    output = folder / "SHA256SUMS.txt"
    if output.is_symlink():
        raise ValueError("SHA256SUMS.txt must not be a symbolic link")
    lines = []
    for path in sorted(folder.iterdir(), key=lambda item: item.name):
        if path == output:
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError("release folder may contain only regular files, not links or directories")
        if re.fullmatch(r"[A-Za-z0-9._-]+", path.name) is None or path.name.startswith("-"):
            raise ValueError("artifact filenames must be simple ASCII names without a leading hyphen")
        with path.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        lines.append(f"{digest}  {path.name}\n")
    if not lines:
        raise ValueError("release folder has no artifacts")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=folder,
                                         prefix=".sums-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.writelines(lines)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args(argv)
    try:
        print(make_sha256sums(args.folder))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Checksums not written: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
