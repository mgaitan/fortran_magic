# -*- coding: utf-8 -*-
"""
=====================
Fortran 90/f2py magic
=====================

{FORTRAN_DOC}



Author:
* Martín Gaitán <gaitan@gmail.com>
"""

from __future__ import print_function

import errno
import hashlib
import io
import os
import random
import shutil
import sys
from distutils.ccompiler import compiler_class
from distutils.command.build_ext import build_ext
from distutils.core import Distribution
from distutils.version import LooseVersion
from subprocess import PIPE, Popen

import numpy as np
from IPython.core import display, magic_arguments
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
from IPython.paths import get_ipython_cache_dir
from IPython.utils import py3compat
from IPython.utils.io import capture_output
from numpy.f2py import f2py2e

__version__ = '0.9'

try:
    from numpy.distutils import fcompiler

    _use_meson = False
    fcompiler.load_all_fcompiler_classes()
except ImportError:
    _use_meson = True

try:
    import importlib.machinery
    import importlib.util

    def _imp_load_dynamic(name, path):
        loader = importlib.machinery.ExtensionFileLoader(name, path)
        spec = importlib.machinery.ModuleSpec(name=name, loader=loader,
                                              origin=path)
        return importlib.util.module_from_spec(spec)
except ImportError:
    import imp

    def _imp_load_dynamic(name, path):
        return imp.load_dynamic(name, path)


def compose(*decorators):
    """Helper to compose decorators::

        @a
        @b
        def f():
            pass

    Is equivalent to::

        @compose(a, b)
        def f():
            ...
    """
    def composed(f):
        for decor in reversed(decorators):
            f = decor(f)
        return f
    return composed


def unquote(v):
    if ((v.startswith('"') and v.endswith('"')) or
            (v.startswith("'") and v.endswith("'"))):
        return v[1:-1]
    return v


