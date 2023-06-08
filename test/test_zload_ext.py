# vim:set sw=4 ts=8 fileencoding=utf-8:
# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2023, Serguei E. Leontiev (leo@sai.msu.ru)
#
"""Test compile & load fortran extension"""

import sys

import IPython.core.interactiveshell as ici
import pytest


@pytest.mark.usefixtures("use_fortran_config")
def test_load_ext():
    """Check load/reload fortran extension"""

    ish = ici.InteractiveShell()
    if sys.platform.startswith("win32"):
        f_config = "--fcompiler=gnu95 --compiler=mingw32"
    else:
        f_config = ""
    tdigits = "%%fortran -vv " + f_config + """

        integer function test_digits()
            real x
            test_digits = digits(x)
        end
        """
    cells = [
        "%load_ext fortranmagic",
        "%fortran_config --defaults",
        tdigits,
        "assert 24 == test_digits(), test_digits()",
        tdigits,
        "assert 24 == test_digits(), test_digits()",
        "%fortran_config --f90flags '-fdefault-real-8'",
        tdigits,
        "assert 53 == test_digits(), test_digits()",
    ]

    for c in cells:
        er = ish.run_cell(c)
        assert er.success
