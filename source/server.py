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
import platform
import logging

logging.basicConfig(filename="data/serverlog.log",level=logging.DEBUG,format="[%(asctime)s][%(levelname)s]:%(message)s",
	datefmt="%Y-%m-%d %H:%M:%S")
logging.getLogger('scrapy').propagate = False

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
	logging.info("Attempting to read config.json")
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
		if fset.get(show)[0][0] >= 0.48:
			fset_watchlist[fset.get(show)[0][1]] = watchlist[show]
		else:
			print("\033[91m[-] {} does not seem to be airing this season! Ignoring..\033[0m".format(show))

	config['watchlist'] = fset_watchlist
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

#Calls Scrapy and downloads the episodes
def checkNewAndDownload(mode = "normal"):
	with cd("downloader/downloader"):
		if mode == "all":
			output = subprocess.run(["scrapy", "crawl", "hslatest", "-a", "mode=all", "--nolog"])
			#output = subprocess.run(["scrapy", "crawl", "hslatest", "-a", "mode=all"])
		else:
			output = subprocess.run(["scrapy", "crawl", "hslatest", "-a", "mode=normal", "--nolog"])
			#output = subprocess.run(["scrapy", "crawl", "hslatest", "-a", "mode=normal"])

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

# Convert name of day to a number
dayMapping = {
	"monday": 0,
	"tuesday": 1,
	"wednesday": 2,
	"thursday": 3,
	"friday": 4,
	"saturday": 5,
	"sunday": 6
}

#Main process
def main():
	logging.info("\nStarting server")
	global ACTIVE
	global INTERVAL

	#Check if the download status of shows needs to be reset
	resetDownloadStatus()

	#Check all anime once
	print("[*] Performing initial check.")
	time.sleep(1)
	print("[*] Getting you up-to date.")
	checkNewAndDownload("all")
	#pdb.set_trace()
	time.sleep(2)

	config = readConfig()
	watchlist = config['watchlist']

	start = time.monotonic()
	print("\033[95m[{}]\033[0m".format(str(datetime.datetime.now())[11:19]))

	day = dayMapping[datetime.datetime.today().strftime("%A").lower()]

	#Check if anime's airing day is today (local system time) and value is False(default), download
	#Set to time-stamp value when episode is downloaded
	for show in watchlist.keys():
		if watchlist[show][2][0] == day:
			print("\033[92m[+] {} is airing today!\033[0m".format(show))
			if watchlist[show][1] == "False":
				watchlist[show][1] = "-1"
			else:
				print("\033[91m[-] {} has already been downloaded! Ignored.\033[0m".format(show))

	#Shows to be check are marked with -1, dump new updated data
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

	shouldQuit = 0
	while not shouldQuit:
		#sendResponse()
		#Download episodes of anime marked as -1 every INTERVAL
		if ACTIVE:
			start = time.monotonic()
			ACTIVE = False
			print("\033[95m[{}]\033[0m".format(str(datetime.datetime.now())[11:19]))
			checkNewAndDownload()
			config = readConfig()
			watchlist = config['watchlist']

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