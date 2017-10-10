import os
from copy import deepcopy


def restore_env(func, *args, **kwargs):
    def wrapfunc(*args, **kwargs):
        oldenv = deepcopy(os.environ)
        retval = func(*args, **kwargs)
        os.environ = oldenv
        return retval
    return wrapfunc
