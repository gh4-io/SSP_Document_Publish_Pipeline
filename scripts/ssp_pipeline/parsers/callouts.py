"""Obsidian-style callout detection and parsing.

Detects and parses callout syntax (> [!WARNING], > [!NOTE], etc.) from blockquotes.
Part of SSP Document Publishing Pipeline v4.

Callouts are special Markdown blockquotes used by Obsidian and other tools for
styled admonitions. Supported types: WARNING, DANGER, NOTE, TIP, INFO.
"""

# TODO: Implement callout detection from Pandoc blockquote elements.
# Should parse `> [!TYPE] Title` syntax and extract type, optional title, and content.
# Return Callout block objects for rendering as styled HTML divs.
