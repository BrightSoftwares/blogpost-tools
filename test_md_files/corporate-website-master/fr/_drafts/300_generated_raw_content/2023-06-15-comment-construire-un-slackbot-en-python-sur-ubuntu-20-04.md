---
author: full
categories:
- slack
date: 2023-06-15
description: Un Slackbot est un programme automatisé qui peut exécuter diverses fonctions
  dans Slack, de l'envoi de messages au déclenchement de tâches en passant par l'alerte
  sur certains événements.
featured: true
image: https://sergio.afanou.com/assets/images/image-midres-31.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-15
pretified: true
ref: slackbot_202007051234
tags:
- slack
- bot
- ubuntu
- python
title: Comment construire un Slackbot en Python sur Ubuntu 20.04
transcribed: true
youtube_video: http://www.youtube.com/watch?v=bi0cKgmRuiA
youtube_video_description: In this Docker Tutorial I show how to get started with
  Docker for your Python Scripts and Python Web Apps. We look at two different ...
youtube_video_id: bi0cKgmRuiA
youtube_video_title: Docker Tutorial For Beginners - How To Containerize Python Applications
---

#  Introduction

salut les gars aujourd'hui je veux vous montrer comment
vous pouvez utiliser docker pour votre application python
je vous montre tous les éléments essentiels
pour commencer, puis nous examinons
deux projets différents et comment nous pouvons les
dockeriser
le premier est un simple script qui  a besoin de
dépendances supplémentaires et le deuxième
projet
est une application Web avec une API rapide
ce deuxième exemple montre également comment
dockeriser un environnement virtuel
donc cet exemple est l'un des
cas d'utilisation les plus courants pour docker
et si vous me suivez ici, vous
devriez pouvoir  appliquez ceci pour tous
vos propres projets,
donc tout d'abord, qu'est-ce que docker
en termes simples, docker est un outil qui
vous permet de mettre votre application dans un
conteneur,
ces conteneurs vous permettent de conditionner
l'application avec toutes les pièces dont elle a
besoin,
donc tout  les bibliothèques et toutes les autres
dépendances
, puis nous pouvons le déployer en tant que package,
donc
si un autre l'utilise,
il n'a pas à se soucier d'
installer tous les bons depe  ndencies d'
abord
pour que nous puissions commencer à l'utiliser tout de suite d'
accord alors maintenant commençons à dockeriser nos
applications python
[Musique]
tout d'abord nous devons installer docker
bien sûr donc pour cela vous pouvez aller sur la
page d'accueil officielle
docker.com puis cliquer sur obtenir  démarré
, puis je recommande de télécharger et d'
installer docker
desktop afin que cela vous donne à la fois l'
interface de ligne de commande et également une
application de bureau utile, alors choisissez votre
système d'exploitation et téléchargez-le et
suivez les guides d'installation
et une fois que vous l'avez installé, vous pouvez le
vérifier dans  votre terminal en tapant
docker moins v
cela devrait vous indiquer la version actuelle de docker
alors oui ici nous pouvons voir que j'ai déjà
cela sur ma machine,
donc cela fonctionne et ici
j'utilise
le code visual studio comme mon éditeur et si
vous utilisez la même chose,
je vous recommande également d'installer l'
extension docker
afin que vous puissiez accéder au type de palette de commandes
dans les
extensions d'installation, puis recherchez ici
docker et u  voir l'extension docker officielle
de
Microsoft donc j'ai déjà installé ceci
et cela vous donne de belles fonctionnalités par
exemple pour le débogage ou pour l'
auto-complétion alors allez-y et faites ceci
et maintenant nous pouvons commencer à dockeriser notre
premier
script python donc pour le premier exemple



#  Example 1: Python Scripts

