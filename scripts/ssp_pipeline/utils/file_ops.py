"""File and path operations.

Utilities for managing files, directories, and asset resolution.
Part of SSP Document Publishing Pipeline v4.
"""

import shutil
from datetime import datetime
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists

    Returns:
        The same path (for chaining)

    Raises:
        OSError: If directory cannot be created
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_asset_path(relative_path: str, base_dir: Path, asset_type: str = "images") -> Path:
    """
    Resolve relative asset path to absolute path.

    Args:
        relative_path: Relative path from Markdown (e.g., "Screenshot.png")
        base_dir: Base directory (typically repo root)
        asset_type: Asset subdirectory (images, fonts, web, etc.)

    Returns:
        Absolute path to asset

    Raises:
        FileNotFoundError: If asset does not exist
    """
    assets_dir = base_dir / "assets" / asset_type

    # Search subdirectories (global, doc, project, etc.)
    search_dirs = [
        assets_dir / "global",
        assets_dir / "doc",
        assets_dir / "project",
        assets_dir,  # Also check root of asset type
    ]

    for search_dir in search_dirs:
        # Check direct match
        asset_path = search_dir / relative_path
        if asset_path.exists():
            return asset_path

        # Check recursive subdirectories (e.g., assets/images/doc/SOP-001/file.png)
        for subdir_match in search_dir.rglob(relative_path):
            if subdir_match.is_file():
                return subdir_match

    raise FileNotFoundError(f"Asset not found: {relative_path} in {assets_dir}")


def copy_to_published(source_path: Path, output_type: str, doc_id: str) -> Path:
    """
    Copy output file to published directory with standardized naming.

    Args:
        source_path: Generated file to copy
        output_type: "pdf" or "web"
        doc_id: Document ID (e.g., "SOP-200")

    Returns:
        Path to copied file in published directory

    Raises:
        OSError: If copy fails
    """
    # Determine published directory (published/pdf or published/web)
    published_dir = source_path.parent.parent.parent / "published" / output_type
    ensure_dir(published_dir)

    # Copy with standardized naming
    ext = ".pdf" if output_type == "pdf" else ".html"
    dest_path = published_dir / f"{doc_id}{ext}"
    shutil.copy2(source_path, dest_path)

    return dest_path


def archive_to_releases(source_path: Path, doc_type: str, doc_id: str, version: str) -> Path:
    """
    Archive output to releases with timestamp.

    Args:
        source_path: File to archive
        doc_type: Document type (SOP, STD, REF, APP)
        doc_id: Document ID
        version: Version string (e.g., "1.0")

    Returns:
        Path to archived file

    Raises:
        OSError: If archive fails
    """
    # Create timestamped release directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    releases_dir = source_path.parent.parent.parent / "releases" / doc_type
    release_subdir = releases_dir / f"{doc_id}_v{version}_{timestamp}"
    ensure_dir(release_subdir)

    # Copy file to release directory (preserving metadata)
    dest_path = release_subdir / source_path.name
    shutil.copy2(source_path, dest_path)

    return dest_path
