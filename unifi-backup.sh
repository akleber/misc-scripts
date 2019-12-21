#!/bin/bash

find /var/lib/unifi/backup/autobackup/ -maxdepth 1 -type f -name '*.unf' -print0 \
     | xargs -0 stat --printf "%Y\t%n\n" \
     | sort -n \
     | tail  -n 1 \
     | cut -f 2 \
     | xargs -i /usr/bin/scp -i /home/pi/.ssh/id_rsa \
     {} backup@nas.kleber:/volume1/NAS/Backup/rpi3-unifi
