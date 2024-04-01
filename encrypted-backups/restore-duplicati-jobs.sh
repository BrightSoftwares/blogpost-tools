#!/bin/bash

export `xargs --null --max-args=1 echo < /proc/1/environ`

DUPLICATI_BACKUP_FOLDER=/backups/duplicati

echo "Collecting the IP address of the duplicati server "
IP=$(nslookup $DUPLICATI_SERVER_URL | grep Address | grep -v \#53 | cut -f 2 -d' ')

echo "Login to server"
duc login $IP

echo "Importing jobs from previously exported files from folder $DUPLICATI_BACKUP_FOLDER"

for i in $DUPLICATI_BACKUP_FOLDER/*.json; do 
  echo "Importing file $i"; 
  duc create backup $i; 
done

echo "Import done"
