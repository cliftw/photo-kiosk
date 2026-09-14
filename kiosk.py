# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      kiosk.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Main photo kiosk application and appliance workflow controller.
# =============================================================================
#!/usr/bin/env python3

import time
import socket
import subprocess

from src.device_detect import device_status
from src.student_lookup import lookup_student
from src.student_folder_store import get_folder_id, save_folder_id
from src.filesystem_import import import_from_filesystem
from src.gphoto2_import import import_from_gphoto2
from src.google_drive_api import (
    get_or_create_student_folder,
    share_folder_with_student,
    upload_file_to_folder,
    get_drive_service,
    get_next_upload_number,
)
from src.lcd_grove import GroveRgbLcd
from src.keypad_matrix import MatrixKeypad
from src.student_id_entry import get_student_id
from src.kiosk_logger import logger
from src.roster_refresh import refresh_roster
from src.version import APP_VERSION, APP_YEAR, APP_ORG, APP_SHORT_NAME, APP_NAME, APP_AUTHOR, BUILD_DATE
from pathlib import Path

ADMIN_REFRESH       = "101010"
ADMIN_TOGGLE_DELETE = "202020"
ADMIN_STATUS        = "303030"
ADMIN_DIAGNOSTICS   = "404040"

ROSTER_FILE = Path("config/roster.csv")

delete_after_import = True


def get_or_setup_student_folder(student, lcd):
    folder_id = get_folder_id(student["id"])

    if folder_id:
        logger.info(
            f"FOLDER_FOUND,student={student['id']},folder_id={folder_id}"
        )
        return folder_id

    lcd.message("Creating Drive", "folder...")
    logger.info(
        f"FOLDER_CREATE_START,student={student['id']},email={student['email']}"
    )
    folder_id = get_or_create_student_folder(student)

    lcd.message("Sharing folder", "with student")
    share_folder_with_student(folder_id, student["email"])
    logger.info(
        f"FOLDER_SHARED,student={student['id']},email={student['email']},folder_id={folder_id}"
    )

    save_folder_id(student["id"], folder_id)
    logger.info(
        f"FOLDER_SAVED,student={student['id']},folder_id={folder_id}"
    )
    return folder_id


def wait_for_one_device(lcd):
    last_status = None
    idle_message_time = None
    display_is_off = False
    idle_sleep_seconds = 30

    while True:
        status, devices = device_status()

        if status != last_status:
            last_status = status

            if status == "none":
                lcd.wake()
                lcd.set_rgb(0, 128, 255)
                lcd.message("Photo Kiosk", "Insert camera")
                logger.info("IDLE_WAITING_FOR_DEVICE")

                idle_message_time = time.time()
                display_is_off = False

            elif status == "too_many":
                lcd.wake()
                lcd.set_rgb(255, 0, 0)
                lcd.message("Too many", "devices")
                logger.warning("TOO_MANY_DEVICES")

                idle_message_time = None
                display_is_off = False

            elif status == "ready":
                lcd.wake()
                lcd.set_rgb(0, 255, 0)
                lcd.message("Camera found", "Enter ID")
                logger.info(
                    f"DEVICE_DETECTED,type={devices[0]['type']},description={devices[0]['description']}"
                )
                time.sleep(0.75)
                return devices[0]

        if (
            status == "none"
            and idle_message_time is not None
            and not display_is_off
            and time.time() - idle_message_time >= idle_sleep_seconds
        ):
            lcd.idle_off()
            logger.info("IDLE_DISPLAY_OFF")
            display_is_off = True

        time.sleep(0.5)

        
def wait_for_device_removal(lcd):
    lcd.set_rgb(0, 255, 0)
    lcd.message("Upload done", "Remove camera")

    while True:
        status, devices = device_status()

        if status == "none":
            lcd.set_rgb(0, 128, 255)
            lcd.message("Ready", "Next student")
            time.sleep(1)
            logger.info("DEVICE_REMOVED")
            return

        time.sleep(0.5)


