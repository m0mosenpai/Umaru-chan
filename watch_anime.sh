#!/bin/bash
#A simple bash script to automate the process of choosing and playing any downloaded anime of choice.
#Change the path after 'bitlockermount', to wherever your anime library is located on the Windows Partition. Ensure the name of your anime folder DOES NOT contain spaces.

path="/media/bitlockermount/Users/sarth/Documents/Anime"

#Checks if the partition is mounted and mounts it if it isn't
cd "$path">/dev/null 2>&1
if [ $? -eq 0 ] ; then
	printf "***Bitlocker Drive already mounted. Proceeding ahead...***\n"
else
	printf "***Bitlocker Drive not mounted. Mounting drive...***\n"
	sudo $HOME/Documents/Scripts/mount.sh	
fi
printf "\n"

file_count=$(ls $path -1 | wc -l)

#Hashmap to refer to files in the directory by numbers
declare -A file_list
num=1
for file in $path/*;  do
	printf "$num : ${file##*/}\n"
	file_list[$num]=${file##*/}
	num=$((num + 1))
done

printf "\n"
read -p "Select the anime of your choice [1-$file_count]: " choice

#Using VLC to run the chosen file
echo "***Playing***"
vlc "$path/${file_list[$choice]}">/dev/null 2>&1

