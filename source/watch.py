#!/usr/bin/env python3
from time import sleep
import filetype
import colorama
import os
import platform
import subprocess
import re
import json
import colorama

colorama.init()

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

#Change directory to PATH, lists all files and folders in the directory and opens media file chosen by the user
def createFileList(PATH):
	with cd(PATH):
		print("(In \033[95m{}\033[0m)\n".format(PATH))
		filedict = {}
		cnt = 0
		files = os.listdir()
		if not files:
			print("\033[91mDirectory is Empty!\033[0m")
			exit()

		for file in files:
			filedict[cnt] = file
			print("{}: \033[93m{}\033[0m".format(cnt, file))
			cnt += 1
		#Asks user to choose a media file to play.	
		choice = int(input("\nSelect file/directory [0 - {}]: ".format(len(filedict) - 1)))
		filename = filedict[choice]
		#Check if chosen file is a regular file or a directory
		if os.path.isfile(filename):
			#Check if the file is a video file or not
			kind = filetype.guess(filename)
			if kind.mime.split('/')[0] == "video":
				print("Opening file in default program..")
				#Open the file according to the platform
				if platform.system() == 'Windows':
					os.startfile(filename)
				elif platform.system() == 'Linux':
					subprocess.run(['xdg-open', filename], stderr=subprocess.DEVNULL)
				else:
					print("\033[91mUnsupported Platform!\033[0m")
					exit()
			else:
				print("\033[91mUnsupported File Type! Ensure it's a video file and try again!\033[0m")
				exit()
		elif os.path.isdir(filename):
			#If it's a directory, lists all files in it by recursively calling createFileList
			createFileList(filename)
		else:
			#Else, invalid file type.
			print("\033[91mInvalid file/directory.\033[0m")
	
	return filename

#calls mal_log.py to update anime
def updateMAL(filename):
	#Gets anime name from file name but splitting around () or [] and stripping off white spaces
	animename = re.split("\]|\)|\[|\(", filename)[2].split('-')[0].strip()
	print("Updating episode count on MAL...")
	subprocess.run(["python3", "mal_log.py", animename])
	print("Done.")

#main function
def main():
	#Reads PATH from path.txt
	with open('data/config.json', 'r+') as f:
		config = json.load(f)
		PATH = config['main']['path']
		U = config['main']['username']
		P = config['main']['password']
	#Exits if path not set	
	if PATH == "":
		print("\033[91mAnime Library not set. Run with -p/--path <PATH> to set one up!\033[0m")
		exit()

	filename = createFileList(PATH)
	sleep(2)
	choice = input("Do you want to update episode count on MAL? (y/n): ")
	if U == "" or P == "":
		print("\033[91mUsername/Password not set! Run with -m/--mal-id to set one up!\033[0m")
	else:	
		if choice == 'y':
			updateMAL(filename)

if __name__ == "__main__":	
	try:
		main()
	except KeyboardInterrupt:
		print("\n\033[91mKeyboard Interrupt Detected. Exiting.\033[0m")