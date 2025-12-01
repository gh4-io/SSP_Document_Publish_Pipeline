"""Input validation.

Validates Markdown files, layout profiles, and pipeline inputs.
Part of SSP Document Publishing Pipeline v4.
"""

from pathlib import Path
from typing import Dict, List, Any


def validate_markdown(md_path: Path) -> bool:
    """
    Validate Markdown file exists and has required front matter.

    Args:
        md_path: Path to Markdown file

    Returns:
        True if valid

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If front matter is missing or invalid
    """
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    if not md_path.is_file():
        raise ValueError(f"Path is not a file: {md_path}")

    # Read first 50 lines to check for YAML front matter markers
    with md_path.open("r", encoding="utf-8") as f:
        lines = [f.readline().strip() for _ in range(50)]

    # Front matter must start with "---" on first line
    if not lines or lines[0] != "---":
        raise ValueError(f"Markdown file missing YAML front matter: {md_path}")

    # Find closing "---" marker
    if "---" not in lines[1:]:
        raise ValueError(f"Markdown file has incomplete YAML front matter: {md_path}")

    return True


def validate_profile(profile: Dict[str, Any]) -> bool:
    """
    Validate layout profile schema.

    Args:
        profile: Parsed layout profile dictionary (inner dict, not wrapper)

    Returns:
        True if valid

    Raises:
        ValueError: If profile is missing required fields or invalid
    """
    # Check required keys (rendering_engine is optional, defaults to weasyprint)
    required_keys = ["resources", "styles_map"]
    missing = [k for k in required_keys if k not in profile]
    if missing:
        raise ValueError(f"Profile missing required fields: {missing}")

    # Validate rendering engine value if present
    if "rendering_engine" in profile:
        valid_engines = ["weasyprint", "scribus"]
        engine = profile["rendering_engine"]
        if engine not in valid_engines:
            raise ValueError(
                f"Invalid rendering_engine: {engine}. Must be one of {valid_engines}"
            )

    return True


def validate_metadata(metadata: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate metadata has required fields.

    Args:
        metadata: Parsed metadata dictionary
        required_fields: List of required field names

    Returns:
        True if all required fields present

    Raises:
        ValueError: If required fields are missing
    """
    missing_fields = []

    for field in required_fields:
        if field not in metadata:
            missing_fields.append(field)
        elif metadata[field] in (None, "", []):
            # Field present but empty
            missing_fields.append(f"{field} (empty)")

    if missing_fields:
        raise ValueError(f"Metadata missing required fields: {', '.join(missing_fields)}")

    return True


def validate_css_path(css_path: Path) -> bool:
    """
    Validate CSS file exists and is readable.

    Args:
        css_path: Path to CSS file

    Returns:
        True if valid

    Raises:
        FileNotFoundError: If CSS file does not exist
        OSError: If CSS file is not readable
    """
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file not found: {css_path}")

    if not css_path.is_file():
        raise ValueError(f"CSS path is not a file: {css_path}")

    # Check file is readable
    try:
        with css_path.open("r", encoding="utf-8") as f:
            f.read(1)  # Read single character to verify readability
    except OSError as e:
        raise OSError(f"CSS file not readable: {css_path}") from e

    return True
