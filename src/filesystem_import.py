# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/filesystem_import.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Imports image files from mounted USB storage devices into local
#            storage.
# =============================================================================
#!/usr/bin/env python3

import shutil
from pathlib import Path
from datetime import datetime


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".cr2",
    ".cr3",
    ".crw",
    ".nef",
    ".arw",
    ".orf",
    ".raf",
}


def is_image_file(path):
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def find_image_files(mount_path):
    mount_path = Path(mount_path)

    dcim_path = mount_path / "DCIM"

    if dcim_path.exists() and dcim_path.is_dir():
        search_root = dcim_path
    else:
        search_root = mount_path

    image_files = []

    for path in search_root.rglob("*"):
        if is_image_file(path):
            image_files.append(path)

    return sorted(image_files)


def import_from_filesystem(
    mount_path,
    student_id,
    archive_root="data/imports",
    delete_after_import=False,
):
    mount_path = Path(mount_path)
    archive_root = Path(archive_root)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination_dir = archive_root / student_id / timestamp
    destination_dir.mkdir(parents=True, exist_ok=True)

    image_files = find_image_files(mount_path)
    imported_files = []
    deleted_files = []

    for source_file in image_files:
        destination_file = destination_dir / source_file.name

        counter = 1
        while destination_file.exists():
            destination_file = destination_dir / f"{source_file.stem}_{counter}{source_file.suffix}"
            counter += 1

        shutil.copy2(source_file, destination_file)

        if not destination_file.exists():
            raise RuntimeError(f"Copy failed: {source_file}")

        if destination_file.stat().st_size != source_file.stat().st_size:
            raise RuntimeError(f"Copy size mismatch: {source_file}")

        imported_files.append(destination_file)

        if delete_after_import:
            source_file.unlink()
            deleted_files.append(source_file)

    return {
        "destination_dir": destination_dir,
        "imported_files": imported_files,
        "deleted_files": deleted_files,
    }
