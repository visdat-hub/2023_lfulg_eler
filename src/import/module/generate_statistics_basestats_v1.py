# class base do_statistics
import math
import os
import h5py
import numpy as np
import pandas as pd


class generate_statistics_basestats_v1:
    def __init__(self):
        print("class generate_statistics_basestats_v1")

    def run(self, f_param_array, f_category, f_area_array, total_region, stat):
        print("------------------------------")
        print("run base statistic calculation")
        # f_param[0] is pointer to h5 data, f_param[1] -> decimals, f_param[2] -> dataType
        result = None

        # without area subclasses
        if total_region == 1:
            print("area subclasses: no")
            # without category subclasses ==> false
            if f_category == -1:
                print("category subclasses: no")
                self.run_a0_c0(f_param_array, f_area_array)

            # with category subclasses
            if f_category != -1:
                print("category subclasses: yes")
                self.run_a0_c1(f_param_array, f_area_array, f_category)

        # with area subclasses ==> true
        if total_region == 0:
            print("area subclasses: yes")
            # without category subclasses
            if f_category == -1:
                print("category subclasses: no")
                self.run_a1_c0(f_param_array, f_area_array, stat)

            # with category subclasses
            if f_category != -1:
                print("category subclasses: yes")
                self.run_a1_c1(f_param_array, f_area_array, f_category)
        print("------------------------------")
        return result, total_region

    # area subclasses == false (total_region = 1), category subclasses == false
    def run_a0_c0(self, f_param_array, f_area_array):

        #my_datatype = None
        rows = []
        decimal_divider = self.check_decimals(f_param_array)

        print('--> f_param_array: ' + str(f_param_array))
        print('--> f_area_array: ' + str(f_area_array))
        print('--> decimal_divider: ' + str(decimal_divider))

        # dataType = f_param_array[2]
        f_param = f_param_array[0]
        param_band1 = f_param['Band1']
        f_area = f_area_array[0]
        area_band1 = f_area['Band1']
        no_data_param = param_band1.attrs['_FillValue']
        no_data_area = area_band1.attrs['_FillValue']
        np_param = np.array(param_band1).astype(float)
        np_area = np.array(f_area['Band1']).astype(float)

        np_param[np_param == no_data_param] = np.nan
        np_area[np_area == no_data_area] = np.nan

        np_ar = np.stack((np_area, np_param))
        np_ar = np.where(np.isnan(np_ar[0]) == False, np_ar[1], np.nan)

        df = pd.DataFrame({'value': np_ar.flatten()})
        df_stat = df['value'].agg(['count', 'mean', 'min', 'max', 'std', 'median', 'sum']).reset_index()
        df_stat['value'] = df_stat['value'] / decimal_divider

        data = np.array([df_stat['index'], df_stat['value']])

        rows.append((data[1][0], (data[1][1]), (data[1][2]), (data[1][3]), (data[1][4]), (data[1][5]), (data[1][6])))

        my_datatype = np.dtype(
            [('count', np.int32), ('mean', np.float), ('min', np.float), ('max', np.float), ('std', np.float),
             ('median', np.float), ('sum', np.float)])

        result = rows, my_datatype, 'base_statistic'

        # write data to h5 file
        if len(result[0][0]) > 0:
            self.write_statistics2h5(f_param_array, f_area_array, result)
        else:
            print("WARNING -> length of result: 0")

    # area subclasses == false (total_region = 1), category subclasses == true
    def run_a0_c1(self, f_param_array, f_area_array, f_category):

        #my_datatype, id_category = None, None

        rows = []
        decimal_divider = self.check_decimals(f_param_array)

        print('--> f_param_array: ' + str(f_param_array))
        print('--> f_area_array: ' + str(f_area_array))
        print('--> f_category: ' + str(f_category))
        print('--> decimal_divider: ' + str(decimal_divider))

        # dataType = f_param_array[2]
        f_param = f_param_array[0]
        param_band1 = f_param['Band1']
        f_area = f_area_array[0]
        area_band1 = f_area['Band1']
        category_band1 = f_category['Band1']
        no_data_param = param_band1.attrs['_FillValue']
        no_data_area = area_band1.attrs['_FillValue']
        no_data_category = category_band1.attrs['_FillValue']
        np_param = np.array(param_band1).astype(float)
        np_area = np.array(f_area['Band1']).astype(float)
        np_category = np.array(f_category['Band1']).astype(float)

        np_param[np_param == no_data_param] = np.nan
        np_area[np_area == no_data_area] = np.nan
        np_category[np_category == no_data_category] = np.nan

        np_ar = np.array([np_area.flatten(), np_category.flatten(), np_param.flatten()])

        df = pd.DataFrame(np_ar[0, :], columns=['area'])
        df['category'] = np_ar[1, :]
        df['value'] = np_ar[2, :]
        df = df[pd.notnull(df['area'])]
        df = df[pd.notnull(df['value'])]
        df_stat = df.groupby(['category'])['value'].agg(
            ['count', 'mean', 'min', 'max', 'std', 'median', 'sum']).reset_index()
        data = np.array(df_stat)

        for item in data:
            rows.append((item[0], item[1], (item[2]) / decimal_divider, (item[3]) / decimal_divider,
                         (item[4]) / decimal_divider, (item[5]) / decimal_divider, (item[6]) / decimal_divider,
                         (item[7]) / decimal_divider))

        my_datatype = np.dtype(
            [('category', np.int16), ('count', np.int32), ('mean', np.float), ('min', np.float), ('max', np.float),
             ('std', np.float), ('median', np.float), ('sum', np.float)])

        category_fname = os.path.basename(f_category.filename)
        id_category = str(category_fname.split('_')[0])

        result = rows, my_datatype, 'base_statistic_groupby_' + str(id_category)

        # write data to h5 file
        if len(result[0][0]) > 0:
            self.write_statistics2h5(f_param_array, f_area_array, result)
        else:
            print("WARNING -> length of result: 0")

    # area subclasses == true (total_region = 0), category subclasses == false
    def run_a1_c0(self, f_param_array, f_area_array, stat):

        # my_datatype = None, None

        decimal_divider = self.check_decimals(f_param_array)

        print('--> f_param_array: ' + str(f_param_array))
        print('--> f_area_array: ' + str(f_area_array))
        print('--> decimal_divider: ' + str(decimal_divider))

        # dataType = f_param_array[2]
        f_param = f_param_array[0]
        param_band1 = f_param['Band1']
        f_area = f_area_array[0]
        area_band1 = f_area['Band1']
        no_data_param = param_band1.attrs['_FillValue']
        no_data_area = area_band1.attrs['_FillValue']
        np_param = np.array(param_band1).astype(float)
        np_area = np.array(f_area['Band1']).astype(float)

        np_param[np_param == no_data_param] = np.nan
        np_area[np_area == no_data_area] = np.nan

        np_ar = np.stack((np_area, np_param))

        df = pd.DataFrame({'area': np_ar[0].flatten(), 'value': np_ar[1].flatten()})
        df = df[pd.notnull(df['area'])]

        df_stat = df.groupby(['area'])['value'].agg(
            ['count', 'mean', 'min', 'max', 'std', 'median', 'sum']).reset_index()
        my_datatype = np.dtype(
            [('area', np.int32), ('count', np.int32), ('mean', np.float), ('min', np.float), ('max', np.float),
             ('std', np.float), ('median', np.float), ('sum', np.float)])
        data = np.array(df_stat)
        rows = []
        for item in data:
            if stat == 'avg':
                rows.append((item[0], item[1], (item[2]) / decimal_divider, (item[3]) / decimal_divider,
                             (item[4]) / decimal_divider, (item[5]) / decimal_divider, (item[6]) / decimal_divider,
                             (item[7]) / decimal_divider))
            if stat == 'sum':
                rows.append((item[0], item[1], (item[7]) / decimal_divider, (item[7]) / decimal_divider,
                             (item[7]) / decimal_divider, (item[7]) / decimal_divider, (item[7]) / decimal_divider,
                             (item[7]) / decimal_divider))

        result = rows, my_datatype, 'base_statistic'

        # write data to h5 file
        if len(result[0][0]) > 0:
            self.write_statistics2h5(f_param_array, f_area_array, result)
        else:
            print("WARNING -> length of result: 0")

    # area subclasses == true (total_region = 0), category subclasses == true
    def run_a1_c1(self, f_param_array, f_area_array, f_category):
        
        # my_datatype, id_category = None, None

        decimal_divider = self.check_decimals(f_param_array)

        print('--> f_param_array: ' + str(f_param_array))
        print('--> f_area_array: ' + str(f_area_array))
        print('--> f_category: ' + str(f_category))
        print('--> decimal_divider: ' + str(decimal_divider))

        # dataType = f_param_array[2]
        f_param = f_param_array[0]
        param_band1 = f_param['Band1']
        f_area = f_area_array[0]
        area_band1 = f_area['Band1']
        category_band1 = f_category['Band1']
        no_data_param = param_band1.attrs['_FillValue']
        no_data_area = area_band1.attrs['_FillValue']
        no_data_category = category_band1.attrs['_FillValue']
        np_param = np.array(param_band1).astype(float)
        np_area = np.array(f_area['Band1']).astype(float)
        np_category = np.array(f_category['Band1']).astype(float)

        np_param[np_param == no_data_param] = np.nan
        np_area[np_area == no_data_area] = np.nan
        np_category[np_category == no_data_category] = np.nan

        np_ar = np.array([np_area.flatten(), np_category.flatten(), np_param.flatten()])
        df = pd.DataFrame(np_ar[0, :], columns=['area'])
        df['category'] = np_ar[1, :]
        df['value'] = np_ar[2, :]
        df = df[pd.notnull(df['area'])]
        df = df[pd.notnull(df['value'])]

        df_stat = df.groupby(['area', 'category'])['value'].agg(
            ['count', 'mean', 'min', 'max', 'std', 'median', 'sum']).reset_index()
        data = np.array(df_stat)

        rows = []

        for item in data:
            rows.append((item[0], item[1], item[2], (item[3]) / decimal_divider, (item[4]) / decimal_divider,
                         (item[5]) / decimal_divider, (item[6]) / decimal_divider, (item[7]) / decimal_divider,
                         (item[8]) / decimal_divider))

        my_datatype = np.dtype(
            [('area', np.int32), ('category', np.int16), ('count', np.int32), ('mean', np.float), ('min', np.float),
             ('max', np.float), ('std', np.float), ('median', np.float), ('sum', np.float)])

        category_fname = os.path.basename(f_category.filename)
        id_category = str(category_fname.split('_')[0])

        result = rows, my_datatype, 'base_statistic_groupby_' + str(id_category)

        # write data to h5 file
        if len(result[0][0]) > 0:
            self.write_statistics2h5(f_param_array, f_area_array, result)
        else:
            print("WARNING -> length of result: 0")

    def check_decimals(self, f_param):
        
        decimal_divider = 1
        decimals = float(f_param[1])
        data_type = f_param[4]
        print('--> decimals : ' + str(decimals))
        print('--> data_type : ' + str(data_type))
        if data_type in ["int8", "int16", "int32", "int64"] and decimals != 0:
            decimal_divider = math.pow(10, decimals)
            print("decimal_divider: " + str(decimal_divider))
        return decimal_divider

    def write_statistics2h5(self, f_param_array, f_area_array, data):
        
        print("write statistics to h5 file")

        path = f_param_array[2]
        fname = f_param_array[3] + '.stats.h5'
        id_area = str(f_area_array[4])

        # total_region = data[1]
        tbl_name = data[2]
        dtype = data[1]
        stat_data = data[0]

        # create structure
        f = h5py.File(path + fname, 'a')
        if f.get('areas') is None:
            grp = f.create_group('areas')
        else:
            grp = f['areas']
        if grp.get(id_area) is None:
            grp_area = grp.create_group(id_area)
            # grp_area_total = grp_area.create_group('total')
            grp_area_regions = grp_area.create_group('regions')
        else:
            # grp_area_total = grp['/areas/' + idArea + '/total']
            grp_area_regions = grp['/areas/' + id_area + '/regions']

        # delete table if exists and create new dataset
        for i in grp_area_regions.items():
            # print(str(i)+' == '+ tblName)
            if i[0] == tbl_name:
                del grp_area_regions[tbl_name]
        ds = grp_area_regions.create_dataset(tbl_name, (len(stat_data),), compression="gzip", compression_opts=9,
                                             dtype=dtype)
        ds[:] = stat_data

        f.close()

    def close_files(self, files):
        
        for f in files:
            if f != -1:
                print(f)
                f.close()
                print(f)
