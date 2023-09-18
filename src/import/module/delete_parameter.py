import os, sys
import subprocess

from pg.pg import db_connector
from module.module_functions import module_functions


class delete_parameter(module_functions):
    """
        Class to delete data in file system and DB
    """

    def __init__(self):
        print("class delete_parameter")
        self.project = os.environ.get('STB_DATA_PROJECT')
        self.data_path = os.environ.get('STB_DATA_PATH')
        self.id_level = os.environ.get('STB_LEVEL')
        self.base_path = '/data/' + self.project + '/'
        self.error = False

    def do_delete(self, data_config, data_scenarios):

        """
            function to delete data in file system

            Parameter:
                (dict) data_config (data from config-file)
            Parameter:
                (dict) data_parameter (data from /src/config/default/parameter.config)


            Returns:
                None
        """

        print("--> calculate statistics")

        for id_sc in data_config["options"]['id_sc']:

            data_sc = self.get_scenario_data_from_sc_id(data_scenarios, id_sc)

            for id_param in data_config["options"]['id_param']:
                path = self.base_path + 'parameters/' + data_sc['model_scenario_name'] + '/' + \
                       str(id_param) + '/' + data_sc['model_year'] + '/'
                # print('path', path)

                p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)

                # del directory
                shell_string = 'rm  -r ' + path + ';'
                print(shell_string)

                p.communicate(shell_string.encode('utf8'))
                del p

    def do_delete_db(self, data_config):

        """
            function to delete data in DB (viewer_data.param_area_exists)

            Parameter:
                (dict) data_config (data from config-file)

            Returns:
                None
        """

        print("--> calculate statistics DB")

        pg = db_connector()

        for id_sc in data_config["options"]['id_sc']:

            for id_param in data_config["options"]['id_param']:
                pg.dbConnect()
                pg.tblDeleteRows('viewer_data.param_area_exists', 'idparam = ' + str(id_param) +
                                 ' and idsz = ' + str(id_sc) + ' and idlevel = ' + str(self.id_level))
                pg.dbClose()
