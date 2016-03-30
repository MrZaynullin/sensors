"""Torrent module"""

import time
import shutil
import logging
import libtorrent
from pyroute2 import netns

from ProcessLauncher import ProcessLauncher

class Torrent(ProcessLauncher):
	def __init__(self, file='/etc/stm/test.torrent'):
		self.file = file

	def start(self, args):
		self.file = args['file']
		self.namespaces = args['namespaces']

		self.run()

	def single(self, ns):
		self.signal()
		netns.setns(ns)

		self.results[ns + '_torrent_state'] = "RUN"

		session = libtorrent.session()
		session.listen_on(6881, 6891)

		info = libtorrent.torrent_info(self.file)
		resource = session.add_torrent({'ti' : info, 'save_path' : '/var/tmp/' + ns})

		download_rates_sum = 0 
		download_rates_avg = 0.0 
		upload_rates_sum = 0 
		upload_rates_avg = 0.0 
		download_count = 0 
		upload_count = 0 

		start = time.time()

		while (not resource.is_seed()):
			status = resource.status()
			download_rate = status.download_rate
			upload_rate = status.upload_rate

			if download_rate != 0:
				download_rates_sum += download_rate
				download_count += 1

			if upload_rate != 0:
				upload_rates_sum += upload_rate
				upload_count += 1

			time.sleep(1)

		end = time.time()

		if download_count == 0:
			download_count = 1 

		if upload_count == 0:
			upload_count = 1 

		download_rates_avg = float(download_rates_sum) / download_count
		upload_rates_avg = float(upload_rates_sum) / upload_count

		shutil.rmtree('/var/tmp/' + ns, ignore_errors=True)

		self.results[ns + "_torrent_downspeed"] = download_rates_avg
		self.results[ns + "_torrent_upspeed"] = upload_rates_avg
		self.results[ns + "_torrent_time"] = end - start
		self.results[ns + '_torrent_state'] = "OK"

		logging.info("[TORRENT:%s] download speed = %.2f b/s, upload speed = %.2f b/s, time = %.2f sec" % (ns, download_rates_avg, upload_rates_avg, (end - start)))
