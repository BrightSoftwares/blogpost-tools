---
author: full
categories:
- docker
date: 2022-10-06
description: "L'exécution de votre base de données dans un conteneur est une solution très portable. Il est également reproductible. Mais comment gérez-vous les données à l'intérieur de ce conteneur ? Avec mon serveur mysql fonctionnant dans un conteneur docker, je voulais m'y connecter et le gérer. Le but de ce tutoriel est de partager avec vous comment le faire."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1644274461/pexels-ono-kosuki-5974245_c7quwi.jpg
inspiration: https://stackoverflow.com/questions/33827342/how-to-connect-mysql-workbench-to-running-mysql-inside-docker
lang: fr
layout: flexstart-blog-single
pretified: true
ref: how-do-i-connect-mysql-workbench-to-mysql-inside-docker
tags:
- mysql
- docker
- permission
- dockercompose
title: Comment connecter mysql workbench à mysql dans Docker ?
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

L'exécution de votre base de données dans un conteneur est une solution très portable. Il est également reproductible. Mais comment gérez-vous les données à l'intérieur de ce conteneur ?

Avec mon serveur mysql fonctionnant dans un conteneur docker, je voulais m'y connecter et le gérer. Le but de ce tutoriel est de partager avec vous comment le faire.


# De quoi avons nous besoin ?

Tout d'abord, nous aurons besoin d'un conteneur docker en cours d'exécution exécutant mysql.

J'utiliserai l'image docker `mysql/mysql-server:5.7` et je nommerai mon conteneur `mysql57` pour faciliter mes opérations.

Les numéros de port **extérieurs** que je choisis pour exporter mon service mysql sont `3306` et `33060`, vous pouvez le changer si vous le souhaitez.

> Si vous changez le numéro de port, assurez-vous de le changer dans le reste des commandes

## Étape 1 : Démarrez votre conteneur

### Cas 1 : Vous utilisez **docker-compose**


Si vous utilisez [[2021-12-14-how-to-use-local-docker-images-with-minikube|docker-compose]] préparez votre configuration comme suit.

```
services:
    db:
        image: mysql
		container_name: mysql57
        volumes:
            - "./.data/db:/var/lib/mysql"
        environment:
            MYSQL_ROOT_PASSWORD: root
            MYSQL_DATABASE: mydb
            MYSQL_USER: user
            MYSQL_PASSWORD: pass
        ports:
            3306:3306
```


Pour démarrer le conteneur, exécutez :

```
docker-compose up
```

Cette commande lancera votre conteneur et exposera le port sur l'hôte local.


### Cas 2 : vous exécutez vos conteneurs à partir de la ligne de commande

Démarrez votre conteneur avec les ports requis :

```
docker run -p 3306:3306 -p 33060:33060 --name=mysql57 -d mysql/mysql-server:5.7
```

## Étape 2 : Obtenez le mot de passe généré par mysql

Lorsque MySQL démarre pour la première fois, il génère un mot de passe et l'imprime sur la console. Nous allons utiliser les `docker logs` pour lire ces sorties de console et obtenir le mot de passe généré.

Pour ce faire, exécutez cette commande :

```
docker logs mysql57 2>&1 | grep GENERATED
```


Il imprimera la ligne avec le mot de passe.


## Étape 3 : Mettez à jour le mot de passe de l'utilisateur root

Connectez-vous au serveur `mysqld` en utilisant le `client mysql` à l'intérieur du conteneur.

```
docker exec -it mysql57 mysql -uroot -p
```

Vous obtiendrez une invite à l'intérieur du serveur mysql.

## Étape 3.a : Vérifiez les utilisateurs dans le système

Pour vérifier les utilisateurs du système, exécutez cette commande :


```
mysql> select host, user from mysql.user;
+-----------+---------------+
| host      | user          |
+-----------+---------------+
| localhost | healthchecker |
| localhost | mysql.session |
| localhost | mysql.sys     |
| localhost | root          |
+-----------+---------------+
4 rows in set (0.00 sec)
```


## Étape 3.b : Modifier le mot de passe (pour les nouvelles installations uniquement)
S'il s'agit d'une nouvelle installation, le système vous demandera de modifier le mot de passe à l'aide de la commande `ALTER user`.

Fais le.

Exécutez la commande :

```
update mysql.user set host = '%' where user='root';
```

Une fois cela fait, quittez l'invite de commande MySQL.

## Étape 4 : Redémarrez le conteneur

Maintenant que la configuration interne est terminée, redémarrez le conteneur.

```
docker restart mysql57

```


## Étape 5 : Vérifiez l'état des utilisateurs (après la configuration)

Après la mise à jour, vérifiez à nouveau les utilisateurs.

```
select host, user from mysql.user;
+-----------+---------------+
| host      | user          |
+-----------+---------------+
| %         | root          |
| localhost | healthchecker |
| localhost | mysql.session |
| localhost | mysql.sys     |
+-----------+---------------+
```




## Étape 6 : Connectez-vous à MySQL avec le plan de travail

Voici la configuration à utiliser pour la connexion :


```
host: `0.0.0.0` 
port: `3306`
```


Les données contenues dans la base de données peuvent servir à plusieurs fins. L'une d'elles consiste à héberger [[2020-07-05-how-to-use-onetomany-database-relationships-with-flask-and-sqlite|une application flask avec une relation un à plusieurs]].


# Conclusion

C'est tout. Vous pouvez maintenant vous connecter à votre conteneur MySQL à l'aide de MySQL Workbench.

Maintenant que vous avez une base de données fonctionnelle et que vous pouvez gérer les données, vous êtes peut-être intéressé par [[2020-04-04-how-to-set-up-a-remote-database-to-optimize-site-performance-with- mysql-on-ubuntu-1604|comment configurer une base de données distante pour optimiser les performances du site]].