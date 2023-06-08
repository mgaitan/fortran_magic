# vim:set sw=4 ts=8 fileencoding=utf-8:
# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2023, Serguei E. Leontiev (leo@sai.msu.ru)
#
"""Test setup.py"""

import subprocess
import sys


def test_setup_version():
    """Check versions fortranmagic.py&setup.py"""

    import fortranmagic

    assert (fortranmagic.__version__ == subprocess.check_output(
                [sys.executable, "setup.py", "--version"]).decode().rstrip())
