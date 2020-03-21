#!/usr/bin/env python3
import socket
import os
import datetime
import pytz
import subprocess
import json
import pickle
import fuzzyset
import sched, time
from downloader.downloader import items
from downloader.downloader.spiders import anime_downloader as ad

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
	if (os.path.exists("data/watchlist.txt")):
		with open("data/watchlist.txt", 'r') as file:
			watchlist = file.read().split('\n')
	else:
		with open("data/watchlist.txt", 'w') as file:
			watchlist = file.read().split('\n')	
	return watchlist[:-1]

#Gets scraped data from the data directory
def getSchedule():
	with open('data/data.json') as d:
		data = json.load(d)
	
	#Dictionary of today's shows and their timings	
	schedule = data[0]['timetable']
	return schedule

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
				
			#If show-watchlist ping is received, watchlist is sent to the client	
			elif client_msg == "show-watchlist":
				watchlist = pickle.dumps(getWatchlist())
				clientsocket.send(watchlist)

			#If a login header is found in the message, user and pass is extracted and stored in secrets.py	
			elif client_msg[:5] == "login":
				u = client_msg[5:].split(':')[0]
				p = client_msg[5:].split(':')[1]

				with open("data/secrets.py", 'w') as secrets:
					secrets.write("_id = \"{}\"\n".format(u))
					secrets.write("_pass = \"{}\"\n".format(p))

				clientsocket.send(bytes("MAL Login ID set! Check secret.py.\n", 'utf-8'))
				clientsocket.send(bytes("Auto list-updation is on. Don't forget to add anime to your 'Watching' list on MAL!\n", 'utf-8'))

			#If path header is found, set path	
			elif client_msg[:4] == "path":
				PATH = client_msg[4:]
				with open("data/path.txt", "w") as path:
					path.write(PATH)
				clientsocket.send(bytes("Default download directory set! \n", 'utf-8'))

			#If a refresh ping is received, database is refreshed by calling scrapy	
			elif client_msg == "refresh":
				with cd("data"):
					if os.path.exists("data.json"):
						#Remove current data.json
						os.remove("data.json")

				#Change to scrapy directory
				with cd("downloader/downloader"):
					#Runs scrapy; remove the --nolog option to see logs in server.py output
					subprocess.run(["scrapy", "crawl", "anime", "-o", "../../data/data.json", "--nolog"])

				LAST_REFRESH = local_datetime.ctime()	
				clientsocket.send(bytes("Database refreshed successfully!\n", 'utf-8'))

			#If no incoming message, close socket and break	
			else:
				break

	# except socket.error:
	# 	print("Socket error detected!")

	except KeyboardInterrupt:
		print("\nKeyboard Interrupt Detected!")

#Main process - runs forever once started	
while True:
	schedule = getSchedule()
	watchlist = getWatchlist()
	#Loop through the watchlist
	for show in watchlist:
		#Take one show at a time and add to fuzzyset
		fs = fuzzyset.FuzzySet()
		fs.add(show)
		tmp = []
		#Loop through today's schedule and fuzzy match each key to show in watchlist
		for key in schedule.keys():
			tmp.append(fs.get(key))
		if max(tmp)[0] >= 0.8
		show = max(tmp)[0]
		#Check if the show is out yet
		if timeCompare(schedule[show]):
			#Start scraping every 10 minutes
		else:
			continue
			#Do nothing and wait
	sendResponse()				