# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      tests/test_drive_api_auth.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Manual test for Google API authentication and token creation.
# =============================================================================
#!/usr/bin/env python3

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from src.google_drive_api import SCOPES


CONFIG_DIR = Path("config")
TOKEN_FILE = CONFIG_DIR / "token.json"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"


def main():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    elif not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES,
        )

        creds = flow.run_local_server(
            host="localhost",
            port=8080,
            open_browser=False,
        )

    TOKEN_FILE.write_text(creds.to_json())

    print("Authentication successful.")
    print()
    print("Token written to:")
    print(TOKEN_FILE)


if __name__ == "__main__":
    main()
