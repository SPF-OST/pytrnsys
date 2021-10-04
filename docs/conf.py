# pylint: skip-file
# type: ignore

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../"))
from shutil import copy
from pathlib import Path

# from_path = (Path(".") / "../README.md" ).resolve().__str__()
# copy(from_path, '.')
import recommonmark
from recommonmark.transform import AutoStructify

autodoc_mock_imports = ["numpy"]
autodoc_mock_imports = ["scipy"]
autodoc_mock_imports = ["pandas"]
autodoc_mock_imports = ["matplotlib"]
autodoc_mock_imports = ["seaborn"]
autodoc_mock_imports = ["bokeh"]
master_doc = "index"

github_doc_root = "https://github.com/rtfd/recommonmark/tree/master/doc/"


def setup(app):
    app.add_config_value(
        "recommonmark_config",
        {
            #'url_resolver': lambda url: github_doc_root + url,
            "auto_toc_tree_section": "Contents",
        },
        True,
    )
    app.add_transform(AutoStructify)


# from mock import Mock as MagicMock

# class Mock(MagicMock):
#    @classmethod
#    def __getattr__(cls, name):
#        return MagicMock()

# MOCK_MODULES = ['numpy', 'scipy', 'matplotlib.pyplot']
# sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# -- Project information -----------------------------------------------------

project = "pytrnsys"
copyright = "2021, Institute for Solar Technology (SPF), OST Rapperswil"
author = "Dani Carbonell, Martin Neugebauer, Damian Birchler, Jeremias Schmidli, Maike Schubert,"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.coverage", "sphinx.ext.napoleon", "sphinx.ext.viewcode", "recommonmark"]
# ,
#    'rst2pdf.pdfbuilder'

# pdf_documents = [('index', u'rst2pdf', u'Sample rst2pdf doc', u'Your Name'),]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}
