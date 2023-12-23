---
author: full
categories:
- kubernetes
date: 2022-10-19
description: Lorsque vous utilisez minikube, vous devez exposer des ports pour accéder
  à vos services. Dans docker, vous avez un indicateur de commande pour le faire.
  Comment faites-vous la même chose dans minikube ? N'oubliez pas que kubernetes a
  plus de composants que docker. En fait, docker fait partie des composants de kubernetes,
  d'où minikube.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1640559437/jon-tyson-ROfrX4F__ck-unsplash_pcnxnd.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2022-10-19
pretified: true
ref: howtoexposeaportonminikube
tags:
- minikube
- linux
- docker
- minikube
title: Comment exposer un port sur Minikube
---

Lorsque vous utilisez minikube, vous devez exposer des ports pour accéder à vos services. Dans docker, vous avez un indicateur de commande pour le faire. Comment faites-vous la même chose dans minikube ?

N'oubliez pas que kubernetes a plus de composants que docker. En fait, docker fait partie des composants de kubernetes, d'où minikube.

# TL;DR

La solution consiste à utiliser la commande ```minikube service <SERVICE_NAME> --url``. Cette commande vous donnera une URL qui vous permettra de vous connecter au service backend exécuté sur minikube.

1. Créez votre service (cela devrait déjà être fait)
2. Exposez le déploiement
3. Vérifiez que tous ont été créés avec succès
4. Exposez le port du service sur minikube

Il existe une solution alternative utilisant le transfert de port ```kubectl port-forward <service> 27017:27017```.


# The steps to open a port on minikube



1. Create a deployment

Think of this as a container.

{% include codeHeader.html %}
{% raw %}
```
kubectl lance hello-minikube --image=gcr.io/google_containers/echoserver:1.4 --port=8080
```
{% endraw %}

You will get this output.

{% raw %}
```
déploiement "hello-minikube" créé
```
{% endraw %}

2. Expose the deployment 

{% include codeHeader.html %}
{% raw %}
```
kubectl expose le déploiement bonjour-minikube --type=NodePort
```
{% endraw %}

The output is :

{% raw %}
```
service "hello-minikube" exposé
```
{% endraw %}

3. Check that all is setup correctly

{% include codeHeader.html %}
{% raw %}
```
kubectl obtenir svc
```
{% endraw %}

You will get the output.

{% raw %}
```
NOM IP DU CLUSTER PORT(S) IP EXTERNE ÂGE
bonjour-minikube 10.0.0.102 <nœuds> 8080/TCP 7s
kubernetes 10.0.0.1 <aucun> 443/TCP 13m
```
{% endraw %}

4. Expose the port on minikube

{% include codeHeader.html %}
{% raw %}
```
service minikube bonjour-minikube --url
```
{% endraw %}


This command will print the url where you can reach the service:

{% raw %}
```
http://192.168.99.100:31167
```
{% endraw %}

If you want to open the url directly in your browser, run this command : 

{% include codeHeader.html %}
{% raw %}
```
service minikube bonjour-minikube
```
{% endraw %}

# Tips and tricks

1. Make sure you can ping your minikube VM. 192.168.99.100
2. If your cluster is not working as expected, you can delete the ```.minikube``` dossier et recréez le cluster. Tout sera réinitialisé.
3. Pour inspecter facilement un conteneur docker, jetez un œil au [[2020-08-04-docker-tip-inspect-and-jq|docker and jq tutorial]]