#ifndef _NPY_UMATH_CYTHON_H_
#define _NPY_UMATH_CYTHON_H_

/*
 * _UMATHMODULE IS needed in __ufunc_api.h, included from numpy/ufuncobject.h.
 * This is a mess and it would be nice to fix it. It has nothing to do with
 * __ufunc_api.c
 */
#define _UMATHMODULE
#define NPY_NO_DEPRECATED_API NPY_API_VERSION

#include "Python.h"

#include "npy_config.h"
#ifdef ENABLE_SEPARATE_COMPILATION
#define PY_ARRAY_UNIQUE_SYMBOL _npy_umathmodule_ARRAY_API
#endif

#include "numpy/arrayobject.h"
#include "numpy/ufuncobject.h"

extern void** PyUFunc_API;

NPY_NO_EXPORT void
npy_capi_init_operators(PyObject *d);

#endif
