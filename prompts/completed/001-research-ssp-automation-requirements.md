<objective>
Research and document comprehensive requirements for a flexible, robust SSP document automation pipeline that handles the full workflow: Markdown → Pandoc → DocBook → Scribus → PDF/HTML/Web.

This research will feed into architectural planning and guide implementation of feature gaps:
- Web output generation (HTML, responsive, web assets)
- Metadata validation (YAML schema, required fields, cross-references)
- Asset pipeline (image optimization for print/web, version control)
- Batch processing (multi-document operations, automated rebuilds)
- Image positioning and manipulation
- Flexible CSS, HTML, fonts, type rendering, emojis, unicode, layouts

The end goal is a production-ready system that's easily extensible and maintainable.
</objective>

<context>
**Current State**:
- Manual Markdown → Pandoc → DocBook → Scribus Python → PDF workflow
- Scripts: `scribus_pipeline_adv_v3.py`, `release_packager.py`
- Supports SOP/STD/REF/APP document families
- YAML front-matter metadata, layout profiles (`layout_map.yaml`)
- Scribus master pages (MP_FIRST, MP_CONT), frame-based layout
- Special Markdown directives: `<!-- ::PAGEBREAK -->`, `<!-- ::KEEP-TOGETHER -->`
- Asset management in `/assets` (images, XML, fonts, diagrams, web)

**Current Limitations**:
- No web output generation
- No metadata validation
- Manual image optimization
- No batch processing
- Limited flexibility for CSS/HTML/fonts/unicode
- Scribus-only (no HTML rendering path)

**Project Context**:
Read @CLAUDE.md for project standards and workflow details.
</context>

<research_scope>
Thoroughly investigate and document the following areas:

1. **Web Output Generation**:
   - Pandoc's HTML5 output capabilities and customization
   - CSS frameworks for responsive document layouts (print.css vs screen.css)
   - Static site generators vs custom HTML pipeline
   - Font embedding and web font formats (WOFF2, variable fonts)
   - Emoji and unicode rendering across browsers
   - Image responsive design (srcset, picture elements)
   - Syntax highlighting and code block rendering
   - Table of contents, cross-references, footnotes in HTML
   - Accessibility (ARIA, semantic HTML, WCAG compliance)

