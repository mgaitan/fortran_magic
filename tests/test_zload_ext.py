"""Test compile & load fortran extension"""

import IPython.core.interactiveshell as ici
import pytest

pytestmark = pytest.mark.requires_fortran


@pytest.mark.usefixtures("use_fortran_config")
def test_load_ext() -> None:
    """Check load/reload fortran extension"""

    ish = ici.InteractiveShell()
    tdigits = (
        "%%fortran -vv "
        """

        integer function test_digits()
            real x
            test_digits = digits(x)
        end
        """
    )
    cells = [
        "%load_ext fortranmagic",
        "%fortran_config --defaults",
        tdigits,
        "assert 24 == test_digits(), test_digits()",
        tdigits,
        "assert 24 == test_digits(), test_digits()",
        "%fortran_config --f90flags '-fdefault-real-8'",
        tdigits,
        "assert 53 == test_digits(), test_digits()",
    ]

    for c in cells:
        er = ish.run_cell(c)
        assert er.success
