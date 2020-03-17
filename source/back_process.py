#!/usr/bin/env python3
import socket
import os
import datetime
import pytz
from downloader.downloader import items
from downloader.downloader.spiders import anime_downloader, mal_updater

BUFFSIZE = 2048
ACTIVE = False
path = ''

#Read watchlist from watchlist file
def getWatchlist():
	with open("watchlist.txt", 'r') as file:
		watchlist = file.read().split('\n')
	return watchlist[:-1]

def getPDT():
	#PDT time for HorribleSubs
	pst_timezone = pytz.timezone("US/Pacific")
	pdt = datetime.datetime.now(pst_timezone).time()
	return pdt

#Opens TCP ipv4 socket on specified port and host
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

	if client_msg == "send-status":
		time = "Local Time: {}	PDT: {} \n".format(local_datetime, getPDT())
		clientsocket.send(bytes(time, 'utf-8'))
		if ACTIVE == True:
			clientsocket.send(bytes("Umaru-chan is working hard! \n", 'utf-8'))
		else:
			clientsocket.send(bytes("All done for the day! \n", 'utf-8'))
		
	if client_msg == "show-watchlist":
		clientsocket.send(bytes("Your Watchlist: \n", 'utf-8'))
		watchlist = getWatchlist()

	#if client_msg == "refresh-list":
		