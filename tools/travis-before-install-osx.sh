#!/bin/bash
set -ex

git clone https://github.com/matthew-brett/multibuild

source multibuild/common_utils.sh
source multibuild/travis_steps.sh
before_install
