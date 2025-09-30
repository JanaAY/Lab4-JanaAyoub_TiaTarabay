import os, sys
sys.path.insert(0, os.path.abspath('../src'))  # your code is under src/

project = "School Management (PyQt5)"
author = "Tia Tarabay"
release = "1.0.0"

# Sphinx shows THIS in the footer. Include your name and year.
copyright = "2025, Tia Tarabay"

# optional: control the window/tab title
html_title = "School Management (PyQt5) — API"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

autosummary_generate = True
autodoc_member_order = "bysource"
add_module_names = False
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# mock heavy deps so qt_app imports during docs build
autodoc_mock_imports = [
    "PyQt5", "PyQt5.QtWidgets", "PyQt5.QtGui", "PyQt5.QtCore",
    "models.db", "models.data_manager", "models.db_sync",
]

html_theme = "sphinx_rtd_theme"
html_theme_options = {"collapse_navigation": False, "sticky_navigation": True}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "venv", ".venv"]
