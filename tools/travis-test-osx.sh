#!/bin/bash
set -ex

export NPY_NUM_BUILD_JOBS=2

. venv/bin/activate
python -V
python -c "import sys; print(sys.exec_prefix)"

pip install cython nose pytz
export CFLAGS="-Wno-sign-compare -x86_64 -O0"
export CXXFLAGS="-Wno-sign-compare -x86_64 -O0"
export CC=clang
export CXX=clang++
python setup.py bdist_wheel

virtualenv venv-for-wheel
. venv-for-wheel/bin/activate
python -V
python -c "import sys; print(sys.exec_prefix)"
pip install nose pytz

pushd dist
pip install --pre --no-index --upgrade --find-links=. numpy
popd

mkdir -p empty
pushd empty
python ../tools/test-installed-numpy.py
popd
