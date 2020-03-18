#!/usr/bin/env python3
import socket
import os
import datetime
import pytz
from downloader.downloader import items
from downloader.downloader.spiders import anime_downloader

BUFFSIZE = 2048
ACTIVE = False
path = ''

#Read watchlist from watchlist file
def getWatchlist():
	with open("watchlist.txt", 'r') as file:
		watchlist = file.read().split('\n')
	return watchlist[:-1]

#PDT time for HorribleSubs
def getPDT():
	pst_timezone = pytz.timezone("US/Pacific")
	pdt = datetime.datetime.now(pst_timezone).time()
	return pdt

def closeSocket():
	

#Opens TCP ipv4 socket on specified port and host
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((socket.gethostname(), 6969))
s.listen(5)

while True:
	#Local time
	local_datetime = datetime.datetime.now()

	clientsocket, address = s.accept()
	#Connection history is stored in log file
	with open("LogFile.txt", "a") as log:
		log.write("{} connected! on {} \n".format(address, local_datetime))
		
	client_msg = clientsocket.recv(BUFFSIZE).decode('utf-8')

	#If send-status ping is received, IST and PDT is sent along with activity status
	if client_msg == "send-status":
		time = "Local Time: {}	PDT: {} \n".format(local_datetime, getPDT())
		clientsocket.send(bytes(time, 'utf-8'))
		if ACTIVE == True:
			clientsocket.send(bytes("Umaru-chan is working hard! \n", 'utf-8'))
		else:
			clientsocket.send(bytes("All done for the day! \n", 'utf-8'))
		
	#If show-watchlist ping is received, watchlist is sent to the client	
	if client_msg == "show-watchlist":
		clientsocket.send(bytes("Your Watchlist: \n", 'utf-8'))
		watchlist = getWatchlist()

	#If a login header is found in the message, user and pass is extracted and stored in secrets.py	
	if client_msg[:5] == "login":
		u = client_msg[5:].split(':')[0]
		p = client_msg[5:].split(':')[1]

		with open("secrets.py", 'w') as secrets:
			secrets.write("_id = \"{}\"\n".format(u))
			secrets.write("_pass = \"{}\"\n".format(p))

		clientsocket.send(bytes("MAL Login ID set! Check secret.py.\n", 'utf-8'))
		clientsocket.send(bytes("Auto list-updation is on. Don't forget to add anime to your 'Watching' list on MAL!\n", 'utf-8'))
	
		