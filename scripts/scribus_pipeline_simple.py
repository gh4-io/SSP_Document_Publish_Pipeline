# scribus_pipeline_advanced.py
# Advanced Scribus pipeline: template validation, DocBook parsing, metadata mapping via layout_map.yaml.
#
# Typical job JSON:
# {
#   "markdown_source": "drafts/SOP-200_Create_Workackage_Sequencing_Type.md",
#   "source_docbook": "drafts/SOP-200_Create_Workackage_Sequencing_Type.docbook.xml",
#   "layout_map": "scripts/layout_map.yaml",
#   "log_file": "logs/SOP-200.log",
#   "output_pdf": "published/pdf/SOP-200.pdf"
# }
#
# Run from within Scribus.

import sys
import os
import json
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


# These are now *generic* requirements.
# We no longer assume HeaderFrame/FooterFrame; we rely on layout_map.yaml.
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
    We don't hard-code frame names anymore; those come from layout_map.yaml.
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

def load_docbook(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return root


def build_blocks(root):
    """
    Build a list of blocks (heading/para) from DocBook.
    Extend later for tables/lists.
    """
    ns = {"db": root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    blocks = []

    # Top-level title as H1
    title_el = root.find("db:title", ns)
    if title_el is not None and title_el.text:
        blocks.append({"type": "heading", "level": 1, "text": title_el.text.strip()})

    # Sections as H2 + paras
    for sec in root.findall(".//db:section", ns):
        sec_title = sec.find("db:title", ns)
        if sec_title is not None and sec_title.text:
            blocks.append({"type": "heading", "level": 2, "text": sec_title.text.strip()})
        for para in sec.findall("db:para", ns):
            if para.text:
                blocks.append({"type": "para", "text": para.text.strip()})

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
    - ensure document_id/title keys exist (if possible)
    - flatten list values into <key>_joined
    - handle pipeline_profile as string or list
    """
    meta = dict(raw_meta or {})

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
    """
    meta = prepare_meta(raw_meta)

    pages = layout_map.get("sop_to_layout_map", {}).get("pages", [])
    if not pages:
        log("No pages defined in sop_to_layout_map.", log_file)
        return

    for page_cfg in pages:
        page_number = page_cfg.get("page")
        if page_number:
            try:
                scribus.gotoPage(page_number)
            except Exception:
                # Ignore if page doesn't exist yet
                continue

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
                # Leave as-is or clear; here we leave it unchanged
                continue

            scribus.setText(text, frame_name)
            log(f"Set meta {key} in frame {frame_name}: {text}", log_file)


# ─────────────────────────────────────────────────────────────
# BODY FLOW (page 1 only for now)
# ─────────────────────────────────────────────────────────────

def flow_blocks_into_body(blocks, body_frame_name, log_file=None):
    """
    Simple version: flow headings + paragraphs into a single body frame.
    Later we can extend this to handle continuation frames and dynamic pages.
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


# ─────────────────────────────────────────────────────────────
# TEST HOOK (metadata only, SOP-200-specific)
# ─────────────────────────────────────────────────────────────

def run_sop_meta_test():
    """
    Helper you can call from Scribus to test metadata mapping only.
    Assumes:
    - scripts/.. = pipeline root
    - drafts/SOP-200_Create_Workackage_Sequencing_Type.md
    - scripts/layout_map.yaml
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # scripts/.. = pipeline root

    md_path = os.path.join(base_dir, "drafts", "SOP-200_Create_Workackage_Sequencing_Type.md")
    layout_map_path = os.path.join(base_dir, "scripts", "layout_map.yaml")

    if not scribus.haveDoc():
        error_dialog("Open the DTS template (.sla) before running run_sop_meta_test().")
        return

    try:
        meta = load_markdown_metadata(md_path)
    except Exception as e:
        error_dialog(f"Failed to load Markdown metadata: {e}")
        return

    try:
        layout_map = load_layout_map(layout_map_path)
    except Exception as e:
        error_dialog(f"Failed to load layout_map.yaml: {e}")
        return

    apply_meta_to_frames(layout_map, meta)
    scribus.messageBox("Pipeline", "Metadata applied for SOP-200.", scribus.ICON_NONE, scribus.BUTTON_OK)


# ─────────────────────────────────────────────────────────────
# MAIN PIPELINE (job JSON-driven)
# ─────────────────────────────────────────────────────────────

def main():
    # Get job JSON path from Scribus argument or file dialog.
    if len(sys.argv) > 1:
        job_path = sys.argv[1]
    else:
        job_path = scribus.fileDialog("Select job JSON", "JSON (*.json)", "", "", False)

    if not job_path:
        return

    if not os.path.isfile(job_path):
        error_dialog("Job JSON not found: %s" % job_path)
        return

    with open(job_path, "r", encoding="utf-8") as f:
        job = json.load(f)

    log_file = job.get("log_file")
    log("Job loaded: %s" % job_path, log_file)

    # Required: DocBook source for body.
    docbook_path = job.get("source_docbook")
    if not docbook_path or not os.path.isfile(docbook_path):
        error_dialog("DocBook XML not found: %s" % docbook_path)
        log("DocBook XML missing.", log_file)
        return

    # Optional: Markdown source for metadata.
    md_path = job.get("markdown_source")

    # Layout map path.
    layout_map_path = job.get("layout_map")
    if not layout_map_path:
        # Default to scripts/layout_map.yaml relative to this script.
        base_dir = os.path.dirname(os.path.dirname(__file__))
        layout_map_path = os.path.join(base_dir, "scripts", "layout_map.yaml")

    if not scribus.haveDoc():
        error_dialog("Open the appropriate template (.sla) before running this script.")
        return

    if not validate_template_styles(log_file):
        error_dialog("Template validation failed (missing paragraph styles). See log for details.")
        return

    # Load metadata (prefer Markdown front matter; fallback to empty)
    raw_meta = {}
    if md_path and os.path.isfile(md_path):
        try:
            raw_meta = load_markdown_metadata(md_path)
        except Exception as e:
            log(f"Failed to load Markdown metadata: {e}", log_file)
    else:
        log("No markdown_source provided or file missing; proceeding with empty metadata.", log_file)

    # Load layout map
    try:
        layout_map = load_layout_map(layout_map_path)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog(f"Failed to load layout_map.yaml: {e}")
        log(f"layout_map load error: {tb}", log_file)
        return

    # Apply metadata to frames (Title, DocId, APNs, etc.)
    apply_meta_to_frames(layout_map, raw_meta, log_file=log_file)

    # Parse DocBook and build content blocks
    try:
        root = load_docbook(docbook_path)
        blocks = build_blocks(root)
    except Exception as e:
        tb = traceback.format_exc()
        error_dialog("Failed to parse DocBook: %s" % e)
        log("DocBook parse error: %s" % tb, log_file)
        return

    # For now, we use the first page's body frame from layout_map as the primary body target.
    body_frame_name = None
    pages = layout_map.get("sop_to_layout_map", {}).get("pages", [])
    for page_cfg in pages:
        if page_cfg.get("page") == 1:
            roles = page_cfg.get("roles", {})
            body_role = roles.get("body")
            if isinstance(body_role, dict):
                body_frame_name = body_role.get("frame")
            break

    if not body_frame_name:
        error_dialog("No body frame mapping found for page 1 in layout_map.yaml.")
        log("No body frame mapping for page 1.", log_file)
        return

    # Flow content into body (single frame for now)
    flow_blocks_into_body(blocks, body_frame_name, log_file=log_file)

    # Export PDF if configured
    pdf_path = job.get("output_pdf")
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

    log("Job completed.", log_file)


if __name__ == "__main__":
    main()
