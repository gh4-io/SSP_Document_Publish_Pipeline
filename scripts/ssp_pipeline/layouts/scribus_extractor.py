"""Scribus layout extractor.

Extracts frame geometry and styles from Scribus .sla files for CSS generation.
Part of SSP Document Publishing Pipeline v4.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def extract_frames(sla_path: Path) -> Dict[str, Any]:
    """
    Extract frame definitions from Scribus .sla file.

    Args:
        sla_path: Path to Scribus .sla XML file

    Returns:
        Dictionary mapping frame names to geometry and style properties
        Format: {frame_name: {x, y, width, height, type, ...}}

    Raises:
        FileNotFoundError: If .sla file does not exist
        xml.etree.ElementTree.ParseError: If .sla XML is malformed
        ValueError: If required frame data missing
    """
    if not sla_path.exists():
        raise FileNotFoundError(f"Scribus file not found: {sla_path}")

    logger.info(f"Extracting frames from {sla_path}")

    try:
        tree = ET.parse(sla_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ET.ParseError(f"Malformed XML in {sla_path}: {e}")

    frames = {}

    # Find all PAGEOBJECT elements (Scribus frames)
    for page_obj in root.iter('PAGEOBJECT'):
        frame_data = parse_frame_geometry(page_obj)

        if frame_data and 'name' in frame_data:
            frame_name = frame_data.pop('name')
            frames[frame_name] = frame_data
            logger.debug(f"Extracted frame: {frame_name}")

    if not frames:
        raise ValueError(f"No frames found in {sla_path}")

    logger.info(f"Extracted {len(frames)} frames")
    return frames


def parse_frame_geometry(frame_element: ET.Element) -> Dict[str, Any]:
    """
    Parse frame geometry attributes from XML element.

    Args:
        frame_element: Scribus PAGEOBJECT XML element

    Returns:
        Dictionary with name, x, y, width, height (in points), type, etc.

    Raises:
        ValueError: If geometry attributes missing or invalid
    """
    # Extract required attributes
    required_attrs = ['XPOS', 'YPOS', 'WIDTH', 'HEIGHT', 'ANNAME']

    for attr in required_attrs:
        if attr not in frame_element.attrib:
            logger.warning(f"Frame missing required attribute: {attr}")
            return {}

    try:
        # Convert Scribus points to inches (1 inch = 72 points)
        x_points = float(frame_element.get('XPOS'))
        y_points = float(frame_element.get('YPOS'))
        width_points = float(frame_element.get('WIDTH'))
        height_points = float(frame_element.get('HEIGHT'))

        frame_data = {
            'name': frame_element.get('ANNAME'),
            'x': x_points / 72.0,  # Convert to inches
            'y': y_points / 72.0,
            'width': width_points / 72.0,
            'height': height_points / 72.0,
            'type': frame_element.get('PTYPE', ''),
            'x_points': x_points,  # Keep original for reference
            'y_points': y_points,
            'width_points': width_points,
            'height_points': height_points
        }

        # Add optional font information if present
        story_text = frame_element.find('.//StoryText/DefaultStyle')
        if story_text is not None:
            if 'FONT' in story_text.attrib:
                frame_data['font'] = story_text.get('FONT')
            if 'FONTSIZE' in story_text.attrib:
                frame_data['fontsize'] = float(story_text.get('FONTSIZE'))

        return frame_data

    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid geometry values: {e}")


def extract_master_pages(sla_path: Path) -> List[Dict[str, Any]]:
    """
    Extract master page definitions from Scribus file.

    Args:
        sla_path: Path to Scribus .sla file

    Returns:
        List of master page dictionaries with frames and properties

    Raises:
        FileNotFoundError: If .sla file does not exist
        ValueError: If master pages not found
    """
    if not sla_path.exists():
        raise FileNotFoundError(f"Scribus file not found: {sla_path}")

    logger.info(f"Extracting master pages from {sla_path}")

    try:
        tree = ET.parse(sla_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ET.ParseError(f"Malformed XML in {sla_path}: {e}")

    master_pages = []

    # Find all MASTERPAGE elements
    for master_page in root.iter('MASTERPAGE'):
        page_data = {
            'name': master_page.get('NAM', 'Unnamed'),
            'width': float(master_page.get('PageWidth', 0)) / 72.0,
            'height': float(master_page.get('PageHeight', 0)) / 72.0,
            'frames': []
        }

        # Extract frames on this master page
        page_number = master_page.get('NUM', '0')
        for page_obj in root.iter('PAGEOBJECT'):
            if page_obj.get('OwnPage') == page_number:
                frame_data = parse_frame_geometry(page_obj)
                if frame_data:
                    page_data['frames'].append(frame_data)

        master_pages.append(page_data)
        logger.debug(f"Extracted master page: {page_data['name']}")

    if not master_pages:
        logger.warning(f"No master pages found in {sla_path}")

    return master_pages


def get_frame_by_name(sla_path: Path, frame_name: str) -> Optional[Dict[str, Any]]:
    """
    Get specific frame data by name.

    Args:
        sla_path: Path to Scribus .sla file
        frame_name: Name of frame to extract (ANNAME attribute)

    Returns:
        Frame dictionary or None if not found

    Raises:
        FileNotFoundError: If .sla file does not exist
    """
    frames = extract_frames(sla_path)
    return frames.get(frame_name)


def extract_text_styles(sla_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Extract text style definitions from Scribus file.

    Args:
        sla_path: Path to Scribus .sla file

    Returns:
        Dictionary mapping style names to properties (font, size, color, etc.)

    Raises:
        FileNotFoundError: If .sla file does not exist
    """
    if not sla_path.exists():
        raise FileNotFoundError(f"Scribus file not found: {sla_path}")

    logger.info(f"Extracting text styles from {sla_path}")

    try:
        tree = ET.parse(sla_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ET.ParseError(f"Malformed XML in {sla_path}: {e}")

    text_styles = {}

    # Find all STYLE elements
    for style in root.iter('STYLE'):
        style_name = style.get('NAME', 'Unnamed')
        style_data = {
            'font': style.get('FONT', ''),
            'size': float(style.get('FONTSIZE', 12)),
        }

        # Add optional properties
        if 'FCOLOR' in style.attrib:
            style_data['color'] = style.get('FCOLOR')
        if 'FONTFEATURES' in style.attrib:
            style_data['weight'] = style.get('FONTFEATURES')

        text_styles[style_name] = style_data
        logger.debug(f"Extracted style: {style_name}")

    logger.info(f"Extracted {len(text_styles)} text styles")
    return text_styles


def validate_sla_file(sla_path: Path) -> bool:
    """
    Validate Scribus .sla file structure.

    Args:
        sla_path: Path to .sla file

    Returns:
        True if valid

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file structure invalid
    """
    if not sla_path.exists():
        raise FileNotFoundError(f"File not found: {sla_path}")

    # Check file extension
    if sla_path.suffix.lower() != '.sla':
        raise ValueError(f"Not a .sla file: {sla_path}")

    try:
        tree = ET.parse(sla_path)
        root = tree.getroot()

        # Check for DOCUMENT root element
        if root.tag != 'SCRIBUSUTF8NEW' and root.tag != 'SCRIBUSUTF8':
            raise ValueError(f"Invalid Scribus file: root element is '{root.tag}'")

        # Check for at least one DOCUMENT element
        doc = root.find('.//DOCUMENT')
        if doc is None:
            raise ValueError("No DOCUMENT element found in Scribus file")

        logger.info(f"Validated {sla_path}")
        return True

    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {e}")
