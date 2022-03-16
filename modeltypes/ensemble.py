"""Class for loading an ensemble of data, for post-processing etc

Given many variables on different levels and in different models, we may
need a standardised way to refer to, e.g., 2-m temp (T2m? T? TEMP? etc)

TODO:
    * Maybe we use RawArray to do faster multiprocessing if needed
    * Watch out for space - will need to decide on which products to download

"""

import os
import pdb

from valpomet.modeltypes.gefs import GEFS

class Ensemble:
    def __init__(self,f_info):
        self.members = self.form_ensemble(f_info)

    def form_ensemble(self,f_info):
        for f in f_info:
            # Named tuple per member
            # xarray lazy loading where possible?

            # file location, init time, valid time, etc
            pass
        return

    def get(self,vrbl,utc,lv,lats,lons):
        pass

    def get_exceedence(self,vrbl,thresh):
        # the probability of exceeding a threshold
