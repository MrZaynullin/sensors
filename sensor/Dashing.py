"""Dashing module"""

import urllib2

import simplejson as json


DEFAULT_DASHING_AUTH_TOKEN = 'YOUR_AUTH_TOKEN'


class Dashing(object):
	"""Send data to dashing widget

	Usage:

	dashing = Dashing('http://localhost:3030')
	dashing.send_data('welcome', {'text': 'Hello from python!'})
	"""

	def __init__(self, host_url, auth_token=None):
		self._host_url = host_url
		self._auth_token = auth_token or DEFAULT_DASHING_AUTH_TOKEN

	def _get_widget_url(self, widget_id):
		"""Return dashing widget url for the given widget id

		Args:
		widget_id(str): widget id
		"""

		return '{host_url}/widgets/{widget_id}'.format(
			host_url=self._host_url,
			widget_id=widget_id,
			)

	def _get_auth_token_data(self):
		"""Return a dict of 'auth_token' -> `auth_token`
		"""

		return {
			'auth_token': self._auth_token
		}

	def _get_request(self, widget_id, data):
		"""Retrun a urllib2.Request object

		Args:
		widget_id(str): widget id
		data(dict): data to be sent to dashing widget
		"""

		url = self._get_widget_url(widget_id)
		request_data = self._get_auth_token_data()
		request_data.update(data)
		encoded_data = json.dumps(request_data)

		return urllib2.Request(url=url, data=encoded_data)

	def send_data(self, widget_id, data):
		"""Send data to a dashing widget

		Args:
		widget_id(str): widget id
		data(dict): data to be sent to dashing widget
		"""

		request = self._get_request(widget_id, data)
		urllib2.urlopen(request).read()
