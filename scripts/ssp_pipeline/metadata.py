"""Metadata parsing and normalization.

Extracts and validates YAML front matter from Markdown documents.
Part of SSP Document Publishing Pipeline v4.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


def parse_frontmatter(markdown_path: Path) -> Dict[str, Any]:
    """
    Extract YAML front matter from Markdown file.

    Args:
        markdown_path: Path to Markdown file with YAML front matter

    Returns:
        Parsed metadata dictionary from YAML

    Raises:
        FileNotFoundError: If Markdown file does not exist
        ValueError: If front matter is missing or invalid YAML
    """
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    logger.info(f"Parsing frontmatter from {markdown_path}")

    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match YAML frontmatter between --- markers at start of file
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"No YAML frontmatter found in {markdown_path}")

    yaml_text = match.group(1)

    # Simple YAML parser (key: value pairs + simple arrays)
    # For production, could use PyYAML, but keeping stdlib-only for now
    metadata = {}
    lines = yaml_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line or line.startswith('#'):
            continue

        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Check if value is empty (array follows on next lines)
            if not value:
                # Look ahead for array items (lines starting with -)
                array_items = []
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith('- '):
                        # Extract array item
                        item = next_line[2:].strip()
                        # Remove quotes if present
                        if item.startswith('"') and item.endswith('"'):
                            item = item[1:-1]
                        elif item.startswith("'") and item.endswith("'"):
                            item = item[1:-1]
                        array_items.append(item)
                        i += 1
                    else:
                        break
                metadata[key] = array_items
            else:
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                metadata[key] = value

    logger.debug(f"Extracted {len(metadata)} metadata fields")
    return metadata


def normalize_metadata(raw_meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate metadata fields.

    Converts field names to standard format, applies defaults, validates types.

    Args:
        raw_meta: Raw metadata dictionary from front matter

    Returns:
        Normalized metadata with standard field names and validated values

    Raises:
        ValueError: If required fields missing or invalid types
    """
    logger.debug("Normalizing metadata fields")

    normalized = {}

    # Field name mappings (handle common variations)
    field_map = {
        "doc_id": "document_id",
        "docid": "document_id",
        "id": "document_id",
        "rev": "revision",
        "version": "revision",
        "date": "effective_date",
        "effectivedate": "effective_date",
        "owner": "author",  # DTS profile uses "owner", pipeline expects "author"
    }

    # Normalize field names
    for key, value in raw_meta.items():
        key_lower = key.lower().replace('-', '_').replace(' ', '_')
        normalized_key = field_map.get(key_lower, key_lower)
        normalized[normalized_key] = value

    # Validate required fields
    required = get_required_fields()
    missing = [f for f in required if f not in normalized]
    if missing:
        raise ValueError(f"Missing required metadata fields: {missing}")

    # Add timestamp if not present
    if "generated_at" not in normalized:
        normalized["generated_at"] = datetime.utcnow().isoformat()

    logger.debug(f"Metadata normalized: {len(normalized)} fields")
    return normalized


def extract_document_id(metadata: Dict[str, Any]) -> str:
    """
    Extract standardized document ID from metadata.

    Args:
        metadata: Normalized metadata dictionary

    Returns:
        Document ID string (e.g., "SOP-200", "STD-105")

    Raises:
        KeyError: If document_id field missing
        ValueError: If document_id format invalid
    """
    if "document_id" not in metadata:
        raise KeyError("Metadata missing 'document_id' field")

    doc_id = metadata["document_id"]

    # Validate format: TYPE-NNN (e.g., SOP-200, STD-105, REF-2201, APP-001)
    pattern = r'^[A-Z]{3,4}-\d{2,4}$'
    if not re.match(pattern, doc_id):
        raise ValueError(
            f"Invalid document_id format '{doc_id}'. "
            f"Expected format: TYPE-NNN (e.g., SOP-200, STD-105)"
        )

    logger.debug(f"Extracted document_id: {doc_id}")
    return doc_id


def get_required_fields() -> List[str]:
    """
    Return list of required metadata fields.

    Returns:
        List of required field names for validation
    """
    return [
        "document_id",
        "title",
        "revision",
        "author"
    ]


def merge_with_defaults(metadata: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge metadata with default values.

    Args:
        metadata: User-provided metadata
        defaults: Default values dictionary

    Returns:
        Merged metadata with defaults applied
    """
    # Start with defaults, then override with user values
    merged = defaults.copy()
    merged.update(metadata)

    logger.debug(f"Merged metadata: {len(merged)} fields total")
    return merged


def resolve_profile_path(metadata: Dict[str, Any], fallback_profile: Path) -> Path:
    """
    Resolve layout profile path from metadata or fallback.

    Args:
        metadata: Parsed metadata dictionary
        fallback_profile: Default profile path if not specified in metadata

    Returns:
        Resolved Path to layout profile JSON

    Raises:
        FileNotFoundError: If resolved profile does not exist
    """
    # Check if pipeline_profile specified in frontmatter
    if "pipeline_profile" in metadata:
        profile_name = metadata["pipeline_profile"]
        logger.info(f"Document specifies pipeline_profile: {profile_name}")

        # Profile name mapping (short name → full path)
        profile_map = {
            "dts_master_report": "templates/profiles/layout_profile_dts_master_report.json",
            "default": "templates/profiles/layout_profile_default.json",
        }

        if profile_name in profile_map:
            profile_path = Path(profile_map[profile_name])
            logger.debug(f"Mapped '{profile_name}' → {profile_path}")
        else:
            # Assume it's a direct path
            profile_path = Path(profile_name)
            logger.debug(f"Using direct path: {profile_path}")

        # Validate profile exists
        if not profile_path.exists():
            raise FileNotFoundError(
                f"Layout profile specified in frontmatter not found: {profile_path}"
            )

        return profile_path

    # Use fallback (command-line argument)
    logger.debug(f"No pipeline_profile in frontmatter, using fallback: {fallback_profile}")
    return fallback_profile
