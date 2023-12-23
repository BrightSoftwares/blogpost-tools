---
author: full
categories:
- docker
date: 2023-05-12
description: I am the happy administrator of an nginx docker container running in
  front of an application using a mysql database. The database runs on the host of
  the docker container and the container is not bound to the IP address of the machine.
  The challenge today is to connect to the mysql database from the docker container.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1643965648/pexels-fauxels-3182746_dwlzff.jpg
image_search_query: data storage
lang: en
layout: flexstart-blog-single
post_date: 2023-05-12
pretified: true
ref: running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: container docker kubernetes
tags:
- nginx
- mysql
- docker
title: Running MySQL Server in Docker Container and Connecting to it from Host Machine
transcribed: true
youtube_video: http://www.youtube.com/watch?v=20om-9Gwuc0
youtube_video_id: 20om-9Gwuc0
---

To [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] MySQL server in a [[2022-05-08-can-docker-connect-to-database|Docker]] [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]] and [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|connect]] to it from your [[2022-07-28-how-to-copy-files-from-host-to-docker-container|host]] [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|machine]], follow these steps:

## Pull MySQL Image

First, you need to pull the MySQL image. [[2021-12-14-how-to-use-local-docker-images-with-minikube|Use]] the following command to pull the static [[2023-12-15-release-management-with-tiller-in-helm-version-2|version]] 8:

```
docker pull mysql:8
```

## Run MySQL Container

Next, [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] the MySQL [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]] using the following command. Note that we are specifying a root password using the -e flag. In this [[2023-08-25-docker-exec-bash-example|example]], we will [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] "123" as the password.

```
docker run -d -p 3306:3306 --name mysql-server -e MYSQL_ROOT_PASSWORD=123 mysql:8
```

The above command will start a MySQL [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]] and [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|run]] it in the background. You can confirm that the [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|container]] is running using the following command:

```
docker ps
```

This will [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|show]] you a list of running containers.

## Connect to MySQL Container

Now, you can [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|connect]] to the MySQL [[2023-10-29-docker-run-stopped-container|container]] using the MySQL client installed on your host [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|machine]]. To [[2022-05-08-can-docker-connect-to-database|connect]] to the MySQL [[2023-05-14-understanding-kubernetes-the-container-orchestrator|container]], [[2023-10-25-using-helm-practical-use-cases|use]] the following command:

```
mysql -u root -p -h 127.0.0.1 -P 3306
```


When prompted, enter the root password you specified earlier (in this case, "123"). This will [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|connect]] you to the MySQL server running inside the [[2023-11-22-monit-docker-container-a-comprehensive-guide|container]].

Alternatively, you can run a MySQL command inside the [[2023-05-15-understanding-container-networking|container]] using the following command:

```
docker exec -it mysql-server mysql -uroot -p -e "SELECT VERSION();"
```

This will run the `SELECT VERSION();` command inside the container and return the version of MySQL that is currently running.

If you want to create a database inside the container, you can run the following command:

```
docker exec -it mysql-server mysql -uroot -p -e "CREATE DATABASE dbname;"
```

Replace `dbname` with the name of the database you want to create.

Note that if you are using Windows, you may need to specify a different IP address and [[2021-12-26-how-to-expose-a-port-on-minikube|port]] when connecting to the MySQL container. You can specify a [[2021-12-26-how-to-expose-a-port-on-minikube|port]] mapping when running the container using the -p flag.