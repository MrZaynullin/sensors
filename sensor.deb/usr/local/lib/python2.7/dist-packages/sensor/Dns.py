# -*- coding: utf8 -*-

"""
Dns module

Класс, выполняющий Dns проверки.
Наследуется от класса ProcessLauncher.

"""

import re
import time
import logging
import dns.resolver, dns.reversename
from pyroute2 import netns

from ProcessLauncher import ProcessLauncher

class Dns(ProcessLauncher):
	def __init__(self, host='is74.ru', server='78.29.2.21', query_type='A'):
		self.type = 'dns'
		self.host = host
		self.server = server
		self.query_type = query_type

	def start(self, args):
		self.host = args['host']
		self.server = args['server']
		self.query_type = args['query_type']
		self.namespaces = args['namespaces']
		self.check = args['check']
		self.delay = args['delay']

		# Запуск функции run из родительского класса ProcessLauncher
		self.run()

	# Реализация проверки Dns
	def single(self, ns):
		self.signal()
		netns.setns(ns)

		k = ns + '_' + self.check

		recursor = dns.resolver.Resolver()

		while True:
			self.results[k] = { 'check': self.check, 'type': self.type, 'ns': ns, 'state': 'RUN' }
			res = self.results[k]

			recursor.nameservers = [self.server]
			error = ""

			# Если резолвим IP адрес, приводим его к правильному виду
			if re.search("^\d+\.\d+\.\d+\.\d+$", self.host):
				self.host = dns.reversename.from_address(self.host)

			# Замеряем время выполнения запроса
			start = time.time()

			# Выполняем запрос
			try:
				answers = recursor.query (self.host, self.query_type)
			except dns.exception.DNSException as e:
				if isinstance(e, dns.resolver.NXDOMAIN):
					error = "No such domain " + str(self.host)
				elif isinstance(e, dns.resolver.Timeout):
					error = "Timed out while resolving " + str(self.host)
				elif isinstance(e, dns.resolver.NoAnswer):
					error = "No answer while resolving " + str(self.host)
				elif isinstance(e, dns.resolver.NoNameservers):
					error = "Nameserver " + str(self.server) + " not available"
				else:
					error = "Unhandled DNS exception"

			# Замеряем время выполнения запроса
			end = time.time()

			if error != "":
				res['qtime'] = (end - start) * 1000
				res['state'] = 'FAIL'

				logging.info("[DNS:%s] host = %s, query time = %.2f msec, return message = %s" % (ns, self.host, (end - start) * 1000, error))
			else:
				res['qtime'] = (end - start) * 1000
				res['state'] = 'OK'

				logging.info("[DNS:%s] host = %s, query time = %.2f msec, return message = Success" % (ns, self.host, (end - start) * 1000))

			self.results[k] = res

			time.sleep(float(self.delay))
