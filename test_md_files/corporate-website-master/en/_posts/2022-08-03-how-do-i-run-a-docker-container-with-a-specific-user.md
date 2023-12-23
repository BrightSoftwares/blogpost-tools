---
author: full
categories:
- kubernetes
tags:
- docker
- containers
- root
date: 2022-08-03
description: How do I run a docker container with a specific user. You connect to the terminal as root user, but I would like to connect as a different user.  How can you achieve that ? The solution is to add a user flag to your command line when you start the container or in your docker compose.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551306/pexels-tim-gouw-52608_o69uwf.jpg
inspiration: https://stackoverflow.com/questions/35734474/connect-to-docker-container-as-user-other-than-root
lang: en
layout: flexstart-blog-single
post_date: 2022-08-03
pretified: true
ref: How do I run a docker container with a specific user
title: How do I run a docker container with a specific user
transcribed: false
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
toc: true
---


BY default when you run

`docker run -it [myimage]`

OR

`docker attach [mycontainer]`

You connect to the terminal as root user, but I would like to connect as a different user.  How can you achieve that ?

# The solution for docker run as user command line


## For docker run as user command

In the command line, you need to run  `docker run`:

To specify the user simply add the option `--user <user>` to change to another user when you start the docker container.

```
docker run -it --user nobody busybox
```


## For docker attach and docker exec


If you really want to attach to the user you want to have, then

1.  start with that user `run --user <user>` or mention it in your `Dockerfile` using `USER`
2.  change the user using `su


For `docker attach` or `docker exec`:

Since the command is used to attach/execute into the existing process, therefore it uses the current user there directly.

```
docker run -it busybox  # CTRL-P/Q to quit
docker attach <container id>  # then you have root user
/ # id
uid=0(root) gid=0(root) groups=10(wheel)

docker run -it --user nobody busybox # CTRL-P/Q to quit
docker attach <container id>  
/ $ id
uid=99(nobody) gid=99(nogroup)
```



# The solution for docker-compose

For `docker-compose`, you need to edit the  `docker-compose.yml`.

Add in your service the `user` .


```
version: '3'
services:
    app:
        image: ...
        user: ${UID:-0}
...
```

The value of this parameter is `${UID:-0}`. It means that the variable UID is stored in an `.env` variable.


In `.env`:

```
UID=1000
```


# Few use cases on docker with specific user


## Connect to the container with apache www-data

If you have an apache container and you don't want to connect with the `root` user but rather the `www-data`.

Execute command as `www-data` user:

`docker exec -t --user www-data container bash -c "ls -la"`


## Connect  to node container with a specific user


You may encounter the error : ```Compile webpack stuff in nodejs container on Windows running Docker Desktop with WSL2 and have the built assets under your currently logged in user.```

To solve it you need to specify the `--user` or the `-u` in the docker command line.

```bash
docker run -u 1000 -v "$PWD":/build -w /build node:10.23 /bin/sh -c 'npm install && npm run build'
```


In the command above, the user `1000` is used to run the container. This is probably the root user. You may be interested in checking whether it is suitable for your case to [[2023-04-04-should-a-docker-container-run-as-root-or-user|run the container as the root user]].


Based on the answer by [eigenfield](https://stackoverflow.com/a/47894556/53864). Thank you!

Also [this](https://medium.com/@mccode/understanding-how-uid-and-gid-work-in-docker-containers-c37a01d01cf) material helped me understand what is going on.

This technique is not only for a node container. You can also apply it to a [[2022-05-08-can-docker-connect-to-database|database container]].



# Conclusion

You may encounter other cases where the container needs to connect to other containers. Check this post to learn [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|how to solve hostname related issues]].

Did you find this blog post useful? Which other tip do you use to change the root user? 

Let us know in the comments.
