import time
from typing import Any, List, Tuple
from process import MpCoordinator
from multiprocessing import freeze_support, set_start_method, Pipe
from multiprocessing.connection import Connection
import dill

import sys
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=False)


class MyCoordinator(MpCoordinator):

	def __init__(self, workerCount: int):
		self.x = 5
		super().__init__(workerCount)

	def work(self, index: int, count: int):
		for i in range(count):
			pass
		return True


def main():
	coordinator = MyCoordinator(20)

	result = coordinator.startWork(10, 100)
	print(result)

	time.sleep(1)
	print("Deactivate...")
	coordinator.deactivate()

if __name__ == "__main__":
	print("Test...")
	freeze_support()
	set_start_method("spawn")
	main()