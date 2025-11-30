"""Obsidian-style callout detection and parsing.

Detects and parses callout syntax (> [!WARNING], > [!NOTE], etc.) from blockquotes.
Part of SSP Document Publishing Pipeline v4.

Callouts are special Markdown blockquotes used by Obsidian and other tools for
styled admonitions. Supported types: WARNING, DANGER, NOTE, TIP, INFO, CAUTION.

## Syntax

```markdown
> [!WARNING]
> This is a warning message.
> It can span multiple lines.

> [!NOTE] Optional Title
> This is a note with a custom title.
```

## Parsing

Callout detection is handled in the core parser (`pandoc_ast.py`) via the
`detect_callout()` function. When Pandoc encounters a blockquote starting with
`[!TYPE]`, it is converted to a Callout block object.

## Supported Types

- **WARNING**: Yellow/amber, caution symbol
- **DANGER**: Red, alert symbol
- **NOTE**: Blue, info symbol
- **TIP**: Green, lightbulb symbol
- **INFO**: Light blue, info symbol
- **CAUTION**: Orange, warning symbol

## Rendering

Callout blocks are styled in HTML as:
```html
<div class="callout callout-warning">
    <div class="callout-title">Warning</div>
    <div class="callout-content">This is a warning message.</div>
</div>
```

CSS classes can be customized via layout profiles to match branding.
"""

# All callout logic is implemented in pandoc_ast.py (detect_callout function)
# This module provides documentation and may be extended in future for:
# - Custom callout types
# - Icon mappings
# - Theme-specific rendering hints
