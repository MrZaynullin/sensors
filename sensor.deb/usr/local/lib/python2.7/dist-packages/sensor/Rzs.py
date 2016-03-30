# -*- coding: utf8 -*-

"""
Rzs module

Класс, выполняющий Rzs проверки.
Наследуется от класса ProcessLauncher.

"""

import time
import requests
import logging
from pyroute2 import netns

from ProcessLauncher import ProcessLauncher

class Rzs(ProcessLauncher):
	def __init__(self, blockfile='/etc/stm/rzs.block'):
		self.type = 'rzs'
		self.blockfile = blockfile

	def start(self, args):
		self.blockfile = args['blockfile']
		self.namespaces = args['namespaces']
		self.check = args['check']
		self.delay = args['delay']

		# Запуск функции run из родительского класса ProcessLauncher
		self.run()

	# Реализация проверки Rzs
	def single(self, ns):
		self.signal()
		netns.setns(ns)

		logger_rzs = logging.getLogger('RZS')
		logger_rzs.propagate = False
		log_handler_rzs = logging.FileHandler('/var/log/sensors_rzs_' + ns + '.log')
		logger_rzs.addHandler(log_handler_rzs)

		logging.getLogger("urllib3").propagate = False

		k = ns + '_' + self.check

		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

		while True:
			self.results[k] = { 'check': self.check, 'type': self.type, 'ns': ns, 'state': 'RUN' }
			res = self.results[k]
			available_hosts_count = 0
			unavailable_hosts_count = 0
			total_hosts_count = 0

			try:
				f = open(self.blockfile, 'r')
				blocked_urls = f.read()
				f.close()

				for url in blocked_urls.splitlines():
					total_hosts_count += 1

					try:
						response = requests.get(url, headers=headers, timeout=0.5)
						available_hosts_count += 1
						logger_rzs.info("[RZS:%s] %s Available host: %s" % (ns, time.strftime("%H:%M:%S %d/%m/%Y", time.localtime(time.time())), url))
					except Exception as e:
						unavailable_hosts_count += 1

				res['rzs_total'] = total_hosts_count
				res['rzs_available'] = available_hosts_count
				res['rzs_unavailable'] = unavailable_hosts_count
				res['state'] = 'OK'

				logging.info("[RZS:%s] Total hosts count = %d, available hosts count = %d, unavailable hosts count = %d" % (ns, total_hosts_count, available_hosts_count, unavailable_hosts_count))
			except:
				res['state'] = 'FAIL'

				logging.info("[RZS:%s] Cannot open block file %s" % (ns, self.blockfile))

			self.results[k] = res

			time.sleep(float(self.delay))
