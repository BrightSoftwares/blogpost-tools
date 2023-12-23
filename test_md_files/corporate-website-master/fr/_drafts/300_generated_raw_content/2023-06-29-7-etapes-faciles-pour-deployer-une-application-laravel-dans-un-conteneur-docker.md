---
author: full
categories:
- laravel
date: 2023-06-29
description: Laravel est un framework PHP très utile pour construire des projets impressionnants.
  Il dispose d'outils intéressants qui permettent à un développeur de sortir rapidement
  un prototype de son application. Je suis fan de l'organisation de mon application
  dans des conteneurs pour faciliter le déploiement et la gestion des dépendances.
  Je suis tombé sur un projet intéressant que je voulais déployer et tester. Je pensais
  partager avec vous les étapes pour effectuer un tel déploiement.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1653583799/pexels-taryn-elliott-4253925_vcxrxv.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-29
pretified: true
ref: 5-easy-steps-to-deploy-a-laravel-application-in-a-docker-container
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
tags:
- docker
- laravel
- pgsql
- postgres
title: 7 étapes faciles pour déployer une application laravel dans un conteneur docker
transcribed: true
use_mermaid: true
youtube_video: http://www.youtube.com/watch?v=urCLl_JhF_g
youtube_video_description: 'Introduction au déploiement sans conteneurs et avec conteneurs.
  Virtualisation : Concept, Types et Niveaux. Virtualisation vs ...'
youtube_video_id: urCLl_JhF_g
youtube_video_title: Préparer le déploiement d&#39;un projet Web Laravel 8 avec Docker
---

# Introduction

[Musique]
bonjour à tous et bienvenue sur le
semtex protéger on voit aujourd'hui
comment déployer une application
l'arrivée louit utilisons les docks est
donc on va utiliser un ensemble de
dépendances on va épuiser un ginks la
version 1.3.5 utiliser le php 8 points
et ont utilisé mysql 5 points 7 donc on



# Déploiement sans conteneurs

va commencer un autre vidéo par voir la
différence entre le déployement son
conteneur et ensuite on veut le voir
avec les conteneurs
donc là on va commencer avec le cas sans
quoi tenir bon au niveau de notre road
development on va installer la révéler 8
he would et dépendance on a besoin de
l'affection 5.7 au niveau de mysql les
dix 6.2 php 8.11 ginks donc 1.0.5 donc
ça ce sont les dépendances qui sont
installés pour assurer le bon
fonctionnement de notre site la v8 donc
bien sûr là sur notre mode de
développement tout va bien ok s'exécute
normalement les problèmes ils peuvent
survenir là lors du dépouillement ça
veut dire lorsqu'on va déployer notre
application qu'on a déjà développé et on
va la mettre sur le serveur hôte
donc si le mode de production donc là on
aura besoin d'installer la v8 est
malheureusement dix ans on peut avoir
quelques problèmes là c'est quoi c'est
que les dépendances qui existe déjà sur
les offres de production ou bien est ce
un pôle de production ils peuvent avoir
des versions qui sont différentes de
celles qui sont à notre niveau de haute
de développement donc là par exemple au
lieu de 57 ans peut trouver la version
5.6 qui est installé sur le serveur de
production qu'équipe au niveau de
l'édition peut avoir une version
inférieure qui est 5.0 voyez-vous de php
aussi on peut avoir la version 7.2 au
niveau de 1,6 on peut avoir un point
19.4 alors que c'est pas les dernières
versions avec lesquels n'ont qu on a
développé notre application
donc là ça peut poser des problèmes et
il ya un grand risque d'erreur disons
depuis le démarrage là on peut dire que
la lgv et 8 ne peut pas fonctionner avec
php 5.2
donc là comme vous voyez on a un conflit
entre php la version 7.2 et la version
8.1 donc là encore petite version on
peut avoir la des problèmes lors de
l'exécution de quelques implications
parce que les applications qui se base
sur la version 7.2 et d'autres qui se
base sur une gestion antérieure
donc là c'est un exemple de problème et
aussi vous allez voir que en cas
d'utilisation de ranka de déploiement
son compte n'a donc on aura besoin de
faire un processus ou bien de lancer un
processus d'installation différents
selon le système d'exploitation cible
donc ça ce sont les inconvénients de
déploiement son utilisation de la
technologie de dockers
maintenant la deuxième
solution dans notre cas on va faire un
déploiement avec contenant donc avec les
twins au coeur et quand vous voyez là au
niveau de la haute de développement on a
installé dockers on a installé notre
framework php la belgique on a installé
un jeans version 1.0.5 mais ce que c'est
que cette pêche fait huit fois rang
ready 6.2 et lorsqu'on veut faire le
déploiement se notre produit haute de
production bien ces vols de production
vous voyez que tout le joker il sera
déplacé il n'y aura plus de problème à
ce niveau et malgré qu'on a déjà sur le
serveur des versions qui sont
antérieures et ceux ci se pose plus de
problème parce que alors on va voir que
les applications qui seront lancés à
travers le dock l île selon sauvegardés
dans des conteneurs qui sont isolées par
rapport aux autres applications de notre
système
aussi il faut mentionner que la
configuration et les identique sur
différentes plateformes différents
systèmes d'exploitation
donc on aura plus de problème là et donc
on va plus intéressés donc aux
plateformes cibles parce que le dock est
donc qui va prendre si c'est une
abstraction il va cacher nous cacher
toutes les différences entre ces
plateformes et on veut voir aussi que
une commande unique elle va nous
permettre de lancer le déploiement de
notre application donc atteint vers le
dos quelle mesure
ce qui n'était pas le cas avant donc et
il fallait enchaîner tous les logiciels
nécessaires tout des dépendances et
ensuite là on aura plusieurs étapes à
suivre pour déployer notre application
donc dorénavant avec les dockers on peut
dénoncer à travers une commande unique
aussi il faut signaler que dorénavant à
en utilisant les dockers on aura une
coexistence deux versions différentes de
la même application sur la même machine
donc parce que ils sont isolés l'un de
l'autre donc on n'y aura plus de conflit
à ce niveau



