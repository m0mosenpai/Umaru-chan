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
import malupdate as mal
import base64
import time
import fuzzyset

import server
import watch

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

#Check if username and password exist in config
def credentialCheck():
	with open("data/config.json", "r") as f:
		config = json.load(f)
	user = config['main']['username']
	passwd = base64.b64decode(bytes(config['main']['password'], "utf-8").decode("utf-8")).decode("utf-8")

	if user == "" or passwd == "":
		print("\033[91mUsername/Password not set! Run with -m/--mal-id to set one up!\033[0m")
		exit()
	else:
		return [user, passwd]

def login():
	# Get loginData from login json file
	with open("data/loginData.json", "r") as f:
		loginData = json.load(f)

	# if loginData is empty or it's been "expires_in" seconds (expiration of the access_token), do a fresh login
	if (not loginData) or ((time.time() - float(loginData['access_token'][1])) > float(loginData['expires_in'])):
		# Get login credentials from config
		info = credentialCheck()

		# Get loginInfo by logging in and add current timestamp to file
		loginInfo = mal.User.login(info[0], info[1])
		loginInfo['access_token'] = [loginInfo['access_token'], str(time.time())]

		with open("data/loginData.json", "w+") as f:
			json.dump(loginInfo, f, indent=4)
		AT = loginInfo['access_token'][0]

	# else, get the existing access_token from the json file
	else:
		credentialCheck()
		AT = loginData['access_token'][0]

	return AT

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

# Convert name of day to a number
dayMapping = {
	"monday": 0,
	"tuesday": 1,
	"wednesday": 2,
	"thursday": 3,
	"friday": 4,
	"saturday": 5,
	"sunday": 6
}

def getDayTimeAlt(AT, show):
	#Get broadcast time of show from MAL
	mal_watchlist = mal.User.getAnimeList(AT, "watching", ['broadcast', 'alternative_titles'])[0]["data"]

	fset = fuzzyset.FuzzySet()
	fset.add(show)
	max_prob, max_prob_idx = 0, 0

	for idx, item in enumerate(mal_watchlist):
		result = fset.get(item['node']['title'])
		current_prob = result[0][0] if result != None else 0
		if current_prob > max_prob:
			max_prob = current_prob
			max_prob_idx = idx

	if max_prob >= 0.6:
		day = dayMapping[mal_watchlist[max_prob_idx]['node']['broadcast']['day_of_the_week']]
		time = int(mal_watchlist[max_prob_idx]['node']['broadcast']['start_time'].replace(":", ""))

		#Converting day from JST to IST
		if(time <= 330):
			day = (day + 6) % 7

		hr = int(time / 100)
		mi = time % 100

		if mi < 30:
			hr = (hr + 20) % 24
		else:
			hr = (hr + 21) % 24

		mi = (mi + 30) % 60
		time = hr * 100 + mi

		#Get list of alternative titles
		alt_names = mal_watchlist[max_prob_idx]['node']['alternative_titles']['synonyms']
		alt_names.append(mal_watchlist[max_prob_idx]['node']['title'])
		return day, time, alt_names

	else:
		print("\033[91m[-] Anime not found in watchlist! Ignoring.\033[0m")
		return None, None, None

#Correct watchlist keys
def fixWatchlist():
	config = readConfig()

	print("[*] Looking for issues in watchlist.")
	at = login()

	#Add alternative titles key
	# 0 - Last downloaded episode number
	# 1 - timestamp/status
	# 2 - airing day/time
	# 3 - alternative titles

	for show in config['watchlist']:
		#Get broadcast time of show from MAL
		day, time, alt_names = getDayTimeAlt(at, show)
		if day == None and time == None and alt_names == None:
			continue

		if len(config['watchlist'][show]) == 2:
			#Append
			config['watchlist'][show].append([day, time])
			config['watchlist'][show].append(alt_names)

		elif len(config['watchlist'][show]) == 3:
			#Update
			config['watchlist'][show][2] = [day, time]
			#Append
			config['watchlist'][show].append(alt_names)

		elif len(config['watchlist'][show]) == 4:
			#Update
			config['watchlist'][show][2] = [day, time]
			config['watchlist'][show][3] = alt_names

	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

	print("\033[92m[+] Watchlist fixed! Use -l/--list to see your watchlist.\033[0m")

