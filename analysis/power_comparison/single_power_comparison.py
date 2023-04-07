from configparser import ConfigParser

from analysis.power_comparison.power_comparator import single_file_compare

if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('/Users/erikbl/PycharmProjects/TraceReader/config.ini')
    pow_conf = cfg['SINGLE_POWCOMP']

    print(single_file_compare(
        pow_conf.get('file1'),
        pow_conf.get('file2'),
        pow_conf.getboolean('filter_dupes', True)
    ))
