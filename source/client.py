#!/usr/bin/env python3
import socket
import os
import sys
import argparse
import pickle

BUFFSIZE = 2048

def status(s):
	while True:
		#Send ping request to show status
		status_ping = "send-status".encode('utf-8')
		s.send(status_ping)

		msg = s.recv(BUFFSIZE).decode('utf-8')
		print(msg, end='')

def watchlist(s):
	while True:
		#Send ping request to show watchlist
		watchlist_ping = "show-watchlist".encode('utf-8')
		s.send(watchlist_ping)

		msg = s.recv(BUFFSIZE) 
		watchlist = pickle.loads(msg)
		print("Your Watchlist:\n {}".format(watchlist), end='')

def refresh(s):
	while True:
		#Send ping request to refresh watchlist
		refresh_ping = "refresh".encode('utf-8')
		s.send(refresh_ping)

		msg = s.recv(BUFFSIZE).decode('utf-8')
		print(msg, end='')

def setPATH(s, directory):
	while True:
		#Send path to server by prepending path header
		path = 'path' + directory
		s.send(path.encode('utf-8'))

		msg = s.recv(BUFFSIZE).decode('utf-8')
		print(msg, end='')

def setMAL(s, username, password):
	while True:	
		#Send login credentials to server by prepending login header
		cred = 'login' + username + ':' + password
		s.send(cred.encode('utf-8'))

		msg = s.recv(BUFFSIZE).decode('utf-8')
		print(msg, end='')

parser = argparse.ArgumentParser(description="Command-line interface for Umaru-chan")
parser.add_argument('-s', '--status', help="Displays current status.",action='store_true')
parser.add_argument('-w', '--watchlist', help='Displays current set watchlist', action='store_true')
parser.add_argument('-m', '--mal-id', nargs=2, help="Sets username and password of MyAnimeList account")
parser.add_argument('-r', '--refresh', help="Refreshes database", action='store_true')
parser.add_argument('-p', '--path', nargs=1, help="Sets default download directory.", metavar=("PATH"))
args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 6969))

try:
	if args.status:
		status(s)
	elif args.watchlist:
		watchlist(s)
	elif args.refresh:
		refresh(s)
	elif args.path != None:
		setPATH(s, args.path[0])
	elif args.mal_id != None:
		setMAL(s, args.mal_id[0], args.mal_id[1])
	else:
		print("Atleast one argument is required!")
		parser.print_help()

except KeyboardInterrupt:
	print("\n")
	print("Keyboard Interrupt Detected!")

finally:
	print("Closing socket...")
	s.close()