#Add shows to watchlist
def addShows(showlist):
	config = readConfig()

	print("[*] Getting anime info from MyAnimeList.")
	at = login()

	for show in showlist:
		#Takes show name from the argument before the ":" and the latest ep number after the ":"
		if show.find(":") != -1:
			config['watchlist'][show[:show.index(":")]] = [show[(show.index(":")+1):]]
			show = show[:show.index(":")]
		else:
			config['watchlist'][show] = ["0"]

		#Get broadcast time of show from MAL
		day, time, alt_names = getDayTimeAlt(at, show)
		if day == None and time == None and alt_names == None:
			continue

		config['watchlist'][show].append("False")
		config['watchlist'][show].append([day, time])
		config['watchlist'][show].append(alt_names)

	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

	print("\033[92m[+] Shows added succesfully! Use -l/--list to see your watchlist.\033[0m")

#Deletes selected show from watchlist
def removeShows(numlist):
	config = readConfig()
	#Check if show index is out of bounds
	for num in numlist:
		if num > len(config['watchlist']):
			print("\033[91m[-] There are only {} shows in your watchlist!\033[0m".format(len(config['watchlist'])))
			return
	#Check if watchlist is empty
	if not config['watchlist']:
		print("\033[91m[-] Your Watchlist is empty! Add shows using -a/--add <name>!\033[0m")
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
		print("\033[91m[-] Requires atleast 3 arguments! [name, start, end]\033[0m")
		return
	elif len(showinfo) > 4:
		print("\033[91m[-] Too many arguments - 3 required [name, start, end], 1 optional [release]\033[0m")
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

	print("\033[92m[*] Config has been reset.\033[91m")

#Clears watchlist
def clearList():
	config = readConfig()
	def_list = {"main":config['main'],"watchlist":{}}
	with open("data/config.json", "w") as f:
		json.dump(def_list, f, indent=4)

	print("\033[92m[*] Your watchlist has been reset. Use -a/--add to add shows!\033[91m")

#Sets watch/anime library path
def setPATH(PATH):
	config = readConfig()
	config['main']['path'] = PATH
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

	print("\033[92m[+] Default anime watching directory set!\033[0m")

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

	print("\033[92m[+] Default download directory for torrent files set!\033[0m")

#Sets quality for downloads
def setQuality(Q):
	config = readConfig()
	config['main']['quality'] = Q
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

	print("\033[92m[+] Quality of downloads set to\033[0m \033[95m{}\033[0m".format(Q))

#Sets login id and password for MAL account
def setMAL(username, password):
	config = readConfig()
	config['main']['username'] = username
	config['main']['password'] = base64.b64encode(password.encode("utf-8")).decode("utf-8")
	with open('data/config.json', 'w') as f:
		json.dump(config, f, indent=4)

	print("\033[92m[*] MAL Login ID set! Check secret.py.\033[0m")
	print("\033[92m[*] Auto list-updation is on. Don't forget to add anime to your 'Watching' list on MAL!\033[0m")

# Runs server
def execute():
	try:
		config = readConfig()
		if config["main"]["torrent"] == "":
			print("\033[91mTorrent download directory not set! Set by running client.py with -t/--torrent\033[0m")
		elif config["main"]["quality"] == "":
			print("\033[91mDownload quality not set! Set by running client.py with -q/--quality\033[0m")
		elif not config["watchlist"]:
			print("\033[91mWatchlist is empty! Add shows by running client.py with -a/--add option\033[0m")
		else:
			server.main()

	except KeyboardInterrupt:
		print("\n\033[91mKeyboard Interrupt Detected. Exiting.\033[0m")

# def main():
parser = argparse.ArgumentParser(description="Command-line interface for Umaru-chan.")
parser.add_argument('-e', '--execute', help="Starts main program.", action='store_true')
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
parser.add_argument('-f', '--fix', help="Fixes any issues in watchlist.", action='store_true')
args = parser.parse_args()
# print(args)

try:
	if args.watch:
		# exec(open('watch.py').read())
		watch.main()
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
	elif args.fix:
		fixWatchlist()
	elif args.execute:
		execute()
	else:
		print("\033[91mAtleast one argument is required!\033[0m")
		parser.print_help()

except KeyboardInterrupt:
	print("\n\033[91mKeyboard Interrupt Detected!\033[0m")

except json.decoder.JSONDecodeError:
	print("\033[91mConfig file got corrupted! Try -cl/--clr-list to reset watchlist or -cc/clr-config to reset config if the former doesn't work.\033[0m")

# if __name__ == "__main__":
# 	main()