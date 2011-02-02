import os
import sys
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import waflib.Logs
import waflib.Configure
import waflib.Utils

# Ugly but necessary hack: import numpy here so that wscript in sub directories
# will see this numpy and not an already installed one
import __builtin__
__builtin__.__NUMPY_SETUP__ = True
import numpy

waflib.Configure.autoconfig = True

top = '.'
out = 'build'

def options(opt):
    opt.tool_options('python') # options for disabling pyc or pyo compilation
    opt.tool_options('compiler_cc')
    opt.add_option('-i', dest='inplace', action="store_true")

def configure(conf):
    conf.check_tool('compiler_cc')
    conf.check_tool('python')
    conf.check_python_version((2, 4, 0))
    conf.check_python_headers()

    conf.recurse("numpy/core")

def build(bld):
    bld.recurse("numpy/core")
    bld.recurse("numpy/lib")

    # Poor man's replacement for in-place build
    if "-i" in sys.argv:
        for g in bld.groups:
            for task_gen in g:
                if hasattr(task_gen, "link_task"):
                    #print dir(task_gen)
                    #print type(task_gen.target)
                    print task_gen.link_task
