# release_packager.py
# Create a zip release artifact for a given SOP/STD/REF/APP document.

import os
import zipfile
import datetime
import argparse


def make_release(family, doc_id, revision, files, releases_root="releases"):
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M")
    family_dir = os.path.join(releases_root, family.upper())
    os.makedirs(family_dir, exist_ok=True)
    zip_name = f"{doc_id}_rev{revision}_{ts}.zip"
    zip_path = os.path.join(family_dir, zip_name)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for label, path in files.items():
            if path and os.path.isfile(path):
                arcname = os.path.join(label, os.path.basename(path))
                z.write(path, arcname=arcname)
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Create a release zip for a document.")
    parser.add_argument("--family", required=True, help="SOP, STD, REF, APP")
    parser.add_argument("--doc-id", required=True, help="e.g. SOP-001")
    parser.add_argument("--revision", required=True, help="Revision number")
    parser.add_argument("--markdown", help="Path to source Markdown")
    parser.add_argument("--docbook", help="Path to DocBook XML")
    parser.add_argument("--pdf", help="Path to PDF")
    parser.add_argument("--html", help="Path to HTML")
    parser.add_argument("--job-json", help="Path to job JSON")
    parser.add_argument("--log", help="Path to log file")
    parser.add_argument("--releases-root", default="releases")
    args = parser.parse_args()

    files = {
        "source": args.markdown,
        "docbook": args.docbook,
        "output": args.pdf,
        "web": args.html,
        "meta": args.job_json,
        "logs": args.log,
    }

    zip_path = make_release(args.family, args.doc_id, args.revision, files, args.releases_root)
    print(zip_path)


if __name__ == "__main__":
    main()
