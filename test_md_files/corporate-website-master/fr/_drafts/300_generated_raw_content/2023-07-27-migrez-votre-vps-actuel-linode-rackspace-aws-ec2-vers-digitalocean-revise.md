---
author: full
categories:
- aws
date: 2023-07-27
description: You may want to move your data from a server to another for any reason.
  Migrating between VPS providers can seem like a daunting task. Like DigitalOcean,
  other VPS providers, such as Linode and Rackspace, provide root access. This allows
  you to transfer all of the necessary files to your new DigitalOcean VPS. For this
  guide, we will demonstrate how to transfer a simple WordPress blog from Linode to
  a DigitalOcean cloud server.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1642606953/pexels-cottonbro-4569340_y7otyd.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-27
pretified: true
ref: migrate_yourcurrent_vps_reviewed
tags:
- digitalocean
- wordpress
- lamp
- vps
- linux
title: Migrez votre VPS actuel (Linode, Rackspace, AWS EC2) vers DigitalOcean (révisé)
---

J'ai précédemment fait un article sur le sujet [[2020-04-02-migrate-your-current-vps-linode-rackspace-aws-ec2-to-digitalocean|la migration de vos données d'un VPS à un autre]]. Ceci est une version révisée de cet article. Si vous suivez les bonnes étapes, vous pouvez facilement migrer vos données. Comme [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|DigitalOcean]] , d'autres [[2021-12-29-how-to- Les fournisseurs run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|VPS]], tels que Linode et Rackspace, fournissent un accès root. Cela vous permet de transférer tous les fichiers nécessaires vers votre nouveau VPS DigitalOcean.

Pour ce guide, nous allons montrer comment transférer un simple blog [[2020-04-04-how-to-install-wordpress-with-lemp-on-ubuntu-1604|Wordpress]] de Linode vers un serveur cloud DigitalOcean.


Les deux instances exécuteront Ubuntu. Ces instructions peuvent être adaptées pour migrer d'autres services d'autres fournisseurs. Nous travaillerons en tant que root dans les deux instances VPS.

# Que signifie le ```Red```

Les lignes que l'utilisateur doit saisir ou personnaliser seront en rouge dans ce tutoriel ! Le reste devrait principalement être copié-collé.


# Configuration préliminaire du serveur DigitalOcean Cloud

## Installation de la LAMPE

Pour commencer, vous voudrez installer une pile [[2020-04-04-how-to-install-wordpress-with-lamp-on-ubuntu-1604|LAMP]] (Linux, Apache, MySQL, PHP) sur votre Serveur cloud DigitalOcean. Cela peut être accompli de différentes manières.

Le moyen le plus simple de faire fonctionner LAMP sur Ubuntu est de choisir l'image préconfigurée "LAMP sur Ubuntu" lorsque vous créez initialement votre droplet.

Dans la partie ```"Select Image"``` de la page de création de droplet, choisissez l'onglet ```"Applications"```. Sélectionnez ```"LAMP on Ubuntu 14.04"```.

Si vous avez déjà une droplet que vous aimeriez utiliser, vous pouvez installer une pile LAMP sur Ubuntu en suivant ce lien.


## Installation de Rsync

Nous ferons nos transferts de fichiers en utilisant ssh et rsync. Assurez-vous que rsync est installé sur votre VPS DigitalOcean en utilisant la commande suivante :

```
rsync --version
```


Si cette commande renvoie un message "command not found", alors vous devez installer rsync avec apt-get :

```
apt-get install rsync
```


## Communication entre les serveurs VPS

Les étapes suivantes auront lieu sur votre ancien VPS. Si vous ne l'êtes pas déjà, connectez-vous en tant que root.
Votre ancien VPS doit également avoir installé rsync. Réexécutez la vérification de rsync sur ce système :

```
rsync --version
```


Si nécessaire, installez rsync :

```
apt-get install rsync
```

Afin de transférer les informations pertinentes de notre précédent VPS vers notre serveur cloud DigitalOcean, rsync doit pouvoir se connecter à notre nouveau serveur à partir de notre ancien serveur. Nous utiliserons SSH pour ce faire.

Si vous n'avez pas de clés SSH générées sur votre ancien VPS, créez-les maintenant avec la commande suivante :

```
ssh-keygen -t rsa -b 4096 -v
```


Répondez aux invites si nécessaire. N'hésitez pas à appuyer sur "Entrée" à travers toutes les invites pour accepter les valeurs par défaut.


Ensuite, transférez la clé SSH vers notre nouveau VPS en utilisant la commande suivante. Modifiez la partie en rouge pour refléter votre adresse IP DigitalOcean VPS :

```
ssh-copy-id 111.222.333.444
```


