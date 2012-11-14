# -*- coding: UTF-8 -*-
import sqlite3 as sqlite
from Log import Log
from config import config

class Logs:
	def __init__(self, gui):
		self.logs = []
		self.gui = gui

	def reload(self):
		self.logs = []

		con = sqlite.connect(config.DB)
		cur = con.cursor()
		cur.execute("SELECT id, logDate FROM logs ORDER BY logDate DESC;")

		for row in cur:
			self.logs.append((row[0], row[1]))

		cur.close()

	def deleteLog(self, logId):
		con = sqlite.connect(config.DB)
		cur = con.cursor()

		cur.execute("DELETE FROM logs WHERE id = ?;", (logId,))

		con.commit()
		cur.close

		self.gui.logListRepopulate()

	def getLog(self, logId):
		return Log(logId)

	def parseData(self, data):
		log = Log()

		sample = 0
		for a, b in zip(data[::2],data[1::2]):
			steps = a + 256 * b
			if (steps != 0xffff):
				log.add(sample, steps)
				sample = sample + 1

		return log
