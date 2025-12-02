"""HTML and PDF renderers.

Generate HTML from blocks and render to PDF with WeasyPrint.
"""

from .html_generator import (
    generate_html,
    render_block,
    render_heading,
    render_paragraph,
    render_list,
    render_table,
    render_code_block,
    render_callout,
    render_image,
    render_wikilink,
    generate_metadata_frame,
)
from .weasyprint_renderer import (
    render_pdf,
    load_css_files,
    apply_pdf_metadata,
    validate_weasyprint_available,
    configure_weasyprint,
)

__all__ = [
    # HTML generation
    "generate_html",
    "render_block",
    "render_heading",
    "render_paragraph",
    "render_list",
    "render_table",
    "render_code_block",
    "render_callout",
    "render_image",
    "render_wikilink",
    "generate_metadata_frame",
    # PDF rendering
    "render_pdf",
    "load_css_files",
    "apply_pdf_metadata",
    "validate_weasyprint_available",
    "configure_weasyprint",
]