@magics_class
class FortranMagics(Magics):

    if _use_meson:
        allowed_fcompilers = None
    else:
        allowed_fcompilers = sorted(fcompiler.fcompiler_class.keys())
    allowed_compilers = sorted(compiler_class.keys())

    my_magic_arguments = compose(
        magic_arguments.magic_arguments(),
        magic_arguments.argument(
            "-v", "--verbosity", action="count", default=0,
            help="increase output verbosity"
        ),
        magic_arguments.argument(
            '--backend',
            choices=['distutils', 'meson'],
            help="""Specify the build backend for the compilation
                 process. On Python 3.12 or higher, the default is
                 'meson', see numpy.f2py documentation for details.
                 [TODO, unimplemented]"""  # TODO:XXX
        ),
        magic_arguments.argument(
            '--fcompiler',
            choices=allowed_fcompilers,
            help="""Specify Fortran compiler type by vendor.
                 See %%f2py_help --fcompiler. [NO_MESON]""",
        ),
        magic_arguments.argument(
            '--compiler',
            choices=allowed_compilers,
            help="""Specify C compiler type (as defined by distutils).
                    See %%f2py_help --compiler.  [NO_MESON]"""
        ),
        magic_arguments.argument(
            '--f90flags', help="Specify F90 compiler flags"
        ),
        magic_arguments.argument(
            '--f77flags', help="Specify F77 compiler flags"
        ),
        magic_arguments.argument(
            '--opt', help="Specify optimization flags. [NO_MESON]"
        ),
        magic_arguments.argument(
            '--arch',
            help="""Specify architecture specific optimization flags.
                 [NO_MESON]"""
        ),
        magic_arguments.argument(
            '--noopt', action="store_true",
            help="Compile without optimization. [NO_MESON]"
        ),
        magic_arguments.argument(
            '--noarch', action="store_true",
            help="""Compile without arch-dependent optimization.
                 [NO_MESON]"""
        ),
        magic_arguments.argument(
            '--debug', action="store_true",
            help="Compile with debugging information"
        ),
        magic_arguments.argument(
            '--link', action='append', default=[],
            help="""Link extension module with LINK resource, as defined
                    by numpy.distutils/system_info.py. E.g. to link
                    with optimized LAPACK libraries (vecLib on MacOSX,
                    ATLAS elsewhere), use --link lapack_opt.
                    See also %%f2py_help --resources switch."""
        ),
        magic_arguments.argument(
            '--extra', action='append', default=[],
            help="""Use --extra to pass any other argument in the f2py call. For example
                    --extra '-L/path/to/lib/ -l<libname>'
                    --extra '-D<define> -U<name>'
                    --extra '-DPREPEND_FORTRAN -DUPPERCASE_FORTRAN'
                    etc. """
        ),
        magic_arguments.argument(
            '--add-hash', action='append', default=[],
            help="Additional string to hash of code, flags, etc."
        ),
        )

    def _cache_init(self):
        """Create random cache directory."""

        while True:
            cdir = os.path.join(get_ipython_cache_dir(),
                                'fortranmagic',
                                "%08x" % random.getrandbits(32))
            try:
                os.makedirs(cdir)
                break
            except OSError:
                pass
        self.shell.db['fortranmagic_cache'] = cdir
        self._lib_dir = cdir

    def _cache_open(self):
        """Open cache directory on session start"""

        try:
            cdir = self.shell.db['fortranmagic_cache']
            if os.path.isdir(cdir):
                self._lib_dir = cdir
                return
        except (KeyError, OSError):
            pass
        self._cache_init()

    def _cache_check(self):
        """Check cache directory.

        If the parallel session executed `__cache_init()`, then the
        current session still continues to use the old directory (the
        one that was considered at the start).
        """

        if not os.path.isdir(self._lib_dir):
            try:
                os.makedirs(self._lib_dir)
            except OSError:
                self._cache_init()

    def _cache_clean(self):
        shutil.rmtree(os.path.join(get_ipython_cache_dir(),
                                   'fortranmagic'),
                      ignore_errors=True)
        self._cache_init()

    def __init__(self, shell):
        super(FortranMagics, self).__init__(shell=shell)
        self._reloads = {}
        self._code_cache = {}
        self._cache_open()

    def _import_all(self, module, verbosity=0, code=''):
        imported = []
        for k, v in module.__dict__.items():
            if not k.startswith('__'):
                v.__source__ = code
                self.shell.push({k: v})
                imported.append(k)
        if verbosity > 0 and imported:
            print("\nOk. The following fortran objects "
                  "are ready to use: %s" % ", ".join(imported))

    def _run_f2py(self,
                  argv,
                  show_captured=False,
                  verbosity=0,
                  fflags=None):
        """
        Here we directly call the numpy.f2py module or the f2py executable.
        """
        environ = None if fflags is None else os.environ.copy()
        if fflags is not None:
            environ = os.environ.copy()
            environ['FFLAGS'] = environ.get('FFLAGS', '') + ' ' + fflags
        else:
            environ = None

        if np.__version__ < LooseVersion('1.10.0'):
            if sys.version_info[0] >= 3:
                command = ['f2py3']
            else:
                command = ['f2py']
        else:
            command = [sys.executable, '-m', 'numpy.f2py']
        command += map(str, argv)

        if verbosity > 1:
            print("Running...\n   %s" % ' '.join(command))

        p, out, err = None, None, None
        try:
            with capture_output() as captured:
                # subprocess.call(command)
                # Refactor subprocess call to work with jupyterhub
                try:
                    p = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE,
                              env=environ,
                              cwd=self._lib_dir)
                except OSError as e:
                    if e.errno == errno.ENOENT:
                        print("Couldn't find program: %r" % command[0])
                        return -1
                    raise
                out, err = p.communicate(input=None)
        finally:
            if show_captured or verbosity > 2 or p is None or p.returncode:
                if err:
                    sys.stderr.write(err.decode())
                    sys.stderr.flush()
                if out:
                    sys.stdout.write(out.decode())
                    sys.stdout.flush()
                captured()

        return p.returncode

    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        '--resources', action="store_true",
        help="""List system resources found by system_info.py.

                See also
                %%f2py_help --link <resource> switch.
                """
    )
    @magic_arguments.argument(
        '--link',
        help="""Given a resource name, show what it foun.
                E.g. try '--link lapack.

                See also
                %%f2py_help --link <resource> switch.
                """
    )
    @magic_arguments.argument(
        '--fcompiler', action="store_true",
        help="List available Fortran compilers",
    )
    @magic_arguments.argument(
        '--compiler', action="store_true",
        help="List available C compilers",
    )
    @line_magic
    def f2py_help(self, line):
        args = magic_arguments.parse_argstring(self.f2py_help, line)
        if args.fcompiler:
            self._run_f2py(['-c', '--help-fcompiler'], True)
        elif args.compiler:
            self._run_f2py(['-c', '--help-compiler'], True)
        elif args.resources:
            self._run_f2py(['--help-link'], True)
        elif args.link:
            self._run_f2py(['--help-link', args.link], True)

    @my_magic_arguments
    @magic_arguments.argument(
        '--defaults', action="store_true", help="Delete custom configuration "
        "and back to default"
    )
    @magic_arguments.argument(
        '--clean-cache', action="store_true", help="Clean fortran modules "
        "build cache"
    )
    @line_magic
    def fortran_config(self, line):
        """
        View and handle the custom configuration for %%fortran magic.

            %fortran_config

                Show the current custom configuration

            %fortran_config --clean-cache

                Clean fortran modules build cache

            %fortran_config --defaults

                Delete the current configuration and back to defaults

            %fortran_config <other options>

                Save <other options> to use with %%fortran
        """

        args = magic_arguments.parse_argstring(self.fortran_config, line)
        if args.clean_cache:
            print("Clean cache:", self._lib_dir)
            self._cache_clean()
            if args.verbosity >= 1:
                print("New cache:", self._lib_dir)
        elif args.defaults:
            try:
                del self.shell.db['fortranmagic']
                print("Deleted custom config. Back to default arguments for %%fortran")
            except KeyError:
                print("No custom config found for %%fortran")
        elif not line:
            try:
                line = self.shell.db['fortranmagic']
                print("Current defaults arguments for %%fortran:\n\t%s" % line)
            except KeyError:
                print("No custom config found for %%fortran")
        else:
            self.shell.db['fortranmagic'] = line
            print("New default arguments for %%fortran:\n\t%s" % line)

    @my_magic_arguments
    @cell_magic
    def fortran(self, line, cell):
        """Compile and import everything from a Fortran code cell, using f2py.

        The content of the cell is written to a `.f90` file in the
        directory `IPYTHONDIR/fortran` using a filename with the hash of
        the code, flags and configuration data. This file is then
        compiled. The resulting module is imported and all of its
        symbols are injected into the user's namespace.


        Usage
        =====
        Prepend ``%%fortran`` to your fortran code in a cell::

        ``%%fortran

        ! put your code here.
        ``


        """

        # verbosity is a "count" argument were each ocurrence is
        # added implicit.
        # so, for instance, -vv in %fortran_config and -vvv in %%fortran means
        # a nonsense verbosity=5.
        # To override: if verbosity is given for the magic cell
        # we ignore the saved config.
        args = magic_arguments.parse_argstring(self.fortran, line)
        f_config = self.shell.db.get('fortranmagic', "")
        if f_config:
            sverbosity = args.verbosity
            args = magic_arguments.parse_argstring(self.fortran,
                                                   f_config + " " + line)
            if sverbosity > 0:
                args.verbosity = sverbosity

        # boolean flags
        f2py_args = ['--%s' % k for k, v in vars(args).items() if v is True]

        try:
            base_str_class = basestring
        except NameError:
            # py3
            base_str_class = str

        kw = ['--%s=%s' % (k, v) for k, v in vars(args).items()
              if isinstance(v, base_str_class)]

        f2py_args.extend(kw)

        # link resource
        if args.link:
            # TODO: Now `f2py --backend meson` unimplemented
            if not _use_meson:
                resources = ['--link-%s' % r for r in args.link]
            else:
                resources = []
                for r in args.link:
                    resources.append('--dep')
                    resources.append(r)
            f2py_args.extend(resources)

        if args.extra:
            extras = ' '.join(map(unquote, args.extra))
            extras = extras.split()
            f2py_args.extend(extras)

        code = cell if cell.endswith('\n') else cell + '\n'
        self._cache_check()
        key = (code, line, f_config,
               self._lib_dir,
               sys.version_info, sys.executable, f2py2e.f2py_version)

        module_name = "_fortran_magic_" + \
                      hashlib.md5(str(key).encode('utf-8')).hexdigest()

        if module_name in sys.modules:
            module = sys.modules[module_name]
            print("The extension", module_name,
                  "is already loaded. To reload it, use:")
            print("  %fortran_config --clean-cache")
        else:
            module_path = os.path.join(self._lib_dir, module_name + self.so_ext)

            fsuffix = ".f90"

            # TODO: Now `f2py --backend meson` unimplemented
            if not _use_meson:
                fflags = None
            else:
                # `--f77flags` & `--f90flags`. Use `FFLAGS` workaround, see
                # https://github.com/numpy/numpy/issues/24874#issuecomment-1762981664
                # https://github.com/numpy/numpy/issues/24874

                if args.f77flags is not None:
                    fflags = args.f77flags
                else:
                    fflags = args.f90flags
                if args.f77flags is not None and args.f90flags is not None:
                    # TODO: f2py used requiresf90wrapper()
                    print("Warning: ambiguity, both f77flags and f90flags "
                          "are set, assume the %s module" % (
                              "f77" if fflags == args.f77flags else "f90"),
                          file=sys.stderr)
                lfflags = unquote(fflags).split() if fflags is not None else []
                fflags = ""
                for flag in lfflags:
                    if flag == "-ffixed-form":
                        fsuffix = ".f"
                    elif flag == "-ffree-form":
                        fsuffix = ".f90"
                    else:
                        fflags += flag + " "
                if fflags and ' ' == fflags[-1]:
                    fflags = fflags[:-1]

            f_f90_file = os.path.join(self._lib_dir, module_name + fsuffix)
            f_f90_file = py3compat.cast_bytes_py2(
                            f_f90_file,
                            encoding=sys.getfilesystemencoding())
            with io.open(f_f90_file, 'w', encoding='utf-8') as f:
                f.write(code)

            res = self._run_f2py(f2py_args + ['-m', module_name, '-c',
                                              f_f90_file],
                                 verbosity=args.verbosity,
                                 fflags=fflags)
            if res != 0:
                raise RuntimeError("f2py failed, see output")

            self._code_cache[key] = module_name
            module = _imp_load_dynamic(module_name, module_path)
        self._import_all(module, verbosity=args.verbosity, code=code)

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


__doc__ = __doc__.format(FORTRAN_DOC=' ' * 8 + FortranMagics.fortran.__doc__)


def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(FortranMagics)

    # enable fortran highlight
    patch = """
        if(typeof IPython === 'undefined') {
            console.log('fortranmagic.py: TDOO: JupyterLab ' +
                        'syntax highlight - unimplemented.');
        } else {
            IPython.CodeCell.options_default
            .highlight_modes['magic_fortran'] = {'reg':[/^%%fortran/]};
        }
        """
    js = display.Javascript(data=patch)
    display.display_javascript(js)
