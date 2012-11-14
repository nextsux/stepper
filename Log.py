# -*- coding: UTF-8 -*-
import sqlite3 as sqlite
from config import config

class Log:
	def __init__(self, logId = None):
		self.logId = logId
		self.samples = {}
		self.steps = 0

		if (logId):
			self.__load()

	def __load(self):
		con = sqlite.connect(config.DB)
		cur = con.cursor()
		cur.execute("SELECT sample_no, steps FROM samples WHERE logs_id = ? ORDER BY sample_no;", (self.logId,))
		for row in cur:
			self.samples[row[0]] = row[1]
			self.steps = self.steps + row[1]

		cur.close()

	def saveLog(self):
		con = sqlite.connect(config.DB)
		cur = con.cursor()

		cur.execute("INSERT INTO logs DEFAULT VALUES;")
		self.logId = cur.lastrowid

		for sample_no, steps in self.samples.iteritems():
			cur.execute("INSERT INTO samples (logs_id, sample_no, steps) VALUES (?, ?, ?)", (self.logId, sample_no, steps))

		con.commit()
		cur.close()

	def add(self, sample, steps):
		self.samples[sample] = steps
		self.steps = self.steps + steps
