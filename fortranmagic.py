# -*- coding: utf-8 -*-
"""
=====================
Fortran 90/f2py magic
=====================

{FORTRAN_DOC}



Author:
* Martín Gaitán <gaitan@gmail.com>

This code was heavily inspired in the Cython magic
"""

from __future__ import print_function

import imp
import io
import os
import sys

try:
    import hashlib
except ImportError:
    import md5 as hashlib

from IPython.core.error import UsageError
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.core import display, magic_arguments
from IPython.utils import py3compat
from IPython.utils.io import capture_output
from IPython.utils.path import get_ipython_cache_dir
from numpy.f2py import f2py2e
from numpy.distutils import fcompiler
from distutils.core import Distribution
from distutils.ccompiler import compiler_class
from distutils.command.build_ext import build_ext

fcompiler.load_all_fcompiler_classes()

@magics_class
class FortranMagics(Magics):


    allowed_fcompilers = sorted(fcompiler.fcompiler_class.keys())
    allowed_compilers = sorted(compiler_class.keys())

    def __init__(self, shell):
        super(FortranMagics, self).__init__(shell)
        self._reloads = {}
        self._code_cache = {}
        self._lib_dir = os.path.join(get_ipython_cache_dir(), 'fortran')


    def _import_all(self, module):
        for k, v in module.__dict__.items():
            if not k.startswith('__'):
                self.shell.push({k: v})

    def _run_f2py(self, argv, show_captured=False):
        """
        Here we directly call the numpy.f2py.f2py2e.run_compile() entry point,
        after some small amount of setup to get sys.argv and the current
        working directory set appropriately.
        """
        old_argv = sys.argv
        old_cwd = os.getcwdu() if sys.version_info[0] == 2 else os.getcwd()
        try:
            sys.argv = ['f2py'] + argv
            os.chdir(self._lib_dir)
            try:
                with capture_output() as captured:
                    f2py2e.main()
                if show_captured:
                    captured()
            except SystemExit as e:
                captured()
                raise UsageError(str(e))
        finally:
            sys.argv = old_argv
            os.chdir(old_cwd)

    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        '--help-link', default='all', required=False,
        help="""List system resources found by system_info.py.
                Optionally give a resource name.
                E.g. try '--help-link lapack_opt.

                See alsof
                %%fortran --link <resource> switch.
                """
    )
    @magic_arguments.argument(
        '--help-fcompiler', action="store_true",
        help="List available Fortran compilers",
    )
    @magic_arguments.argument(
        '--help-compiler', action="store_true",
        help="List available C compilers",
    )
    @line_magic
    def f2py(self, line):
        args = magic_arguments.parse_argstring(self.f2py, line)
        if args.help_fcompiler:
            self._run_f2py(['-c', '--help-fcompiler'], True)
        elif args.help_compiler:
            self._run_f2py(['-c', '--help-compiler'], True)
        elif len(args.help_link) == 0:
            self._run_f2py(['--help-link'])
        elif len(args.help_link) > 0:
            self._run_f2py(['--help-link', args.help_link], True)


    @property
    def so_ext(self):
        """The extension suffix for compiled modules."""
        try:
            return self._so_ext
        except AttributeError:

            dist = Distribution()
            config_files = dist.find_config_files()
            try:
                config_files.remove('setup.cfg')
            except ValueError:
                pass
            dist.parse_config_files(config_files)
            build_extension = build_ext(dist)
            build_extension.finalize_options()
            self._so_ext = build_extension.get_ext_filename('')
            return self._so_ext

# __doc__ = __doc__.format(FORTRAN_DOC=' ' * 8 + FortranMagics.fortran.__doc__)


def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(FortranMagics)

    # enable fortran highlight
    patch = ("IPython.config.cell_magic_highlight['magic_fortran'] = {'reg':[/^%%fortran/]};")
    js = display.Javascript(data=patch,
                            lib=["https://raw.github.com/marijnh/CodeMirror/master/mode/fortran/fortran.js"])
    display.display_javascript(js)
