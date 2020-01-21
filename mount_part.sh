#!/bin/bash
#A script to mount the Windows partition

dislocker /dev/nvme0n1p3 -v --recovery-password=449273-176011-028820-629068-531322-091696-259919-270985 /media/bitlocker
mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
