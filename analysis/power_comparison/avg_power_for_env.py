import os
import sys
from configparser import ConfigParser

from parsers.environment_parser.EnvironmentParser import EnvironmentLog

def get_avg_power(file: str, current_divider: float) -> float:
    env = EnvironmentLog(file, current_divider)
    return env.get_power_average()

def get_power_for_directory(directory: str, current_divider: float):
    files = os.listdir(directory)
    averages = []
    good_files = []
    for file in files:
        with open(directory+file, 'r') as open_file:
            #just swallow exceptions
            try:
                if 'INIT FILE' in open_file.readline():
                    good_files.append(file)
            except:
                pass

    for file in good_files:
        avg = get_avg_power(directory + file, current_divider)
        averages.append((file, avg))
    return averages

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 3:
        print(get_avg_power(args[1], float(args[2])))
    if len(args) == 2:
        conf = args[1]
        cfg = ConfigParser()
        cfg.read(conf)
        cfg = cfg['AVGPOWER']
        dir_mode = cfg.getboolean('dir_mode')
        directory = cfg.get('directory')
        filename = cfg.get('filename')
        current_divider = cfg.getfloat('current_divider')

        if dir_mode:
            avgs = get_power_for_directory(directory, current_divider)
            for average in avgs:
                print(f'name: {average[0]} average: {average[1]}')
        else:
            print(get_avg_power(directory+filename, current_divider))