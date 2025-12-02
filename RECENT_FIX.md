● Summary of Fixes

  ✅ Issue 1: Files dumped in wrong directories (templates/published/, templates/releases/)

  Root Cause: copy_to_published() and archive_to_releases() used source_path.parent.parent.parent creating relative paths
  Fix: Changed to Path.cwd() / "published" and Path.cwd() / "releases" (file_ops.py:84, 113)
  Result: Files now correctly go to published/pdf/ and releases/SOP/

  ✅ Issue 2: .sla file not being used

  Root Cause: DTS profile missing rendering_engine field, defaulted to weasyprint
  Fix: Added auto-detection in get_rendering_engine() - if scribus_template exists in resources, use scribus engine (config.py:79-81)
  Status: Scribus now detected but raises NotImplementedError (expected - renderer not implemented yet)
  Workaround: Remove pipeline_profile: dts_master_report from frontmatter to use WeasyPrint

  ✅ Issue 3: No content rendering (bullets, sub-headers, paragraphs empty)

  Root Causes:
  1. List parsing broken: pandoc_ast.py tried to double-unwrap list items, getting first block instead of all blocks
  2. Missing CSS files: No default profile or CSS existed, WeasyPrint had no styles
  3. Styles_map mismatch: HTML generator expected styles_map["pandoc"] but DTS uses styles_map["docbook"]

  Fixes:
  - Fixed BulletList/OrderedList parsing to iterate item_blocks directly, check for "Para" OR "Plain" blocks (pandoc_ast.py:185-213)
  - Created layout_profile_default.json with WeasyPrint config (templates/profiles/)
  - Created default_layout.css with page layout (templates/styles/)
  - Created default_theme.css with element styles (templates/styles/)
  - Changed HTML generator to use flat styles_map keys: heading1, paragraph, etc. (html_generator.py:121-144)

  Test Results

  Test Document (TEST-002):
  - PDF size: 10KB (was 22KB empty)
  - Contains full content: headings, paragraphs, bullets, numbered lists ✅
  - Output: published/pdf/TEST-002.pdf
  - Archive: releases/TEST/TEST-002_v1_20251201_163113/

  SOP-200 (without DTS profile override):
  - PDF size: 15KB
  - Contains full document structure ✅
  - Output: published/pdf/SOP-200.pdf
  - Archive: releases/SOP/SOP-200_v0_20251201_163201/

  Remaining Limitation

  Scribus rendering not implemented: When documents specify pipeline_profile: dts_master_report, pipeline detects scribus but raises NotImplementedError. To use these docs:
  - Option 1: Remove pipeline_profile: dts_master_report from frontmatter
  - Option 2: Add rendering_engine: weasyprint to DTS profile JSON
  - Option 3: Implement scribus_renderer.render_pdf_from_sla() function

  Run now:
  # Works (uses default WeasyPrint profile):
  uv run python3 -m scripts.ssp_pipeline.pipeline /tmp/test_simple.md templates/profiles/layout_profile_default.json

  # Fails (SOP-200 requests scribus):
  uv run python3 -m scripts.ssp_pipeline.pipeline drafts/SOP-200_Create_Workackage_Sequencing_Type.md templates/profiles/layout_profile_default.json