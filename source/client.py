#!/usr/bin/env python3
import socket
import os
import sys
import subprocess
import argparse
import pickle

BUFFSIZE = 2048

def status(s):
	while True:
		#Send ping request to show status
		status_ping = "send-status".encode('utf-8')
		s.send(status_ping)

		try:
			msg = s.recv(BUFFSIZE).decode('utf-8')
			print(msg, end='')
		except socket.timeout:
			break

def watchlist(s):
	while True:
		#Send ping request to show watchlist
		watchlist_ping = "show-watchlist".encode('utf-8')
		s.send(watchlist_ping)

		try:
			msg = s.recv(BUFFSIZE) 
			watchlist = pickle.loads(msg)
			print("Your Watchlist:\n {}".format(watchlist))
		except socket.timeout:
			break

def refresh(s):
	s.settimeout(5)
	while True:
		#Send ping request to refresh watchlist
		refresh_ping = "refresh".encode('utf-8')
		s.send(refresh_ping)

		try:
			msg = s.recv(BUFFSIZE).decode('utf-8')
			print(msg, end='')
		except socket.timeout:
			break

def setPATH(PATH):
	with open("data/path.txt", "w+") as path:
		path.write(PATH)
	print("\033[92mDefault download directory set!\033[0m")

def setMAL(username, password):
	#Send login credentials to server by prepending login header
	with open("data/secrets.py", 'w') as secrets:
		secrets.write("_id = \"{}\"\n".format(username))
		secrets.write("_pass = \"{}\"\n".format(password))
	print("\033[92mMAL Login ID set! Check secret.py.\033[0m")
	print("\033[92mAuto list-updation is on. Don't forget to add anime to your 'Watching' list on MAL!\033[0m")

parser = argparse.ArgumentParser(description="Command-line interface for Umaru-chan.")
parser.add_argument('-s', '--status', help="Displays current status.",action='store_true')
parser.add_argument('-l', '--list', help="Displays current set watchlist.", action='store_true')
parser.add_argument('-m', '--mal-id', nargs=2, help="Sets username and password of MyAnimeList account.")
parser.add_argument('-r', '--refresh', help="Refreshes database.", action='store_true')
parser.add_argument('-p', '--path', nargs=1, help="Sets default download directory.", metavar=("PATH"))
parser.add_argument('-w', '--watch', help="Watch anime.", action='store_true')
args = parser.parse_args()

if args.watch:
	exec(open('watch.py').read())
elif args.path != None:
	setPATH(args.path[0])
elif args.mal_id != None:
	setMAL(args.mal_id[0], args.mal_id[1])
else:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((socket.gethostname(), 6969))
		s.settimeout(2)

		if args.status:
			status(s)
		elif args.list:
			watchlist(s)
		elif args.refresh:
			refresh(s)
		else:
			print("\033[91mAtleast one argument is required!\033[0m")
			parser.print_help()

	except KeyboardInterrupt:
		print("\n\033[91mKeyboard Interrupt Detected!\033[0m")

	except socket.error:
		print("\033[91mConnection Error!\033[0m")

	finally:
		s.close()