# Effectuez la migration

Voici les étapes à suivre pour effectuer la migration.

## Étape 1 : Transférer les fichiers du site


Tout d'abord, nous allons transférer les fichiers de la racine Web de notre ancien serveur vers notre nouveau serveur cloud. Nous trouverons où se trouve notre racine Web WordPress en examinant le fichier de configuration. Nous examinerons le répertoire sites-enabled pour trouver le bon fichier VirtualHost :

```
cd /etc/apache2/sites-enabled
ls
li606-185.members.linode.com
```


Ici, notre fichier s'appelle ```"li606-185.members.linode.com"```, mais le vôtre peut être quelque chose de différent.

Ouvrez le fichier dans nano :

```
nano li606-185.members.linode.com
```


Nous recherchons la ligne "DocumentRoot" pour nous dire à partir de quel répertoire notre contenu Web est servi.
Dans notre exemple, la ligne se lit comme suit :

```
DocumentRoot /srv/www/li606-185.members.linode.com/public_html/
```


Fermez le fichier et cd dans ce répertoire :

```
cd /srv/www/li606-185.members.linode.com/public_html/
ls -F
```


Production

```
latest.tar.gz wordpress/
```


Comme vous pouvez le voir, nous avons un répertoire pour notre site WordPress. Celui-ci contient tout le contenu Web de notre site. Nous transférerons l'intégralité de ce répertoire, ainsi que ses autorisations et sous-répertoires, de cet emplacement vers la racine Web de notre serveur cloud DigitalOcean. Par défaut, apache2 sur Ubuntu 14.04 sert son contenu à partir de "/var/www/html", c'est donc là que nous placerons ce contenu.


Nous ajouterons quelques options à rsync afin qu'il puisse être transféré correctement. L'option ```"-a"``` signifie archive, ce qui nous permet de transférer de manière récursive tout en préservant de nombreuses propriétés de fichier sous-jacentes telles que les autorisations et la propriété.


Nous utilisons également le drapeau ```"-v"``` pour une sortie détaillée, et le drapeau "-P", qui nous montre la progression du transfert et permet à rsync de reprendre en cas de problème de transfert.

```
rsync -avP wordpress 111.222.333.444:/var/www/html/
```

Notez qu'il n'y a pas de barre oblique après "wordpress", mais qu'il y en a dans ```"/var/www/html/"```. Cela transférera le répertoire ```"wordpress"``` lui-même vers la destination au lieu de transférer uniquement le contenu du répertoire.

Toute notre structure de répertoires WordPress a maintenant été transférée à la racine Web du nouveau serveur cloud.

À ce stade, si nous dirigeons notre navigateur Web vers l'adresse IP de notre nouveau serveur cloud et essayons d'accéder à notre site WordPress, nous obtiendrons une erreur MySQL :


```
111.222.333.444/wordpress
Error establishing a database connection
```


En effet, WordPress stocke ses données dans une base de données MySQL qui n'a pas encore été transférée. Nous nous occuperons ensuite du transfert MySQL.


## Étape 2 : Transférez la base de données MySQL

### Compresser et exporter les données


La meilleure façon de transférer des bases de données MySQL est d'utiliser la base de données interne de MySQL ```dumping utility```. Tout d'abord, nous verrons quelles bases de données nous devons vider.

Connectez-vous à MySQL :


```cd
mysql -u root -p
```


Entrez le mot de passe de l'administrateur de la base de données pour continuer. Répertoriez les bases de données MySQL avec la commande suivante :

```
show databases;
+--------------------+
| Database |
+--------------------+
| information_schema |
| mysql |
| wordpress |
+--------------------+
3 rows in set (0.00 sec)

```


Nous aimerions transférer notre base de données "wordpress", qui contient les informations de notre site, ainsi que notre base de données "mysql", qui transférera toutes nos informations utilisateur, etc. "information_schema" n'est qu'une information de structure de données, et nous ne pas besoin de s'accrocher à ça.

Faites-vous une idée des bases de données que vous souhaitez transférer pour la prochaine étape.

Quittez MySql :

```
exit
```


Nous allons vider les informations de la base de données avec ```"mysqldump"``` puis les compresser avec "bzip2". Nous utiliserons un certain nombre de paramètres pour que nos bases de données soient importées proprement.

Remplacez le rouge par les noms de vos bases de données :

```
mysqldump -u root -p -QqeR --add-drop-table --databases mysql wordpress | bzip2 -v9 - > siteData.sql.bz2

```


Encore une fois, entrez le mot de passe de l'administrateur de votre base de données pour continuer.


### Transférez le fichier compressé vers le nouveau serveur

Nous avons maintenant un fichier de base de données compressé que nous pouvons transférer sur notre nouveau serveur cloud. Nous utiliserons à nouveau rsync.

