# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import uptime_kuma_client

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'uptime-kuma-client'
copyright = (
    '2023 Lucas Held, 2025 Alexandre Magnier, 2026 Janus Coetzee. '
    'Derived from uptime-kuma-api by Lucas Held'
)
author = 'Janus Coetzee'

version = uptime_kuma_client.__version__
release = uptime_kuma_client.__version__


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

toc_object_entries_show_parents = "hide"
autodoc_member_order = "bysource"
add_module_names = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'

html_theme_options = {
    "show_powered_by": False,
    "github_user": "JanusCoetzee",
    "github_repo": "uptime-kuma-client",
    "github_banner": True,
    "show_related": False,
    "note_bg": "#FFF59C",
    "github_button": True,
    "github_type": "star"
}
