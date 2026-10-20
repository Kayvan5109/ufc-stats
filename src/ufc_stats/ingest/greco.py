"""Download pinned snapshots of the Greco1899 UFCStats CSV mirror.

See docs/adr/0002-data-source.md for the source decision and snapshot policy.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from ufc_stats.config import RAW_DATA_DIR

SOURCE_REPO = "Greco1899/scrape_ufc_stats"
SOURCE_BRANCH = "main"
COMMIT_API_URL = f"https://api.github.com/repos/{SOURCE_REPO}/commits/{SOURCE_BRANCH}"
RAW_URL_TEMPLATE = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{{sha}}/{{filename}}"
SNAPSHOT_ROOT = RAW_DATA_DIR / "greco1899"
MANIFEST_NAME = "manifest.json"
TIMEOUT_SECONDS = 60

# Expected header row per file, as of source commit 3e2f3db (2026-10-18).
EXPECTED_COLUMNS: dict[str, list[str]] = {
    "ufc_event_details.csv": ["EVENT", "URL", "DATE", "LOCATION"],
    "ufc_fight_details.csv": ["EVENT", "BOUT", "URL"],
    "ufc_fight_results.csv": [
        "EVENT", "BOUT", "OUTCOME", "WEIGHTCLASS", "METHOD", "ROUND", "TIME",
        "TIME FORMAT", "REFEREE", "DETAILS", "URL",
    ],
    "ufc_fight_stats.csv": [
        "EVENT", "BOUT", "ROUND", "FIGHTER", "KD", "SIG.STR.", "SIG.STR. %",
        "TOTAL STR.", "TD", "TD %", "SUB.ATT", "REV.", "CTRL", "HEAD", "BODY",
        "LEG", "DISTANCE", "CLINCH", "GROUND",
    ],
    "ufc_fighter_details.csv": ["FIRST", "LAST", "NICKNAME", "URL"],
    "ufc_fighter_tott.csv": ["FIGHTER", "HEIGHT", "WEIGHT", "REACH", "STANCE", "DOB", "URL"],
}


class HttpSession(Protocol):
    def get(self, url: str, **kwargs: Any) -> Any: ...


class SchemaMismatchError(RuntimeError):
    """A downloaded file's header row differs from EXPECTED_COLUMNS."""


@dataclass(frozen=True)
class SourceCommit:
    sha: str
    date: str  # ISO 8601 committer date

    @property
    def snapshot_name(self) -> str:
        return f"{self.date[:10]}_{self.sha[:7]}"


def resolve_latest_commit(session: HttpSession) -> SourceCommit:
    response = session.get(COMMIT_API_URL, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    return SourceCommit(sha=payload["sha"], date=payload["commit"]["committer"]["date"])


def read_header(content: bytes) -> list[str]:
    first_line = content.decode("utf-8-sig").splitlines()[0] if content else ""
    return next(csv.reader([first_line]), [])


def download_snapshot(
    session: HttpSession,
    commit: SourceCommit | None = None,
    root: Path = SNAPSHOT_ROOT,
) -> Path:
    """Download all source CSVs pinned to one commit and return the snapshot directory.

    Skips the download if a complete snapshot for that commit already exists.
    Files are written to a temporary directory and only moved into place once
    every file has downloaded and passed the header check.
    """
    commit = commit or resolve_latest_commit(session)
    snapshot_dir = root / commit.snapshot_name
    if (snapshot_dir / MANIFEST_NAME).is_file():
        return snapshot_dir

    staging_dir = root / f".staging-{commit.snapshot_name}"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True)

    try:
        files = []
        for filename, expected in EXPECTED_COLUMNS.items():
            url = RAW_URL_TEMPLATE.format(sha=commit.sha, filename=filename)
            response = session.get(url, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            content: bytes = response.content

            header = read_header(content)
            if header != expected:
                raise SchemaMismatchError(
                    f"{filename} at {commit.sha[:7]}: expected columns {expected}, got {header}"
                )

            (staging_dir / filename).write_bytes(content)
            files.append(
                {
                    "name": filename,
                    "url": url,
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )

        manifest = {
            "source_repo": SOURCE_REPO,
            "commit_sha": commit.sha,
            "commit_date": commit.date,
            "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "files": files,
        }
        (staging_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        if snapshot_dir.exists():
            # Leftover from an interrupted run that never wrote a manifest.
            shutil.rmtree(snapshot_dir)
        staging_dir.rename(snapshot_dir)
    except BaseException:
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise

    return snapshot_dir
