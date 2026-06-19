# =============================================================================
# PROJECT:   Hilhi Engineering Photo Kiosk
# FILE:      src/kiosk_logger.py
# COPYRIGHT: Wayne Clift, 2026
# LICENSE:   GPLv3 (see LICENSE)
# ORG:       Hilhi Engineering
# DESC:      Configures the shared timestamped kiosk log file.
# =============================================================================
import logging
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "kiosk.log"


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


logger = logging.getLogger("photo_kiosk")
