"""Scribus layout extraction and CSS generation.

Extract frame geometry from Scribus and build CSS for WeasyPrint.
"""

from .scribus_extractor import (
    extract_frames,
    parse_frame_geometry,
    extract_master_pages,
    get_frame_by_name,
    extract_text_styles,
    validate_sla_file,
)
from .css_builder import (
    build_layout_css,
    generate_page_rules,
    generate_frame_css,
    convert_points_to_units,
    generate_text_styles_css,
    merge_css_files,
    validate_css_syntax,
)

__all__ = [
    # Scribus extraction
    "extract_frames",
    "parse_frame_geometry",
    "extract_master_pages",
    "get_frame_by_name",
    "extract_text_styles",
    "validate_sla_file",
    # CSS building
    "build_layout_css",
    "generate_page_rules",
    "generate_frame_css",
    "convert_points_to_units",
    "generate_text_styles_css",
    "merge_css_files",
    "validate_css_syntax",
]
