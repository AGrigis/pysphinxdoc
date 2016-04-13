##########################################################################
# pysphinxdoc - Copyright (C) AGrigis, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import unittest
import os
import subprocess
from setuptools import find_packages
import shutil

# Pysphinxdoc import
import pysphinxdoc
from pysphinxdoc.docgen import DocHelperWriter


class SphinxDoc(unittest.TestCase):
    """ Test the documentation generation script.
    """
    def test_command_execution(self):
        """ Test the normal behaviour of the command.
        """
        moduledir = os.path.dirname(pysphinxdoc.__path__[0])
        docdir = os.path.join(moduledir, "doc")
        generateddir = os.path.join(docdir, "source", "generated")
        if os.path.isdir(generateddir):
            shutil.rmtree(generateddir)
        cmd = ["sphinxdoc", "-p",  moduledir, "-n", "pysphinxdoc", "-o",
               docdir, "-v", "2"]
        subprocess.check_call(cmd)

    def test_class_execution(self):
        """ Test the normal behaviour of the class.
        """
        moduledir = os.path.dirname(pysphinxdoc.__path__[0])
        docdir = os.path.join(moduledir, "doc")
        generateddir = os.path.join(docdir, "source", "generated")
        if os.path.isdir(generateddir):
            shutil.rmtree(generateddir)
        module_names = find_packages(moduledir)
        docwriter = DocHelperWriter(moduledir, docdir, module_names,
                                    "pysphinxdoc", verbose=2)
        docwriter.write_sphinx_config()
        docwriter.write_layout()
        docwriter.write_index()
        docwriter.write_installation()
        docwriter.write_documentation_index()
        docwriter.write_api_docs()


if __name__ == "__main__":
    unittest.main()
