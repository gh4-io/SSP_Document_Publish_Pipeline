# scribus_pipeline_advanced.py
# Basic Scribus pipeline for SOP-200, with:
# - layout_map.yaml metadata mapping
# - improved DocBook parsing (inline + lists)
# - overflow handling (BodyTextMP -> BodyTextCONT -> extra pages)
#
# No JSON, no fileDialog, no argv.
# Run from within Scribus via Script -> Execute Script…

import sys
import os
import datetime
import traceback
import xml.etree.ElementTree as ET
import re  # for YAML front matter parsing

try:
    import scribus
except ImportError:
    print("This script must be run from within Scribus.")
    sys.exit(1)

try:
    import yaml  # PyYAML
except ImportError:
    scribus.messageBox(
        "Error",
        "PyYAML (yaml) module not found. Install it for layout_map.yaml support.",
        scribus.ICON_WARNING,
        scribus.BUTTON_OK
    )
    yaml = None


# Paragraph styles we expect in the template
REQUIRED_STYLES = ["BodyText", "Heading1", "Heading2"]


def log(msg, log_file=None):
    ts = datetime.datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass


def error_dialog(msg):
    if scribus.haveDoc():
        scribus.messageBox("SOP Pipeline – Error", msg, scribus.ICON_WARNING, scribus.BUTTON_OK)
    else:
        print("ERROR:", msg)


# ─────────────────────────────────────────────────────────────
# TEMPLATE VALIDATION (styles only; frames via layout_map)
# ─────────────────────────────────────────────────────────────

def validate_template_styles(log_file=None):
    """
    Ensure required paragraph styles exist.
    We don't hard-code frame names; those come from layout_map.yaml.
    """
    ok = True
    styles = scribus.getParagraphStyles()
    for req in REQUIRED_STYLES:
        if req not in styles:
            log(f"Missing paragraph style: {req}", log_file)
            ok = False
    return ok


# ─────────────────────────────────────────────────────────────
# DOCBOOK PARSING (for body content)
# ─────────────────────────────────────────────────────────────

def get_full_text(elem):
    """
    Recursively collect all text from an element, including inline children
    and their tails. This avoids losing text around <emphasis>, <link>, etc.
    """
    parts = []

    if elem.text:
        parts.append(elem.text)

    for child in elem:
        parts.append(get_full_text(child))
        if child.tail:
            parts.append(child.tail)

    return "".join(parts)


