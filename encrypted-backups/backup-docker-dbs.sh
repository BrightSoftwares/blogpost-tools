#!/bin/bash

# DB Container Backup Script Template
# ---
# This backup script can be used to automatically backup databases in docker containers.
# It currently supports mariadb, mysql and bitwardenrs containers.
# 

#NB_DAYS=$(printenv NB_DAYS)
export `xargs --null --max-args=1 echo < /proc/1/environ`

echo "Backing databases up..."
echo "NB_DAYS = $NB_DAYS"

if [[ -z "$NB_DAYS" ]]; then
  echo "The env variable NB_DAYS is not defined. Please define it and run the script again."
  echo "Exiting ..."
  exit -1
else
  echo "All env variables defined. We can continue"
fi

DAYS=$NB_DAYS
BACKUPDIR=/backups/databases


# backup all mysql/mariadb containers

CONTAINER=$(docker ps --format '{{.Names}}:{{.Image}}' | grep 'mysql\|mariadb' | cut -d":" -f1)

echo $CONTAINER

if [ ! -d $BACKUPDIR ]; then
    mkdir -p $BACKUPDIR
fi

for i in $CONTAINER; do
    MYSQL_DATABASE=$(docker exec $i env | grep MYSQL_DATABASE |cut -d"=" -f2-)
    MYSQL_PWD=$(docker exec $i env | grep MYSQL_ROOT_PASSWORD |cut -d"=" -f2-)

    echo "Backing up db $MYSQL_DATABASE in container $i. Saving result to $BACKUPDIR."

    docker exec -e MYSQL_DATABASE=$MYSQL_DATABASE -e MYSQL_PWD=$MYSQL_PWD \
        $i /usr/bin/mysqldump -u root $MYSQL_DATABASE \
        | gzip > $BACKUPDIR/$i-$MYSQL_DATABASE-$(date +"%Y%m%d%H%M").sql.gz

    OLD_BACKUPS=$(ls -1 $BACKUPDIR/$i*.gz |wc -l)
    if [ $OLD_BACKUPS -gt $DAYS ]; then
        find $BACKUPDIR -name "$i*.gz" -daystart -mtime +$DAYS -delete
    fi
done


# bitwarden backup

BITWARDEN_CONTAINERS=$(docker ps --format '{{.Names}}:{{.Image}}' | grep 'bitwardenrs' | cut -d":" -f1)

for i in $BITWARDEN_CONTAINERS; do
    docker exec  $i /usr/bin/sqlite3 data/db.sqlite3 .dump \
        | gzip > $BACKUPDIR/$i-$(date +"%Y%m%d%H%M").sql.gz

    OLD_BITWARDEN_BACKUPS=$(ls -1 $BACKUPDIR/$i*.gz |wc -l)
    if [ $OLD_BITWARDEN_BACKUPS -gt $DAYS ]; then
        find $BACKUPDIR -name "$i*.gz" -daystart -mtime +$DAYS -delete
    fi
done

echo "$TIMESTAMP Backup for Databases completed"