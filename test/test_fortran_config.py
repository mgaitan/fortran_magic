# vim:set sw=4 ts=8 fileencoding=utf-8:
# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2023, Serguei E. Leontiev (leo@sai.msu.ru)
#
"""
Checking flags of `%fortran_config` and `%%fortran`.

WARNING: Tests change `%fortran_config`, so they are not parallel
processes safe.
"""

import os
import shutil
import sys
import warnings

import IPython.core.interactiveshell as ici
import IPython.paths
import pytest

_USE_MESON = (sys.version_info >= (3, 12))

# For slightly faster compilations.
FORTRAN = "%%fortran --noopt  --f90flags '-O0' "

GOOD_PRG = """
subroutine hj(x)
    x = 1.
end subroutine hj
"""
BUG_PRG = """
subroutine hj(x)
    x = ?-+1+-?
end subroutine hj
"""


class Cish(object):
    """IPython interactive shell and test configuration."""

    def __init__(self, numpy_correct_compilers=None, verbose=None, src=None):
        if src is not None:
            assert numpy_correct_compilers is None and verbose is None
            self.cap = src.cap
            self.numpy_correct_compilers = src.numpy_correct_compilers
            self.verbose = src.verbose
            self.ish = src.ish
        else:
            assert numpy_correct_compilers is not None and verbose is not None
            self.cap = None
            self.numpy_correct_compilers = " ".join(numpy_correct_compilers)
            self.verbose = verbose
            self.ish = ici.InteractiveShell()
            self.chk_run("%load_ext fortranmagic")
            self.f_config("")

    def uck_run(self, src):
        """Calculating cell and capture stdout/stderr."""

        r = self.ish.run_cell(src, store_history=False)
        if self.cap is None:
            return r, "", ""
        c = self.cap.readouterr()
        if self.verbose >= 2:
            warnings.warn(str(r))
            warnings.warn(c.out)
            warnings.warn(c.err)
        return r, c.out, c.err

    def chk_run(self, src):
        """Calculating cell, capture and check success."""

        r, o, e = self.uck_run(src)
        assert r.success, "Fail: " + src
        return r, o, e

    def f_config(self, flgs):
        """Call `%fortran_config` and check success."""

        if flgs is not None:
            if self.numpy_correct_compilers:
                flgs = self.numpy_correct_compilers + " " + flgs
            elif not flgs:
                flgs = "--defaults"
            self.chk_run("%fortran_config " + flgs)

    def check_pattern(self, vrngs):
        """Compile and check patterns in stdout/stderr."""

        for vf in vrngs:
            _, o, e = self.chk_run(FORTRAN + vf['a'] + "\n" + GOOD_PRG)
            for p in vf['ps']:
                assert (o.count(p['p']) >= p['o'][0] and
                        o.count(p['p']) <= p['o'][1]), o
                assert (e.count(p['p']) >= p['e'][0] and
                        e.count(p['p']) <= p['e'][1]), e


@pytest.fixture(scope='module')
def ish(numpy_correct_compilers, verbose):
    """Fixture for IPython interactive shell and test configuration."""

    r = Cish(numpy_correct_compilers, verbose)
    yield r
    r.f_config("")


class CtxIsh(Cish):
    """Context of capture and IPython interactive shell."""

    def __init__(self, cish, capfd):
        super(CtxIsh, self).__init__(src=cish)
        self.cap = capfd


@pytest.fixture(scope='function')
def ctxish(capfd, ish):
    """Fixture for context of capture and IPython interactive shell."""

    return CtxIsh(ish, capfd)


MAXLOG = 10**9


@pytest.mark.slow
@pytest.mark.usefixtures("use_fortran_config")
@pytest.mark.parametrize(
    "f_config_arg, fortran_arg, outrange, errrange", [
        ("", "", [0, 0], [0, 0]),
        (None, "-v", [1, 2], [0, 0]),
        (None, "-vv", [4, 5], [0, 0]),
        (None, "-vvv", [6, MAXLOG], [0, MAXLOG]),
        ("-v -v", "", [4, 5], [0, 0]),
        (None, "-v", [1, 2], [0, 0]),
        pytest.param(
            None, "-vv", [4, 5], [0, 0],
            marks=pytest.mark.paranoid),
        pytest.param(
            None, "-vvv", [6, MAXLOG], [0, MAXLOG],
            marks=pytest.mark.paranoid),
        pytest.param(
            "-v", "", [1, 2], [0, 0],
            marks=pytest.mark.paranoid),
        pytest.param(
            None, "-v", [1, 2], [0, 0],
            marks=pytest.mark.paranoid),
        pytest.param(
            None, "-vv", [4, 5], [0, 0],
            marks=pytest.mark.paranoid),
        pytest.param(
            None, "-vvv", [6, MAXLOG], [0, MAXLOG],
            marks=pytest.mark.paranoid),
        ("-v", "--add-hash 1", [1, 2], [0, 0]),
        (None, "--add-hash 2", [1, 2], [0, 0]),
        pytest.param(
            None, "--add-hash 3", [1, 2], [0, 0],
            marks=pytest.mark.paranoid),
        ])
