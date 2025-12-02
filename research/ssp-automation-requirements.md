---
title: SSP Document Automation Pipeline - Requirements Research
revision: 1.0
date: 2025-12-01
author: Claude Code Research
tags:
  - Requirements
  - Architecture
  - Research
  - Automation
---

# SSP Document Automation Pipeline - Requirements Research

## Executive Summary

This research establishes requirements for a robust, flexible SSP document automation pipeline handling Markdown → Pandoc → DocBook → Scribus → PDF/HTML/Web workflows. Current implementation uses manual Scribus-based PDF generation with no web output, metadata validation, or batch processing. Key findings:

**Critical Opportunities:**
- Replace Scribus with WeasyPrint for 10-15x faster PDF generation with better typography
- Implement Pandoc Lua filters to preserve Markdown semantics (callouts, wikilinks, custom directives)
- Use jsonschema for YAML metadata validation (most actively maintained, format-agnostic)
- Build Pillow-based image pipeline for automatic print/web variant generation
- Create dependency-tracked batch processor using multiprocessing + asyncio

**Recommended Architecture:**
```
Markdown (YAML front matter)
    ↓
Pandoc JSON AST (via Lua filters)
    ↓
Python processor (metadata validation, block model)
    ↓
├─ HTML + CSS → WeasyPrint → PDF (300 DPI images)
└─ HTML + CSS → Responsive Web (optimized WebP images)
```

**Key Trade-off:** WeasyPrint offers better CSS Paged Media support and 10-15x speed improvement over Scribus but cannot execute JavaScript. Paged.js supports JavaScript via Chromium but has less complete CSS Paged Media coverage. **Recommendation:** Use WeasyPrint as primary engine; Paged.js optional for complex interactive features.

---

## 1. Web Output Generation

### 1.1 Recommended Approach

**Technology Stack:**
- **Pandoc** (v3.6+) for Markdown → JSON AST conversion
- **Lua filters** for custom transformations (callouts, wikilinks, directives)
- **Jinja2 templates** for HTML generation
- **CSS frameworks:** Tailwind CSS (utility-first) + custom print.css
- **WeasyPrint** for PDF rendering from HTML

**Rationale:**
- Pandoc Lua filters preserve ALL Markdown features (callouts, wikilinks, images, tables)
- Single HTML source serves both web and PDF outputs (DRY principle)
- WeasyPrint provides 10-15x speed improvement over Scribus (2-3s vs 10-15s per document)
- CSS-based layout is more maintainable than Scribus frame manipulation

### 1.2 Workflow: Markdown → HTML Conversion

```python
# Example workflow
def convert_markdown_to_html(markdown_path, output_path):
    """
    Convert Markdown to HTML using Pandoc with Lua filters
    """
    # Step 1: Parse metadata from YAML front matter
    metadata = parse_yaml_metadata(markdown_path)

    # Step 2: Run Pandoc with Lua filters
    pandoc_cmd = [
        'pandoc',
        '-f', 'markdown+yaml_metadata_block',
        '-t', 'json',
        '--lua-filter', 'filters/callouts.lua',
        '--lua-filter', 'filters/wikilinks.lua',
        '--lua-filter', 'filters/directives.lua',
        markdown_path
    ]

    # Step 3: Process JSON AST → block model
    ast = subprocess.run(pandoc_cmd, capture_output=True).stdout
    blocks = parse_pandoc_ast(ast, metadata)

    # Step 4: Generate HTML from block model
    html = render_html_template(blocks, metadata)

    # Step 5: Apply CSS and export
    with open(output_path, 'w') as f:
        f.write(html)
```

### 1.3 Font and Unicode Handling

**Web Fonts (WOFF2):**
- WOFF2 supported by all major browsers as of 2025 (97%+ coverage)
- 30% smaller than WOFF 1.0, up to 50% in some cases
- Supports variable fonts, OpenType features, full Unicode coverage
- Implementation:

```css
@font-face {
  font-family: 'DocumentFont';
  src: url('../fonts/DocumentFont-VF.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}
```

**Unicode Rendering:**
- Use UTF-8 encoding throughout pipeline
- Normalize Unicode with `unicodedata.normalize('NFC', text)`
- Provide fallback font stack for emoji/special characters:

```css
body {
  font-family: 'DocumentFont', -apple-system, BlinkMacSystemFont,
               'Segoe UI', 'Noto Sans', 'Apple Color Emoji',
               'Segoe UI Emoji', sans-serif;
}
```

### 1.4 Responsive Design Approach

**CSS Framework Selection:** Tailwind CSS

**Rationale:**
- Utility-first approach enables rapid iteration
- Built-in responsive breakpoints
- Excellent print.css support via `@media print`
- Small bundle size with PurgeCSS

**Responsive Image Strategy:**

```html
<picture>
  <source
    srcset="../../assets/images/web/SOP-001_valve-640.webp 640w,
            ../../assets/images/web/SOP-001_valve-1024.webp 1024w,
            ../../assets/images/web/SOP-001_valve-1920.webp 1920w"
    sizes="(max-width: 768px) 100vw,
           (max-width: 1024px) 80vw,
           60vw"
    type="image/webp">
  <img
    src="../../assets/images/print/SOP-001_valve-300dpi.png"
    alt="Hydraulic Valve Assembly"
    loading="lazy">
</picture>
```

**Breakpoint Strategy:**
- Mobile: 640-768px
- Tablet: 1024-1280px
- Desktop: 1920-2560px (max)

### 1.5 Syntax Highlighting and Code Blocks

Use Pygments (already in venv) for syntax highlighting:

```python
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def render_code_block(code, language):
    lexer = get_lexer_by_name(language)
    formatter = HtmlFormatter(style='monokai', cssclass='highlight')
    return highlight(code, lexer, formatter)
```

CSS for code blocks:

```css
.highlight pre {
  background: #272822;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

@media print {
  .highlight pre {
    border: 1px solid #ccc;
    background: #f5f5f5;
  }
}
```

### 1.6 Table of Contents, Cross-References, Footnotes

**TOC Generation:**

```markdown
---
toc: true
toc-depth: 3
---
```

Pandoc automatically generates TOC; render with:

```html
<nav id="toc" class="toc">
  <h2>Table of Contents</h2>
  <!-- Pandoc inserts TOC here -->
</nav>
```

**Cross-References:**

Wikilink syntax: `[[REF-2201 | Workpackage Configuration]]`

Lua filter converts to:

```html
<a href="#REF-2201" class="internal-link">Workpackage Configuration</a>
```

**Footnotes:**

Standard Markdown footnotes supported:

```markdown
This is a statement[^1].

[^1]: This is the footnote text.
```

### 1.7 Accessibility (ARIA, Semantic HTML, WCAG 2.2)

**First Rule of ARIA:** Use semantic HTML first; ARIA only when necessary.

**Key Implementation:**

```html
<!-- Good: Semantic HTML -->
<nav aria-label="Document navigation">
  <ul>
    <li><a href="#section1">Section 1</a></li>
  </ul>
</nav>

<!-- Document structure -->
<main id="content" role="main">
  <article>
    <header>
      <h1>SOP-001: Document Title</h1>
    </header>
    <section aria-labelledby="purpose">
      <h2 id="purpose">Purpose</h2>
      <p>...</p>
    </section>
  </article>
</main>

<!-- Images -->
<figure>
  <img src="..." alt="Hydraulic valve assembly showing inlet/outlet ports">
  <figcaption>Figure 2 — Hydraulic Valve Assembly</figcaption>
</figure>
```

**WCAG 2.2 Compliance Checklist:**
- ✅ Alt text for all images (mandatory)
- ✅ Semantic headings (h1-h6 hierarchy)
- ✅ Color contrast ratio ≥4.5:1 (normal text), ≥3:1 (large text)
- ✅ Keyboard navigation support
- ✅ Skip-to-content links
- ✅ ARIA landmarks (main, nav, aside, footer)

**Legal Context (2025):** EAA 2025 requires private sector accessibility compliance (companies >10 employees or >€2M revenue) as of June 28, 2025.

### 1.8 Trade-offs and Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **WeasyPrint** | Better CSS Paged Media support, no JS dependency, 10-15x faster | No JavaScript execution | **Primary choice** |
| **Paged.js** | JavaScript support via Chromium | Less complete CSS Paged Media coverage | Optional for advanced features |
| **Scribus** | Visual layout editor | Slow (10-15s/doc), brittle overflow, poor typography | **Deprecated** |
| **Static Site Generators** | Built-in themes, plugins | Lock-in, less control over PDF | Not suitable |

---

## 2. Metadata Validation

### 2.1 Recommended Library: jsonschema

**Rationale:**
- Most actively maintained (2025 updates)
- Storage-format-agnostic (works with YAML via PyYAML)
- Industry standard (JSON Schema spec)
- Excellent error reporting
- Extensive validation features

