# © ENG.YSWEF — yswefalhmzy@gmail.com
"""Add/update a tool after streaming and hashing its public GitHub Release asset."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

if __package__:
    from .validate_catalog import ROOT, load_json, validate_catalog, validate_release_url
else:
    from validate_catalog import ROOT, load_json, validate_catalog, validate_release_url

CDN_HOSTS = {"release-assets.githubusercontent.com", "objects.githubusercontent.com"}


def validate_download_url(url):
    """Only the initial owned Release URL or GitHub's explicit asset CDN hosts."""
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port is not None
        or parsed.fragment
        or any(ord(c) <= 32 or ord(c) == 127 for c in url)
        or "\\" in url
    ):
        raise ValueError("unsafe download redirect")
    if parsed.netloc == "github.com":
        validate_release_url(url)
    elif parsed.netloc not in CDN_HOSTS:
        raise ValueError("download redirect host is not allowlisted")


class ReleaseRedirectHandler(HTTPRedirectHandler):
    max_redirections = 5

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_download_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_digest(url, max_bytes):
    validate_release_url(url)
    opener = build_opener(ReleaseRedirectHandler())
    request = Request(url, headers={"User-Agent": "Grimoire-Catalog/1", "Accept-Encoding": "identity"})
    digest = hashlib.sha256()
    size = 0
    deadline = time.monotonic() + 300
    with opener.open(request, timeout=30) as response:
        validate_download_url(response.geturl())
        if response.status != 200:
            raise ValueError("asset download did not return HTTP 200")
        if response.headers.get("Content-Encoding", "identity").lower() != "identity":
            raise ValueError("encoded downloads are not supported")
        content_length = response.headers.get("Content-Length")
        expected = int(content_length) if content_length is not None else None
        if expected is not None and not 1 <= expected <= max_bytes:
            raise ValueError("asset Content-Length is outside the allowed size")
        while chunk := response.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes or time.monotonic() > deadline:
                raise ValueError("asset exceeds the download size or time limit")
            digest.update(chunk)
    if size == 0 or (expected is not None and size != expected):
        raise ValueError("asset is empty or truncated")
    return digest.hexdigest(), size


def write_catalog(path, catalog):
    """Replace only after a complete write; never truncate an existing catalog."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                                         prefix=".catalog-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(catalog, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("id", "name", "version", "description", "license", "url"):
        parser.add_argument(f"--{field}", required=True)
    parser.add_argument("--catalog", type=Path, default=ROOT / "catalog.json")
    parser.add_argument("--kind", choices=("installer", "portable"))
    parser.add_argument("--min-windows")
    parser.add_argument("--data-dir")
    for field in ("name", "description"):
        for language in ("ar", "en"):
            parser.add_argument(f"--{field}-{language}")
    parser.add_argument("--max-bytes", type=int, default=2 * 1024**3)
    args = parser.parse_args(argv)
    try:
        if args.max_bytes < 1:
            raise ValueError("--max-bytes must be positive")
        if args.catalog.is_symlink():
            raise ValueError("catalog must not be a symbolic link")
        original = args.catalog.read_bytes()
        catalog = load_json(args.catalog)
        errors = validate_catalog(catalog)
        if errors:
            raise ValueError("existing catalog is invalid: " + "; ".join(errors))
        tool = next((item for item in catalog["tools"] if item["id"] == args.id), {})
        for field in ("id", "name", "version", "description", "license"):
            tool[field] = getattr(args, field)
        for field in ("min_windows", "data_dir"):
            if getattr(args, field) is not None:
                tool[field] = getattr(args, field)
        for field in ("name", "description"):
            for language in ("ar", "en"):
                value = getattr(args, f"{field}_{language}")
                if value is not None:
                    tool.setdefault(f"{field}_i18n", {})[language] = value
        kind = args.kind or tool.get("release", {}).get("kind", "installer")
        tool["release"] = {
            "url": args.url, "asset": validate_release_url(args.url),
            "sha256": "0" * 64, "size": 1, "kind": kind,
        }
        catalog["tools"] = sorted(
            [item for item in catalog["tools"] if item["id"] != args.id] + [tool],
            key=lambda item: item["id"],
        )
        errors = validate_catalog(catalog)
        if errors:
            raise ValueError("; ".join(errors))
        digest, size = fetch_digest(args.url, args.max_bytes)
        tool["release"].update(sha256=digest, size=size)
        catalog["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        errors = validate_catalog(catalog)
        if errors:
            raise ValueError("; ".join(errors))
        if args.catalog.is_symlink() or args.catalog.read_bytes() != original:
            raise ValueError("catalog changed during download; retry with no concurrent writers")
        write_catalog(args.catalog, catalog)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Tool not added: {exc}\n")
    print(f"Updated {args.id}: sha256={digest}, size={size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