je veux  avoir un seul script python
main.pi et pour cet exemple,
je vais utiliser le code d'un autre
tutoriel que j'ai déjà ici
sur ma chaîne, donc c'est le
tutoriel de grattage de film imdb où je
gratte les graphiques imdb puis
suggère au hasard un film
donc cela utilise la
bibliothèque de requêtes et une belle soupe et si cela vous
intéresse, alors allez-y et
consultez également ce tutoriel, donc je
vais mettre le lien dans la description
alors maintenant je copie et colle simplement ceci
et ici je m'occupe  avec une entrée d'utilisateur
également,
donc pour l'instant je commente ceci, mais je vais
vous montrer comment nous pouvons l'utiliser dans une
seconde également, alors
commentons-le afin que nous puissions maintenant commencer à
stocker cela
et la première chose dont nous avons besoin est  un
fichier docker donc nous devons
différencier trois choses différentes le premier est
le
fichier docker puis nous avons l'image docker
et ensuite nous avons un conteneur docker
donc un fichier docker est un plan pour
créer des
images une image est un modèle pour exécuter des
conteneurs
et le conteneur est alors le
processus en cours d'exécution réel
où nous avons notre projet de package,
donc la première chose que nous devons faire est de
définir
notre fichier docker et d'ailleurs nous pouvons
utiliser des
commentaires ici comme celui-ci et la première
chose que nous devons faire est  spécifiez
une image de base donc ici nous pouvons dire de
puis utiliser python puis deux
-points et nous pouvons spécifier la version 3.8
donc cela extrait cette image du
hub de docker qui
a déjà installé python donc nous avons
tout
ce dont nous avons besoin pour avoir python dans  notre
conteneur
et maintenant la prochaine chose que nous voulons faire, nous
voulons ajouter ce fichier de tarte principal
dans notre conteneur, nous le faisons donc en
disant
à puis la source
est le point principal pi et la destination est
juste un
point donc dans le  e répertoire actuel dans notre
conteneur
maintenant que nous avons que nous devons installer
les dépendances, donc comme je l'ai dit, nous
utilisons des requêtes et une belle
soupe, nous devons donc les installer avec pip et
nous pouvons le faire en disant
run puis simplement la commande
pip  demandes d'installation
et aussi belle
soupe et je suppose que le paquet pip
s'appelle belle soupe
4 alors maintenant que nous avons cela
, la dernière chose que nous devons faire est de
spécifier
la commande d'entrée lorsque nous démarrons
notre conteneur et ici nous voulons dire
python et  puis en tant que paramètre de secondes
ici, nous disons une
barre oblique puis un point principal
pi donc cela exécute simplement python
main.pi
dans notre terminal de conteneurs donc
maintenant nous avons tout pour notre fichier docker
et maintenant nous devons créer notre
image docker donc nous le faisons avec  la commande
docker build moins t pour la
balise puis le nom de l'image donc
j'appelle ce python
imdb et appuyez sur entrée et je dois également spécifier
l'emplacement donc ici j'utilise simplement un point à
nouveau
et maintenant il construit l'image et comme
yo  vous pouvez
voir que c'est um exécuter ces étapes
dans cet ordre donc l'ordre est important
donc il tire l'image python puis
il ajoute main.pi
puis il installe les modules et
puis nous avons terminé et puis quand nous démarrons
notre conteneur alors il exécute ceci
fichier puis nous commençons notre conteneur en
disant
docker run puis le nom de l'
image
python imdb puis nous voyons que notre
conteneur démarre et le script est en
cours d'exécution et nous obtenons une
suggestion de film aléatoire puis notre conteneur
arrive à la fin donc  il s'arrête à
nouveau,
alors maintenant nous pouvons réessayer
, puis nous devrions obtenir une autre suggestion aléatoire,
donc cela fonctionne et
maintenant, comme je l'ai dit ici, j'ai commenté cette
partie où nous avons
utilisé l'entrée de l'utilisateur,
alors laissez-moi la remettre à nouveau  alors
maintenant, nous avons le
script complet et l'enregistrons, puis nous devons
reconstruire notre image docker, donc encore une
fois, nous exécutons cette commande et maintenant, si nous
démarrons
notre conteneur avec cette commande docker run
comme celle-ci, alors ce sera cras  h
donc oui donc nous voyons que nous obtenons cette
erreur eof et c'est parce que si nous utilisons
une
entrée utilisateur, nous devons utiliser
des arguments supplémentaires pour la commande docker run
, nous devons donc dire docker
run moins t et moins
je donc le i se tient  pour le mode interactif
et le t nous donnera un pseudo terminal
et où nous pouvons taper l'entrée de l'utilisateur,
donc maintenant, si nous l'exécutons comme ça, cela
devrait fonctionner à nouveau,
alors maintenant cela fonctionne, nous
obtenons donc une
suggestion de film, puis il  nous demande
si nous voulons voir un autre film si je dis
oui alors cela devrait m'en donner un autre
et oui
et oui donc cela fonctionne et puis si je
dis
non alors cela devrait terminer le script et
terminer également le
conteneur bien donc c'est  fonctionne



#  Example 2: Web App

