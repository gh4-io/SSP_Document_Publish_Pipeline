"""Table parsing from Pandoc AST.

Extracts table structure (headers, rows, captions) from Pandoc table elements.
Part of SSP Document Publishing Pipeline v4.

Handles Pandoc's table representation including:
- Column headers
- Row data (cell alignment, multi-column spans)
- Optional table captions
- Table alignment (left, center, right, default)
"""

from typing import Dict, Any, List, Optional
import logging

# Import from parent package
from .pandoc_ast import Table, extract_inline_text


logger = logging.getLogger(__name__)


def parse_table_element(table_data: Dict[str, Any]) -> Optional[Table]:
    """
    Parse Pandoc Table element into simplified table structure.

    Pandoc Table structure (complex):
    {"t": "Table", "c": [
        [id, classes, kvpairs],  # attrs
        caption,                  # Caption object
        colspecs,                 # Column specs (alignment)
        table_head,               # TableHead with header rows
        table_bodies,             # List of TableBody objects
        table_foot                # TableFoot
    ]}

    Args:
        table_data: Pandoc Table element dictionary

    Returns:
        Table block with headers and rows, or None if parsing fails
    """
    if table_data.get("t") != "Table":
        return None

    content = table_data.get("c", [])
    if len(content) < 6:
        logger.warning("Invalid Table element structure")
        return None

    content[0]
    caption_obj = content[1]
    content[2]
    table_head = content[3]
    table_bodies = content[4]
    content[5]

    # Extract caption (if present)
    caption = extract_caption(caption_obj)

    # Extract headers from table_head
    headers = extract_table_headers(table_head)

    # Extract rows from table_bodies
    rows = extract_table_rows(table_bodies)

    return Table(headers=headers, rows=rows, caption=caption)


def extract_caption(caption_obj: Dict[str, Any]) -> Optional[str]:
    """
    Extract caption from Pandoc caption object.

    Caption structure:
    {"t": "Caption", "c": [short_caption, [blocks]]}

    Args:
        caption_obj: Pandoc Caption object

    Returns:
        Caption text or None
    """
    if not isinstance(caption_obj, dict):
        return None

    if caption_obj.get("t") != "Caption":
        return None

    content = caption_obj.get("c", [])
    if len(content) < 2:
        return None

    # Extract text from caption blocks
    caption_blocks = content[1]
    caption_parts = []
    for block in caption_blocks:
        if block.get("t") == "Para":
            caption_parts.append(extract_inline_text(block["c"]))

    return " ".join(caption_parts) if caption_parts else None


def extract_table_headers(table_head: Dict[str, Any]) -> List[str]:
    """
    Extract headers from Pandoc TableHead.

    TableHead structure:
    {"t": "TableHead", "c": [attrs, [rows]]}

    Args:
        table_head: Pandoc TableHead object

    Returns:
        List of header cell texts
    """
    if not isinstance(table_head, dict) or table_head.get("t") != "TableHead":
        return []

    content = table_head.get("c", [])
    if len(content) < 2:
        return []

    rows = content[1]
    if not rows:
        return []

    # Get first row (header row)
    first_row = rows[0]
    if first_row.get("t") != "Row":
        return []

    row_content = first_row.get("c", [])
    if len(row_content) < 2:
        return []

    cells = row_content[1]  # [attrs, [cells]]

    headers = []
    for cell in cells:
        cell_text = extract_cell_text(cell)
        headers.append(cell_text)

    return headers


def extract_table_rows(table_bodies: List[Dict[str, Any]]) -> List[List[str]]:
    """
    Extract rows from Pandoc TableBody list.

    TableBody structure:
    {"t": "TableBody", "c": [attrs, row_head_columns, head_rows, body_rows]}

    Args:
        table_bodies: List of Pandoc TableBody objects

    Returns:
        List of rows, where each row is a list of cell texts
    """
    rows = []

    for tbody in table_bodies:
        if not isinstance(tbody, dict) or tbody.get("t") != "TableBody":
            continue

        content = tbody.get("c", [])
        if len(content) < 4:
            continue

        body_rows = content[3]  # The actual data rows

        for row in body_rows:
            if row.get("t") != "Row":
                continue

            row_content = row.get("c", [])
            if len(row_content) < 2:
                continue

            cells = row_content[1]

            row_cells = []
            for cell in cells:
                cell_text = extract_cell_text(cell)
                row_cells.append(cell_text)

            rows.append(row_cells)

    return rows


def extract_cell_text(cell: Dict[str, Any]) -> str:
    """
    Extract text from a table cell.

    Cell structure:
    {"t": "Cell", "c": [attrs, alignment, rowspan, colspan, [blocks]]}

    Args:
        cell: Pandoc Cell object

    Returns:
        Cell text content
    """
    if not isinstance(cell, dict) or cell.get("t") != "Cell":
        return ""

    content = cell.get("c", [])
    if len(content) < 5:
        return ""

    blocks = content[4]  # Cell content blocks

    cell_parts = []
    for block in blocks:
        if block.get("t") == "Para":
            cell_parts.append(extract_inline_text(block["c"]))
        elif block.get("t") == "Plain":
            cell_parts.append(extract_inline_text(block["c"]))

    return " ".join(cell_parts)
