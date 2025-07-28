from pathlib import Path

ROOT_DIR_PATH = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT_DIR_PATH / "docker" / "backend" / ".env"