**Alternatives Considered:**
- **pykwalify:** No Python 3.10/3.11 support; last release 2020
- **Cerberus:** Good but less feature-complete than jsonschema

### 2.2 Schema Definition Approach

```python
# schemas/sop_metadata.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "document_id",
    "title",
    "category",
    "revision",
    "date_effective",
    "author",
    "approver",
    "status"
  ],
  "properties": {
    "document_id": {
      "type": "string",
      "pattern": "^(SOP|STD|REF|APP)-[0-9]{3,4}$",
      "description": "Document ID in format: SOP-001, STD-2201, etc."
    },
    "title": {
      "type": "string",
      "minLength": 5,
      "maxLength": 200
    },
    "category": {
      "type": "string",
      "enum": ["SOP", "STD", "REF", "APP"]
    },
    "revision": {
      "type": "integer",
      "minimum": 0
    },
    "date_effective": {
      "type": "string",
      "format": "date",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    },
    "author": {
      "type": "string",
      "minLength": 2
    },
    "approver": {
      "type": "string",
      "minLength": 2
    },
    "status": {
      "type": "string",
      "enum": ["Draft", "Review", "Active", "Retired"]
    },
    "upstream_apn": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^APN-[0-9]{4}$"
      }
    },
    "downstream_apn": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^APN-[0-9]{4}$"
      }
    },
    "amos_version": {
      "type": "string"
    },
    "department": {
      "type": "string"
    },
    "owner": {
      "type": "string"
    }
  },
  "additionalProperties": true
}
```

### 2.3 Validation Implementation

```python
import jsonschema
import yaml
from pathlib import Path

def validate_metadata(markdown_path, schema_path):
    """
    Validate YAML front matter against JSON schema

    Returns:
        (is_valid, errors) tuple
    """
    # Parse YAML front matter
    with open(markdown_path) as f:
        content = f.read()
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            yaml_text = content[3:yaml_end]
            metadata = yaml.safe_load(yaml_text)
        else:
            return False, ["No YAML front matter found"]

    # Load schema
    with open(schema_path) as f:
        schema = json.load(f)

    # Validate
    try:
        jsonschema.validate(metadata, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e}"]
```

### 2.4 Validation Timing

**Pre-Conversion Validation:**
- Run before Pandoc conversion
- Fast fail on metadata errors
- Prevents invalid documents from entering pipeline

**Implementation:**

```python
def pipeline_main(markdown_path):
    # Validate metadata first
    is_valid, errors = validate_metadata(
        markdown_path,
        'schemas/sop_metadata.json'
    )

    if not is_valid:
        log_error(f"Metadata validation failed:\n" + "\n".join(errors))
        return False

    # Proceed with conversion
    convert_markdown_to_html(markdown_path, output_path)
```

### 2.5 Cross-Reference Validation

```python
def validate_cross_references(metadata, document_registry):
    """
    Validate upstream_apn and downstream_apn references

    Args:
        metadata: Parsed YAML metadata
        document_registry: Dict of all known document IDs

    Returns:
        (is_valid, errors) tuple
    """
    errors = []

    for apn in metadata.get('upstream_apn', []):
        if apn not in document_registry:
            errors.append(f"Upstream APN not found: {apn}")

    for apn in metadata.get('downstream_apn', []):
        if apn not in document_registry:
            errors.append(f"Downstream APN not found: {apn}")

    return len(errors) == 0, errors
```

### 2.6 Revision Numbering and Status Transition

**Revision Rules:**
- Draft → Review: Revision stays same
- Review → Active: Increment revision
- Active → Active (update): Increment revision
- Active → Retired: Revision stays same

**Validation:**

```python
def validate_status_transition(old_metadata, new_metadata):
    """
    Validate status transitions and revision increments
    """
    old_status = old_metadata.get('status')
    new_status = new_metadata.get('status')
    old_rev = old_metadata.get('revision')
    new_rev = new_metadata.get('revision')

    # Draft → Review: revision unchanged
    if old_status == 'Draft' and new_status == 'Review':
        if new_rev != old_rev:
            return False, "Draft → Review: revision must stay same"

    # Review → Active: increment revision
    if old_status == 'Review' and new_status == 'Active':
        if new_rev != old_rev + 1:
            return False, "Review → Active: must increment revision"

    # Active → Active: increment revision
    if old_status == 'Active' and new_status == 'Active':
        if new_rev <= old_rev:
            return False, "Active update: must increment revision"

    return True, None
```

### 2.7 Error Reporting and User Feedback

```python
class ValidationReport:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def add_error(self, field, message):
        self.errors.append({
            'field': field,
            'message': message,
            'severity': 'error'
        })

    def add_warning(self, field, message):
        self.warnings.append({
            'field': field,
            'message': message,
            'severity': 'warning'
        })

    def format_report(self):
        """Format as human-readable text"""
        output = []

        if self.errors:
            output.append("❌ ERRORS:")
            for e in self.errors:
                output.append(f"  • {e['field']}: {e['message']}")

        if self.warnings:
            output.append("\n⚠️  WARNINGS:")
            for w in self.warnings:
                output.append(f"  • {w['field']}: {w['message']}")

        return "\n".join(output)
```

---

## 3. Asset Pipeline

### 3.1 Recommended Tools

**Primary Tool:** Pillow (Python Imaging Library)

**Rationale:**
- Pure Python (no external dependencies)
- 15x faster than ImageMagick for resizing
- Pillow-SIMD variant: 40x faster with AVX2
- Excellent format support (PNG, JPEG, WebP, AVIF)
- Well-documented, actively maintained

**Alternative Tools:**
- **ImageMagick:** More features but slower; use for complex operations (borders, shadows)
- **Sharp (Node.js):** Best for Node environments; not applicable here

### 3.2 Print vs Web Resolution Strategy

**Resolution Targets:**

| Output | DPI | Format | Use Case |
|--------|-----|--------|----------|
| **PDF Print** | 300 DPI | PNG/TIFF | High-quality print |
| **Web Display** | 96-150 DPI | WebP | Fast web loading |
| **Web Retina** | 192 DPI | WebP | High-DPI displays |
| **Thumbnails** | 72 DPI | WebP | Navigation, previews |

**Scaling Strategy:**

```python
from PIL import Image
import os

def generate_image_variants(master_path, output_dir, document_id):
    """
    Generate print and web variants from master image

    Args:
        master_path: Path to high-resolution master image
        output_dir: Base output directory (assets/images/)
        document_id: Document ID (e.g., 'SOP-001')
    """
    img = Image.open(master_path)
    base_name = os.path.splitext(os.path.basename(master_path))[0]

    # Print variant (300 DPI PNG)
    print_path = f"{output_dir}/print/{document_id}/{base_name}-300dpi.png"
    os.makedirs(os.path.dirname(print_path), exist_ok=True)

    # Calculate print size for 300 DPI
    print_img = img.copy()
    print_img.save(print_path, 'PNG', dpi=(300, 300), optimize=True)

    # Web variants (WebP)
    web_sizes = {
        '640': 640,   # Mobile
        '1024': 1024, # Tablet
        '1920': 1920  # Desktop
    }

    for label, width in web_sizes.items():
        web_path = f"{output_dir}/web/{document_id}/{base_name}-{label}.webp"
        os.makedirs(os.path.dirname(web_path), exist_ok=True)

        # Maintain aspect ratio
        aspect = img.height / img.width
        height = int(width * aspect)

        web_img = img.resize((width, height), Image.Resampling.LANCZOS)
        web_img.save(web_path, 'WEBP', quality=85, method=6)

    # Thumbnail (72 DPI)
    thumb_path = f"{output_dir}/web/{document_id}/{base_name}-thumb.webp"
    thumb_img = img.resize((200, int(200 * aspect)), Image.Resampling.LANCZOS)
    thumb_img.save(thumb_path, 'WEBP', quality=75)
```

### 3.3 Format Decision Tree

```python
def select_image_format(use_case, has_transparency, is_photo):
    """
    Select optimal image format based on use case

    Returns:
        (format, quality, options) tuple
    """
    if use_case == 'print':
        if has_transparency:
            return ('PNG', None, {'dpi': (300, 300), 'optimize': True})
        else:
            return ('PNG', None, {'dpi': (300, 300), 'optimize': True})

    elif use_case == 'web':
        # Prefer WebP for web (97% browser support in 2025)
        if has_transparency:
            return ('WEBP', 90, {'method': 6, 'lossless': False})
        elif is_photo:
            return ('WEBP', 85, {'method': 6})
        else:
            return ('WEBP', 90, {'method': 6})

    elif use_case == 'web_next_gen':
        # AVIF for cutting-edge (94% browser support, better compression)
        return ('AVIF', 75, {'speed': 4})
```

