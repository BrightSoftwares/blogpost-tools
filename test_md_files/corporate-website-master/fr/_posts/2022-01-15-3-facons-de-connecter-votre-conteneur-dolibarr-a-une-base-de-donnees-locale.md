---
layout: flexstart-blog-single
title: 3 façons de connecter votre conteneur Dolibarr à une base de données locale
author: full
lang: fr
ref: 3waystoconnectyourOdoocontainertolocaldatabase
inspiration: https://superuser.com/questions/1254515/setup-a-docker-container-to-work-with-a-local-database
categories:
  - docker
date: 2022-02-03
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1642938172/pexels-joshua-welch-1624600_pxc6ym.jpg
tags:
  - dolibarr
  - docker
  - container
  - database
description: "L'une des priorités d'un administrateur système est l'optimisation des performances des déploiements et de l'infrastructure sous-jacente. J'ai un mariadb déployé et en cours d'exécution sur un serveur Linux. Il est optimisé pour les performances et le stockage de la base de données. Maintenant, je prévois de déployer un conteneur dolibarr docker dessus. Comment puis-je me connecter du conteneur dolibarr docker à la base de données mariadb locale ?"
---



L'une des priorités d'un administrateur système est l'optimisation des performances des déploiements et de l'infrastructure sous-jacente. J'ai un mariadb déployé et en cours d'exécution sur un serveur Linux. Il est optimisé pour les performances et le stockage de la base de données. Maintenant, je prévois de déployer un conteneur dolibarr docker dessus.

Comment puis-je me connecter du conteneur dolibarr docker à la base de données mariadb locale ?

Il existe 3 façons de connecter votre conteneur.

Parcourons-les.

## 1. Utiliser l'option `--net=host` 

> Remarque importante : cette option ne fonctionne pas sur Mac OS X. Si vous utilisez OS X, passez à la deuxième option.

Lorsque vous exécutez votre conteneur docker, vous pouvez passer l'option `--net=host` comme ceci :

```
docker run --net=host ... tuxgasy/dolibarr
```

Lorsque vous utilisez cette option, docker utilise la pile réseau des hôtes pour votre conteneur. Cela signifie que le conteneur aura accès à l'ensemble de la pile du réseau hôte. Le conteneur partage les services et les ports disponibles sur l'hôte.

Une fois dans ce mode, le conteneur a un accès direct à localhost. Vous pouvez maintenant accéder à localhost:3306.

> Remarque : Cette configuration ne fournit aucune isolation réseau au conteneur.


## 2. Montez la prise de service dans le conteneur

L'idée ici est d'utiliser le socket de base de données MariaDb disponible sur l'hôte et de le monter dans le conteneur.

> Qu'est-ce qu'une prise ?
> Un _socket_ est un point d'extrémité d'une liaison de communication bidirectionnelle entre deux programmes s'exécutant sur le réseau. Un socket est lié à un numéro de port afin que la couche TCP puisse identifier l'application à laquelle les données sont destinées à être envoyées.
> Source : [documents Oracle](https://docs.oracle.com/javase/tutorial/networking/sockets/definition.html)

Sur l'hôte, le socket est installé dans le répertoire `/var/run/mysqld`. Nous allons monter cette prise dans le conteneur.

```
docker run -v /var/run/mysqld:/mariadb_socket ... tuxgasy/dolibarr
```

Ensuite, pour accéder à la base de données depuis le conteneur, connectez-vous au socket situé à `/mariadb_socket/mysqld.sock`

## 3. Connectez-vous à l'adresse IP de l'hôte docker

Docker a une pile réseau appelée "docker0".
L'idée de cette méthode est de trouver l'adresse IP de ce réseau et de s'y connecter.

Démarrez une invite de commande et tapez "ip addr"

Recherchez le réseau "docker0". L'adresse IP ressemble à `172.17.0.1`.

> Le résultat de votre invite de ligne de commande peut être différent


![Docker0 IP address, source: tecmint.com](https://res.cloudinary.com/brightsoftwares/image/upload/v1642934808/Check-Docker-IP-Address_ygq4bh.png)

Maintenant que vous avez l'adresse IP, vous pouvez l'utiliser dans votre conteneur docker en vous connectant à `172.17.0.1:3309`.

# Conclusion

Nous détaillons 3 façons de connecter notre conteneur frontal dolibarr à la base de données située sur votre serveur local.
Faites-moi savoir dans les commentaires si vous avez d'autres moyens.

Si vous avez des images docker locales que vous souhaitez utiliser localement, rendez-vous sur [[2021-12-14-how-to-use-local-docker-images-with-minikube|ce tutoriel]]. Vous serez entre de bonnes mains.
