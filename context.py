import sys
import os
import contextlib
import time

@contextlib.contextmanager
def surpress_console():
	old_stdout = sys.stdout # backup current stdout
	sys.stdout = open(os.devnull, "w")
	yield
	sys.stdout = old_stdout # reset old stdout
	
@contextlib.contextmanager
def timing(msg = ""):
	start_time = time.time()
	yield
	if msg:
		print(f"{msg}: {time.time() - start_time}")
	else:
		print(f"Timed: {time.time() - start_time}")