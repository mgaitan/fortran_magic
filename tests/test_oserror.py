"""Tests Popen() errors"""

import os
import sys

import IPython.core.interactiveshell as ici
import pytest

sys.path.insert(0, os.getcwd())  # Load modules from `pytest` starting directory

PATTERN = "Couldn't find program:"

GOOD_PRG = """
subroutine hj(x)
    x = 1.
end subroutine hj
"""


@pytest.mark.usefixtures("use_fortran_config")
def test_popen_oserror(capfd) -> None:
    """Test diagnostic of errno.ENOENT"""

    ish = ici.InteractiveShell()
    res = ish.run_cell("%load_ext fortranmagic")
    assert res.success
    save_sys_executable = sys.executable
    try:
        sys.executable = "_not./.executable_/_path."
        res = ish.run_cell("%%fortran\n" + GOOD_PRG)
        coe = capfd.readouterr()
        assert not res.success
        assert coe.out.count(PATTERN) + coe.err.count(PATTERN) == 1
    finally:
        sys.executable = save_sys_executable
