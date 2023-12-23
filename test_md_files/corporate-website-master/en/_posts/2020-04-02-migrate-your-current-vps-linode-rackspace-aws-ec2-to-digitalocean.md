---
layout: flexstart-blog-single
title:  "Migrate Your Current VPS (Linode, Rackspace, AWS EC2) to DigitalOcean"
author: full
lang: en
ref: migrate_yourcurrent_vps
categories: [ aws ]
description: "Migrating between VPS providers can seem like a daunting task. Like DigitalOcean, other VPS providers, such as Linode and Rackspace, provide root access. This allows you to transfer all of the necessary files to your new DigitalOcean VPS. For this guide, we will demonstrate how to transfer a simple WordPress blog from Linode to a DigitalOcean cloud server."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1642606953/pexels-cottonbro-4569340_y7otyd.jpg
tags:
  - digitalocean
  - wordpress
  - lamp
  - vps
  - linux
seo:
  links: [ "https://www.wikidata.org/wiki/Q456157" ]
toc: true
---



Migrating between VPS providers can seem like a daunting task. Like [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|DigitalOcean]] , other [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|VPS]] providers, such as Linode and Rackspace, provide root access. This allows you to transfer all of the necessary files to your new DigitalOcean VPS.

For this guide, we will demonstrate how to transfer a simple [[2020-04-04-how-to-install-wordpress-with-lemp-on-ubuntu-1604|Wordpress]] blog from Linode to a DigitalOcean cloud server.


Both instances will be running Ubuntu. These instructions can be adapted to migrate other services from other providers. We will be working as root in both VPS instances.

# What the ```Red``` Means

The lines that the user needs to enter or customize will be in red in this tutorial! The rest should mostly be copy-and-pastable.


# Preliminary DigitalOcean Cloud Server Configuration

## LAMP Installation

To begin, you will want to install a [[2020-04-04-how-to-install-wordpress-with-lamp-on-ubuntu-1604|LAMP]] (Linux, Apache, MySQL, PHP) stack on your DigitalOcean cloud server. This can be accomplished in a few different ways.

The easiest way to get LAMP up and running on Ubuntu is to choose the pre-configured "LAMP on Ubuntu" image when you are initially creating your droplet. 

In the ```"Select Image"``` portion of the Droplet creation page, choose the ```"Applications"``` tab. Select ```"LAMP on Ubuntu 14.04"```.

If you already have a droplet that you would like to use, you can install a LAMP stack on Ubuntu by following this link.


## Rsync Installation

We will be doing our file transfers using ssh and rsync. Make sure rsync is installed on your DigitalOcean VPS using the following command:

```
rsync --version
```


If this command returns a "command not found" message, then you need to install rsync with apt-get:

```
apt-get install rsync
```


## Communicating Between VPS Servers

The following steps will take place on your old VPS. If you aren't already, log in as root.
Your old VPS also needs to have rsync installed. Re-run the check for rsync on this system:

```
rsync --version
```


If necessary, install rsync:

```
apt-get install rsync
```

In order to transfer the relevant information from our previous VPS to our DigitalOcean cloud server, rsync needs to be able to log into our new server from our old server. We will be using SSH to do this.

If you do not have SSH keys generated on your old VPS, create them now with the following command:

```
ssh-keygen -t rsa -b 4096 -v
```


Answer the prompts as required. Feel free to press "Enter" through all of the prompts to accept the default values.


Next, transfer the SSH key to our new VPS using the following command. Change the portion in red to reflect your DigitalOcean VPS IP address:

```
ssh-copy-id 111.222.333.444
```


## Transferring Site Files


First, we will be transferring the files in our old server's web root to our new cloud server. We will find where our WordPress web root is by examining the configuration file. We will look at the sites-enabled directory to find the correct VirtualHost file:

```
cd /etc/apache2/sites-enabled
ls
li606-185.members.linode.com
```


Here, our file is called ```"li606-185.members.linode.com"```, but yours may be something different. 

Open the file in nano:

```
nano li606-185.members.linode.com
```


We are looking for the "DocumentRoot" line to tell us which directory our web content is being served from. 
In our example, the line reads:

```
DocumentRoot /srv/www/li606-185.members.linode.com/public_html/
```


Close the file and cd into that directory:

```
cd /srv/www/li606-185.members.linode.com/public_html/
ls -F
```


Output

```
latest.tar.gz wordpress/
```


As you can see, we have a directory for our WordPress site. This contains all of the web content for our site. We will transfer this entire directory, along with its permissions and sub-directories, from this location into the web root of our DigitalOcean cloud server. By default, apache2 on Ubuntu 14.04 serves its content out of "/var/www/html", so that is where we will place this content.


We will add some options to rsync in order for it to transfer properly. The ```"-a"``` option stands for archive, which allows us to transfer recursively while preserving many of the underlying file properties like permissions and ownership.


We also use the ```"-v"``` flag for verbose output, and the "-P" flag, which shows us transfer progress and allows rsync to resume in the event of a transfer problem.

```
rsync -avP wordpress 111.222.333.444:/var/www/html/
```

