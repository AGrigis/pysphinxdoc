##########################################################################
# pysphinxdoc - Copyright (C) AGrigis, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from __future__ import print_function
import os
import sys
import re
from pprint import pprint
from docutils.core import publish_parts
import importlib
import datetime


class DocHelperWriter(object):
    """ A basic class to create the Sphinx documentation of a module.
    """
    def __init__(self, module_names, root_module_name, rst_extension=".rst",
                 verbose=0):
        """ Initialize the DocHelperWriter class

        Parameters
        ----------
        module_names: list of str (mandatory)
            List of modules defined in the project (ie. the output of
            'setuptools.find_packages')
        root_module_name: str (mandatory)
            The name of the python package to be documented.
        rst_extension : string (optional)
            Extension for reST files, default '.rst'.
        verbose : int (optional)
            The verbosity level, default 0.
        """
        # Load module description
        importlib.import_module(root_module_name)
        module = sys.modules[root_module_name]
        release_info = {}
        with open(os.path.join(module.__path__[0], "info.py")) as open_file:
            exec(open_file.read(), release_info)

        # Instance parameters
        self.module_names = module_names
        self.rst_extension = rst_extension
        self.root_module_name = root_module_name
        self.rst_section_levels = ['*', '=', '-', '~', '^']
        self.verbose = verbose
        self.module = module
        self.release_info = release_info

    def title_for(self, title):
        """ Create a title from a underscore-separated string.

        Parameters
        ----------
        title: str (mandatory)
            the string to format.

        Returns
        -------
        out: str
            the formated string.
        """
        return title.replace("_", " ").capitalize()

    def rst2html(self, rst, indent=4):
        """ Convert a reST formated string to a HTML string.

        Parameters
        ----------
        rst: str (mandatory)
            the rst formated string.
        ident: int
            the number of blank prefix.

        Returns
        -------
        out: str
            the html formated string.
        """
        parts = publish_parts(rst, writer_name="html")
        html = parts["body_pre_docinfo"] + parts["body"]
        html = "\n".join([" " * indent + elem for elem in html.splitlines()])
        return html

    def format_with_dict(self, string, dictionary):
        """ Use regular expressions to replace % by %% where % is not followed
        by (.
        Avoid "not enough arguments for format string" errors.

        Parameters
        ----------
        string : str
            a string to be formated.
        dictionary : dict
            a mapping used to edit the input string.
        """
        string = re.sub(r"%([^\(])", r"%%\1", string)
        string = re.sub(r"%$", r"%%", string)
        return string % dictionary

    def write_from_template(self, out_file, template_file, template_info):
        """ Edit/save a template file.

        Parameters
        ----------
        out_file : str
            the location where the edited template file content is written.
        template_file : str
            the location of the template file.
        template_info : dict
            a mapping used to edit the template content.
        """
        if self.verbose > 1:
            print("[debug] Generating file {0} from {1}.".format(
                out_file, template_file))
            pprint(template_info)
        with open(out_file, "wt") as open_file:
            w = open_file.write
            with open(template_file) as template_open_file:
                s = self.format_with_dict(template_open_file.read(),
                                          template_info)
                w(s)

    def write_sphinx_config(self, outdir):
        """ Generate the Sphinx configuration.

        Parameters
        ----------
        outdir : str
            Directory name in which to store generated files.
        """
        # Check if outupt dir exists
        if not os.path.isdir(outdir):
            raise IOError("'{0}' is not a valid directory.".format(outdir))

        # Create config maping
        conf_info = {
            "MODULE": self.root_module_name,
            "YEAR": str(datetime.datetime.now().year),
            "AUTHOR": self.release_info["AUTHOR"],
            "AUTHOR_EMAIL": self.release_info["AUTHOR_EMAIL"],
            "VERSION": self.release_info["__version__"],
            "SRCDIR": outdir,
            "PYSPHINXDOCDIR": os.path.dirname(__file__),
            "NAME": self.release_info["NAME"]
        }

        # Start writting the Makefile
        template_make_file = os.path.join(
            os.path.dirname(__file__), "resources", "Makefile")
        make_file = os.path.join(os.path.dirname(outdir), "Makefile")
        self.write_from_template(make_file, template_make_file, conf_info)

        # Start writting the conf
        template_conf_file = os.path.join(
            os.path.dirname(__file__), "resources", "conf.py")
        conf_file = os.path.join(outdir, "conf.py")
        self.write_from_template(conf_file, template_conf_file, conf_info)

    def write_layout(self, outdir, staticdir):
        """Generate the Sphinx layout.

        Parameters
        ----------
        outdir : str (mandatory)
            Directory name in which to store generated files.
        staticdir : str (mandatory)
            The path to the static images used to display the logo and the
            carousel.
        """
        # Check if outupt dir exists
        if not os.path.isdir(outdir):
            raise IOError("'{0}' is not a valid directory.".format(outdir))

        # Top selection panel
        indices = [
            """<li><a href="{{{{ pathto('generated/{0}') }}}}">"""
            """{1}</a></li>""".format(x, self.title_for(x))
            for x in self.module_names]

        # Carousel items
        carousel_items_path = os.path.join(staticdir, "carousel")
        carousel_items = [item for item in os.listdir(carousel_items_path)]
        images = []
        indicators = []
        for cnt, item in enumerate(carousel_items):
            if cnt == 0:
                indicators.append(
                    "<li data-target='#examples_carousel' data-slide-to='0' "
                    "class='active'></li>")
                images.append(
                    """<div class="active item">"""
                    """<a href="{{pathto('index')}}">"""
                    """<img src="{{ pathto('_static/carousel/%s', 1) }}">"""
                    """</div></a>""" % item)
            else:
                indicators.append(
                    "<li data-target='#examples_carousel' data-slide-to='{0}' "
                    "</li>".format(cnt))
                images.append(
                    """<div class="item"><a href="{{pathto('index')}}">"""
                    """<img src="{{ pathto('_static/carousel/%s', 1) }}">"""
                    """</a></div>""" % item)

        # Create layout maping
        pysphinxdoc_info = {}
        info_file = os.path.join(os.path.dirname(__file__), "info.py")
        with open(info_file) as open_file:
            exec(open_file.read(), pysphinxdoc_info)
        layout_info = {
            "NAME_LOWER": self.root_module_name,
            "NAME_UPPER": self.root_module_name.upper(),
            "INDEX": "\n".join(indices),
            "CAROUSEL_INDICATORS": "\n".join(indicators),
            "CAROUSEL_IMAGES": "\n".join(images),
            "DESCRIPTION": self.rst2html(self.release_info["DESCRIPTION"]),
            "LOGO": self.root_module_name,
            "URL": self.release_info["URL"],
            "EXTRAURL": (self.release_info.get("EXTRAURL") or
                         pysphinxdoc_info["URL"]),
            "EXTRANAME": self.release_info.get("EXTRANAME") or "PYSPHINXDOC"
        }

        # Start writting the layout
        template_layout_file = os.path.join(
            os.path.dirname(__file__), "resources", "layout.html")
        layout_file = os.path.join(outdir, "layout.html")
        self.write_from_template(layout_file, template_layout_file,
                                 layout_info)

    def write_index(self, outdir):
        """ Generate the index page.

        Parameters
        ----------
        outdir : str
            Directory name in which to store generated files.
        """
        # Check if outupt dir exists
        if not os.path.isdir(outdir):
            raise IOError("'{0}' is not a valid directory.".format(outdir))

        # Create correspondance mapping
        index_info = {
            "MODULE": self.root_module_name,
            "DESCRIPTION": self.release_info["LONG_DESCRIPTION"]
        }

        # Start writting the index
        template_index_file = os.path.join(
            os.path.dirname(__file__), "resources", "index.rst")
        index_file = os.path.join(outdir, "index.rst")
        self.write_from_template(index_file, template_index_file, index_info)

    def write_installation(self, outdir):
        """ Generate the installation recommendations.

        Parameters
        ----------
        outdir : str
            Directory name in which to store generated files.
        """
        # Check if outupt dir exists
        if not os.path.isdir(outdir):
            raise IOError("'{0}' is not a valid directory.".format(outdir))

        # Generate title
        title = "Installing `{0}`".format(self.root_module_name)
        title = [self.rst_section_levels[1] * len(title), title,
                 self.rst_section_levels[1] * len(title)]

        # Create correspondance mapping
        install_info = {
            "NAME_LOWER": self.root_module_name,
            "NAME_UPPER": self.root_module_name.upper(),
            "TITLE": "\n".join(title),
            "URL": self.release_info["URL"]
        }

        # Start writting the installation
        template_install_file = os.path.join(
            os.path.dirname(__file__), "resources", "installation.rst")
        install_file = os.path.join(outdir, "installation.rst")
        self.write_from_template(install_file, template_install_file,
                                 install_info)

    def write_documentation_index(self, outdir):
        """ Generate the documentation index.

        Parameters
        ----------
        outdir : str
            Directory name in which to store generated files.
        """
        # Check output directory
        if not os.path.isdir(outdir):
            raise IOError("'{0}' is not a valid directory.".format(outdir))

        # Get full output filename path
        path = os.path.join(outdir, "documentation" + self.rst_extension)

        # Start writing the documentation index
        if self.verbose > 1:
            print("[debug] Generating file {0}.".format(path))
        with open(path, "wt") as open_file:
            w = open_file.write

            # Header
            w(".. AUTO-GENERATED FILE -- DO NOT EDIT!\n\n")
            title = "Documentation of {0}\n".format(
                self.root_module_name.upper())
            w(title)
            w(self.rst_section_levels[1] * len(title) + "\n\n")

            # Modules
            w(".. raw:: html\n\n")
            w("    <!-- Block section -->\n\n")
            for cnt, module_name in enumerate(self.module_names):
                if cnt % 2 == 0:
                    w("    <div class='row-fluid'>\n\n")
                w(self.generate_documentation_index_entry(module_name))
            w("\n    </div>")

    def generate_documentation_index_entry(self, module_name, indent=4):
        """ Generate a new entry in the dicumentation index.

        Parameters
        ----------
        module_name: string
            the name of the module we want to index.
        ident: int
            the number of blank prefix.

        Returns
        -------
        ad : string
            the reST formated index description.
        """
        # Try to get the module description
        importlib.import_module(module_name)
        module = sys.modules[module_name]
        description = module.__doc__

        # Then reST formatting
        spacer = " " * indent
        ad = spacer + "<div class='span6 box'>\n"
        ad += spacer + "<h2><a href='{0}.html'>\n".format(module_name)
        ad += spacer + "{0}\n".format(module_name)
        ad += spacer + "</a></h2>\n"
        ad += spacer + "<blockquote>\n"
        if description is not None:
            ad += spacer + self.rst2html(description, indent=indent)
        ad += spacer + "</blockquote>\n"
        ad += spacer + "</div>\n"

        return ad

    def write_api_docs(self, outdir, relative_to=None, indent=4):
        """ Generate API reST files.

        Parameters
        ----------
        outdir : str
            Directory name in which to store generated files.
        relative_to : str
            Path to which written filenames are relative. Default is None,
            meaning leave path as it is.
        ident: int
            The number of blank prefix.
        """
        # Check output directory
        if not os.path.isdir(outdir):
            raise IOError("'{0}' is not a valid directory.".format(outdir))

        # Path written into index is relative to rootpath
        outdir = outdir.rstrip(os.path.sep)
        if relative_to is not None:
            relpath = outdir.replace(relative_to, "")
        else:
            relpath = outdir

        # Generate reST API of each module
        for module_name in self.module_names:

            # Import the module
            importlib.import_module(module_name)
            module = sys.modules[module_name]
            description = module.__doc__ or ""

            # List all sub modules
            submodules_list = []
            for name in os.listdir(module.__path__[0]):
                submodule_path = os.path.join(module.__path__[0], name)
                submodule_name = module_name + "." + name
                if (submodule_path.endswith(".py") and
                        os.path.isfile(submodule_path) and
                        name not in ["__init__.py", "info.py"]):

                    # Import the submodule
                    submodule_name = submodule_name.replace(".py", "")
                    importlib.import_module(submodule_name)
                    submodule = sys.modules[submodule_name]
                    subdescription = submodule.__doc__ or ""
                    subdescription = self.rst2html(subdescription,
                                                   indent=indent)
                    submodules_list.append((submodule_name, subdescription))

                    # Write submodule API doc to file
                    outfile = os.path.join(outdir,
                                           submodule_name + self.rst_extension)
                    if self.verbose > 1:
                        print("[debug] Generating file {0}.".format(outfile))
                    with open(outfile, "wt") as open_file:
                        w = open_file.write

                        # Add header to tell us that this documentation must
                        # not be edited
                        w(".. AUTO-GENERATED FILE -- DO NOT EDIT!\n\n")
                        w(":orphan:\n\n")

                        w(".. automodule:: {0}\n\n".format(submodule_name))

            # Write module index to file
            outfile = os.path.join(outdir, module_name + self.rst_extension)
            if self.verbose > 1:
                print("[debug] Generating file {0}.".format(outfile))
            with open(outfile, "wt") as open_file:
                w = open_file.write

                # Add header to tell us that this documentation must not be
                # edited
                w(".. AUTO-GENERATED FILE -- DO NOT EDIT!\n\n")
                w(":orphan:\n\n")
                title = "Documentation of *{0}*\n".format(module_name)
                w(title)
                w(self.rst_section_levels[1] * len(title) + "\n\n")

                # Display module description
                w("{0}\n\n".format(description))

                # Generate a table with all the generated submodules
                # submodule_name (link) + first docstring line
                w(".. raw:: html\n\n")
                w(" " * indent + "<br/>")

                # Table definition
                table = ["<!-- Block section -->"]
                table.append(
                    "<table border='1' class='docutils' style='width:100%'>")
                table.append("<colgroup><col width='25%'/><col width='75%'/>"
                             "</colgroup>")
                table.append("<tbody valign='top'>")

                # Add all modules
                for submodule_name, desc in submodules_list:
                    href = os.path.join(relpath, submodule_name + ".html")
                    table.append("<tr class='row-odd'>")
                    table.append(
                        "<td><a class='reference internal' href='{0}'>"
                        "<em>{1}</em></a></td>".format(href, submodule_name))
                    table.append("<td>")
                    table.append(desc)
                    table.append("</td>")
                    table.append("</tr>")

                # Close divs
                table.append("</tbody>\n\n")
                table.append("</table>")

                # Format the table
                table_with_indent = [" " * indent + line for line in table]
                w("\n".join(table_with_indent))
