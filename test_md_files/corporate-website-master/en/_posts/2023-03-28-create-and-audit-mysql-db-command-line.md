---
ToReview: true
author: full
categories:
- wordpress
date: 2023-03-28
description: Quick steps to create, connect, generate a database and audit it's performance
  from a command line.
image: https://sergio.afanou.com/assets/images/image-midres-29.jpg
lang: en
layout: flexstart-blog-single
ref: create-and-audit-mysql-db-command-line
seo:
  links:
  - https://www.wikidata.org/wiki/Q381
silot_terms: database cli ubuntu
tags:
- ubuntu
- mysql
- performance
- wordpress
title: Create and audit a MySQL database from command line
toc: true
---

## Step 1. Connect to a mysql server and then create a database

To generate the SQL script to connect to a [[2020-04-04-how-to-set-up-a-remote-database-to-optimize-site-performance-with-mysql-on-ubuntu-1604|MySQL]] server, you can use the following command:

```bash
mysql -h <hostname> -u <username> -p<password>
```


Replace `<hostname>` with the hostname or IP address of the MySQL server, `<username>` with the username you want to use to connect to the server, and `<password>` with the password for the username. This will open a MySQL command prompt where you can enter SQL commands.



## Step 2: Create a database 

To create a [[2023-02-28-how-do-i-setup-a-remote-database-to-optimize-site-performance-with-MySQL|database]], use the following SQL command:

```sql
CREATE DATABASE <database_name>;
```

Replace `<database_name>` with the name you want to give to the [[2023-03-07-how-to-choose-a-database-provider|database]]. This will create a new [[2023-03-14-how-do-i-optimize-my-database|database]] with the specified name on the MySQL server. You can then use this [[2023-03-21-how-to-secure-a-remote-database-from-unauthorized-access|database]] to create tables and store data.

Note that you will need to be logged in to the MySQL server using a privileged user account that has permission to create databases in order to execute this command.



## Step 3: Provide read write and execute access to a user

To provide read, write, and execute access to a user in MySQL, you can use the GRANT statement. Here's an example of how to grant these permissions to a user for a specific [[2023-02-24-how-to-optimize-network-traffic-for-a-database|database]]:

```sql
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON <database_name>.* TO '<username>'@'<hostname>' IDENTIFIED BY '<password>';
```


Replace `<database_name>` with the name of the database you want to grant access to, `<username>` with the username you want to grant access to, `<hostname>` with the hostname or IP address of the client machine the user will be connecting from (use '%' to allow access from any host), and `<password>` with the password for the username.

This statement grants the following permissions to the user:

-   SELECT: read access to tables in the database
-   INSERT: write access to tables in the database
-   UPDATE: update access to tables in the database
-   DELETE: delete access to tables in the database
-   EXECUTE: execute access to stored procedures and functions in the database

You can also use more specific permission options such as CREATE, DROP, ALTER, and INDEX, depending on the requirements of your application.

## Step 4: Measure the server's performance


To measure MySQL server performance, you can use a combination of MySQL's built-in performance monitoring tools and external monitoring tools. Here's an example of a script that uses some of these tools to measure MySQL server performance:

```bash
#!/bin/bash

# Set the variables for the MySQL server connection
MYSQL_USER="your_mysql_username"
MYSQL_PASSWORD="your_mysql_password"
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_DATABASE="your_mysql_database_name"

# Set the time interval for monitoring (in seconds)
INTERVAL=5

# Set the path to the MySQL command-line client
MYSQL_CMD="/usr/bin/mysql"

# Loop continuously to monitor performance
while true
do
  # Get the current time
  DATE=$(date +%Y-%m-%d\ %H:%M:%S)

  # Get the current CPU and memory usage of the MySQL process
  PID=$(pgrep -f /usr/sbin/mysqld)
  CPU=$(ps -p $PID -o %cpu | tail -n 1)
  MEM=$(ps -p $PID -o %mem | tail -n 1)

  # Get the current number of connections to the MySQL server
  CONNECTIONS=$($MYSQL_CMD -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD -e "SHOW STATUS WHERE Variable_name = 'Threads_connected';" $MYSQL_DATABASE | awk '{print $2}')

  # Get the current number of queries per second on the MySQL server
  QPS=$($MYSQL_CMD -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD -e "SHOW STATUS WHERE Variable_name = 'Queries';" $MYSQL_DATABASE | awk '{print $2}')
  sleep $INTERVAL
  QPS=$((($($MYSQL_CMD -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD -e "SHOW STATUS WHERE Variable_name = 'Queries';" $MYSQL_DATABASE | awk '{print $2}')-$QPS)/$INTERVAL))

  # Output the current performance metrics
  echo "$DATE CPU=$CPU% MEM=$MEM% Connections=$CONNECTIONS QPS=$QPS"
done

```

This script uses the following techniques to measure MySQL server performance:

-   It gets the current CPU and memory usage of the MySQL process using the `ps` command.
-   It gets the current number of connections to the MySQL server and the current number of queries per second using MySQL's `SHOW STATUS` command.
-   It calculates the queries per second by measuring the difference in queries over a set interval of time.

You can customize this script to monitor additional performance metrics or to output the metrics to a log file or other location.