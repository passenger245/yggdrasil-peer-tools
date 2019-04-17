#/usr/bin/python3
import http.client
import json
import subprocess
import select
import time
import os
class peerCheck(object):

	def __init__(self):
		self.connCheckHosts = ['y.tekst.xyz']
	def get_peers(self):
		conn = http.client.HTTPSConnection('api.yggdrasil.icu', 443, timeout=10)
		conn.request("GET", "/peers.json")
		data = conn.getresponse()
		return json.load(data)
	def parse_line(self, stdout):
		stdout = str(stdout)
		if len(stdout) > 0:
			pass
		if stdout.find("Connected TCP") == -1:
			return False
		if len(stdout.split()) < 5:
			return False
		try:
			ygg_ip, public_ip = stdout.split()[4].split("@")
			return {
				"ygg_ip": ygg_ip,
				"public_ip": public_ip[:-1]
			}
		except:
			pass


	def add_peer(self, peerIP, port):
		cmd = "yggdrasilctl addPeer uri='tcp://%s:%s'" % (peerIP, port)
		addpeer_p = subprocess.Popen(cmd,shell=True)

	def launch_process(self, peerIP, peerPort):
		cleanConf = subprocess.Popen("yggdrasil -genconf".split(),stdout=subprocess.PIPE)
	
		cmd = "yggdrasil -useconf" 
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stdin=cleanConf.stdout)

		poller = select.poll()
		poller.register(process.stdout, select.POLLIN)
		timeS = time.time()
		connected = False
		added_peer = False
		while 1:		
			if poller.poll(1):
				if not added_peer:
					added_peer = True
					self.add_peer(peerIP, peerPort)

				connected = self.parse_line(process.stdout.readline())
				if connected:
					break
			else:			
				time.sleep(1)
			if time.time() - timeS > 5:
				break

		if connected:
			# need ping twice, first ping attempt always fails in OS returncode
			cmd = "ping -c1 -w5 %s" % self.connCheckHosts[0]
			ping = subprocess.Popen(cmd.split())
			retr = ping.wait()
			ping = subprocess.Popen(cmd.split())
			retr = ping.wait()

			connected["connectivity_check"] = retr == 0

			process.terminate()

			return connected
		else:
			process.terminate()
			return False
