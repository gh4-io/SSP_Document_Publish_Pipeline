#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# scribus_export_layout_all_pages_simple.py
#
# Run inside Scribus (Script → Execute Script…).
# Exports ALL document pages as a YAML layout description.
#
# Structure:
# layout:
#   pages:
#     - page: 1
#       frames:
#         - name: 'TitleP1'
#           type: 'TextFrame'
#           x: 0.5000
#           y: 0.5000
#           width: 7.5000
#           height: 0.8000
#           font: 'YourFont'
#           fontsize: 14.00
#     - page: 2
#       frames:
#         - name: 'BodyP2'
#           ...
#
import sys

try:
    import scribus
except ImportError:
    print("Run this script from within Scribus.")
    sys.exit(1)


def error_box(msg):
    scribus.messageBox("Layout Export", msg, scribus.ICON_WARNING, scribus.BUTTON_OK)


def info_box(msg):
    scribus.messageBox("Layout Export", msg, scribus.ICON_INFORMATION, scribus.BUTTON_OK)


def safe_get_geometry(name):
    try:
        x, y = scribus.getPosition(name)
        w, h = scribus.getSize(name)
        return x, y, w, h
    except Exception:
        return None, None, None, None


def safe_get_text_attributes(name):
    try:
        if scribus.getTextLength(name) <= 0:
            return None, None
        scribus.selectText(0, 1, name)
        font = scribus.getFont(name)
        size = scribus.getFontSize(name)
        return font, size
    except Exception:
        return None, None


def export_layout_all_pages():
    if not scribus.haveDoc():
        error_box("No document is open.\n\nOpen your .sla first, then run this script.")
        return

    page_count = scribus.pageCount()
    if page_count <= 0:
        error_box("This document has no pages.")
        return

    yaml_lines = []
    yaml_lines.append("layout:")
    yaml_lines.append("  pages:")

    any_frames = False

    for page in range(1, page_count + 1):
        scribus.gotoPage(page)
        items = scribus.getPageItems()

        # Skip pages with no items at all
        if not items:
            continue

        page_frame_lines = []
        for item in items:
            name = item[0]
            try:
                obj_type = scribus.getObjectType(name)
            except Exception:
                obj_type = "Unknown"

            x, y, w, h = safe_get_geometry(name)
            font, fontsize = (None, None)
            if obj_type == "TextFrame":
                font, fontsize = safe_get_text_attributes(name)

            page_frame_lines.append(f"      - name: {name!r}")
            page_frame_lines.append(f"        type: {obj_type!r}")

            if x is not None:
                page_frame_lines.append(f"        x: {x:.4f}")
                page_frame_lines.append(f"        y: {y:.4f}")
                page_frame_lines.append(f"        width: {w:.4f}")
                page_frame_lines.append(f"        height: {h:.4f}")
            else:
                page_frame_lines.append("        x: null")
                page_frame_lines.append("        y: null")
                page_frame_lines.append("        width: null")
                page_frame_lines.append("        height: null")

            if font is not None:
                page_frame_lines.append(f"        font: {font!r}")
            else:
                page_frame_lines.append("        font: null")

            if fontsize is not None:
                page_frame_lines.append(f"        fontsize: {fontsize:.2f}")
            else:
                page_frame_lines.append("        fontsize: null")

        if page_frame_lines:
            any_frames = True
            yaml_lines.append(f"    - page: {page}")
            yaml_lines.append("      frames:")
            yaml_lines.extend(page_frame_lines)

    if not any_frames:
        error_box("No page items found on any document page.\n\n"
                  "If you only see frames on master pages, copy them onto document pages.")
        return

    yaml_text = "\n".join(yaml_lines)

    out_path = scribus.fileDialog(
        "Save layout YAML for all pages",
        filter="YAML files (*.yaml *.yml);;All files (*.*)",
        isdir=False,
        defaultname="layout_all_pages.yaml",
    )
    if not out_path:
        return

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(yaml_text)
    except Exception as e:
        error_box(f"Failed to write layout YAML:\n{e}")
        return

    info_box(f"Layout for all pages written to:\n{out_path}")


if __name__ == "__main__":
    export_layout_all_pages()
