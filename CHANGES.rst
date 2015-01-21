
Changelog
=========

0.5 / 2015-01-21
----------------

- Call f2py via subprocess. It fixes problems finding fortran compilers under Windows. (Thanks to `David Powell`_ )

.. _David Powell: https://github.com/DavidPowell

0.4.3 / 2013-12-09
-------------------

- Fix two python3.2+ incompatibilities (Thanks `Ramon Crehuet`_ for the report)

.. _Ramon Crehuet: https://github.com/rcrehuet

0.4.2 / 2013-10-08
------------------

- Implement the ``--extra`` option (Thanks to `Denis Vasilyev`_ for the help)
- Include ``%%fortran``'s args in the hashing, so the same cell are
  recompiled with the same code but different arguments

.. _Denis Vasilyev: https://github.com/Vutshi

0.3 / 2013-10-03
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