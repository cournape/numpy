export NPY_NUM_BUILD_JOBS=2

python setup.py bdist_wheel

python -m virtualenv venv-for-wheel
. venv-for-wheel/bin/activate

pushd dist
pip install --pre --no-index --upgrade --find-links=. numpy
popd

mkdir -p empty
pushd empty
python ../tools/test-installed-numpy.py
popd
