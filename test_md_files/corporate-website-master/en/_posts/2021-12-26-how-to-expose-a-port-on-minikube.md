---
author: full
categories:
- kubernetes
date: 2021-12-26 22:50:24.317000+00:00
description: When using minikube, you need to expose ports to access your services.
  In docker, you have a command flag to do that. How do you do the same thing in minikube?
  Remeber that kubernetes has more components than docker. A matter of fact, docker
  is among the components of kubernetes, hence minikube.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1640559437/jon-tyson-ROfrX4F__ck-unsplash_pcnxnd.jpg
lang: en
layout: flexstart-blog-single
ref: howtoexposeaportonminikube
seo:
  links:
  - https://www.wikidata.org/wiki/Q22661306
silot_terms: container docker kubernetes
tags:
- minikube
- linux
- docker
- minikube
title: How to expose a port on Minikube
toc: true
---

When using [[2020-08-12-play-with-kubernetes-with-minikube|minikube]], you need to expose ports to access your services. In [[2023-04-04-should-a-docker-container-run-as-root-or-user|docker]], you have a command flag to do that. How do you do the same thing in [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|minikube]]? 

Remeber that [[2020-08-13-work-with-kubernetes-with-minikube|kubernetes]] has more components than [[2022-05-08-can-docker-connect-to-database|docker]]. A matter of fact, [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|docker]] is among the components of [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|kubernetes]], hence [[2021-12-14-how-to-use-local-docker-images-with-minikube|minikube]].

# TL;DR

The solution is to [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] the ```minikube service <SERVICE_NAME> --url``` command. This command will give you a url that will allow you to [[2022-05-08-can-docker-connect-to-database|connect]] to the [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|backend service]] [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|running]] on [[2020-08-12-installing-kubernetes-with-minikube|minikube]].

1. Create your [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|service]] ([[2023-04-04-should-a-docker-container-run-as-root-or-user|should]] be already done)
2. Expose the [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|deployment]]
3. Check that all have been created successfully
4. Expose the port of the [[2023-05-10-building-microservices-with-docker-creating-a-product-service|service]] on [[2020-08-12-installing-kubernetes-with-minikube|minikube]]

There is an alternate solution using the port forwading ```kubectl port-forward <service> 27017:27017```.


# The steps to open a port on minikube



1. Create a [[2023-11-19-continuous-deployment-with-argocd|deployment]]

Think of this as a [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]].

{% include codeHeader.html %}
{% raw %}
```
kubectl run hello-minikube --image=gcr.io/google_containers/echoserver:1.4 --port=8080
```
{% endraw %}

You will get this output.

{% raw %}
```
deployment "hello-minikube" created
```
{% endraw %}

2. Expose the deployment 

{% include codeHeader.html %}
{% raw %}
```
kubectl expose deployment hello-minikube --type=NodePort
```
{% endraw %}

The output is :

{% raw %}
```
service "hello-minikube" exposed
```
{% endraw %}

3. Check that all is setup correctly

{% include codeHeader.html %}
{% raw %}
```
kubectl get svc
```
{% endraw %}

You will get the output.

{% raw %}
```
NAME             CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
hello-minikube   10.0.0.102   <nodes>       8080/TCP   7s
docker           10.0.0.1     <none>        443/TCP    13m
```
{% endraw %}

4. Expose the port on [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|minikube]]

{% include codeHeader.html %}
{% raw %}
```
minikube service hello-minikube --url 
```
{% endraw %}


This command will print the url where you can reach the [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|service]] :

{% raw %}
```
http://192.168.99.100:31167
```
{% endraw %}

If you want to open the url directly in your browser, [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|run]] this command : 

{% include codeHeader.html %}
{% raw %}
```
minikube service hello-minikube
```
{% endraw %}

# Tips and tricks

1. Make sure you can ping your [[2020-08-13-work-with-kubernetes-with-minikube|minikube]] VM. 192.168.99.100
2. If your [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]] is not working as expected, you can delete the ```.minikube``` folder and recreate the cluster. All will be reset.
3. To inspect easily a [[2022-07-28-how-to-copy-files-from-host-to-docker-container|docker]] [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]], take a look to [[2020-08-04-docker-tip-inspect-and-jq|docker and jq tutorial]]