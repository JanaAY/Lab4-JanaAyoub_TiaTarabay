# -- Path setup --------------------------------------------------------------
import os
import sys
from pathlib import Path

# docs/ -> project root
DOCS_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = DOCS_DIR.parent.resolve()
SRC_DIR = PROJECT_ROOT / "src"

# Add project root (imports like `import models...`) and src/ (if present)
sys.path.insert(0, str(PROJECT_ROOT))
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

# -- Project information -----------------------------------------------------
project = "School Management (PyQt5)"
author = "Tia Tarabay & Jana Ayoub"
release = "1.0.0"
copyright = "2025, " + author
html_title = "School Management (PyQt5) — API"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

# Keep pages non-empty and readable
autosummary_generate = True
add_module_names = False
autodoc_member_order = "bysource"
autodoc_typehints = "description"

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "inherited-members": True,  # keep from main
    "show-inheritance": True,
}

# Mock GUI/heavy deps so the docs build without a GUI runtime
autodoc_mock_imports = [
    "tkinter",
    "PyQt5", "PyQt5.QtWidgets", "PyQt5.QtGui", "PyQt5.QtCore",
    "sip",
    "models.db", "models.data_manager", "models.db_sync",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "venv",
    ".venv",
    "**/qt_forms_*.py",
    "**/main_pyqt5.py",
]

# -- HTML --------------------------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {"collapse_navigation": False, "sticky_navigation": True}
html_static_path = ["_static"]
