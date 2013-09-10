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

from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.utils import py3compat
from IPython.utils.path import get_ipython_cache_dir
from numpy.f2py import f2py2e


@magics_class
class FortranMagics(Magics):

    def __init__(self, shell):
        super(FortranMagics, self).__init__(shell)
        self._reloads = {}
        self._code_cache = {}

    def _import_all(self, module):
        for k, v in module.__dict__.items():
            if not k.startswith('__'):
                self.shell.push({k: v})

    @cell_magic
    def fortran(self, line, cell):
        """Compile and import everything from a Fortran code cell, using f2py.

        The contents of the cell are written to a `.f90` file in the
        directory `IPYTHONDIR/fortran` using a filename with the hash of the
        code. This file is then compiled. The resulting module
        is imported and all of its symbols are injected into the user's
        namespace.


        Usage
        =====
        Prepend ``%%fortran`` to your fortran code in a cell::

        ``%%fortran

        ! put your code here.
        ``


        """
        code = cell if cell.endswith('\n') else cell+'\n'
        lib_dir = os.path.join(get_ipython_cache_dir(), 'fortran')
        key = code, sys.version_info, sys.executable, f2py2e.f2py_version

        if not os.path.exists(lib_dir):
            os.makedirs(lib_dir)

        module_name = "_fortran_magic_" + \
                      hashlib.md5(str(key).encode('utf-8')).hexdigest()

        mod_ext = '.pyd' if 'win' in sys.platform.lower() else '.so'
        module_path = os.path.join(lib_dir, module_name + mod_ext)

        f90_file = os.path.join(lib_dir, module_name + '.f90')
        f90_file = py3compat.cast_bytes_py2(f90_file,
                                            encoding=sys.getfilesystemencoding())
        with io.open(f90_file, 'w', encoding='utf-8') as f:
            f.write(code)

        cmd = "f2py -m %s -c %s" % (module_name, f90_file)

        # move to lib_dir temporally
        pwd = os.getcwdu()
        os.chdir(lib_dir)
        self.shell.getoutput(cmd)
        os.chdir(pwd)

        self._code_cache[key] = module_name
        module = imp.load_dynamic(module_name, module_path)
        self._import_all(module)

__doc__ = __doc__.format(FORTRAN_DOC=' ' * 8 + FortranMagics.fortran.__doc__)


def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(FortranMagics)
