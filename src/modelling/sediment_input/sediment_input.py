# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import numpy as np
import subprocess
import gdal, gdalconst, _gdal
import ogr
import osr
import math as math

from general.project_data import project_data


# # This is the main class of the module water_balance
# @date  23.03.2023
#
# @author Stephan Bürger <br>
#        VisDat geodatentechnologie GmbH<br>
#        01277 Dresden <br>
#        Am Ende 14 <br>
#        http://www.galf-dresden.de <br>
#        info@galf-dresden.de <br>
#


class sediment_input:
    """
        Class to create sediment input
    """

    def __init__(self, data_config, data_param, data_area, data_level, data_nc):
        self.project_data = project_data(data_config, data_param, data_area, data_level, data_nc)

    def raster2numpy(self, raster_data):
        ds = gdal.Open(raster_data)
        my_array = np.array(ds.GetRasterBand(1).ReadAsArray())

        ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform()
        lrx = ulx + (ds.RasterXSize * xres)
        lry = uly + (ds.RasterYSize * yres)

        xmin = ulx
        ymax = uly

        my_array = np.flipud(my_array)

        return my_array, xmin, ymax

    def prepare_slope(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """
        input_file = '/data/stb_sachsen/tmp/burn_barrier_dgm.sgrd'
        target_file = '/data/stb_sachsen/tmp/slope.sgrd'

        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)
        saga_string = 'saga_cmd ta_morphometry "Slope, Aspect, Curvature" -ELEVATION=' + input_file + ' -SLOPE=' + \
                      target_file + ' -METHOD=6 -UNIT_SLOPE=2 -UNIT_ASPECT=1'

        print(saga_string)
        p.communicate(saga_string.encode('utf8'))
        del p

        result_file = '/data/stb_sachsen/tmp/slope.sdat'
        result_array, xmin, ymax = self.raster2numpy(result_file)

        __result = np.where(result_array > 0.0, result_array / 100.0, result_array)

        self.project_data.set_data(__result, kwargs, True)
        del __result

    def slope_radiant(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_sediment_input('slope_radiant')

        __result = (__input_data['slope'] * np.pi / 180.0)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_likeliness_connectivity(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_sediment_input('likeliness_connectivity', kwargs)

        pd = np.where((__input_data['water_distance'] >= 0.0),
                      -0.1358 * np.log(__input_data['water_distance']) + 0.9717, np.nan)

        print("likeliness of connectivity (Pb - soil erosion) ...")

        pb = np.where((__input_data['abag'] >= 0.1), 0.0671 * np.log(__input_data['abag']) + 0.1557, 0.0)

        print("likeliness of connectivity (Pa - surface_runoff) ...")

        pa = np.where(__input_data['surface_runoff'] >= 0.1, 0.0386 * np.log(__input_data['surface_runoff']) + 0.0994,
                      0.0)

        print("likeliness of connectivity (p total) ...")

        # cond_list = [(pd == 0.0), (pb == 0.0), (pa == 0.0)]
        # choice_list = [0.0, 0.0, 0.0]

        # tmp = np.select(cond_list, choice_list, (np.sqrt(np.square(pa) + np.square(pb) + np.square(pd))))
        # __result = np.where(tmp > 1.0, 1.0, tmp)

        __result = np.power((np.power(pd, 2) + np.power(pb, 2) + np.power(pa, 2)), 0.5)

        __result = np.where(pa == 0.0, 0.0, __result)
        __result = np.where(pb == 0.0, 0.0, __result)
        __result = np.where(pd == 0.0, 0.0, __result)

        __result = np.where(np.isnan(__input_data['water_distance']), np.nan, __result)
        __result = np.where(np.isnan(__input_data['abag']), np.nan, __result)
        __result = np.where(np.isnan(__input_data['surface_runoff']), np.nan, __result)

        # -0.005 geschummelt!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # nur im idsz 177 (bis jetzt)
        # __result = np.where(__result > 1.0, 1.0, __result-0.005)
        # __result = np.where(__result > 1.0, 1.0, __result)
        __result = np.where(__result < 0.0, 0.0, __result)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del pd
        del pb
        del pa
        # del tmp
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_chi(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_sediment_input('chi', kwargs)

        __result = 1.43 * np.log(__input_data['cfactor']) + 9.49

        # Anpassung damit Chi nicht negativ wird -> prüfen!!!
        __result = np.where((__result < 0.0), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_sdr(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_sediment_input('sdr', kwargs)

        # __s = np.tan((__input_data['slope'] * np.pi / 180.0))
        # __s = np.tan((__input_data['slope'] * 3.14195 / 180.0))

        # print(np.pi)
        # print(51*np.pi/180)
        # print(np.tan((51*np.pi/180)))
        # sys.exit()

        """__result = np.where(__input_data['connectivity'] > 0.0, __input_data['chi_factor'] *
                            np.power(__s / __input_data['water_distance'],
                                     (1 - __input_data['connectivity'])), np.nan)"""

        __result = np.where(__input_data['connectivity'] > 0.0, __input_data['chi_factor'] *
                            np.power(__input_data['slope'] / __input_data['water_distance'],
                                     (1 - __input_data['connectivity'])), np.nan)

        __result = np.where(__result > 1.0, 1.0, __result)
        __result = np.where(__result < 0.001, 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_sediment_input(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_sediment_input('sediment_input', kwargs)

        water_connect = np.where(__input_data['water_distance'] > 0.0, 1.0, 0.0)

        __result = __input_data['sdr'] * __input_data['abag'] * water_connect

        __result = np.where(__result > 0.0, __result * 1000.0, 0)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result
