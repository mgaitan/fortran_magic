# -*- coding: utf-8 -*-
import pytest

import numpy as np
import numpy.f2py
import os
import platform
import subprocess
import sys


sys.path.insert(0, os.getcwd())  # Load modules from `pytest` starting directory

if platform.system() == 'Windows':
    extra_args = ['--fcompiler=gnu95', '--compiler=mingw32']
else:
    extra_args = []


# Test numpy.f2py.compile
# See: https://numpy.org/doc/stable/f2py/usage.html#numpy.f2py.compile
@pytest.mark.skipif(platform.system() == 'Windows',
                    reason="Probably gnu95/mingw32 can't load module "
                           "with print")
@pytest.mark.slow
def test_f2py_compile_fsource(capfd):
    mod = 'hello'
    fsource = '''
      subroutine foo
      use iso_fortran_env
      print*, "Hello world!"
      flush(unit=output_unit)  ! GNU extension: call flush() / flush(unit=6)
      end
    '''
    assert 0 == numpy.f2py.compile(fsource, modulename=mod, verbose=0,
                                   extra_args=extra_args)

    import hello

    hello.foo()

    out, err = capfd.readouterr()
    sout = out.splitlines()
    assert " Hello world!" in sout  # Fortran `print` add first space


# Test numpy.f2py command line
# https://numpy.org/doc/stable/f2py/f2py.getting-started.html#
@pytest.mark.slow
def test_f2py_command():
    tdir = 'test'
    mod = 'fib1'
    ret = subprocess.run([sys.executable, '-m', 'numpy.f2py',
                          '-c', tdir + '/' + mod + '.f', '-m', mod]
                         + extra_args,
                         check=True)
    assert 0 == ret.returncode

    import fib1

    a = np.zeros(8, 'd')
    fib1.fib(a)
    np.testing.assert_allclose(a, [0., 1., 1., 2., 3., 5., 8., 13.])
