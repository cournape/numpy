from numpy.testing import *
from numpy.fft.tests.helpers import direct_dft, direct_idft, direct_rdft, direct_irdft
import numpy as np

class TestFFTShift(TestCase):
    def test_fft_n(self):
        self.assertRaises(ValueError,np.fft.fft,[1,2,3],0)

class _TestBase1d(TestCase):
    def setUp(self):
        np.random.seed(0)

    def test_basic(self):
        rand = np.random.random
        x = rand(30) + 1j*rand(30)
        assert_array_almost_equal(self.reference(x), self.func(x))

    def test_prime(self):
        for n in [2, 3, 5, 7, 11, 37]:
            x = rand(n) + 1j*rand(n)
            assert_array_almost_equal(self.reference(x), self.func(x))

    def test_definition(self):
        def _test(x):
            for n in range(1, len(x) * 2):
                y = self.func(x, n)
                y1 = self.reference(x, n)
                assert_array_almost_equal(y, y1)
        x = np.array([1, 2, 3, 4+1j, 1, 2, 3, 4+2j])
        _test(x)
        x = np.array([1, 2, 3, 4+0j, 5])
        _test(x)

    def test_n_argument_real(self):
        x1 = np.array([1, 2, 3, 4])
        x2 = np.array([1, 2, 3, 4])
        for n in range(1, 2*len(x1) - 1):
            y = self.func([x1, x2], n)
            assert_equal(y.shape, (2, n))
            assert_array_almost_equal(y[0], self.reference(x1, n))
            assert_array_almost_equal(y[1], self.reference(x2, n))

    def test_n_argument_complex(self):
        x1 = np.array([1, 2, 3, 4+1j])
        x2 = np.array([1, 2, 3, 4+1j])
        for n in range(1, 2*len(x1) - 1):
            y = self.func([x1, x2], n)
            assert_equal(y.shape, (2, n))
            assert_array_almost_equal(y[0], self.reference(x1, n))
            assert_array_almost_equal(y[1], self.reference(x2, n))

class TestFFT(_TestBase1d):
    def reference(self, x, n=None):
        return direct_dft(x, n)

    def func(self, x, n=None):
        return np.fft.fft(x, n)

class TestIFFT(_TestBase1d):
    def reference(self, x, n=None):
        return direct_idft(x, n)

    def func(self, x, n=None):
        return np.fft.ifft(x, n)

class _TestBaseReal1d(TestCase):
    def setUp(self):
        np.random.seed(0)

    def test_basic(self):
        rand = np.random.random
        x = rand(30)
        assert_array_almost_equal(self.reference(x), self.func(x))

    def test_prime(self):
        for n in [2, 3, 5, 7, 11, 37, 251, 541]:
            x = rand(n)
            assert_array_almost_equal(self.reference(x), self.func(x))

    def test_definition(self):
        def _test(x):
            for n in range(1, len(x) * 2):
                y = self.func(x, n)
                y1 = self.reference(x, n)
                assert_array_almost_equal(y, y1)
        x = np.array([1, 2, 3, 4, 5])
        _test(x)
        x = np.array([1, 2, 3, 4, 5, 6])
        _test(x)

    def test_n_argument(self):
        x1 = np.array([1, 2, 3, 4])
        x2 = np.array([1, 2, 3, 4])
        for n in range(1, 2*len(x1) - 1):
            y = self.func([x1, x2], n)
            assert_array_almost_equal(y[0], self.reference(x1, n))
            assert_array_almost_equal(y[1], self.reference(x2, n))

class TestRFFT1d(_TestBaseReal1d):
    def reference(self, x, n=None):
        return direct_rdft(x, n)

    def func(self, x, n=None):
        return np.fft.rfft(x, n)

class TestIRFFT1d(_TestBaseReal1d):
    def reference(self, x, n=None):
        return direct_irdft(x, n)

    def func(self, x, n=None):
        return np.fft.irfft(x, n)

if __name__ == "__main__":
    run_module_suite()
