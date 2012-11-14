# -*- coding: UTF-8 -*-
import os
import sqlite3 as sqlite

class config:
	DB = None
	dataDir = '.'

	stepLenCm = 1
	kCalKm = 1

	def __init__(self):
		config.DB = 'stepper.db'
		self.checkOrUpgradeDb()
		self.loadSettings()

	def checkOrUpgradeDb(self):	
		homedir = os.path.expanduser('~')
		try:
			# not tested ... I do not have that M$ shit
			from win32com.shell import shellcon, shell
			homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
		except ImportError:
			homedir = os.path.expanduser("~")

		self.dataDir = os.path.join(homedir, ".stepper/")
		config.DB = os.path.join(self.dataDir, config.DB)

		if not os.path.isdir(self.dataDir):
			os.mkdir(self.dataDir)

		con = sqlite.connect(config.DB)
		cur = con.cursor()

		try:
			cur.execute("SELECT version FROM version LIMIT 1;")
			ver = cur.fetchone()
			self.version = ver[0]
		except sqlite.OperationalError, e:
			self.version = 0

		if self.version == 0:
			# no db... create one
			cur.execute('CREATE TABLE logs (id integer primary key, logDate date);')
			cur.execute('CREATE TABLE samples (id integer primary key, logs_id integer not null, sample_no integer not null, steps integer not null default 0, foreign key(logs_id) references logs(id) on delete cascade);')
			cur.execute('CREATE TABLE version(version int);')
			cur.execute('CREATE INDEX samples_logs_id_ix on samples(logs_id);')
			cur.execute("""CREATE TRIGGER delete_samples_with_log before delete on logs
BEGIN
DELETE FROM samples WHERE logs_id = old.rowid;
END;
			""")
			cur.execute("""CREATE TRIGGER insert_logs_logDate after insert on logs
BEGIN
update logs set logDate = DATETIME(\'NOW\', \'LOCALTIME\') WHERE rowid = new.rowid;
END;
			""")
			cur.execute('INSERT INTO version (version) VALUES (1);')
			con.commit()
			self.version = 1
			
		if self.version == 1:
			cur.execute('CREATE TABLE settings (steplencm integer, kcalperkm integer);')
			cur.execute('INSERT INTO settings (steplencm, kcalperkm) VALUES (60, 70);')
			cur.execute('UPDATE version SET version = 2;')
			con.commit()
			self.version = 2

		if self.version > 2:
			raise ValueError('Unknown DB version')

		cur.close()

	def loadSettings(self):
		con = sqlite.connect(config.DB)
		cur = con.cursor()

		cur.execute("SELECT steplencm, kcalperkm FROM settings LIMIT 1;")
		settings = cur.fetchone()

		config.stepLenCm = int(settings[0])
		config.kCalKm = int(settings[1])

		cur.close()
