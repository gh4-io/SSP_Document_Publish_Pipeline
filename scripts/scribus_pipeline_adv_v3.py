# scribus_pipeline_adv_v2.py
# Advanced Scribus pipeline driven by layout profile JSON.
#
# Key responsibilities:
# - Read Markdown front matter (YAML) for metadata and pipeline_profile
# - Load DocBook XML and build a simple block model (headings + paragraphs)
# - Load a layout profile JSON (templates/profiles/layout_profile_<profile>.json)
# - Inject metadata into Scribus frames based on frame roles/meta_keys
# - Flow body text into the first body frame
# - Handle overflow by:
#     * Linking the first body frame to the page‑2 continuation frame
#     * Creating additional continuation pages/frames as long as overflow exists
# - Export a PDF using the profile’s output naming convention
#
# This script is intended to be run from inside Scribus:
#   Script → Execute Script… → select this file.
#
# For now, it expects that:
#   - The correct Scribus template (.sla) is already open.
#   - The Markdown and DocBook paths are configured in main().
#
# The script is deliberately written to be:
#   - Profile‑driven (no hard‑coded frame names)
#   - Layout‑profile aware (JSON instead of layout_map.yaml)
#   - Safer and more robust in overflow handling than the previous version.

import sys
import os
import datetime
import traceback
import xml.etree.ElementTree as ET
import re
import json

try:
    import scribus  # type: ignore
except ImportError:  # pragma: no cover (Scribus only)
    scribus = None  # allows basic import/testing outside Scribus


# ─────────────────────────────────────────────────────────────
# LOGGING + DIALOG HELPERS
# ─────────────────────────────────────────────────────────────

def log(msg, log_file=None):
    """Append a timestamped line to the log file and print to console."""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{timestamp}] {msg}"
    try:
        print(line)
    except Exception:
        pass
    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass


def error_dialog(msg):
    """Show an error in Scribus if possible, otherwise print."""
    if scribus is not None and getattr(scribus, "haveDoc", None) and scribus.haveDoc():
        scribus.messageBox("SOP Pipeline – Error", msg, scribus.ICON_WARNING, scribus.BUTTON_OK)
    else:
        print("ERROR:", msg)


# ─────────────────────────────────────────────────────────────
# MARKDOWN METADATA (YAML FRONT MATTER)
# ─────────────────────────────────────────────────────────────

def load_markdown_metadata(md_path):
    """
    Extract YAML front matter from a Markdown file and return as a dict.
    Only 'document_id' and 'title' are truly required; everything else is optional.
    """
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Front matter between --- ... --- at top of file
    m = re.match(r"^---\s*\n(.*?\n)---\s*\n", text, re.DOTALL)
    if not m:
        return {}

    yaml_text = m.group(1)
    meta = {}
    current_key = None

    # Ultra‑simple YAML subset parser (key: value, lists, basic scalars)
    for line in yaml_text.splitlines():
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z0-9_\-]+:\s*", line):
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val == "" or val == "|" or val == ">":
                current_key = key
                meta[current_key] = ""
            else:
                current_key = key
                meta[current_key] = val
        elif line.lstrip().startswith("- ") and current_key:
            # list item
            item = line.lstrip()[2:].strip()
            existing = meta.get(current_key)
            if not isinstance(existing, list):
                existing = [] if existing in (None, "") else [existing]
            existing.append(item)
            meta[current_key] = existing
        else:
            # continuation of a multi‑line value
            if current_key is not None:
                existing = meta.get(current_key, "")
                if isinstance(existing, list):
                    # append to last element
                    if existing:
                        existing[-1] = (existing[-1] + "\n" + line).rstrip()
                    else:
                        existing.append(line)
                else:
                    meta[current_key] = (existing + "\n" + line).rstrip()

    return meta


