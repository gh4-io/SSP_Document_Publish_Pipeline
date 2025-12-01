"""Legacy Scribus renderer (fallback mode).

Renders documents using Scribus Python scripting API for compatibility.
Part of SSP Document Publishing Pipeline v4.

This renderer is a **fallback option** for cases where WeasyPrint cannot be used.
The primary rendering engine is WeasyPrint (see weasyprint_renderer.py).

Scribus rendering workflow:
1. Open Scribus template (.sla file)
2. Populate text frames with parsed content from blocks
3. Apply paragraph styles from layout profile
4. Insert images into image frames
5. Export to PDF

Note: Scribus rendering is slower and less flexible than WeasyPrint.
Use only when explicitly specified in layout profile (`rendering_engine: "scribus"`).
"""

import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def render_pdf_from_sla(
    sla_template: Path,
    blocks: List[Any],
    metadata: Dict[str, Any],
    output_path: Path,
    styles_map: Dict[str, Any]
) -> Path:
    """
    Render PDF from Scribus .sla template.

    Args:
        sla_template: Path to Scribus .sla template file
        blocks: Parsed document blocks
        metadata: Document metadata
        output_path: Output PDF path
        styles_map: Style mappings from profile

    Returns:
        Path to generated PDF

    Raises:
        NotImplementedError: Scribus rendering not yet fully implemented
        FileNotFoundError: If .sla template not found
    """
    if not sla_template.exists():
        raise FileNotFoundError(f"Scribus template not found: {sla_template}")

    logger.warning(
        f"Scribus rendering requested but not yet implemented. "
        f"Template: {sla_template}"
    )
    logger.info(
        "Scribus rendering requires:\n"
        "  1. Scribus installed (scribus-ng or scribus 1.5+)\n"
        "  2. Python bindings or script runner\n"
        "  3. Frame population logic\n"
        f"Found {len(blocks)} blocks and {len(metadata)} metadata fields"
    )

    raise NotImplementedError(
        f"Scribus rendering not yet implemented. "
        f"Template available: {sla_template}\n"
        f"To use this profile, either:\n"
        f"  1. Implement scribus_renderer.py\n"
        f"  2. Add 'rendering_engine: weasyprint' to profile\n"
        f"  3. Remove 'scribus_template' from profile resources"
    )