et c'est le premier
exemple maintenant regardons un tutoriel plus
avancé
donc pour le deuxième exemple
je veux créer une application web avec
le
framework api rapide mais cela fonctionne fondamentalement de
la même manière pour tous les autres
frameworks web que vous utilisez donc nous  commencez par
créer
un vir  environnement tual puis installez les
dépendances
puis euh écrivez notre application
puis dockerisez-la
donc faisons-le bien alors ici je suis
dans un nouveau
répertoire vide et la première chose que je
veux faire est de
créer un environnement virtuel donc je le
fais par  en disant
python 3 moins mv et
vn cette commande peut être légèrement
différente sur Windows
et maintenant nous l'avons créée et ensuite nous devons
l'activer en disant
point v et slash bin
slash activer et encore cette commande
peut être légèrement différente sur Windows
et maintenant nous sommes  à l'intérieur de cet
environnement virtuel,
nous installons donc maintenant les dépendances
dans ce cas pour une api rapide, nous disons donc
pip install fast api
et nous avons également besoin d'un serveur Web, nous disons donc
pip install uv corn
et appuyez sur entrée, alors maintenant nous
avons cela et maintenant créons notre  app alors
créons
un autre répertoire ici, puis le
fichier principal point pi dans ce répertoire
et maintenant récupérons l'exemple de code du
site Web
donc celui-ci ici et collez-le ici
pour que cette syntaxe soit très similaire  à la syntaxe du
flacon
afin que nous créons une application, puis nous
définissons nos fonctions où nous définissons
les routes afin que nous ayons une route de base,
puis une route à slash
item slash item id
alors maintenant tout d'abord testons
notre application localement donc nous faisons ceci
avec cette commande ou
nous pouvons également le faire d'une deuxième
manière, alors laissez-moi vous montrer cela également afin que
nous puissions importer la
bibliothèque de maïs uv, puis nous disons
si le nom est
égal à la main
, puis nous disons uvicorn
dot run et ensuite nous voulons  exécutez
notre application donc c'est je pense la même chose ou
très similaire avec flacon
avec flacon vous pouvez également le démarrer à partir
du terminal
ou vous pouvez le démarrer avec flask.run à l'
intérieur ici ou app.run je suppose que c'est avec
flacon
alors oui alors faisons  c'est comme ça
et bien sûr nous devons exécuter le
script alors maintenant nous disons allons
dans le répertoire de l'application
, puis disons python main dot
pi et il dit que notre serveur
est opérationnel afin que nous puissions aller à localhost
8000
et nous  voir nous obtenons la réponse hello world
donc cela fonctionne et si nous y allons
pour réduire les
éléments slash ID d'élément,
nous obtenons la deuxième réponse que nous avons
spécifiée,
donc oui, cela fonctionne, alors arrêtons à
nouveau ce serveur et
revenons au répertoire racine de
ce projet
et laissez-moi effacer cela alors maintenant nous voulons
dockerize ceci donc la première chose que nous
voulons faire est de
sauvegarder toutes les dépendances dans un
fichier requirements txt donc pour cela nous disons
pip freeze puis le plus grand signe
et ensuite requirements.txt
donc cela écrit toutes les dépendances que
nous venons d'
installer dans ce  fichier donc nous voyons que nous
avons
une api rapide nous avons licorne et quelques autres
dépendances
donc la prochaine chose que nous voulons faire est encore une fois
nous voulons
créer notre fichier docker fichier docker
et cela devrait être dans le
répertoire racine de notre projet et là
encore nous commençons  en spécifiant une
image de base donc ici encore nous disons python
et version
3.8 et maintenant je veux faire quelque chose de nouveau
donc je veux organiser les dossiers
dans le conteneur d'une manière légèrement meilleure
donc je crée un répertoire de travail
avec  cette commande, puis
appelons ce répertoire dans ce
conteneur
fast api dash
app et cela ira également automatiquement
dans ce répertoire alors maintenant et
c'est notre
point de départ et maintenant nous voulons
copier l'exigence
dans ce répertoire de travail um donc nous
devons simplement  dites
deux points alors nous devons installer les
dépendances et nous le faisons à nouveau avec
la commande run
et cette fois nous disons pip install
puis moins r exige
mans dot txt alors
la prochaine chose que nous voulons faire est de copier
tout ce
dossier d'application avec le  main dot pi
file alors faisons cela en disant copier
et nous voulons copier à partir de l'application point slash
donc c'est le dossier ici
sur notre machine et ensuite nous spécifions le
nom du dossier
à l'intérieur du conteneur alors appelons également
cette
application alors maintenant nous avons ça  et maintenant, nous
devons également spécifier le
point d'entrée de notre conteneur, donc encore une fois
ici, nous utilisons
la commande python, puis nous voulons
exécuter le
fichier main.pi, donc c'est dans le
dossier de l'application point slash, puis slash
main point pi alors maintenant  c'est notre
fichier docker et encore une fois nous devons
construire
notre image donc nous disons docker build
moins t puis appelons ce
python moins fast api
et encore une fois j'ai oublié le point ici encore une fois
avec le
point à la fin pour l'emplacement actuel
donc  maintenant, cela fonctionne et exécute
toutes ces étapes correctement, donc cela a fonctionné
, nous avons donc maintenant un conteneur docker avec
toutes ces dépendances installées, nous pouvons donc maintenant l'
exécuter à nouveau avec la commande docker
run et le nom était python
fast api, alors maintenant ça  dit
que notre serveur uvicon fonctionne sur
localhost 8000
mais maintenant cela ne fonctionne pas, donc si nous allons
à nouveau sur cette route
, puis appuyez sur Entrée, nous voyons que
ce site ne peut pas être atteint, donc
pour cela, nous devons faire quelques changements
donc tout d'abord  quand
nous arrêtons à nouveau le conteneur,
alors tout d'abord, ce que nous devons faire,
c'est lorsque nous exécutons notre conteneur,
nous devons mapper le port en disant
moins p, puis nous devons mapper
le port de l'extérieur au port
du  conteneur
donc  comme ceci mais avant de faire
cela, nous devons également spécifier l'hôte
et la partie dans notre application afin que nous puissions le faire
ici
dans cette commande uv corn run et ici nous
pouvons
mettre dans l'argument
port le port est égal à 8 000, c'est donc la valeur par défaut de
toute façon
mais ce qui est également très important, c'est
l'hôte, nous devons donc dire que l'hôte est égal
, puis ici, en tant que chaîne 0.0.0.0,
c'est très important, donc c'est la
même chose lorsque nous utilisons
ceci ou, par exemple, lorsque nous utilisons
flask
nous toujours  devons spécifier cette
adresse d'hôte,
alors maintenant que nous l'avons et ce que nous
devons faire,
c'est à nouveau construire notre
image, alors exécutons à nouveau la
commande docker build, puis
exécutons à nouveau notre conteneur avec cet
argument de port moins et
nous mappons 8000  deux huit mille
donc maintenant si nous exécutons cela, cela devrait
fonctionner alors maintenant
encore, allons à cette
adresse localhost huit mille et appuyez sur Entrée
et maintenant nous voyons que cela fonctionne et nous
pouvons également aller à la
route des éléments, puis utiliser un identifiant d'élément
donc ceci  fonctionne à nouveau et nous voyons ici que
nous g  et les
informations dans ce terminal donc
oui maintenant notre application Web fonctionne
comme un conteneur docker
donc maintenant par exemple nous pouvons aller au
tableau de bord docker et puis ici nous voyons
qu'il s'agit du conteneur actuel donc
ici nous pouvons
inspecter les verrous ou supprimer ceci  ou
éteignez-le et redémarrez-le,
alors oui, l'application de bureau Docker
est très utile
et ce qui est également très agréable, c'est que nous pouvons
obtenir un
terminal à l'intérieur de ce conteneur Docker
si nous cliquons ici, alors maintenant nous avons un
terminal et puis je veux aussi
pour démontrer à nouveau cette structure de dossiers,
c'est donc en fait
mon terminal par défaut,
alors laissez-moi revenir à mon autre terminal
, puis je veux vous montrer comment nous pouvons le
faire avec la commande,
donc tout d'abord, nous pouvons dire docker ps
cela listera  tous les conteneurs en cours d'exécution
, nous voyons donc qu'en ce moment, ce conteneur
est en
cours d'exécution et c'est l'identifiant du conteneur
afin que nous puissions saisir cette commande
docker exec moins i
t, puis cet identifiant de conteneur docker
et le coller ici et ensuite  nous
devons dire
slash bin slash ace
h et maintenant nous obtenons le shell à l'intérieur de ce
conteneur en utilisant la ligne de commande
donc maintenant par exemple si nous disons ls
alors nous voyons que nous sommes actuellement dans
notre répertoire de travail donc à l'intérieur de
ce répertoire donc si nous allons un
dossier en disant cd deux-points deux-points
et encore une fois ls
nous voyons tous les dossiers et donc cette
structure de fichiers linux dans notre conteneur
et puis ici nous voyons ce nouveau dossier
que nous avons créé avec cette
commande work directory fast
api donc c'est pourquoi je l'ai fait  ceci donc maintenant
encore une fois si nous allons
dans ce répertoire um fast
api dash f c'est notre
point de départ
et encore une fois nous avons ce
répertoire d'application et ici nous avons le
fichier main.pi que nous avons copié avec cette commande
alors oui cela peut être utile parfois
pour
obtenir une ligne de commande dans votre
terminal et oui, c'est tout ce que je voulais
vous montrer pour l'instant j'espère que vous avez
beaucoup appris ici et si vous avez apprécié ce
tutoriel, appuyez sur le bouton J'aime
et envisagez de vous abonner à la chaîne
, puis j'espère  à voir dans la prochaine
vidéo au revoir