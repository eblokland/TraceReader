import csv
from typing import List

from analysis.function.Comparators.function_result import FunctionResult

csv_header = ['name set', 'p-value local', 'p-value nonlocal', 'local-diff', 'nonlocal-diff']


def write_compare_csv(output_file: str, comp_list: List[FunctionResult]):
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quotechar='|')
        writer.writerow(comp_list[0].get_full_csv_header())
        for entry in comp_list:
            writer.writerow(entry.get_csv_fields())

