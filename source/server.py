#!/usr/bin/env python3
import select
import socket
import os
import datetime
import subprocess
import json
import fuzzyset
import time
import colorama

BUFFSIZE = 2048
ACTIVE = False
LAST_REFRESH = ""
INTERVAL = 600 #10 minutes

colorama.init()

#A context manager class which changes the working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#Reads config file
def readConfig():
	with open("data/config.json", 'r') as f:
		config = json.load(f)
	return config

#Checks if 24 hours have passed and resets download values for shows accordingly
def resetDownloadStatus():
	config = readConfig()
	watchlist = config['watchlist']
	timestamp = time.time()

	for show in watchlist.keys():
		if watchlist[show][1] != "False":
			if (timestamp - float(watchlist[show][1])) >= 86400:
				config['watchlist'][show][1] = "False"
	with open("data/config.json", "w") as f:
		json.dump(config, f, indent=4)

#Read watchlist from watchlist file
def setCorrectWatchlist(season):
	config = readConfig()
	watchlist = config['watchlist']

	#Add shows from current season to fuzzyset list
	fset = fuzzyset.FuzzySet()
	for show in season:
		fset.add(show)

	#Generating correct watchlist	
	fset_watchlist = {}
	for show in watchlist.keys():
		if fset.get(show)[0][0] >= 0.7:
			fset_watchlist[fset.get(show)[0][1]] = watchlist[show]
		else:
			print("\033[91m[-] {} does not seem to be airing this season! Ignoring..\033[0m".format(show))
	
	config['watchlist'] = fset_watchlist
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

#Gets scraped data from the data directory
def getData():
	#Change to scrapy directory
	with cd("downloader/downloader"):
		#Runs scrapy; remove the --nolog option to see logs in server.py output
		subprocess.run(["scrapy", "crawl", "data", "--nolog"])

	if not os.path.exists('data/data.json'):
		with open('data/data.json', 'w') as f:
			pass
	with open('data/data.json', 'r') as d:
		data = json.load(d)

	#Dictionary with entire data
	return data

#Calls Scrapy and downloads the episodes
def checkNewAndDownload(mode = "normal"):
	with cd("downloader/downloader"):
		#output = subprocess.run(["scrapy", "crawl", "hslatest", "--nolog"])
		if mode == "all":
			output = subprocess.run(["scrapy", "crawl", "hslatest", "-a", "mode=all"])
		else:
			output = subprocess.run(["scrapy", "crawl", "hslatest", "-a", "mode=normal"])

#Upon request from client, sends response. Else, keep scraping
def sendResponse():
	global BUFFSIZE
	global ACTIVE
	global LAST_REFRESH

	#Opens TCP ipv4 socket on specified port and host
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((socket.gethostname(), 6969))
	s.listen(5)

	#Local time
	local_datetime = datetime.datetime.now()
	local_time =  local_datetime.ctime().split()[3]

	readable, writable, errored = select.select([s], [], [], 2)

	print("Checking for connection from client")
	if s in readable:
		clientsocket, address = s.accept()
		print("Connected to a client")
		#Connection history is stored in log file
		with open("data/LogFile.txt", "a") as log:
			log.write("{} connected! on {} \n".format(address, local_datetime))
		
		client_msg = clientsocket.recv(BUFFSIZE).decode('utf-8')

		#If send-status ping is received, IST and PDT is sent along with activity status
		if client_msg == "send-status":
			time = "Local Time: {}\n".format(local_time)
			clientsocket.send(bytes(time, 'utf-8'))
			if LAST_REFRESH != "":
				clientsocket.send(bytes("Last Refresh: {} \n".format(LAST_REFRESH), 'utf-8'))

			if ACTIVE == True:
				clientsocket.send(bytes("Umaru-chan is working hard! \n", 'utf-8'))
			else:
				clientsocket.send(bytes("All done for the day! \n", 'utf-8'))
	s.close()

#Main process	
def main():
	global ACTIVE
	global INTERVAL

	data = getData()
	schedule = data['timetable']
	season = data['current_season']

	#Correct watchlist by passing through fuzzyset
	setCorrectWatchlist(season)
	#Check if the download status of shows needs to be reset
	resetDownloadStatus()

	config = readConfig()
	watchlist = config['watchlist']

	#Check all anime once
	checkNewAndDownload("all")
	start = time.monotonic()

	#Check if anime is in schedule and value is False(default), download
	#Set to time-stamp value when episode is downloaded
	#Reset Time-stamp value to 0 after 24 hours	
	for show in watchlist.keys():
		if show in schedule:
			print("\033[92m[+] {} is airing today!\033[0m".format(show))
			if watchlist[show][1] == "False":
				watchlist[show][1] = "-1"
			else:
				print("\033[91m[-] {} has already been downloaded! Ignored.\033[0m".format(show))

	#Shows to be check are marked with -1, dump new updated data
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

	while True:
		#sendResponse()
		#Download episodes of anime marked as -1 every INTERVAL
		if ACTIVE:
			start = time.monotonic()
			ACTIVE = False
			checkNewAndDownload()
			print("\033[92m[*] Server is running!\033[0m \033[95m[{}]\033[0m".format(str(datetime.datetime.now())[11:19]))

		now = time.monotonic()	
		if now - start >= INTERVAL:
			ACTIVE = True

		#Close if done for the day
		shouldQuit = 1
		for show in watchlist.keys():
			if watchlist[show][1] == "-1":
				shouldQuit = 0
		if shouldQuit:
			print("\033[92m[*] Done for today!\033[0m")
			break

if __name__ == "__main__":
	try:
		config = readConfig()
		if config["main"]["torrent"] == "":
			print("\033[91mTorrent download directory not set! Set by running client.py with -t/--torrent\033[0m")
		elif config["main"]["quality"] == "":
			print("\033[91mDownload quality not set! Set by running client.py with -q/--quality\033[0m")
		elif not config["watchlist"]:
			print("\033[91mWatchlist is empty! Add shows by running client.py with -a/--add option\033[0m")
		else:
			main()

	except KeyboardInterrupt:
		print("\n\033[91mKeyboard Interrupt Detected. Exiting.\033[0m")