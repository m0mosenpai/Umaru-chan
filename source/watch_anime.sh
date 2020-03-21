#!/bin/bash
#A simple bash script to automate the process of choosing and playing any downloaded anime of choice.
#Change the path to wherever your anime library is located. Ensure the name of your anime folder DOES NOT contain spaces.
version='BETA'

clear

printf "\n"
printf "\n"
printf "\e[95;1mWelcome to \e[0m \n"
printf "\e[93;1m██╗   ██╗███╗   ███╗ █████╗ ██████╗ ██╗   ██╗       ██████╗██╗  ██╗ █████╗ ███╗   ██╗\e[0m\n"
printf "\e[93;1m██║   ██║████╗ ████║██╔══██╗██╔══██╗██║   ██║      ██╔════╝██║  ██║██╔══██╗████╗  ██║\e[0m\n"
printf "\e[93;1m██║   ██║██╔████╔██║███████║██████╔╝██║   ██║█████╗██║     ███████║███████║██╔██╗ ██║\e[0m\n"
printf "\e[93;1m██║   ██║██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║╚════╝██║     ██╔══██║██╔══██║██║╚██╗██║\e[0m\n"
printf "\e[93;1m╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝      ╚██████╗██║  ██║██║  ██║██║ ╚████║\e[0m\n"
printf "\e[93;1m ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝        ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝\e[0m \e[95;1m v$version\e[0m\n"
printf "\e[95;1mA simple program to automate anime watching on Linux.\e[0m"
printf "\n"
printf "\n"

#Global Variables
path="/media/bitlockermount/Users/sarth/Documents/Anime"
declare -A file_list

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
		#Parameter Exansion in BASH
		name=${file##*/}
		cd "$path/$name">/dev/null 2>&1
		#Condition to check whether it's a file or a directory
		#Using ANSI codes to print colored outputs
		if [ $? -eq 0 ] ; then
			#Print Directory names in Cyan
			printf "\e[96;1m $num : $name \e[0m\n"
		else
			#Print File names in Red 
			printf "\e[91;1m $num : $name \e[0m\n"
		fi

		file_list[$num]=$name
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
file_count=$(ls $path -1 | wc -l)

printf "\n"
read -p "Select media file [1-$file_count]: " choice1

clear
printf "Opening in VLC... \n"
vlc "$path/${file_list[$choice1]}">/dev/null 2>&1
printf "Done. \n"
printf "\n"
removePrompt "$choice1"