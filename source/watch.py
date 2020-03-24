import os
import subprocess
import re

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
		os.system('clear')
		print("(In {}) \n".format(PATH))
		filedict = {}
		cnt = 0
		files = os.listdir()
		for file in files:
			filedict[cnt] = file
			print("{}: {}".format(cnt, file))
			cnt += 1
		#Asks user to choose a media file to play.	
		choice = int(input("\nSelect media file [0 - {}]: \n".format(len(filedict) - 1)))
		filename = filedict[choice]
		#Check if chosen file is a regular file or a directory
		if os.path.isfile(filename):
			#Runs the file in vlc is it's a regular file
			print("Opening file in VLC..")
			#Errors are piped to /dev/null
			subprocess.run(["vlc", filename], stderr=subprocess.DEVNULL)
		elif os.path.isdir(filename):
			#If it's a directory, lists all files in it by recursively calling createFileList
			createFileList(filename)
		else:
			#Else, invalid file type.
			print("Invalid file/directory.")
	
	choice = input("Do you want to update episode count on MAL? (y/n)\n")
	if choice == 'y':
		updateMAL(filename)
	return

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
	with open('data/path.txt', 'r+') as f:
		PATH = f.read()
	#Exits if path not set	
	if PATH == '':
		print("Download directory not set. Run with -p/--path <PATH> to set one up!")
		exit()

	createFileList(PATH)

if __name__ == "__main__":	
	try:
		main()
	except KeyboardInterrupt:
		print("\nKeyboard Interrupt Detected. Exiting.")