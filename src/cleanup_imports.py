# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/cleanup_imports.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Removes old local import folders from the Pi after the retention
#            period.
# =============================================================================
#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timedelta
import shutil

from src.kiosk_logger import logger


IMPORT_ROOT = Path("data/imports")
RETENTION_DAYS = 7


def find_old_import_dirs(retention_days=RETENTION_DAYS):
    cutoff = datetime.now() - timedelta(days=retention_days)
    old_dirs = []

    if not IMPORT_ROOT.exists():
        return old_dirs

    for student_dir in IMPORT_ROOT.iterdir():
        if not student_dir.is_dir():
            continue

        for import_dir in student_dir.iterdir():
            if not import_dir.is_dir():
                continue

            try:
                timestamp = datetime.strptime(
                    import_dir.name,
                    "%Y%m%d-%H%M%S"
                )
            except ValueError:
                continue

            if timestamp < cutoff:
                old_dirs.append(import_dir)

    return sorted(old_dirs)


def cleanup_imports(retention_days=RETENTION_DAYS, dry_run=True):
    old_dirs = find_old_import_dirs(retention_days)

    deleted_dirs = []

    for import_dir in old_dirs:
        if dry_run:
            logger.info(
                f"CLEANUP_DRY_RUN,path={import_dir}"
            )
        else:
            shutil.rmtree(import_dir)
            deleted_dirs.append(import_dir)
            logger.info(
                f"CLEANUP_DELETED,path={import_dir}"
            )

    logger.info(
        f"CLEANUP_COMPLETE,"
        f"dry_run={dry_run},"
        f"retention_days={retention_days},"
        f"matched={len(old_dirs)},"
        f"deleted={len(deleted_dirs)}"
    )

    return {
        "matched": old_dirs,
        "deleted": deleted_dirs,
    }


if __name__ == "__main__":
    result = cleanup_imports(dry_run=False)

    print("Cleanup Pi Imports LIVE")
    print(f"Matched old import folders: {len(result['matched'])}")
    print("Deleted folders: 0")

    for path in result["matched"]:
        print(path)
