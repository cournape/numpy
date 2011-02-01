import os
import re

import waflib.Configure
from waflib import Logs, Utils

from setup_common \
    import \
        LONG_DOUBLE_REPRESENTATION_SRC, pyod, long_double_representation

DEFINES = waflib.Tools.c_config.DEFINES
UNDEFINED = waflib.Tools.c_config.UNDEFINED
DEFINE_COMMENTS = "define_commentz"

def to_header(dct):
    if 'header_name' in dct:
        dct = Utils.to_list(dct['header_name'])
        return ''.join(['#include <%s>\n' % x for x in dct])
    return ''

# Make the given string safe to be used as a CPP macro
def sanitize_string(s):
    key_up = s.upper()
    return re.sub('[^A-Z0-9_]', '_', key_up)

def validate_arguments(self, kw):
    if not 'env' in kw:
        kw['env'] = self.env.derive()
    if not "compile_mode" in kw:
        kw["compile_mode"] = "c"
    if not 'compile_filename' in kw:
        kw['compile_filename'] = 'test.c' + \
                ((kw['compile_mode'] == 'cxx') and 'pp' or '')
    if not 'features' in kw:
        kw['features'] = [kw['compile_mode']]
    if not 'execute' in kw:
        kw['execute'] = False
    if not 'okmsg' in kw:
        kw['okmsg'] = 'yes'
    if not 'errmsg' in kw:
        kw['errmsg'] = 'no !'

def try_compile(self, kw):
    self.start_msg(kw["msg"])
    ret = None
    try:
        ret = self.run_c_code(**kw)
    except self.errors.ConfigurationError as e:
        self.end_msg(kw['errmsg'], 'YELLOW')
        if Logs.verbose > 1:
            raise
        else:
            self.fatal('The configuration failed')
    else:
        kw['success'] = ret
        self.end_msg(self.ret_msg(kw['okmsg'], kw))

@waflib.Configure.conf
def check_header(self, header_name, **kw):
    code = """
%s

int main()
{
}
""" % to_header({"header_name": header_name})

    kw["code"] = code
    kw["define_comment"] = "/* Define to 1 if you have the `%s' header. */" % header_name
    kw["define_name"] = "HAVE_%s" % sanitize_string(header_name)
    if not "features" in kw:
        kw["features"] = ["c"]
    kw["msg"] = "Checking for header %r" % header_name

    validate_arguments(self, kw)
    try_compile(self, kw)
    ret = kw["success"]

    self.post_check(**kw)
    if not kw.get('execute', False):
        return ret == 0
    return ret

@waflib.Configure.conf
def check_declaration(self, symbol, **kw):
    code = r"""
int main()
{
#ifndef %s
    (void) %s;
#endif
    ;
    return 0;
}
""" % (symbol, symbol)

    kw["code"] = to_header(kw) + code
    kw["msg"] = "Checking for macro %r" % symbol
    kw["errmsg"] = "not found"
    kw["okmsg"] = "yes"

    validate_arguments(self, kw)
    try_compile(self, kw)
    ret = kw["success"]

    kw["define_name"] = "HAVE_DECL_%s" % sanitize_string(symbol)
    kw["define_comment"] = "/* Set to 1 if %s is defined. */" % symbol
    self.post_check(**kw)
    if not kw.get('execute', False):
        return ret == 0
    return ret

@waflib.Configure.conf
def check_type(self, type_name, **kw):
    code = r"""
int main() {
	if ((%(type_name)s *) 0)
        return 0;
	if (sizeof (%(type_name)s))
        return 0;
}
""" % {"type_name": type_name}

    kw["code"] = to_header(kw) + code
    kw["msg"] = "Checking for type %r" % type_name
    kw["errmsg"] = "not found"
    kw["okmsg"] = "yes"

    validate_arguments(self, kw)
    try_compile(self, kw)
    ret = kw["success"]

    kw["define_name"] = "HAVE_%s" % sanitize_string(type_name)
    kw["define_comment"] = "/* Set to 1 if %s is defined. */" % type_name
    self.post_check(**kw)
    if not kw.get('execute', False):
        return ret == 0
    return ret

