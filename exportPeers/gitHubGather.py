#!/usr/bin/python

import subprocess
import os
import re
import ipaddress
import geocoder



class gitHubGather:
	def prepare_repo(self):
		if os.path.exists("public-peers"):
			os.chdir("public-peers")
			cmd = "git pull"

		else:
			cmd = "git clone https://github.com/yggdrasil-network/public-peers.git"
		FNULL = open(os.devnull, 'w')
		checkout = subprocess.Popen(cmd.split(),stdout=FNULL, stderr=subprocess.STDOUT)
		checkout.wait()
		if checkout.returncode == 0:
			if cmd != "git pull":
				os.chdir("public-peers")
			return True
		return False
	def validateIP(self, ip,port):
		isIPv4 = False
		isIPv6 = False


		try:
			addressObj = ipaddress.IPv4Address(unicode(ip))
			isIPv4 = True
		except:
			pass

		if not isIPv4:
			try:
				addressObj = ipaddress.IPv6Address(unicode(ip))
				isIPv6 = True
			except:
				pass

		if not isIPv4 and not isIPv6:
			return False
		if addressObj.is_global:
			return {str(addressObj): {
					"is_ipv6": isIPv6,
					"is_ipv4": isIPv4,
					"port": port
				}}
			


	def parseFile(self, filePath):
		fhandle = open(filePath)
		filedata = fhandle.read()
		ips_ipv4 =  re.findall('`(.*)`', filedata)
		peers = {}
		for ip in ips_ipv4:		
			ip = ip.replace("tcp://","")
			expData = ip.split(":")
			ip = ":".join(expData[:-1]).replace("[","").replace("]","")
			ip_entry = self.validateIP(ip,expData[-1])
			if ip_entry:
				peers.update(ip_entry)
		return peers


	def getPlainPeers(self):
		self.prepare_repo()
		peers = {}
		for continent in os.listdir("."):
			if os.path.isdir(continent):
				for item in os.listdir(continent):
					if item.find(".md") == -1:
						continue
					filePath = "%s/%s" % (continent, item)
					peers.update(self.parseFile(filePath))
		os.chdir("..")
		return peers	

