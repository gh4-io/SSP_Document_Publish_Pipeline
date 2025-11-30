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

# TODO: Implement Scribus Python scripting interface.
# Requires Scribus installed and accessible via subprocess or direct Python bindings.
# Load .sla template, populate frames, apply styles, export PDF.
# Handle Scribus-specific frame naming conventions (TitleMain, BodyMain, etc.).
