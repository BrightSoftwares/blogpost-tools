---
Tags:
- ubuntu
- linux
- server
- security
ToReview: true
author: full
categories:
- ubuntu
date: 2023-06-10
description: When managing a server, you’ll sometimes want to allow users to execute
  commands as “root,” the administrator-level user. The sudo command provides system
  administrators with a way to grant administrator privileges — ordinarily only available
  to the root user — to normal users. In this tutorial, you’ll learn how to create
  a new user with sudo access on Ubuntu 20.04 without having to modify your server’s
  /etc/sudoers file.
image: https://sergio.afanou.com/assets/images/image-midres-47.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-10
pretified: true
ref: sudoenabled_202007051236
tags: []
title: Comment créer un nouvel utilisateur compatible Sudo sur Ubuntu 20.04 [Quickstart]
transcribed: true
youtube_video: http://www.youtube.com/watch?v=efnZTcp9eRs
youtube_video_description: Nous présenterons la procédure à suivre pour son installation
  et sa configuration sur Ubuntu 20.04 LTS. Lien de la formation ...
youtube_video_id: efnZTcp9eRs
youtube_video_title: Asterisk 18 pour construire une infrastructure de téléphonie
  VoIP sur Ubuntu 20.04 LTS
---

# 

[Musique]
c'est quoi astérix c'est un frais -
gratuit et open source créé par san
roman construit une infrastructure de
téléphonie voix sur ip en abrégé voip et
détails d'organisation
a fait c'est une solution logicielle qui
transforme votre ancien ordinateur en un
serveur de communication qui alimente
les systèmes pbx ip les passerelles voip
et d'autres solutions personnalisées
telles que la conférence téléphonique
la messagerie vocale ibm et la
distribution automatique des appels les
files d'attentes les agendas paix les
musiques d'attentes et les mises en
garde d'appel
dans cette formation nous présenterons
la procédure à suivre sur son
installation et sa configuration sur
ubuntu 20 points 0 4 et 10
dans cette poule où nous allons
présenter l'installation d'un styliste
18 fds sur un serveur en boubou 20
points 0,4 à ce thalys est une
application open souscrit passant
gourmands
cette habitation du pnd geler les
communications dans les petites
entreprises ainsi que dans les grandes
entreprises avec l'ass tennis ou pour
huit ans mais vous deviez machine ou
plusieurs serveurs en accusant ses
erreurs de communication ibis ibis
en une perceuse voici bible alain sévère
de conférence où jouent
les solutions 12 des pastellistes
al-iman les call centers
les opérateurs
les agences gouvernementales
à ce moment nous tournons cette vidéo
utiliseront astralis 18
notez qu'elle m'a qui ne s'agit pas
d'une façon elle dit est ce
[Musique]
qu'elle appelle jésus pour les
déploiements une production
qui nécessite la prise en charge de
dijon parlant d' l'on a mis
juste atik de la belle 1 il faut noter *
est écrit à la tâche de tigana chance il
est destiné aux systèmes station linux
il alimente les sites intervenus
d'affaires
iconnect de nombreux protocoles de
téléphonie différents
* est une boîte à outils pour créer un
bébé il y avait de nombreuses
fonctionnalités et des applications
toussaint dépasser droit sublime des
systèmes de conférences
à sélestat à charrat téléphonie voix sur
ip ainsi que prb stm y poste il existe
des sims qui est le pouls du coup voici
d'une courant
à la suite de notre vidéo nous allons
présenter l'installation d'un service 18
aces d'un serveur beau boulot
mais avant même de la notion du terminal
nous sommes d'abord une seat lasteyrie
ce point acquis le site officiel des
stellistes
ok maintenant sont connectés sur deux
thèmes la linux mais avant de commencer
notre installation nous avons d'abord
commencé à mettre à jou les bacs et
habiter effet la mise à niveau de tous
les paquets qui s'est installée de notre
système d'exploitation
comme je l'aï dit tout à l'heure nous
avons fait cette démonstration sur un
serveur linux ubuntu
10.04 lts
ce terminal vraiment taper la commande
suivante
sud on a pété
hoguette
connaissait le mot de passe
pratique de la peine tous les commandes
seront opposées des deux sud où nous
n'avons pas accompli les baquets se
télécharge cela n'est pas nouveau nous
connaissons internet bon gars la
connexion internet est légèrement
dégradée
ok
et n'en donne on veut une mise à niveau
de l'opac les systèmes
subliminal nous avons tapé la promo
suivante
si doux à bt si les idées comme les
invalides
on passe est un pas dans la mise à
niveau de nos paquets 6 km
cela dépend aussi de notre connexion
internet
je vous le commandez fait ces
manipulations sont au système u souffler
nous passerons légèrement pendant
l'installation des paquets
tous les patrons et de télécharger
maintenant on passe à des compressions
des paquets et l'installation suivre
un passage obligé la main
ok pas la mise à niveau et en terminant
je vous recommande de les démarrer vos
du seven dont se nourrit des mineurs
nous allons redémarrer le serveur avait
là comme un nouveau bouton
ans
on passe un terrain cependant que le
serveur et des mains et on va sur le
connecter sur deux serveurs par ssh
hockey nous avons redémarré nous du
serveur nous activerons vous commencez
la configuration comment dit on va taper
la commande client
maintenant nous avons installé les
dépendances fonctionnel nous avons
d'abord établir à cames en tête puis le
mot de passe ouf
il faut noter que prof c'est
l'utilisateur ou des serveurs
et non mon ami ajout
ensuite acheter le début vaisselle après
la commande suivante sud où a habité
positif 18-17 et v sont valides
un stack de dépannage fonctionnel
cela dépend de nous tous collections et
des led
c'était ça son contrat un certain temps
en fonction vous voudrez bien d'élever
au téléchargement est terminé maintenant
on passe à des conditions une
installation des parcs m
c'est un peu obligé le monde
aux cris va se terminer
les lames de l'an passé au
téléchargement de la chimie tard de
pastellistes 18 nous trouverons
la dernière et sione su * port
d'envaux bout de
la version la version disponible et
l'addition 16
zones de taper sur deux serveurs du
thème dans la semaine suivant
vous concédez lagoon avait sont
disponibles je les mange sur ubuntu vent
est la version 16 d'astérix mais nous
nous voulons dire la dernière et 5 et
répulsion 8 moment où nous pourrons
cette vidéo
nous allons prendre nos professionnels
ensuite nous allons utiliser la commande
à péter kent aux voix téléchager cas
source officielle astérix 18
nous avons tapé la commanderie guette
sylvie julien écrit changement lasteyrie
18 août nous voyez
vous ai dit qu'on ne pense * un autre
qui est le site officiel des stellistes
invalides
le changement commence
et un passant qui ne pèse plus vers du
cros hmida
c'est un très bonne
lassé des mines est ainsi nous allons
passer à la décomposition du parti avait
la commande
yvinec suivi du lâche yves on valide
la décompression et minimes
étaient lents nous avons exécuté la
commande suivante vous dévisagent et la
bibliothèque du décodeur mp3 laborie
sens de la source
nous apprenons cette commande se termine
on va aussi * on n'ouvre ikea styliste
8.6 que nous avons téléchargé
actuellement
je suis en effet qu la commande suivante
c'est fait
on va s'assurer que les déplaçant le
yacht à la main suivante
assez intelligemment
tu vas pas en quelques secondes
en passant légèrement
nous avons cette page qui s'affiche
nous demander une nounou connue mais le
new delhi gens à l'exemple 61 correspond
un boost à ricky claus câline 33éme
indicative la france nous sommes en
afrique au cameroun indicative vous
compensez du centre ancien
ce système en ligne pour que les
configurations respect de l'homme à
défaut et que l'on materi téléphonique
ouvre aussi tonique soit conforme
si nous dépasse nous avons saisi
nouveaux indicatifs du cameroun qui ait
du sens français et on valide
en passant de légèrement pendant que les
configurations
continue
ok nous avons ce message succès foule
jeudi que tuteur usine où seront
construits et installés à staline suite
de leur retour
après cohésion et la commande configure
nous avons dans le message suivant
et dinan pour voir les options du menu
de la romaine suivent ingres
nous allons utiliser la touche des
flèches qu'on navigue entre boussu mais
nous avons réussi mes mondiaux
complément des natives il
la gauche front
de gauche on est bon ajoute nous
souhaitons installer
une autre *
nous avons activé et m'ont dit de son
camp quand nous souhaitons utiliser
ce qui place
[Musique]
à