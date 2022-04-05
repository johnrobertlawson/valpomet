"""Class for opening GEFS files - use with Ensemble class.
"""

import itertools
import os
import pdb
import datetime
import wget
import glob

import numpy as np
import pandas as pd
import xarray as xr

class GEFS:
    def __init__(self,fpath=None):
        self.fpath = fpath
        self.lazy_load = True
        self.xrobj, self.metadata = self.get_data_metadata()

        #### KEY METADATA
        # self.utc = self.xrobj.time.dt
        # self.valid_time = self.xrobj.time.values
        self.valid_time = self.xrobj.coords["time"].data[0]
        self.init_time = self.xrobj.coords["reftime"].data
        self.forecast_hour = self.valid_time - self.init_time
        # datetime64[ns] format

        self.gefs_type = self.get_gefs_type()
        self.member_name = self.get_gefs_member_name()

        self.inventory = self.get_inventory()
        self.lats, self.lons = self.get_latlons()
        # self.print_inventory(write_to_file=True)
        # pdb.set_trace()

    def get_latlons(self):
        return self.xrobj.coords["lat"].data, self.xrobj.coords["lon"].data

    def get_gefs_type(self):
        _types = {"pgrb2a","pgrb2s","pgrb2b"}
        for _type in _types:
            if _type in self.fpath:
                return _type
        raise Exception
            
    def get_gefs_member_name(self):
        possibilities = ["gec00",] + [f"gep{n:02d}" for n in range(1,31)]
        for p in possibilities:
            if p in self.fpath:
                return p
        raise Exception

    def print_inventory(self,write_to_file=False):
        for x in self.inventory:
            print(x)
        if write_to_file:
            fpath = f"GEFS_{self.gefs_type}_inventory.txt"
            with open(fpath,"w") as f:
                for x in self.inventory:
                    f.write(f"{x}\n")
        return

    def get_inventory(self):
        prods = sorted(self.metadata["data_vars"].keys())
        return prods

    def parse_metadata(self):
        self.dims = self.metadata["dims"]
        return

    def get(self,vrbl,utc=None,lv=None,lats=None,lons=None,lv_str=None,
                return_z_coords=True,return_units=True,
                return_latlon=False):
        """

        lv_Str should be e.g.  height_above_ground1 - how to get coord?
        """
        if not all([utc,lv,lats,lons]):
            dataset = self.xrobj.data_vars.get(vrbl)
            # pdb.set_trace()
            units = dataset.units
            lats = dataset.lat
            lons = dataset.lon

            data = dataset.data
            # (1,1,361,720) shape for v-comp of wind trop vrbl
            
            # To find vertical coord system, find that name
            if lv_str is None:
                vertical_coord = []
                for coo in self.xrobj.get(vrbl).coords:
                    if coo not in ("lat","lon","reftime","time","ens"):
                        vertical_coord.append(coo)

                if len(vertical_coord) != 1:
                    print("Only one vertical level.")
                    z_coords = None
                else:
                    lv_str = vertical_coord[0]
                    z_coords = self.xrobj.get(vrbl).coords.get(lv_str).data
            
        rets = [data,]
        if return_units:
            rets.append(units)
        if return_latlon:
            rets.extend([lats,lons])
        if return_z_coords:
            rets.append(z_coords)
        
        return rets 

    def get_data_metadata(self):
        """
        #######################
        # This is for the file GEFS_gec00.t12z.pgrb2s.0p25.f003.nc
        # product : "sp25"
        #######################

        # keys in metadata.keys():
        # dict_keys(['coords', 'attrs', 'dims', 'data_vars'])

        # metadata["coords"].keys():
        # dict_keys(['lat', 'lon', 'reftime', 'time', 'time1', 
        #            'height_above_ground', 'pressure_difference_layer', 
        # 'height_above_ground1', 'height_above_ground_layer', 
        # 'depth_below_surface_layer', 'ens'])`

        # metadata["attrs"].keys()
        # dict_keys(['Originating_or_generating_Center', 
        # 'Originating_or_generating_Subcenter', 'GRIB_table_version', 
        # 'Type_of_generating_process', 
        # 'Analysis_or_forecast_generating_process_identifier_defined_by_originating_centre', 
        # 'file_format', 'Conventions', 'history', 'featureType'])

        # metadata["dims"].keys()
        # dict_keys(['lat', 'lon', 'time', 'time1', 'anon0', 
        # 'height_above_ground', 'pressure_difference_layer', 'anon1', 
        # 'height_above_ground1', 'height_above_ground_layer', 'anon2', 
        # 'depth_below_surface_layer', 'anon3', 'ens'])

        # metadata["data_vars"].keys():
        # dict_keys(['LatLon_Projection', 'time1_bounds', 
        # 'pressure_difference_layer_bounds', 'height_above_ground_layer_bounds', 
        # 'depth_below_surface_layer_bounds', 'Convective_available_potential_energy_surface_ens', 
        # 'Convective_available_potential_energy_pressure_difference_layer_ens', 
        # 'Convective_inhibition_surface_ens', 'Convective_inhibition_pressure_difference_layer_ens', 
        # 'Dewpoint_temperature_height_above_ground_ens', 'Ice_thickness_surface_ens', 
        # 'Latent_heat_net_flux_surface_3_Hour_Average_ens', 
        # 'Maximum_temperature_height_above_ground_3_Hour_Maximum_ens', 
        # 'Minimum_temperature_height_above_ground_3_Hour_Minimum_ens', 
        # 'Precipitable_water_entire_atmosphere_single_layer_ens', 'Pressure_surface_ens', 
        # 'Pressure_reduced_to_MSL_msl_ens', 'Relative_humidity_height_above_ground_ens', 
        # 'Sensible_heat_net_flux_surface_3_Hour_Average_ens', 'Snow_depth_surface_ens', 
        # 'Soil_temperature_depth_below_surface_layer_ens', 
        # 'Storm_relative_helicity_height_above_ground_layer_ens', 
        # 'Temperature_height_above_ground_ens', 
        # 'Total_cloud_cover_entire_atmosphere_3_Hour_Average_ens', 
        # 'Total_precipitation_surface_3_Hour_Accumulation_ens', 
        # 'Categorical_Rain_surface_3_Hour_Average_ens', 
        # 'Categorical_Freezing_Rain_surface_3_Hour_Average_ens', 
        # 'Categorical_Ice_Pellets_surface_3_Hour_Average_ens', 
        # 'Categorical_Snow_surface_3_Hour_Average_ens', 'MSLP_Eta_model_reduction_msl_ens', 
        # 'Downward_Short-Wave_Radiation_Flux_surface_3_Hour_Average_ens',
        # 'Upward_Short-Wave_Radiation_Flux_surface_3_Hour_Average_ens', 
        # 'Downward_Long-Wave_Radp_Flux_surface_3_Hour_Average_ens', 
        # 'Upward_Long-Wave_Radp_Flux_surface_3_Hour_Average_ens', 
        # 'Upward_Long-Wave_Radp_Flux_atmosphere_top_3_Hour_Average_ens', 
        # 'Volumetric_Soil_Moisture_Content_depth_below_surface_layer_ens', 
        # 'Water_equivalent_of_accumulated_snow_depth_surface_ens', 'Wind_speed_gust_surface_ens', 
        # 'u-component_of_wind_height_above_ground_ens', 'v-component_of_wind_height_above_ground_ens'])

        #########################
        # Trying the same but for pgrb2ap5
        # /storage/gefs_data/GEFS_gec00.t12z.pgrb2a.0p50.f003.nc
        #########################

        # keys in metadata.keys():
        # SAME

        # metadata["coords"].keys()
        # dict_keys(['lat', 'lon', 'reftime', 'time', 'time1', 'isobaric', 
        # 'height_above_ground', 'pressure_difference_layer', 
        # 'height_above_ground1', 'isobaric1', 'depth_below_surface_layer', 
        # 'isobaric2', 'isobaric3', 'ens'])

        # metadata["attrs"].keys()
        # dict_keys(['Originating_or_generating_Center', 'Originating_or_generating_Subcenter', 'GRIB_table_version', 'Type_of_generating_process', 'Analysis_or_forecast_generating_process_identifier_defined_by_originating_centre', 'file_format', 'Conventions', 'history', 'featureType'])

        # metadata["dims"].keys()
        # dict_keys(['lat', 'lon', 'time', 'time1', 'anon0', 'isobaric', 'height_above_ground', 'pressure_difference_layer', 'anon1', 'height_above_ground1', 'isobaric1', 'depth_below_surface_layer', 'anon2', 'isobaric2', 'isobaric3', 'ens'])

        # metadata["data_vars"].keys()
        # dict_keys(['LatLon_Projection', 'time1_bounds', 'pressure_difference_layer_bounds', 'depth_below_surface_layer_bounds', 'Convective_available_potential_energy_pressure_difference_layer_ens', 'Convective_inhibition_pressure_difference_layer_ens', 'Geopotential_height_isobaric_ens', 'Ice_thickness_surface_ens', 'Latent_heat_net_flux_surface_3_Hour_Average_ens', 'Maximum_temperature_height_above_ground_3_Hour_Maximum_ens', 'Minimum_temperature_height_above_ground_3_Hour_Minimum_ens', 'Precipitable_water_entire_atmosphere_single_layer_ens', 'Pressure_surface_ens', 'Pressure_reduced_to_MSL_msl_ens', 'Relative_humidity_isobaric_ens', 'Relative_humidity_height_above_ground_ens', 'Sensible_heat_net_flux_surface_3_Hour_Average_ens', 'Snow_depth_surface_ens', 'Soil_temperature_depth_below_surface_layer_ens', 'Temperature_isobaric_ens', 'Temperature_height_above_ground_ens', 'Total_cloud_cover_entire_atmosphere_3_Hour_Average_ens', 'Total_precipitation_surface_3_Hour_Accumulation_ens', 'Categorical_Rain_surface_3_Hour_Average_ens', 'Categorical_Freezing_Rain_surface_3_Hour_Average_ens', 'Categorical_Ice_Pellets_surface_3_Hour_Average_ens', 'Categorical_Snow_surface_3_Hour_Average_ens', 'Downward_Short-Wave_Radiation_Flux_surface_3_Hour_Average_ens', 'Upward_Short-Wave_Radiation_Flux_surface_3_Hour_Average_ens', 'Downward_Long-Wave_Radp_Flux_surface_3_Hour_Average_ens', 'Upward_Long-Wave_Radp_Flux_surface_3_Hour_Average_ens', 'Upward_Long-Wave_Radp_Flux_atmosphere_top_3_Hour_Average_ens', 'Volumetric_Soil_Moisture_Content_depth_below_surface_layer_ens', 'Vertical_velocity_pressure_isobaric_ens', 'Water_equivalent_of_accumulated_snow_depth_surface_ens', 'u-component_of_wind_isobaric_ens', 'u-component_of_wind_height_above_ground_ens', 'v-component_of_wind_isobaric_ens', 'v-component_of_wind_height_above_ground_ens'])

        ############################
        ## bp5
        ############################

        # metadata.keys()
        # dict_keys(['coords', 'attrs', 'dims', 'data_vars'])

        # metadata["coords"].keys
        # dict_keys(['lat', 'lon', 'reftime', 'time', 'time1', 'height_above_ground', 'isentrope', 'potential_vorticity_surface', 'isentrope1', 'height_above_ground_layer', 'isobaric', 'isobaric1', 'depth_below_surface_layer', 'hybrid', 'altitude_above_msl', 'depth_below_surface_layer1', 'isobaric2', 'isobaric3', 'isobaric4', 'pressure_difference_layer', 'isobaric5', 'height_above_ground1', 'isentrope2', 'height_above_ground_layer1', 'pressure_difference_layer1', 'isobaric6', 'isobaric7', 'sigma_layer', 'isobaric8', 'isobaric9', 'pressure_difference_layer2', 'height_above_ground2', 'isobaric10', 'height_above_ground3', 'sigma', 'ens'])

        # metadata["attrs"].keys()
        # dict_keys(['Originating_or_generating_Center', 'Originating_or_generating_Subcenter', 'GRIB_table_version', 'Type_of_generating_process', 'Analysis_or_forecast_generating_process_identifier_defined_by_originating_centre', 'file_format', 'Conventions', 'history', 'featureType'])


        # metadata["dims"].keys()
        # dict_keys(['lat', 'lon', 'time', 'time1', 'anon0', 'height_above_ground', 'isentrope', 'potential_vorticity_surface', 'isentrope1', 'height_above_ground_layer', 'anon1', 'isobaric', 'isobaric1', 'depth_below_surface_layer', 'anon2', 'hybrid', 'altitude_above_msl', 'depth_below_surface_layer1', 'anon3', 'isobaric2', 'isobaric3', 'isobaric4', 'pressure_difference_layer', 'anon4', 'isobaric5', 'height_above_ground1', 'isentrope2', 'height_above_ground_layer1', 'anon5', 'pressure_difference_layer1', 'anon6', 'isobaric6', 'isobaric7', 'sigma_layer', 'anon7', 'isobaric8', 'isobaric9', 'pressure_difference_layer2', 'anon8', 'height_above_ground2', 'isobaric10', 'height_above_ground3', 'sigma', 'ens'])

        # metadata["data_vars"].keys()
        # dict_keys(['LatLon_Projection', 'time1_bounds', 'height_above_ground_layer_bounds', 'depth_below_surface_layer_bounds', 'depth_below_surface_layer1_bounds', 'pressure_difference_layer_bounds', 'height_above_ground_layer1_bounds', 'pressure_difference_layer1_bounds', 'sigma_layer_bounds', 'pressure_difference_layer2_bounds', 'Absolute_vorticity_isobaric_ens', 'Albedo_surface_3_Hour_Average_ens', 'Apparent_temperature_height_above_ground_ens', 'Brightness_temperature_atmosphere_top_ens', 'Cloud_mixing_ratio_isobaric_ens', 'Cloud_water_entire_atmosphere_single_layer_ens', 
        # 'Convective_available_potential_energy_surface_ens', 'Convective_available_potential_energy_pressure_difference_layer_ens', 'Convective_inhibition_surface_ens', 'Convective_inhibition_pressure_difference_layer_ens', 'Convective_precipitation_surface_3_Hour_Accumulation_ens', 'Dewpoint_temperature_height_above_ground_ens', 
        # 'Dewpoint_temperature_pressure_difference_layer_ens', 'Geopotential_height_isobaric_ens', 'Geopotential_height_hybrid_ens', 'Geopotential_height_surface_ens', 'Geopotential_height_cloud_ceiling_ens', 'Geopotential_height_tropopause_ens', 
        # 'Geopotential_height_maximum_wind_ens', 'Geopotential_height_zeroDegC_isotherm_ens', 'Geopotential_height_highest_tropospheric_freezing_ens', 'Geopotential_height_potential_vorticity_surface_ens', 'Haines_index_surface_ens', 'ICAO_Standard_Atmosphere_Reference_Height_tropopause_ens', 
        # 'ICAO_Standard_Atmosphere_Reference_Height_maximum_wind_ens', 'Ice_cover_surface_ens', 'Icing_isobaric_ens', 'Land_cover_0__sea_1__land_surface_ens', 'Large-scale_precipitation_non-convective_surface_3_Hour_Accumulation_ens',
        # 'Momentum_flux_u-component_surface_3_Hour_Average_ens', 'Momentum_flux_v-component_surface_3_Hour_Average_ens', 'Montgomery_stream_function_isentrope_ens', 'Parcel_lifted_index_to_500_hPa_pressure_difference_layer_ens', 'Per_cent_frozen_precipitation_surface_ens', 
        # 'Potential_temperature_sigma_ens', 'Potential_vorticity_isentrope_ens', 'Precipitable_water_pressure_difference_layer_ens', 'Precipitation_rate_surface_3_Hour_Average_ens', 'Pressure_msl_ens', 'Pressure_hybrid_ens', 'Pressure_tropopause_ens', 'Pressure_maximum_wind_ens', 'Pressure_height_above_ground_ens', 
        # 'Pressure_potential_vorticity_surface_ens', 'Pressure_high_cloud_bottom_3_Hour_Average_ens', 'Pressure_middle_cloud_bottom_3_Hour_Average_ens', 'Pressure_low_cloud_bottom_3_Hour_Average_ens', 'Pressure_low_cloud_top_3_Hour_Average_ens', 'Pressure_high_cloud_top_3_Hour_Average_ens', 'Pressure_middle_cloud_top_3_Hour_Average_ens', 'Pressure_convective_cloud_bottom_ens', 'Pressure_convective_cloud_top_ens', 
        # 'Relative_humidity_hybrid_ens', 'Relative_humidity_isobaric_ens', 'Relative_humidity_zeroDegC_isotherm_ens', 'Relative_humidity_pressure_difference_layer_ens', 'Relative_humidity_sigma_layer_ens', 'Relative_humidity_sigma_ens', 'Relative_humidity_entire_atmosphere_single_layer_ens', 'Relative_humidity_highest_tropospheric_freezing_ens', 'Snow_cover_surface_3_Hour_Average_ens', 
        # 'Snow_phase_change_heat_flux_surface_3_Hour_Average_ens', 'Soil_temperature_depth_below_surface_layer_ens', 'Specific_humidity_isobaric_ens', 'Specific_humidity_pressure_difference_layer_ens', 'Specific_humidity_height_above_ground_ens', 'Storm_relative_helicity_height_above_ground_layer_ens', 'Surface_roughness_surface_ens', 'Temperature_hybrid_ens', 'Temperature_isentrope_ens', 'Temperature_potential_vorticity_surface_ens', 'Temperature_sigma_ens', 'Temperature_isobaric_ens', 'Temperature_surface_ens', 
        # 'Temperature_tropopause_ens', 'Temperature_maximum_wind_ens', 'Temperature_pressure_difference_layer_ens', 'Temperature_height_above_ground_ens', 'Temperature_altitude_above_msl_ens', 'Temperature_low_cloud_top_3_Hour_Average_ens', 'Temperature_high_cloud_top_3_Hour_Average_ens', 'Temperature_middle_cloud_top_3_Hour_Average_ens', 'Total_cloud_cover_isobaric_ens', 'Total_cloud_cover_low_cloud_3_Hour_Average_ens', 
        # 'Total_cloud_cover_middle_cloud_3_Hour_Average_ens', 'Total_cloud_cover_high_cloud_3_Hour_Average_ens', 'Total_cloud_cover_boundary_layer_cloud_3_Hour_Average_ens', 'Total_cloud_cover_convective_cloud_ens', 'Total_ozone_entire_atmosphere_single_layer_ens', 'Convective_Precipitation_Rate_surface_3_Hour_Average_ens', 'Potential_Evaporation_Rate_surface_ens', 'Ozone_Mixing_Ratio_isobaric_ens', 
        # 'Icing_severity_isobaric_ens', 'Vertical_Speed_Shear_tropopause_ens', 'Vertical_Speed_Shear_potential_vorticity_surface_ens', 'U-Component_Storm_Motion_height_above_ground_layer_ens', 'V-Component_Storm_Motion_height_above_ground_layer_ens', 'Frictional_Velocity_surface_ens', 'Ventilation_Rate_planetary_boundary_ens', 'MSLP_Eta_model_reduction_msl_ens', '5-Wave_Geopotential_Height_isobaric_ens', 'Zonal_Flux_of_Gravity_Wave_Stress_surface_3_Hour_Average_ens', 'Meridional_Flux_of_Gravity_Wave_Stress_surface_3_Hour_Average_ens', 'Planetary_Boundary_Layer_Height_surface_ens', 'Pressure_of_level_from_which_parcel_was_lifted_pressure_difference_layer_ens', 'Upward_Short-Wave_Radiation_Flux_atmosphere_top_3_Hour_Average_ens', 
        # 'UV-B_Downward_Solar_Flux_surface_3_Hour_Average_ens', 'Clear_sky_UV-B_Downward_Solar_Flux_surface_3_Hour_Average_ens', 'Cloud_Work_Function_entire_atmosphere_single_layer_3_Hour_Average_ens', 'Sunshine_Duration_surface_ens', 'Surface_Lifted_Index_surface_ens', 'Best_4_layer_Lifted_Index_surface_ens', 'Volumetric_Soil_Moisture_Content_depth_below_surface_layer_ens', 'Ground_Heat_Flux_surface_3_Hour_Average_ens', 'Plant_Canopy_Surface_Water_surface_ens', 'Wilting_Point_surface_ens', 'Liquid_Volumetric_Soil_Moisture_non_Frozen_depth_below_surface_layer_ens', 
        # 'Field_Capacity_surface_ens', 'Vertical_velocity_pressure_isobaric_ens', 'Vertical_velocity_pressure_sigma_ens', 'Visibility_surface_ens', 'Water_runoff_surface_3_Hour_Accumulation_ens', 'Wind_speed_gust_surface_ens', 'u-component_of_wind_isobaric_ens', 'u-component_of_wind_hybrid_ens', 'u-component_of_wind_isentrope_ens', 'u-component_of_wind_potential_vorticity_surface_ens', 'u-component_of_wind_tropopause_ens', 'u-component_of_wind_maximum_wind_ens', 'u-component_of_wind_height_above_ground_ens', 'u-component_of_wind_altitude_above_msl_ens', 'u-component_of_wind_pressure_difference_layer_ens', 'u-component_of_wind_sigma_ens', 'u-component_of_wind_planetary_boundary_ens', 'v-component_of_wind_isobaric_ens', 
        # 'v-component_of_wind_hybrid_ens', 'v-component_of_wind_isentrope_ens', 'v-component_of_wind_potential_vorticity_surface_ens', 'v-component_of_wind_sigma_ens', 'v-component_of_wind_tropopause_ens', 'v-component_of_wind_maximum_wind_ens', 'v-component_of_wind_height_above_ground_ens', 'v-component_of_wind_altitude_above_msl_ens', 'v-component_of_wind_pressure_difference_layer_ens', 'v-component_of_wind_planetary_boundary_ens'])
        """
        # important?!
        # identify file and the variables within etc
        data = xr.open_dataset(self.fpath)
        metadata = data.to_dict(data=False)

        # pdb.set_trace()
        # close netCDF file? Or should there be an "exit" class method?
        return data, metadata

    @staticmethod
    def download_data(latest=True,all_members=True):
        now = datetime.datetime.utcnow()
        if latest:
            if (now.hour >= 11) and (now.hour <=16):
                hour = 6
            elif (now.hour >= 17) and (now.hour <= 22):
                hour = 12
            elif (now.hour >= 23) or (now.hour <= 4):
                if now.hour <= 4:
                    now -= timedelta(days=1)
                else:
                    hour = 18
            else:
                hour = 0     

        date = datetime.datetime(now.year,now.month,now.day,hour)
        os.chdir('/storage/gefs_data')
        # os.chdir('/data/ldmdata/model/gefs')
        prods = {'pgrb2ap5','pgrb2bp5','pgrb2sp25'}
        prod_codes = {"pgrb2ap5":"pgrb2a.0p50",
                        "pgrb2bp5":"pgrb2b.0p50",
                        "pgrb2sp25":"pgrb2s.0p25",}
        # f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.20220316/12/atmos/pgrb2ap5/
        # https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.20220316/12/atmos/pgrb2sp25/gep02.t12z.pgrb2s.0p25.f024
        members = ["c00"] + [f"p{n:02d}" for n in range(1,31)]
        # members = ["p02",]
        # fchrs = np.arange(0,241,3)
        fchrs = [3,]
        for prod,member_code in itertools.product(prods,members):
            for fcsthr in fchrs:
                url_dir = (f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/"
                            "gens/prod/gefs."
                            f"{date:%Y%m%d}/{hour:02d}/atmos/{prod}/")
                fname = f"ge{member_code}.t{hour:02d}z.{prod_codes[prod]}.f{fcsthr:03d}"
                fpath = os.path.join(url_dir,fname)
                # For each member...
                # prod ap5
                # gec00.t12z.pgrb2a.0p50.f018 (p01, etc)

                # prod bp5
                # gec00.t12z.pgrb2b.0p50.f003 (p01, etc)

                # prod sp25
                # gec00.t12z.pgrb2s.0p25.f228 (p01, etc)
                print("Downloading",fpath)
                ds = wget.download(fpath)
                print("Saved to disc. Coverting to netCDF:")
                # os.system(f"java -Xmx512m -classpath /opt/ldm/process_data/netcdfAll-5.2.0.jar ucar.nc2.write.Nccopy -isLargeFile -i GFS_Global_onedeg_{date:%Y%m%d_%H00}.grib2 -o {date:%Y%m%d%H}_gfs.nc") 
                os.system(f"java -Xmx512m -classpath /opt/ldm/process_data/"
                            "netcdfAll-5.2.0.jar" 
                            f" ucar.nc2.write.Nccopy -isLargeFile -i "
                            f"{fname} -o GEFS_{fname}.nc") 
                print('Finished Converting to netCDF') 
                for f in glob.glob("ge*"):
                    os.remove(f)
        print("Finished downloading data.")
        pdb.set_trace()
        return

    @staticmethod
    def create_gefs_fname(member_name,init_h,prod,fhr):
        # prods = {'pgrb2ap5','pgrb2bp5','pgrb2sp25'}
        prod_codes = {"pgrb2ap5":"pgrb2a.0p50",
                        "pgrb2bp5":"pgrb2b.0p50",
                        "pgrb2sp25":"pgrb2s.0p25",}
        p = prod_codes[prod]
        fname = f"GEFS_ge{member_name}.t{init_h:02d}z.{p}.f{fhr:03d}.nc"
        return fname