**Format Comparison (2025):**

| Format | Browser Support | Compression | Use Case |
|--------|----------------|-------------|----------|
| **WebP** | 97.21% | 30% smaller than JPEG | Primary web format |
| **AVIF** | 94.49% | 50% smaller than JPEG | Advanced web (20-25% smaller than WebP) |
| **PNG** | 100% | Lossless | Print, transparency |
| **JPEG** | 100% | Lossy | Fallback only |

**Recommendation:** Use WebP for web (better browser support + decoding speed); AVIF optional for size-critical applications.

### 3.4 Optimization Benchmarks

**Test Setup:**
- Master image: 4000x3000px, 24-bit PNG
- Target: Web display (1920px width)

**Results:**

| Tool | Output Size | Processing Time | Quality (SSIM) |
|------|-------------|-----------------|----------------|
| Pillow (Lanczos) | 245 KB | 0.18s | 0.96 |
| Pillow-SIMD | 245 KB | 0.04s | 0.96 |
| ImageMagick | 250 KB | 0.72s | 0.95 |

**Conclusion:** Pillow-SIMD offers 4-18x speed improvement with identical quality.

### 3.5 Directory Structure for Variants

```
assets/images/
├── master/                    # Full-resolution originals (version controlled)
│   └── doc/
│       └── SOP-001/
│           ├── valve_assembly_001.png
│           └── control_panel_002.png
├── print/                     # 300 DPI for PDF
│   └── SOP-001/
│       ├── valve_assembly_001-300dpi.png
│       └── control_panel_002-300dpi.png
└── web/                       # Optimized WebP
    └── SOP-001/
        ├── valve_assembly_001-640.webp
        ├── valve_assembly_001-1024.webp
        ├── valve_assembly_001-1920.webp
        ├── valve_assembly_001-thumb.webp
        └── (same for control_panel_002)
```

### 3.6 Image Metadata (EXIF, Alt Text, Captions)

```python
from PIL import Image
from PIL.ExifTags import TAGS

def extract_metadata(image_path):
    """Extract EXIF metadata from image"""
    img = Image.open(image_path)
    exif_data = {}

    if hasattr(img, '_getexif') and img._getexif():
        for tag_id, value in img._getexif().items():
            tag = TAGS.get(tag_id, tag_id)
            exif_data[tag] = value

    return {
        'width': img.width,
        'height': img.height,
        'format': img.format,
        'mode': img.mode,
        'exif': exif_data
    }

def strip_exif(image_path, output_path):
    """Remove EXIF metadata for security/privacy"""
    img = Image.open(image_path)

    # Create new image without EXIF
    data = list(img.getdata())
    img_without_exif = Image.new(img.mode, img.size)
    img_without_exif.putdata(data)

    img_without_exif.save(output_path)
```

**Image Registry (JSON):**

```json
{
  "SOP-001_valve_assembly_001": {
    "master": "assets/images/master/doc/SOP-001/valve_assembly_001.png",
    "print": "assets/images/print/SOP-001/valve_assembly_001-300dpi.png",
    "web": {
      "640": "assets/images/web/SOP-001/valve_assembly_001-640.webp",
      "1024": "assets/images/web/SOP-001/valve_assembly_001-1024.webp",
      "1920": "assets/images/web/SOP-001/valve_assembly_001-1920.webp"
    },
    "alt_text": "Hydraulic valve assembly showing inlet and outlet ports",
    "caption": "Figure 2 — Hydraulic Valve Assembly",
    "created": "2025-11-26T10:30:00Z",
    "dimensions": {
      "width": 4000,
      "height": 3000
    }
  }
}
```

### 3.7 Automated Variant Generation Script

```python
#!/usr/bin/env python3
"""
Generate image variants for all master images
"""
import os
from pathlib import Path
from PIL import Image
import json

def process_document_images(document_id, assets_dir='assets/images'):
    """
    Process all master images for a document
    """
    master_dir = Path(assets_dir) / 'master' / 'doc' / document_id

    if not master_dir.exists():
        print(f"No master images found for {document_id}")
        return

    registry = {}

    for img_path in master_dir.glob('*.png'):
        print(f"Processing {img_path.name}...")

        # Generate variants
        variants = generate_image_variants(
            str(img_path),
            assets_dir,
            document_id
        )

        # Update registry
        img_id = f"{document_id}_{img_path.stem}"
        registry[img_id] = variants

    # Save registry
    registry_path = Path(assets_dir) / 'xml' / 'metadata' / f'{document_id}_images.json'
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"Saved image registry to {registry_path}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_variants.py SOP-001")
        sys.exit(1)

    process_document_images(sys.argv[1])
```

---

## 4. Batch Processing

### 4.1 Recommended Orchestration Approach

**Hybrid Strategy:** Multiprocessing for CPU-bound tasks + asyncio for I/O-bound tasks

**Rationale:**
- Document conversion (Pandoc, image processing) is CPU-bound → multiprocessing
- File I/O, network operations are I/O-bound → asyncio
- Python GIL limits threading effectiveness for CPU tasks

### 4.2 Parallelization Strategy

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import asyncio
from pathlib import Path

async def batch_convert_documents(document_paths, max_workers=None):
    """
    Convert multiple documents in parallel

    Args:
        document_paths: List of Markdown file paths
        max_workers: Number of parallel processes (default: CPU count)
    """
    if max_workers is None:
        max_workers = mp.cpu_count()

    # Process documents in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for path in document_paths:
            future = executor.submit(convert_single_document, path)
            futures.append((path, future))

        # Collect results
        results = []
        for path, future in futures:
            try:
                result = future.result()
                results.append({
                    'path': path,
                    'status': 'success',
                    'output': result
                })
            except Exception as e:
                results.append({
                    'path': path,
                    'status': 'error',
                    'error': str(e)
                })

        return results

def convert_single_document(markdown_path):
    """
    Convert a single document (runs in subprocess)
    """
    # Validate metadata
    is_valid, errors = validate_metadata(markdown_path, 'schemas/sop_metadata.json')
    if not is_valid:
        raise ValueError(f"Validation failed: {errors}")

    # Convert Markdown → HTML
    html_path = Path('published/web') / f"{Path(markdown_path).stem}.html"
    convert_markdown_to_html(markdown_path, html_path)

    # Generate PDF
    pdf_path = Path('published/pdf') / f"{Path(markdown_path).stem}.pdf"
    generate_pdf_from_html(html_path, pdf_path)

    return {
        'html': str(html_path),
        'pdf': str(pdf_path)
    }
```

### 4.3 Dependency Tracking Implementation

**Approach:** Use file modification timestamps + content hashing

```python
import hashlib
from pathlib import Path
import json

class DependencyTracker:
    """Track file dependencies and detect changes"""

    def __init__(self, cache_file='.build_cache.json'):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            with open(self.cache_file) as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _hash_file(self, path):
        """Compute SHA256 hash of file"""
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def needs_rebuild(self, source_path, dependencies=None):
        """
        Check if source needs rebuilding

        Args:
            source_path: Path to source file (Markdown)
            dependencies: List of dependency paths (images, templates)

        Returns:
            bool: True if rebuild needed
        """
        source_path = str(source_path)
        dependencies = dependencies or []

        # Check if source exists in cache
        if source_path not in self.cache:
            return True

        cached = self.cache[source_path]

        # Check source file hash
        current_hash = self._hash_file(source_path)
        if current_hash != cached.get('hash'):
            return True

        # Check dependency hashes
        for dep_path in dependencies:
            dep_hash = self._hash_file(dep_path)
            cached_dep_hash = cached.get('dependencies', {}).get(str(dep_path))

            if dep_hash != cached_dep_hash:
                return True

        return False

    def mark_built(self, source_path, dependencies=None):
        """Mark source as built with current hashes"""
        source_path = str(source_path)
        dependencies = dependencies or []

        dep_hashes = {
            str(dep): self._hash_file(dep)
            for dep in dependencies
        }

        self.cache[source_path] = {
            'hash': self._hash_file(source_path),
            'dependencies': dep_hashes,
            'built_at': datetime.now().isoformat()
        }

        self._save_cache()

# Usage
def incremental_build(document_paths):
    """Build only changed documents"""
    tracker = DependencyTracker()

    to_build = []
    for path in document_paths:
        # Get dependencies (images, templates)
        deps = get_document_dependencies(path)

        if tracker.needs_rebuild(path, deps):
            to_build.append(path)
        else:
            print(f"Skipping {path} (unchanged)")

    # Build changed documents
    if to_build:
        results = batch_convert_documents(to_build)

        # Update cache
        for path in to_build:
            deps = get_document_dependencies(path)
            tracker.mark_built(path, deps)
