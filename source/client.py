#!/usr/bin/env python3
import colorama
import socket
import os
import sys
import subprocess
import argparse
import json
import colorama

colorama.init()

BUFFSIZE = 2048
colorama.init()

#Opens and reads the config file
def readConfig():
	with open('data/config.json', 'r+') as f:
		config = json.load(f)
	return config	

#Shows the status
def status():
	global BUFFSIZE
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((socket.gethostname(), 6969))
		s.settimeout(2)

		while True:
			#Send ping request to show status
			status_ping = "send-status".encode('utf-8')
			s.send(status_ping)

			try:
				msg = s.recv(BUFFSIZE).decode('utf-8')
				print(msg, end='')
			except socket.timeout:
				break

	except socket.error:
		print("\033[91mConnection Error!\033[0m")

	finally:
		s.close()

#Refreshed database
def refresh():
	global BUFFSIZE
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((socket.gethostname(), 6969))
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

	except socket.error:
		print("\033[91mConnection Error!\033[0m")

	finally:
		s.close()

#Prints out the watchlist
def showList():
	config = readConfig()
	watchlist = config['watchlist']

	if not watchlist:
		print("\033[91mYour Watchlist is empty! Add shows using -a/--add <name>!\033[0m")
	else:
		print("\033[92mYour Watchlist:\033[0m")
		for i,show in enumerate(watchlist):
			print("{}:\033[93m {}\033[0m".format(i, show))

#Add shows to watchlist
def addShows(showlist):
	config = readConfig()
	for show in showlist:
		#Takes show name from the argument before the ":" and the latest ep number after the ":"
		if show.find(":") == -1:
			config['watchlist'][show] = "0"
		else:
			config['watchlist'][show[:show.index(":")]] = show[(show.index(":")+1):]
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)	

	print("\033[92mShows added succesfully! Use -l/--list to see your watchlist.\033[0m")

#Deletes selected show from watchlist
def deleteShows(numlist):
	config = readConfig()
	if not config['watchlist']:
		print("\033[91mYour Watchlist is empty! Add shows using -a/--add <name>!\033[0m")
	else:
		keylist = list(config['watchlist'].keys())
		for i in numlist:
			print("\033[93m{}\033[0m".format(keylist[int(i)]))
			del config['watchlist'][keylist[int(i)]]
		with open("data/config.json", "w") as f:	
			json.dump(config, f, indent=4)

		print("The following shows have been deleted from the watchlist")

#Clears Config
def clearConfig():
	#Defining default config
	def_config = {"main":{"path":"","torrent":"","quality":"","username":"","password":""},"watchlist":{}}
	with open("data/config.json", "w") as f:
		json.dump(def_config, f, indent=4)

	print("\033[92mConfig has been reset.\033[91m")

#Clears watchlist
def clearList():
	config = readConfig()
	def_list = {"main":config['main'],"watchlist":{}}
	with open("data/config.json", "w") as f:
		json.dump(def_list, f, indent=4)

	print("\033[92mYour watchlist has been reset. Use -a/--add to add shows!\033[91m")

#Sets watch/anime library path
def setPATH(PATH):
	config = readConfig()
	config['main']['path'] = PATH
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)
	
	print("\033[92mDefault anime watching directory set!\033[0m")

#Sets path for downloading torrent files
def setTorrentPATH(PATH):
	config = readConfig()
	config['main']['torrent'] = PATH
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)
	
	print("\033[92mDefault download directory for torrent files set!\033[0m")

#Sets quality for downloads
def setQuality(Q):
	config = readConfig()
	config['main']['quality'] = Q
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

	print("\033[92mQuality of downloads set to\033[0m \033[95m{}\033[0m".format(Q))

#Sets login id and password for MAL account
def setMAL(username, password):
	config = readConfig()
	config['main']['username'] = username
	config['main']['password'] = password
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)
	
	print("\033[92mMAL Login ID set! Check secret.py.\033[0m")
	print("\033[92mAuto list-updation is on. Don't forget to add anime to your 'Watching' list on MAL!\033[0m")

parser = argparse.ArgumentParser(description="Command-line interface for Umaru-chan.")
parser.add_argument('-a', '--add', nargs='+', help="Adds shows to the watchlist", metavar=("NAME"))
parser.add_argument('-d', '--delete', nargs='+', help="Removes one or more shows from the watchlist", metavar=("No."))
parser.add_argument('-l', '--list', help="Displays current set watchlist.", action='store_true')
parser.add_argument('-cc', '--clr-config', help="Clears config", action='store_true')
parser.add_argument('-cl', '--clr-list', help="Clears watchlist", action='store_true')
parser.add_argument('-w', '--watch', help="Watch anime.", action='store_true')
parser.add_argument('-p', '--path', nargs=1, help="Sets default watch directory/anime library.", metavar=("PATH"))
parser.add_argument('-t', '--torrent', nargs=1, help="Sets default download directory for torrent files.", metavar=("DIR"))
parser.add_argument('-q', '--quality', nargs=1, help="Sets quality of downloads (720p/1080p)", metavar=("QUAL"))
parser.add_argument('-m', '--mal-id', nargs=2, help="Sets username and password of MyAnimeList account.")
parser.add_argument('-s', '--status', help="Displays current status.",action='store_true')
parser.add_argument('-r', '--refresh', help="Refreshes database.", action='store_true')
args = parser.parse_args()

try:
	if args.watch:
		exec(open('watch.py').read())
	elif args.path != None:
		setPATH(args.path[0])
	elif args.torrent != None:
		setTorrentPATH(args.torrent[0])
	elif args.quality != None:
		setQuality(args.quality[0])
	elif args.mal_id != None:
		setMAL(args.mal_id[0], args.mal_id[1])
	elif args.add != None:
		addShows(args.add)
	elif args.delete != None:
		deleteShows(args.delete)
	elif args.list:
		showList()
	elif args.clr_config:
		clearConfig()
	elif args.clr_list:
		clearList()
	elif args.status:
		status()
	elif args.refresh:
		refresh()
	else:
		print("\033[91mAtleast one argument is required!\033[0m")
		parser.print_help()

except KeyboardInterrupt:
	print("\n\033[91mKeyboard Interrupt Detected!\033[0m")

except json.decoder.JSONDecodeError:
	print("\033[91mConfig file got corrupted! Try -cl/--clr-list to reset watchlist or -cc/clr-config to reset config if the former doesn't work.\033[0m")