# -*- coding: utf8 -*-

"""
Dashboard module

Класс для отправки данных в dashboard.

"""

import logging
import urllib, urllib2

class Dashboard:
	def __init__(self, url):
		self.url = url

	def send_data(self, data):
		try:
			encoded_data = urllib.urlencode(data)
			request = urllib2.Request(url=self.url, data=encoded_data)
			urllib2.urlopen(request).read()
		except urllib2.HTTPError, e:
			logging.info("[Dashboard] HTTPError = %s" % str(e.code))
		except urllib2.URLError, e:
			logging.info("[Dashboard] URLError = %s" % str(e.reason))
		except httplib.HTTPException, e:
			logging.info("[Dashboard] HTTPException: %s" % str(e))
		except Exception as e:
			logging.info("[Dashboard] Generic exception: %s" % str(e))