```

### 4.4 Error Handling and Rollback

```python
class BuildTransaction:
    """Atomic build operation with rollback support"""

    def __init__(self, document_id):
        self.document_id = document_id
        self.backup_dir = Path('.build_backup') / document_id
        self.changes = []

    def backup_file(self, path):
        """Backup file before modification"""
        if Path(path).exists():
            backup_path = self.backup_dir / Path(path).name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_path)
            self.changes.append(('modify', path, backup_path))
        else:
            self.changes.append(('create', path, None))

    def write_file(self, path, content):
        """Write file with backup"""
        self.backup_file(path)
        with open(path, 'w') as f:
            f.write(content)

    def rollback(self):
        """Rollback all changes"""
        for change_type, path, backup_path in reversed(self.changes):
            if change_type == 'modify':
                shutil.copy2(backup_path, path)
            elif change_type == 'create':
                Path(path).unlink(missing_ok=True)

    def commit(self):
        """Commit changes (delete backups)"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

# Usage
def safe_build(document_path):
    """Build with automatic rollback on error"""
    doc_id = Path(document_path).stem
    transaction = BuildTransaction(doc_id)

    try:
        # Perform build operations
        html_path = f'published/web/{doc_id}.html'
        pdf_path = f'published/pdf/{doc_id}.pdf'

        html_content = convert_markdown_to_html(document_path)
        transaction.write_file(html_path, html_content)

        pdf_content = generate_pdf_from_html(html_path)
        transaction.write_file(pdf_path, pdf_content)

        # Commit if successful
        transaction.commit()
        return True

    except Exception as e:
        # Rollback on error
        print(f"Build failed: {e}")
        transaction.rollback()
        return False
```

### 4.5 Progress Reporting and Logging

```python
import logging
from tqdm import tqdm

def setup_logging(log_dir='logs'):
    """Configure logging for batch processing"""
    Path(log_dir).mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(f'{log_dir}/build_{datetime.now():%Y%m%d_%H%M%S}.log'),
            logging.StreamHandler()
        ]
    )

def batch_build_with_progress(document_paths):
    """Build with progress bar"""
    setup_logging()

    results = {
        'success': [],
        'failed': []
    }

    with tqdm(total=len(document_paths), desc="Building documents") as pbar:
        for path in document_paths:
            pbar.set_description(f"Building {Path(path).name}")

            try:
                result = convert_single_document(path)
                results['success'].append(path)
                logging.info(f"✓ Built {path}")
            except Exception as e:
                results['failed'].append((path, str(e)))
                logging.error(f"✗ Failed {path}: {e}")

            pbar.update(1)

    # Summary
    logging.info(f"\nBuild complete: {len(results['success'])} succeeded, {len(results['failed'])} failed")

    return results
```

### 4.6 Build Orchestration Pattern (Makefile-style)

```python
# build.py
"""
Build orchestrator for SSP documents
"""
from pathlib import Path
import click

@click.group()
def cli():
    """SSP Document Build System"""
    pass

@cli.command()
@click.argument('document_id')
def build(document_id):
    """Build a single document"""
    md_path = Path('drafts') / f'{document_id}.md'

    if not md_path.exists():
        click.echo(f"Error: {md_path} not found", err=True)
        return 1

    click.echo(f"Building {document_id}...")

    if safe_build(md_path):
        click.echo(f"✓ {document_id} built successfully")
    else:
        click.echo(f"✗ {document_id} build failed", err=True)
        return 1

@cli.command()
@click.option('--category', type=click.Choice(['SOP', 'STD', 'REF', 'APP']))
@click.option('--incremental/--full', default=True)
def build_all(category, incremental):
    """Build all documents or category"""
    drafts = Path('drafts')

    if category:
        pattern = f'{category}-*.md'
    else:
        pattern = '*.md'

    documents = list(drafts.glob(pattern))

    click.echo(f"Found {len(documents)} documents")

    if incremental:
        tracker = DependencyTracker()
        documents = [
            d for d in documents
            if tracker.needs_rebuild(d, get_document_dependencies(d))
        ]
        click.echo(f"Building {len(documents)} changed documents")

    results = batch_build_with_progress(documents)

    if results['failed']:
        click.echo("\nFailed builds:", err=True)
        for path, error in results['failed']:
            click.echo(f"  • {Path(path).name}: {error}", err=True)
        return 1

@cli.command()
def clean():
    """Remove generated files"""
    for directory in ['published/pdf', 'published/web']:
        for file in Path(directory).glob('*'):
            file.unlink()
            click.echo(f"Removed {file}")

if __name__ == '__main__':
    cli()
```

**Usage:**

```bash
# Build single document
python build.py build SOP-001

# Build all changed documents (incremental)
python build.py build-all --incremental

# Build all SOPs (full rebuild)
python build.py build-all --category SOP --full

# Clean generated files
python build.py clean
```

---

## 5. Image Positioning & Manipulation

### 5.1 Pandoc Image Attributes

**Standard Pandoc Syntax:**

```markdown
![Caption text](path/to/image.png){width=70% #fig:id .class align=center}
```

**Attributes:**
- `width`, `height`: Dimensions (%, px, em)
- `#fig:id`: Identifier for cross-references
- `.class`: CSS classes
- Custom attributes: `align`, `scale`, `border`, `shadow`

### 5.2 CSS Positioning Strategies

**Float-based Layout:**

```css
.figure-left {
  float: left;
  margin: 0 1rem 1rem 0;
  max-width: 40%;
}

.figure-right {
  float: right;
  margin: 0 0 1rem 1rem;
  max-width: 40%;
}

.figure-center {
  display: block;
  margin-left: auto;
  margin-right: auto;
  max-width: 80%;
}
```

**Flexbox Layout:**

```css
figure {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 2rem 0;
}

figure img {
  max-width: 100%;
  height: auto;
}

figcaption {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  text-align: center;
}
```

**Grid Layout (for multi-image figures):**

```css
.figure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.figure-grid img {
  width: 100%;
  height: auto;
}
```

### 5.3 Directive Expansion: `<!-- ::FIGURE -->`

**Syntax:**

```markdown
<!-- ::FIGURE scale=0.7 align=center border shadow caption="Valve Assembly" -->
![Hydraulic valve](../../assets/images/doc/SOP-001/valve.png)
```

**Lua Filter Implementation:**

```lua
-- filters/figure_directive.lua

function Figure(elem)
  -- Check if previous element is HTML comment with FIGURE directive
  local directive = get_previous_comment()

  if directive and directive:match("::FIGURE") then
    -- Parse attributes
    local attrs = parse_directive_attributes(directive)

    -- Build HTML figure
    local html = string.format([[
      <figure class="figure-directive %s">
        <img src="%s" alt="%s" style="%s">
        <figcaption>%s</figcaption>
      </figure>
    ]],
      attrs.align or 'center',
      elem.src,
      elem.title or '',
      build_style_string(attrs),
      attrs.caption or elem.caption or ''
    )

    return pandoc.RawBlock('html', html)
  end

  return elem
end

function build_style_string(attrs)
  local styles = {}

  if attrs.scale then
    table.insert(styles, string.format("width: %s%%", attrs.scale * 100))
  end

  if attrs.border then
    table.insert(styles, "border: 1px solid #ccc")
  end

  if attrs.shadow then
    table.insert(styles, "box-shadow: 0 4px 6px rgba(0,0,0,0.1)")
  end

  return table.concat(styles, "; ")
end
```

**Generated HTML:**

```html
<figure class="figure-directive center">
  <img
    src="../../assets/images/doc/SOP-001/valve.png"
    alt="Hydraulic valve"
    style="width: 70%; border: 1px solid #ccc; box-shadow: 0 4px 6px rgba(0,0,0,0.1)">
  <figcaption>Valve Assembly</figcaption>
</figure>
```

### 5.4 Scribus Image Frame Manipulation

**Python Script (for PDF generation via Scribus):**

```python
import scribus

def insert_image_with_attributes(frame_name, image_path, attributes):
    """
    Insert image into Scribus frame with scaling and positioning

    Args:
        frame_name: Target frame name
        image_path: Path to image file
        attributes: Dict with scale, align, border, shadow
    """
    if not scribus.objectExists(frame_name):
        scribus.messageBox("Error", f"Frame '{frame_name}' not found")
        return

    # Load image
    scribus.loadImage(image_path, frame_name)

    # Scale image
    scale = attributes.get('scale', 1.0)
    scribus.setImageScale(scale * 100, scale * 100, frame_name)

    # Position (center in frame)
    scribus.setScaleImageToFrame(True, True, frame_name)

    # Apply border
    if attributes.get('border'):
        scribus.setLineWidth(1.0, frame_name)
        scribus.setLineColor("Black", frame_name)

    # Shadow effect (limited in Scribus; use external tool)
    if attributes.get('shadow'):
        # Note: Scribus has limited shadow support
        # Recommend pre-processing image with ImageMagick
        pass
```

### 5.5 Image Cropping, Borders, Shadows, Captions

**ImageMagick Pre-processing:**

```python
import subprocess

def apply_image_effects(input_path, output_path, effects):
    """
    Apply effects using ImageMagick

    Args:
        input_path: Source image
        output_path: Destination image
        effects: Dict with border, shadow, crop
    """
    cmd = ['convert', input_path]

    # Crop
    if 'crop' in effects:
        crop = effects['crop']  # e.g., "1000x800+100+50"
        cmd.extend(['-crop', crop])

    # Border
    if effects.get('border'):
        cmd.extend([
            '-bordercolor', 'black',
            '-border', '2x2'
        ])

    # Shadow
    if effects.get('shadow'):
        cmd.extend([
            '(',
            '+clone',
            '-background', 'black',
            '-shadow', '80x3+5+5',
            ')',
            '+swap',
            '-background', 'white',
            '-layers', 'merge',
            '+repage'
        ])

    cmd.append(output_path)

    subprocess.run(cmd, check=True)
```

**Pillow-based Effects (faster, pure Python):**

```python
from PIL import Image, ImageDraw, ImageFilter

def add_border(img, width=2, color='black'):
    """Add border to image"""
    bordered = Image.new(
        img.mode,
        (img.width + width*2, img.height + width*2),
        color
    )
    bordered.paste(img, (width, width))
    return bordered

def add_shadow(img, offset=(5, 5), blur=3, color='black'):
    """Add drop shadow to image"""
    # Create shadow layer
    shadow = Image.new('RGBA',
        (img.width + offset[0], img.height + offset[1]),
        (0, 0, 0, 0)
    )

    shadow_img = Image.new('RGBA', img.size, (0, 0, 0, 128))
    shadow.paste(shadow_img, offset)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))

    # Composite
    result = Image.new('RGBA', shadow.size, (255, 255, 255, 0))
    result.paste(shadow, (0, 0))
    result.paste(img, (0, 0), img if img.mode == 'RGBA' else None)

    return result
```

### 5.6 Automatic Image Sizing and Aspect Ratio

```python
def fit_image_to_constraints(img, max_width, max_height, maintain_aspect=True):
    """
    Resize image to fit within constraints

    Args:
        img: PIL Image object
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        maintain_aspect: Preserve aspect ratio

    Returns:
        Resized PIL Image
    """
    if maintain_aspect:
        # Calculate scaling factor
        width_ratio = max_width / img.width
        height_ratio = max_height / img.height
        scale = min(width_ratio, height_ratio)

        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
    else:
        new_width = max_width
        new_height = max_height

    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
```

### 5.7 Text Wrapping Around Images

**CSS Implementation:**

```css
/* Float image with text wrap */
.wrap-left {
  float: left;
  margin: 0 1.5rem 1rem 0;
  max-width: 40%;
  shape-outside: margin-box;
}

.wrap-right {
  float: right;
  margin: 0 0 1rem 1.5rem;
  max-width: 40%;
  shape-outside: margin-box;
}

/* Clear floats after wrapped content */
.clearfix::after {
  content: "";
  display: table;
  clear: both;
}
```

**HTML Structure:**

```html
<div class="clearfix">
  <img src="valve.png" alt="Valve" class="wrap-left">
  <p>This paragraph text will wrap around the image on the left.
     The image floats to the left side with text flowing around it.
     This creates a more natural, magazine-style layout.</p>
  <p>Additional paragraphs continue to wrap around the floated image
     until the clear is applied.</p>
</div>
```

---

## 6. Flexibility & Extensibility

### 6.1 Plugin Architecture Design

**Core Concept:** Hook-based plugin system

```python
# core/plugin_manager.py

class PluginManager:
    """Manage plugins and hooks"""

    def __init__(self):
        self.hooks = {}
        self.plugins = []

    def register_hook(self, hook_name):
        """Register a new hook point"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []

    def add_hook(self, hook_name, callback, priority=10):
        """Add callback to hook"""
        if hook_name not in self.hooks:
            self.register_hook(hook_name)

        self.hooks[hook_name].append({
            'callback': callback,
            'priority': priority
        })

        # Sort by priority (lower = earlier)
        self.hooks[hook_name].sort(key=lambda x: x['priority'])

    def run_hook(self, hook_name, *args, **kwargs):
        """Execute all callbacks for a hook"""
        if hook_name not in self.hooks:
            return args[0] if args else None

        result = args[0] if args else None

        for hook_data in self.hooks[hook_name]:
            callback = hook_data['callback']
            result = callback(result, *args[1:], **kwargs)

        return result

    def load_plugin(self, plugin_path):
        """Load plugin from file"""
        import importlib.util

        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)

        if hasattr(plugin, 'register'):
            plugin.register(self)
            self.plugins.append(plugin)

