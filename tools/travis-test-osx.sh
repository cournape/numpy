export NPY_NUM_BUILD_JOBS=2

source multibuild/common_utils.sh
source multibuild/travis_steps.sh

clean_code numpy "${TRAVIS_COMMIT}"
build_wheel numpy x86_64

install_run x86_64
