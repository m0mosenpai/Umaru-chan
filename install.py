#!/usr/bin/env python3
import os
import colorama
import platform
import getpass
import json
from time import sleep

#A context manager class which changes the working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#Clear screen
if platform.system() == "Windows":
	os.system('cls')
if platform.system() == "Linux":
	os.system('clear')

version = "BETA"
colorama.init()

print("\033[95mWelcome to \033[0m \n")
print("\033[93m██╗   ██╗███╗   ███╗ █████╗ ██████╗ ██╗   ██╗       ██████╗██╗  ██╗ █████╗ ███╗   ██╗\033[0m")
print("\033[93m██║   ██║████╗ ████║██╔══██╗██╔══██╗██║   ██║      ██╔════╝██║  ██║██╔══██╗████╗  ██║\033[0m")
print("\033[93m██║   ██║██╔████╔██║███████║██████╔╝██║   ██║█████╗██║     ███████║███████║██╔██╗ ██║\033[0m")
print("\033[93m██║   ██║██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║╚════╝██║     ██╔══██║██╔══██║██║╚██╗██║\033[0m")
print("\033[93m╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝      ╚██████╗██║  ██║██║  ██║██║ ╚████║\033[0m")
print("\033[93m ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝        ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝\033[0m \033[95m v{}\033[0m".format(version))
print("\033[95mA program to automate anime watching and downloading on Linux.\033[0m")
print("")
print("This script will guide you through setting up Umaru-chan for the first time")
print("")

sleep(2)
with cd("source"):
	print("\033[92m[+] Moved to source directory.\033[0m")
	print("Checking if data folder exists...")
	sleep(1)
	if not os.path.isdir("data"):
		print("\033[91m[-] Does not exist! Creating one...")
		sleep(1)
		os.mkdir("data")
	with cd("data"):
		print("\033[92m[+] Moved to data directory\033[0m")
		path = input("Where is the root folder of your anime library? (Enter absolute path):\n")

		torrent = input("Where do you want your downloaded .torrent files to be stored? (Enter absolute path):\n")
		print("\033[95mIMPORTANT: Turn on 'Download .torrent files automatically from this folder' in the settings of your Torrent Client and set the folder to the one specified above.\033[0m")
		
		q = input("What do you want the default quality of downloads to be? (480p/720p/1080p):\n")
		if q == "480p" or q == "720p" or q == "1080p":
			quality = q
		else:
			print("\033[91mInvalid input! Setting to default quality (720p)\033[0m")
			quality = "720p"

		_id = input("Do you own a MAL(MyAnimeList) account? (y/n): ")
		if _id == 'y':
			print("Enter your credentials \033[91m(WARNING: Your credentials will be stored locally in plaintext form)\033[0m")
			username = input("Username: ")
			password = getpass.getpass("Password: ")

		else:
			username = ""
			password = ""

		print("Creating config...")
		config = {"main":{"path":path,"torrent":torrent,"quality":quality,"username":username,"password":password},"watchlist":{}}
		with open("config.json", "w+") as f:
			json.dump(config, f, indent=4)
		sleep(1)	
		print("\033[92m[+] Config created!\033[0m")
		print("")

		print("\033[92mAll set!\033[0m")
		print("\033[96m[*] Add anime to your watchlist by running client.py with -a/--add option.\033[0m \033[91m(Example: python client.py -a \"boku no hero academia\":87 where the no. following the ':' refers to the last watched episode number)\033[0m")
		print("\033[96m[*] All values set above can be changed by running client.py followed by the appropriate argument. Type -h/--help for more info.\033[0m")
		print("\033[96m[*] When done, run server.py and leave it running in the background (Don't forget to keep your Torrent Client open and ready to download .torrent files!)\033[0m")