# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# import sys

from water_balance.water_balance import water_balance
from soil_erosion.soil_erosion import soil_erosion
from sediment_input.sediment_input import sediment_input
from n_budget.n_budget import n_budget
from p_budget.p_budget import p_budget
from general.project_data import project_data


class process:

    # Konstruktor.
    def __init__(self, data_config, data_param, data_area, data_level, data_nc):

        self.id_sc = data_config['id_sc']
        self.data_config = data_config
        self.data_level = data_level
        self.data_nc = data_nc
        self.data_param = data_param
        self.data_area = data_area

        self.project_data = project_data(data_config, data_param, data_area, data_level, data_nc)

    def stb_processing(self):

        """
            hier werden die Funktionen, die in der WaterBalance Class definiert sind, aufgerufen.

            Parameter:
                None

            Returns:
                None
        """

        ####################################################
        # ################ Water Balance ####################
        ####################################################
        wb = water_balance(self.data_config, self.data_param, self.data_area, self.data_level, self.data_nc)
        ####################################################

        # 12
        """ project_data 349-362 auskommentieren
        datei muss schon vorhanden sein... weshalb... keine Ahnung
        ansonsten steht das grid auf dem kopf.
        # wb.cal_hydromorphiegrad()
        """

        named_query_dict = {
            197: wb.cal_precipitation,
            12: wb.cal_hydromorphiegrad,
            29: wb.cal_runoff_quotient,
            30: wb.cal_exposure_quotient,
            34: wb.cal_cn_value,
            336: wb.cal_humusoberboden,
            # 32: wb.cal_nfkwe,
            37: wb.cal_surface_runoff,
            41: wb.cal_rain_discharge,
            90: wb.cal_percolation_rate,
            36: wb.cal_drainage_rate,
            38: wb.cal_groundwater_runoff,
            39: wb.cal_interflow,
            40: wb.cal_sickerwasserrate,
            42: wb.cal_total_runoff,
            3: wb.cal_eta,
        }

        self.cal_function_pointer(named_query_dict)

        del wb

        ####################################################
        # ################ Water Balance ####################
        ####################################################
        ba = soil_erosion(self.data_config, self.data_param, self.data_area, self.data_level, self.data_nc)
        ####################################################

        named_query_dict = {
            73: ba.calc_cfactor,
            48: ba.calc_abag,
            43: ba.calc_er,
        }

        self.cal_function_pointer(named_query_dict)

        del ba

        ####################################################
        # ################ Sediment input ####################
        ####################################################
        se = sediment_input(self.data_config, self.data_param, self.data_area, self.data_level, self.data_nc)
        ####################################################

        named_query_dict = {
          # 5006: se.prepare_slope,
          # 5006: se.slope_radiant,
            52: se.cal_likeliness_connectivity,
            59: se.cal_chi,
            60: se.cal_sdr,
            53: se.cal_sediment_input,
        }

        self.cal_function_pointer(named_query_dict)

        del se

        ####################################################
        # ################ N budget ####################
        ####################################################
        nb = n_budget(self.data_config, self.data_param, self.data_area, self.data_level, self.data_nc)
        ####################################################

        named_query_dict = {
            95: nb.cal_bilanzsaldo_zf,
            240: nb.cal_n_siedlung_regenwasserkanal,
            239: nb.cal_n_siedlung_unversiegelt,
            104: nb.cal_nmin_austrag,
            105: nb.cal_cnmin_zgw,
            # 105: nb.cal_cnmin_zgw_max_50mg_l,
            103: nb.cal_nmin_zgw,
            106: nb.cal_nmin_r,
            111: nb.cal_nmin_ao,
            112: nb.cal_nmin_ag,
            # 234: nb.cal_nmin_ag_denitr,
            # 148: nb.cal_nmin_ag_denitr_proz,
            114: nb.cal_nmin_az,
            115: nb.cal_nmin_draen,
            116: nb.cal_nmin_a,
            113: nb.cal_cnmin_ag,
            117: nb.cal_npart,
            154: nb.cal_nges_austrag,
            118: nb.cal_nges,
        }

        self.cal_function_pointer(named_query_dict)

        del nb

        ####################################################
        # ################ P budget ####################
        ####################################################
        pb = p_budget(self.data_config, self.data_param, self.data_area, self.data_level,
                            self.data_nc)
        ####################################################

        named_query_dict = {
            68: pb.cal_p_ag,
            69: pb.cal_p_ao,
            70: pb.cal_p_az,
            71: pb.cal_p_draen,
            # 74: pb.cal_ppart,
            74: pb.cal_ppart_gruen,
            76: pb.cal_pgel,
            78: pb.cal_pges,
            160: pb.cal_p_siedung_ew_ohne_anschluss,
            241: pb.cal_p_siedlung_regenwasserkanal,
            242: pb.cal_p_siedlung_unversiegelt,
        }

        self.cal_function_pointer(named_query_dict)

        del pb

    def cal_function_pointer(self, named_query_dict):

        for d in self.data_config['id_param']:

            for n in named_query_dict:

                if d == n:
                    kw_args = self.project_data.get_param_data_from_param_id(d)
                    kw_args['id_area'] = self.data_config['id_area']
                    kw_args['id_area_data'] = self.data_config['id_area_data']
                    print("Starte STOFFBILANZ-Modellierung von " + kw_args['name'] + " ...")
                    function_pointer = named_query_dict.get(d, None)
                    # print('function_pointer', function_pointer)
                    function_pointer(**kw_args)
