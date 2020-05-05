import psutil

"""
Notes:
psutil.pid_exists(pid) - To detect whether a pid exists or not
Process.is_running() - Return whether the current process is running in the current process list.
						This is reliable also in case the process is gone and its PID reused by another process, therefore it
						must be preferred over doing psutil.pid_exists(p.pid).
"""

#Script Data
running = 1 #Whether the script should run
file_formats = [".mkv"] #List of supported file formats
players = [] #Store all running media player processes

#Media player Data
player_processes = ["vlc.exe"]
open_files = {}

print("Starting media_detect script")

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
						if f_str.find(ff) != -1:
							fname = f_str[f_str.rfind("\\") + 1:f_str.find(ff)]
							open_files[p.info['pid']] = fname
							#print(fname)

		#Detect closing of media player
		updated_players = []
		for p in players:
			if p.is_running() is True:
				#Player process is still running, copy to updated list
				updated_players.append(p)
			else:
				print("Process with pname {} and pid {} was closed".format(p.info['name'], p.info['pid']))
				del open_files[p.info['pid']]
		players = updated_players #Update player process list

	#Print name of files being played
	for k in open_files.keys():
		print("[{}]:{}".format(k, open_files[k]))

	#running = 0