"""CSS layout builder.

Generates CSS from extracted Scribus frame data for WeasyPrint rendering.
Part of SSP Document Publishing Pipeline v4.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def build_layout_css(frames: Dict[str, Any], page_size: str = "letter") -> str:
    """
    Generate CSS from Scribus frame geometry.

    Args:
        frames: Frame definitions from scribus_extractor or layout profile JSON
                Expected structure: {frame_name: {x, y, width, height, font, fontsize, ...}}
        page_size: Page size (letter, a4, etc.)

    Returns:
        CSS string with @page rules and frame positioning

    Raises:
        ValueError: If frame data invalid
    """
    if not isinstance(frames, dict):
        raise ValueError("frames must be a dictionary")

    logger.info(f"Generating CSS for {len(frames)} frames, page size: {page_size}")

    css_parts = []

    # Generate @page rules
    page_margins = {"top": 0.5, "right": 0.5, "bottom": 0.5, "left": 0.5}  # inches
    css_parts.append(generate_page_rules(page_size, page_margins))

    # Generate frame CSS
    for frame_name, frame_data in frames.items():
        try:
            css_parts.append(generate_frame_css(frame_name, frame_data))
        except Exception as e:
            logger.warning(f"Skipping frame '{frame_name}': {e}")

    css_output = "\n\n".join(css_parts)
    logger.debug(f"Generated {len(css_output)} characters of CSS")

    return css_output


def generate_page_rules(page_size: str, margins: Dict[str, float]) -> str:
    """
    Generate CSS @page rules for PDF layout.

    Args:
        page_size: Page size identifier (letter, a4, legal)
        margins: Dictionary with top, right, bottom, left margins (in inches)

    Returns:
        CSS @page rule string
    """
    # Map page sizes to dimensions
    page_dimensions = {
        "letter": "8.5in 11in",
        "a4": "210mm 297mm",
        "legal": "8.5in 14in"
    }

    size = page_dimensions.get(page_size.lower(), "8.5in 11in")

    margin_str = f"{margins.get('top', 0.5)}in {margins.get('right', 0.5)}in " \
                 f"{margins.get('bottom', 0.5)}in {margins.get('left', 0.5)}in"

    return f"""@page {{
    size: {size};
    margin: {margin_str};
}}"""


def generate_frame_css(frame_name: str, frame_data: Dict[str, Any]) -> str:
    """
    Generate CSS for single frame.

    Args:
        frame_name: Frame identifier
        frame_data: Frame geometry and style data
                    Expected keys: x, y, width, height (in inches or points)
                    Optional: font, fontsize, role

    Returns:
        CSS rule for the frame
    """
    # Extract geometry (assume inches by default, convert if points)
    x = frame_data.get("x", 0)
    y = frame_data.get("y", 0)
    width = frame_data.get("width", 1)
    height = frame_data.get("height", 1)

    # Generate CSS class name from frame name (sanitize)
    class_name = frame_name.replace(" ", "-").replace("_", "-").lower()

    css = f""".frame-{class_name} {{
    position: absolute;
    left: {x}in;
    top: {y}in;
    width: {width}in;
    height: {height}in;"""

    # Add optional styles
    if "font" in frame_data:
        css += f"\n    font-family: '{frame_data['font']}';"

    if "fontsize" in frame_data:
        css += f"\n    font-size: {frame_data['fontsize']}pt;"

    if "role" in frame_data:
        css += f"\n    /* role: {frame_data['role']} */"

    css += "\n}"

    return css


def convert_points_to_units(points: float, unit: str = "mm") -> float:
    """
    Convert points to CSS units.

    Args:
        points: Value in points (1 point = 1/72 inch)
        unit: Target unit (mm, cm, in, px)

    Returns:
        Converted value

    Raises:
        ValueError: If unit not supported
    """
    # 1 point = 1/72 inch
    inches = points / 72.0

    conversions = {
        "in": inches,
        "mm": inches * 25.4,
        "cm": inches * 2.54,
        "px": points * 1.333,  # Assuming 96 DPI
        "pt": points
    }

    if unit not in conversions:
        raise ValueError(f"Unsupported unit '{unit}'. Valid: {list(conversions.keys())}")

    return conversions[unit]


def generate_text_styles_css(text_styles: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate CSS from Scribus text styles.

    Args:
        text_styles: Text style definitions from scribus_extractor
                     Expected structure: {style_name: {font, size, color, ...}}

    Returns:
        CSS string with text style classes
    """
    if not text_styles:
        return "/* No text styles defined */"

    css_parts = []

    for style_name, style_props in text_styles.items():
        class_name = style_name.replace(" ", "-").replace("_", "-").lower()

        css = f".text-{class_name} {{"

        if "font" in style_props:
            css += f"\n    font-family: '{style_props['font']}';"

        if "size" in style_props:
            css += f"\n    font-size: {style_props['size']}pt;"

        if "color" in style_props:
            css += f"\n    color: {style_props['color']};"

        if "weight" in style_props:
            css += f"\n    font-weight: {style_props['weight']};"

        css += "\n}"
        css_parts.append(css)

    return "\n\n".join(css_parts)


def merge_css_files(css_files: List[Path], output_path: Path) -> Path:
    """
    Merge multiple CSS files into one.

    Args:
        css_files: List of CSS file paths to merge
        output_path: Path for merged output CSS

    Returns:
        Path to merged CSS file

    Raises:
        FileNotFoundError: If input CSS file missing
        OSError: If output cannot be written
    """
    logger.info(f"Merging {len(css_files)} CSS files → {output_path}")

    merged_content = []

    for css_file in css_files:
        if not css_file.exists():
            raise FileNotFoundError(f"CSS file not found: {css_file}")

        logger.debug(f"Reading {css_file}")

        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            merged_content.append(f"/* From: {css_file.name} */")
            merged_content.append(content)
            merged_content.append("")  # Blank line separator

    # Write merged output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(merged_content))

    logger.info(f"Merged CSS written to {output_path}")
    return output_path


def validate_css_syntax(css_content: str) -> bool:
    """
    Validate CSS syntax (basic validation).

    Args:
        css_content: CSS string to validate

    Returns:
        True if valid

    Raises:
        ValueError: If CSS syntax invalid
    """
    # Basic validation: check for balanced braces
    open_braces = css_content.count('{')
    close_braces = css_content.count('}')

    if open_braces != close_braces:
        raise ValueError(
            f"Unbalanced braces in CSS: {open_braces} open, {close_braces} close"
        )

    # Check for empty content
    if not css_content.strip():
        raise ValueError("CSS content is empty")

    # If validation passes
    logger.debug("CSS syntax validation passed")
    return True
