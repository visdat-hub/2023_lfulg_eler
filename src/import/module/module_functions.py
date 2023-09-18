#import sys

class module_functions:

    def __init__(self):
        print('load module_functions')

    def get_scenario_data_from_sc_id(self, data_scenario, id_sc):

        """
           function for the selection of the scenario data for the id_sc

           Parameter:
               (dict) data_scenarios (data from /src/config/default/scenario.config)
           Parameter:
               (int) id_sc

           Returns:
               (dict) selection of the scenario data for the id_sc
       """

        for data_sc in data_scenario:

            if data_sc['id_sc'] == id_sc:
                res = data_sc
                res['error'] = False
                # print(data_sc)
                return res

        error = {"error": True, "description": "scenario with id_sc " + str(id_sc) + " does not exist."}
        return error

    def get_param_data_from_param_id(self, data_parameter, id_param):

        """
           function for the selection of the parameter data for the id_param

           Parameter:
               (dict) data_parameter (data from /src/config/default/parameter.config)
            Parameter:
                (int) id_param

           Returns:
               (dict) selection of the parameter data for the id_param
        """

        for data_param in data_parameter:

            if data_param['id_param'] == id_param:
                res = data_param
                res['error'] = False
                # print(data_param)
                return res

        error = {"error": True, "description": "parameter with id_param " + str(id_param) + " does not exist."}
        return error

    def get_area_data_from_area_id(self, data_areas, id_area):

        """
           function for the selection of the area data for the id_area

           Parameter:
               (dict) data_area (data from /src/config/default/area.config)
           Parameter:
                (int) id_area

           Returns:
               (dict) selection of the area data for the id_area
       """

        for data_area in data_areas:

            if data_area['id_area'] == id_area:
                res = data_area
                res['error'] = False
                # print(data_area)
                return res

        error = {"error": True, "description": "area with id_area " + str(id_area) + " does not exist."}
        return error