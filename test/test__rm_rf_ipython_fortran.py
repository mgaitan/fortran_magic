# vim:set sw=4 ts=8 fileencoding=utf-8:
# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2023, Serguei E. Leontiev (leo@sai.msu.ru)
#
"""Remove fortranmagic cache directory"""

import os
import shutil

import IPython.paths
import pytest


@pytest.mark.fast
def test_rm_rf_ipython_fortran():
    """rm -r {get_ipython_cache_dir()}/fortran"""

    lib_dir = os.path.join(IPython.paths.get_ipython_cache_dir(), 'fortran')
    if os.path.exists(lib_dir):
        shutil.rmtree(lib_dir)
