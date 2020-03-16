#!/usr/bin/env python3
import socket
import os
import datetime
import pytz
from downloader.downloader import items
from downloader.downloader.spiders import anime_downloader

BUFFSIZE = 1024

watchlist = ["Ahiru no Sora", "Boku no Hero Academia"]
MAL_ID = {}
lib_path = ""

#Opens TCP ipv4 socket on specified port and host
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 6969))
s.listen(5)

#Local time
local_datetime = datetime.datetime.now()

#PDT time for HorribleSubs
pst_timezone = pytz.timezone("US/Pacific")
pdt_time = datetime.datetime.now(pst_timezone).time()


while True:
	clientsocket, address = s.accept()
	#Connection status is updated in log file
	with open("LogFile.txt", "a") as log:
		log.write("{} connected! on {} \n".format(address, local_datetime))
		
	clientsocket.send(bytes("Umaru-chan is working hard!", 'utf-8'))

	client_msg = clientsocket.recv(BUFFSIZE).decode('utf-8')
	if client_msg == "send-status":
		clientsocket.send(bytes("Current Status: ", 'utf-8'))
	if client_msg == "show-watchlist":
		clientsocket.send(bytes("Your Watchlist: ", 'utf-8'))
	