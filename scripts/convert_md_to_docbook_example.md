# Markdown → DocBook Conversion (Pandoc)

Example commands (run outside Scribus) for converting Markdown SOPs to DocBook XML.

Basic example:

```bash
pandoc   --from markdown   --to docbook   --output drafts/SOP-001.docbook.xml   drafts/SOP-001.md
```

With a custom reference or filters:

```bash
pandoc   --from markdown   --to docbook   --output drafts/SOP-001.docbook.xml   --metadata-file=metadata.yaml   --filter ./scripts/pandoc_filter_docbook_cleanup.py   drafts/SOP-001.md
```

These commands can be wrapped in a higher-level script that also generates the **job JSON** consumed by `scribus_pipeline_advanced.py`.
