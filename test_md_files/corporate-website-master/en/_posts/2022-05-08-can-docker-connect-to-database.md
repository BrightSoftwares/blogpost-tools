---
author: full
categories:
- kubernetes
date: 2022-05-08
description: There are many situations where you need to connect a external database
  because database in a container doesn't support all the features that is required
  by the application or you need persistent data across your cluster environment.
  In this post we are going to connect external SQL database to docker web container
  and external database can be hosted on dedicated SQL server or any cloud RDS.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1651943394/david-knox-0blbblsyf3o-unsplash_r6a1ng.jpg
inspiration: https://towardsdatascience.com/connect-to-mysql-running-in-docker-container-from-a-local-machine-6d996c574e55?gi=42de54860f08
lang: en
layout: flexstart-blog-single
pretified: true
ref: can-docker-connect-to-database
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: container docker kubernetes
title: Can Docker connect to database?
toc: true
transcribed: true
youtube_video: https://www.youtube.com/watch?v=HknGhxkOXF0&ab_channel=DevopsGuru
youtube_video_id: HknGhxkOXF0
---

There are many situations where you need to [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|connect]] a external database because
database in a [[2023-04-04-should-a-docker-container-run-as-root-or-user|container]] doesn't support all the features that is required by the
application or you need persistent data across your [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]] environment. 


In this post we are going to [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|connect]] external SQL database to [[2021-12-14-how-to-use-local-docker-images-with-minikube|docker]] web [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]] and external database can be hosted on dedicated SQL [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|server]] or any [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|cloud]] RDS.


In this post my SQL database is hosted on dedicated SQL server on a [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|Virtual]] [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|Machine]]. The web application is hosted on a [[2023-04-04-should-a-docker-container-run-as-root-or-user|docker]] [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]]. It then connects to the SQL database on the VM.


Let's begin! 


## The setup

My application's database is hosted on this SQL [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|machine]] and this is the application database.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651939756/brightsoftwares.com.blog/image_aotsri.png)


This is the second machine on which I am running the [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|docker]] [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|container]] for the web
application.

![This is the second machine](https://res.cloudinary.com/brightsoftwares/image/upload/v1651939852/brightsoftwares.com.blog/image_tybk5e.png)




If you need any help about application code or how to set up the
application on a [[2023-10-29-docker-run-stopped-container|container]] you can check [[2021-12-14-how-to-use-local-docker-images-with-minikube|this post]] on [[2021-12-26-how-to-expose-a-port-on-minikube|minikube]].


I configured the database information in web config file of the application.

![web config file](https://res.cloudinary.com/brightsoftwares/image/upload/v1651940759/brightsoftwares.com.blog/image_ecqvxh.png)


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941026/brightsoftwares.com.blog/image_tqzord.png)


I used the IP address of my MS SQL database and [[2021-12-26-how-to-expose-a-port-on-minikube|port]] number. In the screenshot above you have the database information. 

You can also [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] fully qualified domain name of your SQL database if this domain name is getting resolved from the
[[2023-12-22-convert-docker-compose-to-kubernetes|docker]] [[2023-05-14-understanding-kubernetes-the-container-orchestrator|container]] itself.

Note: If you are hosting your database on any [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|cloud]] RDS like edge or or AWS you can [[2023-10-25-using-helm-practical-use-cases|use]] similar connection string to [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|connect]] your RDS.

## Setup the docker-compose stack

> [[2023-11-17-what-is-docker-compose|Compose]] is a tool for defining and running [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|multi]]-[[2023-11-22-monit-docker-container-a-comprehensive-guide|container]] [[2023-05-10-building-microservices-with-docker-creating-a-product-service|Docker]] applications. With [[2023-08-30-docker-compose-vs-dockerfile|Compose]], you use a YAML file to configure your application’s services. 
> Lean more [here](https://docs.docker.com/compose/).


This is my [[2023-05-08-restart-docker-daemon-a-comprehensive-guide|docker]] compose file. I am going to use this file to launch my web [[2023-05-15-understanding-container-networking|container]]. 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941551/brightsoftwares.com.blog/image_qofgot.png)


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941600/brightsoftwares.com.blog/image_erd8m8.png)



I am ready to launch my web container

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941683/brightsoftwares.com.blog/image_m6rght.png)




My [[2023-08-25-docker-exec-bash-example|docker]] container is ready to be used. This is the container and you can access
the application on [[2021-12-26-how-to-expose-a-port-on-minikube|port]] and on the browser. 


## Find the docker  host's IP address

To be able to [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|connect]] to the docker container that runs our application, we need to have it's host's IP address.

To ge the IP address of the host, run this command __from the host computer__.

```
ipconfig
```

On a windows machine, here is the result.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941969/brightsoftwares.com.blog/image_qb3i0r.png)


## Access the application through the browser

Let's access the application on the browser by using the hosts IP address.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942189/brightsoftwares.com.blog/image_jgmplu.png)


Success! The application is successfully able to connect MS SQL database on a dedicated VM. Let's do some database transaction on the application.

For example I want to book a single room on *2nd September* single room has been
confirmed.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942275/brightsoftwares.com.blog/image_n47tys.png)


### Test on container crash

Now let's suppose that the web container has crashed. To mimic that, I will kill the container manually.

No container is running.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942419/brightsoftwares.com.blog/image_xqkefh.png)


If I check my application, it is down.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942462/brightsoftwares.com.blog/image_ve0g2f.png)


This proves that the link to the SQL is through that container.

Let me start again my container to bring the service back.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942684/brightsoftwares.com.blog/image_q8rfiv.png)


A new container has been launched and my application should be available on the browser. Let me check if my reservation is still there (stored on the SQL database).

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942808/brightsoftwares.com.blog/image_qhc04s.png)


Our room reservation is available for the 2nd September because we are stored our data into the persistent volume (the SQL database).


# Conclusion

This is the complete demonstration of how you can connect your external database
to your docker web container to store your data into persistent volume in the cluster environment.