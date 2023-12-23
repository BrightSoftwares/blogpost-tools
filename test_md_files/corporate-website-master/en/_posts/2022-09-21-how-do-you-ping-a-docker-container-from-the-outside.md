---
author: full
categories:
- docker
date: 2022-09-21
description: At some point when you are using docker you are going to find yourself
  needing to worry about container networks. Sometimes what has happened to me at
  least in the past is I will go ahead and create some containers based on images
  but for whatever reasons sometimes these containers are not on the same docker network.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551305/pexels-sascha-du%CC%88ser-187329_pfwh5k.jpg
inspiration: https://stackoverflow.com/questions/24148956/ping-docker-container-from-another-machine-in-the-network
lang: en
layout: flexstart-blog-single
post_date: 2022-09-21
pretified: true
ref: how-do-you-ping-a-docker-container-from-the-outside
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- docker
- networking
- ping
title: How do you ping a Docker container from the outside?
toc: true
transcribed: true
youtube_video: http://www.youtube.com/watch?v=RCG-5N41FpQ
youtube_video_description: Learn how to define container networks so Docker containers
  can communicate to each other. This even works when creating ...
youtube_video_id: RCG-5N41FpQ
youtube_video_title: Define Docker Container Networking so Containers can Communicate
---

At some point when you are using [[2022-07-21-how-to-run-jenkins-jobs-with-docker|docker]] you are going to find yourself needing to worry about [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|container]] networks. Sometimes what has happened to me at least in the past is I will go ahead and create some containers based on images but for whatever reasons sometimes these containers are not on the same [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|docker]] network.

I don't mean like doctor.com Network I just mean locally so when when you fire off containers there's networking involved and sometimes they don't end up on the same network. In this case
they can't communicate to each other.

What you can actually do is you can define your own [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|container]] networking at will. 

Let's go ahead and take a look at some stuff here.

# My current docker networks

First of all what I am going to do is I am going to show what networks I have available in [[2022-08-24-what-is-difference-between-docker-attach-and-exec|docker]] . 

```
docker network ls
```

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661900982/brightsoftwares.com.blog/e2ypczmr41ul0nexymbc.png)
You can see that there are three [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|default]] networks and then one that I created custom. You will see where we are going to [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] each one of them in in just a second.


# How to create a custom network?

You can actually create a new network by saying 

```
docker network create -d bridge
```


We are going to provide it a driver bridge with the -d and then the name that you want to call that network. In my case I called it nraboy.

# The problem: build docker containers on different networks


## Build first container: server1

We want to go ahead and and launch it [[2023-04-11-explore-your-container-with-docker-run|container]]. Let's go ahead and say 

```
docker run -d -p 8080:80 --name server1 nginx:alpine
```

In this ```docker run``` we are going to run in detached mode and we are going to say port and this is going to be lets say an ```nginx``` container. So let's go ahead and say ```8080``` is going to be the host and then ```80``` is going to be the container port. 

We are going to say let's give it a name. We are going to call it ```server1``` and then let's go ahead and say ```nginx alpine``` image.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661901567/brightsoftwares.com.blog/dljzm5vohvjqmczq9txw.png)



If I go into my web browser, let's go ahead and say ```localhost:8080```. We see nginx is working.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661901608/brightsoftwares.com.blog/eauijoe88gdyymrvr9vq.png)

### Inspect the server1

I can say ```docker inspect server1``` which is what we called it and we can see that it does have an IP address and it does have a network.

The network here is bridge.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661901730/brightsoftwares.com.blog/pgytvjtpunyez4zjz8kr.png)

## Build second server: server2

To change things up a bit what I am going to do is I am going to run that same command that I had run earlier but I am going to spin up another container of nginx.

It's  going to be on port 8081 and while I am not going to let nginx really or I should say [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|docker]] decide the network for me just it could very well end up on the same network but in some cases for whatever reason it hasn't. 


I am going to define the network myself. I am going to say network equals and nraboy. 

I am going to go ahead and go to my web browser I am going to open up another tab.


```
docker run -d -p 8081:80 --network="nraboy" --name server2 nginx:alpine
```


I am going to say localhost 8080 one seems to work fine just as it should.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661902259/brightsoftwares.com.blog/ybsqxz16nl7hbjc7fr06.png)



### Inspect server2

I am going to say [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|docker]] [[2020-08-04-docker-tip-inspect-and-less|inspect]] and we call it server2 so it does have an IP address and it does have a different network.

The network is nraboy.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661902297/brightsoftwares.com.blog/w0uuqdq2nn55izmvqbgu.png)


## Reproduce the network communication problem

If I navigate into that container with this command :


```
docker exec -it server2 sh
```

Then I say execute interactive terminal server to and I say shell. And if I type in ping and say I want to ping that other server should work bad address so it doesn't recognize server1, server1 being the host name or the container name that the two containers should be able to communicate to each other.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661902490/brightsoftwares.com.blog/c6nqzvdx2zuvitxiwm78.png)


This is an example of what would happen and and this happens to me like an example of how does this happen to me. Using the whatever [[2020-08-04-docker-tip-inspect-and-grep|docker]] decides as my neck network is so I will spin up a database will spin up an application and then I will bang my head for an hour figure trying to figure out why my application can't can't communicate with my database.


# The root cause and the solution

That's because for whatever reason they ended up on a different network. Let's go ahead and
exit out of this let's go ahead and stop the first container so we are going to say:

```
docker rm -f server1
```


Now it is stopped, we are going to boot it up again with the same network as server2.



```
docker run -d -p 8080:80 --network="nraboy"  --name server1 nginx:alpine
```

Let's go ahead and go back into server two and we are going to say ping and we are going to say ping server one and the ping worked this time.

To go into server2, run the same command as before.

```
docker exec -it server2 sh
```



![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661902844/brightsoftwares.com.blog/xthi3njubmrzfxbpgf0d.png)


It worked because they are both on the same network so server ones hostname was recognized by server two exactly how we would expect.


# Conclusion

It so definitely make use of that network tag so just to go over it here. Make use of network so create a network and actually add it to your [[2020-08-04-docker-tip-inspect-and-jq|docker]] run come in so that way you know which network your containers are running on and then they will be able to communicate to each other.


Note: If you are using docker-compose you won't have to worry because everything inside of a docker compose [[2022-08-31-a-complete-tutorial-about-jenkins-file|file]] actually is on the same network by default. That's one of the cool things  about compose.


But if you are firing off these docker containers using the command line command line like I did with docker run you should really define your network and if you wanted to so say maybe you you spun up a docker-compose docker-compose will create its own network you could actually do ```--network```  in a command like I am doing right now and try to connect to that docker-compose network and it should work fine as well.

So different scenarios definitely useful long term.