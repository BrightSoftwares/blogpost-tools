---
author: full
categories:
- webdevelopment
date: 2022-09-14
description: I want to answer for you guys today is what is a lamp stack so we've
  gotten some questions and comments in the past we've had people approach us and
  they say hey i hear this referenced all the time i have absolutely no idea what
  a lamp stack is this is not something i'm familiar with and so
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655555091/pexels-victor-freitas-973505_d0mrkk.jpg
inspiration: null
lang: en
layout: flexstart-blog-single
post_date: 2022-09-14
pretified: true
ref: what-is-the-lamp-stack
silot_terms: server dev and admin
tags:
- lamp
- apache
- linux
- mysql
- php
title: What is the LAMP stack
toc: true
transcribed: true
youtube_video: https://www.youtube.com/watch?v=tzBgFog6NmY&ab_channel=IBMTechnology
youtube_video_id: tzBgFog6NmY
---

I want to answer for you guys today is what is a lamp stack so we've gotten some questions and comments in the past we've had people approach us and they
say hey i hear this referenced all the time i have absolutely no idea what a lamp
stack is this is not something i'm familiar with and so.


# What is LAMP stands for?

LAMP is an acronym it stands for **Linux Apache MySQL and Php** and it is the stack of software that at its most fundamental makes the internet run.


I know that seems kind of bizarre and kind of an outlandish claim but I can assure you that the internet exists in the form that we use today in the form that we consume it today because of the lamp stack and so first I want to go through like what are those components and then we're going to talk about how they work.

So, if we think about running a website right in order to run a website you have to
have some sort of a server now that server could be: 
- a physical server 
- a virtual server

It could be in a data center it could be running: 
- in cloud it could be in a colo facility 
- be just a laptop that's plugged into your room

But you have to have some sort of a computer hardware to run that website you have to have
something that is turned on and has electricity and network access.

Then on top of that hardware you have the four lamp components right the first one that we're going to talk about here is our linux.

## LAMP Component 1: Linux

Linux is the free open source software that is an operating system it's community supported it's community developed and linux is that operating system that forms most of the internet. 
It is the underlying operating system of the internet writ large.

Linux comes in lots of different flavors right. You've got pure linux if you will so the pure linux kernel you have ubuntu from canonical you have red hat you have susa you have centos you have mint all different flavors but all using the same underlying kernel or close enough. That it really doesn't matter but again it's free it's freely distributed. 

Linux has several permission layers. One one them is `sudo`. For more [[2023-11-27-hp-web-services-not-working-troubleshooting-tips|tips]] on how to How To Create a New Sudo-enabled [[2023-05-04-current-user-what-it-is-and-how-it-can-help-your-business|User]] on Ubuntu 20.04 quickstart, check out our blog post on [[2020-07-05-how-to-create-a-new-sudoenabled-user-on-ubuntu-2004-quickstart.md|ubuntu create new sudo user]].



Anybody can go out and download it compile it install it and get it running.


## LAMP Component 2: Apache

Our next piece in our lamp stack is our a a is Apache. 

Apache again free open source software from the apache foundation apache is the web server layer so apache software that you install onto your linux operating system onto the server. 

The point of apache is to be able to understand all of those incoming network requests what do they mean and what do I send back when I am done.

So apache is the actual web server itself if you want to think about the web server being its own standalone software. So can secure apache with certificates. For more information on how to How To Create a Self-Signed SSL Certificate for Apache on CentOS 8, check out our [[2023-11-29-port-forward-pia-a-comprehensive-guide|comprehensive guide]] on [[2020-07-05-how-to-create-a-selfsigned-ssl-certificate-for-apache-on-centos-8.md|create self signed certificate ubuntu]].



## LAMP Component 3: MySQL

The next piece that's mysql.

Mysql is a free open source sql structured query language database again free open source community developed community supported so anybody can go down install or download it compile it install it and run it.


The idea behind mysql is it is the database layer for your lamp stack. It's the database for your website well what is a database a database has tables in it inside the tables we store data.


So if you think about going to a website where you're going to log in right that website prompts you for credentials it : wants your username and your password.

Before you could log into it you had to register for it you had to give it your name your address your telephone number your email address so on and so forth all of that data that you input goes into this database.


So when you log in it's going to go and it's going to check against the database to say hey does this username match does this password match so that's the database that's where all of the data that is dynamic is housed.


## LAMP Component 4: Php

Then our fourth, and this goes down here at the bottom we've got all of our components how  do we write the site well we need a language and that's what "P" is for php.

Php is the most commonly used language in  running websites building websites. Php is again it is free it is community written it is community supported anybody can download it anybody can compile it and anybody can install it.

Php is far and away the most common language used for scripting or writing websites. For example, wordpress is written in PhP. For more information on how to How To Install WordPress with LAMP on Ubuntu 16.04, check out our comprehensive guide on [[2020-04-04-how-to-install-wordpress-with-lamp-on-ubuntu-1604.md|lamp ubuntu 16]].


So that's a description these are the components of the lamp stack. Let's talk about how do they work.


# How the LAMP stack work?

Let's imagine a guy. 

This guy got a laptop right. And his laptop he wants to get onto it he wants to go to your website and so he's going to send a request down here to your server that's running LAMP.


He's going to say *hey please send me your front page*!


That request that's going to come in, the request is going to be *hey please send this to me*.

So it's going to come in it's going to hit the apache and say hey this guy wants the website.

Apache is going to say all right well we need to send it out. So let me run the code the php to send html back so that it knows what to display 

Let me access that "M" the mysql database to say *hey what data are we going to send back is there anything in the database we're going to send* or is it all static or hard coded.

And it's going to talk to the "L" to the linux and say *hey operating system this incoming request it's good to go* and we're going to send this data back to him.

We're going to send back the code we're going to send back the data and we're going to send it back in this web compliant standard method.

And so it is then going to transmit those via packets back to our guy with our laptop and he's 
going to be able to view the website.


Everything that he clicks on is going to generate a new series of communications back and forth between his laptop and the server running the lamp stack to serve up all of the images to serve up the text to serve up the prompts anything that moves anything that's intelligent, the underlying components are exactly the same.


# Conclusion

LAMP is far and away the longest serving it is the most popular. It's the one that's been around the longest and it really doesn't matter what web framework you're going to use. At the end of the day the underlying architecture depends on the exact same things that we scripted at 15 years ago when the lamp stack was originally developed.