"""Main pipeline orchestration.

Coordinates the full Markdown → PDF publishing workflow.
Part of SSP Document Publishing Pipeline v4.
"""

from pathlib import Path
from typing import Optional


def run_pipeline(
    markdown_path: Path,
    profile_path: Path,
    output_dir: Optional[Path] = None,
    skip_validation: bool = False
) -> Path:
    """
    Execute complete document publishing pipeline.

    Workflow:
    1. Load layout profile
    2. Validate inputs
    3. Parse Markdown front matter
    4. Generate Pandoc JSON AST
    5. Parse AST to block model
    6. Generate HTML with CSS classes
    7. Render to PDF (WeasyPrint or Scribus)
    8. Copy to published/
    9. Archive to releases/

    Args:
        markdown_path: Path to source Markdown file
        profile_path: Path to layout profile JSON
        output_dir: Custom output directory (default: from profile)
        skip_validation: Skip input validation (not recommended)

    Returns:
        Path to generated PDF file

    Raises:
        FileNotFoundError: If input files missing
        ValueError: If validation fails
        RuntimeError: If pipeline execution fails
    """
    # TODO: Implement full pipeline orchestration
    raise NotImplementedError


def generate_pandoc_ast(markdown_path: Path, output_path: Path) -> Path:
    """
    Generate Pandoc JSON AST from Markdown.

    Args:
        markdown_path: Path to source Markdown
        output_path: Path for JSON output

    Returns:
        Path to generated JSON AST file

    Raises:
        RuntimeError: If Pandoc execution fails
        FileNotFoundError: If Pandoc not installed
    """
    # TODO: Implement Pandoc subprocess call
    raise NotImplementedError


def cleanup_temp_files(temp_dir: Path) -> None:
    """
    Clean up temporary files after pipeline completion.

    Args:
        temp_dir: Directory containing temporary files
    """
    # TODO: Implement temp file cleanup
    raise NotImplementedError


def get_pipeline_version() -> str:
    """
    Return current pipeline version string.

    Returns:
        Version string (e.g., "4.0.0")
    """
    return "4.0.0"