def do_binary_search(conf, type_name, kw):
    code = """\
typedef %(type)s waf_check_sizeof_type;
int main ()
{
    static int test_array [1 - 2 * !(((long) (sizeof (waf_check_sizeof_type))) >= 0)];
    test_array [0] = 0

    ;
    return 0;
}
""" % {"type": type_name}
    kw["code"] = to_header(kw) + code

    try:
        conf.run_c_code(**kw)
    except conf.errors.ConfigurationError, e:
        conf.end_msg("failed !")
        if waflib.Logs.verbose > 1:
            raise
        else:
            conf.fatal("The configuration failed !")

    body = r"""
typedef %(type)s waf_check_sizeof_type;
int main ()
{
    static int test_array [1 - 2 * !(((long) (sizeof (waf_check_sizeof_type))) <= %(size)s)];
    test_array [0] = 0

    ;
    return 0;
}
"""
    # The principle is simple: we first find low and high bounds
    # of size for the type, where low/high are looked up on a log
    # scale. Then, we do a binary search to find the exact size
    # between low and high
    low = 0
    mid = 0
    while True:
        try:
            kw["code"] = to_header(kw) + body % {"type": type_name, "size": mid}
            validate_arguments(conf, kw)
            conf.run_c_code(**kw)
            break
        except conf.errors.ConfigurationError:
            #log.info("failure to test for bound %d" % mid)
            low = mid + 1
            mid = 2 * mid + 1

    high = mid
    ret = None
    # Binary search:
    while low != high:
        mid = (high - low) / 2 + low
        try:
            kw["code"] = to_header(kw) + body % {"type": type_name, "size": mid}
            validate_arguments(conf, kw)
            ret = conf.run_c_code(**kw)
            high = mid
        except conf.errors.ConfigurationError:
            low = mid + 1

    return low

@waflib.Configure.conf
def check_type_size(conf, type_name, expected_size=None, **kw):
    kw["define_name"] = "SIZEOF_%s" % sanitize_string(type_name)
    kw["define_comment"] = "/* The size of `%s', as computed by sizeof. */" % type_name
    kw["msg"] = "Checking sizeof(%s)" % type_name

    validate_arguments(conf, kw)
    conf.start_msg(kw["msg"])

    if expected_size is not None:
        code = """\
typedef %(type)s waf_check_sizeof_type;
int main ()
{
    static int test_array [1 - 2 * !(((long) (sizeof (waf_check_sizeof_type))) == %(size)d)];
    test_array [0] = 0

    ;
    return 0;
}
""" % {"type": type_name, "size": expected_size}
        kw["code"] = code
        try:
            conf.run_c_code(**kw)
            size = expected_size
        except conf.errors.ConfigurationError:
            size = do_binary_search(conf, type_name, kw)
    else:
        size = do_binary_search(conf, type_name, kw)

    kw["define_value"] = size
    kw["success"] = 0
    conf.end_msg(size)
    conf.post_check(**kw)
    return size

@waflib.Configure.conf
def check_functions_at_once(self, funcs, **kw):
    header = []
    header = ['#ifdef __cplusplus']
    header.append('extern "C" {')
    header.append('#endif')
    for f in funcs:
        header.append("\tchar %s();" % f)
        # Handle MSVC intrinsics: force MS compiler to make a function
        # call. Useful to test for some functions when built with
        # optimization on, to avoid build error because the intrinsic
        # and our 'fake' test declaration do not match.
        header.append("#ifdef _MSC_VER")
        header.append("#pragma function(%s)" % f)
        header.append("#endif")
    header.append('#ifdef __cplusplus')
    header.append('};')
    header.append('#endif')
    funcs_decl = "\n".join(header)

    tmp = []
    for f in funcs:
        tmp.append("\t%s();" % f)
    tmp = "\n".join(tmp)

    code = r"""
%(include)s
%(funcs_decl)s

int main (void)
{
    %(tmp)s
        return 0;
}
""" % {"tmp": tmp, "include": to_header(kw), "funcs_decl": funcs_decl}
    kw["code"] = code
    if not "features" in kw:
        kw["features"] = ["c", "cprogram"]

    msg = ", ".join(funcs)
    if len(msg) > 30:
        _funcs = list(funcs)
        msg = []
        while len(", ".join(msg)) < 30 and _funcs:
            msg.append(_funcs.pop(0))
        msg = ", ".join(msg) + ",..."
    if "lib" in kw:
        kw["msg"] = "Checking for functions %s in library %r" % (msg, kw["lib"])
    else:
        kw["msg"] = "Checking for functions %s" % msg

    validate_arguments(self, kw)
    try_compile(self, kw)
    ret = kw["success"]

    # We set the config.h define here because we need to define several of them
    # in one shot
    if ret == 0:
        for f in funcs:
            self.define_with_comment("HAVE_FUNC_%s" % sanitize_string(f), 1,
                                "/* Define to 1 if you have the `%s' function */" % f)

    self.post_check(**kw)
    if not kw.get('execute', False):
        return ret == 0
    return ret

@waflib.Configure.conf
def check_inline(conf, **kw):
    validate_arguments(conf, kw)

    code = """
#ifndef __cplusplus
static %(inline)s int static_func (void)
{
    return 0;
}
%(inline)s int nostatic_func (void)
{
    return 0;
}
#endif"""

    conf.start_msg("Checking for inline support")
    inline = None
    for k in ['inline', '__inline__', '__inline']:
        try:
            kw["code"] = code % {"inline": k}
            ret = conf.run_c_code(**kw)
            inline = k
            break
        except conf.errors.ConfigurationError:
            pass

    if inline is None:
        conf.end_msg("failed", 'YELLOW')
        if Logs.verbose > 1:
            raise
        else:
            conf.fatal('The configuration failed')
    else:
        kw['success'] = ret
        conf.end_msg(inline)
        return inline

