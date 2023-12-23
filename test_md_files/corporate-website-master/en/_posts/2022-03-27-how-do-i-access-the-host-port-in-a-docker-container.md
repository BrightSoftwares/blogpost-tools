---
author: full
categories:
- docker
date: 2022-03-27
description: Most of the time when you configure your kubernetes cluster, using the
  default ingress controller settings works. But when you need to do something custom,
  you may run into problems. Your underlying docker and kubernetes engine may give
  you head eaches. We will see in this walkthrough, how to fix on of these and put
  a smile back on your face.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1648402232/anne-nygard-RaUUoAnVgcA-unsplash_brnnwx.jpg
inspriration: https://stackoverflow.com/questions/31324981/how-to-access-host-port-from-docker-container
lang: en
layout: flexstart-blog-single
ref: how-do-i-access-the-host-port-in-a-docker-container
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- docker
- container
title: How do I access the host port in a Docker container?
toc: true
use_mermaid: false
---

Most of the time when you configure your kubernetes cluster, using the [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|default]] ingress controller settings works. But when you need to do something custom, you may [[2022-07-21-how-to-run-jenkins-jobs-with-docker|run]] into problems. 

Your underlying [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|docker]] and kubernetes engine may give you head eaches. 
We will see in this walkthrough, how to fix on of these and put a smile back on your face.




# TL;DR

You need to [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] the `docker0` interface IP of your server. I am running Linux on my server.

```
ip addr show docker0
```

You get this answer:

```
docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 00:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
    inet6 fe80::f4d2:49ff:fedd:28a0/64 scope link 
       valid_lft forever preferred_lft forever
```



# My configuration

I am running [[2022-08-24-what-is-difference-between-docker-attach-and-exec|docker]] natively from a Linux machine. I have [[2022-09-07-overview-on-jenkins|jenkins]] installed on it. 
When a new feature is ready, I push the code to the repository and my CI/CD process get triggered.

It runs [[2022-08-31-a-complete-tutorial-about-jenkins-file|jenkins]] and is suppose to [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|connect]] to the web frontend to perform some actions.


## My problem

Given the configuration above, I need [[2023-05-17-how-can-i-make-jenkins-ci-with-git-trigger-on-pushes-to-master|jenkins]] to be able to [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|connect]] to the web frontend.
But in the this case, jenkins cannot connect.

I believe this is because the configuration inside [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|docker]] does  not allow it.


## The solution

Here are the steps that I have used to [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|solve]] my issue.

### Step 1: Get the host's IP address

Running this command will allow you to grab your host IP address.

```
ip addr show docker0
```

You will get this answer:

```
7: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 00:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
    inet6 fe80::f4d2:49ff:fedd:28a0/64 scope link 
       valid_lft forever preferred_lft forever
```


### Step 2: Get the container's IP

Connect to the [[2023-04-11-explore-your-container-with-docker-run|container]] and run this command:

```
ip route show
```

You get this answer:

```
default via 172.17.0.1 dev eth0 
172.17.0.0/16 dev eth0  src 172.17.0.4 
```


### Step 3: Setup your firewall to accept the connection from other docker containers (optional)

Running this command does allow connections for my container.
Your situation might be different. There might be other rules setup in the firewall. Check the firewall and adapt the command.

```
iptables -A INPUT -i docker0 -j ACCEPT
```

> **Note**
> 
> Iptables rules are ordered, and this rule may or may not do the right thing depending on what other rules come before it.


### Step 4: Connect jenkins and enjoy

Now that everything is setup, I can setup my jenkins and make it connect to the web frontend. Enjoy.


## An alternate solution (not recommended)

The idea here is to use the _**brutal?**_ option `--net=host`.

You run the web frontend container with the option `--net=host`. This will make the `localhost` of the container the same as the localhost of the server.

Jenkins will then be able to connect to the web frontend as if it was connecting to the localhost of the server.

To know more about how to connect jenkins to localhost, check [[2022-01-23-how-do-i-connect-to-localhost|this tutorial]].




## Few things I have tried and didn't work

### Connect to the host IP directly

I tried to connect to the web application using the host IP address but it failed.

```
curl http://172.17.1.78:7000/
```

The answer I got was

```
curl: (7) Failed to connect to 172.17.1.78 port 7000: No route to host
```


### Use the magic internal address

I have tried it, my apologies. But I encourage you to do so.

From [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|docker]] 18.03 and above, there is a DNS record that point to your internal IP address `host.[[2020-08-04-docker-tip-inspect-and-less|docker]].internal`. Use it to connect to your containerized applications.

More information [here](https://docs.docker.com/docker-for-mac/networking/#i-cannot-ping-my-containers).



# Tips

## How to get the IP address of the host

If you need to get the IP address of the host running your [[2020-08-04-docker-tip-inspect-and-grep|docker]] container, run this command:

```
ip addr show docker0 | grep -Po 'inet \K[\d.]+'
```


### How to get the container IP address

This quick bash script grabs the IP address from your Linux container.

```
#!/bin/sh

hostip=$(ip route show | awk '/default/ {print $3}')
echo $hostip
```