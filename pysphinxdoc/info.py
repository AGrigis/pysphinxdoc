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
version_minor = 0
version_micro = 0

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
description = "[pysphinxdoc] API Documentation Generation Tool."
long_description = """
============
pysphinxdoc
============

Pysphinxdoc is a tool for generating automatically API documentation
for Python modules, based on their reStructuredText docstrings, using the
`scikit-learn <http://scikit-learn.org/>`_ theme and
`Sphinx <http://www.sphinx-doc.org/>`_.
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
    "sphinx>=1.0"
]
EXTRA_REQUIRES = {}
