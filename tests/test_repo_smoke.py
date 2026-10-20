from pathlib import Path

from ufc_stats import __version__
from ufc_stats.config import DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR


def test_package_version_is_defined() -> None:
    assert isinstance(__version__, str)
    assert __version__.startswith("0.")


def test_repo_structure_directories_exist() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "src").is_dir()
    assert (root / "scripts").is_dir()
    assert (root / "docs").is_dir()
    assert DATA_DIR.is_dir()
    assert RAW_DATA_DIR.is_dir()
    assert PROCESSED_DATA_DIR.is_dir()
