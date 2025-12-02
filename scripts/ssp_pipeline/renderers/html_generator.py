"""HTML generation from block model.

Generates HTML body and metadata frames with CSS classes from parsed blocks.
Part of SSP Document Publishing Pipeline v4.
"""

from pathlib import Path
from typing import List, Dict, Any
import html as html_lib
from ..parsers.pandoc_ast import Block, Heading, Paragraph, Table, CodeBlock, Callout, Image, ListBlock, Wikilink


def generate_html(blocks: List[Block], metadata: Dict[str, Any], styles_map: Dict[str, Any]) -> str:
    """
    Generate complete HTML document from block list and metadata.

    Args:
        blocks: List of Block objects from AST parser
        metadata: Document metadata dictionary
        styles_map: CSS class mapping from layout profile

    Returns:
        Complete HTML string with CSS classes applied

    Raises:
        ValueError: If blocks or metadata invalid
    """
    if not isinstance(blocks, list):
        raise ValueError("blocks must be a list")

    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")

    # Generate HTML body from blocks
    body_parts = []
    for block in blocks:
        try:
            block_html = render_block(block, styles_map)
            body_parts.append(block_html)
        except Exception as e:
            # Log error but continue rendering
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to render block {block.block_type}: {e}")

    body_content = "\n".join(body_parts)

    # Generate metadata frame
    metadata_html = generate_metadata_frame(metadata)

    # Construct complete HTML document
    doc_title = metadata.get("title", "Untitled Document")

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_lib.escape(doc_title)}</title>
</head>
<body>
    <div class="metadata-frame">
        {metadata_html}
    </div>
    <div class="document-body">
        {body_content}
    </div>