2. **Metadata Validation**:
   - YAML schema validation libraries (Python: pykwalify, cerberus, jsonschema)
   - Required field enforcement (document_id, revision, title, owner, approver, effective_date, status)
   - Cross-reference validation (upstream_apn, downstream_apn linking)
   - Revision numbering rules and automated incrementing
   - Status transition workflows (Draft → Review → Active)
   - Date format validation and effective_date logic
   - Custom validators for document_id patterns (SOP-###, STD-###, etc.)

3. **Asset Pipeline**:
   - Image optimization tools (Pillow, ImageMagick, sharp)
   - Print vs web resolution handling (300 DPI vs 72 DPI, adaptive sizing)
   - Format conversion (PNG, JPEG, WebP, AVIF)
   - Image compression strategies (lossless for print, lossy for web)
   - Asset versioning and cache invalidation
   - Image metadata (EXIF, alt text, captions)
   - SVG handling and optimization
   - Automated generation of image variants (print/web/thumbnail)

4. **Batch Processing**:
   - Multi-document conversion workflows
   - Parallel processing strategies (multiprocessing, asyncio)
   - Dependency tracking (which docs need rebuilding)
   - Incremental builds (only rebuild changed docs)
   - Build orchestration patterns (Makefile, task runners, custom scripts)
   - Error handling and rollback for batch operations
   - Progress reporting and logging

5. **Image Positioning & Manipulation**:
   - Pandoc image attributes and figure positioning
   - CSS positioning strategies (float, flexbox, grid)
   - Scribus image frame population and scaling
   - Directive expansion: `<!-- ::FIGURE scale=0.7 align=center border shadow caption="..." -->`
   - Image cropping, borders, shadows, captions
   - Automatic image sizing and aspect ratio preservation
   - Text wrapping around images

6. **Flexibility & Extensibility**:
   - Pandoc custom filters (Lua filters for transformation logic)
   - Template systems (Jinja2, Pandoc templates, Scribus templates)
   - CSS variable systems for theming
   - Font management (loading custom fonts, fallback stacks)
   - Plugin architecture for custom processors
   - Configuration file design (YAML, TOML, JSON)
   - Unicode normalization and character set handling
   - Layout engine flexibility (switching between Scribus, WeasyPrint, Paged.js)

7. **Current Codebase Patterns**:
   - Review existing scripts: @scripts/scribus_pipeline_adv_v3.py, @scripts/release_packager.py
   - Review layout configuration: @scripts/layout_map.yaml
   - Review Markdown standards: @_boilerplate/*.md (if exists)
   - Identify reusable functions and patterns
   - Document technical debt and improvement opportunities
</research_scope>

<deliverables>
Create a comprehensive research document: `./research/ssp-automation-requirements.md`

**Required Sections**:

1. **Executive Summary** (1-2 paragraphs)
   - High-level findings and recommendations
   - Critical gaps and opportunities

2. **Web Output Generation** (detailed analysis)
   - Recommended approach and rationale
   - Technology stack (Pandoc + filters, CSS framework, HTML templates)
   - Example workflow: Markdown → HTML conversion
   - Font and unicode handling strategy
   - Responsive design approach
   - Trade-offs and alternatives considered

3. **Metadata Validation** (detailed analysis)
   - Recommended validation library and rationale
   - Schema definition approach
   - Validation timing (pre-conversion, post-conversion, CI/CD)
   - Error reporting and user feedback
   - Example validation rules

4. **Asset Pipeline** (detailed analysis)
   - Recommended tools and workflow
   - Print vs web resolution strategy
   - Image format decision tree
   - Optimization benchmarks (size reduction, quality preservation)
   - Directory structure for variants
   - Example automation script outline

5. **Batch Processing** (detailed analysis)
   - Recommended orchestration approach
   - Parallelization strategy
   - Dependency tracking implementation
   - Error handling and recovery
   - Example build script outline

6. **Image Positioning & Manipulation** (detailed analysis)
   - Recommended directive syntax and expansion logic
   - CSS positioning patterns for web
   - Scribus frame manipulation for PDF
   - Example implementations

7. **Flexibility & Extensibility** (architectural recommendations)
   - Plugin architecture design
   - Configuration management strategy
   - Template system design
   - Font loading and fallback approach
   - Unicode and character set best practices
   - Future-proofing considerations

8. **Current Codebase Analysis**
   - Reusable components identified
   - Integration points for new features
   - Technical debt to address
   - Migration considerations

9. **Recommendations Summary**
   - Prioritized feature list
   - Technology choices with rationale
   - Architecture patterns to adopt
   - Quick wins vs long-term investments

10. **Open Questions**
    - Unresolved technical decisions
    - Areas needing clarification
    - Trade-offs requiring user input
</deliverables>

<research_approach>
For maximum efficiency, perform research in parallel where possible:

1. **Explore existing codebase** to understand current patterns
2. **Research technology options** for each feature gap (web, validation, assets, batch)
3. **Investigate integration approaches** for combining new features with existing workflow
4. **Document findings incrementally** as you discover information

Use web search for:
- Current best practices (2025 standards for Pandoc, HTML/CSS, Python libraries)
- Comparison articles (e.g., "Python YAML validation libraries comparison")
- Performance benchmarks (e.g., "image optimization tools benchmark")
- Unicode and font rendering best practices

Read existing code to:
- Understand current architecture and patterns
- Identify integration points
- Find reusable functions
- Document technical constraints
</research_approach>

<success_criteria>
The research document must:
- Provide clear, actionable recommendations for each feature gap
- Include technology choices with rationale (WHY this approach)
- Document trade-offs and alternatives considered
- Identify integration points with existing codebase
- Be comprehensive enough to feed into detailed planning
- Include concrete examples (code snippets, workflow diagrams, configuration samples)
- Address flexibility and extensibility requirements explicitly
- Consider maintenance burden and future modifications
</success_criteria>

<output_handoff>
This research output will feed into the PLANNING stage, which will use it to create a detailed implementation plan with:
- Step-by-step tasks
- File modifications
- Testing strategies
- Migration approach

Ensure the research document is detailed enough to support planning without requiring additional research rounds.
</output_handoff>