Note how there is no trailing slash after "wordpress", but that there is in ```"/var/www/html/"```. This will transfer the ```"wordpress"``` directory itself to the destination instead of only transferring the directory contents.

Our entire WordPress directory structure has now been transferred to the web root of the new cloud server.

At this point, if we direct our web browser to our new cloud server's IP address and try to access our WordPress site, we will get a MySQL error:


```
111.222.333.444/wordpress
Error establishing a database connection
```


This is because WordPress stores its data in a MySQL database that has not been transferred yet. We will handle the MySQL transfer next.


## MySQL Database Transfer


The best way to transfer MySQL databases is to use MySQL's internal database ```dumping utility```. First, we will see what databases we need to dump. 

Log into MySQL:


```cd
mysql -u root -p
```


Enter the database administrator's password to continue. List the MySQL databases with the following command:

```
show databases;
+--------------------+
| Database |
+--------------------+
| information_schema |
| mysql |
| wordpress |
+--------------------+
3 rows in set (0.00 sec)

```


We would like to transfer our "wordpress" database, which contains our site information, and also our "mysql" database, which will transfer all of our user info, etc. The "information_schema" is just data structure information, and we don't need to hold onto that.

Get an idea of which databases you want to transfer for the next step. 

Exit out of MySql:

```
exit
```


We will be dumping the database information with ```"mysqldump"``` and then compressing it with "bzip2". We will use a number of parameters to make our databases import cleanly. 

Replace the red with your database names:

```
mysqldump -u root -p -QqeR --add-drop-table --databases mysql wordpress | bzip2 -v9 - > siteData.sql.bz2

```


Again, enter your database administrator's password to continue.

We now have a zipped database file that we can transfer to our new cloud server. We will use rsync again. 

Change the IP address to reflect your DigitalOcean server's IP address:

```
rsync -avP siteData.sql.bz2 111.222.333.444:/root
```


## Importing the Databases

Our database file is compressed and transferred to our new DigitalOcean cloud server. We must import it into MySQL on our new server so that WordPress can utilize it.

Log into your DigitalOcean cloud server as root for the following steps.
Our database file was transferred to the root user's home directory, so move to that directory now. 

We will uncompress the file using "bunzip2":

```
cd /root
bunzip2 siteData.sql.bz2
```


Now we can import the file into our new MySQL database:

```
mysql -u root -p < siteData.sql
```


Let's check to see that MySQL has imported correctly:

```
mysql -u root -p
show databases;
+--------------------+
| Database |
+--------------------+
| information_schema |
| mysql |
| performance_schema |
| test |
| wordpress |
+--------------------+
5 rows in set (0.00 sec)
```


As you can see, our "wordpress" database is present. The previous "mysql" database has been replaced with the one from our old VPS.

Exit out of MySQL:

```
exit
```

Now we will restart our database and our server for good measure:

```
service mysql restart
service apache2 restart
```

Now, if we navigate to our DigitalOcean VPS IP address followed by "/wordpress", we will see the WordPress site that was previously hosted on our old VPS:

```
111.222.333.444/wordpress
```

# Final Considerations

Before changing over your domain name to point to your new site location, it is important to test your setup extensively. It is a good idea to reference the services that were running on your old VPS, and then check their configuration files. You can see the services that were running on your old VPS by logging in and typing:

```
netstat -plunt
```

```
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address Foreign Address State PID/Program name
tcp 0 0 127.0.0.1:3306 0.0.0.0:_ LISTEN 13791/mysqld  
tcp 0 0 0.0.0.0:22 0.0.0.0:_ LISTEN 10538/sshd  
tcp 0 0 127.0.0.1:25 0.0.0.0:_ LISTEN 13963/master  
tcp6 0 0 :::80 :::_ LISTEN 13771/apache2  
tcp6 0 0 :::22 :::_ LISTEN 10538/sshd  
udp 0 0 0.0.0.0:68 0.0.0.0:_ 2287/dhclient3
```

Here, we can see the services in the last column that we will want to configure on our new server. Your list will probably be different.

Each service has its own configuration syntax and configuration location, so you will need to check the documentation on a case-by-case basis.


As an example, if we wanted to replicate the configuration of our SSH daemon on our new VPS we could transfer the configuration file to the home directory of our new VPS using rsync:

```
rsync -avP /etc/ssh/sshd_config 111.222.333.444:/root
```


After we've transferred the file, we do not want to simply replace the default file with the one from our old VPS.

Different versions of programs can introduce changes to the syntax. Issues can also arise from configuration options that were specific to your old VPS. Options referencing hostnames, IP addresses, or file paths will need to be changed to reflect your new setup.


It is safer to produce a diff of the files so that you can adjust your new cloud server's native configuration file as necessary.

There are a number of different programs that can give you the differences between two files. One is simply diff:

```
diff /root/sshd_conf /etc/ssh/sshd_config
```

This will produce a list of all of the differences between the two files. You can examine the differences and take them into consideration. Some configuration options you might want to incorporate from your old setup, while others you might want to modify or discard.


If you still have AWS EC2, in the T-xxx family, take a look to [[2020-02-12-amazons-t3-who-should-use-it-when-how-and-the-why|this tutorial]] that will walk you through the steps to better use that EC2 server family.