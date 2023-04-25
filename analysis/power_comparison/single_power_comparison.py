from configparser import ConfigParser

from analysis.power_comparison.power_comparator import single_file_compare_withavg

if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('/Users/erikbl/PycharmProjects/TraceReader/config.ini')
    pow_conf = cfg['SINGLE_POWCOMP']


    res, avg1, avg2= single_file_compare_withavg(
        pow_conf.get('file1'),
        pow_conf.get('file2'),
        pow_conf.getboolean('filter_dupes', True)
    )
    print(f'{res} avg1: {avg1} avg2: {avg2}')
