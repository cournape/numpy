import os
import sys
import shutil
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import waflib.Logs
import waflib.Configure
import waflib.Utils
import waflib.TaskGen
import waflib.Task

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

def post_build(bld):
    # Poor man's replacement for in-place build
    if "-i" in sys.argv:
        for g in bld.groups:
            for task_gen in g:
                if hasattr(task_gen, "link_task"):
                    ltask = task_gen.link_task
                    for output in ltask.outputs:
                        if not output.is_child_of(bld.srcnode):
                            shutil.copy(output.abspath(), output.path_from(bld.bldnode))
                elif "gen_pymodule" in task_gen.features:
                    for output in task_gen.tasks[0].outputs:
                        if not output.is_child_of(bld.srcnode):
                            shutil.copy(output.abspath(), output.path_from(bld.bldnode))

# FIXME: abstract those module gen tasks...
class write_module(waflib.Task.Task):
    color = "CYAN"
    vars = ["CONTENT"]
    def run(self):
        # FIXME: put actual data here
        self.outputs[0].write(self.env.CONTENT)

@waflib.TaskGen.feature("gen_pymodule")
def process_write_config(self):
    if not hasattr(self, "content"):
        raise ValueError("task gen %r expects a 'content' argument" % self.name)
    else:
        self.env.CONTENT = self.content
    tsk = self.create_task("write_module")
    tsk.set_outputs(self.path.find_or_declare(self.target))
    return tsk

def build(bld):
    bld.recurse("numpy/core")
    bld.recurse("numpy/fft")
    bld.recurse("numpy/lib")
    bld.recurse("numpy/linalg")
    bld.recurse("numpy/random")

    bld(features="gen_pymodule",
        target="numpy/__config__.py",
        content="""\
def show():
    pass
""",
        always=True)
    bld(features="gen_pymodule",
        target="numpy/version.py",
        content="""\
git_revision = ""
version = ""
""",
        always=True)

    bld.add_post_fun(post_build)
