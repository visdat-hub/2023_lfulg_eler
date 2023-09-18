# python3 /src/modelling/main.py /src/config/modelling/165.config
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os
import sys
import time

from general.process import process

if __name__ == "__main__":

    print("Starte STOFFBILANZ-Modellierung ...")

    sc_path = os.environ.get('STB_CONFIG_SCENARIO_PHAT')
    param_path = os.environ.get('STB_CONFIG_PARAMETER_PHAT')
    area_path = os.environ.get('STB_CONFIG_AREA_PHAT')
    grid_path = os.environ.get('STB_CONFIG_GRID_PHAT')
    nc_path = os.environ.get('STB_CONFIG_NC_PHAT')

    print('grid_path', grid_path)

    t1 = time.time()

    # Konfigurationsobjekt laden
    print(sys.argv)

    if len(sys.argv) == 2:

        if sys.argv[1]:
            pathConfigFile = sys.argv[1]
            print(pathConfigFile)
            json_file = open(pathConfigFile)
            data_config = json.load(json_file)

            json_file = open(sc_path)
            data_sc = json.load(json_file)

            for d in data_sc:

                if d['id_sc'] == data_config['id_sc']:
                    data_config['id_sc2'] = d['id_sc']
                    # data_config['model_project_name'] = d['model_project_name']
                    data_config['model_scenario_name'] = d['model_scenario_name']
                    data_config['model_year'] =  d['model_year']
            # print('--> data_config',data_config)

            json_file = open(grid_path)
            data_level = json.load(json_file)
            # print('--> data_level', data_level)

            json_file = open(nc_path)
            data_nc = json.load(json_file)
            # print('--> data_nc',data_nc)

            json_file = open(param_path)
            data_param = json.load(json_file)
            # print('--> data_param',data_param)

            json_file = open(area_path)
            data_area = json.load(json_file)
            # print('--> data_area',data_area)

            p = process(data_config, data_param, data_area, data_level, data_nc)
            p.stb_processing()

    else:
        print("Bitte Configfile angeben!")

    t2 = time.time()
    print('Laufzeit:')
    print(str(t2 - t1))