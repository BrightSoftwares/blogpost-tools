---
author: full
categories:
- docker
date: 2023-07-22
description: La plupart du temps, lorsque vous configurez votre cluster Kubernetes,
  l'utilisation des paramètres du contrôleur d'entrée par défaut fonctionne. Mais
  lorsque vous devez faire quelque chose de personnalisé, vous pouvez rencontrer des
  problèmes. Votre docker sous-jacent et votre moteur kubernetes peuvent vous donner
  des têtes. Nous allons voir dans cette soluce, comment les réparer et vous redonner
  le sourire.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1648402232/anne-nygard-RaUUoAnVgcA-unsplash_brnnwx.jpg
inspriration: https://stackoverflow.com/questions/31324981/how-to-access-host-port-from-docker-container
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-22
pretified: true
ref: how-do-i-access-the-host-port-in-a-docker-container
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
tags:
- docker
- container
title: Comment accéder au port hôte dans un conteneur Docker ?
transcribed: true
use_mermaid: false
youtube_video: http://www.youtube.com/watch?v=mzJ2yWXmbkI
youtube_video_description: Dans cette vidéo, nous voyons comment utiliser un container
  et surtout comment pouvoir interagir avec celui-ci. En regardant ...
youtube_video_id: mzJ2yWXmbkI
youtube_video_title: Docker - Utiliser efficacement un container
---

# 

utiliser efficacement un container
docker souviens toi
dans la vidéo précédente jeter montrer
comment lancer ton premier container
cette semaine nous allons voir comment
l'utiliser plus efficacement
salut je suis thierry de l'informatique
sans complexe et ensemble nous allons
utiliser les containers docker mais tout
d'abord si tu aimes mes vidéos n'oublie
pas de ta bonnet et d'activer les
notifications et regardant les
commentaires tu trouveras un lien pour
recevoir gratuitement mon premier module
de formation sur le cloud computing
comme tu le sais quand une application
fonctionne dans un container
elle se croit seul au monde elle dispose
en effet de son propre espace 10 de son
propre réseau ou encore de son propre
temps processeur du coup par défaut
cette application n'est pas accessible
depuis l'extérieur du container mais
alors comment fait-on pour y accéder eh
bien on utilise des mappings les
mappings ce sont des fonctionnalités qui
permettent de créer des liens entre
l'extérieur et l'intérieur du container
c'est un peu comme si on ouvrait la
porte du container pour pouvoir accéder
à l'application qui est à l'intérieur
souviens toi dans la dernière vidéo nous
avons lancé un container avec un serveur
web à l'intérieur et pour pouvoir
accéder à ce serveur web
nous avons ajouté une option dans la
ligne de commande l'option - paix avec
deux numéros de porc le numéro de port
vu de l'extérieur et le numéro de port à
l'intérieur du container cela nous a
permis d'accéder à notre containers
depuis notre navigateur
en fait nous avons indiqué à docker de
rediriger tous ceux qui arrivaient sur
le port extérieur du container vers le
port intérieur du container sans cela il
aurait été difficile de savoir si le
serveur web fonctionnait vraiment de la
même façon on ne peut pas accéder depuis
l'extérieur au disque du container pour
cela on utilise un mapping du répertoire
avec l'option - v cette option va nous
permettre d'établir un lien entre un
répertoire de notre pc et un répertoire
du container ça te paraît compliqué pas
de panique
nous allons maintenant voir comment cela
fonctionne avec un exemple souviens toi
la semaine dernière nous avons lancé
notre containers http des cantons fait
docker ps on peut le voir fonctionner et
si on va sur notre browser internet on
peut voir qu'il fonctionne mais là
c'est pas très intéressant parce
qu'effectivement on peut lancer un
serveur web
mais on ne peut pas changer son contenu
pour changer son contenu
nous allons devoir maps et un disque du
container un disque local sur notre pc
tout d'abord nous devons connaître quel
répertoire
le container utilise en interne pour
faire cela le plus simple c'est de se
rendre sur la page du container httpd et
de chercher l'information
ici on peut voir que le répertoire en
local c'est le répertoire cela chez acer
flash local slash apache de slash
acheter dox c'est le répertoire que
voile applications dans le container
pour commencer nous devons créer un
répertoire en local ce sera le
répertoire qui sera ma paie sur le
répertoire du container comme les
fichiers apache sont dans le répertoire
acheter doc
nous allons créer le répertoire acheter
tox puis ensuite nous lançons le
container en faisant docker run - p 81
81 donc le port externe 81 vers le port
interne 80 - v pour le mapping de
répertoire et là nous de dont le
répertoire que nous venons de créer le
répertoire local
attention à bien prendre le chemin
absolue est pas le chemin relatif
acheter dox deux points
le nom du répertoire tels que nous
l'avons trouvée sur la documentation
plus loin httpd pour dire que nous
lançons le container httpd voilà le
container est lancé nous pouvons aller
le tester et là la différence c'est
qu'au lieu d'afficher it works ca
affiche index à flash pour dire qu'en
fait il n'y a pas de fichier
si nous allons dans le répertoire
acheter ducks et que nous créons un
fichier index html dans lequel nous
écrivons par exemple informatique sans
complexe un index point html vous voyez
que dans ce fichier
il n'ya que cette ligne si nous
retournons sur notre brothers et que
nous rafraîchissons nous avons bien
informatique sans complexe qui s'affiche
donc à partir de là si dans ce
répertoire acheter ducks vous copier
tous les fichiers composant votre site
web
votre containers va faire fonctionner ce
site web et va pouvoir le délivrer voilà
tu sais maintenant comment utiliser
efficacement ton containers docker tu
vas pouvoir s'entraîner en lançant t'es
propre containers expérimente c'est
comme cela qu'on apprend et n'hésite pas
à me faire des retours dans les
commentaires à très vite pour une
nouvelle vidéo sur une question
informatique en moins de trois minutes