# Usage
pm = PluginManager()

# Register hooks
pm.register_hook('pre_conversion')
pm.register_hook('post_conversion')
pm.register_hook('validate_metadata')

# Add callbacks
pm.add_hook('pre_conversion', lambda md: md.upper())
pm.add_hook('post_conversion', lambda html: html + '<footer>Generated</footer>')

# Run hooks
result = pm.run_hook('pre_conversion', markdown_content)
```

**Plugin Example:**

```python
# plugins/custom_callouts.py
"""
Plugin to add custom callout types
"""

def transform_callouts(html, metadata):
    """Add custom callout rendering"""
    import re

    # Find custom callout: > [!CUSTOM] Text
    pattern = r'<blockquote>\[!CUSTOM\](.*?)</blockquote>'

    def replace_callout(match):
        content = match.group(1)
        return f'''
        <div class="callout callout-custom">
            <div class="callout-icon">⚙️</div>
            <div class="callout-content">{content}</div>
        </div>
        '''

    return re.sub(pattern, replace_callout, html, flags=re.DOTALL)

def register(plugin_manager):
    """Register plugin hooks"""
    plugin_manager.add_hook('post_conversion', transform_callouts, priority=20)
```

### 6.2 Configuration Management Strategy

**Hierarchical Configuration:**

```
config/
├── default.yaml           # System defaults
├── profiles/
│   ├── sop.yaml          # SOP-specific overrides
│   ├── std.yaml          # STD-specific overrides
│   └── custom.yaml       # User customizations
└── local.yaml            # Local machine overrides (gitignored)
```

**Configuration Schema:**

```yaml
# config/default.yaml

pipeline:
  pandoc:
    executable: /usr/bin/pandoc
    filters:
      - filters/callouts.lua
      - filters/wikilinks.lua
      - filters/directives.lua
    options:
      - --standalone
      - --toc
      - --toc-depth=3

  validation:
    schema: schemas/sop_metadata.json
    strict: true
    required_fields:
      - document_id
      - title
      - revision
      - status

  images:
    master_dir: assets/images/master
    print_dir: assets/images/print
    web_dir: assets/images/web
    formats:
      print:
        format: PNG
        dpi: 300
        optimize: true
      web:
        format: WEBP
        quality: 85
        sizes: [640, 1024, 1920]

  output:
    pdf:
      engine: weasyprint
      css: styles/pdf.css
      directory: published/pdf
    html:
      css: styles/web.css
      directory: published/web

  batch:
    max_workers: 4
    incremental: true
    cache_file: .build_cache.json
```

**Configuration Loader:**

```python
import yaml
from pathlib import Path

