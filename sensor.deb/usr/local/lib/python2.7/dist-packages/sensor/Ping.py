# -*- coding: utf8 -*-

"""
Ping module

Класс, выполняющий Ping проверки.
Наследуется от класса ProcessLauncher.

"""

import time
import logging
import pyping
from pyroute2 import netns

from ProcessLauncher import ProcessLauncher

class Ping(ProcessLauncher):
	def __init__(self, host='is74.ru', count=5, length=64):
		self.type = 'ping'
		self.host = host
		self.count = count
		self.length = length

	def start(self, args):
		self.host = args['host']
		self.count = args['count']
		self.length = args['length']
		self.namespaces = args['namespaces']
		self.check = args['check']
		self.delay = args['delay']

		# Запуск функции run из родительского класса ProcessLauncher
		self.run()

	# Реализация проверки Ping
	def single(self, ns):
		self.signal()
		netns.setns(ns)

		k = ns + '_' + self.check

		while True:
			self.results[k] = { 'check': self.check, 'type': self.type, 'ns': ns, 'state': 'RUN' }
			res = self.results[k]

			try:
				r = pyping.ping(self.host, count=self.count, packet_size=self.length)

				res['max_rtt'] = r.max_rtt
				res['avg_rtt'] = r.avg_rtt
				res['min_rtt'] = r.min_rtt
				res['packet_lost'] = r.packet_lost
				res['state'] = 'OK'

				logging.info("[PING:%s] host = %s, max time = %s, avg time = %s, min time = %s, lost packets = %d" % (ns, self.host, r.max_rtt, r.avg_rtt, r.min_rtt, r.packet_lost))
			except:
				res['state'] = 'FAIL'

				logging.info("[PING:%s] Cannot ping host %s" % (ns, self.host))

			self.results[k] = res

			time.sleep(float(self.delay))
