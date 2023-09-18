# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import numpy as np

from general.project_data import project_data


# # This is the main class of the module p_butget
# @date  23.03.2023
#
# @author Stephan Bürger <br>
#        VisDat geodatentechnologie GmbH<br>
#        01277 Dresden <br>
#        Am Ende 14 <br>
#        http://www.galf-dresden.de <br>
#        info@galf-dresden.de <br>
#


class p_budget:
    """
            Class to create the P budget
        """

    def __init__(self, data_config, data_param, data_area, data_level, data_nc):

        self.project_data = project_data(data_config, data_param, data_area, data_level, data_nc)

    def cal_p_ag(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('p_ag', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # (kein Gewässer, keine Siedlung und keine Devastierung) & groundwater_runoff >= 0.0
        __result = np.where((((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)) &
                             (__input_data['groundwater_runoff'] > 0.0)),
                            __input_data['groundwater_runoff'] * __input_data['cp_ag'] / 100.0,
                            __result)

        __result = np.where((((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)) &
                             (__input_data['groundwater_runoff'] <= 0.0)), 0.0, __result)

        __result = np.where(((np.isnan(__result)) & (__hn <= 6)), 0.0, __result)
        __result = np.where((__hn > 6), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_p_ao(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('p_ao', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # (kein Gewässer, keine Siedlung und keine Devastierung) & Oberflächenabfluss >= 0.0
        __result = np.where((((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)) &
                             (__input_data['surface_runoff'] > 0.0)), __input_data['surface_runoff'] *
                            __input_data['cp_ao'] / 100.0, __result)

        __result = np.where((((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)) &
                             (__input_data['surface_runoff'] <= 0.0)), 0.0, __result)

        __result = np.where(((np.isnan(__result)) & (__hn <= 6)), 0.0, __result)
        __result = np.where((__hn > 6), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_p_az(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('p_az', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # (kein Gewässer, keine Siedlung und keine Devastierung) & interflow >= 0.0
        # __result = np.where((((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)) & 
        # (__input_data['interflow'] > 0.0)), 
        # __input_data['interflow'] * __input_data['cp_az'] / 100.0, __result)

        __result = np.where((((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)) &
                             (__input_data['interflow'] > 0.0)), __input_data['interflow'] * 0.01 / 100.0, __result)

        __result = np.where((((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)) &
                             (__input_data['interflow'] <= 0.0)), 0.0, __result)

        __result = np.where(((np.isnan(__result)) & (__hn <= 6)), 0.0, __result)
        __result = np.where((__hn > 6), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_p_draen(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('p_draen', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # (kein Gewässer, keine Siedlung und keine Devastierung) & Dränabfluss >= 0.0
        __result = np.where((((__hn == 1) | (__hn == 2)) & (__input_data['drainage_rate'] > 0.0)),
                            __input_data['drainage_rate'] * __input_data['cp_drean'] / 100.0, __result)

        __result = np.where((((__hn == 1) | (__hn == 2)) & (__input_data['drainage_rate'] <= 0.0)), 0.0, __result)

        __result = np.where(((__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)), 0.0, __result)

        __result = np.where(((np.isnan(__result)) & (__hn <= 6)), 0.0, __result)
        __result = np.where((__hn > 6), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_ppart_gruen(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('ppart_gruen', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # (kein Gewässer, keine Siedlung und keine Devastierung) & Dränabfluss >= 0.0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)),
                            __input_data['er'] * __input_data['pt_boden'] * __input_data['sediment_input'] / 1000000.0,
                            __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] <= 6)), 0.0, __result)

        __result = np.where((__hn == 1), __result / (1.0 - (0.14 * 0.4)) , __result)

        __result = np.where((__hn == 1), __result * (1.0 - (__input_data['gruenland'] * 0.4)), __result)

        __result = np.where((__hn > 6), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_ppart(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('ppart', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # (kein Gewässer, keine Siedlung und keine Devastierung) & Dränabfluss >= 0.0
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)),
                            __input_data['er'] * __input_data['pt_boden'] * __input_data['sediment_input'] / 1000000.0,
                            __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] <= 6)), 0.0, __result)
        __result = np.where((__hn > 6), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_pgel(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('pgel', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        __result = np.where((__hn <= 10), 0.0, __result)

        # (kein Gewässer, keine Siedlung und keine Devastierung) & Dränabfluss >= 0.0
        # __result = __input_data['p_ag'] + __input_data['p_ao'] + __input_data['p_az'] + __input_data['p_draen']
        __result = np.where((__hn <= 6),
                            __input_data['p_ag'] + __input_data['p_ao'] + __input_data['p_az'] + __input_data[
                                'p_draen'], np.nan)

        __result = np.where(((np.isnan(__result)) & (__hn <= 6)), 0.0, __result)
        # __result = np.where((__hn > 6), np.nan, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_pges(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('pges', kwargs)

        __result = np.zeros_like(__input_data['land_use'])

        __hn = __input_data['land_use']

        # kein Gewässer, keine Siedlung und keine Devastierung
        __result = np.where(((__hn == 1) | (__hn == 2) | (__hn == 3) | (__hn == 4) | (__hn == 5) | (__hn == 6)),
                            __input_data['ppart'] + __input_data['pgel'], __result)

        # Siedlung
        __result = np.where((__hn == 7),
                            __input_data['p_unversiegelt'] + __input_data['p_siedlung_regenwasserkanal'] +
                            __input_data['p_siedlung_haus_o_kanal'], __result)

        # Gewässer
        __result = np.where((__hn == 8), 0.4, __result)

        # Devastierung
        __result = np.where((__hn == 9), 0.5, __result)

        __result = np.where(np.isnan(__input_data['land_use']), np.nan, __result)

        __result = np.where(((np.isnan(__result)) & (__input_data['land_use'] > 0)), 0.0, __result)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_p_siedung_ew_ohne_anschluss(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('p_siedung_ew_ohne_anschluss', kwargs)

        # Siedlung
        __result = np.where((__input_data['land_use'] == 7), __input_data['p_ew_ohne_anschluss'], np.nan)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_p_siedlung_regenwasserkanal(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('p_siedlung_regenwasserkanal', kwargs)

        __kp = 1.23
        __permeability = 0.75

        # Siedlung
        __result = np.where((__input_data['land_use'] == 7),
                            __input_data['versiegelungsgrad'] / 100.0 * __kp * __permeability, np.nan)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result

    def cal_p_siedlung_unversiegelt(self, **kwargs):
        """
            function to calculate

            Parameter:
                kwargs (kwargs['id_param'], kwargs['dtype'], kwargs['decimals'], kwargs['fileSuffix'])

            Returns:
                (numpy) 2 dimensional array for the map display
        """

        __input_data = self.project_data.get_data_p_budget('p_siedlung_unversiegelt', kwargs)

        __kp = 0.5
        __rboden = 0.9
        __permeability = 0.75

        # Siedlung
        __result = np.where((__input_data['land_use'] == 7), __kp * (1.0 - __rboden) *
                            (1.0 - (__input_data['versiegelungsgrad'] / 100.0 * __permeability)), np.nan)

        __result = np.where(__input_data['model_area'] > 0, __result, np.nan)
        del __input_data
        self.project_data.set_data(__result, kwargs, True)
        del __result
