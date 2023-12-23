---
author: full
categories:
- kubernetes
date: 2022-03-25
description: 'I have hosted one of my websites on kubernetes and am happy with it
  ... except with one thing: how I can access it. My local IP address is 10.0.0.21.
  If I use localhost or 127.0.0.1, it works. But if I use my local IP address, I cannot
  access it. Sound similar. Here is how to solve it.'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1648310138/maria-teneva-2Wa88Py0h0A-unsplash_gwbtaf.jpg
inspiration: https://stackoverflow.com/questions/38175020/cant-access-localhost-via-ip-address
lang: en
layout: flexstart-blog-single
ref: how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip
seo:
  links:
  - https://www.wikidata.org/wiki/Q22661306
silot_terms: container docker kubernetes
title: How to solve can connect with localhost but not IP?
toc: true
---

I have hosted one of my websites on [[2020-08-12-play-with-kubernetes-with-minikube|kubernetes]] and am happy with it ... except with one thing: how I can access it. My [[2021-12-14-how-to-use-local-docker-images-with-minikube|local]] IP address is `10.0.0.21`. If I [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] `localhost` or `127.0.0.1`, it works. But if I [[2023-10-25-using-helm-practical-use-cases|use]] my local IP address, I [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|cannot]] access it. 

Sound similar. **Here is how to solve it.**

## TL;DR

You must pay attention to the **interface** your website is listening on.
if you [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] the website with grunt, make sure that you use `0.0.0.0` instead of `localhost`.

> **IMPORTANT NOTICE**
>
> Most of the application come configured to listen on `localhost` only for **security reasons**. 
It avoids [[2021-12-26-how-to-expose-a-port-on-minikube|exposing]] a potentially unsecure [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|server]] [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|outside]] of the server it is running on. 
It allows the administrator to test locally the application before releasing it to the rest of the world.


## My setup

I have my website installed on [[2020-08-13-work-with-kubernetes-with-minikube|kubernetes]].
To [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|run]] it, I use the command `grunt serve`.

The command starts my website on the ```port 9000```.


## The problem

Here are the urls that I use to access it (If my computer is connected to my home [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|network]]):

- http://localhost:9000/ : works okay.
- http://127.0.0.1:9000/ : works okay too.
- http://10.0.0.21:9000/ : fail to [[2022-05-08-can-docker-connect-to-database|connect]]

If my computer is connected to other networks, all the three urls [[2020-08-13-work-with-kubernetes-with-minikube|work]] well.


## The solution

The issue is coming from **the interface** the application is running on.
If you start the application using `localhost` interface it will be available on the server only.
If you start the application using `0.0.0.0` interface, it will be available on **all the available interfaces**, hence your local IP address.

To solve the issue:

1. Stop the application
2. Update the configuration (start the application using the `0.0.0.0`)
3. Start the application using the same command as before `grunt serve`
4. [[2022-05-08-can-docker-connect-to-database|Connect]] to the application using it's local ip address `http://10.0.0.21:9000/`


## Conclusion

I hope this solution will help you in your journey. Contact us if you need help.