def handle_admin_command(student_id, lcd):
    global delete_after_import

    if student_id == ADMIN_REFRESH:
        lcd.set_rgb(128, 0, 255)
        lcd.message("Refreshing", "roster...")
        print("ADMIN: refresh roster requested")
        logger.info("ADMIN_COMMAND,command=refresh_roster")

        try:
            result = refresh_roster()

            lcd.set_rgb(0, 255, 0)
            lcd.message(
                "Roster updated",
                f"{result['record_count']} records",
            )

            print(f"Roster refreshed: {result['record_count']} records")
            logger.info(
                f"ADMIN_REFRESH_COMPLETE,"
                f"records={result['record_count']},"
                f"duplicates={result['duplicates']},"
                f"conflicts={result['conflicts']}"
            )

        except Exception:
            lcd.set_rgb(255, 0, 0)
            lcd.message("Refresh failed", "Check logs")
            logger.exception("ADMIN_REFRESH_FAILED")

        time.sleep(2)
        return True

    if student_id == ADMIN_TOGGLE_DELETE:
        delete_after_import = not delete_after_import

        lcd.set_rgb(128, 0, 255)

        if delete_after_import:
            lcd.message("Delete mode", "ON")
            print("ADMIN: delete mode ON")
            logger.info("ADMIN_COMMAND,command=toggle_delete,delete_after_import=True")
        else:
            lcd.message("Delete mode", "OFF")
            print("ADMIN: delete mode OFF")
            logger.info("ADMIN_COMMAND,command=toggle_delete,delete_after_import=False")

        time.sleep(2)
        return True

    if student_id == ADMIN_STATUS:
        lcd.set_rgb(128, 0, 255)
        lcd.message("Checking", "system...")

        try:
            service = get_drive_service()
            service.files().list(pageSize=1, fields="files(id)").execute()

            roster_exists = ROSTER_FILE.exists()
            roster_status = "YES" if roster_exists else "NO"
            delete_status = "ON" if delete_after_import else "OFF"

            lcd.set_rgb(0, 255, 0)
            lcd.message("Google Auth", "OK")
            time.sleep(2)

            lcd.message("Roster File", roster_status)
            time.sleep(2)

            lcd.message("Delete Mode", delete_status)
            time.sleep(2)

            lcd.message("Hilhi Engr", APP_VERSION)
            time.sleep(2)

            
            logger.info(
                f"ADMIN_STATUS,"
                f"google_auth=ok,"
                f"roster_exists={roster_exists},"
                f"delete_after_import={delete_after_import}"
            )

        except Exception:
            lcd.set_rgb(255, 0, 0)
            lcd.message("Google Auth", "FAILED")
            logger.exception("ADMIN_STATUS_FAILED")
            time.sleep(2)

        return True
    
    if student_id == ADMIN_DIAGNOSTICS:

        logger.info("ADMIN_COMMAND,command=diagnostics")

        try:

            ip = "unknown"

            try:
                result = subprocess.run(
                    ["hostname", "-I"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    ip = result.stdout.strip().split()[0]

            except Exception:
                pass

            lcd.set_rgb(128, 0, 255)

            lcd.message(
                "Network",
                ip[:16]
            )
            time.sleep(3)

            lcd.message(
                "Roster",
                "Present" if ROSTER_FILE.exists() else "Missing"
            )
            time.sleep(2)

            lcd.message(
                "Delete Mode",
                "ON" if delete_after_import else "OFF"
            )
            time.sleep(2)

            lcd.message(
                "Version",
                APP_VERSION
            )
            time.sleep(2)

            logger.info(
                f"ADMIN_DIAGNOSTICS,ip={ip},roster_exists={ROSTER_FILE.exists()},delete_after_import={delete_after_import}"
            )

        except Exception:
            logger.exception("ADMIN_DIAGNOSTICS_FAILED")

            lcd.set_rgb(255, 0, 0)
            lcd.message(
                "Diagnostics",
                "FAILED"
            )
            time.sleep(2)

        return True
    
    return False


def get_valid_student(lcd, keypad):
    while True:
        lcd.set_rgb(0, 128, 255)
        lcd.message("Camera found", "Enter ID")

        student_id = get_student_id(lcd, keypad)
        if student_id is None:
            return None

        if handle_admin_command(student_id, lcd):
            continue

        if not ROSTER_FILE.exists():
            lcd.set_rgb(255, 128, 0)
            lcd.message("Roster missing", "Refreshing...")
            logger.warning("ROSTER_MISSING,action=auto_refresh")

            try:
                result = refresh_roster()
                logger.info(
                    f"ROSTER_AUTO_REFRESH_COMPLETE,records={result['record_count']}"
                )
            except Exception:
                lcd.set_rgb(255, 0, 0)
                lcd.message("Roster refresh", "failed")
                logger.exception("ROSTER_AUTO_REFRESH_FAILED")
                time.sleep(2)
                continue

        student = lookup_student(student_id)


        
        if student is None:
            lcd.set_rgb(255, 0, 0)
            lcd.message("Invalid ID", student_id)
            print(f"Invalid ID: {student_id}")
            logger.warning(
                f"INVALID_ID,id={student_id}"
            )
            time.sleep(2)
            continue

        logger.info(
            f"STUDENT_VALIDATED,id={student['id']},name={student['name']},email={student['email']}"
        )
        return student

def show_startup_splash(lcd):
    lcd.set_rgb(0, 128, 255)
    lcd.message("HilhiEngineering", f"Photo Kiosk {APP_YEAR}")
    time.sleep(2)

    lcd.set_rgb(128, 0, 255)
    lcd.message("Engineering Lab", "Photo Capture")
    time.sleep(2)

    lcd.set_rgb(0, 128, 255)
    lcd.message(f"Version {APP_VERSION}", "Ready")
    time.sleep(2)

def run_once(lcd, keypad):
    device = wait_for_one_device(lcd)
    logger.info("WORKFLOW_START")
    logger.info(
        f"DEVICE_DETECTED,"
        f"{device['type']},"
        f"{device['description']}"
    )
    student = get_valid_student(lcd, keypad)

    if student is None:
        return

    status, devices = device_status()

    if status != "ready" or devices[0] != device:
        logger.warning("DEVICE_CHANGED_DURING_ID_ENTRY")
        lcd.set_rgb(255, 128, 0)
        lcd.message("Camera changed", "Try again")
        time.sleep(2)
        return

    logger.info(
        f"STUDENT_VALIDATED,"
        f"{student['id']},"
        f"{student['name']},"
        f"{student['email']}"
    )

    
    lcd.set_rgb(0, 255, 0)
    lcd.message("Welcome", student["name"][:16])

    print()
    print(f"Student: {student['name']}")
    print(f"Email:   {student['email']}")
    print(f"Delete after import: {delete_after_import}")
    logger.info(
        f"WORKFLOW_STUDENT,id={student['id']},name={student['name']},email={student['email']},delete_after_import={delete_after_import}"
    )
    time.sleep(1)

    folder_id = get_or_setup_student_folder(student, lcd)

    lcd.set_rgb(0, 128, 255)
    lcd.message("Importing", "photos...")
    logger.info(
        f"IMPORT_START,student={student['id']},device_type={device['type']},delete_after_import={delete_after_import}"
    )

    if device["type"] == "gphoto":
        result = import_from_gphoto2(
            student_id=student["id"],
            delete_after_import=delete_after_import,
        )

    elif device["type"] == "usb_storage":
        result = import_from_filesystem(
            mount_path=device["mount_path"],
            student_id=student["id"],
            delete_after_import=delete_after_import,
        )

    else:
        lcd.set_rgb(255, 0, 0)
        lcd.message("Unsupported", device["type"][:16])
        time.sleep(2)
        return

    imported_files = result["imported_files"]
    deleted_files = result["deleted_files"]
    logger.info(
        f"IMPORT_COMPLETE,student={student['id']},imported={len(imported_files)},deleted={len(deleted_files)}"
    )

    if not imported_files:
        lcd.set_rgb(255, 128, 0)
        lcd.message("No images", "found")
        time.sleep(2)
        logger.warning(
            f"NO_IMAGES_FOUND,student={student['id']},device_type={device['type']}"
        )
        wait_for_device_removal(lcd)
        return

    total = len(imported_files)

    logger.info(
        f"UPLOAD_START,student={student['id']},count={len(imported_files)}"
    )

    upload_number = get_next_upload_number(folder_id)
    upload_prefix = f"U{upload_number:03d}_"

    for index, path in enumerate(imported_files, start=1):
        drive_filename = f"{upload_prefix}{path.name}"

        lcd.write_line(0, f"Upload {index}/{total}")
        lcd.write_line(1, path.name[:16])

        uploaded = upload_file_to_folder(path, folder_id, drive_filename=drive_filename)

        print(f"{uploaded['action'].title()}: {uploaded['name']}")
        logger.info(
            f"FILE_UPLOADED,student={student['id']},file={uploaded['name']},action={uploaded['action']}"
        )

    print()
    print(f"Imported {len(imported_files)} file(s).")
    print(f"Deleted {len(deleted_files)} source file(s).")
    logger.info(
        f"WORKFLOW_COMPLETE,student={student['id']},imported={len(imported_files)},deleted={len(deleted_files)},uploaded={len(imported_files)}"
    )
    print("WORKFLOW COMPLETE")

    lcd.set_rgb(0, 255, 0)
    lcd.message(
        f"Imported {len(imported_files)}",
        f"Deleted {len(deleted_files)}",
    )
    time.sleep(2)
    
    wait_for_device_removal(lcd)


def main():
    lcd = GroveRgbLcd()
    keypad = MatrixKeypad()
    logger.info(f"KIOSK_STARTUP,version={APP_VERSION},author={APP_AUTHOR},built={BUILD_DATE}")
    show_startup_splash(lcd)
    
    try:
        while True:
            run_once(lcd, keypad)

    except KeyboardInterrupt:
        lcd.clear()
        lcd.set_rgb(0, 0, 0)
        keypad.close()
        lcd.close()


if __name__ == "__main__":
    main()
