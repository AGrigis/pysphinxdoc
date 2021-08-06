##########################################################################
# pysphinxdoc - Copyright (C) AGrigis, 2016 - 2017
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" Provide usefull functions to interpret a Python code.
"""

# System import
from __future__ import print_function
import os
import re


def examplify(filename, outfile):
    """ Read Python code from the file named by the first argument, and
    write an example as expected by sphinx gallery.

    Parameters
    ----------
    filename: str
        the file path with the Python code to read.
    outfile: str
        the destination file with the gallery example.
    """
    # Read the code
    with open(filename, "rt") as openfile:
        buf = openfile.read()

    # Remove license
    for line in buf.split("\n"):
        if line.startswith("#"):
            buf = buf.replace(line + "\n", "")
        else:
            break

    # Update comments
    for comment in re.findall('""".*?"""', buf, flags=re.DOTALL):
        if buf[buf.find(comment) - 1] != "\n":
            continue
        formated_comment = "#" * 77 + "\n"
        for line in comment.split("\n")[1: -1]:
            formated_comment += "# " + line + "\n"
        buf = buf.replace(comment, formated_comment)

    # Add header
    name = os.path.basename(filename).split(".")[0]
    name = name.replace("_", " ").title()
    header = '"""\n' + name + "\n" + "=" * len(name) + "\n\n"
    header += 'Example automatically generated from package script.\n"""\n\n'
    buf = header + buf

    # Write
    with open(outfile, "wt") as openfile:
        openfile.write(buf)


def dummy():
    """ A simple test function.

    See Also
    --------
    pysphinxdoc.docgen.DocHelperWriter, examplify

    Examples
    --------
    >>> from pysphinxdoc.utils import dummy
    >>> dummy()
    """
    print("OK")
