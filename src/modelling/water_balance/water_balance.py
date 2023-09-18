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
#


class water_balance:
    """
        Class to create the water balance
    """

    def __init__(self, data_config, data_param, data_area, data_level, data_nc):

        self.project_data = project_data(data_config, data_param, data_area, data_level, data_nc)

        try:
            file_modul_config = data_config['water_balance']['file_modul_config']
            self.__modul_config = self.project_data.moduldata_from_txt(file_modul_config)
        except:
            pass


    def cal_precipitation(self, **kwargs):
        """
            function to calculate the total precipitation
            (Calculates the total precipitation as the sum of summer and winter precipitation.)

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('precipitation', kwargs)

        __result = __input_data['rain_summer'] + __input_data['rain_winter']

        __result = np.where(__result < 0, np.nan, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_hydromorphiegrad(self, **kwargs):
        """
            function to calculate the 'Hydromorphiegrad'

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display (Hydromorphiegrad = 1,2,3)
        """

        __input_data = self.project_data.get_data_waterbalance('hydromorphiegrad', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        # __result = np.where(np.isnan(__result), np.nan, np.nan)

        # __result = np.where((__input_data['bodentyp'] <= 21) & (__input_data['bodentyp'] >= 18), 3, __result)
        # __result = np.where((__input_data['bodentyp'] <= 17) & (__input_data['bodentyp'] >= 15), 2, __result)
        # __result = np.where((__input_data['bodentyp'] <= 14) & (__input_data['bodentyp'] >= 1), 1, __result)

        __result = np.where((np.isnan(__input_data['land_use'])), np.nan, 1)

        __result = np.where((__input_data['bodentyp'] == 15), 2, __result)

        __result = np.where((__input_data['bodentyp'] == 18), 3, __result)

        __result = np.where((__input_data['bodentyp'] == 22), np.nan, __result)

        __result = np.where((__input_data['bodentyp'] == 23), np.nan, __result)

        # __result = np.where((__input_data['land_use'] == 7), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_humusoberboden(self, **kwargs):
        """
            function to calculate the 'cal_humusoberboden'

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __conf = self.__modul_config[7]['humusoberboden']  # aus dem json file

        __input_data = self.project_data.get_data_waterbalance('humusoberboden', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        for y in range(len(__conf)):
            __result = np.where((__input_data['bodenartengruppe'] == __conf[y]['idbodenartgruppe']) & (
                    __input_data['bodentyp'] == __conf[y]['idbodentyp']), __conf[y]['humus_oberboden'],
                                __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_runoff_quotient(self, **kwargs):
        """
            function to calculate the runoff quotient

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __conf = self.__modul_config[2]['runoff_quotient']  # aus dem json file

        __input_data = self.project_data.get_data_waterbalance('runoff_quotient', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        for y in range(len(__conf)):
            __result = np.where(
                ((__input_data['slope'] > __conf[y]['min']) & (__input_data['slope'] <= __conf[y]['max'])
                 & (__input_data['hydromorphiegrad'] == __conf[y]['hydromorphology'])),
                round(__conf[y]['value'], 1), __result)

        __res_fest = np.where(__input_data['mnq'] <= 0, np.nan, np.round(__input_data['mq'] / __input_data['mnq'], 1))

        __result = np.where(((__input_data['fest_locker'] == 2) & (__res_fest > 0.0)), __res_fest, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        del __res_fest
        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_exposure_quotient(self, **kwargs):
        """
            function to calculate the exposure quotient

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __conf = self.__modul_config[1]['exposure_quotient']

        __input_data = self.project_data.get_data_waterbalance('exposure_quotient', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __exposure_id = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        # Nord 1
        __exposure_id = np.where((__input_data['exposure'] >= 0) & (__input_data['exposure'] < 22.5), 1,
                                 __exposure_id)
        __exposure_id = np.where((__input_data['exposure'] >= 337.5) & (__input_data['exposure'] <= 360), 1,
                                 __exposure_id)

        # Nordost 3
        __exposure_id = np.where((__input_data['exposure'] >= 22.5) & (__input_data['exposure'] < 67.5), 3,
                                 __exposure_id)

        # Ost 7
        __exposure_id = np.where((__input_data['exposure'] >= 67.5) & (__input_data['exposure'] < 112.5), 7,
                                 __exposure_id)

        # Südost 6
        __exposure_id = np.where((__input_data['exposure'] >= 112.5) & (__input_data['exposure'] < 157.5), 6,
                                 __exposure_id)

        # Süd 4
        __exposure_id = np.where((__input_data['exposure'] >= 157.5) & (__input_data['exposure'] < 202.5), 4,
                                 __exposure_id)

        # Südwest 5
        __exposure_id = np.where((__input_data['exposure'] >= 202.5) & (__input_data['exposure'] < 247.5), 5,
                                 __exposure_id)

        # West 8
        __exposure_id = np.where((__input_data['exposure'] >= 247.5) & (__input_data['exposure'] < 292.5), 8,
                                 __exposure_id)

        # Nordwest 2
        __exposure_id = np.where((__input_data['exposure'] >= 292.5) & (__input_data['exposure'] < 337.5), 2,
                                 __exposure_id)

        for y in range(len(__conf)):
            __result = np.where(((__input_data['slope'] > __conf[y]['min']) & (
                    __input_data['slope'] <= __conf[y]['max']) & (__exposure_id == __conf[y]['idexposition'])),
                                __conf[y]['value'], __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        del __exposure_id
        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_cn_value(self, **kwargs):
        """
            function to calculate the cn value

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __conf = self.__modul_config[3]['cn_value']

        __input_data = self.project_data.get_data_waterbalance('cn_value', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        # 'ss'
        __result = np.where(__input_data['land_use'] == 1 & (__input_data['bodenartengruppe'] == 1),
                            (62.0 * (__input_data['dkbb'] + __input_data['dsaat']) / 100.0 + 67.0 * (
                                    100.0 - (__input_data['dkbb'] + __input_data['dsaat'])) / 100.0), __result)

        # 'us','ls','tu','lu','su'
        __result = np.where(__input_data['land_use'] == 1 & (
                (__input_data['bodenartengruppe'] == 2) | (__input_data['bodenartengruppe'] == 3) |
                (__input_data['bodenartengruppe'] == 5) | (__input_data['bodenartengruppe'] == 6) | (
                        __input_data['bodenartengruppe'] == 8)),
                            (73.0 * (__input_data['dkbb'] + __input_data['dsaat']) / 100.0 + 78.0 * (
                                    100.0 - (__input_data['dkbb'] + __input_data['dsaat'])) / 100.0),
                            __result)

        # 'sl','ll','tl'
        __result = np.where(__input_data['land_use'] == 1 & (
                (__input_data['bodenartengruppe'] == 4) | (__input_data['bodenartengruppe'] == 7) |
                (__input_data['bodenartengruppe'] == 9)),
                            (79.0 * (__input_data['dkbb'] + __input_data['dsaat']) / 100.0 + 86.0 * (
                                    100.0 - (__input_data['dkbb'] + __input_data['dsaat'])) / 100.0),
                            __result)

        # 'lt','ut','Hn','Hh'
        __result = np.where(__input_data['land_use'] == 1 & (
                (__input_data['bodenartengruppe'] == 10) | (__input_data['bodenartengruppe'] == 11) |
                (__input_data['bodenartengruppe'] == 12) | (__input_data['bodenartengruppe'] == 13)),
                            (80.0 * (__input_data['dkbb'] + __input_data['dsaat']) / 100.0 + 89.0 * (
                                    100.0 - (__input_data['dkbb'] + __input_data['dsaat'])) / 100.0),
                            __result)

        # print('--> __conf', __conf)

        for y in range(len(__conf)):
            __result = np.where(
                (__input_data['land_use'] != 1) & (__input_data['bodenartengruppe'] == __conf[y]['idbag']) & (
                        __input_data['land_use'] == __conf[y]['idhn']), __conf[y]['cn_wert'], __result)

        # Bei "Siedlung" wird für die unversiegelte Fläche ein CN- wert von "Grünland" angenommen
        __result = np.where(__input_data['land_use'] == 7, 61.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_nfkwe(self, **kwargs):
        """
            function to calculate the the exposure quotient
            (erechnet die nutzbare Feldkapazität im effektiven Wurzelraum, abhängig von landnutzung, bodenart und humus)

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __conf = self.__modul_config[4]['nfkwe']

        __input_data = self.project_data.get_data_waterbalance('nfkwe', kwargs)

        __humusgehalt = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        __humusgehalt = __input_data['humusoberboden'] * (2.0 - 0.16666666 * (__input_data['temp'] - 4.0))
        # __humusgehalt =  input_data['humusoberboden'] *(-0.1943 * input_data['temp']+ 2.749)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 1),
                            1.9139 * np.log(__humusgehalt) + 0.5044, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 2),
                            -0.0163 * np.square(__humusgehalt) + 0.6192 * __humusgehalt + 1.264, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 3),
                            -0.0306 * np.square(__humusgehalt) + 0.669 * __humusgehalt + 0.3198, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 4),
                            -0.0401 * np.square(__humusgehalt) + 1.0384 * __humusgehalt + 0.03364, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 5),
                            -0.0276 * np.square(__humusgehalt) + 0.6497 * __humusgehalt + 0.164, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 6),
                            0.0196 * np.square(__humusgehalt) + 0.0742 * __humusgehalt + 1.5435, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 7),
                            -0.0512 * np.square(__humusgehalt) + 1.3258 * __humusgehalt + 0.0055, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 8),
                            -0.0414 * np.square(__humusgehalt) + 0.9748 * __humusgehalt + 1.246, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 9),
                            -0.0702 * np.square(__humusgehalt) + 1.5604 * __humusgehalt + 0.3197, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 10),
                            -0.0623 * np.square(__humusgehalt) + 1.5031 * __humusgehalt + 0.2788, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 11),
                            -0.0558 * np.square(__humusgehalt) + 1.3791 * __humusgehalt + 0.5016, __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 12), 1.0,
                            __result)
        __result = np.where((__input_data['land_use'] < 3) & (__input_data['bodenartengruppe'] == 13), 1.0,
                            __result)

        __result = np.where((__input_data['land_use'] >= 3), 0.0, __result)

        for y in range(len(__conf)):
            __result = np.where((__input_data['bodenartengruppe'] == __conf[y]['idbag']),
                                ((__result + __conf[y]['nfk']) * __conf[y]['we']), __result)

        __result = np.where(__result < 0.0, 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        del __humusgehalt
        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_surface_runoff(self, **kwargs):
        """
            function to calculate the surface runoff

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('surface_runoff', kwargs)

        __cnspl = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        __nmean = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        __ia = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        __surface_runoff_cn = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __cn_value = np.where(__input_data['land_use'] >= 0, __input_data['cn_value'], np.nan)

        __cnspl = (__cn_value * np.exp(0.00673 * (100.0 - __cn_value)) - __cn_value) / \
                  3.0 * (1.0 - 2.0 * np.exp(-13.86 * np.tan(__input_data['slope'] * (2 * np.pi / 360)))) \
                  + __cn_value

        __nmean = np.where(__input_data['regentage'] > 0.0,
                           (__input_data['rain_summer'] + __input_data['rain_winter']) / __input_data[
                               'regentage'], 0.0)

        __ia = 0.03 * (1000.0 / __cnspl - 10.0) * 25.4

        __surface_runoff_cn = np.power((__nmean - __ia), 2) / (__nmean - __ia + __ia / 0.03) * __input_data[
            'regentage'] * (1.0 - __input_data['draenflaeche'] / 100.0)

        # Siedlung
        __surface_runoff_cn = np.where((__input_data['land_use'] == 7),
                                       (__surface_runoff_cn * (1.0 - __input_data['versiegelungsgrad'] / 100.0)),
                                       __surface_runoff_cn)

        # Neu! Anpassung über hydraulische Anbindung herausgenommen, 20.08.2019.
        # __surface_runoff_cn = __surface_runoff_cn * __input_data['hyd_connect'] /100.0

        __result = np.where(__input_data['land_use'] > 0, 0.0, np.nan)

        __result = np.where(__input_data['regentage'] > 0.0, __surface_runoff_cn, 0.0)

        __result = np.where(__input_data['slope'] > 0.5, __result, 0.0)

        # Gewässer ist Oberflächenabfluss = 0
        __result = np.where((__input_data['land_use'] == 8), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __cn_value
        del __cnspl
        del __nmean
        del __ia
        del __surface_runoff_cn
        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_kr(self, kwargs):

        """
            function to calculate kr

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __conf = self.__modul_config[5]['kapillaraufstieg']

        __input_data = self.project_data.get_data_waterbalance('kr', kwargs)

        # dblZa = dblMngw - dblWe
        # if (dblZa <= 0.0){dblZa = 0.1}
        # for(int loop=0; loop != kr[0].i; loop++){}
        # 	if(kr[loop].iIDBodenartgruppe == tmpIDBodenartgruppe)
        # 		if(kr[loop].dblZa_min < dblZa and kr[loop].dblZa_max >= dblZa){
        # 			return kr[loop].dblKr}}

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        for y in range(len(__conf)):
            __result = np.where((__input_data['bodenartengruppe'] == __conf[y]['idbag']) & (
                        __input_data['bodentyp'] == __conf[y]['idbt'])
                        & (__input_data['land_use'] == __conf[y]['idhn']), __conf[y]['kr'], __result)

        __result = np.where(np.isnan(__input_data['bodentyp']), np.nan, __result)
        __result = np.where(np.isnan(__input_data['bodenartengruppe']), np.nan, __result)

        # print('bodenartengruppe')
        # print(__input_data['bodenartengruppe'][1065:1075, 284:294])

        # print('bodentyp')
        # print(__input_data['bodentyp'][1065:1075, 284:294])

        del __input_data

        return __result

    def cal_ta(self, frucht, kr, kwargs):

        """
            function to calculate ta
            (tägliche Dauer des kapillaren Aufstiegs, abhängig von Ackernutzung und nfkwe)

            Parameter:
                frucht
            Parameter:
                kr

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('ta', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        if frucht == 1:
            __result = np.where((kr <= 1.25), 0.075 * __input_data['nfkwe'] + 21.5, __result)
            __result = np.where(((kr <= 1.75) & (kr > 1.25)), 0.075 * __input_data['nfkwe'] + 25.0, __result)
            __result = np.where(((kr <= 2.25) & (kr > 1.75)), 0.07 * __input_data['nfkwe'] + 30.0, __result)
            __result = np.where(((kr <= 2.75) & (kr > 2.25)), 0.055 * __input_data['nfkwe'] + 35.0, __result)
            __result = np.where(((kr <= 3.25) & (kr > 2.75)), 0.05 * __input_data['nfkwe'] + 40.0, __result)
            __result = np.where(((kr <= 3.75) & (kr > 3.25)), 0.035 * __input_data['nfkwe'] + 45.0, __result)
            __result = np.where(((kr <= 4.5) & (kr > 3.75)), 0.035 * __input_data['nfkwe'] + 48.0, __result)
            __result = np.where((kr > 4.5), 60.0, __result)

        if frucht == 2:
            __result = np.where((kr <= 1.25), 0.1 * __input_data['nfkwe'] + 26.5, __result)
            __result = np.where(((kr <= 1.75) & (kr > 1.25)), 0.09 * __input_data['nfkwe'] + 34.0, __result)
            __result = np.where(((kr <= 2.25) & (kr > 1.75)), 0.085 * __input_data['nfkwe'] + 41.5, __result)
            __result = np.where(((kr <= 2.75) & (kr > 2.25)), 0.08 * __input_data['nfkwe'] + 47.5, __result)
            __result = np.where(((kr <= 3.25) & (kr > 2.75)), 0.07 * __input_data['nfkwe'] + 53.0, __result)
            __result = np.where(((kr <= 3.75) & (kr > 3.25)), 0.065 * __input_data['nfkwe'] + 60.0, __result)
            __result = np.where(((kr <= 4.5) & (kr > 3.75)), 0.06 * __input_data['nfkwe'] + 66.0, __result)
            __result = np.where((kr > 4.5), 90.0, __result)

        if frucht == 3:
            __result = np.where((kr <= 1.25), 0.12 * __input_data['nfkwe'] + 31.0, __result)
            __result = np.where(((kr <= 1.75) & (kr > 1.25)), 0.14 * __input_data['nfkwe'] + 40.0, __result)
            __result = np.where(((kr <= 2.25) & (kr > 1.75)), 0.12 * __input_data['nfkwe'] + 50.0, __result)
            __result = np.where(((kr <= 2.75) & (kr > 2.25)), 0.11 * __input_data['nfkwe'] + 60.0, __result)
            __result = np.where(((kr <= 3.25) & (kr > 2.75)), 0.10 * __input_data['nfkwe'] + 70.0, __result)
            __result = np.where(((kr <= 3.75) & (kr > 3.25)), 0.10 * __input_data['nfkwe'] + 80.0, __result)
            __result = np.where(((kr <= 4.5) & (kr > 3.75)), 0.10 * __input_data['nfkwe'] + 90.0, __result)
            __result = np.where((kr > 4.5), 120.0, __result)

        # self.project_data.np2sql(__result, 5001, True)

        del __input_data

        return __result

    def cal_ka_kli(self, kwargs):

        """
            function to calculate ka_kli
            (Der mittlere kapillare Aufstieg KA kli wird in Abhängigkeit des Defizits der klimatischen Wasserbilanz im
            Sommerhalbjahr und der Landnutzung gemäß Ad-hoc-AG Boden (2003) berechnet (Tabelle 8).r:))

            Parameter:
                None
            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('ka_kli', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = np.where((__input_data['land_use'] == 1), 1.05, __result)
        __result = np.where((__input_data['land_use'] == 2), 1.2, __result)
        __result = np.where((__input_data['land_use'] == 5), 1.3, __result)
        __result = np.where((__input_data['land_use'] == 6), 1.3, __result)

        __oa_ns = 1.0 - __input_data['surface_runoff'] / (__input_data['rain_summer'] + __input_data['rain_winter'])

        __result = __result * (0.72 * __input_data['etp'] + 48.0) - __input_data['rain_summer'] * __oa_ns + 0.5 * \
                   __input_data['nfkwe']

        __result = np.where((__result < 0.0), 0.0, __result)

        del __oa_ns
        del __input_data

        return __result

    def cal_ka_max(self, ta, kr):

        """
            function to calculate ka_max
            (der maximale Betrag des mittleren kapillaren Aufstiegs KA max wird aus der mittleren täglichen kapillaren
            Aufstiegsrate KR [mm/d] und der entsprechenden mittleren, täglichen Dauer des kapillaren Aufstiegs ta [d])

            Parameter:
                ta
            Parameter:
                kr

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        return ta * kr

    def cal_ka(self, ka_max, ka_kli):

        """
            function to calculate the kr
            (der Betrag des mittleren kapillaren Aufstiegs KA wird in Abhängigkeit vom Defizit der klimatischen
            Wasserbilanz im Sommerhalbjahr begrenzt, sodass KA nach folgenden Bedingungen ermittelt wird)

            Parameter:
                ka_max
            Parameter:
                ka_kli

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        # _result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = np.where((ka_kli < 0.0), 0.0, np.nan)  # (a) KA = 0 wenn KA kli = 0.

        __result = np.where((ka_max > ka_kli), ka_kli, ka_max)  # (b) KA = KA kli wenn KA max > KA kli,
        # (c) KA = KA max wenn KA max <= KA kli

        return __result

    def cal_wpf(self, ka, kwargs):
        """
            function to calculate wpf

            Parameter:
                ka

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('wpf', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = ka + __input_data['nfkwe']

        del __input_data

        return __result

    def cal_percolation_rate_liebscher(self, wpf, kwargs):

        """
            function to calculate the percolation rate (liebscher)

            Parameter:
                wpf

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('percolation_rate_liebscher', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __oa_ns = 1.0 - __input_data['surface_runoff'] / (__input_data['rain_summer'] + __input_data['rain_winter'])

        __result = 0.86 * (__input_data['rain_summer'] + __input_data['rain_winter']) * __oa_ns

        __result = __result - 111.6 * __input_data['rain_summer'] / __input_data['rain_winter']

        __result = __result - 120.0 * np.log10(wpf)

        del __oa_ns
        del __input_data

        return __result

    def cal_wv(self, ka, kwargs):

        """
            function to calculate kv

            Parameter:
                ka

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('wv', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __oa_ns = 1.0 - __input_data['surface_runoff'] / (__input_data['rain_summer'] + __input_data['rain_winter'])

        __result = ka + __input_data['nfkwe'] + __input_data['rain_summer'] * __oa_ns

        del __oa_ns
        del __input_data

        return __result

    def cal_percolation_rate_gras(self, wv, kwargs):
        """
            function to calculate the percolation rate (FAO-Gras Referenzverdunstung)

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('percolation_rate_gras', kwargs)

        # __tmp1 = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        # __tmp2 = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        # __tmp3 = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        # __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __tmp1 = np.where(np.isnan(__input_data['land_use']), np.nan, 0.0)
        __tmp2 = np.where(np.isnan(__input_data['land_use']), np.nan, 0.0)
        __tmp3 = np.where(np.isnan(__input_data['land_use']), np.nan, 0.0)
        __result = np.where(np.isnan(__input_data['land_use']), np.nan, 0.0)

        #########################################################
        # Acker und wv > 700 => 1,05 sonst => 1.45 * (np.log10(wv)) - 3.08
        __tmp1 = np.where(((__input_data['land_use'] == 1) & (wv > 700.0)), 1.05, 1.45 * (np.log10(wv)) - 3.08)

        # Acker
        # grundwasserbeinflusst
        __tmp2 = np.where(((__input_data['land_use'] == 1) &
                           ((__input_data['bodentyp'] == 16) | (__input_data['bodentyp'] == 19) | (
                                       __input_data['bodentyp'] == 20) |
                            (__input_data['bodentyp'] == 21) | (__input_data['bodentyp'] == 22))), 0.61, __tmp2)

        # terrestrisch
        __tmp2 = np.where(((__input_data['land_use'] == 1) &
                           ((__input_data['bodentyp'] < 16) | (__input_data['bodentyp'] == 17) | (
                                       __input_data['bodentyp'] == 18) |
                            (__input_data['bodentyp'] == 23))), 0.76, __tmp2)

        # grundwasserbeinflusst
        __tmp3 = np.where(((__input_data['land_use'] == 1) &
                           ((__input_data['bodentyp'] == 16) | (__input_data['bodentyp'] == 19) | (
                                       __input_data['bodentyp'] == 20) |
                            (__input_data['bodentyp'] == 21) | (__input_data['bodentyp'] == 22))), 2.66, __tmp3)
        # terrestrisch
        __tmp3 = np.where(((__input_data['land_use'] == 1) &
                           ((__input_data['bodentyp'] < 16) | (__input_data['bodentyp'] == 17) | (
                                       __input_data['bodentyp'] == 18) |
                            (__input_data['bodentyp'] == 23))), 3.07, __tmp3)

        #############################################################
        # Grünland und wv > 700
        __tmp1 = np.where(((__input_data['land_use'] == 2) & (wv > 700.0)), 1.2, __tmp1)

        # Grünland und wv ≤ 700
        __tmp1 = np.where(((__input_data['land_use'] == 2) & (wv <= 700.0)), 1.79 *
                          (np.log10(wv)) - 3.89, __tmp1)

        # Grünland
        # grundwasserbeinflusst
        __tmp2 = np.where(((__input_data['land_use'] == 2) &
                           ((__input_data['bodentyp'] == 16) | (__input_data['bodentyp'] == 19) | (
                                   __input_data['bodentyp'] == 20) |
                            (__input_data['bodentyp'] == 21) | (__input_data['bodentyp'] == 22))), 0.4, __tmp2)

        # terrestrisch
        __tmp2 = np.where(((__input_data['land_use'] == 2) &
                           ((__input_data['bodentyp'] < 16) | (__input_data['bodentyp'] == 17) | (
                                   __input_data['bodentyp'] == 18) | (__input_data['bodentyp'] == 23))), 0.66,
                          __tmp2)

        # grundwasserbeinflusst
        __tmp3 = np.where(((__input_data['land_use'] == 2) &
                           ((__input_data['bodentyp'] == 16) | (__input_data['bodentyp'] == 19) | (
                                   __input_data['bodentyp'] == 20) |
                            (__input_data['bodentyp'] == 21) | (__input_data['bodentyp'] == 22))), 2.07, __tmp3)

        # terrestrisch
        __tmp3 = np.where(
            (((__input_data['land_use'] == 2) | (__input_data['land_use'] == 7) | (__input_data['land_use'] == 9)) &
             ((__input_data['bodentyp'] < 16) | (__input_data['bodentyp'] == 17) | (
                     __input_data['bodentyp'] == 18) | (__input_data['bodentyp'] == 23))), 2.79, __tmp3)

        #####################################################################
        # Nadelwald und wv > 750
        __tmp1 = np.where(((__input_data['land_use'] == 5) & (wv > 750.0)), 1.3, __tmp1)

        # Nadelwald und wv ≤ 750
        __tmp1 = np.where(((__input_data['land_use'] == 5) & (wv <= 750.0)), 1.68 * (np.log10(wv)) - 3.53, __tmp1)

        # Nadelwald
        # grundwasserbeinflusst
        __tmp2 = np.where(
            ((__input_data['land_use'] == 5) & ((__input_data['bodentyp'] == 16) | (__input_data['bodentyp'] == 19) |
                                                (__input_data['bodentyp'] == 20) | (__input_data['bodentyp'] == 21) | (
                                                            __input_data['bodentyp'] == 22))), 0.81, __tmp2)

        # terrestrisch
        __tmp2 = np.where(
            ((__input_data['land_use'] == 5) & ((__input_data['bodentyp'] < 16) | (__input_data['bodentyp'] == 17) |
                                                (__input_data['bodentyp'] == 18) | (__input_data['bodentyp'] == 23))),
            0.92, __tmp2)

        # grundwasserbeinflusst
        __tmp3 = np.where(
            ((__input_data['land_use'] == 5) & ((__input_data['bodentyp'] == 16) | (__input_data['bodentyp'] == 19) |
                                                (__input_data['bodentyp'] == 20) | (__input_data['bodentyp'] == 21) | (
                                                            __input_data['bodentyp'] == 22))), 3.2, __tmp3)

        # terrestrisch
        __tmp3 = np.where(
            ((__input_data['land_use'] == 5) & ((__input_data['bodentyp'] < 16) | (__input_data['bodentyp'] == 17) |
                                                (__input_data['bodentyp'] == 18) | (__input_data['bodentyp'] == 23))),
            3.52, __tmp3)

        #########################################################################
        # Laubwald und wv > 750
        __tmp1 = np.where(
            ((__input_data['land_use'] == 6) | (__input_data['land_use'] == 3) | (__input_data['land_use'] == 4) |
             (__input_data['land_use'] == 7) | (__input_data['land_use'] == 9)), 0.9 * 1.3, __tmp1)
        # __tmp1 = np.where(((__input_data['land_use'] == 6) & (wv > 750.0)) , 1.3, __tmp1)

        # Laubwald und wv ≤ 750
        __tmp1 = np.where(
            (((__input_data['land_use'] == 6) | (__input_data['land_use'] == 3) | (__input_data['land_use'] == 4) |
              (__input_data['land_use'] == 7) | (__input_data['land_use'] == 9)) & (wv <= 750)),
            0.9 * (1.68 * (np.log10(wv)) - 3.53), __tmp1)
        # __tmp1 = np.where(((__input_data['land_use'] == 6) & (wv <= 750)) , (1.68 * (np.log10(wv)) - 3.53),
        # __tmp1)

        # Laubwald
        # grundwasserbeinflusst
        __tmp2 = np.where(
            (((__input_data['land_use'] == 6) | (__input_data['land_use'] == 3) | (__input_data['land_use'] == 4) |
              (__input_data['land_use'] == 7) | (__input_data['land_use'] == 9)) &
             ((__input_data['bodentyp'] == 16) | (__input_data['bodentyp'] == 19) | (__input_data['bodentyp'] == 20) |
              (__input_data['bodentyp'] == 21) | (__input_data['bodentyp'] == 22))), 0.81, __tmp2)

        # terrestrisch
        __tmp2 = np.where(
            (((__input_data['land_use'] == 6) | (__input_data['land_use'] == 3) | (__input_data['land_use'] == 4) |
              (__input_data['land_use'] == 7) | (__input_data['land_use'] == 9)) &
             ((__input_data['bodentyp'] < 16) | (__input_data['bodentyp'] == 17) |
              (__input_data['bodentyp'] == 18) | (__input_data['bodentyp'] == 23))), 0.92, __tmp2)

        # grundwasserbeinflusst
        __tmp3 = np.where(
            (((__input_data['land_use'] == 6) | (__input_data['land_use'] == 3) | (__input_data['land_use'] == 4) |
              (__input_data['land_use'] == 7) | (__input_data['land_use'] == 9)) &
             ((__input_data['bodentyp'] == 16) | (__input_data['bodentyp'] == 19) | (__input_data['bodentyp'] == 20) |
              (__input_data['bodentyp'] == 21) | (__input_data['bodentyp'] == 22))), 3.2, __tmp3)

        # terrestrisch
        __tmp3 = np.where(
            (((__input_data['land_use'] == 6) | (__input_data['land_use'] == 3) | (__input_data['land_use'] == 4) |
              (__input_data['land_use'] == 7) | (__input_data['land_use'] == 9)) &
             ((__input_data['bodentyp'] < 16) | (__input_data['bodentyp'] == 17) |
              (__input_data['bodentyp'] == 18) | (__input_data['bodentyp'] == 23))), 3.52, __tmp3)

        __oa_ns = 1.0 - __input_data['surface_runoff'] / (__input_data['rain_summer'] + __input_data['rain_winter'])

        __result = (__input_data['rain_summer'] + __input_data['rain_winter']) * __oa_ns - __input_data[
            'etp'] * __tmp1 * \
                   (__tmp2 * np.log10(1.0 / __input_data['etp']) + __tmp3)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        del __tmp1
        del __tmp2
        del __tmp3
        del __oa_ns
        del __input_data

        return __result

    def cal_drainage_rate(self, **kwargs):
        """
            function to calculate the drainage

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('drainage_rate', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __ka = np.where((__input_data['land_use'] < 3), 0.0, np.nan)
        __wv = self.cal_wv(__ka, kwargs)
        __sw = self.cal_percolation_rate_gras(__wv, kwargs)

        __result = np.where((__input_data['land_use'] < 3), __sw * __input_data['draenflaeche'] / 100.0, __result)
        __result = np.where((__input_data['land_use'] > 2), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __ka
        del __wv
        del __sw
        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_percolation_rate(self, **kwargs):
        """
            function to calculate the percolation rate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('percolation_rate', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        # __ka = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        # __wpf = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        # Total area
        __f_all = __input_data['qw'] + __input_data['ww'] + __input_data['wg'] + __input_data['wr'] + __input_data[
            'sg'] + __input_data['sm'] + \
                  __input_data['km'] + __input_data['oel'] + __input_data['k'] + __input_data['hf'] + __input_data[
                      'sb'] + __input_data['kl'] + \
                  __input_data['fl'] + __input_data['fg'] + __input_data['th'] + __input_data['td'] + __input_data[
                      'eb'] + __input_data['sp'] + \
                  __input_data['brache'] + __input_data['r'] + __input_data['ik'] + __input_data['tr'] + __input_data[
                      'gp'] + \
                  __input_data['kup'] + __input_data['mi']

        __f_gedreide = __input_data['wg'] + __input_data['wr'] + __input_data['sg'] + __input_data['oel'] + \
                       __input_data['kl'] + \
                       __input_data['fg'] + __input_data['brache'] + __input_data['r'] + __input_data['ik'] + \
                       __input_data['tr'] + __input_data['gp'] + __input_data['mi']

        __f_mais = __input_data['qw'] + __input_data['ww'] + __input_data['sm'] + __input_data['km'] + __input_data[
            'k'] + __input_data['hf'] + __input_data['sb']

        __f_gruen = __input_data['fl'] + __input_data['kup']

        __proz_gedreide = __f_gedreide / __f_all
        __proz_mais = __f_mais / __f_all
        __proz_gruen = __f_gruen / __f_all

        # print '1'
        __kr = self.cal_kr(kwargs)

        __ka_kli = self.cal_ka_kli(kwargs)

        __ta_gedreide = self.cal_ta(1, __kr, kwargs)

        __ka_max_gedreide = self.cal_ka_max(__ta_gedreide, __kr)

        __ka_gedreide = self.cal_ka(__ka_max_gedreide, __ka_kli)

        __wv_gedreide = self.cal_wv(__ka_gedreide, kwargs)

        __sw_gedreide = self.cal_percolation_rate_gras(__wv_gedreide, kwargs)

        # print '2'
        __ta_mais = self.cal_ta(2, __kr, kwargs)

        __ka_max_mais = self.cal_ka_max(__ta_mais, __kr)

        __ka_mais = self.cal_ka(__ka_max_mais, __ka_kli)

        __wv_mais = self.cal_wv(__ka_mais, kwargs)

        __sw_mais = self.cal_percolation_rate_gras(__wv_mais, kwargs)

        # print '3'
        __ta_gruen = self.cal_ta(3, __kr, kwargs)

        __ka_max_gruen = self.cal_ka_max(__ta_gruen, __kr)

        __ka_gruen = self.cal_ka(__ka_max_gruen, __ka_kli)

        __wv_gruen = self.cal_wv(__ka_gruen, kwargs)

        __sw_gruen_gras = self.cal_percolation_rate_gras(__wv_gruen, kwargs)

        __wpf_gruen = self.cal_wpf(__ka_gruen, kwargs)

        #
        # __wpf_gruen = self.cal_wpf(__ka_max_gruen, kwargs) ist egal!!!!
        #
        __sw_gruen_liebscher = self.cal_percolation_rate_liebscher(__wpf_gruen, kwargs)

        """
        print 'land_use'
        print __input_data['land_use'][1065:1075, 284:294]

        print '__wpf_gruen'
        print __wpf_gruen[1065:1075, 284:294]

        print 'kr'
        print __kr[1065:1075, 284:294]

        print 'ka_kli'
        print __ka_kli[1065:1075, 284:294]

        print '__ta_gruen'
        print __ta_gruen[1065:1075, 284:294]

        print '__ka_max_gruen'
        print __ka_max_gruen[1065:1075, 284:294]

        print '__ka_gruen'
        print __ka_gruen[1065:1075, 284:294]

        print '__wv_gruen'
        print __wv_gruen[1065:1075, 284:294]

        print '__sw_gruen_gras'
        print __sw_gruen_gras[1065:1075, 284:294]

        print '__sw_gruen_liebscher'
        print __sw_gruen_liebscher[1065:1075, 284:294]
        """

        """
        if((F_teil+F_kup) > 0){
                dblSW_gruen_oKup = funcSickerwasserrate_Gras (iHauptnutzung, dblWv_gruen) * F_teil/(F_teil+F_kup)
                dblSW_Kup = funcSickerwasserrate_Gras (5, dblWv_gruen) * F_kup/(F_teil+F_kup)
                dblSW_gruen = (dblSW_Kup + dblSW_gruen_oKup) * dblProz_gruen
        }else{dblSW_gruen = 0;}
        """

        """
        __ka = np.where((__input_data['land_use'] == 1), __ka_gedreide *__proz_gedreide + __ka_mais *__proz_mais + 
        __ka_gruen *__proz_gruen, __ka)
        __ka = np.where((__input_data['land_use'] == 2), __ka_gruen, __ka)
        __ka = np.where((__input_data['land_use'] == 3), __ka_gruen, __ka)
        __ka = np.where((__input_data['land_use'] == 4), __ka_gruen, __ka)
        __ka = np.where((__input_data['land_use'] == 5), __ka_gruen, __ka)
        __ka = np.where((__input_data['land_use'] == 6), __ka_gruen, __ka)
        __ka = np.where((__input_data['land_use'] == 7), __ka_gruen, __ka)
        __ka = np.where((__input_data['land_use'] == 8), 0.0, __ka)
        __ka = np.where((__input_data['land_use'] == 9), __ka_gruen, __ka)
        """

        """"
        __result = np.where((__input_data['land_use'] == 1),
                            __sw_gedreide * __proz_gedreide + __sw_mais * __proz_mais + __sw_gruen_gras * __proz_gruen,
                            __result)
        __result = np.where((__input_data['land_use'] == 2), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 3), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 4), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 5), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 6), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 7), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 8), 0.0, __result)
        __result = np.where((__input_data['land_use'] == 9), __sw_gruen_gras, __result)
        """

        __result = np.where((__input_data['land_use'] == 1),
                            __sw_gedreide * __proz_gedreide + __sw_mais * __proz_mais + __sw_gruen_gras * __proz_gruen,
                            __result)
        __result = np.where((__input_data['land_use'] == 2), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 3), __sw_gruen_liebscher, __result)
        __result = np.where((__input_data['land_use'] == 4), __sw_gruen_liebscher, __result)
        __result = np.where((__input_data['land_use'] == 5), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 6), __sw_gruen_gras, __result)
        __result = np.where((__input_data['land_use'] == 7), __sw_gruen_liebscher, __result)
        __result = np.where((__input_data['land_use'] == 8), 0.0, __result)
        __result = np.where((__input_data['land_use'] == 9), __sw_gruen_liebscher, __result)

        # print '__result'
        # print __result[1065:1075, 284:294]

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __input_data
        del __f_all
        del __f_gedreide
        del __f_mais
        del __f_gruen
        del __proz_gedreide
        del __proz_mais
        del __proz_gruen
        del __kr
        del __ka_kli
        del __ta_gedreide
        del __ka_max_gedreide
        del __ka_gedreide
        del __wv_gedreide
        del __sw_gedreide
        del __ta_mais
        del __ka_max_mais
        del __ka_mais
        del __wv_mais
        del __sw_mais
        del __ta_gruen
        del __ka_max_gruen
        del __ka_gruen
        del __wv_gruen
        del __sw_gruen_gras
        del __sw_gruen_liebscher

        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_groundwater_runoff(self, **kwargs):
        """
            function to calculate the groundwater runoff

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('groundwater_runoff', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = np.where((__input_data['percolation_rate'] > 0.0),
                            __input_data['percolation_rate'] * __input_data['exposure_quotient'],
                            __input_data['percolation_rate'] + (1.0 - __input_data['exposure_quotient']) *
                            __input_data['percolation_rate'])

        # Siedlung
        __result = np.where((__input_data['land_use'] == 7),
                            (__result * (1.0 - 0.75 * __input_data['versiegelungsgrad'] / 100.0)), __result)

        __input_data['runoff_quotient'] = np.where(__input_data['runoff_quotient'] == 0.0, 999999999.0,
                                                   __input_data['runoff_quotient'])

        __result = __result * (1.0 - __input_data['draenflaeche'] / 100.0) / __input_data['runoff_quotient']

        # Gewässer ist Basisabfluss = 0
        __result = np.where((__input_data['land_use'] == 8), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_interflow(self, **kwargs):
        """
            function to calculate the interflow
            (calculates the interflow as a proportion (runoff quotient) of the GW discharge)

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('interflow', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = (__input_data['runoff_quotient'] - 1) * __input_data['groundwater_runoff']

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_sickerwasserrate(self, **kwargs):
        """
            function to calculate the 'Sickerwasserrate'
            (calculate 'Sickerwasserrate' from groundwater runoff and interflow)

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('sickerwasserrate', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = __input_data['groundwater_runoff'] + __input_data['interflow']

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_rain_discharge(self, **kwargs):
        """
            function to calculate the rain discharge

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('rain_discharge', kwargs)

        __cnspl = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        __nmean = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        __ia = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        __surface_runoff_cn = np.where(__input_data['land_use'] >= 0, 0, np.nan)
        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __cnspl = (99.0 * np.exp(0.00673 * (100.0 - 99.0)) - 99.0) / 3 * (
                1.0 - 2.0 * np.exp(-13.86 * __input_data['slope'] / 45.0)) + 99.0

        __nmean = np.where(__input_data['regentage'] > 0.0,
                           (__input_data['rain_summer'] + __input_data['rain_winter']) / __input_data[
                               'regentage'], 0.0)

        __ia = 0.03 * (1000 / __cnspl - 10) * 25.4

        __result = np.square(__nmean - __ia) / (__nmean - __ia + __ia / 0.03) * __input_data['regentage'] * (
                __input_data['versiegelungsgrad'] / 100.0)

        # nur bei Siedlung
        __result = np.where((__input_data['land_use'] != 7), 0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __surface_runoff_cn
        del __cnspl
        del __nmean
        del __ia
        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_total_runoff(self, **kwargs):
        """
            function to calculate the total runoff
            (Summe aus Drainage, GW-Abfluss, Zwischenabfluss, Oberflächenabfluss, Direktabfluss)

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('total_runoff', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = __input_data['drainage_rate'] + __input_data['groundwater_runoff'] + \
                   __input_data['interflow'] + __input_data['surface_runoff'] + __input_data['rain_discharge']

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_eta(self, **kwargs):
        """
            function to calculate the evapotranspiration

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_waterbalance('eta', kwargs)

        __result = np.where(__input_data['land_use'] >= 0, 0, np.nan)

        __result = __input_data['rain_summer'] + __input_data['rain_winter'] - __input_data['total_runoff']

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result
