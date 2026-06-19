# BUILD_NOTES_PI_SETUP.md

# Raspberry Pi 5 Classroom Photo Kiosk

## Platform Build Notes / Environment Recreation Guide

Date: June 2026

Purpose: This document captures the Raspberry Pi setup, Google
configuration, authentication process, package installation, lessons
learned, and deployment notes that are NOT contained in the project
source code.

------------------------------------------------------------------------

# Hardware

Current development platform:

-   Raspberry Pi 5
-   512GB NVMe SSD
-   Raspberry Pi OS
-   SSH enabled

Access:

``` bash
ssh cliftw@raspberrypi
```

------------------------------------------------------------------------

# Core Packages Installed

Confirmed installed:

``` bash
sudo apt install gphoto2
sudo apt install emacs-nox
```

Python already present.

Important later package:

``` bash
sudo apt install python3-venv
```

Optional:

``` bash
sudo apt install elpa-markdown-mode
```

------------------------------------------------------------------------

# Project Directory

``` text
~/photo-kiosk/

src/
config/
data/
logs/
```

Important files:

``` text
config/roster.csv
config/credentials.json
config/token.json

data/student_folders.csv
```

------------------------------------------------------------------------

# Rclone Setup

Purpose:

-   Initial Google Drive uploads
-   Early testing

Remote name:

``` text
HilhiEngineeringDrive
```

Important discovery:

Headless Pi setup did NOT follow browser flow directly.

Authentication required:

``` bash
rclone authorize "drive"
```

from a browser-capable machine.

Generated token was pasted back into Pi setup.

Testing commands:

``` bash
rclone lsd HilhiEngineeringDrive:
rclone mkdir HilhiEngineeringDrive:PhotoKioskTest
rclone copy test.jpg HilhiEngineeringDrive:PhotoKioskTest
```

------------------------------------------------------------------------

# Google Cloud Setup

Project created:

``` text
Hilhi Photo Kiosk
```

Drive API enabled.

OAuth Consent Screen created.

OAuth scope:

``` text
https://www.googleapis.com/auth/drive
```

Desktop OAuth application created:

``` text
Photo Kiosk Pi
```

Downloaded:

``` text
credentials.json
```

Copied to:

``` text
~/photo-kiosk/config/credentials.json
```

------------------------------------------------------------------------

# Python Virtual Environment

Important discovery:

Raspberry Pi OS enforces PEP 668.

Attempting:

``` bash
pip install ...
```

failed with:

``` text
externally-managed-environment
```

Decision:

Use virtual environment.

Creation:

``` bash
cd ~/photo-kiosk
python3 -m venv .venv
```

Activate:

``` bash
source .venv/bin/activate
```

Prompt becomes:

``` text
(.venv)
```

Install packages:

``` bash
pip install \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib
```

------------------------------------------------------------------------

# OAuth Authentication

Initial attempt:

``` python
flow.run_local_server()
```

Result:

Pi attempted browser launch.

Text browser appeared.

Not desired.

Second attempt:

``` python
run_console()
```

Not supported by installed library version.

Final working solution:

``` python
flow.run_local_server(
    host="localhost",
    port=8080,
    open_browser=False,
)
```

Plus SSH tunnel.

On PC:

``` bash
ssh -L 8080:localhost:8080 cliftw@raspberrypi
```

Then:

``` bash
python test_drive_api_auth.py
```

Open provided URL in PC browser.

Google redirects:

``` text
localhost:8080
```

SSH tunnel forwards redirect back to Pi.

Successful result:

``` text
config/token.json
```

created.

------------------------------------------------------------------------

# Google Drive Folder Strategy

Root:

``` text
PhotoKioskStudents
```

Student folder:

Username portion of email.

Example:

``` text
dunhm030@hsd.k12.or.us
```

becomes:

``` text
PhotoKioskStudents/dunhm030
```

Reasons:

-   no spaces
-   unique
-   matches school account
-   easy to search

------------------------------------------------------------------------

# Metadata Storage Strategy

Teacher-managed roster:

``` text
config/roster.csv
```

Format:

``` csv
id,name,email,active
```

Future source:

Google Sheet export/sync.

Generated kiosk metadata:

``` text
data/student_folders.csv
```

Format:

``` csv
id,folder_id
```

Reason:

Keep generated Drive metadata separate from teacher-maintained roster.

------------------------------------------------------------------------

# Important Bugs Found

## CSV Whitespace Bug

Original code:

Returned raw CSV rows.

Problem:

``` csv
999999, Wayne Clift , cliftw@hsd.k12.or.us , , yes
```

Produced invalid email values.

Fix:

Strip whitespace from all fields during lookup.

------------------------------------------------------------------------

## gphoto2 Delete Bug

Original:

Download file.

Delete file.

Continue.

Problem:

Camera file numbering shifted after deletion.

Fix:

Download all files first.

Delete afterwards in reverse file-number order.

------------------------------------------------------------------------

## Google Drive Duplicate Filename Behavior

Discovery:

Drive allows multiple files with same visible name.

Original upload code:

``` python
files.create()
```

always created new file.

Fix:

Search for existing filename.

If found:

``` python
files.update()
```

Otherwise:

``` python
files.create()
```

Result:

Overwrite behavior.

------------------------------------------------------------------------

## USB Mount Delay

Observed:

Approximately 5 second delay after insertion before mount visible.

Implication:

Kiosk must tolerate stabilization delay.

------------------------------------------------------------------------

## Google Sharing Observation

Some invalid-looking email addresses can still appear in permissions
list.

Conclusion:

Roster should be trusted source of student accounts.

Do not use share success as account validation.

------------------------------------------------------------------------

# Deployment Notes

Never publish:

``` text
config/credentials.json
config/token.json
config/roster.csv
data/student_folders.csv
```

Safe to publish:

``` text
src/
README.md
sample_roster.csv
CAD files
wiring diagrams
install scripts
```

------------------------------------------------------------------------

# Future Recreation Strategy

For a new Pi:

Preferred:

Clone SSD image.

Alternative:

Install packages manually and copy project directory.

Potential future:

Create install.sh script.

------------------------------------------------------------------------

# Recommended Next Development Step

Build:

``` text
kiosk.py
```

Terminal-only state machine.

Flow:

Idle -\> Device detected -\> Enter ID -\> Import -\> Upload -\> Complete
-\> Idle

Only after kiosk.py:

-   keypad
-   Grove LCD
-   systemd service
-   roster sync
-   cleanup jobs

------------------------------------------------------------------------

# Final Lesson

Most project risk was removed before hardware UI work began.

The critical workflow:

Student -\> Import -\> Archive -\> Drive -\> Shared Folder

is already proven.
