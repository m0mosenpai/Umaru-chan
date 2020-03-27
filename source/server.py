#!/usr/bin/env python3
import socket
import os
import datetime
import pytz
import subprocess
import json
import fuzzyset
import time

BUFFSIZE = 2048
ACTIVE = True
LAST_REFRESH = ""

#A context manager class which changes the working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#PDT time for HorribleSubs
def getPDT():
	pst_timezone = pytz.timezone("US/Pacific")
	pdt = datetime.datetime.now(pst_timezone).time()
	return pdt

#Compare showtime and PDT
def timeCompare(showtime):
	pdt = getPDT()
	pdth = 	pdt.hour
	pdtm = pdt.minute
	sth = showtime.split(':')[0]
	stm = showtime.split(':')[1]

	if pdth > sth:
		return False
	elif pdth == sth:
		if pdtm >= stm:
			return False
		else:
			return True
	else:
		return True

#Read watchlist from watchlist file
def getWatchlist():
	with open('data/config.json', 'r+') as f:
		config = json.load(f)
		watchlist = config['watchlist']
	return watchlist

#Gets scraped data from the data directory
def getShows():
	#Change to scrapy directory
	with cd("downloader/downloader"):
		#Runs scrapy; remove the --nolog option to see logs in server.py output
		subprocess.run(["scrapy", "crawl", "anime", "--nolog"])

	with open('data/data.json') as d:
		data = json.load(d)

	#Dictionary with entire data
	return data

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

	try:
		while True:
			#Local time
			local_datetime = datetime.datetime.now()
			local_time =  local_datetime.ctime().split()[3]

			clientsocket, address = s.accept()
			#Connection history is stored in log file
			with open("data/LogFile.txt", "a") as log:
				log.write("{} connected! on {} \n".format(address, local_datetime))
			
			client_msg = clientsocket.recv(BUFFSIZE).decode('utf-8')

			#If send-status ping is received, IST and PDT is sent along with activity status
			if client_msg == "send-status":
				time = "Local Time: {}	PDT: {} \n".format(local_time, getPDT())
				clientsocket.send(bytes(time, 'utf-8'))
				if LAST_REFRESH != "":
					clientsocket.send(bytes("Last Refresh: {} \n".format(LAST_REFRESH), 'utf-8'))

				if ACTIVE == True:
					clientsocket.send(bytes("Umaru-chan is working hard! \n", 'utf-8'))
				else:
					clientsocket.send(bytes("All done for the day! \n", 'utf-8'))

			#If a refresh ping is received, database is refreshed by calling scrapy	
			elif client_msg == "refresh":
				if os.path.exists("data/data.json"):
					#Remove current data.json
					os.remove("data/data.json")

				#Change to scrapy directory
				with cd("downloader/downloader"):
					#Runs scrapy; remove the --nolog option to see logs in server.py output
					subprocess.run(["scrapy", "crawl", "anime", "-o", "../../data/data.json", "--nolog"])

				LAST_REFRESH = local_datetime.ctime()	
				clientsocket.send(bytes("\033[92mDatabase refreshed successfully!\033[0m\n", 'utf-8'))

			#If no incoming message, close socket and break	
			else:
				break

	# except socket.error:
	# 	print("Socket error detected!")

	except KeyboardInterrupt:
		print("\n\033[91mKeyboard Interrupt Detected!\033[0m")

def checkNewAndDownload():
	with cd("downloader/downloader"):
		output = subprocess.run(["scrapy", "crawl", "hslatest", "--nolog"])

#Main process - runs forever once started	
interval = 6000 #in seconds
should_check = True
while True:
	if should_check is True:
		start = time.monotonic()

	#Run below every 10 mins
	if (should_check):
		#print("PRINT!")
		should_check = False
		data = getShows()
		watchlist = getWatchlist()
		nums = list(watchlist.values())
		shows = watchlist.keys()
		#print('Watchlist as entered by the baka user: {}'.format(watchlist))
		#Loop through the watchlist
		season_fset = fuzzyset.FuzzySet()
		#Add all shows in current season to fuzzy set
		for show in data["current_season"]:
			season_fset.add(show)

		#Get actual watchlist (Names according to hs)
		f_watchlist = {}

		i = 0
		for show in shows:
			# print(type(season_fset.get(show)))
			f_watchlist[season_fset.get(show)[0][1]] = nums[i]
			i += 1

		#print('Correct watchlist: {}'.format(f_watchlist))

		with open('data/config.json', 'r+') as f:
			config = json.load(f)
			config['watchlist']= f_watchlist
			f.seek(0)
			json.dump(config, f, indent=4)

		local_datetime = datetime.datetime.now()
		local_time =  local_datetime.ctime().split()[3]
		print('Server is running! [{}]'.format(local_time))

		#last ep downloaded data
		#last_down
		# if os.path.exists('data/last_down.json') is False:
		# 	with open('data/last_down.json', 'w') as f:
		# 		json.dump(last_down, f)
		# with open('data/last_down.json', 'r') as f:
		# 	last_down = json.load(f)

		#print(getListOfNewEps())
		#Download if new ep is found
		checkNewAndDownload() #This function will return the latest ep no. of all shows in watchlist
		#shows_download = getShowsToDown(new_ep_num, f_watchlist) #Compare and find which shows to download
		#downloadShows(shows_download)

		#print(new_ep_num)

	now = time.monotonic()
	if (now - start > interval):
		should_check = True

	#break
	
	#sendResponse()