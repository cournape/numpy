from libc.stdio cimport printf

from cpython.object cimport PyObject
from cpython.ref cimport PyTypeObject, Py_TYPE

cdef extern from "Python.h":
    bint PyType_Ready(PyTypeObject*)

cdef extern from "numpy/npy_3kcompat.h":
    object NpyCapsule_FromVoidPtr(void *ptr, void (*dtor)(PyObject *))

cdef extern from "numpy/ndarrayobject.h":
    bint npy_capi_init_operators(object)

cdef extern from "umath_cython.h":
    int _import_array();
    struct PyUFuncObject:
        pass
    void** PyUFunc_API;
    PyTypeObject PyUFunc_Type;

    int UFUNC_ERR_IGNORE;
    int UFUNC_ERR_WARN;
    int UFUNC_ERR_CALL;
    int UFUNC_ERR_RAISE;
    int UFUNC_ERR_PRINT;
    int UFUNC_ERR_LOG;
    int UFUNC_ERR_DEFAULT;

    int UFUNC_SHIFT_DIVIDEBYZERO;
    int UFUNC_SHIFT_OVERFLOW;
    int UFUNC_SHIFT_UNDERFLOW;
    int UFUNC_SHIFT_INVALID;

    int UFUNC_FPE_DIVIDEBYZERO;
    int UFUNC_FPE_OVERFLOW;
    int UFUNC_FPE_UNDERFLOW;
    int UFUNC_FPE_INVALID;

    int UFUNC_FLOATING_POINT_SUPPORT;

    int UFUNC_FLOATING_POINT_SUPPORT;

    char* UFUNC_PYVALS_NAME;


# 'private' C API of umath
cdef extern from "umathmodule.h":
    object npy_capi_ufunc_frompyfunc(object function, int nin, int nout);
    object npy_capi_add_newdoc_ufunc(PyUFuncObject *ufunc, char* docstr);
    object npy_capi_ufunc_geterr();
    object npy_capi_ufunc_seterr(object val);


def frompyfunc(function, int nin, int nout):
    return npy_capi_ufunc_frompyfunc(function, nin, nout)


def geterrobj():
    return npy_capi_ufunc_geterr()


def seterrobj(val):
    return npy_capi_ufunc_seterr(val)


def _add_newdoc_ufunc(ufunc, char* docstr):
    cdef PyUFuncObject *ufunc_ptr;

    if Py_TYPE(ufunc) != &PyUFunc_Type:
        raise ValueError("Object {0!r} is not a ufunc !")
    else:
        ufunc_ptr = <PyUFuncObject*>ufunc
        return npy_capi_add_newdoc_ufunc(ufunc_ptr, docstr)


def _import_init():
    cdef int status;
    d = globals()
    
    if (_import_array() < 0):
        raise ImportError("_import_array failed")

    if PyType_Ready(&PyUFunc_Type) < 0:
        raise ImportError("PyType_Ready call failed")

    npy_capi_init_operators(d)


def _init_capsule():
    return NpyCapsule_FromVoidPtr(<void *>PyUFunc_API, NULL);

print("start init")

_import_init()

_UFUNC_API = _init_capsule()

__version__ = "0.4.0"

ERR_IGNORE = UFUNC_ERR_IGNORE
ERR_WARN = UFUNC_ERR_WARN
