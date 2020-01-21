#!/bin/bash
#A script to mount the Windows partition

dislocker /dev/nvme0n1p3 -v --recovery-password=<Enter-Recovery-Key-Here> /media/bitlocker
mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
