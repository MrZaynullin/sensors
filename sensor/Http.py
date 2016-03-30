# -*- coding: utf8 -*-

"""
Http module

Класс, выполняющий Http проверки.
Наследуется от класса ProcessLauncher.

"""

import time
import pycurl
import logging
from pyroute2 import netns

from ProcessLauncher import ProcessLauncher

class Http(ProcessLauncher):
	def __init__(self, host='is74.ru'):
		self.type = 'http'
		self.host = host

	def start(self, args):
		self.host = args['host']
		self.namespaces = args['namespaces']
		self.check = args['check']
		self.delay = args['delay']

		# Запуск функции run из родительского класса ProcessLauncher
		self.run()

	# Реализация проверки Http
	def single(self, ns):
		self.signal()
		netns.setns(ns)

		k = ns + '_' + self.check

		c = pycurl.Curl()
		c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
		c.setopt(c.FOLLOWLOCATION, 1)
		c.setopt(c.MAXREDIRS, 5)
		c.setopt(c.OPT_FILETIME, 1)
		c.setopt(pycurl.CONNECTTIMEOUT, 15)
		c.setopt(pycurl.TIMEOUT, 30)
		c.setopt(pycurl.NOSIGNAL, 1)

		while True:
			self.results[k] = { 'check': self.check, 'type': self.type, 'ns': ns, 'state': 'RUN' }
			res = self.results[k]

			try:
				c.setopt(c.URL, self.host)
				c.perform()

				res['code'] = c.getinfo(c.HTTP_CODE)
				res['time'] = c.getinfo(c.TOTAL_TIME)
				res['speed'] = c.getinfo(c.SPEED_DOWNLOAD)
				res['size'] = c.getinfo(c.SIZE_DOWNLOAD)
				res['state'] = 'OK'

				logging.info("[HTTP:%s] host = %s, return code = %d, total time = %.2f sec, download speed = %.2f b/sec, download size = %d Kb" % (ns, self.host, c.getinfo(c.HTTP_CODE), c.getinfo(c.TOTAL_TIME), c.getinfo(c.SPEED_DOWNLOAD), c.getinfo(c.SIZE_DOWNLOAD) / 1024))
			except:
				res['state'] = 'FAIL'

				logging.info("[HTTP:%s] Cannot get %s" % (ns, self.host))

			self.results[k] = res

			time.sleep(float(self.delay))
