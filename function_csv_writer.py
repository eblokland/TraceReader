import csv
from typing import List, Any
from statistical_analysis import Function

csv_header = ['function address', 'name set', 'leaf samples', 'tree samples', 'local probability',
              'nonlocal probability','local prob interval', 'nonlocal prob interval', 'local runtime', 'nonlocal runtime', 'local energy', 'nonlocal energy',
              'mean local power', 'mean nonlocal power']


def write_function(writer, fun: Function):
    arr: List[Any] = [fun.addr] + list(fun.name_set) + \
                     [fun.num_leaf_samples, fun.num_samples, fun.local_prob,
                      fun.nonlocal_prob, fun.local_prob_interval, fun.nonlocal_prob_interval, fun.local_runtime, fun.nonlocal_runtime, fun.local_energy_cost,
                      fun.nonlocal_energy_cost, fun.mean_local_power, fun.mean_nonlocal_power]
    writer.writerow(arr)


def write_csv(output_file: str, functions: List[Function]):
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quotechar='|')
        writer.writerow(csv_header)
        for fun in functions:
            write_function(writer, fun)

