=============
Fortran magic
=============

.. image:: https://pypip.in/v/fortran-magic/badge.png
   :target: https://pypi.python.org/pypi/fortran-magic
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/fortran-magic/badge.png
   :target: https://pypi.python.org/pypi/fortran-magic
   :alt: Number of PyPI downloads
 

Compile and import symbols from a cell with Fortran code, using f2py.

The contents of the cell are written to a `.f90` file in the
directory `IPYTHONDIR/fortran` using a filename with the hash of the
code. This file is then compiled. The resulting module
is imported and all of its symbols are injected into the user's
namespace.


:author: Martín Gaitán <gaitan@gmail.com>
:homepage: https://github.com/mgaitan/fortran_magic
:documentation: see `this notebook`__

__ documentation_
.. _documentation:  http://nbviewer.ipython.org/urls/raw.github.com/mgaitan/fortran_magic/master/documentation.ipynb


Install
=======

You can install or upgrade via pip

    pip install -U fortran-magic

or directly from the repository using the `%install_ext` magic command::

    In[1]: %install_ext https://raw.github.com/mgaitan/fortran_magic/master/fortranmagic.py


Basic usage
===========

Once it's installed, you can load it with `%load_ext fortranmagic`. Then put your Fortran code in a cell started with the cell magic `%%fortran``.
For example::

    In[2]: %load_ext fortranmagic


    In[3]: %%fortran

           subroutine f1(x, y, z)
                real, intent(in) :: x,y
                real, intent(out) :: z

                z = sin(x+y)

           end subroutine f1


Every symbol is automatically imported. So `f1` is already available::

    In[4]:  f1(1.0, 2.1415)
    Out[4]: 9.26574066397734e-05


See the documentation_ for details.
