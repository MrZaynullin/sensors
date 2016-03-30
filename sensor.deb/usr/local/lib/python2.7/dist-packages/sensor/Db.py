"""Db module"""

import os
os.environ['ORACLE_HOME'] = '/usr/lib/oracle/12.1/client64'
os.environ['TNS_ADMIN'] = '/etc/oracle'
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
import cx_Oracle

class Db:
	def __init__(self):
		self.server = 'DB'
		self.username = 'username'
		self.password = 'password'

	def get_topology(self, bsname):
		db = cx_Oracle.connect(self.username, self.password, self.server)
		cursor = db.cursor()
		
		cursor.execute ("""SELECT * FROM table1 WHERE bsname = '%s'""" % (bsname) )

		topology = cursor.fetchall()
		cursor.close()
		db.close()

		return topology
