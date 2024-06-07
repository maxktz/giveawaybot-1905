from pathlib import Path

ROOT_DIR = Path(__file__).absolute().parents[3]
GSHEET_AUTH_FILE: Path = ROOT_DIR / ".google_service_key.json"
