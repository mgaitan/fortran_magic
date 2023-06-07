# vim:set sw=4 ts=8 fileencoding=utf-8:
# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2023, Serguei E. Leontiev (leo@sai.msu.ru)
#
"""
Pytest configuration:
    1. Add `pytest` starting directory for load `fortranmagic.py` and
       compiled testing modules;
    2. Fixture for verbosity level at session start;
    3. Fixture for workaround probable bug `numpy.f2py` on Windows.
"""

import os
import sys

import IPython.core.interactiveshell as ici
import pytest

_VERBOSE = None

if sys.platform.startswith("win"):
    _NUMPY_CORRECT_COMPILERS = ['--fcompiler=gnu95', '--compiler=mingw32']
else:
    _NUMPY_CORRECT_COMPILERS = []


def pytest_configure(config):
    """Get verbosity level"""

    global _VERBOSE
    _VERBOSE = config.getoption("verbose")

    sys.path.insert(0, os.getcwd())


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

    if _NUMPY_CORRECT_COMPILERS:
        f_config = " ".join(_NUMPY_CORRECT_COMPILERS)
    else:
        f_config = "--defaults"
    ish = ici.InteractiveShell()
    ish.run_cell("%load_ext fortranmagic")
    ish.run_cell("%fortran_config " + f_config)

    yield

    ish.run_cell("%fortran_config " + f_config)
    # Unfortunately, the state of the `FortranMagics` class cannot be
    # reset because in `fortranmagic.py ` there is no
    # `unload_extension()` function.