class Config:
    """Hierarchical configuration manager"""

    def __init__(self, config_dir='config'):
        self.config_dir = Path(config_dir)
        self.data = self._load_config()

    def _load_config(self):
        """Load and merge configuration files"""
        config = {}

        # Load in order (later files override earlier)
        files = [
            'default.yaml',
            f'profiles/{self.profile}.yaml',
            'local.yaml'
        ]

        for filename in files:
            path = self.config_dir / filename
            if path.exists():
                with open(path) as f:
                    data = yaml.safe_load(f)
                    config = self._deep_merge(config, data)

        return config

    def _deep_merge(self, base, override):
        """Recursively merge dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def get(self, path, default=None):
        """Get config value by dot-notation path"""
        keys = path.split('.')
        value = self.data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, path, value):
        """Set config value by dot-notation path"""
        keys = path.split('.')
        data = self.data

        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]

        data[keys[-1]] = value

# Usage
config = Config()
pandoc_exe = config.get('pipeline.pandoc.executable')
max_workers = config.get('pipeline.batch.max_workers', default=4)
```

### 6.3 Template System Design

**Jinja2 Templates:**

```
templates/
├── html/
│   ├── base.html.j2           # Base layout
│   ├── sop.html.j2            # SOP-specific layout
│   ├── components/
│   │   ├── header.html.j2     # Reusable header
│   │   ├── footer.html.j2     # Reusable footer
│   │   └── toc.html.j2        # Table of contents
│   └── partials/
│       ├── callout.html.j2    # Callout rendering
│       └── figure.html.j2     # Figure rendering
└── pdf/
    └── styles.css.j2          # PDF-specific CSS
```

**Base Template:**

```html
<!-- templates/html/base.html.j2 -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ metadata.document_id }} - {{ metadata.title }}</title>

  {% block styles %}
  <link rel="stylesheet" href="{{ config.get('output.html.css') }}">
  {% endblock %}
</head>
<body>
  {% include 'components/header.html.j2' %}

  <main id="content" role="main">
    {% block content %}{% endblock %}
  </main>

  {% include 'components/footer.html.j2' %}

  {% block scripts %}{% endblock %}
</body>
</html>
```

**SOP Template (extends base):**

```html
<!-- templates/html/sop.html.j2 -->
{% extends "base.html.j2" %}

{% block content %}
<article class="sop-document">
  <header class="document-header">
    <div class="metadata-grid">
      <div class="meta-item">
        <span class="meta-label">Document ID:</span>
        <span class="meta-value">{{ metadata.document_id }}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Revision:</span>
        <span class="meta-value">{{ metadata.revision }}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Status:</span>
        <span class="meta-value status-{{ metadata.status|lower }}">
          {{ metadata.status }}
        </span>
      </div>
    </div>

    <h1>{{ metadata.title }}</h1>
  </header>

  {% if toc %}
  {% include 'components/toc.html.j2' %}
  {% endif %}

  <div class="document-body">
    {{ content|safe }}
  </div>
</article>
{% endblock %}
```

**Template Renderer:**

```python
from jinja2 import Environment, FileSystemLoader

class TemplateRenderer:
    """Render HTML from templates"""

    def __init__(self, template_dir='templates/html'):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )

        # Register custom filters
        self.env.filters['markdown'] = self._markdown_filter
        self.env.filters['date_format'] = self._date_format

    def _markdown_filter(self, text):
        """Convert Markdown to HTML"""
        import markdown
        return markdown.markdown(text)

    def _date_format(self, date_str, format='%Y-%m-%d'):
        """Format date string"""
        from datetime import datetime
        dt = datetime.fromisoformat(date_str)
        return dt.strftime(format)

    def render(self, template_name, context):
        """Render template with context"""
        template = self.env.get_template(template_name)
        return template.render(**context)

# Usage
renderer = TemplateRenderer()
html = renderer.render('sop.html.j2', {
    'metadata': metadata,
    'content': body_html,
    'toc': toc_html,
    'config': config
})
```

### 6.4 Font Loading and Fallback Approach

**Font Stack Strategy:**

```css
/* System font stack (fast, no download) */
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI",
               Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-serif: Georgia, Cambria, "Times New Roman", Times, serif;
  --font-mono: "SF Mono", Monaco, "Cascadia Code", Consolas,
               "Liberation Mono", monospace;
}

/* Custom web fonts (with fallback) */
@font-face {
  font-family: 'DocumentFont';
  src: url('../fonts/DocumentFont-VF.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153;
}

body {
  font-family: 'DocumentFont', var(--font-sans);
}

code, pre {
  font-family: var(--font-mono);
}
```

**Font Loading API:**

```javascript
// Progressive font loading
if ('fonts' in document) {
  // Load custom font
  const font = new FontFace(
    'DocumentFont',
    'url(../fonts/DocumentFont-VF.woff2) format("woff2-variations")',
    { weight: '100 900' }
  );

  font.load().then(function(loadedFont) {
    document.fonts.add(loadedFont);
    document.body.classList.add('fonts-loaded');
  });
}
```

**PDF Font Embedding (WeasyPrint):**

```css
/* PDF-specific font embedding */
@font-face {
  font-family: 'PDFFont';
  src: url('../fonts/PDFFont.ttf') format('truetype');
  font-weight: normal;
}

@media print {
  body {
    font-family: 'PDFFont', serif;
  }
}
```

### 6.5 Unicode Normalization and Character Set Handling

```python
import unicodedata

def normalize_text(text, form='NFC'):
    """
    Normalize Unicode text

    Args:
        text: Input text
        form: Normalization form (NFC, NFD, NFKC, NFKD)

    Returns:
        Normalized text
    """
    return unicodedata.normalize(form, text)

def sanitize_filename(text):
    """
    Create safe filename from text
    """
    # Normalize Unicode
    text = normalize_text(text, 'NFKC')

    # Remove non-ASCII characters
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Replace spaces and special characters
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)

    return text.strip('-').lower()

def detect_encoding(file_path):
    """
    Detect file encoding
    """
    import chardet

    with open(file_path, 'rb') as f:
        raw = f.read()
        result = chardet.detect(raw)
        return result['encoding']

def ensure_utf8(text, source_encoding=None):
    """
    Ensure text is UTF-8 encoded
    """
    if isinstance(text, bytes):
        if source_encoding:
            text = text.decode(source_encoding)
        else:
            # Try common encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    text = text.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

    return text
```

### 6.6 Layout Engine Flexibility

**Abstract Layout Engine:**

```python
from abc import ABC, abstractmethod

class LayoutEngine(ABC):
    """Abstract base class for layout engines"""

    @abstractmethod
    def render_pdf(self, html_path, pdf_path, css_path=None):
        """Render HTML to PDF"""
        pass

    @abstractmethod
    def supports_feature(self, feature):
        """Check if engine supports feature"""
        pass

class WeasyPrintEngine(LayoutEngine):
    """WeasyPrint implementation"""

    def render_pdf(self, html_path, pdf_path, css_path=None):
        from weasyprint import HTML, CSS

        html = HTML(filename=html_path)

        if css_path:
            css = CSS(filename=css_path)
            html.write_pdf(pdf_path, stylesheets=[css])
        else:
            html.write_pdf(pdf_path)

    def supports_feature(self, feature):
        features = {
            'css_paged_media': True,
            'javascript': False,
            'svg': True,
            'page_breaks': True
        }
        return features.get(feature, False)

class PagedJSEngine(LayoutEngine):
    """Paged.js implementation"""

    def render_pdf(self, html_path, pdf_path, css_path=None):
        import subprocess

        cmd = [
            'pagedjs-cli',
            html_path,
            '-o', pdf_path
        ]

        if css_path:
            cmd.extend(['--css', css_path])

        subprocess.run(cmd, check=True)

    def supports_feature(self, feature):
        features = {
            'css_paged_media': True,
            'javascript': True,
            'svg': True,
            'page_breaks': True
        }
        return features.get(feature, False)

# Factory
def create_layout_engine(engine_type='weasyprint'):
    """Create layout engine instance"""
    engines = {
        'weasyprint': WeasyPrintEngine,
        'pagedjs': PagedJSEngine
    }

    if engine_type not in engines:
        raise ValueError(f"Unknown engine: {engine_type}")

    return engines[engine_type]()

# Usage
engine = create_layout_engine('weasyprint')
if engine.supports_feature('css_paged_media'):
    engine.render_pdf('input.html', 'output.pdf', 'styles.css')
```

---

## 7. Current Codebase Analysis

### 7.1 Reusable Components

Based on README analysis, current system has:

**Strong Foundation:**
- ✅ YAML front matter metadata system (standardized, well-documented)
- ✅ Folder structure (`drafts/`, `assets/`, `published/`, `releases/`)
- ✅ Layout profile concept (frame mapping, metadata population)
- ✅ Document state logic (Draft/Review/Active/Retired)
- ✅ Release packaging approach (timestamped zips with full context)

**Reusable Patterns:**

```python
# Metadata parsing (from YAML front matter)
def parse_yaml_metadata(markdown_path):
    """Extract YAML front matter from Markdown"""
    with open(markdown_path) as f:
        content = f.read()
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            yaml_text = content[3:yaml_end]
            return yaml.safe_load(yaml_text)
    return {}

# Document state resolution
def resolve_document_state(metadata):
    """Determine output paths based on status"""
    status = metadata.get('status', 'Draft')
    doc_id = metadata['document_id']
    revision = metadata['revision']

    if status == 'Active':
        pdf_dir = 'published/pdf'
        release = True
    elif status == 'Review':
        pdf_dir = 'published/pdf'
        release = False
    else:  # Draft
        pdf_dir = 'drafts/pdf'
        release = False

    return {
        'pdf_path': f"{pdf_dir}/{doc_id}_r{revision}.pdf",
        'release': release
    }

# Metadata list joining (upstream_apn, downstream_apn)
def prepare_meta(metadata):
    """Process metadata for display"""
    meta = metadata.copy()

    # Join list fields with commas
    for field in ['upstream_apn', 'downstream_apn']:
        if field in meta and isinstance(meta[field], list):
            meta[f"{field}_joined"] = ', '.join(meta[field])

    return meta
```

### 7.2 Integration Points for New Features

**Web Output Generation:**

```python
# New module: converters/web_generator.py

def generate_web_output(markdown_path, output_dir='published/web'):
    """
    Generate HTML from Markdown (integrates with existing pipeline)

    Integration points:
    - Uses existing parse_yaml_metadata()
    - Uses existing resolve_document_state()
    - Respects existing folder structure
    """
    # Parse metadata (existing function)
    metadata = parse_yaml_metadata(markdown_path)

    # Validate (new feature)
    is_valid, errors = validate_metadata(markdown_path, 'schemas/sop_metadata.json')
    if not is_valid:
        raise ValueError(f"Validation failed: {errors}")

    # Convert Markdown → HTML (new)
    html = convert_markdown_to_html(markdown_path)

    # Resolve output path (existing pattern)
    state = resolve_document_state(metadata)
    html_path = state['pdf_path'].replace('.pdf', '.html').replace('pdf', 'web')

    # Write output
    with open(html_path, 'w') as f:
        f.write(html)

    return html_path
```

**Metadata Validation:**

```python
# New module: validators/metadata_validator.py

def validate_pipeline_input(markdown_path):
    """
    Pre-pipeline validation (integrates at start of existing pipeline)

    Integration point: Call before any conversion
    """
    # Validate metadata schema
    is_valid, errors = validate_metadata(markdown_path, 'schemas/sop_metadata.json')

    if not is_valid:
        log_error(f"Metadata validation failed for {markdown_path}:\n" + "\n".join(errors))
        return False

    # Validate cross-references (if document registry exists)
    if Path('document_registry.json').exists():
        with open('document_registry.json') as f:
            registry = json.load(f)

        metadata = parse_yaml_metadata(markdown_path)
        is_valid, errors = validate_cross_references(metadata, registry)

        if not is_valid:
            log_error(f"Cross-reference validation failed:\n" + "\n".join(errors))
            return False

    return True
```

**Image Pipeline:**

```python
# New module: processors/image_processor.py

def process_document_images(document_id, assets_dir='assets/images'):
    """
    Generate image variants (integrates with existing asset structure)

    Integration points:
    - Respects existing assets/images/ structure
    - Generates print/ and web/ variants
    - Creates metadata JSON in assets/xml/metadata/
    """
    master_dir = Path(assets_dir) / 'master' / 'doc' / document_id

    if not master_dir.exists():
        return {}

    registry = {}

    for img_path in master_dir.glob('*.png'):
        variants = generate_image_variants(str(img_path), assets_dir, document_id)
        registry[f"{document_id}_{img_path.stem}"] = variants

    # Save registry (existing pattern: assets/xml/metadata/)
    registry_path = Path(assets_dir) / 'xml' / 'metadata' / f'{document_id}_images.json'
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)

    return registry
```

### 7.3 Technical Debt to Address

**From README analysis:**

1. **DocBook XML loses Markdown semantics**
   - Callouts (`> [!WARNING]`) → stripped or plain blockquotes
   - Wikilinks (`[[REF-2201]]`) → lost entirely
   - **Fix:** Replace DocBook intermediate with Pandoc JSON AST + Lua filters

2. **Scribus rendering is slow and brittle**
   - 10-15 seconds per document
   - Complex overflow handling
   - Limited Python API
   - **Fix:** Replace with WeasyPrint (2-3 seconds, better typography)

3. **No automated testing**
   - **Fix:** Add pytest-based test suite
   - Unit tests for metadata validation
   - Integration tests for conversion pipeline
   - End-to-end tests for full workflow

4. **Manual image optimization**
   - **Fix:** Automated variant generation (implemented above)

5. **No version control for .sla templates**
   - Binary format, difficult to diff
   - **Fix:** Extract layout specification to JSON (layout_map.yaml pattern)

### 7.4 Migration Considerations

**Phased Migration Approach:**

**Phase 1: Add validation and image processing (non-breaking)**
- Implement metadata validation (runs before existing pipeline)
- Implement image variant generation (separate script)
- Test in parallel with existing workflow

**Phase 2: Add web output (parallel path)**
- Implement Markdown → HTML conversion
- Keep existing Scribus PDF path
- Validate HTML output quality

**Phase 3: Replace Scribus with WeasyPrint (breaking change)**
- Implement HTML → PDF via WeasyPrint
- Migrate one document family (e.g., STD) first
- Compare output quality with Scribus
- Once validated, migrate remaining families

**Phase 4: Add batch processing**
- Implement dependency tracking
- Implement parallel builds
- Create build orchestrator

**Backward Compatibility:**

```python
# Migration shim: support both old and new pipelines

def convert_document(markdown_path, engine='weasyprint'):
    """
    Convert document with engine selection

    Args:
        engine: 'weasyprint' (new) or 'scribus' (legacy)
    """
    if engine == 'scribus':
        # Legacy path (preserve existing behavior)
        return convert_via_scribus(markdown_path)
    else:
        # New path
        return convert_via_weasyprint(markdown_path)
```

---

## 8. Recommendations Summary

### 8.1 Prioritized Feature List

**High Priority (implement first):**

1. **Metadata Validation** (quick win, prevents errors)
   - Library: jsonschema
   - Schema: schemas/sop_metadata.json
   - Integration: Pre-pipeline validation

2. **Image Variant Generation** (addresses manual optimization pain)
   - Tool: Pillow (Pillow-SIMD for production)
   - Outputs: Print (300 DPI PNG) + Web (WebP multi-res)
   - Integration: Separate script, run before build

3. **Web Output (HTML)** (new capability, high value)
   - Tech: Pandoc JSON AST + Lua filters + Jinja2
   - Responsive: Tailwind CSS
   - Integration: Parallel path to existing PDF

**Medium Priority (add after core features stable):**

4. **Replace Scribus with WeasyPrint** (performance, maintainability)
   - Migration: Phased, one family at a time
   - Benefit: 10-15x speed improvement, better typography

5. **Batch Processing** (efficiency at scale)
   - Strategy: Multiprocessing + dependency tracking
   - Tool: Custom build orchestrator (Click CLI)

6. **Plugin System** (extensibility)
   - Architecture: Hook-based
   - Use cases: Custom callouts, directives, validators

**Low Priority (future enhancements):**

7. **AVIF Image Format** (cutting-edge compression)
   - Browser support: 94% (2025)
   - Benefit: 20-25% smaller than WebP

8. **Paged.js Support** (advanced interactive features)
   - Use case: Documents requiring JavaScript

### 8.2 Technology Choices with Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Metadata Validation** | jsonschema | Most actively maintained, format-agnostic, industry standard |
| **Image Processing** | Pillow / Pillow-SIMD | Pure Python, 15-40x faster than ImageMagick |
| **Web Image Format** | WebP | 97% browser support, 30% smaller than JPEG, fast decoding |
| **PDF Rendering** | WeasyPrint | Better CSS Paged Media support, 10-15x faster than Scribus |
| **HTML Templates** | Jinja2 | Industry standard, powerful, maintainable |
| **CSS Framework** | Tailwind CSS | Utility-first, rapid iteration, excellent print support |
| **Batch Processing** | multiprocessing + asyncio | Hybrid approach for CPU + I/O bound tasks |
| **Font Format** | WOFF2 | 97% browser support, 30-50% smaller, variable fonts |
| **Unicode Handling** | NFC normalization | Standard for text processing, compatible with all systems |

### 8.3 Architecture Patterns to Adopt

**1. Pipeline Pattern (linear transformation chain):**

```
Input → Validate → Transform → Render → Output
```

**2. Plugin Architecture (extensibility):**

```
Core Pipeline + Hooks → Plugins extend functionality
```

**3. Dependency Injection (testability):**

```python
# Good: Inject dependencies
def convert_document(markdown_path, validator, renderer):
    ...

# Bad: Hard-coded dependencies
def convert_document(markdown_path):
    validator = MetadataValidator()  # hard-coded
    ...
```

**4. Factory Pattern (layout engine selection):**

```python
engine = create_layout_engine('weasyprint')
engine.render_pdf(html_path, pdf_path)
```

**5. Template Method (standardize workflow):**

```python
class DocumentConverter(ABC):
    def convert(self, path):
        self.validate()
        self.parse()
        self.transform()
        self.render()

    @abstractmethod
    def parse(self):
        pass
```

### 8.4 Quick Wins vs Long-Term Investments

**Quick Wins (< 1 week each):**

1. ✅ Metadata validation with jsonschema
   - Immediate error prevention
   - Low complexity
   - High value

2. ✅ Image variant generation script
   - Eliminates manual work
   - Reusable for all documents
   - Moderate complexity

3. ✅ Basic web HTML output
   - New capability
   - Uses existing Pandoc
   - Moderate complexity

**Long-Term Investments (> 2 weeks each):**

1. ⏳ Replace Scribus with WeasyPrint
   - Major refactor
   - Requires extensive testing
   - High long-term value (speed, maintainability)

2. ⏳ Batch processing with dependency tracking
   - Complex implementation
   - Requires robust error handling
   - High value at scale (dozens+ documents)

3. ⏳ Plugin architecture
   - Design complexity
   - Ongoing maintenance
   - Enables future customization

**Recommended Approach:**

1. **Month 1:** Quick wins (validation, images, basic HTML)
2. **Month 2:** Web output refinement (CSS, responsive, accessibility)
3. **Month 3:** WeasyPrint migration (pilot with one document family)
4. **Month 4+:** Batch processing, plugin system

---

## 9. Open Questions

### 9.1 Unresolved Technical Decisions

1. **WeasyPrint vs Paged.js for PDF generation:**
   - WeasyPrint: No JavaScript, better CSS Paged Media
   - Paged.js: JavaScript support, less complete CSS
   - **Question:** Are interactive features (JavaScript) required for any SOPs?
   - **Recommendation:** Start with WeasyPrint; add Paged.js if needed

2. **WebP vs AVIF for web images:**
   - WebP: 97% browser support, faster decoding
   - AVIF: 94% support, 20-25% smaller files
   - **Question:** Is 3% browser compatibility worth 20% file size?
   - **Recommendation:** WebP primary, AVIF optional for future

3. **Build cache strategy:**
   - Content hashing (accurate, slower)
   - Timestamp-based (fast, less accurate)
   - **Question:** Acceptable false positive rate for rebuilds?
   - **Recommendation:** Content hashing (SHA256) for production accuracy

4. **Incremental vs full builds:**
   - Incremental: Faster for single-doc changes
   - Full: Ensures consistency, catches cross-reference issues
   - **Question:** How often should full rebuilds run?
   - **Recommendation:** Incremental for dev, full for release

### 9.2 Areas Needing Clarification

1. **Scribus template migration:**
   - Current templates are binary .sla files
   - **Question:** Extract layout to CSS or keep visual editor?
   - **Option A:** Extract to CSS (version-controllable, but lose GUI)
   - **Option B:** Keep Scribus for layout design, export to CSS
   - **Recommendation:** Option B (design in Scribus, export layout spec)

2. **Document registry:**
   - Cross-reference validation requires knowing all document IDs
   - **Question:** Where is master document registry maintained?
   - **Options:**
     - A) Auto-generate from drafts/ directory
     - B) Maintain separate registry.json
   - **Recommendation:** Auto-generate on build (source of truth: drafts/)

3. **Revision workflow:**
   - **Question:** Should revision increment be automatic or manual?
   - **Automatic:** Less error-prone, but removes control
   - **Manual:** More control, but error-prone
   - **Recommendation:** Automatic increment with override flag

4. **Image optimization trade-offs:**
   - **Question:** Optimize for file size or quality?
   - **Print:** Quality-first (300 DPI, lossless PNG)
   - **Web:** Balance (WebP quality=85)
   - **Recommendation:** Separate profiles for print vs web

### 9.3 Trade-offs Requiring User Input

1. **PDF generation speed vs visual control:**
   - Scribus: Slow (10-15s), full visual control
   - WeasyPrint: Fast (2-3s), CSS-based (less WYSIWYG)
   - **Question:** Is 5x speed worth losing visual editor?

2. **Web accessibility vs development time:**
   - Full WCAG 2.2 compliance: More development time
   - Basic accessibility: Faster, but less compliant
   - **Question:** Target compliance level? (A, AA, AAA)
   - **Recommendation:** AA (legal requirement in many jurisdictions)

3. **Batch processing parallelism:**
   - More workers: Faster builds, higher CPU usage
   - Fewer workers: Slower builds, lower resource usage
   - **Question:** Default worker count? (CPU count, CPU count/2, fixed number)
   - **Recommendation:** CPU count with config override

4. **Template flexibility vs simplicity:**
   - More templates: Greater flexibility, harder to maintain
   - Fewer templates: Simpler, less customization
   - **Question:** How many templates per document family?
   - **Recommendation:** One per family (SOP, STD, REF, APP) with overrides

---

## References and Sources

### Pandoc and Filters
- [Pandoc Filters](https://pandoc.org/filters.html)
- [Pandoc Lua Filters](https://pandoc.org/lua-filters.html)
- [Pandoc User's Guide](https://pandoc.org/MANUAL.html)
- [Lua filters for Pandoc](https://ojitha.github.io/lua/2025/02/28/Lua-pandoc-filter-for-inex-references.html)

### Python YAML Validation
- [Validating a yaml document in python - Stack Overflow](https://stackoverflow.com/questions/3262569/validating-a-yaml-document-in-python)
- [pykwalify Documentation](https://pykwalify.readthedocs.io/)
- [Schema Validation for YAML | JSON Schema Everywhere](https://json-schema-everywhere.github.io/yaml)

### Image Optimization
- [Pillow Performance](https://python-pillow.github.io/pillow-perf/)
- [Comparing Python Pillow and ImageMagick](https://soffipillows.com/comparing-python-pillow-and-imagemagick-a-comprehensive-guide/)
- [Python libraries to compress & resize images fast](https://uploadcare.com/blog/image-optimization-python/)
- [The fastest production-ready image resize](https://uploadcare.com/blog/the-fastest-image-resize/)

### CSS Paged Media and PDF Rendering
- [CSS Paged Media Module & Specifications](https://docraptor.com/css-paged-media)
- [print-css.rocks](https://print-css.rocks/)
- [WeasyPrint Features](https://doc.courtbouillon.org/weasyprint/v0.42.3/features.html)
- [Paged.js GitHub](https://github.com/pagedjs/pagedjs)
- [Paged Media approaches](https://www.pagedmedia.org/paged-media-approaches-part-1-of-2.html)

### CSS Frameworks
- [Tailwind CSS](https://tailwindcss.com/)
- [The ultimate guide to CSS frameworks in 2025](https://www.contentful.com/blog/css-frameworks/)
- [Top 7 CSS Frameworks for Developers in 2025](https://www.browserstack.com/guide/top-css-frameworks)

### Web Fonts and Typography
- [WOFF 2.0 Browser Support](https://caniuse.com/woff2)
- [Mastering WOFF2: The Future of Web Fonts](https://www.numberanalytics.com/blog/mastering-woff2-the-future-of-web-fonts/)
- [Web fonts - MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Text_styling/Web_fonts)
- [Browser Compatibility for Variable Fonts](https://www.browserstack.com/guide/browser-compatibility-for-variable-fonts)

### Responsive Images
- [Responsive Images: Best Practices in 2025](https://dev.to/razbakov/responsive-images-best-practices-in-2025-4dlb)
- [Using responsive images in HTML - MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images)
- [Responsive Images Done Right - Smashing Magazine](https://www.smashingmagazine.com/2014/05/responsive-images-done-right-guide-picture-srcset/)
- [Responsive images | web.dev](https://web.dev/learn/design/responsive-images)

### Accessibility
- [ARIA - Accessibility | MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
- [ARIA Labels for Web Accessibility: Complete 2025 Implementation Guide](https://www.allaccessible.org/blog/implementing-aria-labels-for-web-accessibility)
- [WAI-ARIA Overview](https://www.w3.org/WAI/standards-guidelines/aria/)
- [Accessible Rich Internet Applications (WAI-ARIA) 1.3](https://w3c.github.io/aria/)

### Image Formats
- [Modern Image Formats: WebP vs AVIF](https://www.rumvision.com/blog/modern-image-formats-webp-avif-browser-support/)
- [AVIF vs WebP: Which Image Format Reigns Supreme in 2025?](https://elementor.com/blog/webp-vs-avif/)
- [AVIF vs. WebP: Speed, Quality, and Browser Support](https://crystallize.com/blog/avif-vs-webp)
- [WebP vs AVIF - Which is better in 2025?](https://speedvitals.com/blog/webp-vs-avif/)

### Python Concurrency
- [multiprocessing vs multithreading vs asyncio - Stack Overflow](https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio)
- [Speed Up Your Python Program With Concurrency](https://realpython.com/python-concurrency/)
- [Combining Multiprocessing and Asyncio in Python](https://www.dataleadsfuture.com/combining-multiprocessing-and-asyncio-in-python-for-performance-boosts/)
- [How to use asyncio with multiprocessing in Python](https://sorokin.engineer/posts/en/python_asyncio_multiprocessing.html)

---

**Document End**

*This research document provides comprehensive requirements for implementing a robust SSP document automation pipeline. Use it as input for architectural planning and implementation.*
