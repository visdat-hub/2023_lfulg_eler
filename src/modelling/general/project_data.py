# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
# import glob
import json
import subprocess
import h5py
import numpy

from pg.pg import db_connector

# # class call the server modul (include DB and Shell)
# @date  22.03.2023
#
# @author Mario Uhlig, Stephan Bürger <br>
#        VisDat geodatentechnologie GmbH <br>
#        01277 Dresden <br>
#        Am Ende 14 <br>
#        http://www.visdat.de <br>
#        info@visdat.de <br>
#
# Die Klasse ProjectData enthält Funktionen für das Schreiben, Konvertieren, Lesen etc. von Daten sowie den fachlichen
# Modulen zugeordnete Funktionen für deren Datenimport-


class project_data:

    # # Konstruktor.
    def __init__(self, data_config, data_param, data_area, data_level, data_nc):

        self.project = os.environ.get('STB_DATA_PROJECT')
        self.data_path = os.environ.get('STB_DATA_PATH')
        self.id_level = int(os.environ.get('STB_LEVEL'))
        self.epsg = os.environ.get('STB_EPSG')

        self.base_path = '/data/' + self.project + '/'
        self.base_path_area = "/data/" + str(self.project) + "/areas/"

        self.path_preprocessing_exec = os.environ.get('STB_PROC_IMPORT_PATH')

        self.id_sc = data_config['id_sc']
        self.year = data_config['model_year']

        self.sc_name = data_config['model_scenario_name']

        self.data_config = data_config
        self.data_param = data_param
        self.data_area = data_area

        for l in data_level:

            if l['levelId'] == self.id_level:
                self.minx = l['minx']
                self.miny = l['miny']
                self.maxx = l['maxx']
                self.maxy = l['maxy']
                self.cell_size = l['resolution']
                self.width = l['width']
                self.height = l['height']

        self.a_spatial_ref = data_nc['projection']
        self.a_inverse_flattening = data_nc['inverse_flattening']
        self.a_scale_factor_at_central_meridian = data_nc['scale_factor_at_central_meridian']
        self.a_false_easting = data_nc['false_easting']
        self.a_false_northing = data_nc['false_northing']
        self.a_semi_major_axis = data_nc['semi_major_axis']
        self.a_latitude_of_projection_origin = data_nc['latitude_of_projection_origin']
        self.a_GeoTransform = data_nc['GeoTransform']
        self.a_longitude_of_prime_meridian = data_nc['longitude_of_prime_meridian']
        self.a_grid_mapping_name = data_nc['grid_mapping_name']
        self.a_longitude_of_central_meridian = data_nc['longitude_of_central_meridian']

    def get_param_data_from_param_id(self, id_param):

        """
           function for the selection of the parameter data for the id_param

            Parameter:
                (int) id_param

           Returns:
               (dict) selection of the parameter data for the id_param
        """

        for data_param in self.data_param:

            if data_param['id_param'] == id_param:
                res = data_param
                res['error'] = False
                # print(data_param)
                return res

        error = {"error": True, "description": "parameter with id_param " + str(id_param) + " does not exist."}
        return error

    def get_area_data_from_area_id(self, id_area):

        """
           function for the selection of the area data for the id_area

            Parameter:
                (int) id_area

           Returns:
               (dict) selection of the area data for the id_area
        """

        for data_area in self.data_area:

            if data_area['id_area'] == id_area:
                res = data_area
                res['error'] = False
                # print(data_param)
                return res

        error = {"error": True, "description": "area with id_area " + str(id_area) + " does not exist."}
        return error

    def moduldata_from_txt(self, modul_configfile):

        """
            Funktion um JSON-Konfigurationsobjekte aus dem config Ordner zu holen

            Parameter:
                modul_configfile modul Konfigurationsbezeichnung,
                z.B. "file_modul_config": "./src/config/modelling/modul/water_balance.json"

            Returns:
                (text) JSON-Konfigurationsobjekt
        """

        if os.path.isfile(modul_configfile):
            print('Vorhandene Configdatei (Modul) laden ...')
            data = open(modul_configfile)

            json_data = json.load(data)

            data.close()
        else:
            json_data = []

        return json_data

    def __load_data_area(self, id_area, array_id_areadata, ):

        """
            Funktion um Area-Daten aus Filesystem zu holen

            Parameter:
                id_area (id der Raumebene (siehe /src/config/default/area.json))

            Returns:
                (numpy) 2 dimensional array
        """

        data_area = self.get_area_data_from_area_id(id_area)

        data_type = data_area['dtype']
        comma = data_area['decimals']
        suffix = data_area['fileSuffix']
        # no_data = data_area['nodata']
        name = data_area['name']

        # area holen - zuerst prüfen, ob eine numpy-binary Datei des Parameters und Szenarios vorhanden ist
        path = self.base_path_area + str(id_area) + '/'
        # print(path)

        file_name = str(id_area) + '_' + str(self.id_level) + '.' + str(data_type) + '.' + str(comma) + '.' + suffix
        # print(file_name)
        print(name, ' input_file--> ', path + file_name)

        if os.path.exists(path + file_name):
            f = h5py.File(path + file_name, 'r')
            return_array = numpy.array(f['Band1'][:])

            if return_array.shape[0] == self.height and return_array.shape[1] == self.width:
                # print(return_array.shape)

                # no_data_value setzen
                return_array = numpy.isin(return_array, array_id_areadata)

                # Kommastellen bei int erzeugen
                return_array = return_array / (10 ** int(comma))
                return return_array

            else:
                raise ValueError(
                    'Extent of ' + file_name + ' is unequal to width and height in config; height: '
                    + str(return_array.shape[0]) + ' -- ' + str(self.height) + ' width: ' + str(
                        return_array.shape[1]) + ' -- ' + ' ' + str(self.width))
        else:
            print('keine Daten im Area-Path ', path)
            sys.exit()

        del f
        del return_array

    def __load_data(self, id_param):

        """
            Funktion um Parameter-Daten aus Filesystem zu holen

            Parameter:
                id_param  (id des Parameters (siehe /src/config/default/parameter.json))

            Returns:
                (numpy) 2 dimensional array
        """

        data_param = self.get_param_data_from_param_id(id_param)

        id_param = data_param['id_param']
        data_type = data_param['dtype']
        comma = data_param['decimals']
        suffix = data_param['fileSuffix']
        no_data = data_param['nodata']
        name = data_param['name']

        path = self.base_path + '/parameters/' + self.sc_name + '/' + str(id_param) + '/' + str(self.year) + '/'
        # print (path)

        file_name = str(id_param) + '_' + str(self.id_sc) + '_' + str(self.id_level) + '.' \
                                          + str(data_type) + '.' + str(comma) + '.' + suffix
        # print(file_name)
        print(name, ' input_file--> ', path + file_name)

        if os.path.exists(path + file_name):

            f = h5py.File(path + file_name, 'r')
            return_array = numpy.array(f['Band1'][:])

            if return_array.shape[0] == self.height and return_array.shape[1] == self.width:
                # print(return_array.shape)

                # no_data_value setzen
                return_array = return_array.astype(numpy.float32)
                return_array = numpy.where(return_array == no_data, numpy.nan, return_array)

                # Kommastellen bei int erzeugen
                return_array = return_array / (10 ** int(comma))
                return return_array

            else:
                raise ValueError(
                    'Extent of ' + file_name + ' is unequal to width and height in config; height: '
                    + str(return_array.shape[0]) + ' -- ' + str(self.height) + ' width: ' + str(
                        return_array.shape[1]) + ' -- ' + ' ' + str(self.width))
                sys.exit()

        else:
            print('keine Daten im Parameter-Path ', path)
            sys.exit()

        del f
        del return_array

    def set_data(self, input_data_array, file_config, data_2_viewer):

        """
            Daten als numpy_binary in Filesystem schreiben
            (Falls im Filesystem schon vorhanden wird das numpy_binary gelöscht und durch das neue ersetzt)

            Parameter:
                input_data_array - numpy_array
            Parameter:
                id_param (id des Parameters (siehe /src/config/default/parameter.json))
            Parameter:
                target_file_name
            Parameter:
                data_2_viewer (true or false)

            Returns:
                None
        """

        id_param = file_config['id_param']
        data_type = file_config['dtype']
        comma = file_config['decimals']
        suffix = file_config['fileSuffix']

        file_config['target_file_name'] = str(id_param) + '_' + str(self.id_sc) + '_' + str(self.id_level) + '.' \
                           + str(data_type) + '.' + str(comma) + '.' + suffix

        file_config['target_path'] = self.base_path + '/parameters/' + self.sc_name + '/' + str(id_param) + '/' +\
                                     str(self.year) + '/'

        file_config['netcdf_file'] = file_config['target_path'] + "mod_" + str(file_config['target_file_name'])

        self.__model_2_data(input_data_array, file_config)

        if data_2_viewer is True:
            self.__data_2_viewer(file_config)
            self.__remove_netcdf_files(file_config)
            self.__statistic_viewer(file_config)
            self.__show_in_viewer(file_config)

    def __model_2_data(self, input_data_array, file_config):

        dtype = 'float32'
        no_data = file_config['nodata']
        netcdf_file = file_config['netcdf_file']
        target_path = file_config['target_path']

        # filesystem anlegen wenn noch nicht vorhanden
        if os.access(target_path, os.F_OK) is False:
            os.makedirs(target_path)

        input_data_array = input_data_array.astype(numpy.float32)
        input_data = numpy.where(numpy.isnan(input_data_array), no_data, input_data_array)
        input_data = input_data.astype(str(dtype))

        if os.path.isfile(netcdf_file):
            print('Vorhandene Datei löschen ...')
            os.remove(netcdf_file)

        print('Datei wird neu erstellt unter: ' + str(netcdf_file) + ' ...')
        print("-->save as netcdf4... " + netcdf_file)

        # create netcdf data by h5h5netcdf
        with h5py.File(file_config['netcdf_file'], 'w') as f:
            f.attrs['Conventions'] = 'CF-1.5'

            v = f.create_dataset('Band1', input_data.shape, dtype=str(dtype))
            v[:, :] = input_data
            v.attrs['grid_mapping'] = 'transverse_mercator'
            v.attrs['_FillValue'] = [no_data]  # numpy.array(no_data_value).astype(str(meta_data_typ))

            vx = f.create_dataset('x', data=numpy.linspace(self.minx, self.maxx, num=self.width))
            vx.attrs['units'] = 'm'

            vy = f.create_dataset('y', data=numpy.linspace(self.miny, self.maxy, num=self.height))
            vy.attrs['units'] = 'm'

            dt = h5py.special_dtype(vlen=str)
            vm = f.create_dataset('transverse_mercator', (), dtype=dt)
            vm.attrs['spatial_ref'] = self.a_spatial_ref
            vm.attrs['inverse_flattening'] = self.a_inverse_flattening
            vm.attrs['scale_factor_at_central_meridian'] = self.a_scale_factor_at_central_meridian
            vm.attrs['false_easting'] = self.a_false_easting
            vm.attrs['false_northing'] = self.a_false_northing
            vm.attrs['semi_major_axis'] = self.a_semi_major_axis
            vm.attrs['latitude_of_projection_origin'] = self.a_latitude_of_projection_origin
            vm.attrs['GeoTransform'] = self.a_GeoTransform
            vm.attrs['longitude_of_prime_meridian'] = self.a_longitude_of_prime_meridian
            vm.attrs['grid_mapping_name'] = self.a_grid_mapping_name
            vm.attrs['longitude_of_central_meridian'] = self.a_longitude_of_central_meridian

        f.close()

        del vy
        del vx
        del dt
        del vm
        del f
        del input_data
        del input_data_array

    def __data_2_viewer(self, file_config):

        """
            function to import the data into the viewer

            Parameter:
                target_file_name
            Parameter:
                id_param  (id des Parameters (siehe /src/config/default/parameter.json))

            Returns:
                None
        """

        id_param = file_config['id_param']
        target_file_name = file_config['target_file_name']
        target_path = file_config['target_path']

        conf_dict = {
            "process": "import_parameter",
            "general": {
                "id_sc": self.id_sc,
                "id_param": id_param,
                "resamplingMethod": "majority"
            },
            "dataSource": {
                "inFormat": "nc",
                "srcPath": target_path,
                "srcName": str('mod_'+target_file_name).replace('.nc', '')
            }
        }

        # write config files
        print("write config ...")
        print(conf_dict)

        config_path = '/src/config/processing/parameter/scenarios/' + str(self.id_sc)

        if os.access(config_path, os.F_OK) is False:
            os.makedirs(config_path)

        config_file = config_path + '/' + str(target_file_name) + '.config'
        # print(config_file)

        with open(config_file, 'w') as file:
            file.write(json.dumps(conf_dict))

        # print("run_preprocessing ...")
        # print(self.path_preprocessing_exec)
        # sys.exit()

        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)
        shell_string = 'python3 ./' + self.path_preprocessing_exec + '/main.py -p import_parameter -f ' + config_file
        print(shell_string)
        p.communicate(shell_string.encode('utf8'))
        del p

    def __remove_netcdf_files(self, file_config):

        """
            function to delete the netcdf file

            Parameter:
                netcdf_file

            Returns:
                None
        """

        netcdf_file = file_config['netcdf_file']

        os.remove(netcdf_file)

    def __statistic_viewer(self, file_config):

        """
            function to create the statistic data

            Parameter:
                id_param  (id des Parameters (siehe /src/config/default/parameter.json))

            Returns:
                None
        """

        id_param = file_config['id_param']

        pg = db_connector()
        pg.dbConnect()

        """
        sql_txt = 'SELECT idarea FROM spatial.area WHERE statistic = true AND idarea > 0 ORDER BY idarea'

        ret_val, row_count = pg.tblSelect(sql_txt)
        print(ret_val, row_count)

        id_area_array = []

        for row in ret_val:
            id_area_array.append(row[0])

        pg.dbClose()

        print('id_area_array', id_area_array)
        """

        conf_dict = {
            "process": "generate_statistics",
            "statistics": {
                "id_area": [1, 26],
                "id_scenario": [self.id_sc],
                "id_param": [id_param],
                "groupbyCategory": [0, 1],
                "id_category": 6
            }
        }

        config_path = '/src/config/processing/statistics/scenarios/' + str(self.id_sc) + '/'
        print(config_path)

        # prüfen, ob Pfad vorhanden - anlegen wenn noch nicht vorhanden
        if os.access(config_path, os.F_OK) is False:
            os.makedirs(config_path)

        # write config file
        print("write config ...")

        config_file = config_path + '/' + str(id_param) + '_' + str(self.id_sc) + '.config'

        with open(config_file, 'w') as file:
            file.write(json.dumps(conf_dict))

        print("run_preprocessing ...")

        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)

        shell_string = 'python3 ./' + self.path_preprocessing_exec + '/main.py -p generate_statistics -f ' + config_file
        print(shell_string)

        p.communicate(shell_string.encode('utf8'))
        del p

    def __show_in_viewer(self, file_config):

        """
            function to create an insert into DB

            Parameter:
                id_param  (id des Parameters (siehe /src/config/default/parameter.json))

            Returns:
                None
        """

        id_param = file_config['id_param']

        pg = db_connector()
        pg.dbConnect()

        sql_txt = "select * from general.sbvf_insert_param_area_exists(" + str(self.id_level) + "," \
                  + str(self.id_sc) + "," + str(id_param) + ",'/mnt/galfdaten/daten_stb/')"

        ret_val, row_count = pg.tblSelect(sql_txt)
        # print(ret_val, row_count)

        pg.dbClose()

    def get_data_waterbalance(self, function_name, kwargs):
        """
            Funktion um die input-daten für die Berechnung in der Klasse water_balance zu holen
            ruft im Wesentlichen self.__load_data auf

            Parameter:
                function_name: [text] z.B. 'surface_runoff_daily' - holt damit für die Funktion surface_runoff_daily die

            Returns:
                (array) input-array mit den notwendigen Daten (2 dimensional arrays) für die Berechnung
        """

        # Landnutzung und Area-Auswahl
        id_area = kwargs['id_area']
        id_area_data = kwargs['id_area_data']

        input_data = {'land_use': self.__load_data(6),
                      'model_area': self.__load_data_area(id_area, id_area_data)}

        if function_name == 'precipitation':

            input_data['rain_summer'] = self.__load_data(14)
            input_data['rain_winter'] = self.__load_data(15)

            return input_data

        if function_name == 'hydromorphiegrad':
            input_data['bodentyp'] = self.__load_data(11)

            return input_data

        if function_name == 'runoff_quotient':
            input_data['hydromorphiegrad'] = self.__load_data(12)
            slope_raw = self.__load_data(13)
            input_data['slope'] = numpy.where(slope_raw == 0, 0.000001, slope_raw)

            input_data['bodenartengruppe'] = self.__load_data(10)
            input_data['mq'] = self.__load_data(302)
            input_data['mnq'] = self.__load_data(301)
            input_data['fest_locker'] = self.__load_data(303)

            return input_data

        if function_name == 'exposure_quotient':
            slope_raw = self.__load_data(13)
            input_data['slope'] = numpy.where(slope_raw == 0, 0.000001, slope_raw)
            input_data['exposure'] = self.__load_data(7)

            return input_data

        if function_name == 'cn_value':
            input_data['bodenartengruppe'] = self.__load_data(10)
            input_data['dkbb'] = self.__load_data(25)
            input_data['dsaat'] = self.__load_data(520)
            input_data['pkbb'] = 0  # self.__load_data(157)

            return input_data

        if function_name == 'humusoberboden':
            input_data['bodenartengruppe'] = self.__load_data(10)
            input_data['bodentyp'] = self.__load_data(11)

            return input_data

        if function_name == 'nfkwe':
            # input_data['humusgehalt'] = self.__load_data(5)
            input_data['humusoberboden'] = self.__load_data(336)
            input_data['temp'] = self.__load_data(17)
            input_data['bodenartengruppe'] = self.__load_data(10)

            return input_data

        if function_name == 'draenflaeche':

            # input_data['bodentyp'] = self.__load_data(11)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)

            return input_data

        if function_name == 'surface_runoff':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)
            slope_raw = self.__load_data(13)
            input_data['slope'] = numpy.where(slope_raw == 0, 0.000001, slope_raw)
            input_data['regentage'] = self.__load_data(18)
            input_data['rain_summer'] = self.__load_data(14)
            input_data['rain_winter'] = self.__load_data(15)
            # input_data['hyd_connect'] = self.__load_data(28) #Flaeche_Hy_Anb
            input_data['cn_value'] = self.__load_data(34)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)

            return input_data

        if function_name == 'kr':
            input_data['bodenartengruppe'] = self.__load_data(10)
            input_data['bodentyp'] = self.__load_data(11)

            return input_data

        if function_name == 'ka_kli':
            input_data['etp'] = self.__load_data(16)
            input_data['rain_summer'] = self.__load_data(14)
            input_data['rain_winter'] = self.__load_data(15)
            input_data['nfkwe'] = self.__load_data(32)
            input_data['surface_runoff'] = self.__load_data(37)

            return input_data

        if function_name == 'ta':
            input_data['nfkwe'] = self.__load_data(32)

            return input_data

        if function_name == 'wv':

            input_data['rain_summer'] = self.__load_data(14)
            input_data['rain_winter'] = self.__load_data(15)
            input_data['nfkwe'] = self.__load_data(32)
            input_data['surface_runoff'] = self.__load_data(37)

            return input_data

        if function_name == 'wpf':
            input_data['nfkwe'] = self.__load_data(32)

            return input_data

        if function_name == 'percolation_rate_liebscher':

            input_data['rain_summer'] = self.__load_data(14)
            input_data['rain_winter'] = self.__load_data(15)
            input_data['surface_runoff'] = self.__load_data(37)

            return input_data

        if function_name == 'drainage_rate':
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)

            return input_data

        if function_name == 'percolation_rate_gras':
            input_data['etp'] = self.__load_data(16)
            input_data['bodentyp'] = self.__load_data(11)
            input_data['rain_summer'] = self.__load_data(14)
            input_data['rain_winter'] = self.__load_data(15)
            input_data['nfkwe'] = self.__load_data(32)
            input_data['surface_runoff'] = self.__load_data(37)

            return input_data

        if function_name == 'percolation_rate':

            # if self.project == 'sachsen_modell':
            input_data['qw'] = self.__load_data(1000)
            input_data['ww'] = self.__load_data(1001)
            input_data['wg'] = self.__load_data(1002)
            input_data['wr'] = self.__load_data(1003)
            input_data['sg'] = self.__load_data(1004)
            input_data['sm'] = self.__load_data(1005)
            input_data['km'] = self.__load_data(1006)
            input_data['oel'] = self.__load_data(1007)
            input_data['k'] = self.__load_data(1008)
            input_data['hf'] = self.__load_data(1009)
            input_data['sb'] = self.__load_data(1010)
            input_data['kl'] = self.__load_data(1011)
            input_data['fl'] = self.__load_data(1012)
            input_data['fg'] = self.__load_data(1013)
            input_data['th'] = self.__load_data(1014)
            input_data['td'] = self.__load_data(1015)
            input_data['eb'] = self.__load_data(1016)
            input_data['sp'] = self.__load_data(1017)
            input_data['ig'] = self.__load_data(1018)
            input_data['eg'] = self.__load_data(1019)
            input_data['brache'] = self.__load_data(1020)
            input_data['r'] = self.__load_data(1021)
            input_data['ik'] = self.__load_data(1022)
            input_data['tr'] = self.__load_data(1024)
            input_data['gp'] = self.__load_data(1025)
            input_data['kup'] = self.__load_data(1026)
            input_data['mi'] = self.__load_data(1027)

            input_data['nfkwe'] = self.__load_data(32)

            return input_data

        if function_name == 'groundwater_runoff':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)
            input_data['runoff_quotient'] = self.__load_data(29)
            input_data['exposure_quotient'] = self.__load_data(30)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['percolation_rate'] = self.__load_data(90)

            return input_data

        if function_name == 'interflow':
            input_data['runoff_quotient'] = self.__load_data(29)
            input_data['groundwater_runoff'] = self.__load_data(38)

            return input_data

        if function_name == 'sickerwasserrate':
            input_data['groundwater_runoff'] = self.__load_data(38)
            input_data['interflow'] = self.__load_data(39)

            return input_data

        if function_name == 'rain_discharge':
            slope_raw = self.__load_data(13)
            input_data['slope'] = numpy.where(slope_raw == 0, 0.000001, slope_raw)
            input_data['regentage'] = self.__load_data(18)
            input_data['rain_summer'] = self.__load_data(14)
            input_data['rain_winter'] = self.__load_data(15)
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)

            return input_data

        if function_name == 'total_runoff':
            input_data['drainage_rate'] = self.__load_data(36)
            input_data['groundwater_runoff'] = self.__load_data(38)
            input_data['interflow'] = self.__load_data(39)
            input_data['surface_runoff'] = self.__load_data(37)
            rain_discharge_raw = self.__load_data(41)
            input_data['rain_discharge'] = numpy.where(numpy.isnan(rain_discharge_raw), 0, rain_discharge_raw)
            return input_data

        if function_name == 'eta':

            input_data['rain_summer'] = self.__load_data(14)
            input_data['rain_winter'] = self.__load_data(15)
            input_data['total_runoff'] = self.__load_data(42)

            return input_data

    def get_data_soil_erosion(self, function_name, kwargs):
        """
            Funktion um die input-daten für die Berechnung in der Klasse sediment_input zu holen
            ruft im Wesentlichen self.__load_data auf

            Parameter:
                function_name: [text] z.B. 'surface_runoff_daily' - holt damit für die Funktion surface_runoff_daily die

            Returns:
                (array) input-array mit den notwendigen Daten (2 dimensional arrays) für die Berechnung
        """

        # Landnutzung und Area-Auswahl
        id_area = kwargs['id_area']
        id_area_data = kwargs['id_area_data']

        input_data = {'land_use': self.__load_data(6),
                      'model_area': self.__load_data_area(id_area, id_area_data)}

        if function_name == 'cfactor':

            input_data['qw'] = self.__load_data(1000)
            input_data['ww'] = self.__load_data(1001)
            input_data['wg'] = self.__load_data(1002)
            input_data['wr'] = self.__load_data(1003)
            input_data['sg'] = self.__load_data(1004)
            input_data['sm'] = self.__load_data(1005)
            input_data['km'] = self.__load_data(1006)
            input_data['oel'] = self.__load_data(1007)
            input_data['k'] = self.__load_data(1008)
            input_data['hf'] = self.__load_data(1009)
            input_data['sb'] = self.__load_data(1010)
            input_data['kl'] = self.__load_data(1011)
            input_data['fl'] = self.__load_data(1012)
            input_data['fg'] = self.__load_data(1013)
            input_data['th'] = self.__load_data(1014)
            input_data['td'] = self.__load_data(1015)
            input_data['eb'] = self.__load_data(1016)
            input_data['sp'] = self.__load_data(1017)
            input_data['ig'] = self.__load_data(1018)
            input_data['eg'] = self.__load_data(1019)
            input_data['brache'] = self.__load_data(1020)
            input_data['r'] = self.__load_data(1021)
            input_data['ik'] = self.__load_data(1022)
            input_data['tr'] = self.__load_data(1024)
            input_data['gp'] = self.__load_data(1025)
            input_data['kup'] = self.__load_data(1026)
            input_data['mi'] = self.__load_data(1027)

            input_data['cfaktor_eu'] = self.__load_data(5510)
            input_data['dkbb'] = self.__load_data(25) / 100.0
            input_data['dsaat'] = self.__load_data(520) / 100.0
            input_data['zf'] = self.__load_data(501) / 100.0
            input_data['cfactor_zf'] = self.__load_data(46)
            input_data['cfactor_kbb'] = self.__load_data(47)
            input_data['cfactor_dsaat'] = self.__load_data(304)

            return input_data

        if function_name == 'abag':
            input_data['kfactor'] = self.__load_data(26)
            input_data['rfactor'] = self.__load_data(44)
            input_data['lsfactor'] = self.__load_data(210)
            input_data['cfactor'] = self.__load_data(73)

            return input_data

        if function_name == 'er':
            input_data['abag'] = self.__load_data(48)

            return input_data

    def get_data_sediment_input(self, function_name, kwargs):

        """
            Funktion um die input-daten für die Berechnung in der Klasse soil_erosion zu holen
            ruft im Wesentlichen self.__load_data auf

            Parameter:
                function_name: [text] z.B. 'surface_runoff_daily' - holt damit für die Funktion surface_runoff_daily die

            Returns:
                (array) input-array mit den notwendigen Daten (2 dimensional arrays) für die Berechnung
        """

        # Landnutzung und Area-Auswahl
        id_area = kwargs['id_area']
        id_area_data = kwargs['id_area_data']

        input_data = {'land_use': self.__load_data(6),
                      'model_area': self.__load_data_area(id_area, id_area_data)}

        if function_name == 'slope_radiant':
            # slope_raw = self.__load_data(13)
            # input_data['slope'] = numpy.where(slope_raw == 0, 0.000001, slope_raw)
            input_data['slope'] = self.__load_data(13)

            return input_data

        if function_name == 'likeliness_connectivity':
            input_data['water_distance'] = self.__load_data(20)
            input_data['abag'] = self.__load_data(48)
            input_data['abag'] = input_data['abag'] / 1000.0
            input_data['surface_runoff'] = self.__load_data(37)

            return input_data

        if function_name == 'chi':
            input_data['cfactor'] = self.__load_data(73)

            return input_data

        if function_name == 'sdr':
            #  slope_raw = self.__load_data(13)
            # input_data['slope'] = numpy.where(slope_raw == 0, 0.000001, slope_raw)

            # input_data['slope'] = self.__load_data(13)
            input_data['chi_factor'] = self.__load_data(59)
            input_data['slope'] = self.__load_data(5006)
            input_data['water_distance'] = self.__load_data(20)
            input_data['connectivity'] = self.__load_data(52)

            return input_data

        if function_name == 'sediment_input':

            input_data['water_distance'] = self.__load_data(20)
            input_data['sdr'] = self.__load_data(60)
            input_data['abag'] = self.__load_data(48)
            input_data['abag'] = input_data['abag'] / 1000.0

            return input_data

    def get_data_p_budget(self, function_name, kwargs):

        """
            Funktion um die input-daten für die Berechnung in der Klasse p_budget zu holen
            ruft im Wesentlichen self.__load_data auf

            Parameter:
                function_name: [text] z.B. 'surface_runoff_daily' - holt damit für die Funktion surface_runoff_daily die

            Returns:
                (array) input-array mit den notwendigen Daten (2 dimensional arrays) für die Berechnung
        """

        # Landnutzung und Area-Auswahl
        id_area = kwargs['id_area']
        id_area_data = kwargs['id_area_data']

        input_data = {'land_use': self.__load_data(6),
                      'model_area': self.__load_data_area(id_area, id_area_data)}

        if function_name == 'p_siedung_ew_ohne_anschluss':
            input_data['p_ew_ohne_anschluss'] = self.__load_data(5501)

            return input_data

        if function_name == 'p_siedlung_regenwasserkanal':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0,
                                                          versiegelungsgrad_raw)

            return input_data

        if function_name == 'p_siedlung_unversiegelt':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0,
                                                          versiegelungsgrad_raw)

            return input_data

        if function_name == 'p_ag':
            input_data['cp_ag'] = self.__load_data(64)  # Konzentration im Basisabfluss
            input_data['groundwater_runoff'] = self.__load_data(38)

            return input_data

        if function_name == 'p_ao':
            input_data['cp_ao'] = self.__load_data(65)
            input_data['surface_runoff'] = self.__load_data(37)

            return input_data

        if function_name == 'p_az':
            input_data['cp_az'] = self.__load_data(66)
            input_data['interflow'] = self.__load_data(39)

            return input_data

        if function_name == 'p_draen':
            input_data['cp_drean'] = self.__load_data(67)
            input_data['drainage_rate'] = self.__load_data(36)

            return input_data

        if function_name == 'ppart_gruen':
            input_data['pt_boden'] = self.__load_data(21)
            input_data['sediment_input'] = self.__load_data(53)
            input_data['er'] = self.__load_data(43)
            input_data['gruenland'] = self.__load_data(521)/100.0

            return input_data

        if function_name == 'ppart':
            input_data['pt_boden'] = self.__load_data(21)
            input_data['sediment_input'] = self.__load_data(53)
            input_data['er'] = self.__load_data(43)

            return input_data

        if function_name == 'pgel':
            input_data['p_draen'] = self.__load_data(71)
            input_data['p_az'] = self.__load_data(70)
            input_data['p_ao'] = self.__load_data(69)
            input_data['p_ag'] = self.__load_data(68)

            return input_data

        if function_name == 'pges':
            input_data['ppart'] = self.__load_data(74)
            input_data['pgel'] = self.__load_data(76)
            input_data['p_siedlung_haus_o_kanal'] = self.__load_data(160)
            input_data['p_siedlung_buergermeister'] = 0  # self.__load_data(161)
            input_data['p_siedlung_regenwasserkanal'] = self.__load_data(241)
            input_data['p_unversiegelt'] = self.__load_data(242)

            return input_data

    def get_data_n_budget(self, function_name, kwargs):

        # Landnutzung und Area-Auswahl
        id_area = kwargs['id_area']
        id_area_data = kwargs['id_area_data']

        input_data = {'land_use': self.__load_data(6),
                      'model_area': self.__load_data_area(id_area, id_area_data)}

        if function_name == 'dnorg':
            input_data['dnorg'] = self.__load_data(5200)

        if function_name == 'dnmin':
            input_data['dnmin'] = self.__load_data(5201)

        if function_name == 'nfix':
            input_data['nfix'] = self.__load_data(5202)

        if function_name == 'nernte':
            input_data['nernte'] = self.__load_data(5203)

        if function_name == 'nsaat':
            input_data['nsaat'] = self.__load_data(5204)

        if function_name == 'n_flush':
            input_data['n_flush'] = self.__load_data(282)

        if function_name == 'n_som_saldo':
            input_data['n_som_saldo'] = self.__load_data(283)

        if function_name == 'n_atmos':
            input_data['lu'] = self.__load_data(1)
            input_data['natm_a'] = self.__load_data(5600) / 1000.0 * 14.0
            input_data['natm_cnf'] = self.__load_data(5601) / 1000.0 * 14.0
            input_data['natm_crp'] = self.__load_data(5602) / 1000.0 * 14.0
            input_data['natm_wat'] = self.__load_data(5603) / 1000.0 * 14.0
            input_data['natm_dec'] = self.__load_data(5604) / 1000.0 * 14.0
            input_data['natm_grs'] = self.__load_data(5605) / 1000.0 * 14.0
            input_data['natm_mix'] = self.__load_data(5606) / 1000.0 * 14.0
            input_data['natm_oth'] = self.__load_data(5607) / 1000.0 * 14.0
            input_data['natm_urb'] = self.__load_data(5609) / 1000.0 * 14.0

        if function_name == 'verwitterungsklasse':
            input_data['bodenartengruppe'] = self.__load_data(10)
            input_data['bodentyp'] = self.__load_data(11)

        if function_name == 'ertragsklasse':
            input_data['verwitterungsklasse'] = self.__load_data(88)
            input_data['temp'] = self.__load_data(17)
            input_data['oberflaechenabfluss'] = self.__load_data(37)
            input_data['korrgesamtabfluss'] = self.__load_data(42)

        if function_name == 'nnetto':
            input_data['ertragsklasse'] = self.__load_data(91)

        if function_name == 'bilanzsaldo':
            # input_data['feldbilanz'] = self.__load_data(5502)

            input_data['nfix'] = self.__load_data(84)
            input_data['dnmin'] = self.__load_data(81)
            input_data['nernte'] = self.__load_data(85)
            input_data['nsaat'] = self.__load_data(220)
            input_data['n_flush'] = self.__load_data(282)
            input_data['n_som_saldo'] = self.__load_data(283)

        if function_name == 'bilanzsaldo_zf':
            input_data['bilanzsaldo_preprocess'] = self.__load_data(9500)
            input_data['zwf_preprocess'] = self.__load_data(5010) / 100
            input_data['zwf'] = self.__load_data(501) / 100

        if function_name == 'bilanzsaldo_50mg_l':
            input_data['natmos'] = self.__load_data(22)
            input_data['k'] = self.__load_data(97)
            input_data['dmax'] = self.__load_data(98)
            input_data['nmin_austrag_50mg_l'] = self.__load_data(270)

        if function_name == 'immobi':
            input_data['dnorg'] = self.__load_data(23)
            input_data['faktor_imobil'] = self.__load_data(149)
            input_data['ngruen'] = self.__load_data(83)
            input_data['ngruen_abfuhr'] = self.__load_data(87)

        if function_name == 'mobi':
            input_data['dnorg'] = self.__load_data(23)
            input_data['faktor_mobil'] = self.__load_data(150)
            input_data['dngruen'] = self.__load_data(82)
            input_data['nnachlieferung'] = self.__load_data(86)

        if function_name == 'immobi_zwf':
            input_data['dnorg'] = self.__load_data(23)
            input_data['faktor_immobil'] = self.__load_data(149)
            input_data['nzwf'] = self.__load_data(119)
            input_data['ngruen'] = self.__load_data(83)
            input_data['ngruen_abfuhr'] = self.__load_data(87)

        if function_name == 'mobi_zwf':
            input_data['dngruen'] = self.__load_data(82)
            input_data['nnachlieferung'] = self.__load_data(82)
            input_data['faktor_mobil'] = self.__load_data(150)
            input_data['dnorg'] = self.__load_data(23)
            input_data['dngruen_zwf'] = self.__load_data(120)

        if function_name == 'mineral_netto':
            input_data['mobi_zwf'] = self.__load_data(143)
            input_data['immo_zwf'] = self.__load_data(142)

        if function_name == 'k':
            input_data['bodenartengruppe'] = self.__load_data(10)
            input_data['bodentyp'] = self.__load_data(11)
            input_data['ms_skellet'] = self.__load_data(24)

        if function_name == 'dmax':
            input_data['k'] = self.__load_data(97)

        if function_name == 'immobilisierungsrate':
            input_data['temp'] = self.__load_data(17)

        if function_name == 'ndenitr_50mg_l':
            input_data['natmos'] = self.__load_data(22)
            input_data['bilanzsaldo'] = self.__load_data(272)
            input_data['k'] = self.__load_data(97)
            input_data['dmax'] = self.__load_data(98)

        if function_name == 'ndenitr':
            input_data['hydromorphiegrad'] = self.__load_data(12)
            input_data['bodenartengruppe'] = self.__load_data(10)
            input_data['natmos'] = self.__load_data(22)
            input_data['nnetto'] = self.__load_data(80)
            input_data['bilanzsaldo'] = self.__load_data(95)
            input_data['k'] = self.__load_data(97)
            input_data['dmax'] = self.__load_data(98)
            input_data['immobilisierungsrate'] = self.__load_data(99)

        if function_name == 'n_saldo_agrum_minus_n_saldo_tol_st':
            input_data['n_saldo'] = self.__load_data(6000)
            input_data['n_saldo_tol'] = self.__load_data(6002)

        if function_name == 'n_saldo_agrum_minus_n_saldo_tol_agrum':
            input_data['n_saldo'] = self.__load_data(6000)
            input_data['n_saldo_tol'] = self.__load_data(6003)

        if function_name == 'n_saldo_stoffbilanz_minus_n_saldo_tol_agrum':
            input_data['n_saldo'] = self.__load_data(6001)
            input_data['n_saldo_tol'] = self.__load_data(6003)

        if function_name == 'n_saldo_stoffbilanz_minus_n_saldo_tol_st':
            input_data['n_saldo'] = self.__load_data(6001)
            input_data['n_saldo_tol'] = self.__load_data(6002)

        if function_name == 'bilanzsaldo_plus_natm':
            input_data['natmos'] = self.__load_data(22)
            input_data['bilanzsaldo'] = self.__load_data(95)

        if function_name == 'denitr_tolerierbar':
            input_data['bodentyp'] = self.__load_data(11)
            input_data['nmin_austrag_verl'] = self.__load_data(299)

        if function_name == 'nmin_tolerierbar':
            input_data['ndenitr_tolerierbar'] = self.__load_data(100)
            input_data['nmin_austrag_verl'] = self.__load_data(299)

        if function_name == 'n_siedung_ew_ohne_anschluss':
            input_data['n_ew_ohne_anschluss'] = self.__load_data(5500)

        if function_name == 'n_siedlung_regenwasserkanal':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)

        if function_name == 'n_siedlung_unversiegelt':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)
            input_data['natmos'] = self.__load_data(22)
            # input_data['bilanzsaldo'] = self.__load_data(95)
            input_data['ndenitr'] = self.__load_data(100)

        if function_name == 'nmin_ar':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)
            input_data['natmos'] = self.__load_data(22)

        if function_name == 'nmin_austrag_50mg_l':
            input_data['gesamtabfluss'] = self.__load_data(42)

        if function_name == 'nmin_austrag_max_50mg_l':
            input_data['gesamtabfluss'] = self.__load_data(42)
            input_data['nmin_austrag'] = self.__load_data(5800)

        if function_name == 'nmin_austrag_ah':
            input_data['austauschhaeufigkeit'] = self.__load_data(129)
            input_data['nmin_austrag_50mg_l'] = self.__load_data(270)

        if function_name == 'nmin_austrag':
            input_data['natmos'] = self.__load_data(22)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['nnetto'] = self.__load_data(80)
            input_data['bilanzsaldo'] = self.__load_data(95)
            input_data['immobilisierungsrate'] = self.__load_data(99)
            input_data['ndenitr'] = self.__load_data(100)
            input_data['n_siedlung_unversiegelt'] = self.__load_data(239)

        if function_name == 'cnmin_zgw':
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['oberflaechenabfluss'] = self.__load_data(37)
            input_data['basisabfluss'] = self.__load_data(38)
            input_data['zwischenabfluss'] = self.__load_data(39)
            input_data['nmin_austrag'] = self.__load_data(104)
            input_data['n_siedlung_unversiegelt'] = self.__load_data(239)

        if function_name == 'cnmin_zgw_max_50mg_l':
            input_data['nmin_austrag'] = self.__load_data(104)
            input_data['gesamtabfluss'] = self.__load_data(42)

        if function_name == 'nmin_zgw':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['oberflaechenabfluss'] = self.__load_data(37)
            input_data['basisabfluss'] = self.__load_data(38)
            input_data['zwischenabfluss'] = self.__load_data(39)
            input_data['nmin_austrag'] = self.__load_data(104)
            input_data['n_siedlung_unversiegelt'] = self.__load_data(239)

        if function_name == 'nmin_r':
            input_data['natmos'] = self.__load_data(22)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['bilanzsaldo'] = self.__load_data(95)
            input_data['ndenitr'] = self.__load_data(100)
            input_data['nmin_austrag'] = self.__load_data(104)

        if function_name == 'nmin_ao':
            input_data['natmos'] = self.__load_data(22)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['oberflaechenabfluss'] = self.__load_data(37)
            input_data['basisabfluss'] = self.__load_data(38)
            input_data['zwischenabfluss'] = self.__load_data(39)
            input_data['nmin_austrag'] = self.__load_data(104)

        if function_name == 'nmin_ag':
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['abflussquotient'] = self.__load_data(29)
            input_data['oberflaechenabfluss'] = self.__load_data(37)
            input_data['basisabfluss'] = self.__load_data(38)
            input_data['zwischenabfluss'] = self.__load_data(39)
            input_data['nmin_austrag'] = self.__load_data(104)

        if function_name == 'nmin_ag_denitr':
            input_data['nmin_ag_denitr'] = self.__load_data(5700)

        if function_name == 'nmin_ag_denitr_proz':
            input_data['nmin_ag'] = self.__load_data(112)
            input_data['nmin_ag_denitr'] = self.__load_data(234)

        if function_name == 'nmin_az':
            input_data['bodenartengruppe'] = self.__load_data(10)
            input_data['bodentyp'] = self.__load_data(11)
            versiegelungsgrad_raw = self.__load_data(8)
            input_data['versiegelungsgrad'] = numpy.where(numpy.isnan(versiegelungsgrad_raw), 0, versiegelungsgrad_raw)
            input_data['abflussquotient'] = self.__load_data(29)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['oberflaechenabfluss'] = self.__load_data(37)
            input_data['basisabfluss'] = self.__load_data(38)
            input_data['zwischenabfluss'] = self.__load_data(39)
            input_data['nmin_austrag'] = self.__load_data(104)

        if function_name == 'nmin_draen':
            input_data['natmos'] = self.__load_data(22)
            draenflaeche_raw = self.__load_data(35)
            input_data['draenflaeche'] = numpy.where(numpy.isnan(draenflaeche_raw), 0, draenflaeche_raw)
            input_data['nmin_austrag'] = self.__load_data(104)
            # input_data['bilanzsaldo'] = self.__load_data(95)
            # input_data['ndenitr'] = self.__load_data(100)

        if function_name == 'nmin_a':
            input_data['nmin_ao'] = self.__load_data(111)
            input_data['nmin_az'] = self.__load_data(114)
            input_data['nmin_draen'] = self.__load_data(115)
            input_data['nmin_ag_denitr'] = self.__load_data(234)

        if function_name == 'cnmin_ag':
            input_data['basisabfluss'] = self.__load_data(38)
            input_data['nmin_ag_denitr'] = self.__load_data(234)

        if function_name == 'npart':
            input_data['nt_boden'] = self.__load_data(96)
            input_data['sedimenteintrag'] = self.__load_data(53)

        if function_name == 'nges_austrag':
            input_data['nmin_austrag'] = self.__load_data(104)
            input_data['npart'] = self.__load_data(117)
            input_data['n_siedlung_haus_o_kanal'] = self.__load_data(158)
            # input_data['n_siedlung_unversiegelt'] = self.__load_data(239)
            input_data['n_siedlung_regenwasserkanal'] = self.__load_data(240)

        if function_name == 'nges':
            input_data['nmin_a'] = self.__load_data(116)
            input_data['npart'] = self.__load_data(117)
            input_data['n_siedlung_haus_o_kanal'] = self.__load_data(158)
            # input_data['n_siedlung_unversiegelt'] = self.__load_data(239)
            input_data['n_siedlung_regenwasserkanal'] = self.__load_data(240)

        return input_data
