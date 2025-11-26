# How to improve this

I use duplicati to backup all the files in my infra (the ones that are not versioned in a git repository).
I backup mostly docker container files.


Features I like with duplicity

- encryption of the data
- automatic run
- upload to ftp
- able to backup diffs
- clean old backups.

### Expected target behavior

I want to have this experience

- I use ansible/terraform to deploy the duplicati based solution
- All is well setup
- Necessary files are backuped to the ftp remote location.
- When an issue happens (either the whole server, the docker-compose stack or the container)
-   case of the container = usecase is I want to upgrade the container but don't want to corrupt the data, I restore it somewhere else with the restored backuped data and test
-   case of docker-compose = usecase is I want to move the stack to another server. I can run a command/github action workflow) and it will restore the data, restart the stack
-   for the whole server, usecase is I want to move all the stacks on the server to another server. Same as previously, I run a command/script/pipeline and all is recreated.

I am ok to use terraform or ansible.

The idea is to have free of mind. I know that my data is backuped and if I have a failure , I can just recreate everything.


### Notes / commands when I was trying to restore last time

1  apt update
    2  apt install python3 python3-pip git -y
    3  git clone https://github.com/pectojin/duplicati-client --depth 1
    4  cd duplicati-client/
    5  ln -s /location/of/git/repo/duplicati_client.py /usr/bin/duc
    6  duc
    7  /usr/bin/duc
    8  pwd
    9  ln -s /duplicati-client/duplicati_client.py /usr/bin/duc
   10  rm /usr/bin/duc 
   11  ln -s /duplicati-client/duplicati_client.py /usr/bin/duc
   12  duc
   13  pip3 install -r requirements.txt 
   14  duc login http://localhost
   15  duc list backups
   16  duc get backup 11
   17  duc create backup /backups/duplicati/duc_backups.json
   18  duc export backup /backups/duplicati/duc_backups.json
   19  duc export backup --all /backups/duplicati/duc_backups.json
   20  duc export --all /backups/duplicati/duc_backups.json
   21  duc export -h
   22  duc export --all --output JSON --output-path /backups/duplicati/duc_backups.json
   23  ls -la /backups/duplicati/
   24  ls -la /backups/duplicati/duc_backups.json/
   25  less /backups/duplicati/duc_backups.json/Duplicati.json 
   26  history


### A script to download backups

download_encrypted.sh

#!/bin/bash


lftp -u "$FTP_USER","$FTP_PASSWORD" $FTP_HOST <<EOF
#debug;
set ssl:verify-certificate no;
set sftp:auto-confirm yes;
mirror --use-pget-n=10 $REMOTE_DIR $LOCAL_DIR;
exit
EOF
echo "done"

### Env variables for a script to backup/restore backups

I replaced the secrets by fake

SRC_BACKUP_SUBFOLDER=test_volume_backup
GPG_PASSPHRASE=fake
SRC_BACKUP_ROOT=/home/container_data/
DEST_BACKUP_FILES_PATH=/home/container_data/backups/
DUPLICATI_PORT=8200
DUPLICATI_SRC_FOLDER=/home/container_data/
DUPLICATI_CONFIG_FOLDER=/home/container_data/duplicatitemp/
DUPLICATI_BACKUP_FOLDER=/home/container_data/backups/
DUPLICATI_PGID=1000
DUPLICATI_PUID=1000
BACKUP_CRON_EXPRESSION="0/2 * * * *"
FTP_USER=fake
FTP_PASSWORD=fake
FTP_HOST=sftp://141.136.43.89
REMOTE_DIR=openmediavault/duplicati
LOCAL_DIR=myfiles


### An example of docker-compose stack

