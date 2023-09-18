# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# import sys
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


class n_budget:
    """
        Class to create the N budget
    """

    def __init__(self, data_config, data_param, data_area, data_level, data_nc):

        self.project_data = project_data(data_config, data_param, data_area, data_level, data_nc)

    def cal_n_siedlung_regenwasserkanal(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('n_siedlung_regenwasserkanal', kwargs)

        __kp = 4.02
        __permeability = 0.75

        # Siedlung
        __result = np.where((__input_data['land_use'] == 7), __input_data['versiegelungsgrad'] / 100.0 * __kp * 
                            __permeability, np.nan)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_n_siedlung_unversiegelt(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('n_siedlung_unversiegelt', kwargs)

        __permeability = 0.75

        # Siedlung
        # __result = np.where((__input_data['land_use'] == 7), __input_data['bilanzsaldo'] + __input_data['natmos'] - 
        # __input_data['ndenitr'] * (1.0 - __permeability * __input_data['versiegelungsgrad'] / 100.0),np.nan)
        __result = np.where((__input_data['land_use'] == 7), __input_data['natmos'] - __input_data['ndenitr'] * 
                            (1.0 - __permeability * __input_data['versiegelungsgrad'] / 100.0), np.nan)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_bilanzsaldo_zf(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('bilanzsaldo_zf', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # Gewässer
        __result = np.where((__hn == 1), (__input_data['bilanzsaldo_preprocess'] +
                                          (__input_data['zwf_preprocess'] * 24.0) - (__input_data['zwf'] * 24.0)),
                            __input_data['bilanzsaldo_preprocess'])

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_nmin_austrag(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_austrag', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # Gewässer
        __result = np.where((__hn == 8), __input_data['natmos'], np.nan)

        # Wald, Laubwald
        __result = np.where((__hn == 5) | (__hn == 6), __input_data['natmos'] - __input_data['ndenitr'] - 
                            __input_data['immobilisierungsrate'] - __input_data['nnetto'], __result)

        # Siedlung
        __result = np.where((__hn == 7), __input_data['n_siedlung_unversiegelt'], __result)

        # Acker, Grünland, Obstbau, Weinbau, Devastierung
        __result = np.where((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4), (__input_data['bilanzsaldo'] + 
                            __input_data['natmos'] - __input_data['ndenitr']), __result)

        # Devastierung
        __result = np.where((__hn == 9), (__input_data['natmos'] - __input_data['ndenitr']), __result)

        # nmin_austrag < 0.0 => nmin_austrag = 0.0
        __result = np.where((__result < 0), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)
        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_cnmin_zgw(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('cnmin_zgw', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']
        __az_plus_ab = __input_data['zwischenabfluss'] + __input_data['basisabfluss']
        __az_plus_ab_plus_ao = __input_data['zwischenabfluss'] + __input_data['basisabfluss'] + \
                               __input_data['oberflaechenabfluss']

        __tmp = np.where((__az_plus_ab_plus_ao == 0.0) | (__input_data['basisabfluss'] < 0.0), 0.0, 
                         __az_plus_ab / __az_plus_ab_plus_ao * 100.0 / __az_plus_ab)

        # Gewässer
        __result = np.where((__hn == 8), 0.0, __result)

        # Siedlung
        __result = np.where((__hn == 7), (__input_data['nmin_austrag'] * __tmp), __result)

        # Wald, Laubwald
        __result = np.where((__hn == 5) | (__hn == 6), __input_data['nmin_austrag'] * __tmp, __result)

        # Acker, Grünland, Obstbau, Weinbau, Gewässer, Devastierung
        __result = np.where((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 8) | (__hn == 9), 
                            __input_data['nmin_austrag'] * (1.0 - __input_data['draenflaeche'] / 100.0) * __tmp, 
                            __result)
        
        # cnmin_zgw < 0.0 => cnmin_zgw = 0.0
        __result = np.where((__result < 0.0), 0.0, __result)

        # cnmin_zgw < 0.0 => cnmin_zgw = 0.0 | Gewässer
        __result = np.where((__result < 0.0), 0.0, __result * 4.43)

        # cnmin_zgw > 1000.0 => cnmin_zgw = 1000.0
        __result = np.where((__result > 1000.0), 1000.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result
    
    def cal_cnmin_zgw_max_50mg_l(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('cnmin_zgw_max_50mg_l', kwargs)

        __result = np.zeros_like(__input_data['land_use'])
        
        __result = __input_data['nmin_austrag'] * 100 * 4.43 / __input_data['gesamtabfluss']

        # cnmin_zgw > 1000.0 => cnmin_zgw = 1000.0
        __result = np.where((__result > 1000.0), 1000.0, __result)
        
        __result = np.where((__result < 0.0), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_nmin_zgw(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_zgw', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']
        __az_plus_ab = __input_data['zwischenabfluss'] + __input_data['basisabfluss']
        __az_plus_ab_plus_ao = __input_data['zwischenabfluss'] + __input_data['basisabfluss'] + \
                               __input_data['oberflaechenabfluss']

        __tmp = np.where((__az_plus_ab_plus_ao == 0.0) | (__input_data['basisabfluss'] < 0.0), 0.0, 
                         __az_plus_ab / __az_plus_ab_plus_ao)

        # Gewässer
        __result = np.where((__hn == 8), 0.0, __result)

        # Wald, Laubwald & basisabfluss > 0
        __result = np.where(((__hn == 5) | (__hn == 6)) & (__input_data['basisabfluss'] > 0.0), 
                            __input_data['nmin_austrag'] * __tmp, __result)

        # Wald, Laubwald & basisabfluss <= 0
        __result = np.where(((__hn == 5) | (__hn == 6)) & (__input_data['basisabfluss'] <= 0.0), 
                            __input_data['nmin_austrag'], __result)

        # Siedlung & basisabfluss > 0
        __result = np.where((__hn == 7) & (__input_data['basisabfluss'] > 0.0), 
                            __input_data['n_siedlung_unversiegelt'] * __tmp, __result)

        # Acker, Grünland, Obstbau, Weinbau, Gewässer, Devastierung & basisabfluss > 0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 9)) 
                            & (__input_data['basisabfluss'] > 0.0), 
                            (__input_data['nmin_austrag']) * (1.0 - __input_data['draenflaeche'] / 100.0) * __tmp, 
                            __result)

        # Acker, Grünland, Obstbau, Weinbau, Gewässer, Siedlung, Devastierung & basisabfluss <= 0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 7) | (__hn == 9))
                            & (__input_data['basisabfluss'] <= 0.0), 
                            (__input_data['nmin_austrag']) * (1.0 - __input_data['draenflaeche'] / 100.0), __result)

        # basisabfluss < 0.0 => nmin_zgw = 0.0
        # __result = np.where((__input_data['basisabfluss'] < 0.0) , 0.0, __result)

        # nmin_zgw < 0.0 => nmin_zgw = 0.0
        __result = np.where((__result < 0), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)
        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_nmin_r(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_r', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        # Siedlung
        __result = np.where((__input_data['land_use'] == 7), __input_data['nmin_austrag'], 0.0)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nmin_ao(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_ao', kwargs)

        __hn = __input_data['land_use']

        __result = np.zeros_like(__input_data['land_use'])

        __tmp = __input_data['oberflaechenabfluss'] / (__input_data['zwischenabfluss'] + __input_data['basisabfluss'] + 
                                                       __input_data['oberflaechenabfluss'])

        # Siedlung
        __result = np.where((__hn == 7), 0.0, __result)

        # Gewässer
        __result = np.where((__hn == 8), __input_data['natmos'], __result)

        # Wald, Laubwald & basisabfluss > 0
        __result = np.where(((__hn == 5) | (__hn == 6)) & (__input_data['basisabfluss'] > 0.0), 
                            __input_data['nmin_austrag'] * __tmp, __result)

        # Wald, Laubwald & basisabfluss <= 0
        __result = np.where(((__hn == 5) | (__hn == 6)) & (__input_data['basisabfluss'] <= 0.0), 0.0, __result)

        # Acker, Grünland, Obstbau, Weinbau, Devastierung & basisabfluss > 0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 9)) 
                            & (__input_data['basisabfluss'] > 0.0), 
                            (__input_data['nmin_austrag']) * (1.0 - __input_data['draenflaeche'] / 100.0) * __tmp, 
                            __result)

        # Acker, Grünland, Obstbau, Weinbau, Gewässer, Devastierung & basisabfluss <= 0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 9)) 
                            & (__input_data['basisabfluss'] <= 0.0), 0.0, __result)

        # nmin_ao < 0.0 => nmin_ao = 0.0
        __result = np.where((__result < 0.0), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)
        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nmin_ag(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_ag', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        __tmp = np.where((__input_data['zwischenabfluss'] + __input_data['basisabfluss'] +
                          __input_data['oberflaechenabfluss']) != np.nan,
                         (__input_data['basisabfluss'] / (__input_data['zwischenabfluss'] +
                                                          __input_data['basisabfluss'] +
                                                          __input_data['oberflaechenabfluss'])), 0.0)

        # Gewässer
        __result = np.where((__hn == 8), 0.0, __result)

        # Wald, Laubwald & basisabfluss > 0
        __result = np.where(((__hn == 5) | (__hn == 6)) & (__input_data['basisabfluss'] > 0.0),
                            __input_data['nmin_austrag'] * __tmp, __result)

        # Wald, Laubwald & basisabfluss <= 0
        __result = np.where(((__hn == 5) | (__hn == 6)) & (__input_data['basisabfluss'] <= 0.0),
                            __input_data['nmin_austrag'] / __input_data['abflussquotient'], __result)

        # Acker, Grünland, Obstbau, Weinbau, Siedlung, Devastierung & basisabfluss > 0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 7) | (__hn == 9))
                            & (__input_data['basisabfluss'] > 0.0),
                            (__input_data['nmin_austrag']) * (1.0 - __input_data['draenflaeche'] / 100.0) * __tmp,
                            __result)

        # Acker, Grünland, Obstbau, Weinbau, Siedlung, Devastierung & basisabfluss <= 0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 7) | (__hn == 9))
                            & (__input_data['basisabfluss'] <= 0.0),
                            (__input_data['nmin_austrag']) *
                            (1.0 - __input_data['draenflaeche'] / 100.0) / __input_data['abflussquotient'], __result)

        # nmin_ag < 0.0 => nmin_ag = 0.0
        __result = np.where((__result < 0.0), 0.0, __result)
        __result = np.where((__input_data['abflussquotient'] == 0.0), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)
        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nmin_ag_denitr(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_ag_denitr', kwargs)

        __result = np.zeros_like(__input_data['land_use'])
        __hn = __input_data['land_use']

        __result = __input_data['nmin_ag_denitr']

        # Gewässer
        __result = np.where((__hn == 8), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)
        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nmin_ag_denitr_proz(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_ag_denitr_proz', kwargs)

        # __result = np.zeros_like(__input_data['land_use'])

        __result = np.where(__input_data['nmin_ag'] > 0.0,
                            __input_data['nmin_ag_denitr'] / __input_data['nmin_ag'] * 100.0, 0.0)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nmin_az(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_az', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        __tmp = np.where((__input_data['zwischenabfluss'] + __input_data['basisabfluss'] +
                          __input_data['oberflaechenabfluss']) != np.nan,
                         (__input_data['zwischenabfluss'] / (__input_data['zwischenabfluss'] +
                                                             __input_data['basisabfluss'] +
                                                             __input_data['oberflaechenabfluss'])), 0.0)

        # Gewässer
        __result = np.where((__hn == 8), 0.0, np.nan)

        # Wald, Laubwald & basisabfluss > 0
        __result = np.where(((__hn == 5) | (__hn == 6)) & (__input_data['basisabfluss'] > 0.0),
                            __input_data['nmin_austrag'] * __tmp, __result)

        # Wald, Laubwald & basisabfluss <= 0
        __result = np.where(((__hn == 5) | (__hn == 6)) & (__input_data['basisabfluss'] <= 0.0),
                            __input_data['nmin_austrag'] * (1.0 - 1.0 / __input_data['abflussquotient']), __result)

        # Acker, Grünland, Obstbau, Weinbau, Siedlung, Devastierung & basisabfluss > 0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 7) | (__hn == 9))
                            & (__input_data['basisabfluss'] > 0.0),
                            (__input_data['nmin_austrag']) * (1.0 - __input_data['draenflaeche'] / 100.0) * __tmp,
                            __result)

        # Acker, Grünland, Obstbau, Weinbau, Siedlung, Devastierung & basisabfluss <= 0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 7) | (__hn == 9))
                            & (__input_data['basisabfluss'] <= 0.0),
                            (__input_data['nmin_austrag']) * (1.0 - __input_data['draenflaeche'] / 100.0)
                            * (1.0 - 1.0 / __input_data['abflussquotient']), __result)

        # nmin_az < 0.0 => nmin_az = 0.0
        __result = np.where((__result < 0), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)
        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __tmp
        del __hn
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nmin_draen(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_draen', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __result = __input_data['nmin_austrag'] * __input_data['draenflaeche'] / 100.0

        __result = np.where((__result < 0.0), 0.0, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)
        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nmin_a(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nmin_a', kwargs)

        __result = np.zeros_like(__input_data['land_use'])
        __hn = __input_data['land_use']

        # Gewässer
        __result = np.where((__hn == 8), __input_data['nmin_ao'], np.nan)

        # kein Gewässer
        __result = np.where((__hn != 8), __input_data['nmin_draen'] + __input_data['nmin_az'] +
                            __input_data['nmin_ao'] + __input_data['nmin_ag_denitr'], __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_cnmin_ag(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('cnmin_ag', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __result = np.where((__input_data['basisabfluss'] > 0.0),
                            __input_data['nmin_ag_denitr'] / __input_data['basisabfluss'] * 100.0 * 4.43, np.nan)

        __result = np.where((__input_data['basisabfluss'] <= 0.0), 0.0, __result)

        __result = np.where((__result > 1000.0), 1000.0, __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_npart(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('npart', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        __result = np.where((__hn != 7) | (__hn != 8) | (__hn != 9),
                            __input_data['nt_boden'] * __input_data['sedimenteintrag'] / 1000 / 3000, 0.0)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] <= 6)), 0.0, __result)
        __result = np.where((__hn > 6), np.nan, __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nges_austrag(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nges_austrag', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        # Gewässer
        __result = np.where((__input_data['land_use'] == 8), __input_data['nmin_austrag'], __result)

        # Siedlung
        __result = np.where((__input_data['land_use'] == 7), __input_data['nmin_austrag'] +
                            __input_data['n_siedlung_haus_o_kanal'] + __input_data['n_siedlung_regenwasserkanal'],
                            __result)

        # kein Gewässer & keine Siedung
        __result = np.where((__input_data['land_use'] != 7) & (__input_data['land_use'] != 8),
                            __input_data['nmin_austrag'] + __input_data['npart'], __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result

    def cal_nges(self, **kwargs):
        """
            function to calculate the

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_n_budget('nges', kwargs)

        # alle
        __result = __input_data['nmin_a'] + __input_data['npart']

        # Gewässer
        __result = np.where((__input_data['land_use'] == 8), __input_data['nmin_a'], __result)

        # Siedlung
        __result = np.where((__input_data['land_use'] == 7), __input_data['nmin_a'] +
                            __input_data['n_siedlung_haus_o_kanal'] + __input_data['n_siedlung_regenwasserkanal'],
                            __result)

        # Devastierung
        __result = np.where((__input_data['land_use'] == 9), __input_data['nmin_a'], __result)

        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        return __result
