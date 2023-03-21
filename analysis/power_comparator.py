from configparser import ConfigParser
from typing import List

from scipy.stats import ttest_ind

from trace_reader_utils.pickle_utils import gzip_unpickle
from trace_representation.app_sample import PowerSample


def compare_pow_lists(x: List[PowerSample], y: List[PowerSample]) -> float:
    x_list = list(map(lambda samp: samp.power, x))
    y_list = list(map(lambda samp: samp.power, y))

    return ttest_ind(a=x_list, b=y_list, equal_var=False).pvalue


if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('/Users/erikbl/PycharmProjects/TraceReader/config.ini')
    pow_conf = cfg['POWCOMP']
    file1 = pow_conf.get('file1')
    file2 = pow_conf.get('file2')
    powers1 = gzip_unpickle(file1)
    powers2 = gzip_unpickle(file2)
    res = compare_pow_lists(powers1, powers2)
    print(res)
