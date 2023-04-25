import csv
import os
from configparser import ConfigParser
from typing import List, Optional

from scipy.stats import ttest_ind

from trace_reader_utils.file_utils import get_filename
from trace_reader_utils.pickle_utils import gzip_unpickle
from trace_representation.app_sample import PowerSample


def compare_pow_lists(x: List[PowerSample], y: List[PowerSample]) -> float:
    x_list = list(map(lambda samp: samp.power, x))
    y_list = list(map(lambda samp: samp.power, y))

    return ttest_ind(a=x_list, b=y_list, equal_var=False).pvalue


def single_file_compare(file1: str, file2: str, filter_dupes: bool) -> float:
    powers1 = gzip_unpickle(file1)
    powers2 = gzip_unpickle(file2)
    if filter_dupes:
        powers1 = set(powers1)
        powers2 = set(powers2)
    res = compare_pow_lists(powers1, powers2)
    return res

def single_file_compare_withavg(file1: str, file2: str, filter_dupes: bool):
    powers1 = gzip_unpickle(file1)
    powers2 = gzip_unpickle(file2)
    if filter_dupes:
        powers1 = set(powers1)
        powers2 = set(powers2)
    res = compare_pow_lists(powers1, powers2)
    avg1 = sum(list(map(lambda samp: samp.power, powers1))) / len(powers1)
    avg2 = sum(list(map(lambda samp: samp.power, powers2))) / len(powers2)
    return res, avg1, avg2


def directory_compare(directory: str, filter_dupes: bool, output_file: str, decimals: Optional[int] = None):
    file_list: List[str] = os.listdir(directory)
    filtered_files_list = list(filter(lambda file: '_power' in file, file_list))
    filtered_files_list.sort()
    num_files = len(filtered_files_list)

    #result_matrix = [[0 for _ in range(num_files)] for _ in range(num_files)]
    csv_header = [' '] + [name.removesuffix('_power.pickle.gz') for name in filtered_files_list]
    csv_lines = [csv_header]

    for (index, file) in enumerate(filtered_files_list):
        # row before col
        results = [file.removesuffix('_power.pickle.gz')]
        for (compindex, comp) in enumerate(filtered_files_list[:index]):
            res = single_file_compare(directory+file, directory+comp, filter_dupes)
            if decimals is not None:
                res = f'{res:.{decimals}}'
            results.append(res)
        for _ in filtered_files_list[index:]:
            results.append('')
        csv_lines.append(results)

    filename = get_filename(output_file, '.csv')
    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quotechar='|')
        writer.writerows(csv_lines)