# Virtualisation

maintenant on veut voir un peu là
comment la lâcheté culturel a évolué
donc au niveau de la structure classique
elle se base sur la couche matériel
hardware en anglais ensuite sur cette
couche on aura un système d'exploitation
laisse ensuite la liste des applications
au niveau de virtualisation ça sera une
autre manière de présenter les choses
donc on aura une couche matérielle en
bas et ensuite leur sujet cette route on
a une couche de virtualisation et sur
cette couche de virtualisation on aura
des systèmes d'exploitation invités et
c'est eux qui vont évoluer les
applications on peut avoir plusieurs
bien sûr donc on va voir cette route de
virtualisation c'est ce qu'on appelle un
hyperviseur donc c'est quoi ça va c'est
d'assurer le contrôle des ressources cpu
ram etc elle alloue à chaque machine
virtuelle les ressources dont elle a
besoin et aussi la sur le non
interférence entre les machines
virtuelles samedi elle va assurer que
chacun des applications des processus va
les spots et s'ils ont une mémoire il va
pas donc accéder aux 1 de mémoire des
autres processus la l'hyperviseur on
peut les diviser en deux parties donc de
deux types de i can't be there on n'a le
type 1 et de type 2 types en appel belle
métal et le type 2 qui s'appellera ce
métal dans le four lebel métal on va
voir que l'hyperviseur eelv a su
positionner juste au dessus de la couche
matérielle donc c'est là où est ce qu'on
va maintenant être hyper bizarre
donc c'est sûr la couche matérielle
ensuite sur un seul hyperviseur on va
trouver le système d'exploitation un
système donc invité un système
d'exploitation publie t2 etc et ses
systèmes bien sûr nature on va trouver
nos applications où est ce qu'on va les
longs c'est donc là ce sont des
applications qui seront lancées sur le
système d'exploitation invité à c'est
peut-être le swing de snacks et cetera
hélas comme un deuxième système
d'exploitation on va trouver d'autres
applications donc exemple des
hyperviseurs on peut citer la paire
exemple un microsoft apple vit donc
c'est un type
d'hyperviseur bare metal on peut trouver
aussi
d'autres solutions proposées par oracle
donc voilà que la veine
serveurs
x86
on peut trouver aussi
beaucoup d'autres exemples on peut citer
aussi 20 -
rsx fille et c'est donc ça ce sont les
cas ou bien les exemples des
hyperviseurs qui sont de type 1 sachant
que sont le plus les plus répandus au
niveau des entreprises
le deuxième cas où le deuxième type il
s'appelle reste métal est ce si on veut
voir que il ya une différence au niveau
de l'architecturé globale du système
donc là on va trouver comme toujours la
couche matérielle en bas ou bien est ce
qu'on appelle graduelle et sur cette
couche matérielle on veut trouver un os
un système d'exploitation
ce système d'exploitation dont le reste
c'est ou bien être c'est lui qui va
gérer l'accès au matériel et sur ce
système d'exploitation en temps on va
trouver un autre hyperviseur donc vous
voyez là la différence par rapport aux
bermudes albert le métal c'est
l'hyperviseur il va se mettre
directement sur la couche matérielle
donc sert à un niveau 2 alors que au
niveau de reste mes talons il va se
positionner à la troisième niveau donc
il sera
donc lancée par un système
d'exploitation hôte et c'est lui qui va
gérer par la suite les autres systèmes
d'exploitation les autres machines
virtuelles donc systèmes d'exploitation
invités en invité de etc et chacun de



