import time
from typing import Any, List, Tuple
from process import MpCoordinator
from multiprocessing import freeze_support, set_start_method, Pipe, Pool
from multiprocessing.connection import Connection
import dill
from context import timing
import math
import time

import sys
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=False)


class MyCoordinator(MpCoordinator):

    def __init__(self, workerCount: int):
        self.x = 5
        super().__init__(workerCount)

    def work(self, index: int, count: int):
        return worker(count)


def own(count, repeat, cores):
    startTime = time.time()
    with timing("Coord Startup"):
        coordinator = MyCoordinator(cores)

    with timing("Coord Results:"):
        for _ in range(repeat):
            result = coordinator.startWork(cores, count)

    with timing("Coord Deactivate"):    
        coordinator.deactivate()
    return time.time() - startTime

def worker(count):
    result = 0
    for i in range(count):
        result += math.factorial(i)
    return result

def standard(count, repeat, cores):
    startTime = time.time()
    with timing("Pool Startup"):
        pool = Pool(processes=cores)
    
    with timing("Pool Results"):
        for _ in range(repeat):
            results = pool.map(worker, [count] * cores)

    with timing("Pool Deactivate"):
        pool.close()
        pool.join()
    return time.time() - startTime

if __name__ == "__main__":
    freeze_support()
    set_start_method("spawn")

    count = 5000
    repeat = 10
    cores = 20
    print(f"{cores} Cores with {repeat} executions for x={count}:")
    tOwn = own(count, repeat, cores)
    tStandard = standard(count, repeat, cores)
    print(f"\nTotal new coordinator: {tOwn}")
    print(f"Total classic Pool: {tStandard}")
    print(f"Difference: {tStandard - tOwn}")