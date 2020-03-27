#!/usr/bin/env python3
import socket
import os
import sys
import subprocess
import argparse
import json

BUFFSIZE = 2048

#Shows the status
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


#Refreshed database
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

#Prints out the watchlist
def watchlist():
	with open('data/config.json', 'r+') as f:
		config = json.load(f)
		watchlist = config['watchlist']

	if not watchlist:
		print("\033[91mYour Watchlist is empty! Add shows using -a/--add <name>!\033[0m")
	else:
		print("\033[92mYour Watchlist:\033[0m")
		for show in watchlist:
			print(show)

#Add shows to watchlist
def addShows(showlist):
	with open("data/config.json", "r+") as f:
		config = json.load(f)
		for show in showlist:
			print(show)
			config['watchlist'].append(show)
		f.seek(0)
		json.dump(config, f, indent=4)

	print("\033[92mShows added succesfully!\033[0m")

#Sets download path
def setPATH(PATH):
	with open("data/config.json", 'r+') as f:
		config = json.load(f)
		config['main']['path'] = PATH
		f.seek(0)
		json.dump(config, f, indent=4)
	
	print("\033[92mDefault download directory set!\033[0m")

#Sets login id and password for MAL account
def setMAL(username, password):
	with open("data/config.json", "r+") as f:
		config = json.load(f)
		config['main']['username'] = username
		config['main']['password'] = password
		f.seek(0)
		json.dump(config, f, indent=4)
	
	print("\033[92mMAL Login ID set! Check secret.py.\033[0m")
	print("\033[92mAuto list-updation is on. Don't forget to add anime to your 'Watching' list on MAL!\033[0m")

parser = argparse.ArgumentParser(description="Command-line interface for Umaru-chan.")
parser.add_argument('-a', '--add', nargs='+', help="Adds shows to the watchlist", metavar=("NAME"))
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
elif args.add != None:
	addShows(args.add)
elif args.list:
	watchlist()
else:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((socket.gethostname(), 6969))
		s.settimeout(2)

		if args.status:
			status(s)
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