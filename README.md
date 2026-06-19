# Hilhi Engineering Photo Kiosk

## Overview

The Hilhi Engineering Photo Kiosk is a Raspberry Pi based appliance
designed to transfer student photos from cameras and USB storage
devices into managed Google Drive folders.

The kiosk provides a simple workflow for classroom photography,
engineering projects, journalism, yearbook activities, and other
student media projects.

Students connect a camera or USB storage device, enter a six-digit
student ID, and the kiosk performs the remaining workflow
automatically.

---

## Project Information

PROJECT:  Hilhi Engineering Photo Kiosk

AUTHOR:   Wayne Clift

ORG:      Hilhi Engineering

VERSION:  See `src/version.py`

---

## Student Workflow

1. Connect camera or USB storage device.
2. Wait for device detection.
3. Enter six-digit student ID.
4. Press `#`.
5. Wait for upload completion.
6. Remove device when instructed.

The kiosk automatically:

* Validates student ID.
* Creates Google Drive folders.
* Shares folders with students.
* Uploads photos.
* Deletes source photos when enabled.
* Returns to ready state.

---

## Features

### Device Support

* USB storage devices
* Cameras supported through gphoto2

### Student Identification

* Six-digit student IDs
* Keypad entry
* LCD feedback
* Invalid-ID handling

### Google Integration

* Google Drive uploads
* Automatic folder creation
* Automatic folder sharing
* Google Sheets roster synchronization

### Reliability

* Automatic startup on boot
* Automatic roster refresh
* Activity logging
* Recovery from missing roster cache
* Device removal detection

---

## Administrative Commands

### Refresh Roster

```text
101010#
```

Downloads roster information from Google Sheets and rebuilds the
local roster cache.

### Toggle Delete Mode

```text
202020#
```

Enables or disables deletion of source photos after import.

### System Status

```text
303030#
```

Displays:

* Google authentication status
* Roster availability
* Delete mode status
* Software version

### Network Diagnostics

```text
404040#
```

Displays:

* Network IP address
* Roster status
* Delete mode status
* Software version

---

## Nightly Maintenance

### 01:00

Refresh roster from Google Sheets.

```text
Google Sheets
    ->
config/roster.csv
```

### 02:00

Clean student Google Drive folders.

Uploaded photo files are removed.

Student folders remain intact.

### 03:00

Clean local import cache.

Import folders older than seven days are removed.

---

## Logging

Activity is recorded in:

```text
logs/kiosk.log
```

Examples include:

* Device detection
* Student validation
* Upload completion
* Administrative actions
* Cleanup operations
* Error conditions

---

## Repository Layout

```text
photo-kiosk/

├── bin/
├── config/
├── data/
├── docs/
├── logs/
├── src/
├── tests/
├── kiosk.py
└── README.md
```

### bin/

Helper scripts.

### config/

Configuration files and roster cache.

### data/

Runtime data and folder cache information.

### docs/

Project documentation.

### logs/

Runtime log files.

### src/

Production source code.

### tests/

Manual and development test programs.

---

## Security

The following files must never be committed to source control:

```text
config/credentials.json
config/token.json
```

These files contain Google authentication information.

The repository uses `.gitignore` to prevent accidental publication.

---

## Deployment

The kiosk runs as a systemd service:

```text
photo-kiosk.service
```

The service starts automatically whenever the Raspberry Pi boots.

See:

```text
docs/BUILD_NOTES_PI_SETUP.md
docs/SYSTEMD_SETUP.md
```

for deployment details.

---

## Future Improvements

Possible future enhancements include:

* Touch-screen interface
* Barcode scanning
* RFID authentication
* Enhanced diagnostics
* Multi-teacher deployments

---

## Support Documentation

Additional information is available in:

```text
docs/BUILD_NOTES_PI_SETUP.md
docs/SYSTEMD_SETUP.md
tests/README.md
```


License
-------

This project is licensed under the GNU General Public License
Version 3 (GPLv3).

See the LICENSE file for details.
