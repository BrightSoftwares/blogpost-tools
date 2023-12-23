---
author: full
categories:
- docker
date: 2022-01-15
description: Running your database inside a container is a very portable solution.
  It is also reproductible. But how do you manage the data inside that container?
  With my mysql server running in a docker container, I wanted to connect to it and
  manage it. The purpose of this tutorial is to share with you how to do it.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1644274461/pexels-ono-kosuki-5974245_c7quwi.jpg
inspiration: https://stackoverflow.com/questions/33827342/how-to-connect-mysql-workbench-to-running-mysql-inside-docker
lang: en
layout: flexstart-blog-single
ref: how-do-i-connect-mysql-workbench-to-mysql-inside-docker
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- mysql
- docker
- permission
- dockercompose
title: How do I connect mysql workbench to mysql inside Docker?
toc: true
---

Running your database inside a container is a very portable solution. Some applications like [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|Dolibarr]] or [[2022-05-31-solved-laravel-docker-image-could-not-open-input-file-var-www-html-artisan|laravel]] need a mysql database to run. You can compose them also inside a container. It is also reproductible. But how do you manage the data inside that container? 

With my mysql server running in a [[2022-08-24-what-is-difference-between-docker-attach-and-exec|docker]] container, I wanted to connect to it and manage it. The purpose of this [[2022-08-31-a-complete-tutorial-about-jenkins-file|tutorial]] is to share with you how to do it.


# What do we need ?

First, we will need a running [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|docker]] container running mysql.

I will [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] the [[2020-08-04-docker-tip-inspect-and-less|docker]] image `mysql/mysql-server:5.7` and I will name my container `mysql57` to ease my operations.

The **outside** port numbers that I choose to export my mysql service are `3306` and `33060`, you can change it if you want. 

> If you change the port number, make sure you change it in the rest of the commands

## Step 1: Start your container

### Case 1: You are using **docker-compose**


If you are using [[2021-12-14-how-to-use-local-docker-images-with-minikube|docker-compose]] prepare your configuration as follows.

```
services:
    db:
        image: mysql
		container_name: mysql57
        volumes:
            - "./.data/db:/var/lib/mysql"
        environment:
            MYSQL_ROOT_PASSWORD: root
            MYSQL_DATABASE: mydb
            MYSQL_USER: user
            MYSQL_PASSWORD: pass
        ports:
            3306:3306
```


In this [[2020-08-04-docker-tip-inspect-and-grep|docker]]-compose configuration we create a volume that points to the `/var/lib:mysql` folder. This means you can access the files inside that folder externally.

If you need to access other files, refer to this blog post to [[2022-07-28-how-to-copy-files-from-host-to-docker-container|copy a file from a docker container]].

We have also exposed a port from the [[2020-08-04-docker-tip-inspect-and-jq|docker]] container. Learn more about [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|accessing a docker container port here]]. You cann even [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|ping the docker container]] to check that it is working well.

If we wanted to access this mysql [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container from outside the host]], we could have bridged it. But this is not what we are going to do here, to keep things simple.

To start the container, run:

```
docker-compose up
```

This command will spin-up your container and expose the port on the local host.


### Case 2: You run your containers from command line

Start your container with the required ports :

```
docker run -p 3306:3306 -p 33060:33060 --name=mysql57 -d mysql/mysql-server:5.7
```

## Step 2: Get the mysql generated password

When MySQL start for the first time, it generates a password and print it on the console. We are going to use the `docker logs`  to read these console output and get the generated password.

To do so, run this command:

```
docker logs mysql57 2>&1 | grep GENERATED
```


It will print the line with the password.


## Step 3: Update the root user password

Connect to the `mysqld` server using the `mysql client`  inside the container.

```
docker exec -it mysql57 mysql -uroot -p
```

You will get a prompt inside the mysql server.

## Step 3.a: Check the users in the system

To check the users in the system, run this command:


```
mysql> select host, user from mysql.user;
+-----------+---------------+
| host      | user          |
+-----------+---------------+
| localhost | healthchecker |
| localhost | mysql.session |
| localhost | mysql.sys     |
| localhost | root          |
+-----------+---------------+
4 rows in set (0.00 sec)
```


## Step 3.b: Change the password (for fresh installations only)
If this is a fresh installation, the system will ask you to change the password using the `ALTER user`  command.

Do it.

Run the command:

```
update mysql.user set host = '%' where user='root';
```

Once it is done, quit the MySQL command prompt.

## Step 4: Restart the container

Now that the internal configuration is finished, restart the container.

```
docker restart mysql57

```


## Step 5: Check the status of the users (after config)

After the update, check again the users.

```
select host, user from mysql.user;
+-----------+---------------+
| host      | user          |
+-----------+---------------+
| %         | root          |
| localhost | healthchecker |
| localhost | mysql.session |
| localhost | mysql.sys     |
+-----------+---------------+
```




## Step 6: Connect to MySQL with the workbench

Here is the configuration to use for the connection :


```
host: `0.0.0.0` 
port: `3306`
```


The data inside the database can serve many purposes. One of this is to host [[2020-07-05-how-to-use-onetomany-database-relationships-with-flask-and-sqlite|a flask application with one to many relationship]].

Now that the container is running, feel free to [[2023-04-11-explore-your-container-with-docker-run|explore it with the docker exec command]].


# Conclusion

That's all. You can now connect to your MySQL container using MySQL workbench.

You can now connect an application to your database. A good next stop would be to use a [[2022-07-21-how-to-run-jenkins-jobs-with-docker|continuous integration and continous deployment tool like jenkins]].

Now that you have a working database and you can manage the data, you maybe interested in [[2020-04-04-how-to-set-up-a-remote-database-to-optimize-site-performance-with-mysql-on-ubuntu-1604|how to setup a remote database to optimize site performance]].

In this post, we did not focus on the user you are going to use to run your container. You can learn more about [[2022-08-03-how-do-i-run-a-docker-container-with-a-specific-user|running your container using a specific user]] in this blog post and whether you  [[2023-04-04-should-a-docker-container-run-as-root-or-user|need to run your container as root user or not]].

In our recent post on Docker containers, we explored the benefits of containerization and how it can help organizations achieve faster [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|nodejs development using docker]] and more efficient application deployment. Check out the post for more information on Docker containers and how they can benefit your organization.