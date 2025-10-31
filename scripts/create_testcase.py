"""Generate a Windows-friendly test directory tree for the renamer tool.

Usage (PowerShell):
  python scripts/create_testcase.py --target C:\\temp\\win_testcase
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _create_files(dir_path: Path, filenames: Iterable[str]) -> None:
    for name in filenames:
        _write_text(dir_path / name, f"sample content in {name}\n")


def create_test_tree(target: Path) -> None:
    _ensure_dir(target)

    # Sibling directories include numbers and mixed alphanumerics
    top_dirs: List[str] = ["1", "2", "10", "A", "B2", "B10", "b1"]
    nested_dirs: List[str] = ["sub1", "sub10", "sub2"]
    files: List[str] = ["file.txt", "readme.md", "log10.log"]

    for td in top_dirs:
        d = target / td
        _ensure_dir(d)
        _create_files(d, files)

        # Nested structure inside each top dir
        for nd in nested_dirs:
            ndir = d / nd
            _ensure_dir(ndir)
            _create_files(ndir, files)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create test directory tree")
    parser.add_argument(
        "--target",
        type=str,
        default=str(Path.cwd() / "win_testcase"),
        help="Target path to create the test tree",
    )
    args = parser.parse_args()

    target_path = Path(args.target)
    create_test_tree(target_path)
    print(f"Test tree created under: {target_path}")


if __name__ == "__main__":
    main()


