# -*- coding: utf8 -*-

"""
ProcessLauncher module

Общий класс для запуска процессов, выполняющих проверки.
От класса ProcessLauncher наследуются все классы, выполняющие 
непосредственные проверки.
Класс содержит общие поля и методы необходимых для работы
дочерних классов.

"""

import os
import signal
from multiprocessing import Process, Manager

class ProcessLauncher:
	# Менеджер, разделяющий переменные между подпроцессами
	manager = Manager()
	# Хранилище с результатами проверок
	results = manager.dict()
	# Список пространств имен
	namespaces = []
	# Словарь соответствия проверок и выполняющих их процессов
	processes = dict()
	# Тип проверки
	type = ''

	# Функция для запуска подпроцессов, выполняющих проверки
	# Для каждого namespace и каждого типа проверки будет рожден свой процесс
	def run(self):
		for i in self.namespaces:
			# Для каждого из процессов будет вызвана функция self.single
			p = Process(target = self.single, args=(i,))
			p.start()
			self.processes[i + '_' + self.check] = p

	# Функцию single реализуют дочерние классы
	def single(self, ns):
		pass

	# Обработчики сигналов в дочерних процессах
	def signal(self):
		signal.signal(signal.SIGINT, self.kill)
		signal.signal(signal.SIGTERM, self.kill)

	# Функция убивающаяя процесс. Вызывается из дочерних процессов
	def kill(self, sig, frame):
		os._exit(0)

	# Получение типа проверки
	def get_type(self):
		return self.type

	# Функция, вызывающая join() для подпроцессов
	def join(self):
		for i in self.namespaces:
			self.processes[i + '_' + self.check].join()

	# Функция убивающая все дочерние подпроцессы
	def kill_checks(self):
		for i in self.namespaces:
			p = self.processes.pop(i + '_' + self.check, None)

			if p != None:
				p.terminate()
