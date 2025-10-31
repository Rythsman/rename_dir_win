"""Core renaming logic for directory prefixing.

Rules:
- Only rename files (not directories).
- For each directory, compute the directory's index among its sibling
  directories under the same parent, sorted in natural order (1,2,3,10...).
- Prefix all immediate child files of that directory with "<index>_".
- Recurse into subdirectories and repeat independently at each level.
- Existing "number_" prefixes are NOT skipped; new prefixes are added again.

This module is platform-agnostic and works on Windows/Linux.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional, Tuple, Union


LogFunc = Callable[[str], None]


_DIGIT_REGEX = re.compile(r"(\d+)")


def natural_key(text: str) -> List[Union[int, str]]:
    """Return a list of tokens for natural sorting.

    Splits the input into digit and non-digit parts and converts digits to ints
    to achieve natural ordering like 1,2,3,10 instead of 1,10,2,3.

    Args:
      text: File or directory name.

    Returns:
      List of mixed str and int tokens for sort key.
    """
    parts = _DIGIT_REGEX.split(text)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def _iter_subdirs_natural(root: Path) -> Iterator[Path]:
    """Yield subdirectories under root in depth-first, natural-sorted order.

    Args:
      root: The root directory to walk.

    Yields:
      Each subdirectory path under root, depth-first, with siblings sorted in
      natural order.
    """
    try:
        subdirs = [p for p in root.iterdir() if p.is_dir()]
    except FileNotFoundError:
        return
    subdirs.sort(key=lambda p: natural_key(p.name))
    for sd in subdirs:
        yield sd
        yield from _iter_subdirs_natural(sd)


def get_folder_index_among_siblings(folder: Path) -> int:
    """Get 1-based index of a folder among its sibling directories.

    Siblings are directories under the same parent, sorted by natural order.

    Args:
      folder: Target directory.

    Returns:
      1-based index of the folder among siblings.
    """
    parent = folder.parent
    # parent may equal folder for some exotic Path, guard anyway
    if parent == folder:
        return 1
    try:
        siblings = [d for d in parent.iterdir() if d.is_dir()]
    except FileNotFoundError:
        return 1
    siblings.sort(key=lambda p: natural_key(p.name))
    try:
        return siblings.index(folder) + 1
    except ValueError:
        # If the folder is not visible among parent's entries (race/perm),
        # default to 1 to keep progress.
        return 1


def _prefix_files_in_dir(directory: Path, prefix_index: int, log: Optional[LogFunc]) -> int:
    """Prefix all immediate files in directory with "<index>_".

    Args:
      directory: Directory whose immediate child files will be renamed.
      prefix_index: The 1-based index used as prefix.
      log: Optional logging function.

    Returns:
      Number of files successfully renamed.
    """
    changed = 0
    try:
        entries = [p for p in directory.iterdir() if p.is_file()]
    except FileNotFoundError:
        return 0

    # Sort files by natural order for deterministic behavior (not required).
    entries.sort(key=lambda p: natural_key(p.name))
    for file_path in entries:
        new_name = f"{prefix_index}_{file_path.name}"
        dst = file_path.with_name(new_name)
        try:
            _safe_rename(file_path, dst)
            changed += 1
            if log:
                log(f"RENAMED: {file_path} -> {dst}")
        except Exception as exc:  # pylint: disable=broad-except
            # Intentionally broad to keep batch running; log and continue.
            if log:
                log(f"ERROR: Failed to rename {file_path}: {exc}")
    return changed


def _safe_rename(src: Path, dst: Path) -> None:
    """Rename src to dst safely, avoiding conflicts via a temporary hop.

    This avoids collisions when dst already exists or name swaps are needed.
    """
    if src == dst:
        return
    if dst.exists():
        temp = src.with_name(f"__renaming__{uuid.uuid4().hex}__{src.name}")
        src.rename(temp)
        temp.rename(dst)
    else:
        src.rename(dst)


def rename_files_in_tree(
    root: Union[str, Path],
    include_root_files: bool = False,
    log: Optional[LogFunc] = None,
) -> int:
    """Rename files across a directory tree by prefixing with parent index.

    Args:
      root: Root directory to process.
      include_root_files: Whether to also rename files directly under root.
      log: Optional logging function that receives plain text messages.

    Returns:
      Total count of files renamed across the tree.
    """
    root_path = Path(root)
    if not root_path.exists() or not root_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    total_changed = 0

    if include_root_files:
        idx = get_folder_index_among_siblings(root_path)
        if log:
            log(f"Processing root files in {root_path} with index {idx}")
        total_changed += _prefix_files_in_dir(root_path, idx, log)

    for current_dir in _iter_subdirs_natural(root_path):
        idx = get_folder_index_among_siblings(current_dir)
        if log:
            log(f"Processing {current_dir} (index among siblings: {idx})")
        total_changed += _prefix_files_in_dir(current_dir, idx, log)

    if log:
        log(f"DONE. Total files renamed: {total_changed}")
    return total_changed


