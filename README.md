# Fortran magic

[![PyPI](https://img.shields.io/pypi/v/fortran-magic)](https://pypi.python.org/pypi/fortran-magic)
[![CI](https://github.com/mgaitan/fortran_magic/actions/workflows/micromamba.yml/badge.svg)](https://github.com/mgaitan/fortran_magic/actions/workflows/micromamba.yml)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/fortran-magic)](https://pypi.python.org/pypi/fortran-magic)

Compile and import symbols from a cell with Fortran code, using [f2py](https://numpy.org/doc/stable/f2py/).

> **Attention:** I am looking for collaborators to maintain this project. If you are interested,
> please open an issue (or PRs) with your proposals for improvements and volunteer to be a maintainer.

The contents of the cell are written to a `.f90` file in the directory
`IPYTHONDIR/fortran` using a filename with the hash of the code. This file is then
compiled. The resulting module is imported and all of its symbols are injected into
the user's namespace.

- Homepage: https://github.com/mgaitan/fortran_magic
- Documentation: see [this notebook](http://nbviewer.ipython.org/urls/raw.github.com/mgaitan/fortran_magic/master/documentation.ipynb)

## Install

You can install or upgrade via [uv](https://docs.astral.sh/uv/):

```bash
uv add fortran-magic
```

Or via pip:

```bash
pip install -U fortran-magic
```

Or run directly

```bash
uv run --with=fortran-magic ipython
```

## Basic usage

Once it's installed, you can load it with `%load_ext fortranmagic`. Then put your
Fortran code in a cell started with the cell magic `%%fortran`. For example:

```text
In[1]: %load_ext fortranmagic

In[2]: %%fortran

       subroutine f1(x, y, z)
            real, intent(in) :: x,y
            real, intent(out) :: z

            z = sin(x+y)

       end subroutine f1
```

Every symbol is automatically imported. So the subroutine `f1` is already available in
your python session as a function:

```text
In[3]:  f1(1.0, 2.1415)
Out[3]: 9.26574066397734e-05
```

## Tests

Run tests with:

```text
uv run --group dev pytest
```

See the documentation for further details.
