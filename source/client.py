#!/usr/bin/env python3
import colorama
import socket
import select
import os
import sys
import subprocess
import argparse
import json
import colorama
import platform

BUFFSIZE = 2048
colorama.init()

#A context manager class which changes the working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#Opens and reads the config file
def readConfig():
	with open('data/config.json', 'r+') as f:
		config = json.load(f)
	return config

#Makes quueue for downloadShow
def makeQueue(aname, start, end, release="horriblesubs"):
	return [aname, start, end, release]

#Shows the status
def status():
	global BUFFSIZE

	config = readConfig()
	path = config['main']['path']
	torrent_path = config['main']['torrent']
	qual = config['main']['quality']
	U = config['main']['username']
	P = config['main']['password']

	print("-------------------------------------")
	print("\033[92m###VARIABLES SET###\033[0m")
	print("")
	print("\033[93mWatching Directory:\033[0m \033[95m{}\033[0m".format(path))
	print("\033[93mTorrent Download Directory:\033[0m \033[95m{}\033[0m".format(torrent_path))
	print("\033[93mQuality of Downloads:\033[0m \033[95m{}\033[0m".format(qual))
	print("\033[93mMAL Username:\033[0m \033[95m{}\033[0m".format(U))
	print("\033[93mMAL Password:\033[0m \033[95m{}\033[0m".format(P))
	print("-------------------------------------")
	print("\033[92m###SERVER STATUS###\033[0m")
	print("")

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((socket.gethostname(), 6969))
		s.settimeout(2)

		#Send ping request to show status
		status_ping = "send-status".encode('utf-8')
		s.send(status_ping)

		while True:
			msg = s.recv(BUFFSIZE).decode('utf-8')
			if len(msg) == 0:
				break
			print(msg, end='')

	except socket.error:
		print("\033[91mConnection Error!\033[0m")

	finally:
		s.close()

	print("-------------------------------------")

#Prints out the watchlist
def showList():
	config = readConfig()
	watchlist = config['watchlist']

	if not watchlist:
		print("\033[91mYour Watchlist is empty! Add shows using -a/--add <name>!\033[0m")
	else:
		watchlist = list(watchlist)
		watchlist.sort()
		print("\033[92mYour Watchlist:\033[0m")
		for i,show in enumerate(watchlist):
			print("{}:\033[93m {}\033[0m".format(i+1, show))

#Add shows to watchlist
def addShows(showlist):
	config = readConfig()
	for show in showlist:
		#Takes show name from the argument before the ":" and the latest ep number after the ":"
		if show.find(":") == -1:
			config['watchlist'][show] = ["0"]
			config['watchlist'][show].append("False")
		else:
			config['watchlist'][show[:show.index(":")]] = [show[(show.index(":")+1):]]
			config['watchlist'][show[:show.index(":")]].append("False")

	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)	

	print("\033[92mShows added succesfully! Use -l/--list to see your watchlist.\033[0m")

#Deletes selected show from watchlist
def removeShows(numlist):
	config = readConfig()
	#Check if show index is out of bounds
	for num in numlist:
		if num > len(config['watchlist']):
			print("\033[91mThere are only {} shows in your watchlist!\033[0m".format(len(config['watchlist'])))
			return
	#Check if watchlist is empty		
	if not config['watchlist']:
		print("\033[91mYour Watchlist is empty! Add shows using -a/--add <name>!\033[0m")
	#Sort and remove
	else:
		keylist = list(config['watchlist'].keys())
		keylist.sort()
		for i in numlist:
			print("\033[93m{}\033[0m".format(keylist[int(i-1)]))
			del config['watchlist'][keylist[int(i-1)]]

		with open("data/config.json", "w") as f:	
			json.dump(config, f, indent=4)
		print("The following shows have been deleted from the watchlist")

#Download specified show
def downloadShow(showinfo):
	if len(showinfo) < 3:
		print("\033[91mRequires atleast 3 arguments! [name, start, end]\033[0m")
		return
	elif len(showinfo) > 4:
		print("\033[91mToo many arguments - 3 required [name, start, end], 1 optional [release]\033[0m")
		return
	else:
		aname = showinfo[0]
		start = showinfo[1]
		end = showinfo[2]
		if len(showinfo) == 4:
			release = showinfo[3]		
			queue = makeQueue(aname, start, end, release)
		else:
			queue = makeQueue(aname, start, end)

	if not os.path.isdir("tmp"):
		os.mkdir("tmp")
	with open("tmp/tmp_queue.json", 'w+') as f:
		json.dump(queue, f, indent=4)

	config = readConfig()
	if config["main"]["torrent"] == "":
		print("\033[91mTorrent download directory not set! Set by running client.py with -t/--torrent\033[0m")
	elif config["main"]["quality"] == "":
		print("\033[91mDownload quality not set! Set by running client.py with -q/--quality\033[0m")
	else:	
		with cd("downloader/downloader"):
			subprocess.run(["scrapy", "crawl", "show", "--nolog"])

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

	#Check for a trailing slash based on platform
	if platform.system() == "Linux":
		if PATH[-1] != "/":
			PATH = PATH + "/"
	if platform.system() == "Windows":
		if PATH[-1] != "\\":
			PATH = PATH + "\\"

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
parser.add_argument('-a', '--add', nargs='+', help="Adds shows to the watchlist.", metavar=("NAME"))
parser.add_argument('-r', '--remove', nargs='+', help="Removes one or more shows from the watchlist based on their index value.", metavar=("NUM"), type=int)
parser.add_argument('-l', '--list', help="Displays current set watchlist.", action='store_true')
parser.add_argument('-cc', '--clr-config', help="Clears config.", action='store_true')
parser.add_argument('-cl', '--clr-list', help="Clears watchlist.", action='store_true')
parser.add_argument('-w', '--watch', help="Watch anime from your local library.", action='store_true')
parser.add_argument('-p', '--path', nargs=1, help="Sets default watch directory/anime library.", metavar=("PATH"))
parser.add_argument('-t', '--torrent', nargs=1, help="Sets default download directory for torrent files.", metavar=("DIR"))
parser.add_argument('-q', '--quality', nargs=1, help="Sets quality of downloads (480p/720p/1080p)", metavar=("QUAL"))
parser.add_argument('-m', '--mal-id', nargs=2, help="Sets username and password of MyAnimeList account.", metavar=("USER", "PASS"))
parser.add_argument('-d', '--download', nargs='+', help="Downloads a full show or specified range of episodes.")
parser.add_argument('-s', '--status', help="Displays current client and server status.", action='store_true')
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
	elif args.remove != None:
		removeShows(args.remove)
	elif args.download != None:
		downloadShow(args.download)
	elif args.list:
		showList()
	elif args.clr_config:
		clearConfig()
	elif args.clr_list:
		clearList()
	elif args.status:
		status()
	else:
		print("\033[91mAtleast one argument is required!\033[0m")
		parser.print_help()

except KeyboardInterrupt:
	print("\n\033[91mKeyboard Interrupt Detected!\033[0m")

except json.decoder.JSONDecodeError:
	print("\033[91mConfig file got corrupted! Try -cl/--clr-list to reset watchlist or -cc/clr-config to reset config if the former doesn't work.\033[0m")