services:
  backup_1:
    image: offen/docker-volume-backup:v2
    env_file:
      - path: .env
    environment: #
      BACKUP_FILENAME: backup-${SRC_BACKUP_SUBFOLDER}-%Y-%m-%dT%H-%M-%S.tar.gz
      BACKUP_LATEST_SYMLINK: backup-${SRC_BACKUP_SUBFOLDER}-latest.tar.gz
      GPG_PASSPHRASE: ${GPG_PASSPHRASE}
    volumes:
      - ${SRC_BACKUP_ROOT}:/backup/${SRC_BACKUP_SUBFOLDER}:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ${DEST_BACKUP_FILES_PATH}:/archive

  duplicati_client:
    image: python:3.10-bullseye
    container_name: duplicati_client
    depends_on:
      - duplicati_temp
      - duplicati
    command: git clone https://github.com/pectojin/duplicati-client --depth 1 && cd duplicati-client && pip3 install -r requirements.txt && ln -s /duplicati_client/duplicati_client.py /usr/bin/duc && duc && sleep 60

  duplicati_temp:
    #image: lscr.io/linuxserver/duplicati:latest
    image: duplicati/duplicati
    env_file:
      - path: .env
    container_name: duplicati_temp
    environment:
      - PUID=${DUPLICATI_PUID}
      - PGID=${DUPLICATI_PGID}
      - TZ=Etc/UTC
      - CLI_ARGS= #optional
    volumes:
      - ${DUPLICATI_CONFIG_FOLDER_TEMP}:/config
      - ${DUPLICATI_CONFIG_FOLDER}:/config_real
      - ${DUPLICATI_BACKUP_FOLDER}:/backups
      - ${DUPLICATI_SRC_FOLDER}:/source
    ports:
      - ${DUPLICATI_PORT_TEMP:-8201}:8200
    restart: unless-stopped

  duplicati:
    #image: lscr.io/linuxserver/duplicati:latest
    image: duplicati/duplicati
    env_file:
      - path: .env
    container_name: duplicati
    environment:
      - PUID=${DUPLICATI_PUID}
      - PGID=${DUPLICATI_PGID}
      - TZ=Etc/UTC
      - CLI_ARGS= #optional
    volumes:
      - ${DUPLICATI_CONFIG_FOLDER}:/config
      - ${DUPLICATI_BACKUP_FOLDER}:/backups
      - ${DUPLICATI_SRC_FOLDER}:/source
    ports:
      - ${DUPLICATI_PORT:-8200}:8200
    restart: unless-stopped

volumes:
  data_1:
  data_2:

### A script to download/upload/sync using lftp

lftp -u ${FTP_USER},${FTP_PASSWORD} ${FTP_HOST}  -e "set ftp:ssl-allow off" << EOF
mirror --use-pget-n=10 ${REMOTE_DIR}
bye
EOF
echo "done"






lftp -e "set ftp:use-site-utime2 false; mirror -x ^\.git/$ -X flat-logo.png -p -R ftp-php-ap $PUB_FTP_DIR/ftp-php-app; exit" -u $USER,$PASSWORD $HOST


lftp -e "set ftp:use-site-utime2 false; set ftp:ssl-allow off; mirror -x ^\.git/$ -X flat-logo.png -p -R myfiles $REMOTE_DIR; exit" -u $FTP_USER,$FTP_PASSWORD $FTP_HOST



### An attempt to restore everything inside a brand new server (a github codespace) to test everything

    1  id
    2  ll
    3  mkdir -p /home/container_data/duplicati/
    4  sudo mkdir -p /home/container_data/duplicati/
    5  ll
    6  ls /home/container_data/
    7  ll /home/
    8  id
    9  chown -R codespace:codespace /home/container_data/
   10  sudo chown -R codespace:codespace /home/container_data/
   11  ll /home/
   12  ls
   13  ls /home/container_data/duplicati/
   14  ls /home/container_data/duplicatitemp/
   15  ls /home/container_data/duplicati/
   16  ls /home/container_data/duplicatitemp/
   17  ls /home/container_data/
   18  ls /home/container_data/backups/
   19  ls /home/container_data/duplicati/
   20  ls /home/container_data/duplicatitemp/
   21  ls /home/container_data/duplicati/
   22  ls /home/container_data/backups/
   23  ls /home/container_data/duplicati/
   24  ls /home/container_data/duplicatitemp/
   25  ls /home/container_data/backups/
   26  ls -la /home/container_data/duplicatitemp/
   27  ls -la /home/container_data/duplicati/
   28  sudp apt-get update
   29  sudo apt-get update
   30  sudo apt-get install lftp -y
   31  pwd
   32  mkdir enc_files
   33  cd enc_files/
   34  lftp -u ${FTP_USER},${FTP_PASSWORD} ${FTP_HOST}
   35  echo ${FTP_USER}
   36  source .env
   37  source ../.env 
   38  cat ../.env 
   39  echo ${FTP_USER}
   40  source .env
   41  source ../.env 
   42  echo ${FTP_USER}
   43  source ../.env 
   44  echo ${FTP_USER}
   45  lftp -u ${FTP_USER},${FTP_PASSWORD} ${FTP_HOST}  -e "set ftp:ssl-allow off"
   46  history > history.txt






