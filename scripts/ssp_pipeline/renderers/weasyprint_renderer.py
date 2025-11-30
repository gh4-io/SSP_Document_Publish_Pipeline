"""WeasyPrint PDF renderer.

Renders HTML to PDF using WeasyPrint with layout CSS and metadata.
Part of SSP Document Publishing Pipeline v4.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import logging


def render_pdf(
    html: str,
    css_paths: List[Path],
    output_path: Path,
    metadata: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Render HTML to PDF using WeasyPrint.

    Args:
        html: HTML content string
        css_paths: List of CSS file paths (layout CSS + theme CSS)
        output_path: Path for output PDF file
        metadata: Optional PDF metadata (title, author, etc.)

    Returns:
        Path to generated PDF file

    Raises:
        ImportError: If WeasyPrint not installed
        OSError: If output path cannot be written
        RuntimeError: If PDF generation fails
    """
    logger = logging.getLogger(__name__)

    # Validate WeasyPrint is available
    if not validate_weasyprint_available():
        raise ImportError("WeasyPrint is not installed. Install with: uv add weasyprint")

    # Load CSS files
    css_strings = []
    for css_path in css_paths:
        if not css_path.exists():
            logger.warning(f"CSS file not found: {css_path}, skipping")
            continue
        try:
            with css_path.open("r", encoding="utf-8") as f:
                css_strings.append(f.read())
        except Exception as e:
            logger.warning(f"Failed to load CSS {css_path}: {e}")

    # Import WeasyPrint
    try:
        from weasyprint import HTML, CSS
    except ImportError as e:
        raise ImportError(f"Failed to import WeasyPrint: {e}")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create HTML object
    try:
        html_obj = HTML(string=html)
    except Exception as e:
        raise RuntimeError(f"Failed to create HTML object: {e}")

    # Create CSS objects
    css_objs = [CSS(string=css_str) for css_str in css_strings]

    # Render PDF
    try:
        logger.info(f"Rendering PDF to {output_path}")
        html_obj.write_pdf(output_path, stylesheets=css_objs)
    except Exception as e:
        raise RuntimeError(f"PDF rendering failed: {e}")

    # Verify output was created
    if not output_path.exists():
        raise RuntimeError(f"PDF file was not created at {output_path}")

    logger.info(f"PDF successfully rendered: {output_path} ({output_path.stat().st_size} bytes)")

    return output_path


def load_css_files(css_paths: List[Path]) -> str:
    """
    Load and concatenate CSS files.

    Args:
        css_paths: List of CSS file paths

    Returns:
        Combined CSS string

    Raises:
        FileNotFoundError: If CSS file does not exist
    """
    logger = logging.getLogger(__name__)
    css_parts = []

    for css_path in css_paths:
        if not css_path.exists():
            raise FileNotFoundError(f"CSS file not found: {css_path}")

        try:
            with css_path.open("r", encoding="utf-8") as f:
                css_content = f.read()
                css_parts.append(f"/* {css_path.name} */\n{css_content}")
                logger.debug(f"Loaded CSS: {css_path}")
        except Exception as e:
            raise OSError(f"Failed to read CSS file {css_path}: {e}")

    return "\n\n".join(css_parts)


def apply_pdf_metadata(pdf_path: Path, metadata: Dict[str, Any]) -> None:
    """
    Apply metadata to PDF file.

    Note: WeasyPrint handles metadata during rendering via HTML meta tags.
    This function is provided for post-processing if needed.

    Args:
        pdf_path: Path to PDF file
        metadata: Metadata dictionary (title, author, subject, keywords)

    Raises:
        OSError: If PDF cannot be modified
    """
    # WeasyPrint handles metadata through HTML meta tags in the <head> section
    # This function is a placeholder for post-processing if needed
    # For now, metadata should be embedded in HTML before rendering
    logger = logging.getLogger(__name__)
    logger.info(f"Metadata application handled during rendering for {pdf_path}")
    pass


def validate_weasyprint_available() -> bool:
    """
    Check if WeasyPrint is installed and available.

    Returns:
        True if WeasyPrint can be imported, False otherwise
    """
    import importlib.util
    return importlib.util.find_spec("weasyprint") is not None


def configure_weasyprint(
    base_url: Optional[Path] = None,
    dpi: int = 300,
    optimize_size: bool = True
) -> Dict[str, Any]:
    """
    Configure WeasyPrint rendering options.

    Args:
        base_url: Base URL/path for resolving relative resources
        dpi: Output DPI for images and fonts
        optimize_size: Enable PDF size optimization

    Returns:
        Configuration dictionary for WeasyPrint
    """
    config = {
        "dpi": dpi,
        "optimize_size": optimize_size,
    }

    if base_url:
        config["base_url"] = str(base_url)

    return config