def test_v(ctxish, f_config_arg, fortran_arg, outrange, errrange):
    """
    1. There should be no output without the `-v` flag, if there are no
    errors;

    2. With the `-v` and `-vv` flags, the output should be more and more
    detailed;

    3. With the `-vvv` flag, there may also be `stderr` output (warnings
    of internal utilities, etc.);

    4. Specifying the `-v` flag(s) in `%format` redefined `-v` flags in
    '%fortran_config`.

    5. Verbosity level setted by `%fortran_config` must be constant.
    """
    ctxish.f_config(f_config_arg)
    ctxish.check_pattern([
        {'a': fortran_arg, 'ps': [{'p': "\n", 'o': outrange, 'e': errrange}]},
        ])


@pytest.mark.fast
def test_intermediate_rm_rf_ipython_fortran():
    """
    rm -r {get_ipython_cache_dir()}/fortranmagic
    """

    fm = 'fortranmagic'
    lib_dir = os.path.join(IPython.paths.get_ipython_cache_dir(), fm)
    if os.path.exists(lib_dir):
        shutil.rmtree(lib_dir, ignore_errors=True)


@pytest.mark.fast
@pytest.mark.usefixtures("use_fortran_config")
def test_fcompiler_priority(ctxish):
    """
    `%%fortran` `--fcompile`/`--compile` flags must redefined
    `%fortran_config` flags.
    """

    ctxish.f_config("--fcompiler=g95")
    ctxish.check_pattern([
        {'a': "-vv --fcompiler=gnu95",
         'ps': [
            {'p': "--fcompiler=g95",   'o': [0, 0], 'e': [0, 0]},
            {'p': "--fcompiler=gnu95", 'o': [1, 1], 'e': [0, 0]},
            ]}])


@pytest.mark.fast
@pytest.mark.usefixtures("use_fortran_config")
def test_syntax_error(ctxish, numpy_correct_compilers):
    """Check `stderr` output by fortran syntax error."""

    f_config = " ".join(numpy_correct_compilers) if numpy_correct_compilers \
               else "--defaults"
    ctxish.f_config(f_config)
    r, o, e = ctxish.uck_run(FORTRAN + "\n" + BUG_PRG)
    assert not r.success, str(r)
    assert o.count('\n') >= 6, o
    assert e.count('\n') >= 1, e


@pytest.mark.usefixtures("use_fortran_config")
@pytest.mark.parametrize(
    "f_config_arg, fortran_arg", [
        ("--extra '-DNPY_NO_DEPRECATED_API=0' --link lapack",
         "--extra '-DNPY_NO_DEPRECATED_API=0' --link blas"),
        pytest.param(
         None,
         "--extra '-DNPY_NO_DEPRECATED_API=0' --link blas",
         marks=pytest.mark.xfail if sys.platform.startswith("win32")
         else []),
        ])
def test_link_extra(ctxish, f_config_arg, fortran_arg):
    """
    `--extra` and `--link` flags from `%fortran_config` and
    `%%fortran` magic must union.

    On the second run, same flags and their number should be received.
    """

    ctxish.f_config(f_config_arg)
    ctxish.f_config("--clean-cache")
    ctxish.check_pattern([
        {'a': "-vv " + fortran_arg,
         'ps': [
            {'p': "-DNPY_NO_DEPRECATED_API=0", 'o': [2, 2], 'e': [0, 0]},
            {'p': "--dep lapack" if _USE_MESON else "--link-lapack",
             'o': [1, 1], 'e': [0, 0]},
            {'p': "--dep blas" if _USE_MESON else "--link-blas",
             'o': [1, 1], 'e': [0, 0]},
            ]}])
