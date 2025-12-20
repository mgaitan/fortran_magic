"""Test README.md"""

import re

import IPython.core.interactiveshell as ici
import numpy as np
import pytest

pytestmark = pytest.mark.requires_fortran


@pytest.mark.usefixtures("use_fortran_config")
def test_ipython_cells() -> None:
    """Check IPython cells form README.md"""

    with open("README.md") as f:
        rm = f.read()

    cells = []
    celio = None
    lpfx = None
    for line in rm.splitlines():
        assert "\t" not in line
        m = re.match(r"^\s*(In|Out)\[(\d+)\]:\s*(.*)$", line)
        if m and m.group(1) == "In":
            cells.append({"n": int(m.group(2)), "In": [m.group(3)]})
            celio = "In"
            lpfx = len(line) - len(m.group(3))
        elif m and m.group(1) == "Out":
            assert cells[-1]["n"] == int(m.group(2))
            cells[-1]["Out"] = [m.group(3)]
            celio = "Out"
            lpfx = len(line) - len(m.group(3))
        elif celio is not None and lpfx is not None and (len(line) == 0 or line[:lpfx].isspace()):
            cells[-1][celio].append(line[lpfx:] if len(line) > 0 else line)
        else:
            celio = None
            lpfx = None

    ish = ici.InteractiveShell()

    success = 0
    checked = 0
    for c in cells:
        cs = "\n".join(c["In"])
        er = ish.run_cell(cs, store_history=False)
        if er.success:
            success += 1
        else:
            pytest.fail("\n" + cs)
        if "Out" in c:
            np.testing.assert_allclose(float("\n".join(cells[-1]["Out"])), float(er.result))
            checked += 1

    assert success > 0 and checked > 0
