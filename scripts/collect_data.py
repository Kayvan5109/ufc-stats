"""Download the latest Greco1899 UFCStats CSV snapshot into data/raw/greco1899/."""

from __future__ import annotations

import json

import requests

from ufc_stats.ingest.greco import MANIFEST_NAME, download_snapshot


def main() -> None:
    with requests.Session() as session:
        session.headers["User-Agent"] = "ufc-stats-research (+https://github.com/Kayvan5109/ufc-stats)"
        snapshot_dir = download_snapshot(session)

    manifest = json.loads((snapshot_dir / MANIFEST_NAME).read_text(encoding="utf-8"))
    print(f"Snapshot: {snapshot_dir}")
    print(f"Source:   {manifest['source_repo']} @ {manifest['commit_sha'][:7]} ({manifest['commit_date']})")
    for entry in manifest["files"]:
        print(f"  {entry['name']:<26} {entry['bytes']:>12,} bytes")


if __name__ == "__main__":
    main()
