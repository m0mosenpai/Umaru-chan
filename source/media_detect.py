#!/usr/bin/env python3
import psutil
import platform
import malupdate as mal
import colorama
import re
import json
import time
import fuzzyset

colorama.init()

"""
Notes:
psutil.pid_exists(pid) - To detect whether a pid exists or not
Process.is_running() - Return whether the current process is running in the current process list.
						This is reliable also in case the process is gone and its PID reused by another process, therefore it
						must be preferred over doing psutil.pid_exists(p.pid).
"""
# Script Data
running = 1 # Whether the script should run
file_formats = [".mkv", ".mp4", ".ogg", ".avi", ".mov", ".wmv", ".mpeg"] #List of supported file formats
players = [] # Store all running media player processes
shouldPrint = True

# Media player Data
player_processes = ["vlc.exe", "vlc", "totem", "wmplayer.exe"] # List of supported media player processes
open_files = {}

# Makes a list of all the anime that need to be updated
def updateList(filename):
	toUpdate = input("[*] Update list on MAL? (y/n): ")
	if toUpdate != 'y':
		print("\n")
		return

	print("[*] Preparing to update list")
	# PARSER HERE - Get Anime name from filename
	# Using regex as temp. solution (works only for file names following HorribleSubs naming format)
	try:
		animename = re.split("\]|\)|\[|\(", filename)[2].split('-')[0].strip()
	except:
		print("\033[91m[-] Unsupported filename format/Not an anime file! Skipping.\033[0m")
		return
	# Get loginData from login json file
	with open("data/loginData.json", "r") as f:
		loginData = json.load(f)

	# if loginData is empty or it's been "expires_in" seconds (expiration of the access_token), do a fresh login
	if (not loginData) or ((time.time() - float(loginData['access_token'][1])) > float(loginData['expires_in'])):
		print("[*] Doing a fresh login")
		# Get login credentials from config
		with open("data/config.json", "r") as f:
			config = json.load(f)
		user = config['main']['username']
		passwd = config['main']['password']

		# Get loginInfo by logging in and add current timestamp to file
		loginInfo = mal.User.login(user, passwd)
		loginInfo['access_token'] = [loginInfo['access_token'], str(time.time())]

		with open("data/loginData.json", "w+") as f:
			json.dump(loginInfo, f, indent=4)
		AT = loginInfo['access_token'][0]

	# else, get the existing access_token from the json file
	else:
		print("[*] Grabbing existing Access Token from file")
		AT = loginData['access_token'][0]

	# Get User's watchlist
	animeInfo = mal.User.getAnimeList(AT, "watching", ["alternative_titles", "my_list_status"])
	aniList = []

	for i,item in enumerate(animeInfo['data']):
		aniList.append({'names': None, "id": ""})

		originalTitle = item['node']['title']
		engTitle = item['node']['alternative_titles']['en']
		japTitle = item['node']['alternative_titles']['ja']
		# Adding original, english, japanese and all other alternate_titles to names list
		aniList[i]['names'] = [originalTitle, engTitle, japTitle] + [name for name in item['node']['alternative_titles']['synonyms']]
		# Adding id of show
		aniList[i]['id'] = str(item['node']['id'])

	# probDict = {}
	probValues = []
	fset = fuzzyset.FuzzySet()
	fset.add(animename)

	# print("{}: {}".format(aniList, len(aniList)))
	for show in aniList:
		probList = []
		for name in show['names']:
			# print("Name: {}".format(name))
			# Filter out blank entries from the list
			if name is not "":
				fuzzyInfo = fset.get(name)
				#Fuzzy returns None if 2 strings are completely different: filtering out those cases
				if fuzzyInfo is not None:
					# print("Fuzzy: {}".format(fuzzyInfo))
					probList.append(fuzzyInfo[0][0])

		# print("probList: {}".format(probList))
		# Add 0 probability if probList is empty (fuzzyInfo returned None, so show was never added to probList), hence definitely not this show
		if not probList:
			probList.append(0)
		# Add "show: max probability" key-value pair in dictionary
		# Key is first name from list of names of the show (first name is always 'title', the name MAL uses on the website by default)
		# probDict[show['names'][0]] = str(max(probList))
		probValues.append(max(probList))

	if max(probValues) >= 0.7:
		toUpdate_idx = probValues.index(max(probValues))
		toUpdate_name = aniList[toUpdate_idx]['names'][0]
		toUpdate_ID = aniList[toUpdate_idx]['id']
		# print("{} -> {}".format(toUpdate_name, toUpdate_ID))

		#Get previously watched episodes from list
		for show in animeInfo['data']:
			if show['node']['title'] == toUpdate_name:
			 	oldVal = int(show['node']['my_list_status']['num_episodes_watched'])

		#Update list with previously watched episodes + 1
		updatedList = mal.User.updateList(AT, toUpdate_ID, ["num_watched_episodes"], [oldVal + 1])
		print("\033[92m[+]\033[0m \033[93m{}\033[0m \033[92mwas updated!\033[0m \033[95m{} --> {}\033[0m\n".format(toUpdate_name, oldVal, oldVal + 1))
	else:
		print("\033[91m[-] This show does not seem to be in your watchlist! Skipping.\033[0m")
		return

print("[*] Starting media auto-detection script")
try:
	while running:
		# Detect for opening of new media players
		for p in psutil.process_iter(['pid', 'name']):
			if p.info['name'] in player_processes: # Found a supported media player
				# Check if process is not already added
				foundNewProcess = True
				for proc in players:
					if proc.info['pid'] == p.info['pid']:
						foundNewProcess = False # Detected process already exists in player list
				if foundNewProcess is True:
					players.append(p) # Add new player process to list
					print("\033[92m[+] Added new player with\033[0m \033[95mpname: {}, pid: {}\033[0m".format(p.info['name'], p.info['pid']))

		# Detect when a media player gets closed
		if len(players) > 0:
			# Check name of file being played
			for p in players:
				if p.is_running() is True: # Check if process is still running
					files = p.open_files()
					for f in files:
						f_str = str(f)
						# Detect various file formats
						for ff in file_formats:
							# If one of the opened_files contains a file with one of the file_formats in it's name, get the filename
							if f_str.find(ff) != -1:
								if platform.system() == "Linux":
									fname = f_str[f_str.rfind("/") + 1:f_str.find(ff)]
								elif platform.system() == "Windows":
									fname = f_str[f_str.rfind("\\") + 1:f_str.find(ff)]

								if p.info['pid'] not in open_files.keys():
									shouldPrint = True
									open_files[p.info['pid']] = fname

								# New file opened or a change in file name occurs
								if open_files[p.info['pid']] != fname:
									shouldPrint = True
									updateList(open_files[p.info['pid']])
									open_files[p.info['pid']] = fname

			# Detect closing of media player
			updated_players = []
			for p in players:
				if p.is_running() is True:
					# Player process is still running, copy to updated list
					updated_players.append(p)
				else:
					print("\033[91m[-] Process with\033[0m \033[95mpname {}, pid {}\033[0m \033[91mwas closed\033[0m".format(p.info['name'], p.info['pid']))
					if p.info['pid'] in open_files.keys():
						updateList(open_files[p.info['pid']])
						del open_files[p.info['pid']]

			players = updated_players # Update player process list

		# Print name of files being played
		if shouldPrint:
			for k in open_files.keys():
				print("\033[94m[{}]\033[0m: Playing \033[93m{}\033[0m".format(k, open_files[k]))
			shouldPrint = False

		# running = 0
except KeyboardInterrupt as e:
	print("\n[*] Closed.")