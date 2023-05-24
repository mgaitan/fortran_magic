# -*- coding: utf-8 -*-
import pytest
import warnings

import copy
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os
import subprocess
import sys


sys.path.insert(0, os.getcwd())  # Load modules from `pytest` starting directory


def test_setup_version():
    import fortranmagic

    assert (fortranmagic.__version__ == subprocess.check_output(
                [sys.executable, "setup.py", "--version"]).decode().rstrip())


class SkipExecutePreprocessor(ExecutePreprocessor):
    def __init__(self, tags=None, **kwargs):
        self._tags = tags
        return super().__init__(**kwargs)

    def preprocess_cell(self, cell, resources, index):
        if 'tags' in cell['metadata']:
            stags = set(cell['metadata']['tags'])
        else:
            stags = {'_medium'}
        if not (stags & self._tags):
            return
        return super().preprocess_cell(cell, resources, index)


dte_tags = {'random', 'slow', 'fast'}
dte_testing = set()


def documentation_testing_engine(tags: set):
    global dte_testing
    if not (tags - dte_testing):
        pytest.skip(str(tags) + " previously tested")
    assert not dte_testing, "Bad test_documentation_*() order"
    dte_testing |= tags

    with open('documentation.ipynb', 'r') as f:
        test_documentation = nbformat.read(f, nbformat.NO_CONVERT)

    ep = SkipExecutePreprocessor(tags=tags, timeout=600)
    exec_documentation = copy.deepcopy(test_documentation)
    ep.preprocess(exec_documentation)

    assert len(test_documentation.cells) == len(exec_documentation.cells)
    for i in range(len(test_documentation.cells)):
        t = test_documentation.cells[i]
        e = exec_documentation.cells[i]
        if 'tags' in t['metadata']:
            stags = set(t['metadata']['tags'])
            if stags - dte_tags:
                warnings.warn(Warning(
                            "Test documentation.ipynb unknown tags: " +
                            str({'1'})))
            if 'random' in stags:
                continue
        assert not (('outputs' in t) ^ ('outputs' in e))
        if 'outputs' not in t:
            continue
        for to, eo in zip(t['outputs'], e['outputs']):
            if 'execution_count' in to:
                cto, ceo = to.copy(), eo.copy()
                ceo['execution_count'] = cto['execution_count']
                assert cto == ceo, "for cell[%d]: %s" % (i, t['source'])


@pytest.mark.slow
def test_documentation_slow():
    documentation_testing_engine({'slow', '_medium', 'fast'})


@pytest.mark.medium
def test_documentation_outputs():
    documentation_testing_engine({'_medium', 'fast'})


@pytest.mark.fast
def test_documentation_fast():
    documentation_testing_engine({'fast'})
