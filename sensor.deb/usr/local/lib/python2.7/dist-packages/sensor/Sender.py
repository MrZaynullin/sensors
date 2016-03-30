"""Sender module"""

import urllib, urllib2

class Sender:
	def __init__(self, url):
		self.url = url

	def send_data(self, data):
		encoded_data = urllib.urlencode(data)
		request = urllib2.Request(url=self.url, data=encoded_data)
		urllib2.urlopen(request).read()
