# -*- coding: utf8 -*-

"""
Statistics module

Класс для отправки статистики.
Наследуется от класса ProcessLauncher.

"""

# torrent disable by https://pm.is74.ru/issues/968

import time
import logging
from ProcessLauncher import ProcessLauncher
from Dashboard import Dashboard
from LldpCtl import LldpCtl
from Zabbix import Zabbix

class Statistics(ProcessLauncher):
	def __init__(self):
		self.type = 'statistics'

	def start(self, args):
		self.zabbix = Zabbix(args['zabbix'])
		self.server = Dashboard(args['dashboard'])
		self.lldpctl = LldpCtl(args['discovery'])
		self.namespaces = args['namespaces']
		self.check = args['check']
		self.delay = args['delay']

		# Запуск функции run из родительского класса ProcessLauncher
		self.run()

	# Отправка статистики
	def single(self, ns):
		self.signal()

		self.lldpctl.start()
		# Время на инициализацию LLDP
		time.sleep(5)

		while True:
			self.location = self.lldpctl.get_location()

			for i in self.results.keys():
				res = self.results.get(i, 'NONE')

				if res != 'NONE':

					if res['type'] == 'dhcp' and res['ns'] == ns:
						dhcp_state = res.get('state', 'NONE')
						dhcp_time = res.get('time', None)

						if dhcp_state == 'OK' and dhcp_time > 30:
							dhcp_state = 'WARN'

						try:
							if dhcp_state != 'RUN':
								self.zabbix.send(self.location, res['type'] + '.' + res['ns'], dhcp_time)

							self.server.send_data({ 'location': self.location, 'service': ns, 'check' : res['check'], 'value': dhcp_state })
						except Exception as e:
							logging.info("[Statistics] Generic exception: %s" % str(e))

					elif res['type'] == 'ping' and res['ns'] == ns:
						ping_state = res.get('state', 'NONE')
						ping_max_rtt = res.get('max_rtt', None)
						ping_avg_rtt = res.get('avg_rtt', None)
						ping_min_rtt = res.get('min_rtt', None)
						ping_packet_lost = res.get('packet_lost', None)

						if ping_state == 'OK' and (ping_packet_lost != 0 or float(ping_avg_rtt) > 200):
							ping_state = 'WARN'

						try:
							if ping_state != 'RUN':
								self.zabbix.send(self.location, res['type'] + '.time.' + res['ns'] + '[' + res['check'] + ']', ping_avg_rtt)
								self.zabbix.send(self.location, res['type'] + '.lost.' + res['ns'] + '[' + res['check'] + ']', ping_packet_lost)

							self.server.send_data({ 'location': self.location, 'service': ns, 'check' : res['check'], 'value' : ping_state })
						except Exception as e:
							logging.info("[Statistics] Generic exception: %s" % str(e))

					elif res['type'] == 'dns' and res['ns'] == ns:
						dns_state = res.get('state', 'NONE')
						dns_qtime = res.get('qtime', None)

						if dns_state == 'OK' and float(dns_qtime) > 200:
							dns_state = 'WARN'

						try:
							if dns_state != 'RUN':
								self.zabbix.send(self.location, res['type'] + '.' + res['ns'], dns_qtime)

							self.server.send_data({ 'location': self.location, 'service': ns, 'check' : res['check'], 'value': dns_state })
						except Exception as e:
							logging.info("[Statistics] Generic exception: %s" % str(e))

					elif res['type'] == 'http' and res['ns'] == ns:
						http_state = res.get('state', 'NONE')
						http_code = res.get('code', None)
						http_time = res.get('time', None)
						http_speed = res.get('speed', None)
						http_size = res.get('size', None)

						if http_state == 'OK' and float(http_time) > 5:
							http_state = 'WARN'

						try:
							if http_state != 'RUN':
								self.zabbix.send(self.location, res['type'] + '.time.' + res['ns'] + '[' + res['check'] + ']', http_time)
								self.zabbix.send(self.location, res['type'] + '.speed.' + res['ns'] + '[' + res['check'] + ']', http_speed)

							self.server.send_data({ 'location': self.location, 'service': ns, 'check' : res['check'], 'value': http_state })
						except Exception as e:
							logging.info("[Statistics] Generic exception: %s" % str(e))

					elif res['type'] == 'rzs' and res['ns'] == ns:
						rzs_state = res.get('state', 'NONE')
						rzs_total = res.get('rzs_total', None)
						rzs_available = res.get('rzs_available', None)
						rzs_unavailable = res.get('rzs_unavailable', None)

						if rzs_state == 'OK' and (float(rzs_available)/float(rzs_total) > 0.1):
							rzs_state = 'WARN'

						if rzs_state == 'OK' and (float(rzs_available)/float(rzs_total) > 0.3):
							rzs_state = 'FAIL'

						try:
							if rzs_state != 'RUN':
								self.zabbix.send(self.location, res['type'] + '.total.' + res['ns'], rzs_total)
								self.zabbix.send(self.location, res['type'] + '.available.' + res['ns'], rzs_available)
								self.zabbix.send(self.location, res['type'] + '.unavailable.' + res['ns'], rzs_unavailable)

							self.server.send_data({ 'location': self.location, 'service': ns, 'check' : res['check'], 'value': rzs_state })
						except Exception as e:
							logging.info("[Statistics] Generic exception: %s" % str(e))

			time.sleep(float(self.delay))
