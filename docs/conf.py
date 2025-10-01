# -- Path setup --------------------------------------------------------------
import os, sys
# conf.py is in docs/, project root is one level up
sys.path.insert(0, os.path.abspath('..'))

DOCS_DIR = os.path.dirname(__file__)
PACKAGE_PARENT = os.path.abspath(os.path.join(DOCS_DIR, '..', '..'))  # one above Lab2_JanaAyoub
sys.path.insert(0, PACKAGE_PARENT)

# -- Project information -----------------------------------------------------
project = 'PyQt5/Tkinter'
author = 'Jana Ayoub'
copyright = '2025, Jana Ayoub'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]

# Show members (prevents empty pages)
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'inherited-members': True,
    'show-inheritance': True,
}
autosummary_generate = True

# If GUI/deps cause import errors, mock them
autodoc_mock_imports = ['tkinter', 'PyQt5', 'sip']

# Optional polish
add_module_names = False
autodoc_typehints = 'description'
napoleon_google_docstring = True
napoleon_numpy_docstring = True

templates_path = ['_templates']
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    '**/qt_forms_*.py',
    '**/main_pyqt5.py',
]


# -- HTML --------------------------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
