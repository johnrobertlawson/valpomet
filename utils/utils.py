import pdb
# import dill
import pickle
import time
import datetime
import functools
import time

import numpy as np

def time_this(f):
    @functools.wraps(f)
    def wrap(*args, **kw):
        t0 = time.time()
        result = f(*args, **kw)
        t1 = time.time()
        dt_sec = t1-t0
        t_totalsec = dt_sec # Testing

        t_min = int(np.floor(t_totalsec/60))
        t_sec = int(t_totalsec % 60)
        print(f"Function {f.__name__} took {t_min:02d} min, {t_sec:02d} sec.")
        return result
    return wrap

def save_pickle(obj,fpath,use_dill=False):
    """Dill not installed by default.
    """
    func = dill if use_dill is True else pickle
    with open(fpath,"wb") as f:
        func.dump(obj,f)
    return

def load_pickle(fpath,use_dill=False):
    """Dill not installed by default.
    """
    func = dill if use_dill is True else pickle
    with open(fpath,"rb") as f:
        x = func.load(f)
    return x
