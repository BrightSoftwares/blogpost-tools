---
author: full
categories:
- kubernetes
date: 2023-05-15
description: How do I access container port?
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551305/pexels-david-dibert-1117210_mlgt9n.jpg
image_search_query: container transportation
inspiration: https://stackoverflow.com/questions/47261308/docker-access-container-ip-port-directly
lang: en
layout: flexstart-blog-single
post_date: 2023-05-15
pretified: true
ref: understanding-container-networking
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: container docker kubernetes
tags: []
title: Understanding Container Networking
transcribed: true
youtube_video: http://www.youtube.com/watch?v=MkRBZSCyN-8
youtube_video_description: 'In this series I give a practical introduction to Docker.
  Links to more tutorials can be found here: http://www.brunel.ac.uk/~csstnns.'
youtube_video_id: MkRBZSCyN-8
youtube_video_title: 'Docker Training 20/29: Docker Container IP Address and Port
  Number'
---

In the previous video, we learned about [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|running]] a [[2023-04-04-should-a-docker-container-run-as-root-or-user|container]] and [[2021-12-26-how-to-expose-a-port-on-minikube|port]] mapping to access it via a web browser or the Curl tool. In this video, we will discuss [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]] networking, IP addresses, and [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|port]] mappings to avoid conflicts.

## Limited IP Addresses

IP [[2023-12-15-release-management-with-tiller-in-helm-version-2|Version]] 4 address, which is represented by something dot something dot something dot something, has a limited number of IP addresses. Therefore, containers won't have public IP addresses but instead have IP addresses for their services like web servers, [[2022-05-08-can-docker-connect-to-database|database]] servers, or mail servers.

## Port Mapping

Containers will [[2021-12-26-how-to-expose-a-port-on-minikube|expose]] services on a [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|port]]-by-port basis, and we will be dealing with port numbers to avoid conflicts. To find out the port mapping, we can [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] `[[2023-04-04-should-a-docker-container-run-as-root-or-user|docker]] ps` or `[[2022-05-08-can-docker-connect-to-database|docker]] port` if we know the [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]] ID.

For instance, by using the command `[[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|docker]] port <container_id>`, we can find out the host port number for a [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]] running on port 8000.


```bash
$ docker port 302d30 8000/tcp -> 0.0.0.0:8888
```

## Assigning a Custom Port Number

We can assign a custom port number by specifying the `-p` flag followed by the mapping. For [[2023-08-25-docker-exec-bash-example|example]], `[[2021-12-14-how-to-use-local-docker-images-with-minikube|docker]] [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|run]] -d -p 88:8000 <image_name>` will map the host port 88 to the [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|container]] port 8000.



```bash
$ docker run -d -p 88:8000 <image_name>
```

We can verify the mapping by using the `[[2023-12-22-convert-docker-compose-to-kubernetes|docker]] ps` command.



```bash
$ docker ps CONTAINER ID   IMAGE          COMMAND              CREATED         STATUS         PORTS                    NAMES 302d30         <image_name>   "python app.py"      1 minute ago    Up 1 minute    0.0.0.0:8888->8000/tcp   gracious_mendeleev
```

## Finding the IP Address

We can find the IP address of a [[2023-10-29-docker-run-stopped-container|container]] using the `[[2023-05-10-building-microservices-with-docker-creating-a-product-service|docker]] inspect` command with the format option.



```bash
$ docker inspect --format '{{ .NetworkSettings.IPAddress }}' <container_id>
```



```bash
$ docker inspect --format '{{ .NetworkSettings.IPAddress }}' 302d30 172.17.0.2
```

However, we should remember that containers shouldn't have public IP addresses. Instead, we should [[2023-10-25-using-helm-practical-use-cases|use]] port mapping to access services.

## Conclusion

In conclusion, we can publish a web server inside a [[2022-07-28-how-to-copy-files-from-host-to-docker-container|docker]] [[2023-05-14-understanding-kubernetes-the-container-orchestrator|container]], make it public, and access it from different computers by being aware of port mapping, which port number to use when accessing the service and [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|running]] few commands.