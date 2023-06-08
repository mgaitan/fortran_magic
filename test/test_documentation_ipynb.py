# vim:set sw=4 ts=8 fileencoding=utf-8:
# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2023, Serguei E. Leontiev (leo@sai.msu.ru)
#
"""
`document.ipynb` as test of `fortranmagic.py` and vice versa
============================================================

1. Checking the successful calculation of the selected subset of cells
(tags: `fast`, `slow` and cells without these tags);

2. Comparison of all cell's outputs that don't have the `random` tag.
"""

import copy
import sys
import warnings

import nbformat
import pytest
from jupyter_client.manager import start_new_kernel
from nbconvert.preprocessors import ExecutePreprocessor

DTE_FAST = 'fast'
DTE_MEDIUM = '_medium'  # No `DTE_TAGS`
DTE_SLOW = 'slow'
DTE_RANDOMS = {'random', 'random_long'}
DTE_TAGS = {DTE_FAST, DTE_SLOW}
DTE_SKIPS = {'skip', 'skip_darwin', 'skip_linux', 'skip_win32'}
DTE_XFAILS = {'xfail', 'xfail_darwin', 'xfail_linux', 'xfail_win32'}

# All kinds of notebook cell tags
DTA_TAGS = DTE_TAGS | {DTE_MEDIUM} | DTE_RANDOMS | DTE_SKIPS | DTE_XFAILS

DTE_TESTED = set()


def _get_stags(meta):
    stags = set(meta.get('tags', []))
    if not (stags & DTE_TAGS):
        stags.add(DTE_MEDIUM)
    return stags


def _check_sxf(sxf, stags):
    for t in stags:
        if t == sxf or (t.startswith(sxf + '_') and
                        sys.platform.startswith(t[len(sxf) + 1:])):
            return True
    return False


class SkipExecutePreprocessor(ExecutePreprocessor):
    """Selecting cells and clearing rejected."""

    def __init__(self, tags=None, verbose=0, **kwargs):
        self._tags = tags
        self._verbose = verbose
        super(SkipExecutePreprocessor, self).__init__(**kwargs)

    def preprocess_cell(self, cell, resources, index):
        stags = _get_stags(cell.metadata)
        if not (stags & self._tags) or _check_sxf('skip', stags):
            if self._verbose >= 1:
                warnings.warn(Warning("SkipExecutePreprocessor: "
                                      "skip cell id: " + cell.id +
                                      "\n" + cell.get('source', "") +
                                      "\n========"))
            rcell, rresources = cell.copy(), resources
        else:
            if self._verbose >= 2:
                warnings.warn(Warning("SkipExecutePreprocessor: "
                                      "execute cell id: " + cell.id +
                                      "\n" + cell.get('source', "") +
                                      "\n========"))
            allow_errors = self.allow_errors
            try:
                if _check_sxf('xfail', stags):
                    self.allow_errors = True
                rcell, rresources = \
                    super(SkipExecutePreprocessor,
                          self).preprocess_cell(cell, resources, index)
            finally:
                self.allow_errors = allow_errors
        return rcell, rresources


def documentation_testing_engine(tags, verbose):
    """Calculation & comparison selected subset of cells."""

    global DTE_TESTED

    if not (tags - DTE_TESTED):
        pytest.skip(str(tags) + " previously tested")
        return
    assert not DTE_TESTED, "Bad test_documentation_*() order"
    DTE_TESTED |= tags

    with open('documentation.ipynb', 'r') as f:
        test_documentation = nbformat.read(f, nbformat.NO_CONVERT)
        assert len(test_documentation.cells) > 1

    test_documentation.cells.insert(
            0,
            nbformat.v4.new_code_cell(
                "import coverage as _tdi_coverage\n"
                "_tdi_cov = _tdi_coverage.Coverage()\n"
                "_tdi_cov.start()\n"
                )
            )
    test_documentation.cells.append(
            nbformat.v4.new_code_cell(
                "_tdi_cov.stop()\n"
                "_tdi_cov.save()\n"
                )
            )

    for t in test_documentation.cells:
        if t.cell_type == 'code':
            if 'execution' in t.metadata:
                del t.metadata['execution']

    ep = SkipExecutePreprocessor(tags=tags, verbose=verbose, timeout=600)
    km, _ = start_new_kernel()  # Ignore kernelspec in documentation.ipynb
    exec_documentation, _ = ep.preprocess(copy.deepcopy(test_documentation),
                                          km=km)

    xfail_cells, xpass_cells = 0, 0

    assert len(test_documentation.cells) == len(exec_documentation.cells)
    for t, e in zip(test_documentation.cells, exec_documentation.cells):
        stags = _get_stags(t.metadata)
        if stags - DTA_TAGS:
            warnings.warn(Warning(
                        "Test documentation.ipynb unknown tags: " +
                        str(stags - DTA_TAGS)))
        if any(o.output_type == 'error' for o in e.get('outputs', [])):
            if _check_sxf('xfail', stags):
                xfail_cells += 1
                continue
            assert False, "for cell: " + str(e)
        if DTE_RANDOMS & stags:
            continue
        try:
            assert not (('outputs' in t) ^ ('outputs' in e)), \
                   "for cell: " + str(t)
            if 'outputs' in t:
                for to, eo in zip(t.outputs, e.outputs):
                    if 'execution_count' in to:
                        cto = to.copy()
                        cto.execution_count = eo.execution_count
                        assert cto == eo, "for cell: " + str(e)
            if _check_sxf('xfail', stags):
                xpass_cells += 1
        except AssertionError:
            if not _check_sxf('xfail', stags):
                raise
            xfail_cells += 1

    if xfail_cells or xpass_cells:
        msg = "\nXFAIL_CELLS = %d XPASS_CELLS = %d\n" % (xfail_cells,
                                                         xpass_cells)
        warnings.warn(Warning(msg))
        if xfail_cells:
            pytest.xfail(msg)


@pytest.mark.slow
@pytest.mark.usefixtures("use_fortran_config")
def test_documentation_slow(verbose):
    """
    Default - all cells.

    This test skipped by `-m 'not slow'` or `-m fast`."""

    documentation_testing_engine({DTE_SLOW, DTE_MEDIUM, DTE_FAST}, verbose)


@pytest.mark.medium
@pytest.mark.usefixtures("use_fortran_config")
def test_documentation_medium(verbose):
    """
    `-m 'not slow'`

    Really working if `DTE_TESTED` empty.
    """

    documentation_testing_engine({DTE_MEDIUM, DTE_FAST}, verbose)


@pytest.mark.fast
@pytest.mark.usefixtures("use_fortran_config")
def test_documentation_fast(verbose):
    """
    `-m fast`

    Really working if `DTE_TESTED` empty.
    """

    documentation_testing_engine({DTE_FAST}, verbose)
