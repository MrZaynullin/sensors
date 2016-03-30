# -*- coding: utf8 -*-

"""
Config module

Класс для обработки конфигурационных файлов

"""

import ast
import ConfigParser

class Config:
	def __init__(self, conffile = '/etc/stm/sensors.conf'):
		self.config = ConfigParser.ConfigParser()
		self.config.read(conffile)
		self.checks = None

	# Вернуть список пространств имен
	def get_namespaces_list(self):
		return self.config.get('common', 'namespaces').replace(" ", "").split(',')

	"""
	Вернуть словарь, в котором каждой проверке соответствует список пространств имен
	Например:
	checks = {
		'ping': {'ping.int': ['ZV', 'ZVNAT', 'WIFI', 'BLOCK'], 'ping.ext': ['ZV', 'ZVNAT', 'WIFI']},
		'dhcp': {'dhcp': ['ZV', 'ZVNAT', 'WIFI', 'BLOCK']}
	}
	"""
	def get_checks(self):
		self.checks = dict()

		self.checks['dhcp'] = ast.literal_eval(self.config.get('dhcp', 'checks'))
		self.checks['ping'] = ast.literal_eval(self.config.get('ping', 'checks'))
		self.checks['dns'] = ast.literal_eval(self.config.get('dns', 'checks'))
		self.checks['http'] = ast.literal_eval(self.config.get('http', 'checks'))
		self.checks['statistics'] = ast.literal_eval(self.config.get('statistics', 'checks'))
		self.checks['rzs'] = ast.literal_eval(self.config.get('rzs', 'checks'))

		return self.checks

	"""
	Вернуть словарь, в котором каждой проверке соответствует список параметров для запуска
	Перед запуском этой функции необходимо запустить функцию get_checks()
	Например:
	params = {
		'http.int': {'host': 'is74.ru', 'namespaces': ['ZV', 'ZVNAT', 'WIFI', 'BLOCK']},
		'dns': {'query_type': 'A', 'host': 'vk.com', 'namespaces': ['ZV', 'ZVNAT', 'WIFI', 'BLOCK']
	}
	"""
	def get_params(self):
		self.params = dict()

		# Запускаем get_checks(), если забыли
		if self.checks is None:
			self.get_checks()

		for i in self.checks['dhcp'].keys():
			self.params[i] = ast.literal_eval(self.config.get('dhcp', i))
			self.params[i]['namespaces'] = self.checks['dhcp'][i]

		for i in self.checks['ping'].keys():
			self.params[i] = ast.literal_eval(self.config.get('ping', i))
			self.params[i]['namespaces'] = self.checks['ping'][i]

		for i in self.checks['dns'].keys():
			self.params[i] = ast.literal_eval(self.config.get('dns', i))
			self.params[i]['namespaces'] = self.checks['dns'][i]

		for i in self.checks['http'].keys():
			self.params[i] = ast.literal_eval(self.config.get('http', i))
			self.params[i]['namespaces'] = self.checks['http'][i]

		for i in self.checks['statistics'].keys():
			self.params[i] = ast.literal_eval(self.config.get('statistics', i))
			self.params[i]['namespaces'] = self.checks['statistics'][i]

		for i in self.checks['rzs'].keys():
			self.params[i] = ast.literal_eval(self.config.get('rzs', i))
			self.params[i]['namespaces'] = self.checks['rzs'][i]

		return self.params

	# Вернуть значение паузы между повторными проверками
	def get_intervals(self):
		self.intervals = dict()

		if self.checks is None:
			return None

		for i in self.checks['dhcp'].keys():
			self.intervals[i] = self.config.get('dhcp', 'interval')

		for i in self.checks['ping'].keys():
			self.intervals[i] = self.config.get('ping', 'interval')

		for i in self.checks['dns'].keys():
			self.intervals[i] = self.config.get('dns', 'interval')

		for i in self.checks['http'].keys():
			self.intervals[i] = self.config.get('http', 'interval')

		for i in self.checks['statistics'].keys():
			self.intervals[i] = self.config.get('statistics', 'interval')

		for i in self.checks['rzs'].keys():
			self.intervals[i] = self.config.get('rzs', 'interval')

		return self.intervals