def prepare_meta(raw_meta):
    """
    Normalize metadata keys and expand helper fields.
    """
    meta = dict(raw_meta or {})

    # Lower‑case normalized copy for easier access
    normalized = {}
    for key, value in list(meta.items()):
        new_key = key.strip()
        normalized[new_key] = value
    for k, v in normalized.items():
        meta.setdefault(k, v)

    # Normalize doc_id/document_id
    if "document_id" not in meta and "doc_id" in meta:
        meta["document_id"] = meta["doc_id"]
    if "title" not in meta:
        meta["title"] = ""

    # pipeline_profile can be string or list
    profiles = meta.get("pipeline_profile")
    if isinstance(profiles, list):
        meta["pipeline_profile_joined"] = ", ".join(str(p) for p in profiles)
        meta["pipeline_profile_active"] = profiles[0] if profiles else ""
    elif isinstance(profiles, str):
        meta["pipeline_profile_joined"] = profiles
        meta["pipeline_profile_active"] = profiles
    else:
        meta["pipeline_profile_joined"] = ""
        meta["pipeline_profile_active"] = ""

    # Generic flattening for any list fields
    for key, value in list(meta.items()):
        if isinstance(value, list):
            joined_key = f"{key}_joined"
            meta[joined_key] = ", ".join(str(v) for v in value)

    return meta


# ─────────────────────────────────────────────────────────────
# DOCBOOK LOADING + BLOCK BUILDING
# ─────────────────────────────────────────────────────────────

def load_docbook(docbook_path):
    if not os.path.exists(docbook_path):
        raise FileNotFoundError(f"DocBook XML not found: {docbook_path}")
    tree = ET.parse(docbook_path)
    return tree.getroot()

def get_full_text(elem):
    """
    Return all text content from an element, with internal whitespace
    normalized so that Scribus doesn't see hard line breaks from the
    pretty-printed DocBook.

    - Collapses runs of whitespace (spaces, tabs, newlines) into a single space.
    - Trims leading and trailing whitespace.
    """
    if elem is None:
        return ""
    # Collect all text nodes
    parts = []
    for t in elem.itertext():
        if t is not None:
            parts.append(t)
    raw = "".join(parts)
    # Normalize any whitespace sequences (including newlines) to a single space
    normalized = re.sub(r"\s+", " ", raw)
    return normalized.strip()



