from configparser import ConfigParser

from analysis.function.Comparators.function_comparator import compare_functions
from trace_reader_utils.pickle_utils import get_dict_from_pickle

if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read('/Users/erikbl/PycharmProjects/TraceReader/config.ini')
    conf = cfg['SINGLEFUN']
    filter_dupes = conf.getboolean('filter_dupes', True)
    file1 = conf.get('file1')
    file2 = conf.get('file2')
    fun1 = conf.get('fun1')
    fun2 = conf.get('fun2')
    if fun1.isdigit():
        fun1 = int(fun1)
    if fun2.isdigit():
        fun2 = int(fun2)

    dict1 = get_dict_from_pickle(file1)
    dict2 = get_dict_from_pickle(file2)

    print(str(compare_functions(fun1, fun2, dict1, dict2, filter_dupes)))

