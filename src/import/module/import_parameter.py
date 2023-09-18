import os, sys
import math

from gis_functions.gdal_raster_functions import gdal_raster_functions
from gis_functions.gdal_vector_functions import gdal_vector_functions
from module.module_functions import module_functions


class import_parameter(module_functions):

    """
        Class for importing data into the file system and DB
    """

    def __init__(self):
        print("class import_parameter")
        self.project = os.environ.get('STB_DATA_PROJECT')
        self.data_path = os.environ.get('STB_DATA_PATH')
        self.epsg = os.environ.get('STB_EPSG')
        self.id_level = os.environ.get('STB_LEVEL')
        self.base_path = '/data/' + self.project + '/'

        self.db_password = os.environ.get('DB_PASSWORD')
        self.db_user = os.environ.get('DB_USER')
        self.db_port = os.environ.get('DB_PORT')
        self.db_name = os.environ.get('DB_NAME')
        self.db_host = os.environ.get('DB_HOST')


    def do_import(self, data_config, grid_level_config, data_scenarios, data_parameter):

        """
            function for importing data into the file system from *.shp, *.asc, *.nc, *.sdat and postgres data

            Parameter:
                (dict) data_config (data from config-file)
            Parameter:
                (dict) grid_level_config (data from /src/config/grid_level/grid_level.config)
            Parameter:
                (dict) data_scenarios (data from /src/config/default/scenario.config)
            Parameter:
                (dict) data_parameter (data from /src/config/default/parameter.config)

            Returns:
                (bool) error (True or False)
        """

        print("--> start importing parameter")
        data_source = data_config["dataSource"]
        id_sc = data_config["general"]['id_sc']
        id_param = data_config["general"]['id_param']

        # selection of the scenario data for id_sc
        data_sc = self.get_scenario_data_from_sc_id(data_scenarios, id_sc)
        # print('data_sc', data_sc)

        # selection of the parameter data for id_sc
        data_param = self.get_param_data_from_param_id(data_parameter, id_param)
        data_param['resampling_method'] = data_config["general"]['resamplingMethod']
        # print('data_param', data_param)

        # rasterize a shapefile
        if data_source["inFormat"] == "shp":
            self.rasterize_shape(grid_level_config, data_source, data_sc, data_param)

        # resample a *.asc ascii grid (ESRI grid exchange format)
        if data_source["inFormat"] in ["asc", "nc", "sdat"]:
            self.resample_grid(grid_level_config, data_source, data_sc, data_param)

        # rasterize postgres SQL datasource
        if data_source["inFormat"] == "PG":
            self.rasterize_pg(grid_level_config, data_source, data_sc, data_param)

    def rasterize_shape(self, grid_level_config, data_source, data_sc, data_param):

        """
            function for importing data into the file system from *.shp

            Parameter:
                (dict) grid_level_config (data from /src/config/grid_level/grid_level.config)
            Parameter:
                (dict) data_source (data[dataSource] from config-file)
            Parameter:
                (dict) data_sc (selection of the scenario data for id_sc)
            Parameter:
                (dict) data_param (selection of the parameter data for id_param)

            Returns:
                None
        """

        # burn shape values into a raster
        # resamplingMethod is majority
        print("--> rasterize shapefile")

        r = gdal_raster_functions()
        
        arg_dict = {}

        id_sc = data_sc['id_sc']
        id_param = data_param['id_param']

        target_path = self.base_path + 'parameters/' + data_sc['model_scenario_name'] + '/' \
               + str(id_param) + '/' + data_sc['model_year'] + '/'

        target_file_name = str(id_param) + '_' + str(id_sc) + '_' + str(self.id_level) + '.' + \
                         data_param['dtype'] + '.' + str(data_param['decimals']) + '.' + data_param['fileSuffix']

        gdal_co, gdal_co2 = r.setGDAL_createOptions(data_param['fileSuffix'])

        of = r.setGDAL_outFormat(data_param['fileSuffix'])
        tr = r.setGDAL_targetResolution(self.id_level, grid_level_config)
        te = r.setGDAL_targetExtent(self.id_level, grid_level_config)

        # create path if not exists
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        arg_dict['a'] = data_source['attribute2raster']
        arg_dict['co'] = gdal_co
        arg_dict['of'] = of
        arg_dict['ot'] = data_param['dtype']
        arg_dict['decimals'] = data_param['decimals']
        arg_dict['a_nodata'] = data_param['nodata']
        arg_dict['te'] = te
        arg_dict['tr'] = tr
        arg_dict['a_srs'] = str(self.epsg)
        arg_dict['src_path'] = data_source['srcPath']
        arg_dict['src_filename'] = data_source['srcName']
        arg_dict['src_format'] = data_source["inFormat"]
        arg_dict['src_srs'] = str(self.epsg)
        arg_dict['dst_path'] = target_path
        arg_dict['dst_filename'] = target_file_name
        arg_dict['dst_srs'] = str(self.epsg)

        r.rasterize_shape(arg_dict)

    def resample_grid(self, grid_level_config, data_source, data_sc, data_param):

        """
            function for importing data into the file system from *.asc, *.nc, *.sdat

            Parameter:
                (dict) grid_level_config (data from /src/config/grid_level/grid_level.config)
            Parameter:
                (dict) data_source (data[dataSource] from config-file)
            Parameter:
                (dict) data_sc (selection of the scenario data for id_sc)
            Parameter:
                (dict) data_param (selection of the parameter data for id_param)

            Returns:
                None
        """

        print("--> resample a grid")

        arg_dict = {}

        r = gdal_raster_functions()

        id_sc = data_sc['id_sc']
        id_param = data_param['id_param']
        src_path = data_source['srcPath']
        src_file_name = data_source['srcName']
        in_format = data_source['inFormat']

        # check inFile
        if os.path.isfile(src_path + src_file_name + '.' + in_format):
            print("source file: " + src_path + src_file_name + '.' + in_format)
        else:
            sys.exit('source file missing: ' + src_path + src_file_name + '.' + in_format)

        print("resampling method: " + data_param['resampling_method'])

        # loop through resampling levels and resample grids by means of gdalwarp
        target_path = self.base_path + 'parameters/' + data_sc['model_scenario_name'] + '/' + \
                      str(id_param) + '/' + data_sc['model_year'] + '/'

        target_file_name = str(id_param) + '_' + str(id_sc) + '_' + str(self.id_level) + '.' + \
                           data_param['dtype'] + '.' + str(data_param['decimals']) + '.' + data_param['fileSuffix']

        gdal_of = r.setGDAL_outFormat(data_param['fileSuffix'])
        gdal_co, gdal_co2 = r.setGDAL_createOptions(data_param['fileSuffix'])
        gdal_r = r.setGDAL_resamplingMethod(data_param['resampling_method'])
        gdal_tr = r.setGDAL_targetResolution(self.id_level, grid_level_config)
        gdal_te = r.setGDAL_targetExtent(self.id_level, grid_level_config)
        gdal_srcnodata = str(data_param['nodata'])
        gdal_dstnodata = str(data_param['nodata'])
        # gdal_ot = '-ot ' + out_format[1]

        # create path if not exists
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        print("grid level: " + str(self.id_level))
        print('target: ' + target_file_name)

        arg_dict['co'] = gdal_co
        arg_dict['co2'] = gdal_co2
        arg_dict['of'] = gdal_of
        arg_dict['ot'] = data_param['dtype']
        arg_dict['dst_nodata'] = gdal_dstnodata
        arg_dict['src_nodata'] = gdal_srcnodata
        arg_dict['te'] = gdal_te
        arg_dict['tr'] = gdal_tr
        arg_dict['a_srs'] = str(self.epsg)
        arg_dict['src_path'] = src_path
        arg_dict['src_filename'] = src_file_name
        arg_dict['src_format'] = in_format
        arg_dict['out_format'] = [data_param['fileSuffix'],data_param['dtype'],data_param['decimals']]
        arg_dict['src_srs'] = str(self.epsg)
        arg_dict['dst_path'] = target_path
        arg_dict['dst_filename'] = target_file_name
        arg_dict['dst_srs'] = str(self.epsg)
        arg_dict['resamplingMethod'] = gdal_r

        arg_dict['src_epsg'] = str(self.epsg)
        arg_dict['target_epsg'] = str(self.epsg)

        # print('arg_dict', arg_dict)
        # sys.exit()

        r.resample_grid(arg_dict)

    def rasterize_pg(self, grid_level_config, data_source, data_sc, data_param):

        """
            function for importing data into the file system from postgres data

            Parameter:
                (dict) grid_level_config (data from /src/config/grid_level/grid_level.config)
            Parameter:
                (dict) data_source (data[dataSource] from config-file)
            Parameter:
                (dict) data_sc (selection of the scenario data for id_sc)
            Parameter:
                (dict) data_param (selection of the parameter data for id_param)

            Returns:
                None
        """

        print("--> rasterize vector data from a PostgresSQL database table")

        r = gdal_raster_functions()

        arg_dict = {}

        id_sc = data_sc['id_sc']
        id_param = data_param['id_param']

        target_path = self.base_path + 'parameters/' + data_sc['model_scenario_name'] + '/' \
                      + str(id_param) + '/' + data_sc['model_year'] + '/'

        target_file_name = str(id_param) + '_' + str(id_sc) + '_' + str(self.id_level) + '.' + \
                           data_param['dtype'] + '.' + str(data_param['decimals']) + '.' + data_param['fileSuffix']


        gdal_co, gdal_co2 = r.setGDAL_createOptions(data_param['fileSuffix'])
        of = r.setGDAL_out_format(data_param['fileSuffix'])
        tr = r.setGDAL_targetResolution(self.id_level, grid_level_config)
        te = r.setGDAL_targetExtent(self.id_level, grid_level_config)

        multiplier = 1.0
        if int(data_param['decimals']) in [0, 1, 2, 3, 4, 5, 6]:  # maximal 6 decimals
            if data_param['dtype'] in ["int8", "int16", "int32", "int64"]:
                multiplier = math.pow(10, int(data_param['decimals']))

        sql_string = "SELECT (" + data_source['attribute2raster'] + " * " + str(multiplier) + ")::numeric as id, " + \
                     "the_geom FROM " + data_source['dbschema'] + "." + data_source['dbtable']

        src_pg = "host=" +  self.db_host + " dbname=" + self.db_name + " user=" + self.db_user + " password=" + \
                 self.db_password + " port=" + str(self.db_port )

        # create path if not exists
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        arg_dict['a'] = 'id'
        arg_dict['co'] = gdal_co
        arg_dict['of'] = of
        arg_dict['ot'] = data_param['dtype']
        arg_dict['a_nodata'] = data_param['nodata']
        arg_dict['te'] = te
        arg_dict['tr'] = tr
        arg_dict['a_srs'] = str(self.epsg)
        arg_dict['sql'] = sql_string
        arg_dict['src_pg'] = src_pg
        arg_dict['src_format'] = data_source['inFormat']
        arg_dict['src_srs'] = str(self.epsg)
        arg_dict['dst_path'] = target_path
        arg_dict['dst_filename'] = target_file_name
        arg_dict['dst_srs'] = str(self.epsg)

        # call gdal_raster_functions class
        r.rasterize_pg(arg_dict)

    def reproject_gisdata(self, config):

        """
            function to reproject gis data

            Parameter:
                (dict) config (data from config-file)

            Returns:
                None
        """

        print("--> reproject gis data")
        arg_dict = {}
        dst_filename = config['src_filename'] + '_epsg' + config['a_srs']
        arg_dict["src_file"] = config['src_path'] + config['src_filename'] + '.' + config['src_format']
        arg_dict["dst_file"] = config['src_path'] + dst_filename + '.' + config['src_format']
        arg_dict["s_srs"] = config['src_srs']
        arg_dict["t_srs"] = config['dst_srs']

        # print('-->:', arg_dict)

        v = gdal_vector_functions()
        if config['src_format'] == 'shp':
            v.reproject_vector_data(arg_dict)
        if config['src_format'] in ["asc", "nc", "sgrd"]:
            v.reproject_raster_data(arg_dict)
        return dst_filename
