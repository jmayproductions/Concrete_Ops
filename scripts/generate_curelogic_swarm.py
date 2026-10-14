#!/usr/bin/env python3
"""Regenerate CureLogic Studio drop-in zip from copilot-studio/curelogic-crew."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    studio = ROOT / "copilot-studio" / "curelogic-crew"
    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "CureLogicCuring-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