# Niveaux de virtualisation

ces machines virtuelles ils vont lancer
l'application correspondante au niveau
de l'utilisation là il faut savoir que
il y à des niveaux de virtualisation
donc on a une partie physique une partie
virtuelle et on va voir de la couche de
virtualisation au niveau de la lecture
classique on remarque bien que
l'application le système d'expression et
matériels sont tous donc opté physique
au niveau de virtualisation de systèmes
d'exploitation on va trouver l'apathie
systèmes d'exploitation et applications
donc au virtuel et au niveau de
l'utilisation des applications on va
uniquement focalisé les applications et
c'est ça le cadre de dockers excite
exactement donc c'est pour ça que les



# Machine virtuelle vs Conteneurisation

images doc r ils seront plus petites que
celles de machines virtuelles si les
machines virtuelles ils sont de quelques
gigas d'or de l'ordre de conteneurs et
de quelques méga donc là vous remarqué
au niveau de messi virtuel on a
infrastructures le matériel et on aura
l'hyperviseur et qui va héberger donc
des gains au st been librairie qui sont
les dépendances de application abc
et au niveau de conteneurs on ne va plus
là et projets des os mais uniquement on
va utiliser des applications donc le
host os il va héberger tout ça et le doc
r c'est lui qui va gérer donc les
différentes applications et leur



# Avantages de Docker

virtualisation c'est quoi les avantages
de doc est premièrement on peut
automatiser le déploiement des
applications de leur dépendance de
manière fsi next un seul fichier qu'on
va le lancer il va lancer le déploiement
deuxièmement on peut installer plusieurs
versions de la même application seront
avoir de conflit et simuler
l'environnement de production comme on a
vu au démarrage de cette vidéo aussi on
peut tester des nouvelles technologies
sont touchés à votre environnement de
travail à notre environnement de travail
donc vous l'installez ensuite vous le
supprimer on peut aussi intégrer
facilement à nouveau développeur de
notre équipe si on travaille en groupe
et on a à nouveau développeur donc on
peut lui offrir directement l'image
dockers et il va le lancer est déployée
tout l'environnement de manière très
rapide et aussi dans finalement on va a
cité le cas de préparation de micro
service parce qu'on peut implémenter
mais mikko services à travers les
locales
[Musique]



# Cas pratique

