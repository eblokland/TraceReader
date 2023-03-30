import sys
from configparser import ConfigParser
from typing import Dict

from analysis.function.Comparators.comparison_csv_writer import write_compare_csv
from analysis.function.Comparators.function_comparator import compare_dict
from trace_reader_utils.pickle_utils import gzip_unpickle

if __name__ == "__main__":
    conf = ConfigParser()
    conf.read('./config.ini')
    conf = conf['TRACECOMP']

    file1 = conf.get('file1')
    file2 = conf.get('file2')
    filter_dupes = conf.getboolean('filter_dupes')
    output_file = conf.get('out_file')

    trace_1 = gzip_unpickle(file1)
    trace_2 = gzip_unpickle(file2)
    if trace_1 is None or trace_2 is None:
        print('Invalid pickle files!')
        sys.exit(-1)

    if isinstance(trace_1, Dict) and isinstance(trace_2, Dict):
        result = compare_dict(trace_1, trace_2, filter_dupes)
        write_compare_csv(output_file, result)
    else:
        print('traces not dict?')