</body>
</html>"""

    return html_doc


def render_block(block: Block, styles_map: Dict[str, Any]) -> str:
    """
    Render single block to HTML with CSS classes.

    Args:
        block: Block object to render
        styles_map: CSS class mapping

    Returns:
        HTML string for the block

    Raises:
        ValueError: If block type unsupported
    """
    # Dispatch to appropriate renderer based on block type
    if isinstance(block, Heading):
        return render_heading(block, styles_map)
    elif isinstance(block, Paragraph):
        return render_paragraph(block, styles_map)
    elif isinstance(block, ListBlock):
        return render_list(block, styles_map)
    elif isinstance(block, Table):
        return render_table(block, styles_map)
    elif isinstance(block, CodeBlock):
        return render_code_block(block, styles_map)
    elif isinstance(block, Callout):
        return render_callout(block, styles_map)
    elif isinstance(block, Image):
        return render_image(block, Path.cwd())
    elif isinstance(block, Wikilink):
        return render_wikilink(block, styles_map)
    else:
        raise ValueError(f"Unsupported block type: {type(block).__name__}")


def render_heading(heading: Heading, styles_map: Dict[str, Any]) -> str:
    """
    Render heading block to HTML.

    Args:
        heading: Heading block object
        styles_map: CSS class mapping

    Returns:
        HTML heading tag with appropriate class
    """
    # Get CSS class from styles_map (support both pandoc and docbook)
    heading_key = f"heading{heading.level}"
    css_class = styles_map.get(heading_key, f"Heading{heading.level}")

    # Escape text content
    text = html_lib.escape(heading.text)

    # Generate heading tag with optional id
    id_attr = f' id="{heading.id}"' if heading.id else ''
    return f'<h{heading.level} class="{css_class}"{id_attr}>{text}</h{heading.level}>'


def render_paragraph(para: Paragraph, styles_map: Dict[str, Any]) -> str:
    """
    Render paragraph block to HTML.

    Args:
        para: Paragraph block object
        styles_map: CSS class mapping

    Returns:
        HTML paragraph tag with class
    """
    # Get CSS class from styles_map
    para_class = styles_map.get("paragraph", "BodyText")

    # Escape content
    content = html_lib.escape(para.content)

    return f'<p class="{para_class}">{content}</p>'


def render_list(list_block: ListBlock, styles_map: Dict[str, Any]) -> str:
    """
    Render list block to HTML (ordered or unordered).

    Args:
        list_block: ListBlock object
        styles_map: CSS class mapping

    Returns:
        HTML ul or ol tag with list items
    """
    # Determine list tag type
    tag = "ol" if list_block.list_type == "ordered" else "ul"

    # Generate list items
    items_html = []
    for item in list_block.items:
        escaped_item = html_lib.escape(item)
        items_html.append(f"  <li>{escaped_item}</li>")

    items_content = "\n".join(items_html)

    # Add start attribute for ordered lists
    start_attr = f' start="{list_block.start_number}"' if list_block.list_type == "ordered" and list_block.start_number else ''

    return f'<{tag}{start_attr}>\n{items_content}\n</{tag}>'


def render_table(table: Table, styles_map: Dict[str, Any]) -> str:
    """
    Render table block to HTML.

    Args:
        table: Table block object
        styles_map: CSS class mapping

    Returns:
        HTML table with headers and rows
    """
    # Get CSS class from styles_map
    table_class = styles_map.get("pandoc", {}).get("table", "table-standard")

    # Generate table headers
    header_cells = []
    for header in table.headers:
        escaped_header = html_lib.escape(header)
        header_cells.append(f"    <th>{escaped_header}</th>")

    headers_html = "\n".join(header_cells)

    # Generate table rows
    rows_html = []
    for row in table.rows:
        row_cells = []
        for cell in row:
            escaped_cell = html_lib.escape(cell)
            row_cells.append(f"      <td>{escaped_cell}</td>")
        row_html = "\n".join(row_cells)
        rows_html.append(f"  <tr>\n{row_html}\n  </tr>")

    rows_content = "\n".join(rows_html)

    # Add caption if present
    caption_html = f"  <caption>{html_lib.escape(table.caption)}</caption>\n" if table.caption else ""

    return f'''<table class="{table_class}">
{caption_html}  <thead>
  <tr>
{headers_html}
  </tr>
  </thead>
  <tbody>
{rows_content}
  </tbody>
</table>'''


def render_code_block(code: CodeBlock, styles_map: Dict[str, Any]) -> str:
    """
    Render code block to HTML with syntax highlighting classes.

    Args:
        code: CodeBlock object
        styles_map: CSS class mapping

    Returns:
        HTML pre/code tags with language class
    """
    # Get CSS class from styles_map
    code_class = styles_map.get("pandoc", {}).get("code", "CodeBlock")

    # Escape code content
    escaped_code = html_lib.escape(code.code)

    # Add language class if specified
    lang_class = f' language-{code.language}' if code.language else ''

    return f'<pre class="{code_class}"><code class="{code_class}{lang_class}">{escaped_code}</code></pre>'


def render_callout(callout: Callout, styles_map: Dict[str, Any]) -> str:
    """
    Render Obsidian callout to styled HTML div.

    Args:
        callout: Callout block object
        styles_map: CSS class mapping

    Returns:
        HTML div with callout type class
    """
    # Get CSS class from styles_map
    callout_styles = styles_map.get("pandoc", {}).get("callout", {})
    css_class = callout_styles.get(callout.callout_type, f"callout-{callout.callout_type.lower()}")

    # Escape content
    escaped_content = html_lib.escape(callout.content)

    # Add title if present
    title_html = f'<div class="callout-title">{html_lib.escape(callout.title)}</div>\n  ' if callout.title else ''

    return f'''<div class="callout {css_class}">
  {title_html}<div class="callout-content">{escaped_content}</div>
</div>'''


def render_image(image: Image, base_dir: Path) -> str:
    """
    Render image block to HTML img tag.

    Args:
        image: Image block object
        base_dir: Base directory for resolving relative paths

    Returns:
        HTML img tag with src and alt
    """
    # Use image path as-is (resolution handled during parsing)
    src = html_lib.escape(image.path)

    # Add alt text if present
    alt_attr = f' alt="{html_lib.escape(image.alt_text)}"' if image.alt_text else ' alt=""'

    # Build img tag
    img_tag = f'<img src="{src}"{alt_attr} class="document-image">'

    # Wrap with figure if caption present
    if image.caption:
        caption = html_lib.escape(image.caption)
        return f'<figure>\n  {img_tag}\n  <figcaption>{caption}</figcaption>\n</figure>'

    return img_tag


def render_wikilink(wikilink: Wikilink, styles_map: Dict[str, Any]) -> str:
    """
    Render wikilink to HTML anchor tag.

    Args:
        wikilink: Wikilink block object
        styles_map: CSS class mapping

    Returns:
        HTML anchor tag with internal link
    """
    # Use target as href (resolution handled during parsing)
    href = html_lib.escape(wikilink.target)

    # Use display text if present, otherwise use target
    link_text = html_lib.escape(wikilink.display_text if wikilink.display_text else wikilink.target)

    return f'<a href="{href}" class="wikilink">{link_text}</a>'


def generate_metadata_frame(metadata: Dict[str, Any]) -> str:
    """
    Generate HTML metadata frame (header/footer content).

    Args:
        metadata: Document metadata dictionary

    Returns:
        HTML div with metadata fields
    """
    # Extract common metadata fields
    doc_id = metadata.get("document_id", "")
    title = metadata.get("title", "")
    revision = metadata.get("revision", "")
    author = metadata.get("author", "")
    date = metadata.get("date", "")

    # Build metadata HTML
    parts = []

    if doc_id:
        parts.append(f'<div class="meta-field meta-id"><strong>Document ID:</strong> {html_lib.escape(doc_id)}</div>')

    if title:
        parts.append(f'<div class="meta-field meta-title"><strong>Title:</strong> {html_lib.escape(title)}</div>')

    if revision:
        parts.append(f'<div class="meta-field meta-revision"><strong>Revision:</strong> {html_lib.escape(revision)}</div>')

    if author:
        parts.append(f'<div class="meta-field meta-author"><strong>Author:</strong> {html_lib.escape(author)}</div>')

    if date:
        parts.append(f'<div class="meta-field meta-date"><strong>Date:</strong> {html_lib.escape(date)}</div>')

    return "\n".join(parts) if parts else '<div class="meta-field">No metadata available</div>'
