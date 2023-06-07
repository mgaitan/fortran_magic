=============
Fortran magic
=============

.. image:: https://img.shields.io/pypi/v/fortran-magic
   :target: https://pypi.python.org/pypi/fortran-magic
   :alt: PyPI
   
.. image:: https://img.shields.io/pypi/dm/fortran-magic
   :target: https://pypi.python.org/pypi/fortran-magic
   :alt: PyPI - Downloads
   

Compile and import symbols from a cell with Fortran code, using f2py.

------

..  attention::
    I am looking for collaborators to maintain this project. If you are interested, 
    please open an issue (or PRs) with your proposals for improvements and volunteer to be a maintainer. 

------

The contents of the cell are written to a `.f90` file in the
directory `IPYTHONDIR/fortran` using a filename with the hash of the
code. This file is then compiled. The resulting module
is imported and all of its symbols are injected into the user's
namespace.

:homepage: https://github.com/mgaitan/fortran_magic
:documentation: see `this notebook`__

__ documentation_
.. _documentation:  http://nbviewer.ipython.org/urls/raw.github.com/mgaitan/fortran_magic/master/documentation.ipynb


Install
=======

You can install or upgrade via pip

    pip install -U fortran-magic


Basic usage
===========

Once it's installed, you can load it with ``%load_ext fortranmagic``.
Then put your Fortran code in a cell started with the cell magic ``%%fortran``. For example::


    In[1]: %load_ext fortranmagic

    In[2]: import sys

           if sys.platform.startswith("win"):
               # Depends of system, python builds, and compilers compatibility.
               # See `documentation.ipnb`.
               %fortran_config --fcompiler=gnu95 --compiler=mingw32

    In[3]: %%fortran

           subroutine f1(x, y, z)
                real, intent(in) :: x,y
                real, intent(out) :: z

                z = sin(x+y)

           end subroutine f1


Every symbol is automatically imported. So the subroutine `f1` is already available in your python session as a function::

    In[4]:  f1(1.0, 2.1415)
    Out[4]: 9.26574066397734e-05


See the documentation_ for further details.
