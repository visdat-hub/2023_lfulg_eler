import os, sys
from osgeo import gdal, ogr

from gis_functions.gdal_raster_functions import gdal_raster_functions
from pg.pg import db_connector

class import_area:

    """
        Class for importing area data into the file system and DB
    """

    def __init__(self):
        print("class import_area")
        self.project = os.environ.get('STB_DATA_PROJECT')
        self.data_path = os.environ.get('STB_DATA_PATH')
        self.epsg = os.environ.get('STB_EPSG')
        self.id_level = os.environ.get('STB_LEVEL')

        self.db_password = os.environ.get('DB_PASSWORD')
        self.db_user = os.environ.get('DB_USER')
        self.db_port = os.environ.get('DB_PORT')
        self.db_name = os.environ.get('DB_NAME')
        self.db_host = os.environ.get('DB_HOST')

    def do_import(self, grid_config, data_config):

        """
            function for importing area data into the file system and DB


            Parameter:
                (dict) grid_level_config (data from /src/config/grid_level/grid_level.config)
            Parameter:
                (dict) data_config (data from config-file)

            Returns:
                None
        """

        print("--> start importing area")

        in_format = data_config["dataSource"]["inFormat"]

        # rasterize different data formats
        # rasterize a shapefile
        if in_format == "shp":
            # create area in db
            id_area = self.__create_area_in_db(data_config)

            # create geometries in database
            self.__create_area_data_0_in_db(data_config, id_area)

            self.__rasterize_pg(grid_config, data_config, id_area)


    def __create_area_in_db(self, data_config):

        """
             function to insert area data into DB (spatial.area)

            Parameter:
                (dict) data_config (data[create_area_in_db] from config-file)

            Returns:
                (int) iid_area of the created spatial area
        """


        # create area in pg_database
        # return an unique area identifier
        print("--> create area as a vector gis data in a PostgreSQL database")

        create_options = data_config["create_area_in_db"]
        table = "spatial.area"
        cols = 'area, description, de, eng, reihenfolge, idgistyp, srid, idlayer_level, aktiv'

        value_placeholder = '%(area)s, %(description)s, %(de)s, %(eng)s,  %(reihenfolge)s, %(idgistyp)s, ' \
                            '%(srid)s, %(idlayer_level)s, %(aktiv)s, %(srid)s'

        return_param = "idarea"

        values = {}
        for key in create_options["columns"]:
            print (key,  create_options["columns"][key])
            if create_options["columns"][key] == "":
                values[key] = None
            else:
                values[key] = create_options["columns"][key]

        pg = db_connector()
        pg.dbConnect()
        id_area = pg.tblInsert( table, cols,  value_placeholder,  values,  return_param )
        pg.dbClose()

        print('id_area', id_area)
        return id_area


    # insert area data into spatial_slave.area_data_0
    def __create_area_data_0_in_db(self,  data_config, id_area):

        """
            function to insert area data into DB
            (create area data in spatial_slave.area_data_0 and spatial_slave.area_geom_0)

            Parameter:
                (dict) data_config (data from config-file)
            parameter:
                (int) id_area

            Returns:
                None
        """

        print("--> create area data in table spatial_slave.area_data_0 for id_area... " + str(id_area))

        pg = db_connector()
        pg.dbConnect()

        # data source
        filename = data_config["dataSource"]["srcName"] + '.shp'
        path = data_config["dataSource"]["srcPath"]
        attributes2import = data_config["dataSource"]["attributes2import"]

        # postgis target
        # data table
        table_data = "spatial_slave.area_data_0"
        cols_data = "idlevel, idarea, area_data, description_text, description_int, de, eng"
        value_placeholder_data = "%(idlevel)s, %(idarea)s, %(area_data)s, %(description_text)s, %(description_int)s, %(de)s, %(eng)s"
        return_parameter_data = "idarea_data"
        # geom table
        table_geom = "spatial_slave.area_geom_0"
        cols_geom = "idarea_data, idlevel, the_geom"
        value_placeholder_geom = "%(idarea_data)s, %(idlevel)s, ST_GeometryFromText(%(the_geom)s, " + self.epsg + ")"
        # open shapefile
        print (path + filename)

        driver = ogr.GetDriverByName(str('ESRI Shapefile'))
        data_source = driver.Open(path + filename, 0)
        layer = data_source.GetLayer()
        print('--> layer : '+ str(layer))

        # iterate over features
        for feature in layer:
            print('--> feature : '+ str(feature))

            #import data and geom to database
            values_data = {"idlevel": 0, "idarea": id_area}

            for key in attributes2import:
                if attributes2import[key] == "":
                    values_data[key] = None
                else:
                    values_data[key] = feature.GetField(str(attributes2import[key]))

            values_data['idlevel'] = 0
            print('--> values_data : '+ str(values_data))
            id_area_data = pg.tblInsert(table_data, cols_data,  value_placeholder_data,  values_data,  return_parameter_data)

            print('--> id_area_data : '+ str(id_area_data))

            #import geom to database
            values_geom = {"idarea_data": id_area_data, "idlevel": 0,
                           "the_geom": feature.GetGeometryRef().ExportToWkt()}

            # geometry as wkt
            pg.tblInsert(table_geom, cols_geom,  value_placeholder_geom,  values_geom,  None )

        layer.ResetReading()
        # close db access
        pg.dbClose()

    def __rasterize_pg(self, grid_config, data_config, id_area):

        """
            function to rasterize area data

            Parameter:
                (dict) grid_level_config (data from /src/config/grid_level/grid_level.config)
            Parameter:
                (dict) data_config (data from config-file)
            Parameter:
                (int) id_area

            Returns:
                None
        """

        # burn PostgreSQL vector datasource values into a raster
        # resamplingMethod is majority
        print("--> rasterize vector area data from PostgreSQL database")

        data_area = data_config['rasterize']

        target_path = self.data_path + self.project + "/areas/" + str(id_area) + "/"
        target_file_name = str(id_area) + '_' + self.id_level + '.' + \
                         data_area['dtype'] + '.' + str(data_area['decimals']) + '.' + data_area['fileSuffix']
        print(target_file_name)

        r = gdal_raster_functions()
        gdal_co, gdal_co2 = r.setGDAL_createOptions(data_area['fileSuffix'])
        of = r.setGDAL_outFormat(data_area['fileSuffix'])
        tr = r.setGDAL_targetResolution(self.id_level, grid_config)
        te = r.setGDAL_targetExtent(self.id_level, grid_config)

        sql_string = "SELECT idarea_geom AS gid, a.idarea, a.idarea_data as id, a.area_data as name, " + \
                     "the_geom FROM spatial.area_data a INNER JOIN spatial.area_geom b " + \
                     "ON a.idlevel = b.idlevel AND a.idarea_data = b.idarea_data " + \
                     "WHERE a.idarea = " + str(id_area) + " AND a.idlevel = 0"

        src_pg = "host=" + self.db_host + " dbname=" + self.db_name + " user=" + self.db_user + " password=" \
                 + self.db_password + " port=" + str(self.db_port)

        # create path if not exists
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        print(target_path)

        arg_dict = {'a': 'id', 'co': gdal_co, 'of': of, 'ot': data_area['dtype'], 'a_nodata': data_area['nodata'],
                    'te': te, 'tr': tr, 'a_srs': self.epsg, 'sql': sql_string, 'src_pg': src_pg,
                    'src_format': data_config["dataSource"]["inFormat"], 'src_srs': self.epsg, 'dst_path': target_path,
                    'dst_filename': target_file_name, 'dst_srs': self.epsg}

        print('arg_dict',arg_dict)
        #sys.exit()

        # call gdal_raster_functions class
        r.rasterize_pg(arg_dict)
