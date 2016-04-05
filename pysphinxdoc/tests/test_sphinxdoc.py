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

# Pysphinxdoc import
import pysphinxdoc


class SphinxDoc(unittest.TestCase):
    """ Test the documentation generation script.
    """
    def test_normal_execution(self):
        """ Test the normal behaviour of the function.
        """
        moduledir = os.path.dirname(pysphinxdoc.__path__[0])
        docdir = os.path.join(moduledir, "doc")
        cmd = ["sphinxdoc", "-p",  moduledir, "-n", "pysphinxdoc", "-o",
               docdir, "-v", "2"]
        subprocess.check_call(cmd)


if __name__ == "__main__":
    unittest.main()
