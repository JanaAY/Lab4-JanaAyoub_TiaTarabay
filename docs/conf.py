# -- Path setup --------------------------------------------------------------
import sys
from pathlib import Path

HERE = Path(__file__).resolve()      # .../docs/conf.py
REPO_ROOT = HERE.parents[1]          # repo root that contains 'src'
sys.path.insert(0, str(REPO_ROOT))   # so `import src...` works

# Optional: headless Qt for imports during build
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


# --- Project info ---
project = "PyQt5/Tkinter"
author = "Jana Ayoub Tia Tarabay"
release = "1.0.0"

# --- Extensions ---
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "inherited-members": True,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"

# If GUI deps cause issues, mock them:
autodoc_mock_imports = [
    "tkinter",
    "PyQt5",
    "PyQt5.QtWidgets",
    "PyQt5.QtGui",
    "PyQt5.QtCore",
    "sip",
]

add_module_names = False
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Theme
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
