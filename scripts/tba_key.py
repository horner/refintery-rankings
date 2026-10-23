"""Where the scripts find The Blue Alliance read key. See docs/tba-api.md."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tba_key() -> str:
    """TBA_AUTH_KEY from the environment (CI secret), else from a local tba.env; blank if neither."""
    key = os.environ.get("TBA_AUTH_KEY", "").strip()
    env_file = ROOT / "tba.env"
    if not key and env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "TBA_AUTH_KEY":
                key = value.strip().strip('"').strip("'")
    return key