donc on va se déplacer vers le dossier
exemple ensuite au dossier un tube est
relancé notre avis de commandes et là on
va commencer avec la première
instruction qui sera responsable de la
création du projet là révèle donc je
vous rappelle de la commande
pour leur sélection dans le composent
espace qui a étudié les projets qu ils
aient tiré préfère liste donc on va te
juger le dernière v / de l'arve et en
fit la reverse tâche n'avait ensuite pas
mentionné le nom de notre projet
donc dans notre cas on va l'appeler
revel tilly joker donc organisé sept
veulent d'application ainsi qu'aux
réduisez le septennat sql mais on va
utiliser langage de script côté cette
pub est fluide
non on appuyez sur entrée et on attend
que le système nous fait là le
téléchargement
de la structure de notre projet
donc là une fois on a terminé la
question du projet on va se déplacer
vers ce dossier donc c'était le nom de
notre projet ensuite
on va lancer la commande cote espace
poids et on va ouvrir notre projet d'un
musée studio code
donc on vous voyez là c'est notre
structure générale du côté il avait donc
on a un dossier l'aap donc ce qu'on va
faire là on va commencer par la création
de nouveaux fichiers svg on va l'appeler
dockers dirait qu'on pose pour y m elle
donc pour le indiqué que ça c'est du
langage hamel premièrement on va
commencer avec la version de ce fichier
donc on indiqué que c'est la pression du
panel au niveau du service
hong kong a déclaré notre premier
service qui est celui standing qui va
jouer le rôle de serveur d'application
au niveau de l'image nom de notre image
en fait la pnj revendique ingla que
cette version sera confession table un
pin donc je vais vous montrer comment
retrouver ses fonctions donc là on a
maintenant on a le docteur donc c'est
assez le
logis street au coeur donc où est ce que
on peut trouver des images doc r
bien sûr il faut identifier là si vous
n'avez pas un grand de retour à troquer
un camp ensuite se connecter et là haut
niveau 2 indique donc je vais choisir la
l'image officielle
et par la suite vous allez voir là que
sont les versions donc qu'ils seront
disponibles donc on préfère toujours
choisi d'une version stable
voilà 6
au niveau des peuples
donc comment on va communiquer avec ses
6 ans et cela à travers le pays
81 80 m 2 3 90e va rediriger le parquet
danois sur le port 80 81 eur la petite
remarque que moi c'est explique que j'ai
choisi 80 80 heures c'est pour vous
montrer comment débloquer ces terrains
par la suite parce que nous ne voulons
pas très autoritaire c'est un peur de
backup pour le protocole tcp donc on ne
peut pas l'utiliser ma maman à la fin de
la vidéo on va changer ça à 34 90 heures
il ya 98
mais c'est exprès là pour vous montrer
comment des bouquets des erreurs au
niveau de notre projet qui intègre donc
la solution doc est donc là ce que je
vais faire je vais monter ceci donc à
travers la commande au caire s'oppose à
demander - des poseurs des monstres des
cousettes incessants dans ces eaux-là
des plans
donc on voit là il est en train de
récupérer donc
l'image de m jinks depuis le xiv donc
fait en train de télécharger les
fichiers nécessaires
des fois donc le pool et complique
voilà donc voilà à télécharger une
nouvelle version de hunting quéribus
constate donc ces dames se dissiper
maintenant on veut voir à travers la
commande dockers ps la liste des images
qui sont montés donc comme vous voyez là
donc l'épaule ils sont rédigés là-haut
ou 2,84 à faire donc on va tester un x
et wikileaks et fonctionnel
bon
voilà
ce qu'on va faire maintenant on va
lancer la commande kompozer à beit on va
faire une mise à jour de notre
composteur je vous rappel composé c'est
donc le logiciel qui va gérer la gestion
des package et de notre dépendance donc
on va faire une mise à jour de ce
programme
lui vient donc c'était le mien je suis
ici et là donc on va continuer le reste
donc des sept vis
donc là un vrai besoin
de l'apn donc lula c'est
notre php donc c'est notre langage de
script ce côté serveur
on aura besoin pour lancer des requêtes
la dynamique surtout qu'on va puiser
dans la trop tard une thèse de données
de type my sql
donc au niveau de mobilité la bile dans
le contexte c'est le courant et là on a
indiqué qu' on aura un fichier doc est
donc à travers la tribu de café et là il
se trouve dans ce projet dans le dossier
dockers plage ftr dockers file donc bien
sûr j'aurais besoin de crier ce dossier
qui s'appelle de 15 au niveau de la
connaissance de mon projet
et à l'intérieur je vais ajouter un
fichier qui s'appelle aspect m.de caf a
bousculé ma tête la configuration de
notre image
fpm bien ph8
donc on voulait la jcct liées à un
dossier de kate et ensuite je vais créer
un fichier qui prenons un point de côté
le mouvement touche excellent vie sans
voir que on va ajouter un petit fichier
là
pour éclairer les configurations les
pour nettoyer un peu notre code
donc on va revenir à haut contenu ce
fichier la suite au niveau des volumes
alors que les volumes c'est la manière
qui nous permettent de sauvegarder des
données au niveau d'une image parce que
l'image récupérer à partir de quel
peuple et l'élite en lit donc on peut
pas les changer donc s'il ya des
changements donc là de notre cas on va
indiquer que ce sera sauvegardé au
niveau de slash var stage nous plaît
wsta html
donc au niveau des liens on va dire que
ce pm dans ce pays il sera relié aux
services d'e bay donc je vais déclarer
faillite
qui donc est
responsable de la partie de gestion de
données donc là aussi on va regrouper
les services à travers un réseau
donc et en 26 courses et des oscars
larvée
on va dire que m6 hélas pas tiens à ce
réseau on va voir comment le modifier
par la suite
et au niveau de construction pour te
penjing plein dans notre cas on va
mentionné le contexte on va dire que
c'est le contexte collants et au niveau
d'autres elle aussi
on va indiquer qu' on va se garder un
fichier
pour pas figurer le service jinks
donc c'est ça jinks forme de pâte fine
de personnes
voilà donc vous allez vous aussi de
créer ce fichier au sein de notre
dossier
ok
on revient un cadeau qu'elle compose
donc là on a indiqué c'est quoi le choix
de configurations de hal gill c'est quoi
le chemin de configuration de php à
travers le celui cfpm
donc là on a indiqué que
ce service
jinks et sera en lisant avec fpm avec le
service ap hp
sétif au niveau de volume d'à donc si on
a des données sauvegardées ont indiqué
le chemin de sauvegarde
coût
donc qui se sera penché le répertoire
courant donc le répertoire courant ça
sera lié aux espoirs s'achevèrent slash
ww flash html maintenant on va déclarer
donc notre soliste et b
donc c'est l'image que je veux dire donc
mais ce qu est la version 5 points 7
mais si on peut finir votre question il
faut venir au niveau du site web de
colloques pour choisir la version que
vous avez puisé au niveau des peurs donc
quand vous avez le peuvent donc mais ce
qu'elle fonctionne sous le par ton pot à
0,6
car on va quitter le même pas peut pas
le changer
et si vous changez un policier de
non fonctionnement de sélys manquerait
donc là haut niveau vant la tribune
valmont va déclarer un enfant de
l'information donc la première ça sert à
masquer route passoire donc lui indiquer
la c'est quoi le mot de passe du route
tankers kc route aussi en vain indiqué
un mince curieuse donc comment va se
connecter à notre base de données mysql
donc on va indiquer que
c'est grâce à lui et aux lieux saints et
au niveau du mot de passe de
l'utilisateur donc on va le montrer
ainsi
donc vous allez voir tout ça ce sont des
informations pour mieux les utiliser par
la suite lorsqu'on veut se connecter
entre eux base mysql
donc le mot de passe puis choisissent la
paix soit et au niveau de mysql
database n'est donc
là on va indiquer c'est quoi le nom de
ben est donnée à laquelle on va se
connecter de la coca et là il y avait 10
bd la révèle
donc la non ce sont les configurations
nécessaires monsieur là c'est au niveau
de l'ue notre image on voit que il faut
configurer notre projet le révèle la
presse mise pour que les données soient
donc
les mêmes l'art au niveau de
configuration de l'image dockers et de
notre projet d'un pôle résout dans sa
salle ravel et comme vous voyez donc on
aura une liaison la vesle entre tous les
services
qu'on a crié de notre donc de quel point
tu poses points jamais
donc on va lier ensemble
et comme ça ils peuvent avoir des
communications
entre
classé au niveau de notre fichier doc
point compote
donc là il faut aller au niveau du
fichier pas on est au niveau de la
partie mais sql attention donc au niveau
de db est dorénavant il sera plus
127.0.0.1 mais plutôt le nom de notre
service db dakar et au niveau de
deux autres informations donc on va
garder le db connexion m'en excuse le
peuple veut le garder si 33 06 nom de
passe données non on indique que ce sera
d'aider la reverse à des partenaires
larvée donc il faut les changer ici dès
la veille au
niveau de username d'ampoulés choisi
user
donc on va le communiqué au niveau de
notre projet l'enlever
et au niveau du mode presse dont
convaincu que ces prêts soient
voilà
on va pas lui c'est voilà donc la
automatiquement c'est comme si c'était
une synchronisation là pour le projet la
révèle et notre
hachée crue ou d'appeler
maintenant on va se déplacer au niveau
de bhp est là ont indiqué ces ckoi
l'origine de
cette image
donc là on va dire que ça sera forum php
et là si on revient à notre heure
locale au delà
[Musique]
d
au php là
vous pouvez choisir la version
officielle
si on descend on bat la
noix le lien vers les
différentes versions de php et on va
choisir plus lors des préférences ça
dans ce cas vous allez choisir
révolution
et point fr
voilà dans quel est hélas
quand vous voyez tout ça ce sont des
versions il ça dépend de votre projet a
donc faire attention si on travaille
avec la veille il faut pas voir une
question
inférieur à cette moto est donc de notre
cas on va choisir le point 8 pour moi un
point 1
tf pm et ensuite on va annoncer donc
nous commandent à travers donc le mot
claire-anne c'est la apt-get ah ben dis
donc on va faire une mise à jour l'anti
stage il nous permet de décrire une
instruction sur deux lignes et là dans
notre cas qu'est ce qu'on va faire et
dockers cgt
pas besoin doit installer de pdo là
mysql
voilà
[Musique]
maintenant au niveau de fichiers de
configuration d'origine
on a indiqué la ssii x donc normand sur
mathieu rien il va à choisir la version
stable et on va ajouter un ensemble de
paramètres
donc là on va synchroniser les fichiers
dockers se lâche comme la sienne ce
printemps donc là c'est un dossier qu'on
que je vais crier aussi
un intérêt de dockers dans un sein de
ces deux configurations et à l'intérieur
on va choisir pour la création d'un
nouveau fichier qui s'appellerait aux
points comme
celui là il devra la configuration
nécessaire niveau
de 1,6 donc là on va le lier un officier
des folk printemps donc ici le clitoris
l'a scootée 6 note jing flashback point
d donc ce cash différents camps donc si
riche et ce sera synchronisé avec le
pied bien qu'encore est donc là on va
trouver le tout et configuration de
notre cerveau application hendrix et au
niveau de notre erreur work dit ça veut
dire working directory
le répertoire de travail est mentionné
que ce sera cela sur la double double
doublé slash un schéma maintenant au
niveau de notre configuration de notre
serveur d'applications et jx revendiquer
la selva avait indiqué que le port de
coûte donc nommément le projet coûte 120
sur le port 80 et on va mentionné la un
ensemble de paramètres donc de
configuration de notre serveur x
donc on va indiquer le nom du serveur
c'est revenez on va indiquer la
le loot
donc notre chemin où est ce qu'on va
trouver notre index fra.php donc dans
notre cas ce sera cela cheval crise
l'acheter mais recyclage public et comme
vous savez le dossier public c'est lui
qui contient au bout d'un projet la
ravelle il contient le fichier à des
engagements donc si on cherche la index
on va le trouver dans ce dossier au
niveau de l'index donc si un client
d'être à nouveau de doute là ce sera le
digital index.php là on va voir le la
redirection bien lundi question où est
ce qu'on va sauvegarder les données des
erreurs en bloc des erreurs dans ce sera
dans ce cas tu as l'âge classique h
nginx la chaire points
maintenant au niveau de location va
indiquer comment trouver les fonds m et
les fichiers et on va indiquer la dui
lasser
ce sera de l'algérie et avec donc une
expression régulière là pour vous nous
indiquez vos scores on peut trouver
officielle
donc là au niveau 6 2
si on va passer des paramètres donc ce
sera cela à travers le gorille a inscrit
donc ce sera passé en permettre la
niveau de l'origine aussi
donc on va indiquer
disons-le aux questions qu'ils veulent
[Musique]
non
en tissage point bhb dollars et là on va
écrire ensemble de paramètres
concernant face à gien donc on indiqué
dans les basses
donc de notre cas ce sera le service fn
sur le panneau demi donc je vous
rappelle fpmc il fait référence à nature
à cette liste php
lindon et audrey sur pépé il est en
écoute sur le port nous
aussi on va indiquer
fest d'un terrain assez génial d'apparat
et vous faire attention aussi vous pas
changé de paris dirigé le poids est
fluide donc failli rater la parade et là
on veut faire inscrire année
donc
le nom de notre fichier réelle passe on
va indiquer le chemin donc rien à
et ensuite on va ajouter une autre le
fera si j ai donc
dit
et icloud on va inclure c'est permettre
la festive et princes face et jeudi
attiré par brahms voilà
comment ça c'est au niveau de la
configuration de notre serveur
d'applications ngx donc là
les vies des luttes avec la commande
clients linux ensuite là je vais lancer
la commande qu'elle compose et je vais
lancer la construction de notre projet
et de notre heure est donc h lectures
d'auteurs
donc il est en train de construire le pm
finished
maintenant il est en train de construire
donc le service magics
voilà
tu fais
notre composent un monde et
donc je vais lancer ses services en et
les plans pour ne pas bloquer notre
terminal alors qu'il a lancé
l'accueillez d'enclumes javel de canal
jx paix à pêche bd bpm et jx c'est bien
donc là on va essayer de voir
les images qui sont dans ces dockers ps1
y ait une qui manquent
donc il a généré le jx
d'anciens essayé de se connecter sur
lequel restera quatre marques
autoritaire
toujours là ils n'arrivent pas à nous
non c'est l'arjel normalement à cette
étape on doit avoir un jeu démarrage la
navette donc la page de démarrage donc
là je vous rappelle qu'on a aussi un
logiciel de cadrer ce cas là qui peut
installer et celui là il va nous
permettre de voir les images qui sont
mékong ou et là on a deux images qui
sont lancés en verre et le nzxt et les
visites donc là si je lance là il ya
quelques heures à cela qu'ils
apparaissent
donc qu'est ce qui nous dit la
1re mi-temps face jscript un hymne
si donc on a un problème là haut niveau
de fichiers parce qu'on a une erreur non
voilà face à j 1 là il faut éliminer cet
espace l'empêchement ensuite passagers
je veux le construire le projet
rapidement
[Musique]
sûrement
c'est bien donc on va tester maintenant
les images qui sont montés est toujours
là le mjic serveur d'application n'est
pas monté
[Musique]
donc on va faire
d'accor le composent la mouette et on va
voir ce qu'il ya une erreur quelque part
au niveau de fichiers leurres
qu'est ce qui nous dit on la gauche n'a
c'est le monde services au niveau de
hedging voilà on va le suivre la honte
où vous voyez pm et en bas on arrive
donc invalide par hamit
donc toujours là donc je vais ajouter un
espace voilà après le slash
je veux le construire
voilà
6
très bien dans je vais maintenant
monter
donc envoyé il ya les deux images qui
sont augmentés donc je vivais à travers
la commande de 90 15 14 ap mandela dont
je vais augmenter les images et vous
voyez maintenant il est en train de le
payer la belle angie
jinks
je
donc je lance la commande tôt qu'au ps
et quand vous voyez maintenant les
toiles sont lancés dont on a un jeans
fpr m excuse donc maintenant si
je fais deux cas le buzz
a demandé donc on a les toits ils sont
les trois mots clés
et judokates ps
voilà donc je teste la caresse 94
je vois un petit problème là donc on le
voit c'est quoi le problème le problème
comme je dis là c'est lié aux porcs la f
1 80 m parce que tu as une folle de
bacad deux ep donc on va choisir un père
qui n'est pas utilisé un you do bien
réserve de pas donc on a le port 80
99 bien 98
donc je vais arrêter les images et faire
la direction du port terme envers le
porte-avions 98 donc là le lard et des
images s est fait maintenant des
conteneurs mettant 2 4 compost a demandé
et je vais demander une deuxième fois
avec les autres et à la au niveau de la
direction de notre part
voilà maintenant s'il fait deux ps on va
vérifier est ce que le parent a été
redirigée correctement oui donc là au
lieu de 84 à hauteur je vais mettre 80
90 8 voilà
voile comme tout donc on attendait en
tant que chargé et voilà donc notre
site caravelle et fonctionnel jusqu'à
maintenant on a monté la cette partie
donc
le serveur d'applications et
fonctionnelle la partie bhp est
fonctionnel la ravelle et fonctionnel
donc maintenant on va créer une
application puisse connecte à une ps2 et
donc on va lancer php le celi artisans
php artisans mais quand on va donner
leurs paramètres le nom de notre
contrôleur
dantesque en taule c'est ceci a été créé
avec succès tant qu'on va trouver dans
un apache et tippingpoint voilà
le conteneur a été créé
[Musique]
on va ajouter celui mettant au niveau de
ce contrôleur
et avant de faire ça on va ajouter un
modèle là où est ce qu'on va se gâter
[Musique]
il étonné l'anc la finition 2
on va faire un
et hp attisons mec modèle est là on va
donner le nom de notre modèle parce que
dans le canton arnaud a besoin de faire
une référence vers notre modèle
voilà modèle qualité de chef étoilé donc
on va le lier deux dossiers modèle ce
dès ce midi qu'hp voilà
attends si je viens au niveau de mon
côté
on va éviter une référence de notre
modèle 20 pouces abl anti ch models
antistar le nom de notre modèle dans ce
cas c'est simple et est modeste en cash
qui est donc
est ce la tvq pour indiquer la fin de
l'instruction
et lara gut est une méthode au niveau de
notre contrôle donc on va le déferrer
comme étant publiques ça veut dire
excessive en dehors de cette queue de
cette classe donc public fonction qui
s'appelle tests ont le goût de tests en
mako dans notre cas on va déclarer une
variable qui s'appelle modèle on va là
déclaré comme étant new
day ce modèle
par gu
ensuite là on va
préparer donc
les coûts des données qui sont
sauvegardées au niveau de la base
donc
à travers les colombiens sur est court
et on va utiliser la classe bb de passe
est donc là dans notre cave accusé la
fonction verdun et on va
afficher le contenu de notre modèle
modèle de l'art moderne et on va appeler
la au niveau de notre modèle la fonction
qui détestent lors de notre camp on va
revenir au niveau de notre modèle est
dans notre modèle on va créer cette
fonction et 6 7 fonctionne à moore qui
va se connecter à l'internet base de
données
pour récupérer les données concernant
la tablette est qu'on appelait la suite
on va la retire 38 notre lent au niveau
de nos classes de ce modèle on va
déclarer à une fonction test mais
surtout ça moi je les fais pour tester
la connexion à la base mais est ce qu
elle est dans une prochaine vidéo on
voit comment utiliser les migrations et
tout ça donc pour faire abroger la 28e
avancée mais juste la rouler en train
d'apprendre les principes de règne donc
là de notre cas on aura besoin de la
classe de bep cette classe de bilan elle
appartient illuminés du paraître et 7
ans 8 db
donc c'est la classe lui permet de se
connecter notre best donc bretonne db
deux points de caen
et là on m'indique été bonne l'autre
table on va l'appeler test
et landrin guette
m
on va récupérer les données de cette
halte est maintenant ce qu'on va faire
on va se connecter au service masqué et
on va se connecter sur le terminant donc
je suis au ps et remarquez bien moi je
vais lancer image de une bêche ou bien
donc un terminal sur notre heure images
etc envoyez moi uniquement pour indiquer
le nom de l'image j'indique l'étoile
premières lettres donc 5e 4 c'est celui
de l'image de m'inscrire et ensuite je
note le beh voilà donc le terminal est
ouverte
donc je vais lancer la commande mais ce
qu elle tirait eu et ensuite le nom
d'utilisateur de notre parole à produire
une longue visite à kolontar user - paie
donc je vais rentrer le password mais
surtout ça on la saisit au niveau de
configuration au niveau de fichiers par
an voilà password
donc je vais écrire l'arrêt soit mais ce
grenelle n'est pas le voir là parce que
c'est discret et je suis dj cieux dont
20 me de commandes mais espère donc la
première non je vais sélectionner le nom
de notre base de données dans notre cas
sera bdr avait donc atteint vers la
commande du sbt la baisse oui la date à
bestiaux ensuite il fait chaud des vols
pour afficher la liste des tables qui
existent non en cette baisse de nos
tabous et 17 10 n'y ait pas de baisse
donné jusqu'à maintenant donc je vais
lancer la commande est ce qu a regretté
vol test je vais donner des
des attributs de cette table donc
premier le monde et dit les deux types
int et déjà il est auto imprimante
qui va être gérée automatiquement par le
sgbd et ce sera notre club et mêle donc
à travers prat mary qui vécut donc mieux
giclé une table simple l'a composé de
été dit dans le nom ce sera un rachat de
cinq ans
donc là
et celui là ce sera notre nul
réguler
là je vais ajouter à notre champ qui
écrit ted est et je vais lui associer
une date la date de création de ce crime
à travers donc le titre atteint ce
temple est par défaut different ce sera
comme un terroriste il fournit pas cette
information et si ça ce que je vais
faire ça craint times time ça veut dire
le temps coule en
voilà
ensuite
eugène est gage innodb
[Musique]
voilà points
ok donc c'est bien passé donc s'il fait
chaud thé vous et là que adaptait ses
parents
mais ceci vous maîtrisez cette console
cette manière des quêteurs vous n'aurez
plus besoin de logiciel qui vous
aide à un pays ou bien géré les deux
requêtes donc là on va lancer dans ces
tables quelques quelques lignes dont
seul un test au niveau de la tribune ont
donc n'aura pas besoin d'indiquer l'aï
dit parce que c'est autant un clémente
je l ai besoin uniquement d'indiquer une
chaîne de caractères pour le non donc
voilà si je fais maintenant un select ou
bien je vais ajouter une deuxième ligne
la vendeuse
de tester la section
voilà donc la devienne indigne a été
inséré non pour est ok
c'est
donc je vais ajouter aussi une 1e rocla
au niveau du fichier way-points php pour
nous diriger vers la fonction test
au niveau du contrôleur est un modèle
pour récupérer la liste des citoyens
qu'on a déjà ajouté
donc
là on va ajouter la préférence verne
notre contrôleur move your savent en 10
classes
http quantis les contrôleurs ce petit
strech
on appelait l'artiste contre la voilà
ap
et là donc
on va écrire notre nom de contrôleurs
dans ce test quant aux
deux points de caen place
et par la suite en faire un petit pécule
la voilà donc comment
la belgique et la gêne dick
lamentablement de la méthode dans cette
classe
de sauvegarde et violente mettons nos
cadres à 88
[Musique]
au
niveau de notre fichier test modèles psp
la ligne ans voilà et dr en rouge la
rumba donc on va il manque le mans a
fléchi
donc le symbole supérieur voilà après le
tir est supérieur voilà
donc le sauvegarde je le lance
et voilà donc on obtient les données qui
sont là donc la convoyer là le nom ces
listings de 8 donc là toutes les données
et donc
des lignes qu'on a déjà scellé tout à
l'heure
maintenant on va voir comment voici donc
des visionnaires il nous propose une
version la fri
donc c'est la version 12.1 points 5
donc cette élection il peut nous
permettre de visualiser les données qui
sont dans les têtes non pour moi je vais
vous montrer comment l'utiliser pour
consulter le contenu de vos bases de
données donc là on va utiliser
la table et ensuite cuite database
connexion on va utiliser le la six ans
donc on va l'appeler bt la nouvelle
connexion
[Musique]
ensuite là je vais choisir le pilote
lama sql
de belles prenait on suivait lui fournir
avant de donner donc là au niveau de
la tablette on va l'appeler là ce sera
bd larvée
au niveau de l'identification donc on va
puiser donc le
user donc monsieur il faut que ceux-ci
soient activement au paramétrage qu'on a
indiqué au niveau de notre projet là
révèle donc au niveau d'établir si vous
êtes ensuite s'asseoir comme presse je
fais pingtest hébron et voilà donc
maintenant notre connexion est ouverte
vers la base est là on peut voir la
table test quand vous voyez la 70
créations si j'appuie sur la date
annoncée j'obtiens là les données de
cette table
[Musique]
et