# Raspberry Pi 5 Classroom Photo Kiosk

## Mid-Project Status Report and Continuation Notes

**Date:** June 2026

### Project Goal

Provide a self-service classroom photo import station.

Student workflow:

1.  Plug in camera or photo storage device.
2.  Enter student ID.
3.  Photos import to Raspberry Pi SSD archive.
4.  Photos are removed from source media (camera/storage).
5.  Photos upload to student's Google Drive pickup folder.
6.  Student accesses photos from Chromebook.

------------------------------------------------------------------------

# Hardware

Current hardware:

-   Raspberry Pi 5
-   512GB NVMe SSD
-   Raspberry Pi OS
-   SSH enabled
-   Username: `cliftw`
-   Access: `ssh cliftw@raspberrypi`

Planned UI hardware:

-   4x4 matrix keypad
-   Grove I2C LCD (20x2)

Hardware UI is intentionally deferred until core workflow is complete.

------------------------------------------------------------------------

# Core Design Decisions

## Storage Philosophy

Camera/storage media:

-   Temporary source only
-   Delete after successful import

Pi SSD:

-   Permanent archive copy
-   Source of truth
-   May be retained all school year

Google Drive:

-   Student pickup area
-   Shared read-only with student
-   Contents cleaned periodically
-   Folder persists

------------------------------------------------------------------------

## Supported Device Types

### PTP Cameras

Handled through:

-   gphoto2

Example tested:

-   Canon PowerShot A495

### Filesystem Devices

Handled through mounted storage:

-   USB thumb drives
-   Cameras that mount as storage devices

Importer behavior:

-   Prefer DCIM if present
-   Otherwise recurse entire device
-   Import image files only

Supported image formats:

-   jpg
-   jpeg
-   png
-   cr2
-   cr3
-   crw
-   nef
-   arw
-   orf
-   raf

Videos ignored.

------------------------------------------------------------------------

# Google Drive Design

Root folder:

PhotoKioskStudents/

Student folder:

username extracted from:

email before @

Example:

dunhm030@hsd.k12.or.us

becomes:

PhotoKioskStudents/dunhm030

Folder naming intentionally contains:

-   no spaces
-   no student names
-   stable username only

------------------------------------------------------------------------

# Data Files

## Teacher Managed

config/roster.csv

Current format:

id,name,email,active

Example:

337030,Marcus Dunham,dunhm030@hsd.k12.or.us,yes

Future source:

Google Sheet

Likely future sync:

Google Sheet -\> roster.csv

Roster remains source of truth.

------------------------------------------------------------------------

## Kiosk Managed

data/student_folders.csv

Format:

id,folder_id

Example:

337030,1fFLcHPlwWseZq_pUpz75IUWJiFc21WMq

Purpose:

Maintain mapping between student ID and Drive folder.

This is intentionally separate from roster.csv.

Reason:

Roster will eventually be regenerated from Google Sheets.

Generated metadata should not be stored in roster.csv.

------------------------------------------------------------------------

# Google API Status

Completed:

-   Google Cloud project created
-   Google Drive API enabled
-   OAuth consent screen configured
-   OAuth Desktop App created
-   credentials.json downloaded
-   token.json generated
-   OAuth authentication working

Files:

config/credentials.json config/token.json

Virtual environment:

.venv/

Installed packages:

-   google-api-python-client
-   google-auth-httplib2
-   google-auth-oauthlib

Important note:

OAuth required SSH tunnel because Pi is headless.

Working solution:

SSH port forward to localhost during authentication.

------------------------------------------------------------------------

# Implemented Modules

## src/student_lookup.py

Responsibilities:

-   Read roster.csv
-   Validate student ID
-   Reject inactive students
-   Strip whitespace from CSV fields

Returns clean student record.

------------------------------------------------------------------------

## src/device_detect.py

Responsibilities:

Detect:

-   gphoto2 cameras
-   USB storage devices

States:

-   none
-   ready
-   too_many

Multiple devices intentionally rejected.

------------------------------------------------------------------------

## src/filesystem_import.py

Responsibilities:

Import photos from:

-   USB drives
-   mounted cameras

Features:

-   image filtering
-   archive folder creation
-   copy verification
-   optional source deletion

Tested:

-   copy
-   delete

------------------------------------------------------------------------

## src/gphoto2_import.py

Responsibilities:

Import photos from PTP cameras.

Features:

-   folder-aware file handling
-   download
-   optional delete

Bug fixed:

Deleting while iterating caused file-number shifting.

Final solution:

-   download all first
-   delete in reverse order

Tested successfully.

------------------------------------------------------------------------

## src/drive_upload.py

Original rclone uploader.

Used during early testing.

Still functional.

May eventually be retired in favor of Google API uploads.

------------------------------------------------------------------------

## src/student_folder.py

Responsibilities:

Create student folder path using username.

Original implementation used rclone folder creation.

------------------------------------------------------------------------

## src/google_drive_api.py

Current Drive API layer.

Features:

-   authenticate
-   create folder
-   locate folder
-   share folder
-   upload files

Current upload behavior:

Search existing filename first.

If file exists:

-   update existing file

Otherwise:

-   create new file

This avoids duplicate filenames in Drive.

------------------------------------------------------------------------

## src/student_folder_store.py

Responsibilities:

Read/write:

data/student_folders.csv

Functions:

-   get_folder_id()
-   save_folder_id()

Purpose:

Persistent folder mapping.

------------------------------------------------------------------------

# Tested Workflows

Verified:

Student ID -\> lookup

Device detection -\> USB -\> gphoto2

Import -\> USB -\> gphoto2

Delete source -\> USB -\> gphoto2

Create folder -\> Drive

Share folder -\> Drive

Store folder ID

Upload photos

Replace existing filename uploads

------------------------------------------------------------------------

# Observations and Lessons Learned

Google Drive:

Folder names are not unique.

Folder ID is authoritative.

Store folder IDs.

------------------------------------------------------------------------

Google sharing:

Bogus email addresses may still appear as permissions.

Do not use sharing success as account validation.

Roster should come from trusted school source.

------------------------------------------------------------------------

CSV parsing:

Whitespace caused email sharing failures.

Solution:

Normalize all CSV fields during lookup.

------------------------------------------------------------------------

USB mounting:

Observed approximately 5 second delay before mounted storage became
visible.

Kiosk should tolerate device stabilization delay.

------------------------------------------------------------------------

# Remaining Work

## High Priority

### Build kiosk.py

Replace individual test scripts with permanent state machine.

Desired flow:

Idle -\> Device detected -\> Enter ID -\> Import -\> Upload -\> Complete
-\> Return to idle

Terminal version first.

------------------------------------------------------------------------

### Google Sheet Sync

Future:

Google Sheet -\> roster.csv

Automated refresh.

------------------------------------------------------------------------

### Cleanup Job

Periodic cleanup of student pickup folders.

Keep folder.

Delete contents.

------------------------------------------------------------------------

## Hardware

### Grove LCD

Display status:

-   Enter ID
-   Student name
-   Importing
-   Uploading
-   Complete

### Keypad

Replace keyboard input.

4x4 matrix keypad.

Likely biggest remaining hardware risk.

------------------------------------------------------------------------

## Deployment

systemd service:

kiosk.py

systemd timer:

roster sync

systemd timer:

cleanup job

------------------------------------------------------------------------

# Recommended Next Session Starting Point

Start with:

Build terminal-only kiosk.py

using existing modules:

-   student_lookup
-   device_detect
-   filesystem_import
-   gphoto2_import
-   student_folder_store
-   google_drive_api

Goal:

Single always-running workflow loop before adding keypad and LCD.
