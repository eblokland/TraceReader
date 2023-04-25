import sys
from configparser import ConfigParser

from analysis.power_comparison.power_comparator import directory_compare

if __name__ == "__main__":
    args = sys.argv
    conf_loc = args[1] if len(args) > 1 else './config.ini'
    cfg = ConfigParser()
    cfg.read(conf_loc)
    pow_conf = cfg['DIRECTORY_POWCOMP']
    filter_dupes = pow_conf.getboolean('filter_dupes', True)
    directory = pow_conf.get('directory')
    out_file = pow_conf.get('out_file')
    decimals = pow_conf.getint('decimals')
    if directory is None or out_file is None:
        exit(-1)

    directory_compare(filter_dupes=filter_dupes, directory=directory, output_file=out_file, decimals=decimals)