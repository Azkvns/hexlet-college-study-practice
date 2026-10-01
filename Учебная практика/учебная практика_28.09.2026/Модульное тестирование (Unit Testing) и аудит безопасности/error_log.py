from datetime import datetime
from pathlib import Path

DEFAULT_LOG_PATH = str(Path(__file__).resolve().parent / "app.log")


def log_error(message: str, log_path: str) -> None:
    moment = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{moment} {message}\n"
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(line)
