#! /usr/bin/env python
##########################################################################
# pysphinxdoc - Copyright (C) AGrigis, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Pysphinxdoc current version
version_major = 1
version_minor = 1
version_micro = 3

# Expected by setup.py: string of form "X.Y.Z"
__version__ = "{0}.{1}.{2}".format(version_major, version_minor, version_micro)

# Expected by setup.py: the status of the project
CLASSIFIERS = ["Development Status :: 5 - Production/Stable",
               "Environment :: Console",
               "Environment :: X11 Applications :: Qt",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering",
               "Topic :: Utilities"]

# Project descriptions
description = "Python package documentation generation tool."
SUMMARY = """
.. container:: summary-carousel

    PySphinxDoc is a Python module for **fast and easy documentation of Python
    Packages**.

    It provides the **sphinxdoc** Python script for this purpose.
"""
long_description = """
============
pysphinxdoc
============

PySphinxDoc is a tool for generating automatically API documentation
for Python modules, based on their reStructuredText docstrings, using the
`sikit-learn <http://scikit-learn.org/>`_ theme,
`Bootstrap <http://getbootstrap.com/>`_ and
`Sphinx <http://www.sphinx-doc.org/>`_.
Visit this `module documentation <https://AGrigis.github.io/pysphinxdoc/>`_
for a live example.

Here is an exemple to generate the 'pysphinxdoc' module documentation:

* first generate the rst files 'sphinxdoc -v 2 -p $HOME/git/pysphinxdoc/ -n
  pysphinxdoc -o $HOME/git/pysphinxdoc/doc/'.
* then generate the html files 'cd $HOME/git/pysphinxdoc/doc; make raw-html'.

Expect a '$name_module/doc/source/_static' folder containing a logo named
'$name_module.png' and an 'carousel' subfolder containing a list of images
to be displayed in the index banner of the site.

Expect also an 'axamples' folders containing the gallery items as expected
by the 'sphinx_ext' plugin.

The documentation is generated from the reStructuredText docstrings of each
module, function or class.

In order to find module information, an 'info.py' module is expected at the
root of the module with mandatory keys:

    * NAME: the name of the module.
    * DESCRIPTION: the module short description that will be displayed in the
      banner.
    * SUMMARY: a text displayed with the carousel.
    * LONG_DESCRIPTION: the index page content.
    * URL: the module URL.
    * AUTHOR: the author of the module.
    * AUTHOR_EMAIL: the author e-mail.
    * __version__: the module version.

And optional keys:

    * EXTRANAME: a name that will be displayed in the last element of the
      navbar (default 'PYSPHINXDOC').
    * EXTRAURL: the associated URL (default the pySphinxDoc URL).
"""

# Main setup parameters
NAME = "pysphinxdoc"
ORGANISATION = "CEA"
MAINTAINER = "Antoine Grigis"
MAINTAINER_EMAIL = "antoine.grigis@cea.fr"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "https://github.com/AGrigis/pysphinxdoc"
DOWNLOAD_URL = "https://github.com/AGrigis/pysphinxdoc"
LICENSE = "CeCILL-B"
CLASSIFIERS = CLASSIFIERS
AUTHOR = "pysphinxdoc developers"
AUTHOR_EMAIL = "antoine.grigis@cea.fr"
PLATFORMS = "OS Independent"
ISRELEASE = True
VERSION = __version__
PROVIDES = ["pysphinxdoc"]
REQUIRES = [
    "sphinx==7.2.6",
    "sphinx-gallery==0.19.0",
    "memory-profiler==0.61.0",
    "setuptools",
    "matplotlib",
    "mock"
]
EXTRA_REQUIRES = {}
