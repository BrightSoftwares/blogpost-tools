---
author: full
categories:
- database
description: 'On my website installation, I need a mysql database to store my posts
  and configuration. During the configuration, I suddently run into a strange error:
  mysql server is complaining about authentication issues. Here is how I solved it.'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1646322256/kyle-glenn-dGk-qYBk4OA-unsplash_irufoi.jpg
inspiration: https://stackoverflow.com/questions/2995054/access-denied-for-user-rootlocalhost-using-passwordno?noredirect=1&lq=1
lang: en
layout: flexstart-blog-single
ref: 2022-03-03-how-to-solve-access-denied-for-user-root-localhost-using-password-no-unable-to-authenticate-php-mysql
seo:
  links:
  - https://www.wikidata.org/wiki/Q59
silot_terms: database mysql
tags:
- mysql
- windows
title: 'How to solve Access denied for user ''root''@''localhost'' (using password:
  NO)?Unable to authenticate php/Mysql'
toc: true
---

On my website installation, I need a mysql [[2020-07-05-how-to-use-onetomany-database-relationships-with-flask-and-sqlite|database]] to store my posts and configuration. During the configuration, I suddently run into a strange error: mysql [[2023-11-24-the-odbc-sql-server-driver|server]] is complaining about authentication issues. Here is how I solved it.

# The TL;DR anwser

Run this command:

```
mysql -u root -p
```

When you are prompted for the password, **hit enter key** (leave the password blank).


# My setup

I am working on windows machine. I used the `Web Platform Installer` to have a development stack on my machine.
I am intending to use [[2020-04-04-how-to-install-wordpress-with-lamp-on-ubuntu-1604|Wordpress]] for my website.

***Important note***: I never set a password for the MySQL during the install process.

## Attempt to connect without password

To connect to the database, I used the following command:

```
mysql -u root -p
```

Then it asks a password which I don't have. :(


## Attempt to connect with a password

I tried to connect using this command.

```
mysql -u root password '123'
```


Then it throws this back:

```
Access denied for user 'root@localhost' (using password:NO)
```


# The solution

## First, I made a mistake

There is a mistake in the command I ran. For the password, you need to use either `-p` or `--password`.

So this command is wrong.

```
mysql -u root password '123'
```

The right command is:

```
mysql -u root --password '123'
```


## The default password

The default password for `root` for the installation is **`blank`**. Not the litteral word, but "nothing".


## The steps to solve

Connect to the MySQl server with blank password.

Run this command:

```
mysql -u root -p
```

When you are prompted for the password, **hit enter key** (leave the password blank).

After that, you can set a password for the `root` user.


# Conclusion

To fix the issue you are having, you first need to:

 - check that your command is correct.
 - connect to the MySQL server with root account and blank password.
 - set a password for root user.