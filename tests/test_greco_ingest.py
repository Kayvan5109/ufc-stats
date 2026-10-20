import hashlib
import json

import pytest

from ufc_stats.ingest import greco
from ufc_stats.ingest.greco import (
    COMMIT_API_URL,
    EXPECTED_COLUMNS,
    MANIFEST_NAME,
    SchemaMismatchError,
    SourceCommit,
    download_snapshot,
)

SHA = "3e2f3db5751c14b5d4ea52e41921982ca23b9b23"
COMMIT_DATE = "2026-10-18T18:02:47Z"


class FakeResponse:
    def __init__(self, content: bytes = b"", payload: dict | None = None) -> None:
        self.content = content
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


class FakeSession:
    """Serves the commit API and one small CSV per expected file."""

    def __init__(self, overrides: dict[str, bytes] | None = None) -> None:
        self.overrides = overrides or {}
        self.requested: list[str] = []

    def get(self, url: str, **kwargs) -> FakeResponse:
        self.requested.append(url)
        if url == COMMIT_API_URL:
            return FakeResponse(payload={"sha": SHA, "commit": {"committer": {"date": COMMIT_DATE}}})
        filename = url.rsplit("/", 1)[1]
        if filename in self.overrides:
            return FakeResponse(self.overrides[filename])
        return FakeResponse(fake_csv(filename))


def fake_csv(filename: str) -> bytes:
    columns = EXPECTED_COLUMNS[filename]
    return (",".join(columns) + "\n" + ",".join("x" for _ in columns) + "\n").encode()


def test_downloads_files_pinned_to_commit_sha(tmp_path) -> None:
    session = FakeSession()

    snapshot_dir = download_snapshot(session, root=tmp_path)

    assert snapshot_dir == tmp_path / f"2026-10-18_{SHA[:7]}"
    file_urls = [url for url in session.requested if url != COMMIT_API_URL]
    assert len(file_urls) == len(EXPECTED_COLUMNS)
    for url in file_urls:
        assert url.startswith(f"https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/{SHA}/")
    for filename in EXPECTED_COLUMNS:
        assert (snapshot_dir / filename).read_bytes() == fake_csv(filename)


def test_manifest_records_provenance_and_checksums(tmp_path) -> None:
    snapshot_dir = download_snapshot(FakeSession(), root=tmp_path)

    manifest = json.loads((snapshot_dir / MANIFEST_NAME).read_text(encoding="utf-8"))

    assert manifest["source_repo"] == "Greco1899/scrape_ufc_stats"
    assert manifest["commit_sha"] == SHA
    assert manifest["commit_date"] == COMMIT_DATE
    assert manifest["retrieved_at"]
    assert [entry["name"] for entry in manifest["files"]] == list(EXPECTED_COLUMNS)
    for entry in manifest["files"]:
        content = (snapshot_dir / entry["name"]).read_bytes()
        assert entry["bytes"] == len(content)
        assert entry["sha256"] == hashlib.sha256(content).hexdigest()
        assert SHA in entry["url"]


def test_header_mismatch_fails_and_leaves_no_partial_snapshot(tmp_path) -> None:
    session = FakeSession(overrides={"ufc_fight_stats.csv": b"EVENT,BOUT,RENAMED\n1,2,3\n"})

    with pytest.raises(SchemaMismatchError, match="ufc_fight_stats.csv"):
        download_snapshot(session, root=tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_rerun_for_existing_commit_is_a_noop(tmp_path) -> None:
    commit = SourceCommit(sha=SHA, date=COMMIT_DATE)
    first = download_snapshot(FakeSession(), commit=commit, root=tmp_path)
    manifest_before = (first / MANIFEST_NAME).read_text(encoding="utf-8")

    session = FakeSession()
    second = download_snapshot(session, commit=commit, root=tmp_path)

    assert second == first
    assert session.requested == []
    assert (second / MANIFEST_NAME).read_text(encoding="utf-8") == manifest_before


def test_incomplete_snapshot_without_manifest_is_replaced(tmp_path) -> None:
    commit = SourceCommit(sha=SHA, date=COMMIT_DATE)
    leftover = tmp_path / commit.snapshot_name
    leftover.mkdir()
    (leftover / "ufc_event_details.csv").write_bytes(b"truncated")

    snapshot_dir = download_snapshot(FakeSession(), commit=commit, root=tmp_path)

    assert (snapshot_dir / MANIFEST_NAME).is_file()
    assert (snapshot_dir / "ufc_event_details.csv").read_bytes() == fake_csv("ufc_event_details.csv")


def test_read_header_handles_bom_and_crlf() -> None:
    assert greco.read_header(b"\xef\xbb\xbfEVENT,URL\r\nx,y\r\n") == ["EVENT", "URL"]
