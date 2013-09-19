Fortran magic
=============

Compile and import everything from a Fortran code cell, using f2py.

The contents of the cell are written to a `.f90` file in the
directory `IPYTHONDIR/fortran` using a filename with the hash of the
code. This file is then compiled. The resulting module
is imported and all of its symbols are injected into the user's
namespace.


:author: Martín Gaitán <gaitan@gmail.com>
:homepage: https://github.com/mgaitan/fortran_magic
:documentation: see `this notebook <http://nbviewer.ipython.org/urls/raw.github.com/mgaitan/fortran_magic/master/example_notebook.ipynb>`_  

Install
=======

Install the extension with `%install_ext` ::

    In[1]: %install_ext https://raw.github.com/mgaitan/fortran_magic/master/fortranmagic.py


Usage
=====

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


See the example for details

