---
author: full
categories:
- kubernetes
date: 2023-06-01
description: Il existe de nombreuses situations où vous devez connecter une base de
  données externe car base de données dans un conteneur ne prend pas en charge toutes
  les fonctionnalités requises par le application ou vous avez besoin de données persistantes
  dans votre environnement de cluster.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1651943394/david-knox-0blbblsyf3o-unsplash_r6a1ng.jpg
inspiration: https://towardsdatascience.com/connect-to-mysql-running-in-docker-container-from-a-local-machine-6d996c574e55?gi=42de54860f08
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-01
pretified: true
ref: can-docker-connect-to-database
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
tags: []
title: Docker peut-il se connecter à la base de données ?
transcribed: true
youtube_video: https://www.youtube.com/watch?v=HknGhxkOXF0&ab_channel=DevopsGuru
youtube_video_id: HknGhxkOXF0
---

Il existe de nombreuses situations où vous devez connecter une base de données externe car
base de données dans un conteneur ne prend pas en charge toutes les fonctionnalités requises par le
application ou vous avez besoin de données persistantes dans votre environnement de cluster.


Dans cet article, nous allons connecter une base de données SQL externe au conteneur Web Docker et la base de données externe peut être hébergée sur un serveur SQL dédié ou sur n'importe quel RDS cloud.


Dans cet article, ma base de données SQL est hébergée sur un serveur SQL dédié sur une machine virtuelle. L'application Web est hébergée sur un conteneur Docker. Il se connecte ensuite à la base de données SQL sur la VM.


Commençons!


## La mise en place

La base de données de mon application est hébergée sur cette machine SQL et c'est la base de données de l'application.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651939756/brightsoftwares.com.blog/image_aotsri.png)


C'est la deuxième machine sur laquelle j'exécute le conteneur docker pour le web
application.

![C'est la deuxième machine](https://res.cloudinary.com/brightsoftwares/image/upload/v1651939852/brightsoftwares.com.blog/image_tybk5e.png)




Si vous avez besoin d'aide sur le code d'application ou sur la configuration du
application sur un conteneur, vous pouvez vérifier [[2021-12-14-how-to-use-local-docker-images-with-minikube|ce message]] sur [[2021-12-26-how-to-expose- un-port-sur-minikube|minikube]].


J'ai configuré les informations de la base de données dans le fichier de configuration Web de l'application.

![fichier de configuration Web](https://res.cloudinary.com/brightsoftwares/image/upload/v1651940759/brightsoftwares.com.blog/image_ecqvxh.png)


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941026/brightsoftwares.com.blog/image_tqzord.png)


J'ai utilisé l'adresse IP de ma base de données MS SQL et le numéro de port. Dans la capture d'écran ci-dessus, vous avez les informations de la base de données.

Vous pouvez également utiliser le nom de domaine complet de votre base de données SQL si ce nom de domaine est résolu à partir du
conteneur docker lui-même.

Remarque : Si vous hébergez votre base de données sur un RDS cloud tel que Edge ou ou AWS, vous pouvez utiliser une chaîne de connexion similaire pour connecter votre RDS.

## Configurer la pile docker-compose

> Compose est un outil de définition et d'exécution d'applications Docker multi-conteneurs. Avec Compose, vous utilisez un fichier YAML pour configurer les services de votre application.
> En savoir plus [ici](https://docs.docker.com/compose/).


Ceci est mon fichier de composition docker. Je vais utiliser ce fichier pour lancer mon conteneur Web.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941551/brightsoftwares.com.blog/image_qofgot.png)


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941600/brightsoftwares.com.blog/image_erd8m8.png)



Je suis prêt à lancer mon conteneur Web

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941683/brightsoftwares.com.blog/image_m6rght.png)




Mon conteneur Docker est prêt à être utilisé. Ceci est le conteneur et vous pouvez accéder
l'application sur le port et sur le navigateur.


## Trouver l'adresse IP de l'hôte docker

Pour pouvoir se connecter au conteneur docker qui exécute notre application, nous avons besoin de l'adresse IP de son hôte.

Pour obtenir l'adresse IP de l'hôte, exécutez cette commande __depuis l'ordinateur hôte__.

```
ipconfig
```

Sur une machine windows, voici le résultat.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651941969/brightsoftwares.com.blog/image_qb3i0r.png)


## Accédez à l'application via le navigateur

Accédons à l'application sur le navigateur en utilisant l'adresse IP de l'hôte.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942189/brightsoftwares.com.blog/image_jgmplu.png)


Succès! L'application est capable de se connecter avec succès à la base de données MS SQL sur une machine virtuelle dédiée. Faisons quelques transactions de base de données sur l'application.

Par exemple, je veux réserver une chambre simple le *2 septembre* la chambre simple a été
confirmé.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942275/brightsoftwares.com.blog/image_n47tys.png)


### Test sur crash de conteneur

Supposons maintenant que le conteneur Web ait planté. Pour imiter cela, je vais tuer le conteneur manuellement.

Aucun conteneur n'est en cours d'exécution.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942419/brightsoftwares.com.blog/image_xqkefh.png)


Si je vérifie mon application, elle est en panne.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942462/brightsoftwares.com.blog/image_ve0g2f.png)


Cela prouve que le lien vers le SQL passe par ce conteneur.

Permettez-moi de redémarrer mon conteneur pour ramener le service.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942684/brightsoftwares.com.blog/image_q8rfiv.png)


Un nouveau conteneur a été lancé et mon application devrait être disponible sur le navigateur. Laissez-moi vérifier si ma réservation est toujours là (stockée sur la base de données SQL).

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1651942808/brightsoftwares.com.blog/image_qhc04s.png)


Notre réservation de chambre est disponible pour le 2 septembre car nos données sont stockées dans le volume persistant (la base de données SQL).


# Conclusion

Ceci est la démonstration complète de la façon dont vous pouvez connecter votre base de données externe
à votre conteneur Web Docker pour stocker vos données dans un volume persistant dans l'environnement de cluster.