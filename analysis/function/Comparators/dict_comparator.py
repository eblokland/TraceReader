import sys
from typing import Dict

from analysis.function.Comparators.comparison_csv_writer import write_compare_csv
from analysis.function.Comparators.function_comparator import compare_dict
from trace_reader_utils.pickle_utils import gzip_unpickle

if __name__ == "__main__":
    numargs = len(sys.argv)
    if numargs != 4:
        print('Syntax: python function_comparator.py pickle1 pickle2 outfile')
        sys.exit(0)
    trace_1 = gzip_unpickle(str(sys.argv[1]))
    trace_2 = gzip_unpickle(str(sys.argv[2]))
    if trace_1 is None or trace_2 is None:
        print('Invalid pickle files!')
        sys.exit(-1)

    if isinstance(trace_1, Dict) and isinstance(trace_2, Dict):
        result = compare_dict(trace_1, trace_2)
        write_compare_csv(str(sys.argv[3]), result)
    else:
        print('traces not dict?')