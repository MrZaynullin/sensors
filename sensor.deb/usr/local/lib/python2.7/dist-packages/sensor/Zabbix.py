"""Zabbix module"""

import logging
import socket
from zabbix.sender import ZabbixMetric, ZabbixSender

class Zabbix:
	def __init__(self, server):
		self.server = server

	def send(self, host, item, value):
		if value == None:
			value = 0

		try:
			m = [ ZabbixMetric(socket.getfqdn(), item, value), ]
			z = ZabbixSender(zabbix_server=self.server).send(m)
		except Exception as e:
			logging.info("[Zabbix] Generic exception: %s" % str(e))
