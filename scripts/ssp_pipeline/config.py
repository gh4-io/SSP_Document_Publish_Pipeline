"""Configuration loading and rendering engine selection.

Loads layout profile JSON and determines rendering engine (WeasyPrint or Scribus).
Part of SSP Document Publishing Pipeline v4.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_layout_profile(profile_path: Path) -> Dict[str, Any]:
    """
    Load and parse layout profile JSON.

    Args:
        profile_path: Path to layout profile JSON file

    Returns:
        Parsed profile dictionary containing rendering_engine, resources, styles_map

    Raises:
        FileNotFoundError: If profile file does not exist
        json.JSONDecodeError: If profile JSON is malformed
        ValueError: If profile schema is invalid
    """
    if not profile_path.exists():
        raise FileNotFoundError(f"Layout profile not found: {profile_path}")

    logger.info(f"Loading layout profile from {profile_path}")

    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Malformed JSON in layout profile: {e.msg}",
            e.doc,
            e.pos
        )

    # Validate basic structure - expect "layout_profile" root key
    if "layout_profile" not in data:
        raise ValueError("Invalid profile schema: missing 'layout_profile' root key")

    profile = data["layout_profile"]

    # Validate required top-level keys
    required_keys = ["resources", "styles_map"]
    missing = [k for k in required_keys if k not in profile]
    if missing:
        raise ValueError(f"Invalid profile schema: missing required keys {missing}")

    logger.debug(f"Profile loaded successfully: {profile.get('id', 'unknown')}")
    return profile


def get_rendering_engine(profile: Dict[str, Any]) -> str:
    """
    Extract rendering engine from profile.

    Args:
        profile: Parsed layout profile dictionary

    Returns:
        Rendering engine name ("weasyprint" or "scribus")

    Raises:
        KeyError: If rendering_engine not in profile
        ValueError: If rendering_engine value is invalid
    """
    # Default to weasyprint if not specified (new profiles)
    engine = profile.get("rendering_engine", "weasyprint")

    valid_engines = ["weasyprint", "scribus"]
    if engine not in valid_engines:
        raise ValueError(
            f"Invalid rendering_engine '{engine}'. Must be one of: {valid_engines}"
        )

    logger.debug(f"Rendering engine: {engine}")
    return engine


def get_resource_paths(profile: Dict[str, Any], base_dir: Path) -> Dict[str, Path]:
    """
    Resolve all resource paths from profile to absolute paths.

    Args:
        profile: Parsed layout profile dictionary
        base_dir: Base directory for relative path resolution

    Returns:
        Dictionary mapping resource names to absolute paths

    Raises:
        KeyError: If required resources missing from profile
        FileNotFoundError: If required resource files don't exist
    """
    if "resources" not in profile:
        raise KeyError("Profile missing 'resources' key")

    resources = profile["resources"]
    resolved = {}

    # Resolve each resource path relative to base_dir
    for key, value in resources.items():
        if isinstance(value, str):
            # Simple string path
            path = Path(value)
            if not path.is_absolute():
                path = base_dir / path
            resolved[key] = path
        elif isinstance(value, dict):
            # Nested resource dict (e.g., "docbook" section) - skip for now
            logger.debug(f"Skipping nested resource: {key}")
            continue
        else:
            logger.warning(f"Unexpected resource type for '{key}': {type(value)}")

    logger.debug(f"Resolved {len(resolved)} resource paths")
    return resolved


def get_styles_map(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract Pandoc → CSS styles mapping from profile.

    Args:
        profile: Parsed layout profile dictionary

    Returns:
        Styles mapping dictionary for Pandoc elements

    Raises:
        KeyError: If styles_map missing from profile
    """
    if "styles_map" not in profile:
        raise KeyError("Profile missing 'styles_map' key")

    styles_map = profile["styles_map"]

    # Support both old (docbook) and new (pandoc) style maps
    # Prefer pandoc if both exist
    if "pandoc" in styles_map:
        logger.debug("Using Pandoc styles map")
        return styles_map["pandoc"]
    elif "docbook" in styles_map:
        logger.warning("Using legacy DocBook styles map (consider migrating to Pandoc)")
        return styles_map["docbook"]
    else:
        # Return entire styles_map if no sub-key specified
        logger.debug("Using direct styles map")
        return styles_map
