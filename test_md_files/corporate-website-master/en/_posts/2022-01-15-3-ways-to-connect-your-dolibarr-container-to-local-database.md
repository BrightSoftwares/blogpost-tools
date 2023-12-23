---
author: full
categories:
- docker
date: 2022-01-15
description: One of the priorities of a system administrator is the performance optimization
  of the deployments and the underlying infrastructure. I have a deployed and running
  mariadb on a linux server. It is optimized for performance and database storage.
  Now I am planning deploying a dolibarr docker container on top of it. How can I
  connect from the dolibarr docker container to the local mariadb database?
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1642938172/pexels-joshua-welch-1624600_pxc6ym.jpg
inspiration: https://superuser.com/questions/1254515/setup-a-docker-container-to-work-with-a-local-database
lang: en
layout: flexstart-blog-single
ref: 3waystoconnectyourOdoocontainertolocaldatabase
seo:
  links:
  - https://www.wikidata.org/wiki/Q19841877
silot_terms: devops pipeline
tags:
- dolibarr
- docker
- container
- database
title: 3 ways to connect your Dolibarr container to local database
toc: true
---

One of the priorities of a system administrator is the performance optimization of the deployments and the underlying infrastructure. I have a deployed and running mariadb on a [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|linux]] server. It is optimized for performance and database storage. Now I am planning deploying a dolibarr [[2022-07-21-how-to-run-jenkins-jobs-with-docker|docker]] [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|container]] on top of it.
	
How can I [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|connect]] from the dolibarr [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|docker]] [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|container]] to the local mariadb database?

There are 3 ways you can connect your [[2023-04-11-explore-your-container-with-docker-run|container]].

Let's go through them.

## 1. Use the `--net=host` option

> Important note: this option does not work on Mac OS X. If you are running OS X, jump to the second option.

When you run your [[2022-08-24-what-is-difference-between-docker-attach-and-exec|docker]] container, you can pass the option `--net=host` like this:

```
docker run --net=host ... tuxgasy/dolibarr
```

When you [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] that option, [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|docker]] uses the hosts network stack for your container. That means that the container will have access to the whole host network stack. The container shares the services and ports available on the host.

Once in that mode the container has direct access to localhost. You can now access localhost:3306.

> Note: This configuration does not provide any network isolation to the container.


## 2. Mount the service socket into the container

The idea here is to use the MariaDb database socket available on the host and mount it into the container.

> What is a socket?
> A _socket_ is one endpoint of a two-way communication link between two programs running on the network. A socket is bound to a port number so that the TCP layer can identify the application that data is destined to be sent to.
> Source: [Oracle docs](https://docs.oracle.com/javase/tutorial/networking/sockets/definition.html)

On the host, the socket is installed in the directory `/var/run/mysqld`. We are going to mount that socket into the container.


```
docker run -v /var/run/mysqld:/mariadb_socket ... tuxgasy/dolibarr
```

Then, to access the database from the container, connect to the socket located at `/mariadb_socket/mysqld.sock`

## 3. Connect to the docker host IP

[[2020-08-04-docker-tip-inspect-and-less|Docker]] has a network stack called `docker0`. 
The idea in this method is to find the IP address of that network and connect to it.

Start a command prompt and type `ip addr`

Look for the `docker0` network. The IP address looks like `172.17.0.1`.

> The result on your command line prompt might be different


![Docker0 IP address, source: tecmint.com](https://res.cloudinary.com/brightsoftwares/image/upload/v1642934808/Check-Docker-IP-Address_ygq4bh.png)

Now that you have the IP address, you can use it in your [[2020-08-04-docker-tip-inspect-and-grep|docker]] container by connecting to `172.17.0.1:3309`.

# Conclusion

We are detailed 3 ways to connect our dolibarr frontend container to the database located into your local server.
Let me know in the comments if you have other ways.

If you have local [[2020-08-04-docker-tip-inspect-and-jq|docker]] images you want to use locally, head to [[2021-12-14-how-to-use-local-docker-images-with-minikube|this tutorial]]. You will be in good hands.