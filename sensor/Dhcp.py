# -*- coding: utf8 -*-

"""
Dhcp module

Класс, выполняющий Dhcp проверки.
Наследуется от класса ProcessLauncher.

"""

import re
import random
import time
import logging
import traceback
import socket
from pyroute2.dhcp import BOOTREQUEST, DHCPDISCOVER, DHCPOFFER, DHCPREQUEST, DHCPACK, DHCPRELEASE
from pyroute2.dhcp.dhcp4msg import dhcp4msg
from pyroute2.dhcp.dhcp4socket import DHCP4Socket
from pyroute2 import IPRoute,netns,common

from ProcessLauncher import ProcessLauncher

class Dhcp(ProcessLauncher):
	def __init__(self):
		self.type = 'dhcp'
		self.status = ''

	def request(self, s, msg, expect):
		request_count = 0
		request_max = 5

		# get transaction id
		logging.info("[DHCP] sending DHCP message")
		xid = s.put(msg)['xid']
		logging.info("[DHCP] sent DHCP message with xid = %s" % xid)

		while request_count < request_max:
			request_count += 1

			timeout = time.time() + 2

			if msg['options']['message_type'] == DHCPRELEASE:
				return True

			while time.time() < timeout:
				# wait for response
				logging.info("[DHCP] try get DHCP message with xid = %s" % xid)
				response = s.get()
				logging.info("[DHCP] got DHCP message with xid = %s" % xid)
				if response['xid'] != xid:
					continue

				if response['options']['message_type'] != expect:
					logging.info("[DHCP] Protocol error")
					response = None

				return response

		return None

	def start(self, args):
		self.namespaces = args['namespaces']
		self.check = args['check']
		self.delay = args['delay']

		# Запуск функции run из родительского класса ProcessLauncher
		self.run()

	# DHCPDISCOVER
	def dhcpdiscover(self, socket, xid, chaddr):
		discover = dhcp4msg({'op': BOOTREQUEST,
							'chaddr': chaddr,
							'xid': xid,
							'options': {'message_type': DHCPDISCOVER,
										'parameter_list': [1, 3, 6, 12, 15, 28]}})

		try:
			reply = self.request(socket, discover, expect=DHCPOFFER)
			return reply
		except:
			return None

	# DHCPREQUEST
	def dhcprequest(self, socket, xid, chaddr, requested_ip, server_id):
		request = dhcp4msg({'op': BOOTREQUEST,
							'chaddr': chaddr,
							'xid': xid + 1,
							'options': {'message_type': DHCPREQUEST,
										'requested_ip': requested_ip,
										'server_id': server_id,
										'parameter_list': [1, 3, 6, 12, 15, 28]}})

		try:
			reply = self.request(socket, request, expect=DHCPACK)
			return reply
		except:
			return None

	# DHCPRElEASE
	def dhcprelease(self, socket, xid, chaddr, ciaddr, server_id):
		release = dhcp4msg({'op': BOOTREQUEST,
							'chaddr': chaddr,
							'ciaddr': ciaddr,
							'xid': xid,
							'options': {'message_type': DHCPRELEASE,
										'server_id': server_id,
										'parameter_list': [1, 3, 6, 12, 15, 28]}})

		try:
			reply = self.request(socket, release, expect=0)
			return reply
		except:
			return None

	def add_address(self, ifname, yiaddr, mask, gateway):
		if not self.ip.get_addr(family=socket.AF_INET, label=ifname):
			dev = self.ip.link_lookup(ifname=ifname)[0]
			self.ip.addr('add', index=dev, address=yiaddr, mask=common.dqn2int(mask))
		else:
			for j in self.ip.get_addr(family=socket.AF_INET, label=ifname):
				if j['attrs'][0][1] != yiaddr:
					self.ip.flush_addr(label=ifname)
					dev = self.ip.link_lookup(ifname=ifname)[0]
					self.ip.addr('add', index=dev, address=yiaddr, mask=common.dqn2int(mask))

		if not self.ip.get_default_routes(family=socket.AF_INET):
			self.ip.route("add", dst="0.0.0.0", mask=0, gateway=gateway)
		else:
			for j in self.ip.get_default_routes(family=socket.AF_INET):
				if j['attrs'][1][1] != gateway:
					self.ip.flush_routes()
					self.ip.route("add", dst="0.0.0.0", mask=0, gateway=gateway)

	def single(self, ns):
		self.signal()
		netns.setns(ns)

		k = ns + '_' + self.check

		ifname = 'veth1' + ns
		s = DHCP4Socket(ifname)

		# Turn off blocking mode for socket
		s.settimeout(1.0)

		self.ip = IPRoute()

		try:
			while True:
				self.results[k] = { 'check': self.check, 'type': self.type, 'ns': ns, 'state': 'RUN' }
				res = self.results[k]

				xid = random.randrange(4294967294)

				logging.info("[DHCP:%s] DHCPDISCOVER try" % ns)
				reply = self.dhcpdiscover(s, xid, s.l2addr)
				logging.info("[DHCP:%s] DHCPDISCOVER finish" % ns)

				if reply == None:
					logging.info("[DHCP:%s] DHCPDISCOVER error" % ns)
					self.results[k]['state'] = 'FAIL'

					# DHCPDISCOVER sleep
					time.sleep(1)
					continue

				while reply != None:
					start = time.time()
					logging.info("[DHCP:%s] DHCPREQUEST try" % ns)
					reply = self.dhcprequest(s, xid, s.l2addr, reply['yiaddr'], reply['options']['server_id'])
					logging.info("[DHCP:%s] DHCPREQUEST finish" % ns)
					stop = time.time()

					if reply == None:
						logging.info("[DHCP:%s] DHCPREQUEST error" % ns)
						self.results[k]['state'] = 'FAIL'

						# DHCPREQUEST sleep
						time.sleep(1)
						# Go to DHCPRELEASE
						break

					yiaddr = reply['yiaddr']
					mask = reply['options']['subnet_mask']
					gateway = reply['options']['router'][0]
					server_id = reply['options']['server_id']

					logging.info("[DHCP:%s] add address try" % ns)
					self.add_address(ifname, yiaddr, mask, gateway)
					logging.info("[DHCP:%s] add address finish" % ns)

					res['options'] = { 'xid': xid, 'yiaddr': yiaddr, 'server_id': server_id }
					res['time'] = stop - start
					res['state'] = 'OK'

					logging.info("[DHCP:%s] DHCPREQUEST yiaddr = %s, mask = %s, gateway = %s" % (ns, yiaddr, mask, gateway))

					self.results[k] = res

					# DHCPREQUEST sleep
					time.sleep(float(self.delay))

				# DHCPRELEASE
				if 'options' in res:
					logging.info("[DHCP:%s] DHCPRELEASE try" % ns)
					reply = self.dhcprelease(s, res['options']['xid'], s.l2addr, res['options']['yiaddr'], res['options']['server_id'])
					logging.info("[DHCP:%s] DHCPRELEASE finish" % ns)

					if reply == None:
						logging.info("[DHCP:%s] DHCPRELEASE error" % ns)
					else:
						logging.info("[DHCP:%s] DHCPRELEASE yiaddr = %s" % (ns, res['options']['yiaddr']))

					# DHCPRELEASE sleep
					time.sleep(1)

		except Exception, e:
			error = traceback.format_exc()
			logging.critical("[DHCP:%s] Exception : %s" % (ns, str(e)))
			logging.critical("[DHCP:%s] Traceback : %s" % (ns, str(error)))
