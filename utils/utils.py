import pdb
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
