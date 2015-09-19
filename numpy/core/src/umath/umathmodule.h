#ifndef _UMATHMODULE_H_
#define _UMATHMODULE_H_

PyObject *
npy_capi_ufunc_frompyfunc(PyObject* function, int nin, int nout);

PyObject*
npy_capi_add_newdoc_ufunc(PyUFuncObject *ufunc, char* docstr);

NPY_NO_EXPORT PyObject *
npy_capi_ufunc_geterr(void);

NPY_NO_EXPORT PyObject *
npy_capi_ufunc_seterr(PyObject *val);

NPY_NO_EXPORT int
yolo(void);

#endif
