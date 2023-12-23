---
author: full
categories:
- kubernetes
date: 2022-07-28
description: In my daily work, I have utility containers. Some are based on ubuntu,
  others just on busy box. I start them, run few commands and destroy them. For some
  specific task I need a long running container and populate it with files that are
  from the host. And after my work is done, I copy the result from the container back
  to the host.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551295/pexels-tom-fisk-3840441_iqdghj.jpg
inspiration: https://stackoverflow.com/questions/31249112/allow-docker-container-to-connect-to-a-local-host-postgres-database
lang: en
layout: flexstart-blog-single
pretified: true
ref: how-to-copy-files-from-host-to-docker-container
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: container docker kubernetes
tags:
- docker
- kubernetes
- container
title: How to copy files from host to Docker container?
toc: true
---

In my daily [[2020-08-13-work-with-kubernetes-with-minikube|work]], I have utility containers. Some are based on [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|ubuntu]], others just on busy box. I start them, [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] few commands and destroy them. 

For some specific task I need a long [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|running]] [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]] and populate it with files that are from the [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|host]]. And after my [[2020-08-13-work-with-kubernetes-with-minikube|work]] is done, I copy the result from the [[2023-04-04-should-a-docker-container-run-as-root-or-user|container]] back to the host.


# The post used command is docker cp

According to the reference: [Docker CLI docs for `cp`](https://docs.docker.com/engine/reference/commandline/cp/), the ```cp``` command is the best suited for this task.  It is used to copy files.

## Get the container's ID

To know your [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|container]]'s ID, you need to [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|run]] this command:

```
docker ps
```

This command list all the running containers. Locate yours and note its ID.

## Get the full container ID (optionnal)

To get the full [[2023-10-29-docker-run-stopped-container|container]] ID, run this command (replace ```SHORT_CONTAINER_ID-or-CONTAINER_NAME``` with what is applicable to your [[2023-05-14-understanding-kubernetes-the-container-orchestrator|container]]):

```
docker inspect -f   '{{.Id}}'  SHORT_CONTAINER_ID-or-CONTAINER_NAME
```

For [[2023-08-25-docker-exec-bash-example|example]]:

```bash
docker ps
```

Gives this response:

```bash
CONTAINER ID      IMAGE    COMMAND       CREATED      STATUS       PORTS        NAMES

d8e703d7e303   solidleon/ssh:latest      /usr/sbin/sshd -D                      cranky_pare
```

Then you can run this command to get the full ID:

```bash
docker inspect -f   '{{.Id}}' cranky_pare
```

You get this result:

```
d8e703d7e3039a6df6d01bd7fb58d1882e592a85059eb16c4b83cf91847f88e5
```


## Copy files from the host to the container

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1656261241/brightsoftwares.com.blog/llpuytvl3lvcske4fw14.png)


One specific file can be copied TO the [[2023-11-22-monit-docker-container-a-comprehensive-guide|container]] like:

```
docker cp foo.txt container_id:/foo.txt
```

## Copy files from the container to the host (at the end of my tasks)

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1656261220/brightsoftwares.com.blog/dknv7ggea4lrybtxkqbx.png)


One specific file can be copied FROM the [[2023-05-15-understanding-container-networking|container]] like:

```
docker cp container_id:/foo.txt foo.txt
```

For emphasis, `container_id` is a _container_ ID, **not** an _image_ ID. ([[2021-12-14-how-to-use-local-docker-images-with-minikube|Use]] `[[2022-05-08-can-docker-connect-to-database|docker]] ps` to view listing which includes `container_id`s.)

[[2023-08-20-managing-multiple-clusters-with-argocd|Multiple]] files contained by the folder `src` can be copied into the `target` folder using:

```
docker cp src/. container_id:/target
docker cp container_id:/src/. target
```


> **Note:** In [[2021-12-14-how-to-use-local-docker-images-with-minikube|Docker]] versions prior to 1.8 it was only possible to copy files from a container to the host. Not from the host to a container.


## Bonus : Copy files between two containers

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1656261289/brightsoftwares.com.blog/xniliqvwm9fdt8tdnky5.png)

To achieve that, you need to take two steps:
1. Copy the file from the first container to the to the host.
2. Copy the file from the host to the seconf container.


Here are the commands to run: 

### Copy from container 1 to host

```
docker cp container_id1:./bar/foo.txt .
```

### Copy from host to container 2

```
docker exec -i container_id2 sh -c 'cat > ./bar/foo.txt' < ./foo.txt
```


# Conclusion

That's all. I hope you enjoyed this tutorial. 
Which commands do you often [[2023-10-25-using-helm-practical-use-cases|use]] in your daily work arround [[2022-05-08-can-docker-connect-to-database|docker]]?

Let me know in the comments.



Graphics are from [Ali Hallaji](https://stackoverflow.com/users/3043331/ali-hallaji)