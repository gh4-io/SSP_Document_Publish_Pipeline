"""Wikilink parsing and internal reference resolution.

Parses Obsidian/wiki-style links and resolves to document IDs or paths.
Part of SSP Document Publishing Pipeline v4.

Wikilink syntax: `[[target | display text]]` or `[[target]]`
- Target can be document ID (SOP-200), file path, or heading anchor
- Display text is optional; defaults to target if omitted

Resolves links to:
- Published PDFs (for PDF output)
- Published web pages (for HTML output)
- Section anchors within same document
"""

from pathlib import Path
from typing import Optional
import logging

# Import from parent package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.pandoc_ast import Wikilink, parse_wikilink


logger = logging.getLogger(__name__)


def resolve_wikilink_target(target: str, base_dir: Path, output_format: str = "pdf") -> str:
    """
    Resolve wikilink target to actual published document path.

    Searches published/pdf/ or published/web/ for matching documents.

    Args:
        target: Target from wikilink (e.g., "REF-2201", "SOP-200_Create_Workpackage")
        base_dir: Repository base directory
        output_format: "pdf" or "web" - determines search directory and extension

    Returns:
        Resolved path to published document (relative to published/)

    Raises:
        FileNotFoundError: If target document not found
    """
    published_dir = base_dir / "published" / output_format

    if not published_dir.exists():
        raise FileNotFoundError(f"Published directory not found: {published_dir}")

    # Determine file extension based on output format
    extension = ".pdf" if output_format == "pdf" else ".html"

    # Search strategies:
    # 1. Exact match: target.ext (e.g., "SOP-200.pdf")
    exact_match = published_dir / f"{target}{extension}"
    if exact_match.exists():
        logger.debug(f"Wikilink resolved (exact): {target} -> {exact_match}")
        return str(exact_match.relative_to(base_dir / "published"))

    # 2. Glob pattern: target*.ext (e.g., "SOP-200*.pdf" matches "SOP-200_Create_Workpackage.pdf")
    glob_matches = list(published_dir.glob(f"{target}*{extension}"))
    if glob_matches:
        resolved = glob_matches[0]  # Take first match
        if len(glob_matches) > 1:
            logger.warning(f"Multiple matches for {target}: {[m.name for m in glob_matches]}")
        logger.debug(f"Wikilink resolved (glob): {target} -> {resolved}")
        return str(resolved.relative_to(base_dir / "published"))

    # 3. Recursive search: find anywhere in published dir
    recursive_matches = list(published_dir.rglob(f"*{target}*{extension}"))
    if recursive_matches:
        resolved = recursive_matches[0]
        logger.debug(f"Wikilink resolved (recursive): {target} -> {resolved}")
        return str(resolved.relative_to(base_dir / "published"))

    # Not found
    raise FileNotFoundError(f"Wikilink target not found: {target} in {published_dir}")


def resolve_wikilink(wikilink_text: str, base_dir: Path, output_format: str = "pdf") -> Wikilink:
    """
    Parse and resolve wikilink.

    Args:
        wikilink_text: Full wikilink text (e.g., "[[REF-2201 | Config]]")
        base_dir: Repository base directory
        output_format: "pdf" or "web"

    Returns:
        Wikilink object with resolved target path

    Raises:
        ValueError: If wikilink syntax invalid
        FileNotFoundError: If target not found
    """
    # Parse wikilink syntax
    wikilink = parse_wikilink(wikilink_text)

    # Resolve target to actual file path
    try:
        resolved_path = resolve_wikilink_target(wikilink.target, base_dir, output_format)
        wikilink.target = resolved_path
    except FileNotFoundError as e:
        logger.error(f"Failed to resolve wikilink: {wikilink_text} - {e}")
        raise

    return wikilink
