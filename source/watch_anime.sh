#!/bin/bash
#A simple bash script to automate the process of choosing and playing any downloaded anime of choice.
#Change the path to wherever your anime library is located. Ensure the name of your anime folder DOES NOT contain spaces.
version='BETA'

clear

printf "\n"
printf "\n"
printf "Welcome to \n"
printf "██╗   ██╗███╗   ███╗ █████╗ ██████╗ ██╗   ██╗       ██████╗██╗  ██╗ █████╗ ███╗   ██╗\n"
printf "██║   ██║████╗ ████║██╔══██╗██╔══██╗██║   ██║      ██╔════╝██║  ██║██╔══██╗████╗  ██║\n"
printf "██║   ██║██╔████╔██║███████║██████╔╝██║   ██║█████╗██║     ███████║███████║██╔██╗ ██║\n"
printf "██║   ██║██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║╚════╝██║     ██╔══██║██╔══██║██║╚██╗██║\n"
printf "╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝      ╚██████╗██║  ██║██║  ██║██║ ╚████║\n"
printf " ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝        ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ v$version\n"
printf "A simple program to automate anime watching on Linux."
printf "\n"
printf "\n"

#Global Variables
path="/media/bitlockermount/Users/sarth/Documents/Anime"
declare -A file_list
file_count=$(ls $path -1 | wc -l)

#Mounts Bitlocker Encrypted Drive (if not already mounted)
#Comment out this function if you dont have a Bitlocker encrypted partition or have your library in linux itself.
mountDrive(){
	printf "Checking for Bitlocker Drive... \n"
	sleep 1s
	cd "$path">/dev/null 2>&1
	if [ $? -eq 0 ] ; then
		printf "Bitlocker Drive already mounted. Proceeding ahead...\n"
		sleep 1s
	else
		printf "Bitlocker Drive not mounted. Mounting drive...\n"
		sudo $HOME/Documents/Scripts/mount_part.sh	
	fi
	printf "\n"
}

#Creates a list of all files in the directory
createFileList() {
	num=1
	for file in $path/*;  do
		printf "$num : ${file##*/}\n"
		file_list[$num]=${file##*/}
		num=$((num + 1))
	done
}

#Displays prompt to remove file after watching it
removePrompt() {
	printf "${file_list[$1]} \n"
	printf "\n"
	read -p "Do you want to remove this file from your library? (y/n) " choice2

	if [ $choice2 = 'y' ] ; then
		printf "File Removed.\n"
		rm -r "$path/${file_list[$1]}"
	else
		return
	fi
}

#Main function
mountDrive
createFileList

printf "\n"
read -p "Select the anime of your choice [1-$file_count]: " choice1

clear
printf "Opening in VLC... \n"
vlc "$path/${file_list[$choice1]}">/dev/null 2>&1
printf "Done. \n"
printf "\n"
removePrompt "$choice1"