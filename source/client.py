#!/usr/bin/env python3
import socket
import os

BUFFSIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 6969))

while True:
	intro_msg = s.recv(BUFFSIZE).decode('utf-8')
	print(intro_msg)
	print(" ")

	print("1. Show Status")
	print("2. Edit/Update Watchlist")
	print("3. Let her concentrate on her work")
	choice = input("What do you want her to do?")

	if choice == '1':
		os.system('clear')
		#Send ping request to show status
		status_ping = "send-status".encode('utf-8')
		s.send(status_ping)

		#Receive data
		status = s.recv(BUFFSIZE).decode('utf-8')
		print(status)

	elif choice == '2':
		os.system('clear')
		#Send ping request to show watchlist
		watchlist_ping = "show-watchlist".encode('utf-8')
		s.send(watchlist_ping)

		#Receive data
		watchlist = s.recv(BUFFSIZE).decode('utf-8')
		print(watchlist)

	elif choice == '3':
		exit()
	else:
		print("???? Be more specific!")
		continue