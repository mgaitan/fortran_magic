# vim:set sw=4 ts=8 fileencoding=utf-8:
# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2023, Serguei E. Leontiev (leo@sai.msu.ru)
#
"""Remove fortranmagic configs & cache directory"""

import os
import shutil
import warnings

import IPython.paths
import pytest


@pytest.mark.fast
def test_init_cfg_and_cache(verbose):
    """
    rm -r {get_ipython_cache_dir()}/fortranmagic
    rm {paths.locate_profile()}/fortranmagic
    rm {paths.locate_profile()}/fortranmagic_cache
    """

    fm = 'fortranmagic'
    lib_dir = os.path.join(IPython.paths.get_ipython_cache_dir(), fm)
    if os.path.exists(lib_dir):
        shutil.rmtree(lib_dir)
    try:
        for sfx in ["", "_cache"]:
            cfg_file = os.path.join(IPython.paths.locate_profile(), fm + sfx)
            if os.path.exists(cfg_file):
                os.remove(cfg_file)
    except IOError as e:
        if verbose >= 1:
            warnings.warn(Warning("test_init_cfg_and_cache: except: " +
                                  str(e)))
