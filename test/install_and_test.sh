#!
# vim:set sw=4 ts=8 fileencoding=utf8:
# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2023, Serguei E. Leontiev (leo@sai.msu.ru)
#

set -e

tdir="${1:-itd}"

if [ $# -ge 1 ]; then
    shift
fi

cache_clean() {
    find "$1" -name '*.pyc' -print0 | xargs -0 rm || true
    find "$1" -name '__pycache__' -print0 | xargs -0 rm -r || true
    find "$1" -name '.pytest_cache'-print0 | xargs -0 rm -r || true
}

clean() {
    python -m pip uninstall --quiet --yes fortran-magic || true
    rm -rf "$tdir"
    cache_clean .
}

trap clean EXIT SIGHUP SIGINT SIGTERM
clean

python -m pip install .

mkdir -p "$tdir"
cp -rp CHANGES.md README.md \
    documentation.ipynb pyproject.toml test \
    "$tdir"/.
(cd "$tdir" && \
    python -m pytest "$@" --cov=fortranmagic --capture=fd \
    --cov-report=term-missing --cov-report=html)
rm -rf install_and_test-htmlcov
cp -r "$tdir"/htmlcov install_and_test-htmlcov
