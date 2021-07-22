##########################################################################
# pysphinxdoc - Copyright (C) AGrigis, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" Provide a 'DocHelperWriter' class to generate the Sphinx complient
documentation of a module.
"""

# System import
import os
import sys
import re
import shutil
import warnings
import textwrap
import collections
from pprint import pprint
from docutils.core import publish_parts
import importlib
import datetime
import inspect

# Package import
from .utils import examplify


class DocHelperWriter(object):
    """ A basic class to create the Sphinx complient documentation of a module.
    """
    mandatory_fields = {
        "NAME": "the name of the module",
        "DESCRIPTION": ("the module short description that will be displayed "
                        "in the banner"),
        "SUMMARY": "a summary displayed with the carousel",
        "LONG_DESCRIPTION": "the index page content",
        "URL": "the module URL",
        "AUTHOR": "the author of the module",
        "AUTHOR_EMAIL": "the author e-mail",
        "__version__": "the module version"
    }
    optional_fields = {
        "EXTRANAME": ("a name that will be displayed in the last element "
                      "of the navbar (default 'PYSPHINXDOC')"),
        "EXTRAURL": "the associated URL (default the pySphinxDoc URL)"
    }

    def __init__(self, path_module, outdir, module_names, root_module_name,
                 generate_examples=False, rst_extension=".rst", verbose=0):
        """ Initialize the DocHelperWriter class.

        Parameters
        ----------
        path_module : str (mandatory)
            the path to the module to be documented.
        outdir : str (mandatory)
            the path where the documentation will be generated. Expect a
            '$outdir/source/_static' folder containing a logo named
            '$name_module.png' and an 'carousel' subfolder containing a list
            of images to be displayed in the banner.
        module_names : list of str (mandatory)
            List of modules defined in the project (ie. the output of
            'setuptools.find_packages')
        root_module_name : str (mandatory)
            The name of the python package to be documented.
        generate_examples: bool (optional, default False)
            If set, generates the gallery examples from the package scripts.
        rst_extension : string (optional)
            Extension for reST files, default '.rst'.
        verbose : int (optional)
            The verbosity level, default 0.
        """
        # Load the module to be documented
        importlib.import_module(root_module_name)
        module = sys.modules[root_module_name]

        # Generate destination folders
        self.outdir = outdir
        self.srcdir = os.path.join(outdir, "source")
        if not os.path.isdir(self.srcdir):
            shutil.copytree(
                os.path.join(path_module, "doc", "source"), self.srcdir)
        self.staticdir = os.path.join(self.srcdir, "_static")
        self.generateddir = os.path.join(self.srcdir, "generated")
        self.layoutdir = os.path.join(self.generateddir, "_templates")
        self.carouselpath = os.path.join(self.staticdir, "carousel")
        self.modulepath = path_module
        self.generate_examples = generate_examples
        self.infopath = os.path.join(module.__path__[0], "info.py")
        self.logo = os.path.join(self.staticdir, root_module_name + ".png")
        if not os.path.isfile(self.infopath):
            raise IOError("'{0}' is not a valid description file.".format(
                self.infopath))
        if not os.path.isfile(self.logo):
            raise IOError("Specify a '{0}' logo file.".format(self.logo))
        if os.path.isdir(self.generateddir):
            raise IOError(
                "'{0}' already created, can't delete it automatically. Use "
                "the generated Makefile to generate the documentation using "
                "the 'make raw-html' command or to regenerated the "
                "documentation using the 'make html' command.".format(
                    self.generateddir))
        if not os.path.isdir(self.carouselpath):
            raise IOError("{0} is not a valid folder.".format(self.staticdir))
        os.mkdir(self.generateddir)
        os.mkdir(self.layoutdir)

        # Load the module description
        release_info = {}
        with open(self.infopath) as open_file:
            exec(open_file.read(), release_info)
        errors = set(self.mandatory_fields.keys()) - set(release_info.keys())
        warns = set(self.optional_fields.keys()) - set(release_info.keys())
        if len(errors) > 0:
            raise IOError("Missing mandatory fields {0} in '{1}'.".format(
                errors, self.infopath))
        if len(warns) > 0:
            warnings.warn("Missing optional fields {0} in '{1}'.".format(
                warns, self.infopath))

        # Instance parameters
        self.module_names = module_names
        self.module_members = {}
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
        rst = textwrap.dedent(rst).strip()
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

    def write_sphinx_config(self):
        """ Generate the Sphinx configuration.
        """
        # Welcome message
        if self.verbose > 0:
            print("[info] Generating configuration in {0}...".format(
                self.srcdir))

        # Create config maping
        conf_info = {
            "MODULE": self.root_module_name,
            "YEAR": str(datetime.datetime.now().year),
            "AUTHOR": self.release_info["AUTHOR"],
            "AUTHOR_EMAIL": self.release_info["AUTHOR_EMAIL"],
            "VERSION": self.release_info["__version__"],
            "SRCDIR": self.srcdir,
            "PYSPHINXDOCDIR": os.path.dirname(__file__),
            "NAME": self.release_info["NAME"],
            "MODULE_NAME": self.root_module_name,
            "MODULE_PATH": self.modulepath,
            "OUTDIR": self.outdir
        }

        # Start writting the Makefile
        template_make_file = os.path.join(
            os.path.dirname(__file__), "resources", "Makefile")
        make_file = os.path.join(os.path.dirname(self.srcdir), "Makefile")
        self.write_from_template(make_file, template_make_file, conf_info)

        # Start writting the conf
        template_conf_file = os.path.join(
            os.path.dirname(__file__), "resources", "conf.py")
        conf_file = os.path.join(self.srcdir, "conf.py")
        self.write_from_template(conf_file, template_conf_file, conf_info)

    def write_layout(self):
        """ Generate the Sphinx layout.
        """
        # Welcome message
        if self.verbose > 0:
            print("[info] Generating layout in {0}...".format(self.layoutdir))

        # Top selection panel
        indices = [
            """<li><a href="{{{{ pathto('generated/{0}') }}}}">"""
            """{1}</a></li>""".format(x, self.title_for(x))
            for x in self.module_names]

        # Carousel items
        carousel_items = [item for item in os.listdir(self.carouselpath)]
        if len(carousel_items) == 0:
            raise IOError("No data found in folder '{0}'.".format(
                self.carouselpath))
        images = []
        for cnt, item in enumerate(carousel_items):
            images.append(
                """<img src="{{ pathto('_static/carousel/%s', 1) }}"""
                """">""" % item)
        sections = []
        for item in self.module_names:
            sections.append(
                """<li><a href="{{pathto('generated/%s')}}">""" % item +
                """%s</a></li>""" % item)
        links = []
        for key, val in (self.release_info.get("LINKS") or {}).items():
            links.append("<li><a href='{1}'>{0}</a></li>".format(key, val))
        if len(links) > 0:
            links.insert(0, "<li>LINKS</li>")

        # Create layout maping
        pysphinxdoc_info = {}
        info_file = os.path.join(os.path.dirname(__file__), "info.py")
        with open(info_file) as open_file:
            exec(open_file.read(), pysphinxdoc_info)
        layout_info = {
            "NAME_LOWER": self.root_module_name,
            "NAME_UPPER": self.root_module_name.upper(),
            "INDEX": "\n".join(indices),
            "CAROUSEL_IMAGES": "\n".join(images),
            "DESCRIPTION": self.rst2html(self.release_info["DESCRIPTION"]),
            "SUMMARY": self.rst2html(self.release_info["SUMMARY"]),
            "LOGO": self.root_module_name,
            "URL": self.release_info["URL"],
            "EXTRAURL": (self.release_info.get("EXTRAURL") or
                         pysphinxdoc_info["URL"]),
            "EXTRANAME": self.release_info.get("EXTRANAME") or "PYSPHINXDOC",
            "SECTIONS": "".join(sections),
            "LINKS": "".join(links)
        }

        # Start writting the layout
        template_layout_file = os.path.join(
            os.path.dirname(__file__), "resources", "layout.html")
        layout_file = os.path.join(self.layoutdir, "layout.html")
        self.write_from_template(layout_file, template_layout_file,
                                 layout_info)

    def write_index(self):
        """ Generate the index page.
        """
        # Welcome message
        if self.verbose > 0:
            print("[info] Generating index in {0}.".format(self.srcdir))

        # Create correspondance mapping
        index_info = {
            "MODULE": self.root_module_name,
            "DESCRIPTION": self.release_info["LONG_DESCRIPTION"]
        }

        # Start writting the index
        template_index_file = os.path.join(
            os.path.dirname(__file__), "resources", "index.rst")
        index_file = os.path.join(self.srcdir, "index.rst")
        self.write_from_template(index_file, template_index_file, index_info)

    def write_installation(self, pypi_index=None):
        """ Generate the installation recommendations.

        Parameters
        ----------
        pypi_index: str default None
            set the pypi index of the module: useful if different from the
            module name.
        """
        # Welcome message
        if self.verbose > 0:
            print("[info] Generating installation in {0}.".format(
                self.generateddir))

        # Generate title
        title = "Installing `{0}`".format(self.root_module_name)
        title = [self.rst_section_levels[1] * len(title), title,
                 self.rst_section_levels[1] * len(title)]

        # Create correspondance mapping
        install_info = {
            "NAME_LOWER": pypi_index or self.root_module_name,
            "NAME_UPPER": self.root_module_name.upper(),
            "TITLE": "\n".join(title),
            "URL": self.release_info["URL"]
        }

        # Start writting the installation
        template_install_file = os.path.join(
            os.path.dirname(__file__), "resources", "installation.rst")
        install_file = os.path.join(self.generateddir, "installation.rst")
        self.write_from_template(install_file, template_install_file,
                                 install_info)

    def write_gallery(self):
        """ Copy the example folder in the package to be documentated.
        """
        example_dir = os.path.join(self.modulepath, "examples")
        doc_example_dir = os.path.join(self.outdir, "examples")
        if os.path.isdir(example_dir):
            shutil.copytree(example_dir, doc_example_dir)
        elif self.generate_examples:
            if not os.path.isdir(doc_example_dir):
                os.makedirs(doc_example_dir)
            index = os.path.join(doc_example_dir, "README.txt")
            with open(index, "wt") as openfile:
                header = "{0} usage examples".format(self.root_module_name)
                openfile.write(header + "\n")
                openfile.write("=" * len(header) + "\n\n")
                openfile.write(".. contents:: **Contents**\n")
                openfile.write("    :local:\n")
                openfile.write("    :depth: 1\n\n")
                openfile.write("Tutorial examples\n")
                openfile.write("-" * 17 + "\n\n")
            for script in self.release_info["SCRIPTS"]:
                script_file = os.path.join(self.modulepath, script)
                basename = os.path.basename(script_file)
                if not basename.endswith(".py"):
                    basename += ".py"
                dstfile = os.path.join(doc_example_dir, basename)
                examplify(script_file, dstfile)
        else:
            raise ValueError(
                "No gallery examples provided. Please generate this folder or "
                "use the '-e' option.")

    def write_documentation_index(self):
        """ Generate the documentation index.
        """
        # Welcome message
        if self.verbose > 0:
            print("[info] Generating documentation index in {0}.".format(
                self.generateddir))

        # Get full output filename path
        path = os.path.join(self.generateddir,
                            "documentation" + self.rst_extension)

        # Start writing the documentation index
        if self.verbose > 1:
            print("[debug] Generating file {0}.".format(path))
        with open(path, "wt") as open_file:
            w = open_file.write

            # Header
            w(".. AUTO-GENERATED FILE -- DO NOT EDIT!\n\n")
            title = "API documentation of {0}\n".format(
                self.root_module_name.upper())
            w(title)
            w(self.rst_section_levels[1] * len(title) + "\n\n")

            # Recommandations
            w("This is the classes and functions reference in {0}. Please "
              "refer to the gallery for further details, as the class and "
              "function raw specifications may not be enough to give full "
              "guidelines on their uses.\n\n".format(self.root_module_name))

            # Get modules content
            content = {}
            for module_name in self.module_names:
                data = self.module_members.get(module_name)
                if data is None:
                    content[module_name] = []
                    continue
                _content = []
                for key1, item1 in data.items():
                    for key2, item2 in item1.items():
                        for path, (rpath, _) in item2.items():
                            _content.append((path, rpath))
                content[module_name] = _content

            # Modules
            w(".. raw:: html\n\n")
            w("    <!-- Block section -->\n\n")
            w("    <div class='container-fluid'>\n\n")
            w("    <div class='float-left'>\n\n")
            w("    <div class='row'>\n\n")
            for cnt, module_name in enumerate(self.module_names):
                w(self.generate_documentation_index_entry(module_name))
                if (cnt + 1) % 3 == 0:
                    w("\n    </div>")
                    w("\n    <div class='row'>")
            w("\n    </div>")
            w("\n    </div>")
            w("\n    </div>\n\n")

            # Add the list of modules
            w(".. rst-class:: documentation-contents\n\n")
            w("  **Contents**:\n")
            for cnt, module_name in enumerate(self.module_names):
                _content = content[module_name]
                w("    * `{0} <{0}.html>`_\n".format(module_name))
                if len(_content) > 0:
                    w("        .. hidden-technical-block::\n")
                    w("          :label: [+ show/hide members]\n")
                    w("          :starthidden: true\n\n")
                    for path, rpath in _content:
                        w("          `{0} <{1}.html>`_\n\n".format(
                            path, rpath))
            w("\n")

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
        ad = spacer + "<div class='col-md-4'>\n"
        ad += spacer + "<h3><a href='{0}.html'>\n".format(module_name)
        ad += spacer + "{0}\n".format(module_name)
        ad += spacer + "</a></h3>\n"
        ad += spacer + "<blockquote>\n"
        if description is not None:
            ad += spacer + self.rst2html(description, indent=indent)
        ad += spacer + "</blockquote>\n"
        ad += spacer + "</div>\n"

        return ad

    def getmembers(self, mod):
        """ Return the members of a module.
        """
        mod_name = mod.__name__
        add_members = []
        if hasattr(mod, "__all__"):
            add_members = mod.__all__
        funcs = dict(
            (key, ("{0}.{1}".format(val.__module__, key), val))
            for key, val in inspect.getmembers(mod, inspect.isfunction)
            if key in add_members or val.__module__.startswith(mod_name))
        classes = dict(
            (key, ("{0}.{1}".format(val.__module__, key), val))
            for key, val in inspect.getmembers(mod, inspect.isclass)
            if key in add_members or val.__module__.startswith(mod_name))
        unique_functions = set()
        unique_classes = set()
        members = {"classes": classes, "functions": funcs}
        for name, struct in members.items():
            _struct = {}
            for key, val in struct.items():
                if name == "functions":
                    unique_functions.add(val[0])
                else:
                    unique_classes.add(val[0])
                if key in add_members:
                    mkey = "{0}.{1}".format(mod_name, key)
                else:
                    mkey = "{0}.{1}".format(val[1].__module__, key)
                _struct[mkey] = val
            members[name] = collections.OrderedDict(sorted(_struct.items()))
        return members, unique_functions, unique_classes

    def write_api_docs(self, indent=4):
        """ Generate API reST files.

        Parameters
        ----------
        indent: int
            The number of blank prefix.
        """
        # Welcome message
        if self.verbose > 0:
            print("[info] Generating documentation index in {0}.".format(
                self.generateddir))

        # Path written into index is relative to rootpath
        outdir = self.generateddir.rstrip(os.path.sep)
        relpath = outdir.replace(self.generateddir, "")

        # Generate reST API of each module
        for module_name in self.module_names:

            # Import the module
            importlib.import_module(module_name)
            module = sys.modules[module_name]
            mod_members = {}
            members, unique_functions, unique_classes = self.getmembers(module)
            mod_members[module_name] = members
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
                    members, sub_functions, sub_classes = self.getmembers(
                        submodule)
                    mod_members[submodule_name] = members
                    unique_functions = unique_functions.union(sub_functions)
                    unique_classes = unique_classes.union(sub_classes)
                    subdescription = submodule.__doc__ or ""
                    submodules_list.append((submodule_name, subdescription))
            self.module_members[module_name] = mod_members

            # Write module & submodule API doc to file
            if self.verbose > 1:
                print("[debug] Unique functions: {0}.".format(
                    unique_functions))
                print("[debug] Unique classes: {0}.".format(
                    unique_classes))
            for klass in unique_classes:
                outfile = os.path.join(outdir, klass + self.rst_extension)
                if self.verbose > 1:
                    print("[debug] Generating file {0}.".format(outfile))
                with open(outfile, "wt") as open_file:
                    w = open_file.write

                    # Add header to tell us that this documentation must
                    # not be edited
                    w(".. AUTO-GENERATED FILE -- DO NOT EDIT!\n\n")
                    w(":orphan:\n\n")

                    w(".. autoclass:: {0}\n".format(klass))
                    w("     :members:\n\n")
            for func in unique_functions:
                outfile = os.path.join(outdir, func + self.rst_extension)
                if self.verbose > 1:
                    print("[debug] Generating file {0}.".format(outfile))
                with open(outfile, "wt") as open_file:
                    w = open_file.write

                    # Add header to tell us that this documentation must
                    # not be edited
                    w(".. AUTO-GENERATED FILE -- DO NOT EDIT!\n\n")
                    w(":orphan:\n\n")

                    w(".. autofunction:: {0}\n\n".format(func))

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
                title = "API documentation of *{0}*\n".format(module_name)
                w(title)
                w(self.rst_section_levels[1] * len(title) + "\n\n")

                # Add the list of members
                for mod_name, desc in (
                        [(module_name, description)] + submodules_list):
                    kdata = mod_members[mod_name]["classes"]
                    fdata = mod_members[mod_name]["functions"]
                    w("{0}\n".format(mod_name))
                    w(self.rst_section_levels[4] * len(mod_name) + "\n\n")
                    w("{0}\n\n".format(desc))
                    if len(kdata) > 0 or len(fdata) > 0:
                        w(".. rst-class:: documentation-contents\n\n")
                    if len(kdata) > 0:
                        w("  **Classes**:\n")
                        for klass, (rklass, _) in kdata.items():
                            w("    * `{0} <{1}.html>`_\n".format(
                                klass, rklass))
                        w("\n")
                    if len(fdata) > 0:
                        w("  **Functions**:\n")
                        for func, (rfunc, _) in fdata.items():
                            w("    * `{0} <{1}.html>`_\n".format(
                                func, rfunc))
                        w("\n")
