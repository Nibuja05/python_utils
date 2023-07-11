
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import Any, Dict, List, Union, Tuple
import psutil
import dill


def testFunc():
	pass

class MpCoordinator():

	def __init__(self, workerCount: int):
		self.count = workerCount
		self.workerCount = workerCount
		self.processes: List[Process] = []
		self.cons: List[Tuple[Connection, Connection]] = []
		self.prepareProcesses()

	def __getstate__(self):
		state = self.__dict__.copy()
		del state["count"]
		del state["workerCount"]
		del state["processes"]
		del state["cons"]
		return state

	def prepareProcesses(self):
		for i in range(self.workerCount):
			recvCon, sendCon = Pipe(False)
			sRecvCon, sSendCon = Pipe(False)
			process = Process(target=self.handleProcess, args=(i, sendCon, sRecvCon))
			self.processes.append(process)
			self.cons.append((recvCon, sSendCon))
			process.start()

		for i in range(self.workerCount):
			con, _ = self.cons[i]
			process = self.processes[i]
			con.recv()
			ps = psutil.Process(process.pid)
			ps.suspend()

	def deactivate(self, id: int = -1):
		# for i in range(self.workerCount):
		# 	_, sendCon = self.cons[i]
		# 	process = self.processes[i]
		# 	ps = psutil.Process(process.pid)
		# 	ps.resume()
			# sendCon.send(None)

		for i in range(self.workerCount):
			# con, _ = self.cons[i]
			process = self.processes[i]
			# con.recv()
			process.kill()

		self.processes = None
		self.cons = None

	def startWork(self, actionCount: int, msgData: Any, iterableData: List[Any] = []) -> List[Any]:
		messages = []

		for i in range(0, actionCount, self.workerCount):
			count = min(self.workerCount, actionCount - i)
			newMessages = self.manageWorkCommunication(count, msgData, iterableData[i:i + count])
			messages.extend(newMessages)

		return messages

	def manageWorkCommunication(self, count: int, msgData: Any, iterableData: List[Any]) -> List[Any]:
		messages = []

		# send request to process
		for i in range(count):
			_, sendCon = self.cons[i]
			process = self.processes[i]
			ps = psutil.Process(process.pid)
			ps.resume()
			sendCon.send((iterableData[i] if i < len(iterableData) else None, msgData))

		# gather answers
		for i in range(count):
			con, _ = self.cons[i]
			process = self.processes[i]
			messages.append(con.recv())
			ps = psutil.Process(process.pid)
			ps.suspend()

		return messages

	def handleProcess(self, index: int, sendCon: Connection, statusCon: Connection):
		sendCon.send(None)

		while True:
			receiveData = statusCon.recv()
			if receiveData is None:
				sendCon.send(None)
			else:
				iterableData, constantData = receiveData
				try:
					answer = self.work(index, *([constantData, iterableData] if (iterableData is not None) else [constantData]))
					sendCon.send(answer)
				except Exception as e:
					print("Error in work function:  " + str(e) + "\n")
					sendCon.send(None)
	
	def work(self, index: int, data: Any):
		return 10 + index