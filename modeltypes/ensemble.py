"""Class for loading an ensemble of data, for post-processing etc

Given many variables on different levels and in different models, we may
need a standardised way to refer to, e.g., 2-m temp (T2m? T? TEMP? etc)

TODO:
    * Maybe we use RawArray to do faster multiprocessing if needed
    * Watch out for space - will need to decide on which products to download

"""

import os
import pdb
import collections

import numpy as np
import xarray as xr
import pandas as pd

import utils.utils as utils
from valpomet.modeltypes.gefs import GEFS

class Ensemble:
    def __init__(self,fpaths):
        self.fpaths = fpaths
        self.fileclass = GEFS
        self.ensemble = self.form_ensemble()
        # Implemented only for GEFS so far

    def form_ensemble(self):
        """Set up the ensemble of forecast-member metadata.

        For each member/filepath passed into __init__ via fpath, its metadata 
        is put into a list of NamedTuples that specify each member. However,
        this list does not contain the forecast data itself (that is elsewhere
        depending on whether rawarrays or numpy arrays are used). Note that 
        extra products like ensemble mean can be appended to this ensemble
        list. If you want to access only "original" forecast members, use the
        original_members_only() method.
        """
        # member_names []
        ensemble = []
        # Can name member better than this another time
        for member_n,fpath in enumerate(self.fpaths):
            # member_names.append(
            member_name = f"m{member_n:03d}"
            ens = self.return_member_namedtuple(member_name,fpath,)
            ensemble.append(ens)
        # return member_names, ensemble
        return ensemble

    def return_member_namedtuple(self,member_name,fpath,init_time=None):
        """Create a NamedTuple for a given ensemble member.

        These NamedTuples are then appended to the instance attribute
        self.ensemble. Forecast data is elsewhere.

        Args:
            member_name: The member name! Make sure each name is unique.
                You might use the create_member_fullname() staticmethod
                herein (i.e., you can use the method before instantiating
                the class) to create those unique names if you have
                multiple initialiation times for the data.
            fpath: the absolute filepath to the datafile for this member
            init_time: The member's initialisation time. If None, this is taken
                automatically from the datafile metadata. If init_time is specified, 
                it overrides any metadata regarding init_time.

        TODO:
            * Not sure what happens if two members are given the same name... 
        """
        # These are the attributes each member may have.
        keys = ("name","fpath","class_inst","valid_time",
                    "init_time","full_name",)
        # This is the template for producing members' NamedTuples.
        EnsembleMember = collections.namedtuple("EnsembleMember",
                keys,
                # Don't forget: defaults go from the right side of
                # the keys list.
                defaults=[None,None]
                )

        # Things like ensemble mean, which can be computed and added later,
        # don't have a file path.
        if fpath is not None:
            fc = self.fileclass(fpath,)
        else:
            fc = None

        # An initialisation time must be specified or taken from metadata
        if init_time is None:
            try:
                fc = self.fileclass(fpath,)
                init_time = fc.init_time
            except:
                print("Initialisation time must be specified or in metadata")
                raise Exception

        # Note that full_name isn't added here...?! Delete from keys above?
        return EnsembleMember(name=member_name,
                            fpath=fpath,
                            valid_time=self.fileclass(fpath).valid_time,
                            init_time=init_time,
                            class_inst=fc,
                            # full_name=full_name,
                            )

    def get(self,vrbl,utc=None,lv=None,lats=None,lons=None,members=None):
        if members is None:
            members = len(self.ensemble)
        arrs = []
        others = []
        for mem_nt in self.ensemble:
            # if mem_nt.member in members:
            arr, units, z_coords = mem_nt.class_inst.get(vrbl,utc=utc,lv=lv,lats=lats,
                            lons=lons,return_z_coords=True,return_units=True)
            arrs.append(arr)
            # others.append(extras)
            
        arrs = np.array(arrs).squeeze()
        # [member_num,level,lats,lons]
        # There is only one time.
        # pdb.set_trace()

        # units = self.get_units(vrbl)
        # z_coords = self.get_z_coords(vrbl)
        return arrs,units,z_coords

    # def get_units(self,vrbl):
        

    def get_exceedence(self,vrbl,thresh):
        # the probability of exceeding a threshold
        return
