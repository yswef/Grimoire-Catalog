# © ENG.YSWEF — yswefalhmzy@gmail.com
"""Offline contract, policy, CLI and helper regression tests."""

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from urllib.request import Request

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import add_tool, make_sha256sums, validate_catalog as validator


@pytest.fixture
def catalog():
    return {
        "schema_version": 1,
        "generated_at": "2026-10-10T00:00:00Z",
        "tools": [{
            "id": "example-tool", "name": "Example Tool", "version": "1.0.0",
            "description": "A test tool", "license": "Proprietary",
            "name_i18n": {"ar": "أداة مثال", "en": "Example Tool"},
            "data_dir": "%APPDATA%\\YSWEF\\ExampleTool",
            "release": {
                "url": "https://github.com/yswef/example-tool/releases/download/v1.0.0/Example.exe",
                "asset": "Example.exe", "sha256": "a" * 64, "size": 123, "kind": "installer",
            },
        }],
    }


def test_valid(catalog):
    assert validator.validate_catalog(catalog) == []


def test_empty_catalog_and_metaschema():
    schema = validator.load_json(ROOT / "catalog.schema.json")
    Draft202012Validator.check_schema(schema)
    assert validator.validate_catalog(validator.load_json(ROOT / "catalog.json"), schema) == []


@pytest.mark.parametrize("sha", ["", "a" * 63, "A" * 64, "g" * 64, "a" * 64 + "\n"])
def test_invalid_sha(catalog, sha):
    catalog["tools"][0]["release"]["sha256"] = sha
    assert validator.validate_catalog(catalog)


@pytest.mark.parametrize("url", [
    "http://github.com/yswef/tool/releases/download/v1/Example.exe",
    "https://evil.example/yswef/tool/releases/download/v1/Example.exe",
    "https://github.com.evil.example/yswef/tool/releases/download/v1/Example.exe",
    "https://github.com@evil.example/yswef/tool/releases/download/v1/Example.exe",
    "https://github.com/another/tool/releases/download/v1/Example.exe",
    "https://github.com:443/yswef/tool/releases/download/v1/Example.exe",
    "https://github.com/yswef/tool/releases/download/v1/Example.exe?x=1",
    "https://github.com/yswef/tool/releases/download/v1/Example.exe#fragment",
    "https://github.com/yswef/tool/releases/download/../Example.exe",
    "https://github.com/yswef/tool/releases/download/%2e%2e/Example.exe",
    "https://github.com/yswef/tool/releases/download/v1%2Fv2/Example.exe",
    "https://github.com/yswef/tool/releases/download/v1%255cfoo/Example.exe",
    "https://github.com/yswef/tool/releases/download/v1/Other.exe",
    "https://github.com/yswef/tool/releases/download/v1/Example.exe\n",
])
def test_wrong_host_or_unsafe_url(catalog, url):
    catalog["tools"][0]["release"]["url"] = url
    assert validator.validate_catalog(catalog)


def test_duplicate_id(catalog):
    catalog["tools"].append(deepcopy(catalog["tools"][0]))
    assert any("duplicate" in error for error in validator.validate_catalog(catalog))


def test_unsorted(catalog):
    other = deepcopy(catalog["tools"][0])
    other["id"] = "another-tool"
    catalog["tools"].append(other)
    assert any("sorted" in error for error in validator.validate_catalog(catalog))


@pytest.mark.parametrize("directory", [
    "C:\\Windows", "%APPDATA%\\Other\\Tool", "%APPDATA%\\YSWEF\\..\\Escape",
    "%APPDATA%\\YSWEF\\..", "%APPDATA%\\YSWEF\\.", "%APPDATA%\\YSWEF\\CON",
    "%APPDATA%\\YSWEF\\nul.txt", "%APPDATA%\\YSWEF\\Tool.",
    "%APPDATA%\\YSWEF\\Tool\n", "%APPDATA%/YSWEF/Tool",
])
def test_bad_data_dir(catalog, directory):
    catalog["tools"][0]["data_dir"] = directory
    assert validator.validate_catalog(catalog)


