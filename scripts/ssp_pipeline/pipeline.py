"""Main pipeline orchestration.

Coordinates the full Markdown → PDF publishing workflow.
Part of SSP Document Publishing Pipeline v4.
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, List

from . import config
from . import metadata as meta_module
from .parsers import pandoc_ast
from .renderers import html_generator
from .renderers import weasyprint_renderer
from .utils import logging as log_utils
from .utils import file_ops
from .utils import validators

logger = logging.getLogger(__name__)


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
    logger.info("=" * 60)
    logger.info("SSP Document Publishing Pipeline v4 Starting")
    logger.info("=" * 60)
    log_utils.log_pipeline_start(str(markdown_path))

    # Step 1: Load layout profile
    logger.info("Step 1/9: Loading layout profile")
    profile = config.load_layout_profile(profile_path)
    rendering_engine = config.get_rendering_engine(profile)
    base_dir = profile_path.parent.parent  # Go up to repo root
    resources = config.get_resource_paths(profile, base_dir)
    styles_map = config.get_styles_map(profile)

    # Step 2: Validate inputs
    if not skip_validation:
        logger.info("Step 2/9: Validating inputs")
        validators.validate_markdown(markdown_path)
        validators.validate_profile(profile)
    else:
        logger.warning("Step 2/9: Skipping validation (not recommended)")

    # Step 3: Parse Markdown frontmatter
    logger.info("Step 3/9: Parsing frontmatter")
    raw_metadata = meta_module.parse_frontmatter(markdown_path)
    normalized_metadata = meta_module.normalize_metadata(raw_metadata)
    doc_id = meta_module.extract_document_id(normalized_metadata)
    logger.info(f"Document ID: {doc_id}")

    # Step 4: Generate Pandoc JSON AST
    logger.info("Step 4/9: Generating Pandoc JSON AST")
    temp_json = Path(f"/tmp/{doc_id}_ast.json")
    generate_pandoc_ast(markdown_path, temp_json)

    # Step 5: Parse AST to block model
    logger.info("Step 5/9: Parsing AST to block model")
    blocks = pandoc_ast.parse_pandoc_json(temp_json)
    logger.info(f"Parsed {len(blocks)} blocks")

    # Step 6: Generate HTML
    logger.info("Step 6/9: Generating HTML")
    html_content = html_generator.generate_html(blocks, normalized_metadata, styles_map)

    # Step 7: Render to PDF
    logger.info(f"Step 7/9: Rendering to PDF using {rendering_engine}")

    if rendering_engine == "weasyprint":
        # Get CSS paths from resources
        css_paths: List[Path] = []
        if "css_template" in resources:
            css_paths.append(resources["css_template"])
        if "markdown_theme" in resources:
            css_paths.append(resources["markdown_theme"])

        # Determine output path
        if output_dir:
            pdf_out = output_dir / f"{doc_id}.pdf"
        elif "pdf_directory" in resources:
            pdf_out = resources["pdf_directory"] / f"{doc_id}.pdf"
        else:
            pdf_out = Path(f"published/pdf/{doc_id}.pdf")

        file_ops.ensure_dir(pdf_out.parent)
        pdf_path = weasyprint_renderer.render_pdf(
            html_content,
            css_paths,
            pdf_out,
            normalized_metadata
        )
    else:
        raise NotImplementedError(f"Rendering engine '{rendering_engine}' not yet implemented")

    # Step 8: Copy to published/
    logger.info("Step 8/9: Copying to published directory")
    published_path = file_ops.copy_to_published(pdf_path, doc_id)

    # Step 9: Archive to releases/
    logger.info("Step 9/9: Archiving to releases")
    category = doc_id.split('-')[0]  # Extract SOP, STD, REF, APP
    file_ops.archive_to_releases(published_path, category)

    # Cleanup temp files
    cleanup_temp_files(temp_json.parent)

    log_utils.log_pipeline_complete(str(markdown_path), str(published_path))
    logger.info("=" * 60)
    logger.info(f"Pipeline Complete! Output: {published_path}")
    logger.info("=" * 60)

    return published_path


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
    logger.info(f"Calling Pandoc: {markdown_path} → {output_path}")

    # Ensure output directory exists
    file_ops.ensure_dir(output_path.parent)

    # Build pandoc command
    cmd = [
        "pandoc",
        str(markdown_path),
        "-t", "json",
        "-o", str(output_path)
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        logger.debug("Pandoc completed successfully")

        if not output_path.exists():
            raise RuntimeError(f"Pandoc did not create output file: {output_path}")

        return output_path

    except FileNotFoundError:
        raise FileNotFoundError(
            "Pandoc not found. Install with: apt install pandoc (or brew/choco)"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Pandoc failed with exit code {e.returncode}\n"
            f"stdout: {e.stdout}\nstderr: {e.stderr}"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Pandoc execution timed out after 60 seconds")


def cleanup_temp_files(temp_dir: Path) -> None:
    """
    Clean up temporary files after pipeline completion.

    Args:
        temp_dir: Directory containing temporary files
    """
    if not temp_dir.exists():
        return

    # Only clean up files matching our pattern (doc_id_ast.json)
    for temp_file in temp_dir.glob("*_ast.json"):
        try:
            temp_file.unlink()
            logger.debug(f"Cleaned up temp file: {temp_file}")
        except Exception as e:
            logger.warning(f"Failed to delete temp file {temp_file}: {e}")


def get_pipeline_version() -> str:
    """
    Return current pipeline version string.

    Returns:
        Version string (e.g., "4.0.0")
    """
    return "4.0.0"