def build_blocks(root):
    """
    Build an ordered list of content blocks from DocBook.

    Blocks:
    - 'heading' blocks with a level (1..6)
    - 'paragraph' blocks with text

    This implementation:
    - Treats the document title as H1 (if present).
    - Walks sections in document order, respecting nesting for heading levels.
    - Captures preface paragraphs before the first section.
    - Captures direct paragraphs under each section.
    - Captures itemized and ordered list items as paragraphs, with bullet/number prefixes.
    - Walks through blockquotes instead of skipping them.
    - Falls back to top-level paragraphs/lists if no sections exist.
    """
    # Namespace detection
    ns = {"db": root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    blocks = []

    def add_heading(text: str, level: int) -> None:
        if not text:
            return
        lvl = max(1, min(int(level), 6))
        blocks.append({"type": "heading", "level": lvl, "text": text})

    def add_paragraph(text: str) -> None:
        if not text:
            return
        blocks.append({"type": "paragraph", "text": text})

    def tag_local(el):
        if '}' in el.tag:
            return el.tag.split('}', 1)[1]
        return el.tag

    # 1) Document title as H1 (if present in <article><info><title> etc.)
    title_el = root.find("db:title", ns)
    if title_el is not None:
        text = get_full_text(title_el).strip()
        if text:
            add_heading(text, 1)

    # Helper to render lists as paragraphs
    def handle_list(list_el, kind: str, indent_level: int = 0):
        """
        kind: 'bullet' or 'numbered'
        indent_level: nesting depth (0 = top-level, 1 = nested, etc.)
        """
        indent = "  " * indent_level
        counter = 1

        for li in list_el.findall("db:listitem", ns):
            for child in list(li):
                local = tag_local(child)

                if local == "para":
                    text = get_full_text(child).strip()
                    if not text:
                        continue
                    if kind == "bullet":
                        prefix = "• "
                    else:
                        prefix = f"{counter}. "
                    add_paragraph(f"{indent}{prefix}{text}")
                    if kind == "numbered":
                        counter += 1

                elif local == "itemizedlist":
                    handle_list(child, kind="bullet", indent_level=indent_level + 1)

                elif local == "orderedlist":
                    handle_list(child, kind="numbered", indent_level=indent_level + 1)

                elif local == "blockquote":
                    # Allow nested blockquotes inside list items
                    process_block_node(child, indent_level=indent_level)

    def process_block_node(node, indent_level: int = 0):
        """
        Generic block-level handler. Deals with:
        - para
        - itemizedlist / orderedlist
        - blockquote (recursively)
        """
        local = tag_local(node)

        if local == "para":
            text = get_full_text(node).strip()
            if text:
                add_paragraph(text)
            return

        if local == "itemizedlist":
            handle_list(node, kind="bullet", indent_level=indent_level)
            return

        if local == "orderedlist":
            handle_list(node, kind="numbered", indent_level=indent_level)
            return

        if local == "blockquote":
            # Walk children of the blockquote in order
            for child in list(node):
                process_block_node(child, indent_level=indent_level)
            return

        # Other container-like elements could be added here later (admonitions, etc.)

    # 2) Handle preface content before the first <section> (e.g., intro lists/paras)
    children = list(root)
    for child in children:
        local = tag_local(child)
        if local == "section":
            break  # stop at the first section; remaining content handled by section walker

        # Skip <info> etc.
        if local in ("info", "title"):
            continue

        process_block_node(child, indent_level=0)

    # 3) Walk a section, preserving heading hierarchy and content order
    def walk_section(section_el, base_level: int = 2):
        # Section title (direct child <title>)
        sec_title = section_el.find("db:title", ns)
        if sec_title is not None:
            text = get_full_text(sec_title).strip()
            if text:
                add_heading(text, base_level)

        # Walk direct children in document order
        for child in list(section_el):
            local = tag_local(child)

            if local == "title":
                continue  # already handled

            if local == "section":
                # Nested section => deeper heading level
                walk_section(child, base_level + 1)
                continue

            # All other block-level content is handled generically
            process_block_node(child, indent_level=0)

    # 4) Walk all top-level sections under the root
    top_sections = root.findall("db:section", ns)
    for sec in top_sections:
        walk_section(sec, base_level=2)

    # 5) Fallback: if there were no sections at all, capture top-level blocks
    if not blocks:
        for child in list(root):
            process_block_node(child, indent_level=0)

    return blocks





# ─────────────────────────────────────────────────────────────
# LAYOUT PROFILE LOADING
# ─────────────────────────────────────────────────────────────

def load_layout_profile(profile_path):
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Layout profile not found: {profile_path}")
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    lp = data.get("layout_profile") or {}
    return lp


def safe_format(template, meta):
    """Format a string with {placeholders} using meta, ignoring missing keys."""
    class SafeDict(dict):
        def __missing__(self, key):
            return ""
    try:
        return template.format_map(SafeDict(meta))
    except Exception:
        return template

def resolve_document_state(meta, layout_profile):
    """
    Resolve the normalized document state ('active', 'draft', 'retired')
    using layout_profile.document_state and the document metadata.
    """
    ds = (layout_profile.get("document_state") or {}) if layout_profile else {}
    meta_key = ds.get("meta_key") or "status"
    treat_missing_as = (ds.get("treat_missing_as") or "draft").lower()

    raw_value = str(meta.get(meta_key, "")).strip() if meta else ""
    if not raw_value:
        state = treat_missing_as
    else:
        raw_lower = raw_value.lower()
        def in_list(key):
            for v in ds.get(key, []):
                try:
                    if raw_lower == str(v).lower():
                        return True
                except Exception:
                    continue
            return False

        if in_list("active_values"):
            state = "active"
        elif in_list("draft_values"):
            state = "draft"
        elif in_list("retired_values"):
            state = "retired"
        else:
            state = treat_missing_as

    # Store normalized status back into meta for downstream use
    if meta is not None:
        meta["status_normalized"] = state
    return state


def should_emit_output(mode, doc_state):
    """
    Decide whether a given output should be produced based on its mode
    and the normalized document state.

    mode:
      - 'DISABLED'    -> never
      - 'ACTIVE_ONLY' -> only when doc_state == 'active'
      - 'ALWAYS'      -> always
    """
    if mode is None:
        mode = "DISABLED"
    mode_upper = str(mode).upper()
    if mode_upper == "DISABLED":
        return False
    if mode_upper == "ACTIVE_ONLY":
        return doc_state == "active"
    # Default / 'ALWAYS'
    return True



# ─────────────────────────────────────────────────────────────
# METADATA → FRAMES
# ─────────────────────────────────────────────────────────────

def apply_metadata_to_frames(layout_profile, raw_meta, log_file=None):
    """
    Use the layout_profile.layout.pages[].frames to inject metadata.

    For each frame:
    - role == 'title' → use meta['title'] or value pattern
    - role == 'meta'  → use meta_key + value pattern
    """
    meta = prepare_meta(raw_meta)

    layout = layout_profile.get("layout", {})
    pages = layout.get("pages", [])
    if not pages:
        log("No pages defined in layout_profile.layout.pages.", log_file)
        return

    for page_cfg in pages:
        frames = page_cfg.get("frames", [])
        for f_cfg in frames:
            role = f_cfg.get("role")
            frame_name = f_cfg.get("name")
            if not frame_name or not scribus.objectExists(frame_name):
                continue

            if role == "title":
                # Prefer explicit value pattern, otherwise use {title}
                tmpl = f_cfg.get("value") or "{title}"
                text = safe_format(tmpl, meta).strip()
                if text:
                    scribus.setText(text, frame_name)
                    log(f"Set title frame {frame_name}: {text}", log_file)

            elif role == "meta":
                meta_key = f_cfg.get("meta_key", "")
                if not meta_key:
                    continue
                tmpl = f_cfg.get("value") or "{" + meta_key + "}"
                text = safe_format(tmpl, meta).strip()
                if text:
                    scribus.setText(text, frame_name)
                    log(f"Set meta frame {frame_name} ({meta_key}): {text}", log_file)


# ─────────────────────────────────────────────────────────────
# BODY FLOW
# ─────────────────────────────────────────────────────────────

def flow_blocks_into_body(layout_profile, blocks, body_frame_name, log_file=None):
    """
    Flow headings + paragraphs into the FIRST body frame.
    Paragraph styles are resolved via layout_profile.styles_map.docbook.
    Overflow continuation is handled separately by handle_overflow().
    """
    if not scribus.objectExists(body_frame_name):
        log(f"Body frame {body_frame_name} not found in the open Scribus document.", log_file)
        error_dialog(f"Body frame '{body_frame_name}' not found in the open Scribus document. Check that the frame name matches the layout profile.")
        return

    # Resolve style mappings
    styles_map = (layout_profile.get("styles_map") or {}).get("docbook", {})
    heading_styles = styles_map.get("heading", {})  # e.g. {"1": "Heading1", "2": "Heading2"}
    default_heading_style = styles_map.get("heading_default") or heading_styles.get("2") or "Heading2"
    para_style = styles_map.get("paragraph") or "BodyText"

    scribus.selectObject(body_frame_name)
    scribus.setText("", body_frame_name)

    for block in blocks:
        if block.get("type") == "heading":
            level = str(block.get("level", 1))
            style = heading_styles.get(level, default_heading_style)
            text = block.get("text", "").rstrip() + "\n"
        elif block.get("type") == "paragraph":
            style = para_style
            text = block.get("text", "").rstrip() + "\n\n"
        else:
            continue

        if not text.strip():
            continue

        pos = scribus.getTextLength(body_frame_name)
        scribus.insertText(text, -1, body_frame_name)
        length = len(text)
        try:
            scribus.selectText(pos, length, body_frame_name)
            scribus.setParagraphStyle(style, body_frame_name)
        except Exception:
            # If style not found or out of range, just continue
            log(f"Warning: failed to set style {style} on frame {body_frame_name}", log_file)

    # Initial layout
    scribus.layoutText(body_frame_name)


# ─────────────────────────────────────────────────────────────
# OVERFLOW HANDLING
# ─────────────────────────────────────────────────────────────

def handle_overflow(layout_profile, body_frame_name, log_file=None):
    """
    Handle overflow by:
    - Finding the page‑2 body continuation frame from layout_profile.layout.pages
    - Linking body_frame_name → continuation seed
    - Repeatedly creating new pages using the continuation master and
      cloning the continuation frame geometry while text still overflows.
    """
    if not scribus.objectExists(body_frame_name):
        log(f"Body frame {body_frame_name} not found; cannot handle overflow.", log_file)
        return

    layout = layout_profile.get("layout", {})
    pages = layout.get("pages", [])
    if len(pages) < 2:
        log("Layout profile does not define a page 2 for continuation.", log_file)
        return

    # Page 2 config: find the body frame used as the continuation seed
    page2_cfg = pages[1]
    cont_frame_name = None
    for f_cfg in page2_cfg.get("frames", []):
        if f_cfg.get("role") == "body":
            cont_frame_name = f_cfg.get("name")
            break

    if not cont_frame_name or not scribus.objectExists(cont_frame_name):
        log(f"Continuation frame '{cont_frame_name}' not found on page 2.", log_file)
        return

    # Determine continuation master page
    masters = (layout_profile.get("scribus") or {}).get("masters", {})
    cont_master = masters.get("continuation_pages") or None

    # Capture geometry from the seed continuation frame
    x, y = scribus.getPosition(cont_frame_name)
    w, h = scribus.getSize(cont_frame_name)

    # Link first → continuation seed if not already linked
    try:
        scribus.linkTextFrames(body_frame_name, cont_frame_name)
        log(f"Linked body frame '{body_frame_name}' → '{cont_frame_name}'", log_file)
    except Exception:
        # It's OK if they are already linked
        log(f"Body frame '{body_frame_name}' may already be linked to '{cont_frame_name}'", log_file)

    # Layout once before checking overflow
    scribus.layoutText(body_frame_name)

    # Track the last frame in the chain
    last_frame = cont_frame_name
    safety_limit = 100  # prevent infinite loops
    n = 0

    while n < safety_limit:
        n += 1
        over_tail = scribus.textOverflows(last_frame)
        over_head = scribus.textOverflows(body_frame_name)
        log(f"Overflow check #{n}: head={over_head}, tail={over_tail}", log_file)

        if not over_tail and not over_head:
            break

        # Add a new continuation page at the end
        page_count = scribus.pageCount()
        new_page = page_count + 1
        if cont_master:
            scribus.newPage(new_page, cont_master)
        else:
            scribus.newPage(new_page)
            if cont_master:
                scribus.applyMasterPage(cont_master, new_page)

        scribus.gotoPage(new_page)
        new_frame = scribus.createText(x, y, w, h)
        log(f"Created continuation frame '{new_frame}' on page {new_page}", log_file)

        try:
            scribus.linkTextFrames(last_frame, new_frame)
        except Exception as e:
            log(f"Failed to link frames '{last_frame}' → '{new_frame}': {e}", log_file)
            break

        last_frame = new_frame
        scribus.layoutText(body_frame_name)

    if n >= safety_limit:
        log("Safety limit hit; overflow loop aborted.", log_file)

    log("Overflow handling complete.", log_file)


# ─────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────────────────────

def main():
    """
    Basic end‑to‑end run.

    Current assumptions:
    - The correct Scribus template (.sla) is already open.
    - Markdown + DocBook file paths are hard‑coded below (SOP‑200 example).
    - Layout profile is resolved from metadata.pipeline_profile_active with
      a default of 'sop_default' and loaded from templates/profiles/.
    """
    if scribus is None:
        print("This script must be run inside Scribus.")
        return

    if not scribus.haveDoc():
        error_dialog("Open the correct DTS Scribus template (.sla) before running this script.")
        return

    # Base directory: assume this file is in /scripts/, so base is one level up
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Example SOP‑200 paths (adjust as needed)
    md_path = os.path.join(base_dir, "drafts", "SOP-200_Create_Workackage_Sequencing_Type.md")
    docbook_path = os.path.join(base_dir, "drafts", "SOP-200_Create_Workackage_Sequencing_Type.docbook.xml")

    # Layout profile directory
    profile_dir = os.path.join(base_dir, "templates", "profiles")

    # Load metadata (Markdown front matter)
    try:
        raw_meta = load_markdown_metadata(md_path)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed to load Markdown metadata: {e}")
        # No log file has been resolved yet; best effort to print to console
        print(tb)
        return

    meta = prepare_meta(raw_meta)

    # At this point we do not yet know the layout profile. Logging and outputs
    # will be configured *after* the profile is loaded and the document state is known.
    # Resolve pipeline profile → layout profile
    # Primary profile comes from metadata (pipeline_profile_active); fall back to 'sop_default'.
    pipeline_profile = meta.get("pipeline_profile_active") or "sop_default"
    profile_filename = f"layout_profile_{pipeline_profile}.json"
    profile_path = os.path.join(profile_dir, profile_filename)

    # Attempt to load requested profile; if it fails AND is not the default, fall back to 'sop_default'.
    # NOTE: Logging is not yet fully configured; errors here are reported via dialog and console.
    try:
        layout_profile = load_layout_profile(profile_path)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Requested layout profile '{pipeline_profile}' failed to load from {profile_path}: {e}")
        if pipeline_profile != "sop_default":
            # Fallback to default SOP layout profile
            pipeline_profile = "sop_default"
            profile_filename = f"layout_profile_{pipeline_profile}.json"
            profile_path = os.path.join(profile_dir, profile_filename)
            try:
                layout_profile = load_layout_profile(profile_path)
            except Exception as e2:
                tb2 = traceback.format_exc()
                error_dialog(f"Failed to load fallback layout profile 'sop_default': {e2}")
                print(tb2)
                return
        else:
            error_dialog(f"Failed to load layout profile '{pipeline_profile}': {e}")
            print(tb)
            return

    # Resolve normalized document state (active/draft/retired) from metadata + profile rules
    doc_state = resolve_document_state(meta, layout_profile)

    # Configure logging based on layout_profile.logging and document state
    logging_cfg = layout_profile.get("logging") or {}
    logging_enabled = logging_cfg.get("enabled", False)
    logging_only_active = logging_cfg.get("only_when_active", False)

    log_file = None
    external_log_path = None

    if logging_enabled and (not logging_only_active or doc_state == "active"):
        internal_cfg = logging_cfg.get("internal") or {}
        internal_enabled = internal_cfg.get("enabled", False)
        if internal_enabled:
            internal_dir = internal_cfg.get("directory", "logs")
            logs_dir = os.path.join(base_dir, internal_dir)
            os.makedirs(logs_dir, exist_ok=True)
            internal_pattern = internal_cfg.get("pattern", "{document_id}_pipeline.log")
            log_filename = safe_format(internal_pattern, meta) or "pipeline.log"
            log_file = os.path.join(logs_dir, log_filename)

        external_cfg = logging_cfg.get("external") or {}
        external_enabled = external_cfg.get("enabled", False)
        external_only_active = external_cfg.get("only_when_active", False)
        if external_enabled and (not external_only_active or doc_state == "active"):
            ext_dir = external_cfg.get("directory", "releases/{family}/_logs")
            # family defaults to document_category if not explicitly provided
            if "family" not in meta:
                meta["family"] = layout_profile.get("document_category") or "SOP"
            ext_dir_resolved = safe_format(ext_dir, meta)
            external_dir = os.path.join(base_dir, ext_dir_resolved)
            os.makedirs(external_dir, exist_ok=True)
            ext_pattern = external_cfg.get("pattern", "{document_id}_r{revision}_{pipeline_profile}_{timestamp_utc}.log")
            # Add a basic UTC timestamp token if not present in meta yet
            if "timestamp_utc" not in meta:
                meta["timestamp_utc"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
            external_log_filename = safe_format(ext_pattern, meta) or "external.log"
            external_log_path = os.path.join(external_dir, external_log_filename)

    # At this point, log_file may be None (logging disabled or inactive-doc policy)
    log("Starting advanced pipeline run (layout-profile driven).", log_file)

    # Load DocBook blocks
    # Load DocBook blocks
    try:
        root = load_docbook(docbook_path)
        blocks = build_blocks(root)
        log(f"DocBook parsing produced {len(blocks)} content blocks.", log_file)
        if not blocks:
            error_dialog("DocBook was parsed but produced no blocks. Check the DocBook structure and styles_map.")
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed to parse DocBook: {e}")
        log(f"DocBook parse error: {tb}", log_file)
        return

    # Apply metadata to frames
    try:
        apply_metadata_to_frames(layout_profile, meta, log_file=log_file)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed to apply metadata to frames: {e}")
        log(f"Metadata → frame error: {tb}", log_file)
        return

    # Find first‑page body frame from layout_profile (page == 1, role == 'body')
    layout = layout_profile.get("layout", {})
    pages = layout.get("pages", [])
    body_frame_name = None
    for page_cfg in pages:
        if page_cfg.get("page") != 1:
            continue
        for f_cfg in page_cfg.get("frames", []):
            if f_cfg.get("role") == "body":
                body_frame_name = f_cfg.get("name")
                break
        if body_frame_name:
            break

    if not body_frame_name:
        error_dialog("No body frame (role='body') defined for page 1 in layout profile.")
        log("No page‑1 body frame in layout profile.", log_file)
        return

    # Flow content into the first body frame (page 1)
    try:
        flow_blocks_into_body(layout_profile, blocks, body_frame_name, log_file=log_file)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed to flow blocks into body frame: {e}")
        log(f"Body flow error: {tb}", log_file)
        return

    # Handle multi‑page overflow using page‑2 continuation geometry
    try:
        handle_overflow(layout_profile, body_frame_name, log_file=log_file)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed during overflow handling: {e}")
        log(f"Overflow handling error: {tb}", log_file)
        return

    # Determine PDF output configuration from layout_profile.outputs (preferred)
    outputs_cfg = layout_profile.get("outputs") or {}
    pdf_cfg = outputs_cfg.get("pdf") or {}

    # Determine directory for PDF output
    pdf_target_dir = pdf_cfg.get("target_directory")
    if not pdf_target_dir:
        # Fallback to legacy resources.pdf_directory or default published/pdf
        resources_cfg = layout_profile.get("resources") or {}
        pdf_target_dir = resources_cfg.get("pdf_directory") or os.path.join("published", "pdf")

    pdf_dir = os.path.join(base_dir, pdf_target_dir) if not os.path.isabs(pdf_target_dir) else pdf_target_dir
    os.makedirs(pdf_dir, exist_ok=True)

    # Determine PDF filename pattern
    pdf_pattern = pdf_cfg.get("filename_pattern")
    if not pdf_pattern:
        # Fallback to legacy output_naming.pdf_pattern or a safe default
        output_naming = layout_profile.get("output_naming", {})
        pdf_pattern = output_naming.get("pdf_pattern") or "{document_id}_r{revision}.pdf"

    pdf_name = safe_format(pdf_pattern, meta) or "output.pdf"
    output_pdf = os.path.join(pdf_dir, pdf_name)

    # Decide whether PDF should be emitted based on output mode and document state
    pdf_mode = pdf_cfg.get("mode", "DISABLED")
    if not should_emit_output(pdf_mode, doc_state):
        log(f"PDF output suppressed (mode='{pdf_mode}', doc_state='{doc_state}').", log_file)
        output_pdf = None
    else:
        # Export PDF
        try:
            pdf = scribus.PDFfile()
            pdf.file = output_pdf
            pdf.save()
            log(f"PDF exported to {output_pdf}", log_file)
        except Exception as e:
            tb = traceback.format_exc()
            error_dialog(f"Failed to export PDF: {e}")
            log(f"PDF export error: {tb}", log_file)

    # If external logging is enabled, copy internal log file to the configured external path
    if log_file and external_log_path:
        try:
            import shutil
            shutil.copyfile(log_file, external_log_path)
            log(f"External log written to {external_log_path}", log_file)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Failed to write external log: {e}")
            log(f"External log copy error: {tb}", log_file)

    log("Advanced layout‑profile pipeline run completed.", log_file)
    scribus.messageBox(
        "Pipeline",
        "Advanced layout‑profile pipeline run completed.",
        scribus.ICON_NONE,
       scribus.BUTTON_OK
    )


if __name__ == "__main__":
    main()
