#!/bin/bash
#A script to mount Bitlocker Encrypted Windows partition

#Enter path to the partition to be mounted and Recovery Key for the partition below
dislocker /dev/nvme0n1p3 -v --recovery-password=<Enter-Recovery-Key-Here> /media/bitlocker
mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
