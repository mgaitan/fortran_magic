
Changelog
=========

0.4.1 / 2013-07-10
----------------

- Implement the ``--extra`` option.
- Include ``%%fortran``'s args in the hashing, so the same cell are
  recompiled if its arguments changes

0.3 / 2013-03-10
------------------

- Added ``%fortran_config`` to set and persist default arguments
  for ``%%fortran``
- Improve documentation

0.2.1 / 2013-09-24
------------------

- Packaged and registered in pypi
- Starting a version's changelog

0.2 / 2013-09-19
----------------

- Fortran highlighting in a ``%%fortran`` cell
- Works (or it should) in any platform (linux/windows/osx)
  and with py3 (thanks to `Bradley Froehle`_)
- Many f2py's arguments exposed as magic arguments
- Verbosity handling
- Improved documentation

.. _Bradley Froehle: https://github.com/bfroehle

0.1 / 2013-09-08
----------------

- First public release