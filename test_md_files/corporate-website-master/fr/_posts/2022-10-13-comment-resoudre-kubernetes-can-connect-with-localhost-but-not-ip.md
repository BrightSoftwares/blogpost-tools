---
author: full
categories:
- kubernetes
date: 2022-10-13
description: 'J''ai hébergé un de mes sites web sur kubernetes et j''en suis content...
  sauf d''une chose : comment y accéder. Mon adresse IP locale est `10.0.0.21`. Si
  j''utilise `localhost` ou `127.0.0.1`, cela fonctionne. Mais si j''utilise mon adresse
  IP locale, je ne peux pas y accéder. Cela vous semble familier? Voici comment le
  résoudre.'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1648310138/maria-teneva-2Wa88Py0h0A-unsplash_gwbtaf.jpg
inspiration: https://stackoverflow.com/questions/38175020/cant-access-localhost-via-ip-address
lang: fr
layout: flexstart-blog-single
pretified: true
ref: how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip
title: Comment résoudre Kubernetes can connect with localhost but not ip?
seo:
  links: [ "https://www.wikidata.org/wiki/Q22661306" ]
---

J'ai hébergé un de mes sites web sur kubernetes et j'en suis content... sauf d'une chose : comment y accéder. Mon adresse IP locale est `10.0.0.21`. Si j'utilise `localhost` ou `127.0.0.1`, cela fonctionne. Mais si j'utilise mon adresse IP locale, je ne peux pas y accéder.

Cela vous semble familier? **Voici comment le résoudre.**

## TL;DR

Vous devez faire attention à l'**interface** sur laquelle votre site Web écoute.
si vous exécutez le site Web avec grunt, assurez-vous d'utiliser `0.0.0.0` au lieu de `localhost`.

> **AVIS IMPORTANT**
>
> La plupart des applications sont configurées pour écouter sur `localhost` uniquement pour des **raisons de sécurité**.
Cela évite d'exposer un serveur potentiellement non sécurisé en dehors du serveur sur lequel il s'exécute.
Il permet à l'administrateur de tester localement l'application avant de la diffuser dans le reste du monde.


## Ma configuration

Mon site Web est installé sur kubernetes.
Pour l'exécuter, j'utilise la commande `grunt serve`.

La commande démarre mon site Web sur le `port 9000`.


## Le problème

Voici les urls que j'utilise pour y accéder (si mon ordinateur est connecté à mon réseau domestique) :

- http://localhost:9000/ : fonctionne bien.
- http://127.0.0.1:9000/ : fonctionne bien aussi.
- http://10.0.0.21:9000/ : échec de connexion

Si mon ordinateur est connecté à d'autres réseaux, les trois URL fonctionnent bien.


## La solution

Le problème vient de **l'interface** sur laquelle l'application s'exécute.
Si vous démarrez l'application à l'aide de l'interface `localhost`, elle ne sera disponible que sur le serveur.
Si vous démarrez l'application en utilisant l'interface `0.0.0.0`, elle sera disponible sur **toutes les interfaces disponibles**, d'où votre adresse IP locale.

Pour résoudre le problème :

1. Arrêtez l'application
2. Mettez à jour la configuration (démarrez l'application en utilisant le `0.0.0.0`)
3. Démarrez l'application en utilisant la même commande qu'avant `grunt serve`
4. Connectez-vous à l'application en utilisant son adresse IP locale `http://10.0.0.21:9000/`


## Conclusion

J'espère que cette solution vous aidera dans votre cheminement. Contactez nous si vous avez besoin d'aide.