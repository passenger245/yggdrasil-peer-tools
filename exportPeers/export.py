#!/usr/bin/python

from gitHubGather import gitHubGather
import geocoder
import os
import json
import time
import sys
import traceback
class Export(gitHubGather):

	def __init__(self):
		self.exportBucket = {}
		self.verbosive = True
	def stdout(self, data):
		if self.verbosive:
			print data

	def get_export(self):
		if not os.path.exists("peersExport.json"):
			self.stdout("No cache exists")
			return {}
		try:
			return json.load(open("peersExport.json"))
		except:
			return {}

	def write_export(self):
		a = open("peersExport.json","w")
		a.write(json.dumps(self.exportBucket))
		a.close()

	def sync(self):
		currentData = self.get_export()
		gitHubData = self.getPlainPeers()
		syncedData = {}
		

		for peerIP in currentData:
			if peerIP in gitHubData:
				syncedData[peerIP] = currentData[peerIP]
				self.stdout("Already seen peer: %s" % peerIP)				
		for peerIP in gitHubData:
			if peerIP not in syncedData:
				self.stdout("New peer: %s" % peerIP)
				syncedData[peerIP] = gitHubData[peerIP]
				syncedData[peerIP]["first_seen"] = int(time.time())
		return syncedData

	def get(self):
		self.exportBucket = self.sync()
		self.geocode_peers()
		self.write_export()
	def geocode_peer(self, peerIP):
		geocode = geocoder.ip(peerIP)
		
		if geocode.latlng != []:
			self.stdout("Geocoded %s to %s" % (peerIP, geocode.latlng))
			self.exportBucket[peerIP]["latlng_cords"] = geocode.latlng

	def geocode_peers(self):
		for peerIP in self.exportBucket:
			if "latlng_cords" not in self.exportBucket[peerIP]:
				self.geocode_peer(peerIP)
	
export = Export()
try:			
	export.get()
	export.stdout("OK - exported")
	sys.exit(0)
except SystemExit:
	pass
except:
	traceback.print_exc()
	sys.exit(1)
		
