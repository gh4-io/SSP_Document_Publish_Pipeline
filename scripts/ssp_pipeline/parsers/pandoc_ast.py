"""Pandoc JSON AST parser.

Parses Pandoc JSON AST into structured block model for rendering.
Supports headings, paragraphs, lists, tables, code, callouts, wikilinks, images.
Part of SSP Document Publishing Pipeline v4.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class Block:
    """Base class for AST block elements."""
    block_type: str = field(init=False, default="")


@dataclass
class Heading(Block):
    """Heading block (H1-H6)."""
    level: int  # 1-6
    text: str
    id: Optional[str] = None

    def __post_init__(self):
        self.block_type = "heading"


@dataclass
class Paragraph(Block):
    """Paragraph block with inline content."""
    content: str

    def __post_init__(self):
        self.block_type = "paragraph"


@dataclass
class ListBlock(Block):
    """Ordered or unordered list."""
    list_type: str  # "ordered" or "unordered"
    items: List[str]
    start_number: Optional[int] = None

    def __post_init__(self):
        self.block_type = "list"


@dataclass
class Table(Block):
    """Table block with headers and rows."""
    headers: List[str]
    rows: List[List[str]]
    caption: Optional[str] = None

    def __post_init__(self):
        self.block_type = "table"


@dataclass
class CodeBlock(Block):
    """Code block with optional language."""
    code: str
    language: Optional[str] = None
    line_numbers: bool = False

    def __post_init__(self):
        self.block_type = "code"


@dataclass
class Callout(Block):
    """Obsidian-style callout block."""
    callout_type: str  # WARNING, DANGER, NOTE, TIP
    title: Optional[str] = None
    content: str = ""

    def __post_init__(self):
        self.block_type = "callout"


@dataclass
class Wikilink(Block):
    """Wikilink internal reference."""
    target: str  # Document ID or file path
    display_text: Optional[str] = None

    def __post_init__(self):
        self.block_type = "wikilink"


@dataclass
class Image(Block):
    """Image reference."""
    path: str  # Relative or absolute path
    alt_text: Optional[str] = None
    caption: Optional[str] = None

    def __post_init__(self):
        self.block_type = "image"


def parse_pandoc_json(json_path: Path) -> List[Block]:
    """
    Parse Pandoc JSON AST file into block list.

    Args:
        json_path: Path to Pandoc JSON AST file

    Returns:
        List of Block objects representing document structure

    Raises:
        FileNotFoundError: If JSON file does not exist
        json.JSONDecodeError: If JSON is malformed
        ValueError: If AST structure is invalid
    """
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Pandoc JSON file not found: {json_path}")
    
    # Load JSON file
    try:
        with json_path.open("r", encoding="utf-8") as f:
            ast_data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Malformed JSON in {json_path}: {e.msg}", e.doc, e.pos)
    
    # Validate AST structure
    if not isinstance(ast_data, dict):
        raise ValueError(f"Invalid Pandoc AST: root must be dict, got {type(ast_data)}")
    
    if "blocks" not in ast_data:
        raise ValueError("Invalid Pandoc AST: missing 'blocks' key")
    
    # Parse each block
    blocks = []
    for block_data in ast_data["blocks"]:
        parsed_block = parse_block(block_data)
        if parsed_block is not None:
            blocks.append(parsed_block)
        else:
            # Log unsupported blocks but continue parsing
            block_type = block_data.get("t", "unknown")
            logger.warning(f"Unsupported block type: {block_type}")
    
    return blocks


def parse_block(block_data: Dict[str, Any]) -> Optional[Block]:
    """
    Parse single Pandoc block into Block object.

    Args:
        block_data: Pandoc block dictionary from JSON

    Returns:
        Corresponding Block subclass instance or None if unsupported

    Raises:
        ValueError: If block data is invalid
    """
    block_type = block_data.get("t", "")
    block_content = block_data.get("c", [])
    
    if block_type == "Header":
        # Structure: [level, [id, classes, kvpairs], [inline_elements]]
        level = block_content[0]
        attrs = block_content[1]
        inline_elements = block_content[2]
        header_id = attrs[0] if attrs[0] else None
        text = extract_inline_text(inline_elements)
        return Heading(level=level, text=text, id=header_id)
    
    elif block_type == "Para":
        # Structure: [inline_elements]
        text = extract_inline_text(block_content)
        return Paragraph(content=text)
    
    elif block_type == "BulletList":
        # Structure: [[[blocks]], [[blocks]], ...]
        # Note: Each item is wrapped in an extra list
        items = []
        for item_wrapper in block_content:
            # item_wrapper is a list containing blocks
            item_text_parts = []
            # Flatten the wrapper if it exists
            item_blocks = item_wrapper[0] if item_wrapper and isinstance(item_wrapper[0], list) else item_wrapper
            for item_block in item_blocks:
                if isinstance(item_block, dict) and item_block.get("t") == "Para":
                    item_text_parts.append(extract_inline_text(item_block["c"]))
            items.append(" ".join(item_text_parts))
        return ListBlock(list_type="unordered", items=items)
    
    elif block_type == "OrderedList":
        # Structure: [[start_num, style, delim], [[[blocks]], [[blocks]], ...]]
        # Note: Each item is wrapped in an extra list
        list_attrs = block_content[0]
        start_number = list_attrs[0]
        item_wrappers_list = block_content[1]
        items = []
        for item_wrapper in item_wrappers_list:
            item_text_parts = []
            # Flatten the wrapper if it exists
            item_blocks = item_wrapper[0] if item_wrapper and isinstance(item_wrapper[0], list) else item_wrapper
            for item_block in item_blocks:
                if isinstance(item_block, dict) and item_block.get("t") == "Para":
                    item_text_parts.append(extract_inline_text(item_block["c"]))
            items.append(" ".join(item_text_parts))
        return ListBlock(list_type="ordered", items=items, start_number=start_number)
    
    elif block_type == "CodeBlock":
        # Structure: [[id, classes, kvpairs], code_string]
        attrs = block_content[0]
        code_string = block_content[1]
        language = attrs[1][0] if attrs[1] else None  # First class is language
        return CodeBlock(code=code_string, language=language)
    
    elif block_type == "BlockQuote":
        # Check if this is an Obsidian callout
        callout = detect_callout(block_data)
        if callout:
            return callout
        # Not a callout, skip blockquote for now
        return None
    
    elif block_type == "Table":
        # Delegate to table parser
        from .tables import parse_table_element
        return parse_table_element(block_data)
    
    # Unsupported types: RawBlock, Div, etc.
    # Return None - caller will log warning
    return None


def extract_inline_text(inline_elements: List[Dict[str, Any]]) -> str:
    """
    Extract plain text from Pandoc inline elements.

    Args:
        inline_elements: List of Pandoc inline element dictionaries

    Returns:
        Concatenated plain text string
    """
    text_parts = []
    
    for elem in inline_elements:
        elem_type = elem.get("t", "")
        
        if elem_type == "Str":
            # Plain text string
            text_parts.append(elem["c"])
        
        elif elem_type == "Space":
            # Space between words
            text_parts.append(" ")
        
        elif elem_type == "LineBreak" or elem_type == "SoftBreak":
            # Hard or soft line break
            text_parts.append("\n")
        
        elif elem_type in ("Emph", "Strong", "Strikeout", "Superscript", "Subscript"):
            # Formatted text - recurse to extract inner text
            inner_inlines = elem["c"]
            text_parts.append(extract_inline_text(inner_inlines))
        
        elif elem_type == "Code":
            # Inline code - extract text only (ignore attributes)
            code_text = elem["c"][1] if isinstance(elem["c"], list) else elem["c"]
            text_parts.append(code_text)
        
        elif elem_type == "Link":
            # Link - extract link text (first element after attributes)
            link_text_inlines = elem["c"][1]
            text_parts.append(extract_inline_text(link_text_inlines))
        
        elif elem_type == "Image":
            # Image - extract alt text
            alt_text_inlines = elem["c"][1]
            text_parts.append(extract_inline_text(alt_text_inlines))
        
        # Ignore other types (Quoted, Cite, Math, RawInline, etc.)
    
    return "".join(text_parts)


def detect_callout(paragraph_data: Dict[str, Any]) -> Optional[Callout]:
    """
    Detect if paragraph is Obsidian callout (> [!TYPE]).

    Args:
        paragraph_data: Pandoc paragraph dictionary

    Returns:
        Callout object if detected, None otherwise
    """
    import re
    
    # BlockQuote structure: {"t": "BlockQuote", "c": [blocks]}
    if paragraph_data.get("t") != "BlockQuote":
        return None
    
    blocks = paragraph_data.get("c", [])
    if not blocks:
        return None
    
    # Get first block (should be Para with callout marker)
    first_block = blocks[0]
    if first_block.get("t") != "Para":
        return None
    
    # Extract text from first paragraph
    inline_elements = first_block.get("c", [])
    text = extract_inline_text(inline_elements)
    
    # Check for callout pattern: [!TYPE] or [!TYPE] Title
    callout_pattern = r'^\[!(WARNING|DANGER|NOTE|TIP|INFO|CAUTION)\]\s*(.*)'
    match = re.match(callout_pattern, text, re.IGNORECASE)
    
    if not match:
        return None
    
    callout_type = match.group(1).upper()
    remaining_text = match.group(2).strip()
    
    # Rest of blockquote is callout content
    content_parts = [remaining_text] if remaining_text else []
    for block in blocks[1:]:
        if block.get("t") == "Para":
            content_parts.append(extract_inline_text(block["c"]))
    
    content = "\n".join(content_parts)
    
    return Callout(callout_type=callout_type, content=content)


def parse_wikilink(link_text: str) -> Wikilink:
    """
    Parse wikilink syntax [[target | display]].

    Args:
        link_text: Raw wikilink text

    Returns:
        Wikilink object with target and display text

    Raises:
        ValueError: If wikilink syntax is invalid
    """
    # Strip outer brackets
    if not (link_text.startswith("[[") and link_text.endswith("]]")):
        raise ValueError(f"Invalid wikilink syntax: {link_text}")
    
    inner_text = link_text[2:-2].strip()
    
    if not inner_text:
        raise ValueError("Empty wikilink")
    
    # Split on pipe if present
    if "|" in inner_text:
        parts = inner_text.split("|", 1)
        target = parts[0].strip()
        display_text = parts[1].strip()
    else:
        target = inner_text
        display_text = None
    
    if not target:
        raise ValueError("Wikilink missing target")
    
    return Wikilink(target=target, display_text=display_text)
