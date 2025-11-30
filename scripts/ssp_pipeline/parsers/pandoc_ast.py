"""Pandoc JSON AST parser.

Parses Pandoc JSON AST into structured block model for rendering.
Supports headings, paragraphs, lists, tables, code, callouts, wikilinks, images.
Part of SSP Document Publishing Pipeline v4.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class Block:
    """Base class for AST block elements."""
    block_type: str


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
    # TODO: Implement Pandoc JSON parsing
    raise NotImplementedError


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
    # TODO: Implement block-level parsing with type dispatch
    raise NotImplementedError


def extract_inline_text(inline_elements: List[Dict[str, Any]]) -> str:
    """
    Extract plain text from Pandoc inline elements.

    Args:
        inline_elements: List of Pandoc inline element dictionaries

    Returns:
        Concatenated plain text string
    """
    # TODO: Implement inline text extraction
    raise NotImplementedError


def detect_callout(paragraph_data: Dict[str, Any]) -> Optional[Callout]:
    """
    Detect if paragraph is Obsidian callout (> [!TYPE]).

    Args:
        paragraph_data: Pandoc paragraph dictionary

    Returns:
        Callout object if detected, None otherwise
    """
    # TODO: Implement callout detection from blockquote pattern
    raise NotImplementedError


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
    # TODO: Implement wikilink parsing
    raise NotImplementedError