@pytest.mark.parametrize("timestamp", ["yesterday", "2026-02-30T00:00:00Z", "2026-10-10T00:00:00"])
def test_invalid_timestamp(catalog, timestamp):
    catalog["generated_at"] = timestamp
    assert validator.validate_catalog(catalog)


@pytest.mark.parametrize("field", ["unexpected", "$comment"])
def test_unknown_top_level_field(catalog, field):
    catalog[field] = "not allowed"
    assert validator.validate_catalog(catalog)


@pytest.mark.parametrize("target", ["tool", "release"])
def test_unknown_nested_field(catalog, target):
    obj = catalog["tools"][0]
    if target == "release":
        obj = obj["release"]
    obj["unexpected"] = True
    assert validator.validate_catalog(catalog)


@pytest.mark.parametrize("data", [None, [], {"tools": []}, {"schema_version": 1, "generated_at": 0, "tools": []}])
def test_wrong_shape(data):
    assert validator.validate_catalog(data)


@pytest.mark.parametrize("text", ['{"tools": [], "tools": []}', '{"size": NaN}'])
def test_ambiguous_json(tmp_path, text):
    path = tmp_path / "input.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        validator.load_json(path)


def test_validator_cli(tmp_path, catalog):
    good = subprocess.run([sys.executable, str(ROOT / "scripts/validate_catalog.py")], capture_output=True)
    assert good.returncode == 0
    catalog["tools"][0]["release"]["size"] = 0
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    bad = subprocess.run([sys.executable, str(ROOT / "scripts/validate_catalog.py"), str(path)], capture_output=True)
    assert bad.returncode == 1
    assert b"Validation failed" in bad.stderr


@pytest.mark.parametrize("url", [
    "https://evil.example/file", "http://release-assets.githubusercontent.com/file",
    "https://release-assets.githubusercontent.com.evil.example/file",
    "https://user@release-assets.githubusercontent.com/file",
    "https://objects.githubusercontent.com:443/file", "https://github.com/another/tool",
    "https://release-assets.githubusercontent.com/file#fragment",
])
def test_redirect_rejected(url):
    handler = add_tool.ReleaseRedirectHandler()
    with pytest.raises(ValueError):
        handler.redirect_request(Request("https://github.com/yswef/tool/releases/download/v1/file.exe"),
                                 None, 302, "Found", {}, url)


@pytest.mark.parametrize("host", sorted(add_tool.CDN_HOSTS))
def test_github_cdn_redirect_allowed(host):
    url = f"https://{host}/assets/file?download=1"
    handler = add_tool.ReleaseRedirectHandler()
    redirected = handler.redirect_request(
        Request("https://github.com/yswef/tool/releases/download/v1/file.exe"), None, 302, "Found", {}, url)
    assert redirected.full_url == url


class FakeResponse(io.BytesIO):
    status = 200

    def __init__(self, body, headers):
        super().__init__(body)
        self.headers = headers

    def geturl(self):
        return "https://release-assets.githubusercontent.com/assets/file"


def mock_download(monkeypatch, body, headers):
    class FakeOpener:
        def open(self, request, timeout):
            assert timeout == 30
            return FakeResponse(body, headers)
    monkeypatch.setattr(add_tool, "build_opener", lambda *handlers: FakeOpener())


def test_fetch_digest(monkeypatch):
    mock_download(monkeypatch, b"abc", {"Content-Length": "3"})
    assert add_tool.fetch_digest("https://github.com/yswef/tool/releases/download/v1/file.exe", 10) == (
        hashlib.sha256(b"abc").hexdigest(), 3)


