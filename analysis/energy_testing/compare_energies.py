import sys
from typing import List
from analysis.energy_testing.compare_full_trace import get_sums_from_dir
import scipy


#def compare_energies(population1: List[float], population2: List[float]):
 #   statistic, pvalue = scipy.stats.kruskal(population1, population2)

def compare_directories(*directories):
    sums = [get_sums_from_dir(d) for d in directories]
    return scipy.stats.kruskal(*sums)

if __name__ == "__main__":
    print(compare_directories(sys.argv[1:]))
