"""Image reference parsing and path resolution.

Parses image syntax from Pandoc AST and resolves paths from assets directory.
Part of SSP Document Publishing Pipeline v4.

Handles both standard Markdown images and Obsidian wikilink images:
- `![alt](path/to/image.png)` - Standard Markdown
- `![[image.png]]` - Obsidian wikilink syntax

Resolves relative paths against assets/images/ directory structure.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Import from parent package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.file_ops import resolve_asset_path
from parsers.pandoc_ast import Image


logger = logging.getLogger(__name__)


def parse_image_element(image_data: Dict[str, Any], base_dir: Path) -> Optional[Image]:
    """
    Parse Pandoc Image element and resolve asset path.

    Pandoc Image structure:
    {"t": "Image", "c": [[id, classes, kvpairs], [inline_elements], [target, title]]}

    Args:
        image_data: Pandoc Image element dictionary
        base_dir: Repository base directory for path resolution

    Returns:
        Image block with resolved path, or None if resolution fails
    """
    if image_data.get("t") != "Image":
        return None

    content = image_data.get("c", [])
    if len(content) < 3:
        logger.warning("Invalid Image element structure")
        return None

    # Extract components
    attrs = content[0]  # [id, classes, key-value pairs]
    alt_inlines = content[1]  # List of inline elements for alt text
    target_info = content[2]  # [target_path, title]

    target_path = target_info[0]
    title = target_info[1] if len(target_info) > 1 else None

    # Extract alt text from inline elements
    from parsers.pandoc_ast import extract_inline_text
    alt_text = extract_inline_text(alt_inlines) if alt_inlines else None

    # Resolve relative path to absolute
    try:
        resolved_path = resolve_asset_path(target_path, base_dir, asset_type="images")
        return Image(path=str(resolved_path), alt_text=alt_text, caption=title)
    except FileNotFoundError as e:
        logger.warning(f"Image not found: {target_path} - {e}")
        # Return placeholder path
        return Image(path=target_path, alt_text=alt_text, caption=title)


def parse_obsidian_image(wikilink_text: str, base_dir: Path) -> Optional[Image]:
    """
    Parse Obsidian wikilink image syntax: ![[image.png]]

    Args:
        wikilink_text: Wikilink text (e.g., "![[Screenshot.png]]")
        base_dir: Repository base directory for path resolution

    Returns:
        Image block with resolved path
    """
    # Strip ![[  and ]]
    if not (wikilink_text.startswith("![[") and wikilink_text.endswith("]]")):
        logger.warning(f"Invalid Obsidian image syntax: {wikilink_text}")
        return None

    filename = wikilink_text[3:-2].strip()

    # Resolve path
    try:
        resolved_path = resolve_asset_path(filename, base_dir, asset_type="images")
        return Image(path=str(resolved_path), alt_text=filename)
    except FileNotFoundError as e:
        logger.warning(f"Obsidian image not found: {filename} - {e}")
        return Image(path=filename, alt_text=filename)
