---
ToReview: true
author: full
categories:
- wordpress
description: How To Install WordPress with LEMP on Ubuntu 16.04
image: https://sergio.afanou.com/assets/images/image-midres-25.jpg
lang: en
layout: flexstart-blog-single
ref: howtoinstallwordpress_with_lemp_ubuntu
seo:
  links:
  - https://www.wikidata.org/wiki/Q381
silot_terms: database cli ubuntu
tags:
- lemp
- wordpress
- ubuntu
- linux
title: How To Install WordPress with LEMP on Ubuntu 16.04
toc: true
---

LEMP stack is a popular software stack used for hosting dynamic websites and web applications. LEMP is an acronym for the following software components:

1.  Linux - The operating system on which the web server runs. Linux is open-source software and is widely used for web hosting due to its stability and security.
    
2.  Nginx - The web server that handles HTTP requests and serves web pages to clients. Nginx is known for its high [[2023-02-28-how-do-i-setup-a-remote-database-to-optimize-site-performance-with-MySQL|performance]], scalability, and efficient resource utilization.
    
3.  [[2023-03-28-create-and-audit-mysql-db-command-line|MySQL]]/MariaDB - The relational [[2023-03-07-how-to-choose-a-database-provider|database]] management system that stores data used by web applications. [[2020-04-04-how-to-set-up-a-remote-database-to-optimize-site-performance-with-mysql-on-ubuntu-1604|MySQL]]/MariaDB is a widely-used open-source [[2023-03-14-how-do-i-optimize-my-database|database]] system and is known for its stability, scalability, and security.
    
4.  PHP - The server-side scripting language used to create dynamic web pages and web applications. PHP is widely-used and is known for its ease of use and ability to integrate with various web technologies.
    

Together, these software components form a complete web application stack that can handle large amounts of [[2023-02-24-how-to-optimize-network-traffic-for-a-database|traffic]] and scale easily. The LEMP stack is commonly used for hosting popular content management systems like WordPress, Drupal, and Joomla, as well as custom web applications.

## How to install WordPress with LEMP on Ubuntu

### Step 1.  Update your Ubuntu system 

Update your [[2023-05-06-git-lfs-install-ubuntu-a-comprehensive-guide|Ubuntu]] system by running the following commands:

```bash
sudo apt update sudo apt upgrade
```

### Step 2.  Install Nginx web server 

Install Nginx web server by running the following command:

```bash
sudo apt install nginx
```

### Step 3.  Install MySQL database server 

Install MySQL [[2023-03-21-how-to-secure-a-remote-database-from-unauthorized-access|database]] server by running the following command:

```bash
sudo apt install mysql-server
```

### Step 4.  Secure your MySQL installation 

Secure your MySQL installation by running the following command:

```bash
sudo mysql_secure_installation
```

During the installation, you will be asked to configure some settings. Follow the instructions and answer the questions.

### Step 5.  Install PHP and necessary extensions

Install PHP and necessary extensions by running the following command:

```bash
sudo apt install php-fpm php-mysql php-curl php-gd php-mbstring php-xml php-xmlrpc
```

### Step 6.  Edit the Nginx configuration file 

Edit the Nginx configuration file by running the following command:

```bash
sudo nano /etc/nginx/sites-available/default
```

### Step 7.  Update the configuration content

Replace the contents of the file with the following code:

```bash
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/html;
    index index.php index.html index.htm;

    server_name _;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php7.4-fpm.sock;
    }
}

```

Note: This code is for PHP version 7.4, if you have a different version, update it accordingly.

### Step 8.  Test the Nginx configuration 

Test the Nginx configuration by running the following command:

```bash
sudo nginx -t
```

### Step 9.  Restart the Nginx service


If there are no errors, restart the Nginx service by running the following command:

```bash
sudo systemctl restart nginx
```

### Step 10.  Create a new MySQL database and user 


Create a new MySQL database and user for WordPress by running the following commands:

```bash
sudo mysql -u root -p
```

Enter the MySQL root password when prompted.

```sql
CREATE DATABASE wordpress; CREATE USER 'wordpressuser'@'localhost' IDENTIFIED BY 'password'; GRANT ALL PRIVILEGES ON wordpress.* TO 'wordpressuser'@'localhost'; FLUSH PRIVILEGES; EXIT;
```

Note: Replace 'password' with a strong password of your choice.

### Step 11.  Download the latest WordPress installation package

Download the latest WordPress installation package by running the following command:

```bash
cd /tmp curl -O https://wordpress.org/latest.tar.gz
```

### Step 12.  Extract the downloaded file

Extract the downloaded file by running the following command:

```bash
tar xzvf latest.tar.gz
```

### Step 13.  Copy the extracted WordPress files


Copy the extracted WordPress files to the Nginx document root directory by running the following command:

```


`sudo cp -r /tmp/wordpress/* /var/www/html`
```

### Step 14.  Set the correct permissions

Set the correct permissions and ownership for the WordPress files by running the following commands:

```bash
sudo chown -R www-data:www-data /var/www/html sudo chmod -R 755 /var/www/html
```

### Step 15.  Access your WordPress installation 

Access your WordPress installation by opening a web browser and navigating to your server's IP address or domain name.



### Step 16.  Follow the WordPress installation wizard

Follow the WordPress installation wizard and enter the database name, username, and password you created in step 10.

## Conclusion

That's it! You should now have a working WordPress installation with LEMP on Ubuntu.