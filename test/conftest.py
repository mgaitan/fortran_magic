"""
Pytest configuration:
    1. Add `pytest` starting directory for load `fortranmagic.py` and
       compiled testing modules;
    2. Fixture for verbosity level at session start;
    3. Fixture for workaround probable bug `numpy.f2py` on Windows.
"""

import os
import shutil
import subprocess
import sys

import IPython.core.interactiveshell as ici
import pytest

_VERBOSE = None

_NUMPY_CORRECT_COMPILERS = []
_FORTRAN_COMPILERS = (
    "gfortran",
    "flang-new",
    "flang",
    "nvfortran",
    "pgfortran",
    "ifort",
    "ifx",
    "g95",
)
_FORTRAN_COMPILER = next((compiler for compiler in _FORTRAN_COMPILERS if shutil.which(compiler)), None)
_PKG_CONFIG = shutil.which("pkg-config")


def _pkg_config_exists(name):
    if _PKG_CONFIG is None:
        return False
    return subprocess.run([_PKG_CONFIG, "--exists", name], check=False).returncode == 0


_HAS_BLAS = _pkg_config_exists("blas")
_HAS_LAPACK = _pkg_config_exists("lapack")


@pytest.fixture(scope="session", autouse=True)
def isolate_ipython_dir(tmp_path_factory):
    ipdir = tmp_path_factory.mktemp("ipython")
    mp = pytest.MonkeyPatch()
    mp.setenv("IPYTHONDIR", str(ipdir))
    yield
    mp.undo()


def pytest_configure(config) -> None:
    """Get verbosity level"""

    global _VERBOSE
    _VERBOSE = config.getoption("verbose")

    sys.path.insert(0, os.getcwd())
    config.addinivalue_line("markers", "requires_fortran: requires a working Fortran compiler")
    config.addinivalue_line("markers", "requires_blas: requires pkg-config BLAS/LAPACK entries")


def pytest_collection_modifyitems(config, items) -> None:
    if _FORTRAN_COMPILER is None:
        skip = pytest.mark.skip(reason="No Fortran compiler found in PATH")
        for item in items:
            if "requires_fortran" in item.keywords:
                item.add_marker(skip)
    if not (_HAS_BLAS and _HAS_LAPACK):
        skip = pytest.mark.skip(reason="BLAS/LAPACK not found via pkg-config")
        for item in items:
            if "requires_blas" in item.keywords:
                item.add_marker(skip)


@pytest.fixture(scope="session")
def has_blas_lapack():
    return _HAS_BLAS and _HAS_LAPACK


@pytest.fixture(scope="session")
def verbose():
    """Access to verbosity level"""
    return _VERBOSE


@pytest.fixture(scope="session")
def numpy_correct_compilers():
    """Corrected `numpy.f2py` flags"""

    return _NUMPY_CORRECT_COMPILERS


@pytest.fixture(scope="module")
def use_fortran_config():
    """Init & reset %fortran_config


    Use: @pytest.mark.usefixtures("use_fortran_config")
    """

    f_config = "--defaults"
    ish = ici.InteractiveShell()
    ish.run_cell("%load_ext fortranmagic")
    ish.run_cell("%fortran_config " + f_config)

    yield

    ish.run_cell("%fortran_config " + f_config)
    # Unfortunately, the state of the `FortranMagics` class cannot be
    # reset because in `fortranmagic.py ` there is no
    # `unload_extension()` function.
