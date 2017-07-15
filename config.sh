# Used by multibuild (see osx scripts)

function run_tests {
    # Runs tests on installed distribution from an empty directory
    python --version
    python -c 'import sys; import numpy; sys.exit(numpy.test())'
}
