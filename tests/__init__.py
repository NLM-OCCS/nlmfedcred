import os
from copy import deepcopy


def restore_env(func, *args, **kwargs):
    def wrapfunc(*args, **kwargs):
        oldenv = deepcopy(os.environ)
        retval = func(*args, **kwargs)
        os.environ = oldenv
        return retval
    return wrapfunc


def setup_awsconfig(tmpdir, mockbundle=None):
    awsconfig = tmpdir.join('aws-config')
    if mockbundle:
        awsconfig.write('[default]\nca_bundle = {}\n'.format(mockbundle))
    else:
        awsconfig.write('[default]\n')
    return str(awsconfig)
