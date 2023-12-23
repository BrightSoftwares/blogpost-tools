---
ToReview: true
author: full
categories:
- webdevelopment
description: LAMP stack is a popular web application platform that consists of four
  open-source components that work together to run dynamic websites and web applications.
  The four components of LAMP stack are
image: https://sergio.afanou.com/assets/images/image-midres-30.jpg
lang: en
layout: flexstart-blog-single
ref: howtoinstall_wordpress_with_lamp
seo:
  links:
  - https://www.wikidata.org/wiki/Q381
silot_terms: server dev and admin
tags:
- lamp
- wordpress
- ubuntu
- linux
title: How To Install WordPress with LAMP on Ubuntu 16.04
toc: true
---

## What is LAMP stack

LAMP stack is a popular [[2023-11-27-hp-web-services-not-working-troubleshooting-tips|web]] application platform that consists of four open-source components that work together to run dynamic websites and web applications. The four components of LAMP stack are:

Linux operating system - the foundation of the stack, which serves as the operating system for the web server.

Apache web server - an open-source web server software that is used to serve web pages and applications.

MySQL database server - a relational database management system that stores and manages data for web applications.

PHP - a server-side scripting language that is used to write dynamic web pages and web applications.

Together, these four components provide a complete and powerful platform for building and deploying web applications. LAMP stack is widely used by developers and webmasters for creating and hosting dynamic websites, content management systems, and e-commerce platforms, among other applications.

If you're interested in learning more about the LAMP stack, our blog post on [[2022-09-14-what-is-the-lamp-stack.md|lamp stack full form]] has everything you need to know.


## How to install LAMP stack on Ubuntu

I am going to give you the detailed steps for installing WordPress with LAMP on Ubuntu:


### Step 1: let's install Apache and MySQL 

Update your Ubuntu system by running the following commands:

```bash
sudo apt update
sudo apt upgrade
```


Install Apache web server by running the following command:


```bash
sudo apt install apache2
```

Install MySQL database server by running the following command:

```bash
sudo apt install mysql-server
```

### Step 2: Let's secure our MySQL server 

Secure your MySQL installation by running the following command:

```bash
sudo mysql_secure_installation
```

During the installation, you will be asked to configure some settings. Follow the instructions and answer the questions.


### Step 3: Install PHP to be able to run WordPress 


Install PHP and necessary extensions by running the following command:


```bash
sudo apt install php libapache2-mod-php php-mysql php-curl php-gd php-mbstring php-xml php-xmlrpc
```


### Step 4: Create a MySQL user for WordPress 

Create a new MySQL database and [[2023-05-04-current-user-what-it-is-and-how-it-can-help-your-business|user]] for WordPress by running the following commands:

```bash
sudo mysql -u root -p
```

Enter the MySQL root password when prompted.

```sql
CREATE DATABASE wordpress;
CREATE USER 'wordpressuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON wordpress.* TO 'wordpressuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Note: Replace 'password' with a strong password of your choice.


### Step 5: Download and install WordPress 


Download the latest WordPress installation package by running the following command:

```bash
cd /tmp
curl -O https://wordpress.org/latest.tar.gz
```


Extract the downloaded file by running the following command:

```bash
tar xzvf latest.tar.gz
```


Copy the extracted WordPress files to the Apache document root directory by running the following command:

```bash
sudo cp -r /tmp/wordpress/* /var/www/html
```


Note: If you're interested in learning how to How To Create a New Sudo-enabled User on Ubuntu 20.04, our blog post on [[2020-07-05-how-to-create-a-new-sudoenabled-user-on-ubuntu-2004-quickstart.md|ubuntu create new sudo user]] has everything you need to know.


Set the correct permissions and ownership for the WordPress files by running the following commands:

```bash
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
```

### Step 6: configure Apache to serve WordPress 

Create a new Apache configuration file for your WordPress site by running the following command:

```bash
sudo nano /etc/apache2/sites-available/wordpress.conf
```


Add the following code to the file:

```
<VirtualHost *:80>
    ServerAdmin admin@example.com
    DocumentRoot /var/www/html
    ServerName example.com
    ServerAlias www.example.com

    <Directory /var/www/html/>
        Options FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

Note: Replace 'example.com' with your own domain name.

Our blog post on [[2020-07-05-how-to-create-a-selfsigned-ssl-certificate-for-apache-on-centos-8.md|generate ssl certificate apache]] explores how to create a self-signed SSL certificate for Apache on CentOS 8.


Enable the new Apache configuration by running the following command:

```bash
sudo a2ensite wordpress.conf
```

Restart Apache by running the following command:

```bash
sudo systemctl restart apache2
```

### Step 7: Enjoy your installation 🎉

Access your WordPress installation by opening a web browser and navigating to your server's IP address or domain name.

Follow the WordPress installation wizard and enter the database name, username, and password you created in step 4.

That's it! You should now have a working WordPress installation with LAMP on Ubuntu.