Changez l'adresse IP pour refléter l'adresse IP de votre serveur DigitalOcean :

```
rsync -avP siteData.sql.bz2 111.222.333.444:/root
```


## Étape 3 : Importation des bases de données

Notre fichier de base de données est compressé et transféré sur notre nouveau serveur cloud DigitalOcean. Nous devons l'importer dans MySQL sur notre nouveau serveur afin que WordPress puisse l'utiliser.

Connectez-vous à votre serveur cloud DigitalOcean en tant que racine pour les étapes suivantes.
Notre fichier de base de données a été transféré dans le répertoire personnel de l'utilisateur root, alors allez dans ce répertoire maintenant.


### Décompressez l'exportation de la base de données

Nous allons décompresser le fichier en utilisant "bunzip2":

```
cd /root
bunzip2 siteData.sql.bz2
```



### Importer les données

Nous pouvons maintenant importer le fichier dans notre nouvelle base de données MySQL :

```
mysql -u root -p < siteData.sql
```


Vérifions que MySQL a importé correctement :

```
mysql -u root -p
show databases;
+--------------------+
| Database |
+--------------------+
| information_schema |
| mysql |
| performance_schema |
| test |
| wordpress |
+--------------------+
5 rows in set (0.00 sec)
```


Comme vous pouvez le constater, notre base de données "wordpress" est présente. L'ancienne base de données "mysql" a été remplacée par celle de notre ancien VPS.

Quittez MySQL :

```
exit
```

Nous allons maintenant redémarrer notre base de données et notre serveur pour faire bonne mesure :

```
service mysql restart
service apache2 restart
```


## Étape 4 : Vérifiez le site Web migré

Maintenant, si nous naviguons vers notre adresse IP DigitalOcean VPS suivie de "/wordpress", nous verrons le site WordPress qui était précédemment hébergé sur notre ancien VPS :

```
111.222.333.444/wordpress
```

# Considérations finales

Avant de changer votre nom de domaine pour pointer vers votre nouvel emplacement de site, il est important de tester votre configuration de manière approfondie. C'est une bonne idée de référencer les services qui fonctionnaient sur votre ancien VPS, puis de vérifier leurs fichiers de configuration. Vous pouvez voir les services qui fonctionnaient sur votre ancien VPS en vous connectant et en tapant :

```
netstat -plunt
```

```
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address Foreign Address State PID/Program name
tcp 0 0 127.0.0.1:3306 0.0.0.0:_ LISTEN 13791/mysqld  
tcp 0 0 0.0.0.0:22 0.0.0.0:_ LISTEN 10538/sshd  
tcp 0 0 127.0.0.1:25 0.0.0.0:_ LISTEN 13963/master  
tcp6 0 0 :::80 :::_ LISTEN 13771/apache2  
tcp6 0 0 :::22 :::_ LISTEN 10538/sshd  
udp 0 0 0.0.0.0:68 0.0.0.0:_ 2287/dhclient3
```

Ici, nous pouvons voir les services dans la dernière colonne que nous voudrons configurer sur notre nouveau serveur. Votre liste sera probablement différente.

Chaque service a sa propre syntaxe de configuration et son propre emplacement de configuration, vous devrez donc vérifier la documentation au cas par cas.


A titre d'exemple, si nous voulions répliquer la configuration de notre démon SSH sur notre nouveau VPS nous pourrions transférer le fichier de configuration dans le répertoire home de notre nouveau VPS en utilisant rsync :

```
rsync -avP /etc/ssh/sshd_config 111.222.333.444:/root
```


Après avoir transféré le fichier, nous ne voulons pas simplement remplacer le fichier par défaut par celui de notre ancien VPS.

Différentes versions de programmes peuvent introduire des changements dans la syntaxe. Des problèmes peuvent également provenir d'options de configuration spécifiques à votre ancien VPS. Les options faisant référence aux noms d'hôte, aux adresses IP ou aux chemins de fichiers devront être modifiées pour refléter votre nouvelle configuration.


Il est plus sûr de produire un diff des fichiers afin que vous puissiez ajuster le fichier de configuration natif de votre nouveau serveur cloud si nécessaire.

Il existe un certain nombre de programmes différents qui peuvent vous donner les différences entre deux fichiers. L'un est simplement différent :

```
diff /root/sshd_conf /etc/ssh/sshd_config
```

Cela produira une liste de toutes les différences entre les deux fichiers. Vous pouvez examiner les différences et les prendre en considération. Certaines options de configuration que vous voudrez peut-être incorporer à partir de votre ancienne configuration, tandis que d'autres que vous voudrez peut-être modifier ou supprimer.