#!/bin/bash
today=`date '+%Y_%m_%d-%H_%M_%S'`;
backuppath="/var/backups/influxdb/$today"

/usr/bin/influxd backup -portable $backuppath
/usr/bin/scp -i /home/pi/.ssh/id_rsa -r $backuppath backup@nas.kleber:/volume1/NAS/Backup/rpi3-influxdb
rm -rf $backuppath
