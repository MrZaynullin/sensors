# -*- coding: utf8 -*-

"""
Lldp module

Класс для получения информации по LLDP

"""

import lldpy
import logging
import socket
from Db import Db

class LldpCtl(lldpy.Watcher):
	""" A custom class to hook into llpdctl utility. """
	def __init__(self, interface):
		super(LldpCtl, self).__init__()
		self.location = socket.gethostname().upper()
		self.interface = interface
		self.db = Db()
		self.is_alive = True

	def on_add(self, local, remote):
		if local.interface_name == self.interface:
			self.location = self.db.get_topology(remote.chassis_name)[-1][3]
			self.location = self.location.upper()

	def on_delete(self, local, remote):
		if local.interface_name == self.interface:
			self.location = socket.gethostname()
			self.location = self.location.upper()

	def on_update(self, local, remote):
		if local.interface_name == self.interface:
			self.location = self.db.get_topology(remote.chassis_name)[-1][3]
			self.location = self.location.upper()

	def get_location(self):
		return self.location
