# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import numpy as np

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


class soil_erosion:
    """
        Class to create the soil erosion
    """

    def __init__(self, data_config, data_param, data_area, data_level, data_nc):

        self.project_data = project_data(data_config, data_param, data_area, data_level, data_nc)

    def calc_cfactor(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_soil_erosion('cfactor', kwargs)

        # Total area
        f_all = __input_data['qw'] + __input_data['ww'] + __input_data['wg'] + __input_data['wr'] + \
                __input_data['sg'] + __input_data['sm'] + __input_data['km'] + __input_data['oel'] + \
                __input_data['k'] + __input_data['hf'] + __input_data['sb'] + __input_data['kl'] + \
                __input_data['fl'] + __input_data['fg'] + __input_data['th'] + __input_data['td'] + \
                __input_data['eb'] + __input_data['sp'] + __input_data['brache'] + __input_data['r'] + \
                __input_data['ik'] + __input_data['tr'] + __input_data['gp'] + \
                __input_data['kup'] + __input_data['mi']

        # kwargs['id_param'] = 700
        # self.project_data.set_data(f_all, kwargs, False)

        # md
        md = (__input_data['qw'] + __input_data['wg'] + __input_data['wr'] + __input_data['ww'] + __input_data['sg'] +
              __input_data['oel'] + __input_data['r'] + __input_data['tr'] + __input_data['gp']) * 100.0 / f_all

        # kwargs['id_param'] = 701
        # self.project_data.set_data(md, kwargs, False)

        # afu
        # richtig
        # afu = (__input_data['fg'] + __input_data['mi'] + __input_data['kup']) * 100 / f_all
        afu = (__input_data['fg'] + __input_data['kup']) * 100.0 / f_all

        # kwargs['id_param'] = 702
        # self.project_data.set_data(afu, kwargs, False)

        # ms
        ms = 0

        __tmpval = ((83 - 1.58 * (md + ms + afu) + 0.0082 * np.power((md + ms + afu), 2)) * (
                    1 - (0.03 * afu)) + (0.01 * afu) - (0.05 * ms)) / 100.0

        # kwargs['id_param'] = 703
        # self.project_data.set_data(__tmpval, kwargs, False)

        cond_list = [(afu >= 30), ((afu > 1.3) & (afu < 1.4)), ((afu == 0.0) | (md == 0.0))]

        choice_list = [0.01, 0.1, 0.1]

        __result = np.select(cond_list, choice_list, __tmpval)

        # kwargs['id_param'] = 704
        # self.project_data.set_data(__result, kwargs, False)

        __result = np.where(__input_data['land_use'] == 1, __result, np.nan)

        # kwargs['id_param'] = 705
        # self.project_data.set_data(__result, kwargs, False)

        __input_data['cfactor_kbb'] = np.where((__result > __input_data['cfactor_kbb']), __input_data['cfactor_kbb'],
                                               __result)
        __input_data['cfactor_kbb'] = np.where((__input_data['land_use'] == 1), __input_data['cfactor_kbb'], np.nan)

        # kwargs['id_param'] = 706
        # self.project_data.set_data(__input_data['cfactor_kbb'], kwargs, False)

        __input_data['cfactor_zf'] = np.where((__result > __input_data['cfactor_zf']), __input_data['cfactor_zf'],
                                              __result)
        __input_data['cfactor_zf'] = np.where((__input_data['land_use'] == 1), __input_data['cfactor_zf'], np.nan)

        # kwargs['id_param'] = 707
        # self.project_data.set_data(__input_data['cfactor_kbb'], kwargs, False)

        __input_data['cfactor_dsaat'] = np.where((__result > __input_data['cfactor_dsaat']),
                                                 __input_data['cfactor_dsaat'], __result)
        __input_data['cfactor_dsaat'] = np.where((__input_data['land_use'] == 1), __input_data['cfactor_dsaat'], np.nan)

        # kwargs['id_param'] = 708
        # self.project_data.set_data(__input_data['cfactor_zf'], kwargs, False)

        __tmp_zf = np.where(__input_data['land_use'] == 1 &
                            ((__input_data['dkbb'] + __input_data['dsaat'] + __input_data['zf']) <= 1.0),
                            __input_data['zf'],
                            __input_data['zf'] + (1.0 -
                                                  (__input_data['dkbb'] + __input_data['dsaat'] + __input_data['zf'])))

        __result = np.where(__input_data['land_use'] == 1,
                            __result * (1.0 - (__input_data['dkbb'] + __input_data['dsaat'] + __tmp_zf)) +
                            (__input_data['dkbb']) * __input_data['cfactor_kbb'] +
                            (__input_data['dsaat']) * __input_data['cfactor_dsaat'] +
                            (__tmp_zf * __input_data['cfactor_zf']), np.nan)

        # kwargs['id_param'] = 709
        # self.project_data.set_data(__result, kwargs, False)

        __result = np.where((__input_data['land_use'] == 2) & (__input_data['cfaktor_eu'] > 0.004), 0.004, __result)
        __result = np.where((__input_data['land_use'] == 2) & (__input_data['cfaktor_eu'] <= 0.004),
                            __input_data['cfaktor_eu'], __result)

        __result = np.where((__input_data['land_use'] == 3) & (__input_data['cfaktor_eu'] < 0.1), 0.1, __result)
        __result = np.where((__input_data['land_use'] == 3) & (__input_data['cfaktor_eu'] > 0.1),
                            __input_data['cfaktor_eu'], __result)

        __result = np.where((__input_data['land_use'] == 4) & (__input_data['cfaktor_eu'] < 0.1), 0.1, __result)
        __result = np.where((__input_data['land_use'] == 4) & (__input_data['cfaktor_eu'] > 0.1),
                            __input_data['cfaktor_eu'], __result)

        __result = np.where((__input_data['land_use'] == 5) & (__input_data['cfaktor_eu'] > 0.004), 0.004, __result)
        __result = np.where((__input_data['land_use'] == 5) & (__input_data['cfaktor_eu'] <= 0.004),
                            __input_data['cfaktor_eu'], __result)

        __result = np.where((__input_data['land_use'] == 6) & (__input_data['cfaktor_eu'] > 0.004), 0.004, __result)
        __result = np.where((__input_data['land_use'] == 6) & (__input_data['cfaktor_eu'] <= 0.004),
                            __input_data['cfaktor_eu'], __result)

        __result = np.where(__result < 0, np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def calc_abag(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_soil_erosion('abag', kwargs)

        __result = __input_data['kfactor'] * __input_data['cfactor'] * __input_data['lsfactor'] \
                   * __input_data['rfactor'] * 1000.0

        # __result = np.where(np.isnan(__input_data['lsfactor']), np.nan, __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def calc_er(self, **kwargs):
        """
            function to calculate er

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_soil_erosion('er', kwargs)

        __result = np.where(__input_data['abag'] > 0.0, 2.53 * np.power((__input_data['abag'] / 1000), -0.21), 0)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result
