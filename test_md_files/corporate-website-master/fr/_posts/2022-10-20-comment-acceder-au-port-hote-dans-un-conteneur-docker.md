---
author: full
categories:
- docker
date: 2022-10-20
description: "La plupart du temps, lorsque vous configurez votre cluster Kubernetes, l'utilisation des paramètres du contrôleur d'entrée par défaut fonctionne. Mais lorsque vous devez faire quelque chose de personnalisé, vous pouvez rencontrer des problèmes. Votre docker sous-jacent et votre moteur kubernetes peuvent vous donner des têtes. Nous allons voir dans cette soluce, comment les réparer et vous redonner le sourire."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1648402232/anne-nygard-RaUUoAnVgcA-unsplash_brnnwx.jpg
inspriration: https://stackoverflow.com/questions/31324981/how-to-access-host-port-from-docker-container
lang: fr
layout: flexstart-blog-single
pretified: true
ref: how-do-i-access-the-host-port-in-a-docker-container
tags:
- docker
- container
title: Comment accéder au port hôte dans un conteneur Docker ?
use_mermaid: false
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

La plupart du temps, lorsque vous configurez votre cluster Kubernetes, l'utilisation des paramètres du contrôleur d'entrée par défaut fonctionne. Mais lorsque vous devez faire quelque chose de personnalisé, vous pouvez rencontrer des problèmes.

Votre docker sous-jacent et votre moteur kubernetes peuvent vous donner des têtes.
Nous allons voir dans cette soluce, comment les réparer et vous redonner le sourire.




# TL;DR

Vous devez utiliser l'adresse IP de l'interface `docker0` de votre serveur. J'utilise Linux sur mon serveur.

```
ip addr show docker0
```

Vous obtenez cette réponse :

```
docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 00:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
    inet6 fe80::f4d2:49ff:fedd:28a0/64 scope link 
       valid_lft forever preferred_lft forever
```



# Ma config

J'exécute docker nativement à partir d'une machine Linux. Jenkins est installé dessus.
Lorsqu'une nouvelle fonctionnalité est prête, je pousse le code vers le référentiel et mon processus CI/CD se déclenche.

Il exécute Jenkins et est supposé se connecter à l'interface Web pour effectuer certaines actions.


## Mon problème

Compte tenu de la configuration ci-dessus, j'ai besoin de Jenkins pour pouvoir me connecter à l'interface Web.
Mais dans ce cas, jenkins ne peut pas se connecter.

Je pense que c'est parce que la configuration à l'intérieur du docker ne le permet pas.


## La solution

Voici les étapes que j'ai utilisées pour résoudre mon problème.

### Étape 1 : Obtenir l'adresse IP de l'hôte

L'exécution de cette commande vous permettra de récupérer l'adresse IP de votre hôte.

```
ip addr show docker0
```

Vous obtiendrez cette réponse :

```
7: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 00:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
    inet6 fe80::f4d2:49ff:fedd:28a0/64 scope link 
       valid_lft forever preferred_lft forever
```


### Étape 2 : Obtenir l'adresse IP du conteneur

Connectez-vous au conteneur et exécutez cette commande :

```
ip route show
```

Vous obtenez cette réponse :

```
default via 172.17.0.1 dev eth0 
172.17.0.0/16 dev eth0  src 172.17.0.4 
```


### Étape 3 : Configurez votre pare-feu pour accepter la connexion d'autres conteneurs Docker (facultatif)

L'exécution de cette commande autorise les connexions pour mon conteneur.
Votre situation pourrait être différente. Il peut y avoir d'autres règles configurées dans le pare-feu. Vérifiez le pare-feu et adaptez la commande.

```
iptables -A INPUT -i docker0 -j ACCEPT
```

> **Remarque**
>
> Les règles Iptables sont ordonnées, et cette règle peut ou non faire la bonne chose en fonction des autres règles qui la précèdent.


### Étape 4 : Connectez Jenkins et profitez-en

Maintenant que tout est configuré, je peux configurer mon jenkins et le connecter à l'interface Web. Prendre plaisir.


## Une solution alternative (non recommandée)

L'idée ici est d'utiliser l'option _**brutale ?**_ `--net=host`.

Vous exécutez le conteneur frontal Web avec l'option `--net=host`. Cela rendra le `localhost` du conteneur identique au localhost du serveur.

Jenkins pourra alors se connecter à l'interface Web comme s'il se connectait à l'hôte local du serveur.

Pour en savoir plus sur la façon de connecter jenkins à localhost, consultez [[2022-01-23-how-do-i-connect-to-localhost|ce tutoriel]].




## Peu de choses que j'ai essayées et qui n'ont pas fonctionné

### Connectez-vous directement à l'adresse IP de l'hôte

J'ai essayé de me connecter à l'application Web en utilisant l'adresse IP de l'hôte, mais cela a échoué.

```
curl http://172.17.1.78:7000/
```

La réponse que j'ai eue était

```
curl: (7) Failed to connect to 172.17.1.78 port 7000: No route to host
```


### Utilisez l'adresse interne magique

J'ai essayé, mes excuses. Mais je vous encourage à le faire.

À partir de docker 18.03 et supérieur, il existe un enregistrement DNS qui pointe vers votre adresse IP interne "host.docker.internal". Utilisez-le pour vous connecter à vos applications conteneurisées.

Plus d'informations [ici](https://docs.docker.com/docker-for-mac/networking/#i-cannot-ping-my-containers).



# Des astuces

## Comment obtenir l'adresse IP de l'hôte

Si vous avez besoin d'obtenir l'adresse IP de l'hôte exécutant votre conteneur Docker, exécutez cette commande :

```
ip addr show docker0 | grep -Po 'inet \K[\d.]+'
```


### Comment obtenir l'adresse IP du conteneur

Ce script bash rapide récupère l'adresse IP de votre conteneur Linux.

```
#!/bin/sh

hostip=$(ip route show | awk '/default/ {print $3}')
echo $hostip
```