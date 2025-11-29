# DocBook → Scribus Style Mapping

This note defines how DocBook elements map to Scribus paragraph styles for SOP documents.

| DocBook Element                  | Scribus Style |
| -------------------------------- | ------------- |
| `<title>` (top-level)           | Heading1      |
| `<section><title>` (nested)     | Heading2      |
| `<para>`                        | BodyText      |
| `<programlisting>`              | CodeBlock     |
| `<note role="callout">`         | Callout       |
| `<note role="warning">`         | Warning       |
| `<itemizedlist><listitem>`      | BodyText      |
| `<orderedlist><listitem>`       | BodyText      |
| `<table>` header row            | TableHeader   |
| `<table>` body row              | TableCell     |

As the pipeline grows more complex, add mappings here and reflect them in:

- Scribus styles (Edit → Styles…)
- `scribus_pipeline_advanced.py` logic
- Any XSLT or pre-processing steps applied to DocBook.
