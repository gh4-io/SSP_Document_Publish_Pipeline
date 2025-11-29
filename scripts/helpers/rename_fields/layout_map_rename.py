# rename_frames_from_json.py
# Execute this inside Scribus:
#   Script → Execute Script… → select this file
#
# This script:
#   - Loads mapping from layout_rename_map.json
#   - Selects each old frame by name
#   - Calls setNewName(new_name) on the selected object
#   - Shows a summary of renamed / missing frames

import os
import sys

try:
    import scribus
except ImportError:
    print("This script must be run inside Scribus.")
    sys.exit(1)

import json


def load_rename_map():
    """
    Loads layout_rename_map.json from the same directory as the script.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "layout_rename_map.json")

    if not os.path.exists(json_path):
        scribus.messageBox(
            "Error",
            f"Could not find layout_rename_map.json\nExpected at:\n{json_path}",
            scribus.ICON_WARNING,
            scribus.BUTTON_OK
        )
        return {}

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("frame_rename", {})
    except Exception as e:
        scribus.messageBox(
            "Error Reading JSON",
            f"layout_rename_map.json could not be parsed:\n{e}",
            scribus.ICON_WARNING,
            scribus.BUTTON_OK
        )
        return {}


def rename_frames(frame_map):
    """
    Applies the rename mapping to the currently open Scribus document.

    NOTE:
      - Scribus.setNewName(new_name) renames the *selected* object.
      - So we must select each object by its old name first.
    """
    if not scribus.haveDoc():
        scribus.messageBox(
            "Error",
            "No document open. Please open your template .sla first.",
            scribus.ICON_WARNING,
            scribus.BUTTON_OK
        )
        return

    renamed = []
    missing = []
    collisions = []

    for old_name, new_name in frame_map.items():
        if not scribus.objectExists(old_name):
            missing.append(old_name)
            continue

        # If the new name already exists, warn and skip to avoid collisions
        if scribus.objectExists(new_name):
            collisions.append((old_name, new_name))
            continue

        try:
            scribus.deselectAll()
            scribus.selectObject(old_name)
            scribus.setNewName(new_name)
            scribus.deselectAll()
            renamed.append((old_name, new_name))
        except scribus.NoValidObjectError:
            # Shouldn't happen if objectExists was true, but just in case
            missing.append(old_name)

    # Build summary message
    msg_lines = []

    if renamed:
        msg_lines.append("Renamed Frames:\n")
        for old_name, new_name in renamed:
            msg_lines.append(f"  {old_name} → {new_name}")
        msg_lines.append("")

    if collisions:
        msg_lines.append("Name Collisions (skipped):\n")
        for old_name, new_name in collisions:
            msg_lines.append(f"  {old_name} -> {new_name} (target already exists)")
        msg_lines.append("")

    if missing:
        msg_lines.append("Frames Not Found (skipped):\n")
        for old_name in missing:
            msg_lines.append(f"  {old_name}")

    if not msg_lines:
        msg_lines.append("No frames were renamed.\nCheck layout_rename_map.json names.")

    scribus.messageBox(
        "Rename Summary",
        "\n".join(msg_lines),
        scribus.ICON_NONE,
        scribus.BUTTON_OK
    )


def main():
    if not scribus.haveDoc():
        scribus.messageBox(
            "Error",
            "Open your DTS template .sla before running this script.",
            scribus.ICON_WARNING,
            scribus.BUTTON_OK
        )
        return

    frame_map = load_rename_map()
    if not frame_map:
        scribus.messageBox(
            "No Map Loaded",
            "No rename map was loaded. Aborting.",
            scribus.ICON_WARNING,
            scribus.BUTTON_OK
        )
        return

    rename_frames(frame_map)


if __name__ == "__main__":
    main()
