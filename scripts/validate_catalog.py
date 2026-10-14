# © ENG.YSWEF — yswefalhmzy@gmail.com
"""Validate the unchanged v1 contract plus publication safety invariants."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator, FormatChecker
import rfc3339_validator  # Ensure date-time validation is not silently unavailable.

ROOT = Path(__file__).resolve().parents[1]
SAFE_COMPONENT = re.compile(r"[A-Za-z0-9._-]+")
RELEASE_URL = re.compile(
    r"https://github\.com/yswef/([A-Za-z0-9._-]+)/releases/download/"
    r"([^/?#\s]+)/([A-Za-z0-9._-]+)"
)
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{n}" for prefix in ("COM", "LPT") for n in range(1, 10)
}


def safe_component(value):
    """Accept a single, unambiguous Windows filename or directory component."""
    return (
        isinstance(value, str)
        and SAFE_COMPONENT.fullmatch(value) is not None
        and value not in {".", ".."}
        and not value.endswith(".")
        and value.split(".")[0].upper() not in RESERVED
    )


def validate_release_url(url, asset=None):
    """Reject parser ambiguities; return the asset name without fetching anything."""
    match = RELEASE_URL.fullmatch(url) if isinstance(url, str) else None
    if match is None:
        raise ValueError("release.url must be an HTTPS github.com/yswef Release asset URL")
    repo, tag, filename = match.groups()
    parsed = urlsplit(url)
    decoded_tag = unquote(tag, errors="strict")
    if (
        parsed.netloc != "github.com"
        or repo in {".", ".."}
        or decoded_tag in {".", ".."}
        or any(c in decoded_tag for c in "/\\%?#")
        or any(ord(c) <= 32 or ord(c) == 127 for c in decoded_tag)
        or not safe_component(filename)
    ):
        raise ValueError("release.url contains an unsafe path component")
    if asset is not None and filename != asset:
        raise ValueError("release.asset must match the filename in release.url")
    return filename


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"non-JSON number: {value}")


def load_json(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=_unique_pairs,
        parse_constant=_reject_constant,
    )


def validate_catalog(catalog, schema=None):
    """Return all validation errors; a schema-only client is less restrictive."""
    if schema is None:
        schema = load_json(ROOT / "catalog.schema.json")
    Draft202012Validator.check_schema(schema)
    errors = [
        f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(catalog)
    ]
    if errors:
        return errors  # Shape checks must succeed before accessing typed fields.
    ids = [tool["id"] for tool in catalog["tools"]]
    if len(ids) != len(set(ids)):
        errors.append("tools: duplicate ids")
    if ids != sorted(ids):
        errors.append("tools: must be sorted by id")
    for tool in catalog["tools"]:
        prefix = tool["id"]
        for field in ("id", "version"):
            pattern = schema["properties"]["tools"]["items"]["properties"][field]["pattern"]
            if re.fullmatch(pattern, tool[field]) is None:
                errors.append(f"{prefix}: {field} must match the entire pattern")
        release = tool["release"]
        try:
            validate_release_url(release["url"], release["asset"])
        except ValueError as exc:
            errors.append(f"{prefix}: {exc}")
        if re.fullmatch(r"[a-f0-9]{64}", release["sha256"]) is None:
            errors.append(f"{prefix}: sha256 must be 64 lowercase hexadecimal characters")
        if "data_dir" in tool:
            match = re.fullmatch(r"%APPDATA%\\YSWEF\\([A-Za-z0-9._-]+)", tool["data_dir"])
            if match is None or not safe_component(match.group(1)):
                errors.append(f"{prefix}: unsafe data_dir")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", nargs="?", type=Path, default=ROOT / "catalog.json")
    parser.add_argument("--schema", type=Path, default=ROOT / "catalog.schema.json")
    args = parser.parse_args(argv)
    try:
        errors = validate_catalog(load_json(args.catalog), load_json(args.schema))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Validation failed: {exc}\n")
    if errors:
        parser.exit(1, "Validation failed:\n" + "\n".join(errors) + "\n")
    print("Catalog and draft 2020-12 schema are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
