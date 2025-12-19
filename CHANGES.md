# Changelog

## 1.0 / 2025-12-19

- Switch packaging to `pyproject.toml` with Hatchling and embed pytest config.
- Drop legacy distutils backend and require Meson for f2py builds.
- Support Python 3.10 through 3.14.
- Convert README and changelog to Markdown.
- Update release automation to build/publish with `uv`.
- Stabilize IPython cache handling and test isolation.
- Fix documentation notebook cells used by tests.
- Make micromamba CI Meson-only and more robust on Windows.
- Add Ruff tooling and format checks for the codebase.
- Skip Fortran/BLAS-dependent tests when toolchain deps are missing.
- Fix README test parser edge case for missing prefixes.

## 0.9 / 2024-05-27

- Fix for NumPy 1.26 & Python 3.12. Warning: When using the Meson build
  system (3.12 and later), there are some limitations and differences in
  the interface.
- Ready to NumPy 2.0

[Serguei E. Leontiev](https://github.com/Serge3leo)

## 0.8 / 2023-06-16

- Fix use deprecating `imp` module (removed from Python 3.12b2)
- Fix exponential duplication any not boolean flags of `%%fortran_config`
- Include stored `%%fortran_config`'s args in hashing
- Don't rebuild cell if the module already loaded and hash not changed
  (Unix don't reload already loaded shared library with same name.
  Windows can't rewrite already loaded DLL)
- Repair fortran highlighting in a `%%fortran` cell for `nbclassic`
  (Fortran highlighting for `JupyterLab` - unimplemented, for
  `IPython 3.x` - removed)
- Printing compilers diagnostics for build errors by `%%fortran`
  without `-vvv` flag

[Serguei E. Leontiev](https://github.com/Serge3leo)

## 0.7.1 / 2023-04-12

- Synchronize version number in fortranmagic.py & setup.py (2023-04-10,
  https://github.com/Serge3leo)
- Patch fortran source in compiled object. (029d890, 2020-08-01,
  https://github.com/mgaitan)
- Fix deprecation warning (3667bc1, 2017-08-18, https://github.com/guihigashi)
  [IPython.utils.path removed from IPython 8.x]
- Simplify f2py execution. (d8a058f, 2016-06-04, https://github.com/QuLogic)
  Don't change directories, and don't mangle `sys.argv`. The former can be
  specified directly in the `Popen` constructor, and the latter is cruft
  from when the f2py module was imported directly.

## 0.7 / 2016-03-13

- Fix cross compatibility with older NumPy and Python 3. (15ab10c)

Thanks to [Elliott Sales de Andrade](https://github.com/QuLogic) for this contribution.

## 0.6 / 2015-12-02

- Decode text before printing
- Call f2py module instead of binary (numpy >=1.10 is mandatory)
- Check if f2py command failed

Thanks to [Juan Luis Cano Rodriguez](https://github.com/Juanlu001) for this contribution.

## 0.5 / 2015-01-21

- Call f2py via subprocess. It fixes problems finding fortran compilers under Windows.
  (Thanks to [David Powell](https://github.com/DavidPowell))

## 0.4.3 / 2013-12-09

- Fix two python3.2+ incompatibilities (Thanks [Ramon Crehuet](https://github.com/rcrehuet) for the report)

## 0.4.2 / 2013-10-08

- Implement the `--extra` option (Thanks to [Denis Vasilyev](https://github.com/Vutshi) for the help)
- Include `%%fortran`'s args in the hashing, so the same cell are
  recompiled with the same code but different arguments

## 0.3 / 2013-10-03

- Added `%fortran_config` to set and persist default arguments for `%%fortran`
- Improve documentation

## 0.2.1 / 2013-09-24

- Packaged and registered in pypi
- Starting a version's changelog

## 0.2 / 2013-09-19

- Fortran highlighting in a `%%fortran` cell
- Works (or it should) in any platform (linux/windows/osx)
  and with py3 (thanks to [Bradley Froehle](https://github.com/bfroehle))
- Many f2py's arguments exposed as magic arguments
- Verbosity handling
- Improved documentation

## 0.1 / 2013-09-08

- First public release
