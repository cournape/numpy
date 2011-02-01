import os
import re

import waflib.Configure
from waflib import Logs, Utils

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
        if kw['execute'] and kw.get('define_ret', None) and isinstance(is_success, str):
            self.define_with_comment(kw['define_name'], is_success, cmt, quote=kw.get('quote', 1))
        else:
            self.define_cond(kw['define_name'], is_success, cmt)

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
        self.define_with_comment(name, 1, comment)
    else:
        self.undefine(name)

@waflib.Configure.conf
def get_config_header(self):
    """Fill-in the contents of the config header. Override when you need to write your own config header."""
    config_header = []

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
    return "\n".join(config_header)
