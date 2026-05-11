<<<<<<< HEAD
"""Launcher for the serious game MVP."""

from game import main


if __name__ == "__main__":
    main()
=======
"""Launcher for Ethan's neighborhood cleanup game."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(Path(__file__).with_name("game-ethan.py"), run_name="__main__")
>>>>>>> b4090e0d4ddab29f1a9f5cd434fc6dedb1d2bcbc
