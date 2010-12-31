import numpy as np

def prepare_array(x, n=None):
    if n is None:
        n = len(x)
    elif n < len(x):
        x = x[:n]
    elif n > len(x):
        y = np.zeros(n, x.dtype)
        y[:len(x)] = x
        x = y
    return x, n

def direct_dft(x, n=None):
    x, n = prepare_array(x, n)
    return _direct_dft(x, n, dir=1)

def direct_idft(x, n=None):
    x, n = prepare_array(x, n)
    return _direct_dft(x, n, dir=-1)

def _direct_dft(x, n, dir=1):
    phase = -2j*dir*np.pi*(np.arange(n)/float(n))
    phase = np.arange(n).reshape(-1, 1) * phase
    ret = np.sum(x*np.exp(phase), axis=1)
    if dir == -1:
        ret /= n
    return ret

def direct_rdft(x, n=None):
    x, n = prepare_array(x, n)
    r = _direct_dft(x, n, 1)
    return r[:n/2+1]

def direct_irdft(x, n=None):
    x = np.asarray(x)
    if n is None:
        n = (x.size - 1) * 2
    if n >= x.size * 2:
        y = np.zeros(n, x.dtype)
        y[:x.size] = x
        x = y
    cra = np.zeros(n, np.complex)
    if n % 2 == 0:
        p = n / 2
        cra[:p+1] = x[:p+1]
        cra[p+1:] = np.conj(x[1:p])[::-1]
    else:
        p = n / 2 + 1
        cra[:p] = x[:p]
        cra[p:] = np.conj(x[1:p])[::-1]
    return _direct_dft(cra, n, dir=-1).real

