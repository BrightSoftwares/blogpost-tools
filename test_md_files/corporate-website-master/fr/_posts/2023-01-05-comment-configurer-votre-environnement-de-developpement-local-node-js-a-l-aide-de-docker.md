---
ToReview: true
author: full
categories:
- docker
date: 2023-01-05
description: "Docker est l'ensemble d'outils de facto pour créer des applications modernes et configurer un pipeline CI/CD - vous aidant à créer, expédier et exécuter vos applications dans des conteneurs sur site et dans le cloud. Que vous exécutiez sur des instances de calcul simples telles qu'AWS EC2 ou des machines virtuelles Azure ou quelque chose d'un peu plus sophistiqué comme un service Kubernetes hébergé comme AWS EKS ou Azure AKS, l'ensemble d'outils de Docker est votre nouveau BFF."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1656242721/pexels-pixabay-247431_kthwn3.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: howto_setuplocalnodejs_dev_docker
tags:
- docker
- cicd
- container
- aws
- azure
title: "Comment configurer votre environnement de développement local Node.js à l'aide de Docker"
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

Docker est l'ensemble d'outils de facto pour créer des applications modernes et configurer un pipeline CI/CD - vous aidant à créer, expédier et exécuter vos applications dans des conteneurs sur site et dans le cloud.

Que vous exécutiez sur des instances de calcul simples telles qu'AWS EC2 ou des machines virtuelles Azure ou quelque chose d'un peu plus sophistiqué comme un service Kubernetes hébergé comme AWS EKS ou Azure AKS, l'ensemble d'outils de Docker est votre nouveau BFF.

Mais qu'en est-il de votre environnement de développement local ? La configuration d'environnements de développement locaux peut être pour le moins frustrante.

Vous souvenez-vous de la dernière fois où vous avez rejoint une nouvelle équipe de développement ?

Vous deviez configurer votre machine locale, installer des outils de développement, extraire des référentiels, vous battre avec des documents d'intégration et des fichiers README obsolètes, faire en sorte que tout fonctionne et fonctionne localement sans rien savoir du code et de son architecture. Oh, et n'oubliez pas les bases de données, les couches de mise en cache et les files d'attente de messages. Celles-ci sont notoirement difficiles à mettre en place et à développer localement.

Je n'ai jamais travaillé dans un endroit où nous ne nous attendions pas à au moins une semaine ou plus d'intégration pour les nouveaux développeurs.

Alors, que devons-nous faire ? Eh bien, il n'y a pas de solution miracle et ces choses sont difficiles à faire (c'est pourquoi vous êtes payé beaucoup d'argent) mais avec l'aide de Docker et de ses outils, nous pouvons rendre les choses beaucoup plus faciles.

Dans la partie I de ce didacticiel, nous allons parcourir la configuration d'un environnement de développement local pour une application relativement complexe qui utilise React pour son front-end, Node et Express pour quelques micro-services et MongoDb pour notre magasin de données. Nous utiliserons Docker pour créer nos images et Docker Compose pour rendre tout beaucoup plus facile.

