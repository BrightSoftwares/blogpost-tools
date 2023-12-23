---
author: full
categories:
- kubernetes
date: 2023-06-22
description: 'Installing Kubernetes with Minikube ===================================

  Minikube is a tool that makes it easy to run Kubernetes locally. Minikube runs a
  singlenode Kubernetes cluster inside a Virtual Machine VM on your laptop for users
  looking to try out Kubernetes or develop with it daytoday.

  Minikube Features minikubefeatures


  Minikube supports the following Kubernetes features:

  DNS NodePorts ConfigMaps and Secrets Dashboards Container Runtime: Dockerhttps://www.docker.com/,
  CRIOhttps'
image: https://sergio.afanou.com/assets/images/image-midres-38.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-22
pretified: true
ref: kubernetes_minikube_1252
tags: []
title: Jouez avec Kubernetes avec Minikube
transcribed: true
youtube_video: http://www.youtube.com/watch?v=wa9YDtiE2vo
youtube_video_description: 'Webinar - Kubernetes - 5 technos indispensables : https://bit.ly/39cgijx
  Après avoir vu rapidement minikube, nous allons nous ...'
youtube_video_id: wa9YDtiE2vo
youtube_video_title: KUBERNETES - 4. INSTALLATION PRE-REQUIS | TUTOS FR
---

# 