@waflib.Configure.conf
def check_ldouble_representation(conf, **kw):
    msg = {
        'INTEL_EXTENDED_12_BYTES_LE': "Intel extended, little endian",
        'INTEL_EXTENDED_16_BYTES_LE': "Intel extended, little endian",
        'IEEE_QUAD_BE': "IEEE Quad precision, big endian",
        'IEEE_QUAD_LE': "IEEE Quad precision, little endian",
        'IEEE_DOUBLE_LE': "IEEE Double precision, little endian",
        'IEEE_DOUBLE_BE': "IEEE Double precision, big endian"
    }

    code = LONG_DOUBLE_REPRESENTATION_SRC % {'type': 'long double'}
    validate_arguments(conf, kw)

    conf.start_msg("Checking for long double representation... ")
    try:
        kw["code"] = code
        ret = conf.run_c_code(**kw)
    except conf.errors.ConfigurationError as e:
        conf.end_msg(kw['errmsg'], 'YELLOW')
        if Logs.verbose > 1:
            raise
        else:
            conf.fatal('The configuration failed')
    else:
        task_gen = conf.test_bld.groups[0][0]
        obj_filename = task_gen.tasks[0].outputs[0].abspath()
        tp = long_double_representation(pyod(obj_filename))
        kw['success'] = ret
        conf.end_msg(msg[tp])
        kw["define_name"] = "HAVE_LDOUBLE_%s" % tp
        kw["define_comment"] = "/* Define for arch-specific long double representation */"
    ret = kw["success"]

    conf.post_check(**kw)
    if not kw.get('execute', False):
        return ret == 0
    return ret

@waflib.Configure.conf
def post_check(self, *k, **kw):
    "set the variables after a test was run successfully"

    is_success = 0
    if kw['execute']:
        if kw['success'] is not None:
            is_success = kw['success']
    else:
        is_success = (kw['success'] == 0)

    def define_or_stuff():
        nm = kw['define_name']
        cmt = kw.get('define_comment', None)
        value = kw.get("define_value", is_success)
        if kw['execute'] and kw.get('define_ret', None) and isinstance(is_success, str):
            self.define_with_comment(kw['define_name'], value, cmt, quote=kw.get('quote', 1))
        else:
            self.define_cond(kw['define_name'], value, cmt)

    if 'define_name' in kw:
        define_or_stuff()

    if is_success and 'uselib_store' in kw:
        from waflib.Tools import ccroot

        # TODO see get_uselib_vars from ccroot.py
        _vars = set([])
        for x in kw['features']:
            if x in ccroot.USELIB_VARS:
                _vars |= ccroot.USELIB_VARS[x]

        for k in _vars:
            lk = k.lower()
            if k == 'INCLUDES': lk = 'includes'
            if k == 'DEFINES': lk = 'defines'
            if lk in kw:
                val = kw[lk]
                # remove trailing slash
                if isinstance(val, str):
                    val = val.rstrip(os.path.sep)
                self.env.append_unique(k + '_' + kw['uselib_store'], val)

@waflib.Configure.conf
def define_with_comment(conf, define, value, comment=None, quote=True):
    if comment is None:
        return conf.define(define, value, quote)

    assert define and isinstance(define, str)

    comment_tbl = conf.env[DEFINE_COMMENTS] or waflib.Utils.ordered_dict()
    comment_tbl[define] = comment
    conf.env[DEFINE_COMMENTS] = comment_tbl

    return conf.define(define, value, quote)

@waflib.Configure.conf
def define_cond(self, name, value, comment):
    """Conditionally define a name.
    Formally equivalent to: if value: define(name, 1) else: undefine(name)"""
    if value:
        self.define_with_comment(name, value, comment)
    else:
        self.undefine(name)

@waflib.Configure.conf
def get_config_header(self):
    """Fill-in the contents of the config header. Override when you need to write your own config header."""
    config_header = []

    tpl = self.env["CONFIG_HEADER_TEMPLATE"] or "%(content)s"
    tbl = self.env[DEFINES] or waflib.Utils.ordered_dict()
    cmt = self.env[DEFINE_COMMENTS] or waflib.Utils.ordered_dict()
    for key in tbl.allkeys:
        value = tbl[key]
        if key in cmt:
            config_header.append(cmt[key])
        if value is None:
            config_header.append('#define %s' % key)
        elif value is UNDEFINED:
            config_header.append('/* #undef %s */' % key)
        elif isinstance(value, str):
            config_header.append('#define %s %s' % (key, repr(value)[1:-1]))
        else:
            config_header.append('#define %s %s' % (key, value))
        config_header.append('')
    return tpl % {"content": "\n".join(config_header)}
