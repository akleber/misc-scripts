#!/bin/bash
today=`date '+%Y_%m_%d-%H_%M_%S'`;
backupfile="/var/backups/grafana_$today.tar.gz"

/bin/tar -czvf $backupfile /var/lib/grafana/grafana.db

/usr/bin/scp -i /home/pi/.ssh/id_rsa -r $backupfile backup@nas.kleber:/volume1/NAS/Backup/rpi3-grafana/
rm -f $backupfile
