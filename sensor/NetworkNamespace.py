# -*- coding: utf8 -*-

"""
NetworkNamespace module

Класс для управления пространствами имен.

"""

import os
import signal
import logging
from pyroute2 import NetNS,IPDB,netns

class NetworkNamespace:
	def __init__(self):
		self.nsname = ''
		self.service = ''
		self.veth0 = ''
		self.veth1 = ''
		self.bridge_iface = ''
		self.ns = None

	def create(self, nsname = 'ns', service = 'ZV'):
		signal.signal(signal.SIGINT, self.kill)
		signal.signal(signal.SIGTERM, self.kill)

		if self.is_exist(nsname):
			logging.info("[NS:%s] Namespace is exist" % (nsname))
			return

		self.nsname = nsname
		self.service = service
		self.ns = NetNS(self.nsname)

		self.veth0 = 'veth0' + self.nsname
		self.veth1 = 'veth1' + self.nsname
		self.bridge_iface = self.service + '-BR'

		self.createInterface()

		logging.info("[NS:%s] Create namespace" % (self.nsname))

	def destroy(self, nsname = 'ns', service = 'ZV'):
		if self.nsname == '':
			self.nsname = nsname

		if not self.is_exist(self.nsname):
			logging.info("[NS:%s] Namespace is not exist" % (self.nsname))
			return

		if self.service == '':
			self.service = service

		if self.ns == None:
			self.ns = NetNS(self.nsname)

		if self.veth0 == '':
			self.veth0 = 'veth0' + self.nsname

		if self.veth1 == '':
			self.veth1 = 'veth1' + self.nsname

		if self.bridge_iface == '':
			self.bridge_iface = self.service + '-BR'

		self.destroyInterface()
		self.ns.close()
		self.ns.remove()

		logging.info("[NS:%s] Destroy namespace" % (self.nsname))

	def is_exist(self, nsname = 'ns'):
		if nsname in netns.listnetns():
			return True
		else:
			return False

	def createInterface(self):
		ipdb = IPDB()
		ipdb.create(ifname=self.veth0, kind='veth', peer=self.veth1).commit()

		with ipdb.interfaces[self.veth0] as i:
			i.up()

		with ipdb.interfaces[self.veth1] as i:
			i.up()
			i.net_ns_fd = self.nsname

		with ipdb.interfaces[self.bridge_iface] as i:
			i.add_port(ipdb.interfaces[self.veth0])

		ipdb.release()

	def destroyInterface(self):
		ipdb = IPDB()

		with ipdb.interfaces[self.bridge_iface] as i:
			i.del_port(ipdb.interfaces[self.veth0])

		with ipdb.interfaces[self.veth0] as i:
			i.remove()

		ipdb.release()

	def kill(self, sig, frame):
		os._exit(0)
