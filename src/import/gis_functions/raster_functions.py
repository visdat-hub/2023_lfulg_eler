import sys, os, subprocess


class raster_functions:
    def __init__(self):
        print("class raster_functions")

    def rasterize_shape(self, arg_dict):
        print("rasterize shapefile")
        print(arg_dict)
        if os.path.isfile(arg_dict['shapefile_path'] + ".shp"):
            print("shapefile to rasterize: " + arg_dict['shapefile_path'] + ".shp")
            x_min, y_min, x_max, y_max = arg_dict['model_extent']
            p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)

            saga_string = 'saga_cmd grid_gridding "Shapes to Grid" ' +\
                '-INPUT='+str(arg_dict['shapefile_path'])+'.shp ' +\
                '-FIELD='+str(arg_dict['attribute2raster'])+' '+\
                '-USER_GRID=' + arg_dict['output_raster_path'] + ' '+\
                '-USER_FIT=0 -MULTIPLE=3 -POLY_TYPE=1 -USER_SIZE=' + str(arg_dict['pixel_size']) + ' '+\
                '-USER_XMIN=' + str(x_min + arg_dict['pixel_size']/2) + ' '+\
                '-USER_XMAX=' + str(x_max + arg_dict['pixel_size']/2) + ' '+\
                '-USER_YMIN=' + str(y_min + arg_dict['pixel_size']/2) + ' '+\
                '-USER_YMAX=' + str(y_max + arg_dict['pixel_size']/2) + ' '+\
                '-GRID_TYPE=4'

            print(saga_string)
            p.communicate(saga_string.encode('utf8'))[0]
            del p
        else:
            sys.exit("cannot find shapefile:" + arg_dict['shapefile_path'] + ".shp")

    def generate_grid_index(self, arg_dict):
        print("generate grid index (unique id for each grid cell)")
        print(arg_dict)

        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)

        saga_string = 'saga_cmd grid_tools 21 ' +\
            '-GRID=' + str(arg_dict['raster_path']) + '.sgrd ' +\
            '-INDEX=' + str(arg_dict['raster_path']) + '.sgrd ' +\
            '-ORDER=' + str(arg_dict['sorting_order'])

        print(saga_string)
        p.communicate(saga_string.encode('utf8'))[0]
        del p

    def resample_grid(self, arg_dict):
        print("resample a grid")
        print(arg_dict)

        x_min, y_min, x_max, y_max = arg_dict['model_extent']

        p = subprocess.Popen('/bin/bash', shell=True, stdin=subprocess.PIPE)

        saga_string = 'saga_cmd grid_tools 0 ' +\
            '-INPUT=' + str(arg_dict['input']) + '.sgrd ' +\
            '-USER_GRID=' + str(arg_dict['user_grid']) + '.sgrd ' +\
            '-KEEP_TYPE -' +\
            arg_dict['scale_method'] + '='+str(arg_dict['resampling_method']) + ' ' +\
            '-USER_FIT=' + str(arg_dict['user_fit']) + ' ' +\
            '-USER_SIZE=' + str(arg_dict['pixel_size']) + ' '+\
            '-USER_XMIN=' + str(x_min + arg_dict['pixel_size']/2) + ' '+\
            '-USER_XMAX=' + str(x_max + arg_dict['pixel_size']/2) + ' '+\
            '-USER_YMIN=' + str(y_min + arg_dict['pixel_size']/2) + ' '+\
            '-USER_YMAX=' + str(y_max + arg_dict['pixel_size']/2)

        print(saga_string)
        p.communicate(saga_string.encode('utf8'))[0]
        del p
