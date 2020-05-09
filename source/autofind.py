#!/usr/bin/env python3
import psutil
import json
import time

print("\033[91m[*] INFO: Make sure your media file is running in the media player you want to add.\033[0m")
print("\033[92m[+] Looking for running media players.\033[0m")
time.sleep(2)

#Create a dictionary of processes and the files they have opened
processDict = {}
for proc in psutil.process_iter(['pid', 'name', 'username']):
	processDict[proc] = proc.open_files()

#Get extensions list from extensions.json
with open("data/extensions.json", "r") as f:
	extList = json.load(f)

#If extList is empty
if not extList:
	print("\033[91m[-] Extension list is empty!\033[0m")
	exit()

#Get media players from media_players.json
with open("data/media_players.json", "r") as f:
	mediaPlayers = json.load(f)

playerList = []
for proc,fileList in processDict.items():
	if fileList:
		for file in fileList:
			for ext in extList:
				if file.path.find(ext) != -1:
					if proc.name() not in mediaPlayers:
						playerList.append(proc.name())

if not playerList:
	print("[*] No new media player processes were added.")
	exit()
else:
	mediaPlayers += playerList
	with open("data/media_players.json", "w+") as f:
		json.dump(mediaPlayers, f, indent=4)

	for player in playerList:	
		print("\033[92m[+] New media player with process name\033[0m \033[95m{}\033[0m \033[92mwas added.\033[0m".format(player))

print("\033[96m[*] If any of the added processes are not media player processes, manually remove them from data/media_players.json.\033[0m")
print("[*] Done.")