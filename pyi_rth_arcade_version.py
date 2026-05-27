"""PyInstaller runtime hook for Arcade version loading.

Arcade imports its version module during startup. In frozen builds, the
bundled VERSION file can be inaccessible early in startup on some systems,
which prevents the app from opening at all. This hook provides the version
module up front so Arcade does not need to read the file.
"""

from types import ModuleType
import sys


if "arcade.version" not in sys.modules:
    arcade_version = ModuleType("arcade.version")
    arcade_version.VERSION = "3.3.3"
    arcade_version.__version__ = "3.3.3"
    sys.modules["arcade.version"] = arcade_version
