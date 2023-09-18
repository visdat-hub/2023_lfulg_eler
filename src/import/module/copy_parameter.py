import glob
import os, sys
import shutil
import subprocess

from pg.pg import db_connector
from module.module_functions import module_functions


class copy_parameter(module_functions):
    """
        Class to copy data from source scenario to target scenarios
    """

    def __init__(self):
        print("class import_parameter")
        self.project = os.environ.get('STB_DATA_PROJECT')
        self.data_path = os.environ.get('STB_DATA_PATH')
        self.id_level = os.environ.get('STB_LEVEL')
        self.base_path = '/data/' + self.project + '/'
        self.error = False

    def check_file_exists(self, source_path, check_file_name):

        """
            function to check file exists

            Parameter:
                source_path
            Parameter:
                check_file_name

            Returns:
                None  (set self.error in True or False)
        """

        # print((glob.glob(source_path + '/*')))
        # print(len(glob.glob(source_path + '/*')))

        check = False
        for input_file in glob.glob(source_path + '/*'):

            input_file_name = input_file.replace(source_path + '/', '')

            if input_file_name == check_file_name:
                # print(inputFileName, checkInputFileName)
                check = True

        if not check:
            print('Error: ' + source_path + '/' + check_file_name + ' not exists!')
            self.error = True

        pass

    def check_copy(self, data_config, data_scenarios, data_parameter):

        """
            function to check the source data

            Parameter:
                (dict) data_config (data from config-file)
            Parameter:
                (dict) data_scenarios (data from /src/config/default/scenario.config)
            Parameter:
                (dict) data_parameter (data from /src/config/default/parameter.config)

            Returns:
                (bool) error (True or False)
        """

        print("--> check copy parameter")

        for id_param in data_config["options"]["id_param"]:

            data_param = self.get_param_data_from_param_id(data_parameter, id_param)

            if data_param['error']:
                self.error = True
                print(data_param['description'])

        data_sc = self.get_scenario_data_from_sc_id(data_scenarios, data_config["options"]["source_id_sc"])

        if data_sc['error']:
            self.error = True
            print(data_sc['description'])

        for id_sc in data_config["options"]["target_id_sc"]:
            data_sc = self.get_scenario_data_from_sc_id(data_scenarios, id_sc)

            if data_sc['error']:
                self.error = True
                print(data_sc['description'])

        if self.error:
            return self.error

        source_id_sc = data_config["options"]["source_id_sc"]
        data_sc_source = self.get_scenario_data_from_sc_id(data_scenarios, source_id_sc)

        for id_param in data_config["options"]["id_param"]:

            source_path = self.base_path + 'parameters/' + data_sc_source['model_scenario_name'] + '/' + \
                          str(id_param) + '/' + data_sc_source['model_year']
            # print('source_path', source_path)

            data_param = self.get_param_data_from_param_id(data_parameter, id_param)
            # print('data_param', data_param)

            check_file_name = str(id_param) + '_' + str(source_id_sc) + '_' + str(self.id_level) + '.' + \
                              data_param['dtype'] + '.' + str(data_param['decimals']) + '.nc'
            #
            self.check_file_exists(source_path, check_file_name)

            if data_config['importStatistic'] == 1:
                #
                check_file_name = str(id_param) + '_' + str(source_id_sc) + '_' + str(self.id_level) + '.stats.h5'
                self.check_file_exists(source_path, check_file_name)

        if self.error:
            print('error process ends')
        else:
            print('check ok!')

        return self.error

    def do_copy(self, data_config, data_scenarios, data_parameter):

        """
            function to copy data from source scenario to target scenarios

            Parameter:
                (dict) data_config (data from config-file)
            Parameter:
                (dict) data_scenarios (data from /src/config/default/scenario.config)
            Parameter:
                (dict) data_parameter (data from /src/config/default/parameter.config)

            Returns:
                None
        """

        print("--> copy import")

        source_id_sc = data_config["options"]["source_id_sc"]
        data_sc_source = self.get_scenario_data_from_sc_id(data_scenarios, source_id_sc)

        for id_param in data_config["options"]["id_param"]:

            source_path = self.base_path + 'parameters/' + data_sc_source['model_scenario_name'] + '/' + \
                          str(id_param) + '/' + data_sc_source['model_year']
            # print('source_path', source_path)

            data_param = self.get_param_data_from_param_id(data_parameter, id_param)
            print('data_param', data_param)

            #
            source_file_nc = str(id_param) + '_' + str(source_id_sc) + '_' + str(self.id_level) + '.' + \
                             data_param['dtype'] + '.' + str(data_param['decimals']) + '.nc'

            source_file_h5 = str(id_param) + '_' + str(source_id_sc) + '_' + str(self.id_level) + '.stats.h5'

            for target_id_sc in data_config["options"]["target_id_sc"]:

                data_sc_target = self.get_scenario_data_from_sc_id(data_scenarios, target_id_sc)

                if data_sc_target['id_sc'] != data_sc_source['id_sc']:

                    target_path = self.base_path + 'parameters/' + data_sc_target['model_scenario_name'] + '/' + \
                                  str(id_param) + '/' + data_sc_target['model_year']

                    target_file_nc = str(id_param) + '_' + str(target_id_sc) + '_' + str(self.id_level) + '.' + \
                                     data_param['dtype'] + '.' + str(data_param['decimals']) + '.nc'

                    target_file_h5 = str(id_param) + '_' + str(target_id_sc) + '_' + str(self.id_level) + '.stats.h5'

                    if os.access(target_path, os.F_OK) is True:
                        shutil.rmtree(target_path)
                        os.makedirs(target_path)
                    else:
                        os.makedirs(target_path)

                    p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)

                    if data_config["symbolicLink"] == 0:
                        # copy import
                        shell_string = 'cp ' + source_path + '/' + source_file_nc + ' ' + target_path + \
                                       '/' + target_file_nc + ';'
                        # print('shell_string', shell_string)

                        if data_config['importStatistic'] == 1:
                            #
                            shell_string += 'cp ' + source_path + '/' + source_file_h5 + ' ' + target_path +\
                                            '/' + target_file_h5 + ';'
                            print('shell_string', shell_string)

                        p.communicate(shell_string.encode('utf8'))
                    else:
                        # create link
                        shell_string = 'ln -v ' + source_path + '/' + source_file_nc + ' ' + target_path + '/' + \
                                       target_file_nc + ';'
                        # print('shell_string', shell_string)

                        if data_config['importStatistic'] == 1:
                            #
                            shell_string += 'ln -v ' + source_path + '/' + source_file_h5 + ' ' + target_path + '/' + \
                                            target_file_h5 + ';'
                            print('shell_string', shell_string)

                        p.communicate(shell_string.encode('utf8'))

                    del p
        pass

    def insert_copy(self, data_config):

        """
            function to insert data into DB (data_viewer.param_area_exists)

            Parameter:
                (dict) data_config (data from config-file)

            Returns:
                None
        """

        print("--> insert into DB (viewer_data.param_area_exists")

        # in Datenbank anlegen zur Visualisierung im viewer
        pg = db_connector()
        pg.dbConnect()

        for id_sc in data_config["options"]["target_id_sc"]:
            # sql_txt = "SELECT * from general.sbvf_parameter_ifexits_insert(3," + str(target_id_sc) + ",'" + self.data_path + "');"
            sql_txt = "SELECT * from general.sbvf_parameter_ifexits_insert(3," + str(
                id_sc) + ",'/mnt/galfdaten/daten_stb/');"
            # print(sql_txt)
            ret_val, row_count = pg.tblSelect(sql_txt)
            print(ret_val, row_count)

        pg.dbClose()
