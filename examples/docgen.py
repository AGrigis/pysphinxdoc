"""
Basic example on how to generate a package documentation
========================================================

A simple example of how to document a Python package, here 'pysphinxdoc'.
"""

# System import
import subprocess

# Generate the rst auto documentation
cmd = ["sphinxdoc", "-v", "2", "-p", "$HOME/git/pysphinxdoc", "-n",
       "pysphinxdoc", "-o", "$HOME/git/pysphinxdoc/doc"]
subprocess.check_call(cmd)


# Then compute the html documentation
cmd = ["make", "raw-html"]
subprocess.check_call(cmd,  cwd="$HOME/git/pysphinxdoc/doc")
