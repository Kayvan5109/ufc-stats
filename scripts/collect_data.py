from __future__ import annotations

from pathlib import Path

from ufc_stats.config import PROJECT_ROOT, RAW_DATA_DIR


def main() -> None:
    """Placeholder script for future ingestion work.

    This is intentionally minimal to preserve a clean structure while the project
    data source strategy is being finalized.
    """
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Raw data directory: {RAW_DATA_DIR}")
    print("Data collection entry point is ready for implementation.")


if __name__ == "__main__":
    main()