@pytest.mark.parametrize("body,headers,limit", [
    (b"", {}, 10), (b"abc", {"Content-Length": "4"}, 10),
    (b"abc", {"Content-Length": "11"}, 10), (b"abc", {}, 2),
    (b"abc", {"Content-Encoding": "gzip"}, 10),
])
def test_bad_download(monkeypatch, body, headers, limit):
    mock_download(monkeypatch, body, headers)
    with pytest.raises(ValueError):
        add_tool.fetch_digest("https://github.com/yswef/tool/releases/download/v1/file.exe", limit)


def cli_args(path, tool_id="another-tool"):
    return ["--catalog", str(path), "--id", tool_id, "--name", "Another Tool",
            "--version", "2.0.0", "--description", "A tool", "--license", "Proprietary",
            "--url", "https://github.com/yswef/tool/releases/download/v2/file.exe"]


def test_add_update_sorted_preserves_translations(tmp_path, monkeypatch, catalog):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setattr(add_tool, "fetch_digest", lambda *args: ("b" * 64, 456))
    assert add_tool.main(cli_args(path) + ["--name-ar", "أداة", "--kind", "portable"]) == 0
    assert add_tool.main(cli_args(path)) == 0
    data = validator.load_json(path)
    assert validator.validate_catalog(data) == []
    assert [t["id"] for t in data["tools"]] == ["another-tool", "example-tool"]
    assert data["tools"][0]["name_i18n"]["ar"] == "أداة"
    assert data["tools"][0]["release"]["kind"] == "portable"
    assert data["tools"][0]["release"]["sha256"] == "b" * 64
    assert data["tools"][0]["release"]["size"] == 456
    assert data["generated_at"] != catalog["generated_at"]


def test_failed_download_leaves_catalog_unchanged(tmp_path, monkeypatch, catalog):
    path = tmp_path / "catalog.json"
    original = json.dumps(catalog).encode()
    path.write_bytes(original)
    def fail(*args):
        raise OSError("simulated network failure")
    monkeypatch.setattr(add_tool, "fetch_digest", fail)
    with pytest.raises(SystemExit) as exc:
        add_tool.main(cli_args(path))
    assert exc.value.code == 1
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_invalid_input_is_not_downloaded(tmp_path, monkeypatch, catalog):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    def unexpected(*args):
        pytest.fail("network called before metadata validation")
    monkeypatch.setattr(add_tool, "fetch_digest", unexpected)
    with pytest.raises(SystemExit):
        add_tool.main(cli_args(path, "INVALID"))


def test_atomic_write_failure(tmp_path, monkeypatch):
    path = tmp_path / "catalog.json"
    path.write_bytes(b"original")
    def fail(*args):
        raise OSError("simulated replacement failure")
    monkeypatch.setattr(add_tool.os, "replace", fail)
    with pytest.raises(OSError):
        add_tool.write_catalog(path, {})
    assert path.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [path]


def test_make_sha256sums(tmp_path):
    (tmp_path / "b.exe").write_bytes(b"abc")
    (tmp_path / "a.exe").write_bytes(b"def")
    output = make_sha256sums.make_sha256sums(tmp_path)
    expected = "".join(f"{hashlib.sha256(body).hexdigest()}  {name}\n"
                       for name, body in [("a.exe", b"def"), ("b.exe", b"abc")])
    assert output.read_text() == expected
    make_sha256sums.make_sha256sums(tmp_path)
    assert output.read_text() == expected


@pytest.mark.parametrize("kind", ["empty", "nested", "symlink", "unsafe-name", "output-symlink"])
def test_bad_checksums_folder(tmp_path, kind):
    if kind == "nested":
        (tmp_path / "nested").mkdir()
    elif kind == "symlink":
        (tmp_path / "link.exe").symlink_to(tmp_path / "missing")
    elif kind == "unsafe-name":
        (tmp_path / "bad name.exe").write_bytes(b"abc")
    elif kind == "output-symlink":
        (tmp_path / "SHA256SUMS.txt").symlink_to(tmp_path / "missing")
    with pytest.raises(ValueError):
        make_sha256sums.make_sha256sums(tmp_path)