def load_docbook(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return root


def build_blocks(root):
    """
    Build a list of blocks (heading/para) from DocBook.
    - H1: document title
    - H2: section titles
    - para: any <para> inside sections (including in lists)
    """
    ns = {"db": root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    blocks = []

    # Top-level title as H1
    title_el = root.find("db:title", ns)
    if title_el is not None:
        text = get_full_text(title_el).strip()
        if text:
            blocks.append({"type": "heading", "level": 1, "text": text})

    # Sections as H2 + paras (including list paras)
    for sec in root.findall(".//db:section", ns):
        sec_title = sec.find("db:title", ns)
        if sec_title is not None:
            t = get_full_text(sec_title).strip()
            if t:
                blocks.append({"type": "heading", "level": 2, "text": t})

        # Any para inside this section, at any depth
        for para in sec.findall(".//db:para", ns):
            t = get_full_text(para).strip()
            if t:
                blocks.append({"type": "para", "text": t})

    return blocks


# ─────────────────────────────────────────────────────────────
# MARKDOWN METADATA (YAML front matter)
# ─────────────────────────────────────────────────────────────

def load_markdown_metadata(md_path):
    """
    Extract YAML front matter from a Markdown file and return as dict.
    Only 'document_id' and 'title' are truly required; everything else is optional.
    """
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Front matter between --- ... --- at top of file
    m = re.match(r"^---\s*\n(.*?\n)---\s*\n", text, re.DOTALL)
    if not m:
        # No front matter; return minimal dict
        return {}

    front_matter = m.group(1)

    if yaml is None:
        # Can't parse YAML if module missing
        return {}

    meta = yaml.safe_load(front_matter) or {}
    if not isinstance(meta, dict):
        meta = {}

    return meta


class SafeDict(dict):
    def __missing__(self, key):
        # Missing placeholders become blank
        return ""


def safe_format(expr, meta):
    return expr.format_map(SafeDict(meta))


def prepare_meta(raw_meta):
    """
    Normalize metadata:
    - handle dashed keys (downstream-apn -> downstream_apn)
    - ensure document_id/title keys exist (if possible)
    - flatten list values into <key>_joined
    - handle pipeline_profile as string or list
    """
    meta = dict(raw_meta or {})

    # Normalize dashed keys: downstream-apn -> downstream_apn
    normalized = {}
    for key, value in list(meta.items()):
        new_key = key.replace("-", "_")
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
# LAYOUT MAP (frames + role mapping)
# ─────────────────────────────────────────────────────────────

def load_layout_map(layout_map_path):
    if yaml is None:
        raise RuntimeError("yaml module not available; cannot load layout_map.yaml")

    if not os.path.exists(layout_map_path):
        raise FileNotFoundError(f"layout_map.yaml not found at: {layout_map_path}")

    with open(layout_map_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def apply_meta_to_frames(layout_map, raw_meta, log_file=None):
    """
    Uses sop_to_layout_map/pages/roles in layout_map.yaml to:
    - fill title frames (TitleMP, TitleCONT, etc.)
    - fill meta frames (DocIdMP, APNMP, etc.)
    NOTE: We do NOT call scribus.gotoPage(); we rely on frame names.
    """
    meta = prepare_meta(raw_meta)

    pages = layout_map.get("sop_to_layout_map", {}).get("pages", [])
    if not pages:
        log("No pages defined in sop_to_layout_map.", log_file)
        return

    for page_cfg in pages:
        roles = page_cfg.get("roles", {})

        # Title role
        title_cfg = roles.get("title")
        if title_cfg:
            frame_name = title_cfg.get("frame")
            value_expr = title_cfg.get("value", "{title}")
            text = safe_format(value_expr, meta).strip()
            if frame_name and scribus.objectExists(frame_name):
                scribus.setText(text, frame_name)
                log(f"Set title in frame {frame_name}: {text}", log_file)

        # Meta fields: one frame per field
        meta_cfg = roles.get("meta", {})
        fields = meta_cfg.get("fields", {})
        for key, field_cfg in fields.items():
            frame_name = field_cfg.get("frame")
            value_expr = field_cfg.get("value", "{" + key + "}")
            text = safe_format(value_expr, meta).strip()

            if not frame_name or not scribus.objectExists(frame_name):
                continue

            if text == "":
                # Leave as-is if metadata is missing
                continue

            scribus.setText(text, frame_name)
            log(f"Set meta {key} in frame {frame_name}: {text}", log_file)


# ─────────────────────────────────────────────────────────────
# BODY FLOW + OVERFLOW
# ─────────────────────────────────────────────────────────────

def flow_blocks_into_body(blocks, body_frame_name, log_file=None):
    """
    Flow headings + paragraphs into the FIRST body frame.
    Overflow to continuation frames/pages is handled separately
    by handle_overflow().
    """
    if not scribus.objectExists(body_frame_name):
        log(f"Body frame {body_frame_name} not found.", log_file)
        return

    scribus.selectObject(body_frame_name)
    scribus.setText("", body_frame_name)

    for block in blocks:
        if block["type"] == "heading":
            style = "Heading1" if block.get("level", 1) == 1 else "Heading2"
            pos = scribus.getTextLength(body_frame_name)
            text = block["text"] + "\n"
            scribus.insertText(text, -1, body_frame_name)
            scribus.selectText(pos, len(block["text"]), body_frame_name)
            scribus.setParagraphStyle(style, body_frame_name)
        elif block["type"] == "para":
            pos = scribus.getTextLength(body_frame_name)
            text = block["text"] + "\n\n"
            scribus.insertText(text, -1, body_frame_name)
            scribus.selectText(pos, len(block["text"]), body_frame_name)
            scribus.setParagraphStyle("BodyText", body_frame_name)

    log(f"Body text flowed into frame {body_frame_name}.", log_file)


def handle_overflow(layout_map, body_frame_name, log_file=None):
    """
    Handle multi-page overflow using the continuation body frame defined
    on page 2 in layout_map.yaml (e.g., BodyTextCONT).

    Algorithm:
    - Find the continuation frame name for page 2 from layout_map.
    - Link BodyTextMP -> BodyTextCONT.
    - Use BodyTextCONT's geometry as the pattern for all additional pages.
    - While the *head* of the chain (body_frame_name) still overflows:
        - Append a new page.
        - Create a new text frame at the same position/size.
        - Link previous last frame -> new frame.
        - Re-layout the chain.
    """

    pages_cfg = layout_map.get("sop_to_layout_map", {}).get("pages", [])
    if len(pages_cfg) < 2:
        log("No second page configuration in layout_map; overflow handling skipped.", log_file)
        return

    # Get continuation frame mapping from the second page definition
    second_page_roles = pages_cfg[1].get("roles", {})
    body_role = second_page_roles.get("body")
    if not isinstance(body_role, dict):
        log("Second page has no 'body' role in layout_map; overflow handling skipped.", log_file)
        return

    cont_frame_name = body_role.get("frame")
    if not cont_frame_name or not scribus.objectExists(cont_frame_name):
        log(f"Continuation frame '{cont_frame_name}' not found in document; overflow handling skipped.", log_file)
        return

    # Link the main body frame to the continuation frame on page 2 (once)
    try:
        scribus.linkTextFrames(body_frame_name, cont_frame_name)
        log(f"Linked body chain: {body_frame_name} → {cont_frame_name}", log_file)
    except Exception as e:
        log(f"Failed to link {body_frame_name} to {cont_frame_name}: {e}", log_file)
        return

    # Use the continuation frame geometry as the template for all further frames
    x, y = scribus.getPosition(cont_frame_name)
    w, h = scribus.getSize(cont_frame_name)
    last_frame = cont_frame_name

    # Initial layout so we get a correct overflow status
    scribus.layoutText(body_frame_name)

    # IMPORTANT:
    # Check overflow on the *head* of the chain (body_frame_name),
    # not on the last frame.
    safety_counter = 0
    max_pages = 50  # hard safety to avoid infinite loops

    while scribus.textOverflows(body_frame_name):
        safety_counter += 1
        if safety_counter > max_pages:
            log("Overflow loop aborted: reached max_pages safety limit.", log_file)
            break

        # Append a new page at the end
        try:
            new_page = scribus.newPage(-1)   # typical API: -1 = append at end
        except TypeError:
            # Older Scribus APIs sometimes don't return a value; fallback:
            new_page = scribus.pageCount()

        scribus.gotoPage(new_page)

        # Create a new continuation frame on this new page
        new_frame_name = scribus.createText(x, y, w, h)
        log(f"Created continuation frame '{new_frame_name}' on page {new_page}", log_file)

        # Link the previous last frame to the new frame in the chain
        scribus.linkTextFrames(last_frame, new_frame_name)
        last_frame = new_frame_name

        # Re-layout the entire chain starting from the first frame
        scribus.layoutText(body_frame_name)

    log("Overflow handling complete; all text fits into the frame chain or safety limit reached.", log_file)




# ─────────────────────────────────────────────────────────────
# MAIN: hardcoded SOP-200 test pipeline
# ─────────────────────────────────────────────────────────────

def main():
    """
    Basic end-to-end run for SOP-200, no JSON, no dialogs.
    """
    if not scribus.haveDoc():
        error_dialog("Open the DTS template (.sla) before running this script.")
        return

    # Base directory: assume this file is in /scripts/, so base is one level up
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Hard-coded SOP-200 paths (adjust filenames if needed)
    md_path = os.path.join(base_dir, "drafts", "SOP-200_Create_Workackage_Sequencing_Type.md")
    docbook_path = os.path.join(base_dir, "drafts", "SOP-200_Create_Workackage_Sequencing_Type.docbook.xml")
    layout_map_path = os.path.join(base_dir, "scripts", "layout_map.yaml")

    logs_dir = os.path.join(base_dir, "logs")
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir)
        except Exception:
            pass

    log_file = os.path.join(logs_dir, "SOP-200_basic_overflow.log")

    pdf_dir = os.path.join(base_dir, "published", "pdf")
    if not os.path.exists(pdf_dir):
        try:
            os.makedirs(pdf_dir)
        except Exception:
            pass

    output_pdf = os.path.join(pdf_dir, "SOP-200_basic_overflow.pdf")

    log("Starting basic SOP-200 pipeline run (with overflow).", log_file)

    if not validate_template_styles(log_file):
        error_dialog("Template validation failed (missing paragraph styles). See log for details.")
        return

    # Load metadata
    try:
        raw_meta = load_markdown_metadata(md_path)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed to load Markdown metadata: {e}")
        log(f"Markdown metadata error: {tb}", log_file)
        return

    # Load layout map
    try:
        layout_map = load_layout_map(layout_map_path)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed to load layout_map.yaml: {e}")
        log(f"layout_map load error: {tb}", log_file)
        return

    # Apply metadata to frames
    apply_meta_to_frames(layout_map, raw_meta, log_file=log_file)

    # Load DocBook + build blocks
    if not os.path.exists(docbook_path):
        error_dialog(f"DocBook XML not found: {docbook_path}")
        log("DocBook XML missing.", log_file)
        return

    try:
        root = load_docbook(docbook_path)
        blocks = build_blocks(root)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed to parse DocBook: {e}")
        log(f"DocBook parse error: {tb}", log_file)
        return

    # Pick body frame from first page of layout_map
    body_frame_name = None
    pages = layout_map.get("sop_to_layout_map", {}).get("pages", [])
    if pages:
        first_page_cfg = pages[0]
        roles = first_page_cfg.get("roles", {})
        body_role = roles.get("body")
        if isinstance(body_role, dict):
            body_frame_name = body_role.get("frame")

    if not body_frame_name:
        error_dialog("No body frame mapping found for page 1 in layout_map.yaml.")
        log("No body frame mapping for page 1.", log_file)
        return

    # Flow content into the first body frame (page 1)
    flow_blocks_into_body(blocks, body_frame_name, log_file=log_file)

    # Handle multi-page overflow using page-2 continuation geometry
    handle_overflow(layout_map, body_frame_name, log_file=log_file)

    # Export PDF using the hard-coded output_pdf path
    pdf_path = output_pdf
    if pdf_path:
        pdf = scribus.PDFfile()
        pdf.file = pdf_path
        try:
            pdf.save()
            log(f"PDF exported to {pdf_path}", log_file)
        except Exception as e:
            tb = traceback.format_exc()
            error_dialog("Failed to export PDF: %s" % e)
            log("PDF export error: %s" % tb, log_file)

    log("Basic SOP-200 pipeline run (with overflow) completed.", log_file)
    scribus.messageBox(
        "Pipeline",
        "Basic SOP-200 pipeline (with overflow) completed.",
        scribus.ICON_NONE,
        scribus.BUTTON_OK
    )



    log("Basic SOP-200 pipeline run (with overflow) completed.", log_file)
    scribus.messageBox("Pipeline", "Basic SOP-200 pipeline (with overflow) completed.", scribus.ICON_NONE, scribus.BUTTON_OK)


if __name__ == "__main__":
    main()
