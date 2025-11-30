"""SSP Document Publishing Pipeline v4.

Modern Markdown → PDF publishing pipeline using Pandoc, WeasyPrint, and Scribus layouts.
"""

__version__ = "4.0.0"
__author__ = "Jason Grace"

# Core modules
from . import config
from . import metadata
from . import pipeline

# Subpackages
from . import parsers
from . import renderers
from . import layouts
from . import utils

# Main entry point
from .pipeline import run_pipeline, get_pipeline_version

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Core modules
    "config",
    "metadata",
    "pipeline",
    # Subpackages
    "parsers",
    "renderers",
    "layouts",
    "utils",
    # Main functions
    "run_pipeline",
    "get_pipeline_version",
]
