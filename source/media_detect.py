#!/usr/bin/env python3
import psutil
import platform
import malupdate as mal
import colorama
import re
import json
import time

colorama.init()

"""
Notes:
psutil.pid_exists(pid) - To detect whether a pid exists or not
Process.is_running() - Return whether the current process is running in the current process list.
						This is reliable also in case the process is gone and its PID reused by another process, therefore it
						must be preferred over doing psutil.pid_exists(p.pid).
"""
#Script Data
running = 1 #Whether the script should run
file_formats = [".mkv", ".mp4", ".ogg", ".avi", ".mov", ".wmv", ".mpeg"] #List of supported file formats
players = [] #Store all running media player processes
shouldPrint = True

#Media player Data
player_processes = ["vlc.exe", "vlc", "totem", "wmplayer.exe"] #List of supported media player processes
open_files = {}

#Makes a list of all the anime that need to be updated
def updateList(filename):
	toUpdate = input("Update list on MAL? (y/n): ")
	if toUpdate != 'y':
		return

	print("Preparing to update list")
	# PARSER HERE - Get Anime name from filename
	# Using regex as temp. solution (works only for file names following HorribleSubs naming format)
	try:
		animename = re.split("\]|\)|\[|\(", filename)[2].split('-')[0].strip()
	except:
		print("Unsupported filename format/Not an anime file! Skipping.")
		return
	#Get loginData from login json file
	with open("data/loginData.json", "r") as f:
		loginData = json.load(f)

	time_diff = time.time() - float(loginData['access_token'][1])

	#if loginData is empty or it's been "expires_in" seconds (expiration of the access_token), do a fresh login
	if (not loginData) or (time_diff > float(loginData['expires_in'])):
		print("Doing a fresh login")
		#Get login credentials from config
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

	#else, get the existing access_token from the json file
	else:
		print("Grabbing existing Token from file")
		AT = loginData['access_token'][0]


print("Starting media auto-detection script")
try:
	while running:
		#Detect for opening of new media players
		for p in psutil.process_iter(['pid', 'name']):
			if p.info['name'] in player_processes: #Found a supported media player
				#Check if process is not already added
				foundNewProcess = True
				for proc in players:
					if proc.info['pid'] == p.info['pid']:
						foundNewProcess = False #Detected process already exists in player list
				if foundNewProcess is True:
					players.append(p) #Add new player process to list
					print("Added new player with pname {} and pid {}".format(p.info['name'], p.info['pid']))

		#Detect when a media player gets closed
		if len(players) > 0:
			#Check name of file being played
			for p in players:
				if p.is_running() is True: #Check if process is still running
					files = p.open_files()
					for f in files:
						f_str = str(f)
						#Detect various file formats
						for ff in file_formats:
							#If one of the opened_files contains a file with one of the file_formats in it's name, get the filename
							if f_str.find(ff) != -1:
								if platform.system() == "Linux":
									fname = f_str[f_str.rfind("/") + 1:f_str.find(ff)]
								elif platform.system() == "Windows":
									fname = f_str[f_str.rfind("\\") + 1:f_str.find(ff)]

								if p.info['pid'] not in open_files.keys():
									shouldPrint = True
									open_files[p.info['pid']] = fname

								#New file opened or a change in file name occurs
								if open_files[p.info['pid']] != fname:
									shouldPrint = True
									updateList(open_files[p.info['pid']])
									open_files[p.info['pid']] = fname

			#Detect closing of media player
			updated_players = []
			for p in players:
				if p.is_running() is True:
					#Player process is still running, copy to updated list
					updated_players.append(p)
				else:
					print("Process with pname {} and pid {} was closed".format(p.info['name'], p.info['pid']))
					if p.info['pid'] in open_files.keys():
						updateList(open_files[p.info['pid']])
						del open_files[p.info['pid']]

			players = updated_players #Update player process list

		#Print name of files being played
		if shouldPrint:
			for k in open_files.keys():
				print("[{}]:{}".format(k, open_files[k]))
			shouldPrint = False

		#running = 0
except KeyboardInterrupt as e:
	print("\nClosed.")