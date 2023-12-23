---
author: full
categories:
- kubernetes
date: 2022-06-15
description: We're on a clean docker install on Linux all the networks we saw came
  as part of that default install so this bridge network was created for us. It contains
  a single virtual switch called docker0. We said this is the default Network and
  switch meaning if we create new containers  and don't specify a network for them
  to join they're gonna get connected to that docker0 switch, be part of this bridge
  network and because the bridge network is created with the bridge driver it's a
  single host network.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655109789/jerry-zhang-zemLpQqvJ-0-unsplash_bobi86.jpg
inspiration: https://stackoverflow.com/questions/33814696/how-to-connect-to-a-docker-container-from-outside-the-host-same-network-windo
lang: en
layout: flexstart-blog-single
pretified: true
ref: how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: container docker kubernetes
title: How do I connect a docker bridged container to the outside of the host?
toc: true
transcribed: true
youtube_video: http://www.youtube.com/watch?v=Js_140tDlVI
youtube_video_description: This video demonstrates how to network containers on the
  same host using the bridge driver provided in Docker -- Docker is an ...
youtube_video_id: Js_140tDlVI
youtube_video_title: Bridge Networking for Single Host Container Networking
---

Let's take a look at the built in bridge [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|network]] that you get on all [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|Linux]] based [[2023-04-04-should-a-docker-container-run-as-root-or-user|docker]] hosts. Now this networks roughly equivalent to the default NAT [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|network]] that you get with [[2022-05-08-can-docker-connect-to-database|docker]] on Windows. 

## My setup : Fresh install on Linux
I'm logged in here to a freshly installed [[2021-12-14-how-to-use-local-docker-images-with-minikube|docker]] [[2022-07-28-how-to-copy-files-from-host-to-docker-container|host]] and on my Linux based install. These are the three networks that I get by default. 


### Default networks


![The default networks on a fresh docker install](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110158/brightsoftwares.com.blog/akmy5xdtqxb6ya9bm4d6.png)This one here called bridge using the bridge driver this is the one we're interested in right now: the bridge network.



### Inspect for details

Now if we want to get more info on it we can fire off an inspect command here and we give it the name of the network and we get pretty much the same info as before just with a bunch more as well.

```
docker network inspect bridge
```


![Docker network details with no containers and default gateway](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110268/brightsoftwares.com.blog/iqgc7hho1xbrmimneqpd.png)

For one thing we can see the subnet and the Gateway here and we can see where it
says containers we don't have any. 


Right now this network doesn't have any containers attached to it okay but what's underpinning all of this how does it all [[2020-08-13-work-with-kubernetes-with-minikube|work]] well if we throw this up here we can see that on our [[2023-04-04-should-a-docker-container-run-as-root-or-user|docker]] [[2022-07-28-how-to-copy-files-from-host-to-docker-container|host]]. 


## How the bridge network works?


We've got a [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|virtual]] switch or bridge called ```docker0```. This is what really makes up that network called bridge. All we have to do is plumb containers into it and like any layer to type switch any containers that get plugged into it are going to be able to
talk to each other now because this networks created by the bridge driver. 

![the docker0 bridge network](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110392/brightsoftwares.com.blog/iawmrpbr0mimdpwkth3n.png)
It's confined to this here [[2022-05-08-can-docker-connect-to-database|docker]] [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|host]] that were logged onto that's because the bridge driver is all about ```single host networking``` so it creates isolated networks and switches that only exists within a single [[2021-12-14-how-to-use-local-docker-images-with-minikube|docker]] host. 



### How to see the docker0 bridge

To actually see this dock a zero bridge we need to install the Linux bridge utilities [[2023-11-01-helm-charts-the-package-manager-for-kubernetes|package]].

 ```
 sudo apt-get install bridge-utils
 ```


Now if we go ```brctl show```   there's our ```docker0``` [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|virtual]] switch.


```
brctl show
```

In the native tooling parlance it's called a bridge but **a bridge in a switch are the same**. 

Over here we can see it's got no interfaces attached to it that's cause
we've got no [[2023-10-29-docker-run-stopped-container|container]].

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110524/brightsoftwares.com.blog/bnbb58dqwfjvp6x10qf1.png)


### Add a container to the network

Let's add one and just a simple [[2023-12-22-convert-docker-compose-to-kubernetes|docker]] run command :


```
docker run -it --rm alpine sh
```


This command is saying start as a new [[2023-05-14-understanding-kubernetes-the-container-orchestrator|container]] base it off of the Alpine image and drop us into a shell.

Notice there right we're not specifying which network to join so by default. **If we don't tell a [[2023-11-22-monit-docker-container-a-comprehensive-guide|container]] which network to join it's gonna join that bridge network**.
![Bridged container IP address](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110637/brightsoftwares.com.blog/gr5euqyql5izpsgeuzwd.png)
We're in our [[2023-05-15-understanding-container-networking|container]] and this is our containers IP. We don't need to do anything now so let's just drop out of it here but keep it running. 

To drop out but keep it running, press ```Ctrl P+Q```.


### Check now that the docker0 bridged has a contaier attached to it

Let's see if it did what we said it would do we'll see for join that bridge network. Let's run the inspect command again. 

We've got a container attached to it and there's its IP address too.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110791/brightsoftwares.com.blog/i3u1qwaxpsqdurout5lw.png)


If we look at that docker0 virtual switch again, we see how it's got an interface attached to it now that interface is plumbed into our container. 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110817/brightsoftwares.com.blog/dmhobxbz6iyvxm0ae2ak.png)















## Conclusion

Let's back up and recap. :)

We're on a clean [[2023-05-10-building-microservices-with-docker-creating-a-product-service|docker]] install on Linux all the networks we saw came as part of that default install so this bridge network was created for us.

It contains a single virtual switch called docker0.

We said this is the default Network and switch meaning if we create new containers  and don't specify a network for them to join they're gonna get connected to that docker0 switch, be part of this bridge network and because the bridge network is created with the bridge driver it's a single host network.

If you get into the error `cannot TCP [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|connect]] from outside Virtual Machine`, check our blog post on [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|fixing the connectivity issue outside a virtual machine]].