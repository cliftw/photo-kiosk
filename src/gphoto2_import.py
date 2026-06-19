# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/gphoto2_import.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Imports photos from cameras supported through gphoto2.
# =============================================================================
#!/usr/bin/env python3

import subprocess
from pathlib import Path
from datetime import datetime


def run_gphoto2(args):
    command = ["gphoto2"] + args

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "gphoto2 command failed:\n"
            + " ".join(command)
            + "\n"
            + result.stderr
        )

    return result.stdout


def list_camera_files():
    output = run_gphoto2(["--list-files"])

    files = []
    current_folder = None

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("There are") and "files in folder" in line:
            current_folder = (
                line.split("folder", 1)[1]
                .strip()
                .rstrip(".")
                .strip("'\"")
            )

        elif line.startswith("#") and current_folder:
            parts = line.split()

            if len(parts) < 2:
                continue

            file_number = parts[0].lstrip("#")
            filename = parts[1]

            files.append({
                "folder": current_folder,
                "number": file_number,
                "filename": filename,
            })

    return files


def import_from_gphoto2(
    student_id,
    archive_root="data/imports",
    delete_after_import=False,
):
    archive_root = Path(archive_root)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination_dir = archive_root / student_id / timestamp
    destination_dir.mkdir(parents=True, exist_ok=True)

    camera_files = list_camera_files()

    imported_files = []
    deleted_files = []

    #
    # Download everything first
    #
    for camera_file in camera_files:
        destination_file = destination_dir / camera_file["filename"]

        counter = 1

        while destination_file.exists():
            destination_file = (
                destination_dir
                / f"{destination_file.stem}_{counter}{destination_file.suffix}"
            )
            counter += 1

        run_gphoto2([
            "--folder",
            camera_file["folder"],
            "--get-file",
            camera_file["number"],
            "--filename",
            str(destination_file),
        ])

        if not destination_file.exists():
            raise RuntimeError(
                f"Download failed: {camera_file['filename']}"
            )

        imported_files.append(destination_file)

    #
    # Delete afterwards in descending file-number order
    #
    if delete_after_import:
        files_for_deletion = sorted(
            camera_files,
            key=lambda f: (f["folder"], int(f["number"])),
            reverse=True,
        )

        for camera_file in files_for_deletion:
            run_gphoto2([
                "--folder",
                camera_file["folder"],
                "--delete-file",
                camera_file["number"],
            ])

            deleted_files.append(camera_file)

    return {
        "destination_dir": destination_dir,
        "imported_files": imported_files,
        "deleted_files": deleted_files,
    }
