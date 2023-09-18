from __future__ import unicode_literals
import sys
import os

from general import general
from module.copy_parameter import copy_parameter
from module.delete_parameter import delete_parameter
from module.import_parameter import import_parameter
from module.generate_statistics import generate_statistics
from module.import_area import import_area

if __name__ == "__main__":

    print("--> starting program to import geodata to model grid structure...")

    error = False

    g = general()
    
    data_config = g.load_config()
    # print('data_config-->' + str(data_config))

    path = os.environ.get('STB_CONFIG_SCENARIO_PHAT')
    data_scenarios = g.load_json_file(path)
    # print('data_scenarios-->' + str(data_scenarios))

    path = os.environ.get('STB_CONFIG_PARAMETER_PHAT')
    data_parameter = g.load_json_file(path)
    # print('data_parameter-->' + str(data_parameter))

    path = os.environ.get('STB_CONFIG_AREA_PHAT')
    data_area = g.load_json_file(path)
    # print('data_area-->' + str(data_area))

    path = os.environ.get('STB_CONFIG_GRID_PHAT')
    grid_config = g.load_json_file(path)
    # print('grid_config-->' + str(grid_config))

    process = g.preProcess
    # print("--> process: " + process)
    # print("--> data_config['process'] ", data_config['process'] )

    if process == "import_area" and data_config['process'] == 'import_area':
        print("--> process: " + process)

        p = import_area()
        p.do_import(grid_config, data_config)

    if process == "import_parameter" and data_config['process'] == 'import_parameter':
        print("--> process: " + process)

        p = import_parameter()
        p.do_import(data_config, grid_config, data_scenarios, data_parameter)

    if process == "generate_statistics" and data_config['process'] == 'generate_statistics':
        print("--> process: " + process)

        p = generate_statistics()

        error = p.check_statistic(data_config, data_scenarios, data_parameter, data_area)

        if not error:
            p.do_statistics(data_config, data_scenarios, data_parameter)

    if process == 'copy_parameter' and data_config['process'] == 'copy_parameter':
        print("--> process: " + process)

        p = copy_parameter()

        if data_config['checkFile'] == 1:
            error = p.check_copy(data_config, data_scenarios, data_parameter)

        if not error:
            p.do_copy(data_config, data_scenarios, data_parameter)

            if data_config['insertDB'] == 1:
                p.insert_copy(data_config)

    """
    if process == 'import_parameter' and data_config['process'] == 'import_parameter':
        print("--> process: " + process)

        p = copy_parameter()

        sys.exit()

        if data_config['checkFile'] == 1:
            error = p.check_copy(data_config, data_scenarios, data_parameter)

        if not error:
            p.do_copy(data_config, data_scenarios, data_parameter)

            if data_config['insertDB'] == 1:
                p.insert_copy(data_config)
    """

    if process == 'delete_parameter' and data_config['process'] == 'delete_parameter':
        print("--> process: " + process)

        p = delete_parameter()

        p.do_delete(data_config, data_scenarios)

        if data_config['deleteDB'] == 1:
            p.do_delete_db(data_config)

    print("--> preprocessing finished")
