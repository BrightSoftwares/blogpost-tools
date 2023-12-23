---
author: full
categories:
- docker
date: 2022-08-24
description: In this post we are going to see the docker exec and how we use it. Then
  we are going to see is docker attach and how we use it. So what is docker attach
  and how is it different from docker exec.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551331/pexels-eren-li-7168996_wsecwr.jpg
inspiration: https://stackoverflow.com/questions/30960686/difference-between-docker-attach-and-docker-exec
lang: en
layout: flexstart-blog-single
post_date: 2022-08-24
pretified: true
ref: What is difference between docker attach and exec?
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- docker
- processes
- container
title: What is difference between docker attach and exec?
toc: true
transcribed: true
youtube_video: https://www.youtube.com/watch?v=j_3WcTcQlh0&ab_channel=InfiniteLinux
youtube_video_id: j_3WcTcQlh0
---

In this post we are going to see the [[2022-07-21-how-to-run-jenkins-jobs-with-docker|docker]] exec and how we [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] it. Then we are going to see is [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|docker]] attach and how we use it. So what is [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|docker]] attach and how is it different from [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|docker]] exec. 

Let's start!

# My setup with docker containers

I am on my system right now and I have a couple of [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|docker]] containers which are running.

If I [[2023-04-11-explore-your-container-with-docker-run|run]] ```docker ps```  I have two containers running. One is a Debian [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|container]] which is running bash as the main command and then the nginx container which is running some entry point ```.sh``` script. 


# What is docker exec and how to use it

Let's talk about ```docker exec```. Basically, ```docker exec``` lets you run more than one process inside a container.

[[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|Docker]]'s best practices said that you should run one process per container, and you should treat your containers as cattle and not pets. The containers should be like ephemeral. They should come and go.
Containers shouldn't be treated like the way you treat your virtual machines.

But with ```docker exec``` what you can do is you can run more than one process inside a container. Let's see how.

So we are going to use our Debian container in this demo.


If I run the command 

```docker exec -it a43094daf93 /bin/sh```


In the command above, we are requesting a sudo shell. I am running another shell which is the asset shell.

You can see I am inside the container now, inside the ```bin/sh``` shell.

If I run ```ps -ef```  command  you can see that the PID 1 is still used by the primary process which is the bash. There is the second process which we started when ran the exec of the PS command which we ran inside this container.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661065355/brightsoftwares.com.blog/fs54mghwe6lrnqhqqv6y.png)
You can see there so this process along with I mean we have run a couple of more processes.

This is what ```docker exec``` is actually used for.

If I run Ctrl+D, you can see I exit out of the [[2020-08-04-docker-tip-inspect-and-less|docker]] container. I came out of the container. 
But if I run ```docker ps```, the container is still running. With ```docker attach```  it is a little different.



# What is docker attach and how to use it

Now let's talk about ```docker attach```. It is basically used to attach your host systems standard input, standard output and standard [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|error]] with that of a container.

Let's check how it worked with a demo.
Let me run a ```docker ps``` and this time we well use this nginx container.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661066026/brightsoftwares.com.blog/thu7f6k8o7onw3nyanlo.png)

I am going to run this command to attach to the nginx container.


```docker attach eda453c66229```

After pressing enter, you see that I am not returned a shell.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661066158/brightsoftwares.com.blog/zh92fui4e97qw2uykwxh.png)

But if I go to another terminal and do a curl on localhost on the port 80 (because that container is running nginx which is mapped to port 80 of my host) and if I come back on the ```docker attach``` terminal, you can see I have got a request.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661066288/brightsoftwares.com.blog/immoplriobgerk0g9dxr.png)
![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661066323/brightsoftwares.com.blog/qeeb4fey48kzmjvrdzjr.png)
So this is what actually ```docker attach``` does. It has attached to me or it has attached to my standard input standard output and standard error with that of a [[2020-08-04-docker-tip-inspect-and-grep|docker]] container or the nginx container which is running.

If I press ```Ctrl+D``` to exit and I do run ```docker ps``` you can see that the nginx container is dead.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661066554/brightsoftwares.com.blog/lhzqbgqhngllat6ttxzs.png)

This is one more difference between [[2020-08-04-docker-tip-inspect-and-jq|docker]] exec and docker attach. When you exit out of your container, using ```Ctrl+D```  the container exits.
There is a way you can detach from your container without killing it. We will explore that at the end of this post.


## Attaching to the primary process in the container

Let's start that in the next process and then it's container again.

In this deep in container you can see the primary command is bash.

So if I run ```docker attach a60aaf6ef298``` , you can see I am attached to the primary process which is the bash shell.

I am inside the container. This is another way to get inside the container only for the containers which are running bash or the shell as the primary process. You cannot attach to any other. Other container which is running something else at as is primary process.

In this case this container is running bash as its primary process, that is why we were able to attach.

We actually got inside the container. If I run a ```ps -ef``` , as you can see so these are the processes in the container. No new process has been spawn.
We have attached to the existing bash process. 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661067068/brightsoftwares.com.blog/mhdopwz24aqpc4cvnhqy.png)
# The difference between docker exec and docker attach

This is basically the major difference between exec and attach. When you run an exec, it will basically spins up a new process inside the container whereas attach basically lets you attach to an existing process inside the container. That is a different that you should keep in mind.


# How to detach cleanly from a container without killing it

Last thing I want to show you is how to basically detach cleanly from a container without killing it. 

We have a container running. It is a debian container which is primary process is a bash.
Let's attach to this container.

```docker attach dfca7a50c69e```

Now we are into the container because the primary process is the bash shell.

To detach from a container cleanly without killing it what you need to do is press ```Ctrl+P```  and then press ```Ctrl+Q``` 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661067627/brightsoftwares.com.blog/brzngs9lis2uaeyfw65r.png)


You could see that I have exited out of the container ```read escape sequence``` and now
if I run ```docker ps``` you can see that my container is still running. It was not terminated when I detached from it.


# Conclusion

Tell us in the comments section the tips and tricks you use for the ```docker exec``` and ```docker attach```. How do you manage them?