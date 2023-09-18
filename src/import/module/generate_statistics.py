import os, sys
import h5py
import glob

from module.generate_statistics_basestats_v1 import generate_statistics_basestats_v1
from module.module_functions import module_functions


class generate_statistics(module_functions):

    """
        Class to generate the statistics for param files
    """

    def __init__(self):
        print("class generate_statistics")
        self.project = os.environ.get('STB_DATA_PROJECT')
        self.data_path = os.environ.get('STB_DATA_PATH')
        self.id_level = os.environ.get('STB_LEVEL')
        self.base_path = '/data/' + self.project + '/'
        self.error = False

    def check_statistic(self, data_config, data_scenario, data_parameter, data_area):

        """
            function to check the input data

            Parameter:
                (dict) data_config (data from config-file)
            Parameter:
                (dict) data_scenarios (data from /src/config/default/scenario.config)
            Parameter:
                (dict) data_parameter (data from /src/config/default/parameter.config)
            Parameter:
                (dict) data_area (data from /src/config/default/area.config)

            Returns:
                (bool) error (True or False)
        """

        #check the input data in json
        self.__check_statistic_json(data_config, data_scenario, data_parameter, data_area)

        if self.error:
            print('error process ends')
            return self.error
        else:
            print('check json ok !')

        # check the input data into the file system
        self.__check_statistic_file(data_config, data_scenario, data_parameter)

        if self.error:
            print('error process ends')
        else:
            print('check files system ok!')

        return self.error

    def __check_statistic_json(self, data_config, data_scenario, data_parameter, data_area):

        """
           function to check the input data in json

           Parameter:
               (dict) data_config (data from config-file)
           Parameter:
               (dict) data_scenarios (data from /src/config/default/scenario.config)
           Parameter:
               (dict) data_parameter (data from /src/config/default/parameter.config)
           Parameter:
               (dict) data_area (data from /src/config/default/area.config)

           Returns:
               (bool) error (True or False)
       """


        print("--> check statistic parameter")

        for id_param in data_config["statistics"]["id_param"]:

            # selection of the parameter data for the id_param
            data_param = self.get_param_data_from_param_id(data_parameter, id_param)

            if data_param['error']:
                self.error = True
                print(data_param['description'])

        for id_sc in data_config["statistics"]["id_scenario"]:

            # selection of the scenario data for the id_sc
            data_sc = self.get_scenario_data_from_sc_id(data_scenario, id_sc)

            if data_sc['error']:
                self.error = True
                print(data_sc['description'])

        for id_area in data_config["statistics"]["id_area"]:

            # selection of the area data for the id_area
            data_ar = self.get_area_data_from_area_id(data_area, id_area)

            if data_ar['error']:
                self.error = True
                print(data_ar['description'])

        pass

    def __check_statistic_file(self, data_config, data_scenario, data_parameter):

        """
           function to check the input data into the file system

           Parameter:
               (dict) data_config (data from config-file)
           Parameter:
               (dict) data_scenarios (data from /src/config/default/scenario.config)
           Parameter:
               (dict) data_parameter (data from /src/config/default/parameter.config)
           Parameter:
               (dict) data_area (data from /src/config/default/area.config)

           Returns:
               (bool) error (True or False)
       """

        for id_param in data_config["statistics"]["id_param"]:

            # selection of the parameter data for the id_param
            data_param = self.get_param_data_from_param_id(data_parameter, id_param)
            #print('data_param', data_param)

            for id_sc in data_config["statistics"]["id_scenario"]:

                #selection of the scenario data for the id_sc
                data_sc = self.get_scenario_data_from_sc_id(data_scenario, id_sc)
                #print('data_sc', data_sc)

                parameter_path = self.base_path + 'parameters/' + data_sc['model_scenario_name'] + '/' + \
                                        str(id_param) + '/' + data_sc['model_year']
                #print('parameter_path', parameter_path)

                check_file_name = str(data_param['id_param']) + '_' + str(data_sc['id_sc']) + \
                        '_' + str(self.id_level) + '.' + data_param['dtype'] + '.' + str(data_param['decimals']) + '.nc'
                #print('check_file_name', check_file_name)

                #print((glob.glob(parameter_path + '/*')))
                #print(len(glob.glob(parameter_path + '/*')))

                check = False
                for input_file in glob.glob(parameter_path + '/*'):

                    input_file_name = input_file.replace(parameter_path + '/', '')

                    if input_file_name == check_file_name:
                        print(input_file_name, check_file_name)
                        check = True

                if not check:
                    self.error = True
                    print ('Error: '+ parameter_path + '/' + check_file_name + ' not exists!')

        pass

    def do_statistics(self, data_config, data_scenario, data_parameter):

        """
          function to generate the statistics

           Parameter:
               (dict) data_config (data from config-file)
           Parameter:
               (dict) data_scenarios (data from /src/config/default/scenario.config)
           Parameter:
               (dict) data_parameter (data from /src/config/default/parameter.config)

           Returns:
               None
       """

        print("--> calculate statistics")

        data_statistics = data_config["statistics"]

        for id_param in data_statistics["id_param"]:

            # selection of the parameter data for the id_param
            data_param = self.get_param_data_from_param_id(data_parameter, id_param)
            print('data_param', data_param)

            for id_sc in data_statistics["id_scenario"]:

                # selection of the scenario data for the id_sc
                data_sc = self.get_scenario_data_from_sc_id(data_scenario, id_sc)
                print('data_sc', data_sc)


                for id_area in data_statistics['id_area']:

                    for group_by_category in data_statistics['groupbyCategory']:

                        id_category = data_statistics['id_category']

                        stat_type = 'stat_type'

                        current_config = {'stat_type': stat_type, 'id_scenario': data_sc['id_sc'],
                                          'id_param': data_param['id_param'], 'id_area': id_area,
                                          'id_category': id_category, 'groupbyCategory': group_by_category}

                        #print('--> current_config : ' + str(current_config))
                        config_param, config_category, config_area = self.check_files(current_config, data_sc)
                        #print('--> config_param : ' + str(config_param))
                        #print('--> config_category : ' + str(config_category))
                        #print('--> config_area : ' + str(config_area))

                        if config_param['h5py_file'] == -1:
                            print("loading parameter or param file failed")
                            break
                        if config_category['h5py_file'] == -1:
                            print("loading parameter or category file failed")
                            sys.exit()
                        if config_area['h5py_file'] == -1:
                            print("loading parameter or area file failed")
                            sys.exit()

                        if config_param['h5py_file'] != -1 and config_area['h5py_file'] != -1 and \
                                config_category['h5py_file'] != -1:

                            f_param_array = config_param['h5py_file'], str(config_param['decimals']), str(
                                config_param['fpath']), str(config_param['f_name']), str(config_param['d_type'])

                            f_category = config_category['h5py_file']

                            f_area_array = config_area['h5py_file'], str(config_area['decimals']), str(
                                config_area['fpath']), str(config_area['f_name']), id_area

                            #print('--> f_param_array : ' + str(f_param_array))
                            #print('--> f_category : ' + str(f_category))
                            #print('--> f_area_array : ' + str(f_area_array))

                            if group_by_category == 0:
                                f_category = -1

                            s = generate_statistics_basestats_v1()
                            s.run(f_param_array, f_category, f_area_array, 0, 'avg')
                            #sys.exit()

    def check_files(self, current_config, data_sc):

        """
           function for check files and get specific properties of the file (param, category, area)

           Parameter:
               (dict) current_config = {'stat_type':xx, 'id_scenario': xx, 'id_param':xx, 'id_area':xx,
               'id_category':xx, 'groupbyCategory':xx}
           Parameter:
               (dict) data_sc (selection of the scenario data for id_sc)

           Returns:
                (dict) f_param, f_category, f_area = {'f_file':xx, 'f_name':xx, 'fpath': xx, 'd_type':xx, 'fFormat':xx,
               'decimals':xx, 'idParm':xx, 'h5py_file':xx ,'fillValue':xx}
       """
        # print("check files")

        if current_config['id_param'] != "":

            f_param = self.check_param_file(data_sc, str(current_config['id_param']))
        else:
            print("missing parameter id")
            sys.exit()

        if current_config['id_category'] != "":
            f_category = self.check_category_file(data_sc, str(current_config['id_category']))
        else:
            print("missing category id")
            sys.exit()

        if current_config['id_area'] != "":
            f_area = self.check_area_file(str(current_config['id_area']))
        else:
            print("missing area id")
            sys.exit()

        return f_param, f_category, f_area

    def check_param_file(self, data_sc, id_param):

        """
           function for check parameter files and get specific properties of the file

           Parameter:
               (dict) data_sc (selection of the scenario data for id_sc)
           Parameter:
               (int) id_param

           Returns:
               (dict) config = {'f_file':xx, 'f_name':xx, 'fpath': xx, 'd_type':xx, 'fFormat':xx,
               'decimals':xx, 'idParm':xx, 'h5py_file':xx ,'fillValue':xx}
       """

        # print("check parameter file")

        config = {}
        id_scenario = str(data_sc['id_sc'])
        scenario_name = str(data_sc['model_scenario_name'])
        model_year = str(data_sc['model_year'])

        path = self.base_path + '/parameters/' + scenario_name + '/' + id_param + '/' + model_year + '/'
        f_name = id_param + '_' + id_scenario + '_' + self.id_level
        file = path + f_name
        print(file)

        if os.path.exists(path):
            for x in os.listdir(path):
                x_def = x.split('.')

                if len(x_def) == 4 and x_def[0] == f_name and x_def[1] != 'baseline':
                    data_type = x_def[1]
                    decimals = x_def[2]
                    file_format = x_def[3]
                    file = file + '.' + str(data_type) + '.' + str(decimals) + '.' + str(file_format)

                    config['f_file'] = str(file)
                    config['f_name'] = f_name
                    config['fpath'] = path
                    config['d_type'] = data_type
                    config['fFormat'] = file_format
                    config['decimals'] = decimals
                    config['idParm'] = id_param

            if os.path.isfile(file):
                f_param = h5py.File(file, 'r')
                config['h5py_file'] = f_param
                ds = f_param['Band1']
                config['fillValue'] = ds.attrs['_FillValue'][0]
                # print('--> parameter file found: ' + file)
            else:
                config['h5py_file'] = -1
                print('--> missing parameter file (h5 or nc): ' + file)
        else:
            config['h5py_file'] = -1
            print('--> parameter path not found: ' + str(path))

        return config

    def check_area_file(self, id_area):

        """
           function for check area files and get specific properties of the file

           Parameter:
               (int) id_area

           Returns:
               (dict) config = {'f_file':xx, 'f_name':xx, 'fpath': xx, 'd_type':xx, 'fFormat':xx,
               'decimals':xx, 'idParm':xx, 'h5py_file':xx ,'fillValue':xx}
       """

        # print("check area file")

        config = {}

        path = self.base_path + '/areas/' + id_area + '/'
        f_name = id_area + '_' + self.id_level
        file = path + f_name

        if os.path.exists(path):
            for x in os.listdir(path):
                x_def = x.split('.')
                if len(x_def) == 4 and x_def[0] == f_name:
                    data_type = x_def[1]
                    decimals = x_def[2]
                    file_format = x_def[3]
                    file = file + '.' + str(data_type) + '.' + str(decimals) + '.' + str(file_format)

                    config['f_file'] = file
                    config['f_name'] = f_name
                    config['fpath'] = path
                    config['d_type'] = data_type
                    config['fFormat'] = file_format
                    config['decimals'] = decimals
                    config['id_area'] = id_area

            if os.path.isfile(file):
                f_area = h5py.File(file, 'r')
                config['h5py_file'] = f_area
                ds = f_area['Band1']
                config['fillValue'] = ds.attrs['_FillValue'][0]
                # print('--> area file found: ' + file)
            else:
                config['h5py_file'] = -1
                print('--> missing area file (h5 or nc): ' + file)
        else:
            config['h5py_file'] = -1
            print('--> area path not found: ' + str(path))

        return config

    def check_category_file(self, data_sc, id_category):

        """
           function for category files (land_use) and get specific properties of the file

           Parameter:
               (int) id_category

           Returns:
               (dict) config = {'f_file':xx, 'f_name':xx, 'fpath': xx, 'd_type':xx, 'fFormat':xx,
               'decimals':xx, 'idParm':xx, 'h5py_file':xx ,'fillValue':xx}
       """

        # print("check category file")

        config = {}

        id_scenario = str(data_sc['id_sc'])
        scenario_name = str(data_sc['model_scenario_name'])
        model_year = str(data_sc['model_year'])

        path = self.base_path + '/parameters/' + scenario_name + '/' + id_category + '/' + model_year + '/'
        f_name = id_category + '_' + id_scenario + '_' + self.id_level
        file = path + f_name

        if os.path.exists(path):
            for x in os.listdir(path):
                x_def = x.split('.')
                if len(x_def) == 4 and x_def[0] == f_name:
                    data_type = x_def[1]
                    decimals = x_def[2]
                    file_format = x_def[3]
                    file = file + '.' + str(data_type) + '.' + str(decimals) + '.' + str(file_format)

                    config['f_file'] = file
                    config['f_name'] = f_name
                    config['fpath'] = path
                    config['d_type'] = data_type
                    config['fFormat'] = file_format
                    config['decimals'] = decimals
                    config['id_category'] = id_category

            if os.path.isfile(file):
                f_category = h5py.File(file, 'r')
                config['h5py_file'] = f_category
                ds = f_category['Band1']
                config['fillValue'] = ds.attrs['_FillValue'][0]
                # print('--> category file found: ' + file)
            else:
                config['h5py_file'] = -1
                print('--> missing category file (h5 or nc): ' + file)
        else:
            config['h5py_file'] = -1
            print('--> category path not found: ' + str(path))

        return config
