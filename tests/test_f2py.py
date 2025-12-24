"""Check `numpy.f2py` base functionality."""

import subprocess
import sys

import numpy as np
import numpy.f2py
import pytest

pytestmark = pytest.mark.requires_fortran


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Probably gnu95/mingw32 can't load module with print",
)
@pytest.mark.skipif(np.__version__ >= "2", reason="NumPy 2.0 remove numpy.f2py.compile")
@pytest.mark.slow
def test_f2py_compile_fsource(capfd, numpy_correct_compilers) -> None:
    """
    Check `numpy.f2py.compile`.

    See: https://numpy.org/doc/stable/f2py/usage.html#numpy.f2py.compile
    """

    mod = "hello"
    fsource = """
      subroutine foo
      use iso_fortran_env
      print*, "Hello world!"
      flush(unit=output_unit)  ! GNU extension: call flush() / flush(unit=6)
      end
    """
    assert numpy.f2py.compile(fsource, modulename=mod, verbose=0, extra_args=numpy_correct_compilers) == 0

    import hello

    hello.foo()

    out, _ = capfd.readouterr()
    sout = out.splitlines()
    assert " Hello world!" in sout  # Fortran `print` add first space


@pytest.mark.slow
def test_f2py_command(numpy_correct_compilers) -> None:
    """
    Check `numpy.f2py` command line.

    https://numpy.org/doc/stable/f2py/f2py.getting-started.html#
    """

    tdir = "tests"
    mod = "fib1"
    ret = subprocess.check_call(
        [
            sys.executable,
            "-m",
            "numpy.f2py",
            "--backend",
            "meson",
            "-c",
            tdir + "/" + mod + ".f",
            "-m",
            mod,
            *numpy_correct_compilers,
        ]
    )
    assert ret == 0

    import fib1

    a = np.zeros(8, "d")
    fib1.fib(a)
    np.testing.assert_allclose(a, [0.0, 1.0, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0])