et bonjour à tous bienvenue pour cette
nouvelle vidéo dédiée à cube airness on
va s'intéresser aujourd'hui à
l'installation donc on est dans cette
quatrième vidéo on a vu l'utilisation de
mini tubes mais je vous disais que l'on
préfère quoi moi personnellement je
préfère travailler directement sur une
offre à d'un cluster cas 8 est ce qui va
ressembler à quelque chose qu'on peut
utiliser en production ou en tout cas où
sur lequel on va pouvoir jouer un peu
plus puisqu'on va avoir plusieurs
machines on va vraiment être sur un vrai
cluster donc pour travailler ça ce qu'on
va faire donc on va utiliser un fichier
la grande on va le voir
donc là je les lancers à côté hop
ici donc il est en train de s'installer
on va le voir ainsi que dans le détail
et on va s'intéresser aux prérequis pour
installer qu'à 8 aces sur une dune on va
faire sur vm avec vague rentrent donc il
faut virtualbox
il faut vagues rendent installé et je
vais vous montrer le la grande faille la
recommandation qu'on peut en tout cas
les éléments faut avoir en tête moi
j'utilise j'utilise des machines qui ont
deux gigas de ram de cpu
il faut une ouverture réseau assez large
là je vous ai est listé les ports qui
sont utilisés déjà rien que par sa
vitesse et puis après il ya les
applicatifs qui peuvent avoir besoin
d'eux pour particuliers et la chose
importante qu'il faut avoir en tête
il faut pas de swap sur ces machines là
pour faire fonctionner que la vita sinon
vous aurez un message d'erreur et il
refusera de le faire les fichiers va
grant le fichier la grande que je lance
lui pour un stage déjà docker mais je
vous ai quand même remis les éléments
donc comment installer docker donc voilà
on faire hacker le sur cet élément là et
on lance que shell on ajoute notre
utilisateur
au groupe docker de manière après avoir
tapé des suds ou pour faire des docker
vs et autres on peut faire un remake dû
user docker de manière à pouvoir
sécuriser l'installation de docker
voilà donc ça c'est que nous on est dans
mode démo donc l'objectif c'est pas de
forcément de faire ça donc nous on va
commencer par désactiver le soir donc
voilà ma machine t'installer donc j'ai
un fichier va grande faille que j'ai
lancé qui est ici qui me lance tout
simplement deux machines une première
machine qui s'appelle qu'une master une
deuxième machine qui s'appelle qu'une
note claude parent non le loup s c'est
une goutte ou 16 04 je sais qu'on
pourrait un peu plus à jour mais c'est
pas grave
ensuite on est fini de zipper ici on
indique qu' on provisionnent un docker
dessus donc que l'on je lui disais moi
j'ai pas du coup on n'a pas besoin
d'installer docker c'est déjà fait et
puis derrière on a la memory qui définit
le nom qui est défini le nombre de cpu
et le dns voilà donc moi c'est tout
simplement ce que j'ai pensé donc pour
lancer un wagon de file donc sous tout
ça vous l'avez de le lien dans la
description pour lancer un vrai grand
toit et ses wagons up
voilà ce que j'ai fait la grandeur et
maintenant on va se connecter aux
machines n'ont pas grande
ssh cud de master donc là on va se
connecter au masters est en dessous on
va faire à grant ssh cubain note bleue
pour essayer de grossir un petit peu les
choses
ici on veut aussi un petit peu les
choses aussi et voit donc là on
ad'autres deux machines qui sont prêtes
noms première chose à faire on va
désactiver le soin qu'on veut on fait un
swap of tiré à et ça donc nous on va se
connecter déjà en route pour être
tranquille
donc là on passe un swap of donc là
instantanément on a plus de soi par
contre il faut aller faire une
modification du fichier fs table de
manière à éviter que l'on cadre relance
de la machine dont on est le soin qui se
relance donc là vous ai mis un film à
faire sur le fichier le tcf est stable
officier le fichier de montage et ici on
faisait qu'augmenter la ligne de soin
pour s'assurer que ça marche bien on
peut faire un nom dira voilà donc là si
je fais un df tiré j'ai vu ton on n'a
pas de swaps et je peux faire pareil en
dessous on vit mon petit cfs tab
ici je me rends sur la ligne de soin
c'est pas très pratique de se mettre
trop voilà donc là je commente lynn et
je fais tout petit verre ok nickel donc
sa première chose de faite
première chose de faite ensuite qu'est
ce qu'on va faire on va tout simplement
faire un appel et gâteaux jet a1 apt-get
installe de kearl notamment de kearl et
de à péter transport https
donc ça c'est tout simplement pour
pouvoir faire notre https tranquille
avec notre coeur donc là on lance là ça
va vite
tout a été fait et notre paquet était
déjà installé non pas de problème et
maintenant ce qu'on va faire on va
récupérer la clé gpg qu'on va ajouter
chez nous sur notre système la clé qui
permet d'utiliser les paquets de google
donc la source et google donc à trop de
risques on va dire voilà donc ça c'est
fait et maintenant on va rajouter le
dépôt dans notre source liste ici donc
là il faut bien s'adapter au niveau du
dépôt moi je suis sur une géniale je
suis lent 16,0 caché sur une géniale
voilà donc je rajoute pas à notre source
liste le dépôt en question donc c'est un
dépôt à péter pointu berné thèse pour un
hayon dont il va nous permettre d'avoir
accès aux dés pour google pour récupérer
les binaires qui permettent de
travailler sur que bien des casseurs
quelles sont ces binaire donc les
binaires ici cia cuba dm lui qui va
permettre de faire l'installation du
cluster on a le cul blettes lui qui est
donc on reverra ces éléments là qui est
un service qui tourne sur la machine
donc c'est vraiment un service au niveau
système et qui va permettre de gérer des
lancements de quads etc
et puis on inculpe s'était alors là
c'est la commande vous avez utilisé le
plus cube c'est elle qui permet la
communication avec la paix cas 8 est ce
donc ça va permettre là vraiment de
de gérer les deux listes et les notes de
lister les pod d'interagir avec eux donc
pour installer tout ça assez simple on
va y arriver
on va installer donc cette ligne de
commandes auxquelles donc on a style on
installe pardon qu blettes cuba dm
équipe c'était aller on ajoute qu berne
ats tirer cni alors on colle au corps
alors qu'est-ce qui se passe
ok oui bien sûr ferrer face à naples et
gâte peut-être vraiment parce que j'ai
rajouté un dépôt à péter kent est donc
voilà mais on fait notre installe et la
même chose en tout donc là ça va
s'installer gentiment voilà donc là on a
déjà fait une partie du travail on va on
va s'arrêter sur cette vidéo là donc on
va avoir fait notre installation des
éléments dont du service public de cuba
dm et de cubes c'était lé dans la
prochaine vidéo on va voir
l'installation réellement de notre
kloster là on a fait simplement les
prérequis donc on va attendre que ça se
termine
[Musique]
donc ça va pas hyper vite chez pas
beaucoup de débit c'est pas grave donc
prochaine vidéo à s'intéresser vraiment
à l'installation de notre kuster
appartient des binaires convient
d'installer notamment de cuba dm pour
l'installation du cluster voilà donc je
vous dis à très bientôt sur des harkis