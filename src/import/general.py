import json
import os
import sys


class general:
    
    def __init__(self):
        # print("class general")
        self.configFile = None
        self.preProcess = None

        i = 1
        while i < len(sys.argv):

            arg = sys.argv[i]
            if arg == '-f':
                i = i + 1
                self.configFile = sys.argv[i]
                # print("config file: " + str(self.configFile))
            elif arg == '-p':
                i = i + 1
                self.preProcess = sys.argv[i]
                # print("preprocessing activity: " + str(self.preProcess))
            i = i + 1

        if self.configFile is None:
            print("missing argument: config file")
            sys.exit("cancel preprocessing")
        if self.preProcess is None:
            print("missing argument: process")
            sys.exit("cancel preprocessing")

    def load_config(self):
        # print("load config file")
        path = self.configFile
        if os.path.isfile(path):
            json_file = open(path)
            try:
                config = json.load(json_file)
            except Exception as e:
                sys.exit(e)
        else:
            sys.exit("config file does not exist")

        return config

    def load_json_file(self, path):
        # print("load json file ", path)
        if os.path.isfile(path):
            json_file = open(path)
            try:
                config = json.load(json_file)
            except Exception as e:
                sys.exit(e)
        else:
            sys.exit("config file does not exist")

        return config