Si vous avez des questions, des commentaires ou si vous souhaitez simplement vous connecter. Vous pouvez me joindre dans notre [Community Slack](http://dockr.ly/slack) ou sur Twitter à [@pmckee](https://twitter.com/pmckee).

Commençons.

# Conditions préalables


Pour terminer ce tutoriel, vous aurez besoin de :

* Docker installé sur votre machine de développement. Vous pouvez télécharger et installer Docker Desktop à partir des liens ci-dessous :
    * [Docker Desktop pour Mac](https://download.docker.com/mac/stable/Docker.dmg)
    * [Docker Desktop pour Windows](https://download.docker.com/win/stable/Docker%20Desktop%20Installer.exe)
* [Git](https://git-scm.com/downloads) installé sur votre machine de développement.
* Un IDE ou un éditeur de texte à utiliser pour éditer des fichiers. Je recommanderais [VSCode](https://code.visualstudio.com/Download)

# Clonez le référentiel de code


La première chose que nous voulons faire est de télécharger le code sur notre machine de développement local. Faisons cela en utilisant la commande git suivante :

```
git clone git@github.com:pmckeetx/memphis.git
```

Maintenant que nous avons le code local, regardons la structure du projet. Ouvrez le code dans votre IDE préféré et développez les répertoires de niveau racine. Vous verrez la structure de fichier suivante.

```
├── docker-compose.yml
├── service de notes
│   ├── configuration
│   ├── nœud\_modules
│   ├── nodemon.json
│   ├── package-lock.json
│   ├── package.json
│   └── serveur.js
├── service de liste de lecture
│   ├── configuration
│   ├── nœud\_modules
│   ├── nodemon.json
│   ├── package-lock.json
│   ├── package.json
│   └── serveur.js
├── service utilisateurs
│   ├── Fichier Docker
│   ├── configuration
│   ├── nœud\_modules
│   ├── nodemon.json
│   ├── package-lock.json
│   ├── package.json
│   └── serveur.js
└── yoda-ui
├── LISEZMOI.md
├── nœud\_modules
├── package.json
├── publique
├── source
└── fil.lock
```

L'application est composée de quelques microservices simples et d'un front-end écrit en React.js. Il utilise MongoDB comme datastore.

Généralement, à ce stade, nous démarrons une version locale de MongoDB ou commençons à parcourir le projet pour savoir où nos applications rechercheront MongoDB.

Ensuite, nous démarrions chacun de nos microservices indépendamment, puis nous démarrions enfin l'interface utilisateur et espérons que la configuration par défaut fonctionne.

Cela peut être très compliqué et frustrant. Surtout si nos micro-services utilisent différentes versions de node.js et sont configurés différemment.

Voyons donc comment simplifier ce processus en dockerisant notre application et en plaçant notre base de données dans un conteneur.

# Dockerisation des applications


Docker est un excellent moyen de fournir des environnements de développement cohérents. Cela nous permettra d'exécuter chacun de nos services et de l'interface utilisateur dans un conteneur. Nous allons également mettre en place des choses pour pouvoir développer localement et démarrer nos dépendances avec une seule commande docker.

La première chose que nous voulons faire est de dockeriser chacune de nos applications. Commençons par les microservices car ils sont tous écrits en node.js et nous pourrons utiliser le même Dockerfile.

# Créer des fichiers Docker


Créez un Dockerfile dans le répertoire notes-services et ajoutez les commandes suivantes.

![](https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.12.36-PM. jpeg?resize=576%2C260&ssl=1)

Il s'agit d'un Dockerfile très basique à utiliser avec node.js. Si vous n'êtes pas familier avec les commandes, vous pouvez commencer par notre [guide de démarrage](https://docs.docker.com/get-started/). Consultez également notre [documentation] de référence (https://docs.docker.com/engine/reference/builder/).

# Construire des images Docker


Maintenant que nous avons créé notre Dockerfile, construisons notre image. Assurez-vous que vous êtes toujours dans le répertoire notes-services et exécutez la commande suivante :

```
docker build -t notes-service.
```

![](https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.38.21-PM. jpeg?ssl=1)

Maintenant que nous avons créé notre image, exécutons-la en tant que conteneur et testons qu'elle fonctionne.

```
docker run –rm -p 8081:8081 –name notes notes-service
```

![](https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.11.54-PM. jpeg?resize=568%2C239&ssl=1)

Il semble que nous ayons un problème de connexion à mongodb. Deux choses sont brisées à ce stade. Nous n'avons pas fourni de chaîne de connexion à l'application. La seconde est que nous n'avons pas MongoDB en cours d'exécution localement.

À ce stade, nous pourrions fournir une chaîne de connexion à une instance partagée de notre base de données, mais nous voulons pouvoir gérer notre base de données localement et ne pas avoir à nous soucier de gâcher les données de nos collègues qu'ils pourraient utiliser pour développer.

# Base de données locale et conteneurs


Au lieu de télécharger MongoDB, installez, configurez puis exécutez le service de base de données Mongo. Nous pouvons utiliser [l'image officielle de Docker](https://hub.docker.com/_/mongo/) pour MongoDB et l'exécuter dans un conteneur.

Avant d'exécuter MongoDB dans un conteneur, nous voulons créer quelques volumes que Docker peut gérer pour stocker nos données persistantes et notre configuration. J'aime utiliser les volumes gérés fournis par docker au lieu d'utiliser des montages liés. Vous pouvez tout savoir sur les [volumes dans notre documentation](https://docs.docker.com/storage/).

Créons nos volumes maintenant. Nous allons en créer un pour les données et un pour la configuration de MongoDB.

```
docker volume créer mongodb
volume docker créer mongodb\_config
```

Nous allons maintenant créer un réseau que notre application et notre base de données utiliseront pour communiquer entre elles. Le réseau s'appelle un réseau de pont défini par l'utilisateur et nous offre un service de recherche DNS agréable que nous pouvons utiliser lors de la création de notre chaîne de connexion.

```
réseau docker créer mongodb
```

Nous pouvons maintenant exécuter MongoDB dans un conteneur et l'attacher aux volumes et au réseau que nous avons créés ci-dessus. Docker extraira l'image du Hub et l'exécutera pour vous localement.

```
docker run -it –rm -d -v mongodb:/data/db -v mongodb\_config:/data/configdb -p 27017:27017 –network mongodb –name mongodb mongo
```

Bon, maintenant que nous avons un mongodb en cours d'exécution, nous devons également définir quelques variables d'environnement afin que notre application sache sur quel port écouter et quelle chaîne de connexion utiliser pour accéder à la base de données. Nous ferons cela directement dans la commande docker run.

```
docker exécuter \\_
_\-it –rm -d \\
–network mongodb \\
–notes de nom \\
\-p 8081:8081 \\
\-e SERVEUR\_PORT=8081 \\
\-e SERVEUR\_PORT=8081 \\
\-e DATABASE\_CONNECTIONSTRING=mongodb://mongodb:27017/yoda\_notes \\ notes-service
```

Testons que notre application est connectée à la base de données et est capable d'ajouter une note.

```
curl –demande POST \\
–url http://localhost:8081/services/m/notes \\
–header 'type de contenu : application/json' \\
-Les données '{
"nom": "ceci est une note",
"texte": "c'est une note que je voulais prendre pendant que je travaillais sur la rédaction d'un article de blog.",
"propriétaire": "pierre"
}
```

Vous devriez recevoir le JSON suivant de notre service.

```
{“code”:”success”,”payload”:{“\_id”:”5efd0a1552cd422b59d4f994″,”name”:”this is a note”,”text”:”this is a note that I want to take while Je travaillais sur la rédaction d'un article de blog.", "owner":"peter",,"createDate":"2020-07-01T22:11:33.256Z"}}
```

# Conclusion


Impressionnant! Nous avons terminé les premières étapes de Dockerisation de notre environnement de développement local pour Node.js.

Dans la partie II de la série, nous verrons comment nous pouvons utiliser Docker Compose pour simplifier le processus que nous venons de traverser.

En attendant, vous pouvez en savoir plus sur la mise en réseau, les volumes et les meilleures pratiques Dockerfile avec les liens ci-dessous :

* [Réseau Docker](https://docs.docker.com/network/)
* [Volumes](https://docs.docker.com/storage/)
* [Meilleures pratiques pour écrire des Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

Le message [Comment configurer votre environnement de développement local Node.js à l'aide de Docker] (https://www.docker.com/blog/how-to-setup-your-local-node-js-development-environment-using-docker /) est apparu en premier sur [Docker Blog](https://www.docker.com/blog).