**Usage**

|PythonVersion|_ |License|_

**Development**

|Linter|_ |Doc|_

**Release**

|PyPi|_


.. |PythonVersion| image:: https://img.shields.io/badge/python-3.12-blue
.. _PythonVersion: https://github.com/AGrigis/pysphinxdoc

.. |Linter| image:: https://github.com/AGrigis/pysphinxdoc/actions/workflows/pep8.yml/badge.svg
.. _Linter: https://github.com/AGrigis/pysphinxdoc/actions

.. |PyPi| image:: https://badge.fury.io/py/pysphinxdoc.svg
.. _PyPi: https://badge.fury.io/py/pysphinxdoc

.. |Doc| image:: https://github.com/AGrigis/pysphinxdoc/actions/workflows/documentation.yml/badge.svg
.. _Doc: http://AGrigis.github.io/pysphinxdoc

.. |License| image:: https://img.shields.io/badge/License-CeCILL--B-blue.svg
.. _License: http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html


===========
pysphinxdoc
===========

API Documentation Generation Tool.

Pysphinxdoc is a tool for generating automatically API documentation
for Python modules, based on their reStructuredText docstrings, using
`Sphinx <http://www.sphinx-doc.org/>`_.
Visit this `module documentation <https://AGrigis.github.io/pysphinxdoc>`_
for a live example.

How to
------

Here is an exemple to generate the 'pysphinxdoc' module documentation:
```
sphinxdoc -v 2 -p $HOME/git/pysphinxdoc -n pysphinxdoc -o $HOME/git/pysphinxdoc/doc
cd $HOME/git/pysphinxdoc/doc
make raw-html
```

Expect a '$name_module/doc/source/_static' folder containing a logo named
'$name_module.png' and an 'carousel' subfolder containing a list of images
to be displayed in the index banner of the site.

The documentation is generated from the reStructuredText docstrings of each
module, function or class.

In order to find module information, an 'info.py' module is expected at the
root of the module with mandatory keys:

    * NAME: the name of the module.
    * DESCRIPTION: the module short description that will be displayed in the
      banner.
    * LONG_DESCRIPTION: the index page content.
    * URL: the module URL.
    * AUTHOR: the author of the module.
    * AUTHOR_EMAIL: the author e-mail.
    * __version__: the module version.

And optional keys:

    * EXTRANAME: a name that will be displayed in the last element of the
      navbar (default 'PYSPHINXDOC').
    * EXTRAURL: the associated URL (default the pySphinxDoc URL).

