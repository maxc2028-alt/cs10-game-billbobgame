"""Launcher for Ethan's neighborhood cleanup game."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(Path(__file__).with_name("game-ethan.py"), run_name="__main__")
