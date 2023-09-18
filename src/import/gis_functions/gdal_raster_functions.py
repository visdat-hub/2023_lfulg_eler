import sys, os
import subprocess
import math

class gdal_raster_functions:

    def __init__(self):
        print("class gdal_raster_functions")

    # gdal_rasterize [-b band]* [-i] [-at]
    # {[-burn value]* | [-a attribute_name] | [-3d]} [-add]
    # [-l layername]* [-where expression] [-sql select_statement]
    # [-dialect dialect] [-of format] [-a_srs srs_def] [-to NAME=VALUE]*
    # [-co "NAME=VALUE"]* [-a_nodata value] [-init value]*
    # [-te xmin ymin xmax ymax] [-tr xres yres] [-tap] [-ts width height]
    # [-ot {Byte/Int16/UInt16/UInt32/Int32/Float32/Float64/CInt16/CInt32/CFloat32/CFloat64}] [-q]
    # <src_datasource> <dst_filename>
    def rasterize_shape(self, arg_dict):
        # resampling_method is majority
        print("rasterize shapefile")
        sql = -1
        co = ''
        # print(arg_dict)
        # test for decimals
        if arg_dict['ot'] in ['int8', 'int16', 'int32', 'int64']:
            if int(arg_dict['decimals']) in [1, 2, 3, 4, 5, 6]:
                multiplier = math.pow(10, int(arg_dict['decimals']))
                sql = "'SELECT CAST(\"" + str(arg_dict['a']) + "\" AS INTEGER) * " + str(int(multiplier)) \
                     + " AS \"" + arg_dict['a'] + "\" FROM " + arg_dict['src_filename'] + "' "

                sql = "'SELECT CAST((\"" + str(arg_dict['a']) + "\" * " + str(int(multiplier)) + ") AS INTEGER) AS \"" + \
                      arg_dict['a'] + "\" FROM " + arg_dict['src_filename'] + "' "


                print(sql)

        if 'co' in arg_dict:
            co = arg_dict['co']

        gdal_string = 'gdal_rasterize -a ' + arg_dict['a'] + ' ' + \
                      '-of ' + arg_dict['of'] + ' ' + \
                      co + ' ' + \
                      '-a_nodata ' + str(arg_dict['a_nodata']) + ' ' + \
                      arg_dict['te'] + ' ' + \
                      arg_dict['tr'] + ' ' + \
                      '-ot ' + arg_dict['ot'] + ' '
        if sql != -1:
            gdal_string = gdal_string + '-sql ' + sql
        gdal_string = gdal_string + arg_dict['src_path'] + arg_dict['src_filename'] + '.' + arg_dict['src_format'] + ' ' \
                      + arg_dict['dst_path'] + arg_dict['dst_filename']
        print(gdal_string)
        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)
        p.communicate(gdal_string.encode('utf8'))
        del p

    def resample_grid(self, arg_dict):
        print("resample a grid")
        print(arg_dict)
        # command line processes
        if 'subprocess' in sys.modules:
            # resample data
            shell_string = 'gdalwarp -of ' + arg_dict['of'] + ' -s_srs EPSG:' + arg_dict['src_epsg'] + ' -t_srs EPSG:' + \
                          arg_dict['target_epsg'] + ' ' + arg_dict['co'] + ' ' + arg_dict['resamplingMethod'] + \
                           ' ' + arg_dict['tr'] + ' ' + arg_dict['te'] + ' -srcnodata ' + \
                          arg_dict['src_nodata'] + ' -dstnodata ' + arg_dict['dst_nodata'] + ' -overwrite ' + \
                          arg_dict['src_path'] + arg_dict['src_filename'] + '.' + arg_dict['src_format'] + ' ' + \
                          arg_dict['dst_path'] + 'gdalwarp_' + arg_dict['dst_filename']

            print('shell-command --> ', shell_string)
            # sys.exit()

            p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)
            p.communicate(shell_string.encode('utf8'))
            del p

            # set decimals and outFormat to int
            # "outFormat" : [0 : "fileSuffix", 1 : "dtype", 2 : "decimals"]
            if int(arg_dict['out_format'][2]) in [0, 1, 2, 3, 4, 5, 6]:  # maximal 6 decimals
                if arg_dict['out_format'][1] in ["byte", "int8", "int16", "int32", "int64"]:
                    multiplier = math.pow(10, int(arg_dict['out_format'][2]))
                    shell_string = 'gdal_calc.py -A ' + \
                                  arg_dict['dst_path'] + 'gdalwarp_' + arg_dict['dst_filename'] + ' ' + \
                                  '--outfile=' + arg_dict['dst_path'] + arg_dict['dst_filename'] + ' --overwrite ' + \
                                  '--calc="A*' + str(multiplier) + '" --NoDataValue=' + str(arg_dict['dst_nodata']) \
                                  + ' ' + '--format=' + arg_dict['of'] + ' ' + \
                                  '--type=' + arg_dict['out_format'][1] + ' ' + arg_dict['co2']

                    print('shell-command --> ', shell_string)
                    p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)
                    p.communicate(shell_string.encode('utf8'))
                    del p

                    #
                    os.remove(arg_dict['dst_path'] + 'gdalwarp_' + arg_dict['dst_filename'])

    def rasterize_pg(self, arg_dict):
        print("rasterize a pg datasource (PostgreSQL database table)")
        # print arg_dict
        co = ''
        ot = ''
        if 'co' in arg_dict:
            co = arg_dict['co']
        if 'ot' in arg_dict:
            ot = '-ot ' + arg_dict['ot']

        gdal_string = 'gdal_rasterize -a ' + arg_dict['a'] + ' ' + \
                      '-sql "' + arg_dict['sql'] + '" ' + \
                      '-of ' + arg_dict['of'] + ' ' + \
                      co + ' ' + \
                      '-a_nodata ' + str(arg_dict['a_nodata']) + ' ' + \
                      arg_dict['te'] + ' ' + \
                      arg_dict['tr'] + ' ' + \
                      ot + ' ' + \
                      'PG:"' + arg_dict['src_pg'] + '" ' + \
                      str(arg_dict['dst_path']) + str(arg_dict['dst_filename'])
        print(gdal_string)
        # sys.exit()
        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)
        p.communicate(gdal_string.encode('utf8'))
        del p

    def gdal_translate(self, arg_dict):
        print("gdal_translate")
        print(arg_dict)
        gdal_string = 'gdal_translate ' + \
                      '-of ' + arg_dict['of'] + ' ' + \
                      arg_dict['co'] + ' ' + \
                      '-r ' + arg_dict['r'] + ' ' + \
                      arg_dict['srcFile'] + ' ' + arg_dict['dstFile']
        print(gdal_string)
        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)
        p.communicate(gdal_string.encode('utf8'))
        del p

    def setGDAL_createOptions(self, outFormat):
        co = None
        if outFormat == "nc":
            co = '-co "COMPRESS=DEFLATE" -co "ZLEVEL=9" -co "FORMAT=NC4"'
            co2 = '--co "COMPRESS=DEFLATE" --co "ZLEVEL=9" --co "FORMAT=NC4"'
        return co, co2

    def setGDAL_outFormat(self, outFormat):
        of = None
        if outFormat == "nc":
            of = 'netCDF'
        return of

    def setGDAL_targetResolution(self, id_layer, grid_level_config):
        tr = None
        for item in grid_level_config:
            if int(item['levelId']) == int(id_layer):
                tr = '-tr ' + str(item['resolution']) + ' ' + str(item['resolution'])
        return tr

    def setGDAL_targetExtent(self, id_layer, grid_level_config):
        te = None
        for item in grid_level_config:
            if int(item['levelId']) == int(id_layer):
                te = '-te ' + str(item['minx']) + ' ' + str(item['miny']) + ' ' + \
                     str(item['maxx']) + ' ' + str(item['maxy'])
        return te

    def setGDAL_resamplingMethod(self, resampling_method):
        r = None
        if resampling_method == "mean":
            r = '-r average'
        if resampling_method == "majority":
            r = '-r mode'
        if resampling_method == "median":
            r = '-r med'
        if resampling_method == "min":
            r = '-r min'
        if resampling_method == "max":
            r = '-r max'
        if resampling_method == "bilinear":
            r = '-r bilinear'
        if resampling_method == "near":
            r = '-r near'
        return r

    def reproject_raster_data(self, arg_dict):
        print("reproject raster data")
        sys.exit("!! todo")

    # gdal_fillnodata.py [-q] [-md max_distance] [-si smooth_iterations]
    # [-o name=value] [-b band]
    # srcfile [-nomask] [-mask filename] [-of format] [dstfile]
    def fillNoData(self, arg_dict):
        print("gdal_fillnodata function")
        md = ''

        if 'maxDistance' in arg_dict:
            if int(arg_dict['maxDistance']) > 0:
                md = '-md ' + str(arg_dict['maxDistance'])

        gdal_string = 'gdal_fillnodata.py ' + md + ' ' + \
                      arg_dict['srcFile'] + ' -of ' + arg_dict['of'] + ' ' + arg_dict['co'] + ' ' + arg_dict['dstFile']

        print(gdal_string)
        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)
        p.communicate(gdal_string.encode('utf8'))
        del p
