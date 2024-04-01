#!/bin/bash


# Duplicati Backup Script Template

export `xargs --null --max-args=1 echo < /proc/1/environ`

DUPLICATI_BACKUP_FOLDER=/backups/duplicati

echo "$TIMESTAMP Starting the duplicati jobs backup to folder $DUPLICATI_BACKUP_FOLDER"

if [[ -z "$DUPLICATI_SERVER_URL" ]]; then
  echo "The env variable DUPLICATI_SERVER_URL is not defined. Please define it and run the script again."
  echo "Exiting ..."
  exit -1
else
  echo "All env variables defined. Continue the execution"
  IP=$(nslookup $DUPLICATI_SERVER_URL | grep Address | grep -v \#53 | cut -f 2 -d' ')
  duc login $IP
  duc export --all --output JSON --output-path $DUPLICATI_BACKUP_FOLDER
fi


echo "$TIMESTAMP Backup for duplicati jobs completed"
