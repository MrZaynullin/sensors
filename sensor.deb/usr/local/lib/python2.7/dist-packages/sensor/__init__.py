# -*- coding: utf8 -*-

"""
Sensor module

Класс для запуска процессов, выполняющих проверки

"""

# torrent disable by https://pm.is74.ru/issues/968

import os
import signal
import time
import logging
from multiprocessing import Process

from Config import Config
from Dhcp import Dhcp
from Ping import Ping
from Dns import Dns
from Http import Http
from Statistics import Statistics
from Rzs import Rzs
from NetworkNamespace import NetworkNamespace

class Sensor:
	def __init__(self, conffile = '/etc/stm/sensors.conf'):
		self.is_alive = True
		self.processes = []
		self.check_items = dict()
		self.config = Config(conffile)

		"""
		Словарь соответствия проверок и пространств имен
		Например:
		checks = {
			'ping': {
				'ping.int': ['ZV', 'ZVNAT', 'WIFI', 'BLOCK'],
				'ping.ext': ['ZV', 'ZVNAT', 'WIFI']
			},
			'dhcp': {'dhcp': ['ZV', 'ZVNAT', 'WIFI', 'BLOCK']}
		}
		"""
		self.checks = self.config.get_checks()

		"""
		Словарь соответствия проверок и параметров для запуска
		Например:
		params = {
			'http.int': {'host': 'is74.ru', 'namespaces': ['ZV', 'ZVNAT', 'WIFI', 'BLOCK']},
			'dns': {'query_type': 'A', 'host': 'vk.com', 'namespaces': ['ZV', 'ZVNAT', 'WIFI', 'BLOCK']
		}
		"""
		self.params = self.config.get_params()

		# Словарь соответствия проверок и интервалов между повторными запусками проверок
		self.intervals = self.config.get_intervals()

		"""
		Формируем словарь check_items
		check_items[название_проверки] = объект_класса_проверки
		Например:
		check_items = {
			'dhcp': <sensor.Dhcp.Dhcp instance>,
			'ping.ext': <sensor.Ping.Ping instance>
		}

		"""
		for i in self.checks.keys():
			for j in self.checks[i]:
				p = None

				if i == 'dhcp':
					p = Dhcp()
				elif i == 'ping':
					p = Ping()
				elif i == 'dns':
					p = Dns()
				elif i == 'http':
					p = Http()
				elif i == 'statistics':
					p = Statistics()
				elif i == 'rzs':
					p = Rzs()

				self.check_items[j] = p

	# Создаем пространства имен
	def create(self):
		logging.info("[Sensor] Create")
		self.namespaces = dict()

		for i in self.config.get_namespaces_list():
			if self.is_alive:
				self.namespaces[i] = NetworkNamespace()
				self.namespaces[i].create(nsname = i, service = i)

	# Запускаем проверки
	def start(self):
		logging.info("[Sensor] Start")

		for i in self.check_items:
			self.params[i]['check'] = i
			self.params[i]['delay'] = self.intervals[i]

			self.check_items[i].start(self.params[i])

		for i in self.check_items:
			self.check_items[i].join()

	def destroy(self):
		logging.info("[Sensor] Destroy")

		self.is_alive = False

		for i in self.namespaces.keys():
			self.namespaces[i].destroy(nsname = i, service = i)

	def kill(self, sig, frame):
		for i in self.check_items:
			self.check_items[i].kill_checks()

		self.destroy()

		os._exit(0)
