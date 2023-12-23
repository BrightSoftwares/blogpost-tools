---
author: full
categories: []
date: 2023-07-04
description: Minikube is a tool that makes it easy to run Kubernetes locally. Minikube
  runs a single-node Kubernetes cluster inside a Virtual Machine (VM) on your laptop
  for users looking to try out Kubernetes or develop with it day-to-day.
image: https://sergio.afanou.com/assets/images/image-midres-38.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-04
pretified: true
ref: playingkubernetes_1246
tags: []
title: Jouer à Kubernetes avec Minikube
transcribed: true
youtube_video: http://www.youtube.com/watch?v=bkrcAjclqYI
youtube_video_description: Hello Friends, Welcome back to my channel.Today we are
  here with another tutorial on Kubernetes. In my previous tutorials, we ...
youtube_video_id: bkrcAjclqYI
youtube_video_title: Play With Kubernetes | Free Kubernetes Cluster Playground | Thetips4you
---

# 

[Musique]
bonjour les amis, bienvenue sur ma chaîne
donc je voudrais vous remercier pour votre
grand soutien que vous avez donné
alors continuez euh continuez à
me soutenir et je vous en suis reconnaissant
donc aujourd'hui nous allons voir un autre
tutoriel sur
kubernetes  donc si vous avez vu mon euh
tutoriel précédent,
nous avons vu comment configurer kubernetes dans un
mini
cube et nous avons également parlé des
services de déploiement d'architecture et des pièces dans
kubernetes,
donc ce que nous n'avons pas fait, c'est que nous n'avons pas
configuré correctement une
configuration de cluster  avec le nœud maître et
travailleur,
donc puisque nous avons besoin de plus de ressources, nous
devons utiliser un nuage ou si vous avez un
ordinateur qui a plus de
processeurs et que vous connaissez la mémoire, vous pouvez le faire,
donc ce que nous avons vu, c'est qu'il existe un
moyen facile de  faites ceci
et c'est uniquement à des fins d'apprentissage d'
accord car
euh ce n'est pas une configuration permanente donc ce que
nous allons voir c'est comment utiliser un
outil appelé jouer avec
kubernetes d'accord donc si vous avez vu mes
tutoriels précédents j'ai aussi parlé de
dock  euh
en ce sens que je vous ai montré comment utiliser le
jeu avec docker
, c'est donc le même type de configuration où
nous pouvons créer des nœuds et nous pouvons
ajouter ces nœuds en tant que maître et travailleur
et vous pouvez l'utiliser pendant une courte période de
temps
et  à ce moment-là, il sera
automatiquement supprimé,
donc avant d'entrer dans les détails, comment le faire
si vous n'êtes pas abonné à ma chaîne,
je
vous demanderais de vous abonner comme cette vidéo, de
partager et de commenter d'
accord pour commencer euh vous savez si vous ne le faites pas
sachez comment trouver
euh jouer avec kubernetes il suffit de rechercher dans
google jouer avec kubernetes et vous
pourrez voir ce lien donc il s'appelle
labs.playwithkh.com
afin que vous puissiez cliquer dessus afin que vous
soyez redirigé vers cet écran où vous devez
connectez-
vous pour pouvoir vous connecter avec deux choses, l'une est
github et docker,
donc si vous avez l'un de ces identifiants de connexion euh,
vous pouvez l'utiliser
puisque j'ai déjà une connexion au hub docker,
je vais utiliser docker d'accord
donc cet identifiant d'utilisateur et  password sera le
mot
de passe pour docker hub.com o  kay mettre à jour
docker.com
afin que vous puissiez utiliser le même identifiant d'utilisateur et le même
mot de passe ici
et vous pouvez cliquer sur démarrer d'accord,
donc nous sommes maintenant pris dans l'écran,
donc si vous avez vu cela est presque
similaire au
jeu avec docker d'accord donc c'est euh
des sessions presque similaires où vous pouvez
créer une nouvelle instance, vous pouvez
ajouter une nouvelle instance euh et je pense que vous
pouvez créer cinq instances
et chaque instance fonctionnera pendant
quatre heures, donc après cela, elle sera
automatiquement supprimée, donc ce n'est pas une
configuration de production ou  où vous pouvez l'
utiliser à long terme, mais pour votre
objectif d'apprentissage, c'est certainement une
bonne façon de commencer, alors créons
une
instance, d'accord, alors laissez-moi créer
deux instances, l'une peut être utilisée comme un
nœud maître, une autre
peut être  a agi comme un nœud de travail d'accord, donc
une fois que vous avez créé si vous voyez
qu'il vous donne une adresse IP, quelle est l'
utilisation de la mémoire et quelques
détails, il donne également de la
documentation sur la façon de
faire cette configuration, donc c'est assez simple
à faire  t besoin de euh trois
commandes pour exécuter bien deux sur le
maître et une sur le nœud de travail,
alors vous aurez une configuration de cluster d'accord,
alors commençons
ce nœud en tant que maître d'accord, alors
initialisez
pour initialiser le nœud de cluster, vous devez
exécuter cette commande pour que vous  copiez maintenant
cette commande d'accord
faites simplement défiler jusqu'à votre curseur
et vous avez juste besoin de coller cette commande d'
accord
alors ne vous inquiétez pas de cette erreur vfs d'accord
donc
ce n'est pas un problème alors attendons que
cette configuration soit terminée
[Musique]
ça ne va pas  pour prendre beaucoup de temps, cela peut
prendre probablement une minute ou deux minutes
selon que vous savez combien de temps il
faut pour configurer cela
dans la mesure où j'ai vu qu'il faut moins de deux
à trois minutes pour terminer cette
configuration, vous pouvez voir que cette icône a
été modifiée et  ça
se configure
bien, donc si vous pouvez voir euh la
première
commande a été terminée et vous a donné
un lien ou une commande où il est dit que cubarium
join et
euh le numéro de jeton est donc
nécessaire pour votre euh  ajouter l'autre nœud en
tant que nœud de travail, vous devez donc le
copier et le conserver
quelque part d'accord, alors laissez-moi copier ceci et le
conserver dans un bloc-notes de travail, d'accord, alors laissez-
moi copier ceci et laissez-moi le mettre dans le
bloc-notes d'accord, alors nous  J'utiliserai ce euh pour euh en
ajoutant le nœud deux en tant que travailleur d'accord, donc
avant cela, nous devons faire une étape de plus,
donc si vous voyez que l'
étape deux consiste à initialiser la
mise en réseau du cluster
, nous devons également utiliser cette commande
alors allons-y  copiez cette commande
et revenez au
curseur pouvez simplement coller cette commande d'accord
maintenant si nous avons vu qu'elle a créé un
routeur bien d'accord alors maintenant toutes les
commandes sur le nœud maître sont terminées
donc si vous voyez que nous avons exécuté
euh le numéro un initialisation  le
nœud maître du cluster et le numéro deux est la
mise en réseau du cluster initialisé donc ces
deux sont terminés
maintenant allons à la note 2 donc ici aussi
vous pouvez voir que ces commandes sont là mais
puisque nous n'avons pas besoin que cela soit exécuté en tant que
maître nous ne sommes pas  va courir ça d'accord
alors laissez-moi revenir à t  la
commande de jeton qui est nécessaire pour
ajouter ce travailleur en tant que euh en tant que nœud en tant que
travailleur d'accord, alors exécutons ceci
et attendons que cela soit terminé d'
accord
maintenant si vous avez vu euh cela également
terminé en très
euh quelques secondes afin que vous puissiez  disons que
ce nœud a été rejoint en tant que cluster,
donc cela a également été fait d'accord maintenant
revenons au
nœud maître et effaçons l'
écran d'accord
et ce que nous savons si vous avez vu mon
tutoriel précédent, nous en avons parlé
commande de base à droite alors voyons ces
informations d'accord
cube ctl
cluster info
vous pouvez voir euh c'est l'information du cluster
c'est un maître est en cours d'exécution
et le DNS en ce moment vous allez au cube ctl
get nodes vous pouvez voir qu'il y a deux
nœuds maintenant le nœud un  est un maître et le
nœud deux est euh qui est un travailleur d'accord,
donc cette configuration que nous n'avons pas vue jusqu'à présent,
donc dans le mini cube, nous n'avons qu'un seul
nœud qui a comme maître et c'est aussi en
tant que travailleur parce que c'est un
environnement où nous don  je n'ai pas plusieurs
hochement de tête  es donc c'est
juste un euh vous savez qu'un nœud est configuré dans le
mini cube d'
accord, alors voyons maintenant s'il y a
des ports ou un déploiement en cours d'exécution, donc
cube ctl get parts
donc il n'y a pas de bonnes pièces cube ctl
get déploiements et il n'y a pas de
déploiements cube ctl
obtenir des services
donc il y a un service qui est l'
ip de cluster kubernetes euh d'accord donc le service kubernetes
et
euh avec l'ips de cluster 110.96.0.1 c'est
celui par défaut d'accord
alors effaçons cet écran et
essayons de créer
un déploiement et créons un service
d'accord,
donc si vous avez vu mon précédent tutoriel
sur le déploiement, j'ai créé un
déploiement avec
ngnx, donc je vais juste utiliser le
même
cubectl créer un déploiement d'
accord et je vais utiliser l'image
bien avant l'image dont j'ai besoin  donnez un
nom qui
va être nginx et ça va être une
image
égale à gnx
donc maintenant nous voyons que le déploiement euh est
créé donc si je vais au
cube ctl obtenir des déploiements,
vous pouvez voir qu'il y a un déploiement est
créé
donc  c'est maintenant qu'il affiche zéro sur un d'accord, alors
laissez-moi le relancer,
vous pouvez voir que c'est un slash un à droite, ce
qui signifie qu'il est disponible maintenant d'accord
maintenant si je vais au cube ctl obtenir des pièces,
vous pouvez voir qu'il y a une partie aussi bien en
cours d'exécution donc  lorsque vous créez un
déploiement, il crée une partie
correctement, nous ne créons donc pas de parties
séparément dans ce
didacticiel, vous pouvez également le faire,
mais si vous voyez cube
ctl obtenir svc ou services, nous n'en
avons pas  euh service en cours d'exécution pour
ce déploiement ng nx euh
qui est accessible de l'
extérieur,
donc ce que nous devons faire est d'
exposer ce
déploiement, donc ce que je vais faire est
cubectl
expose le déploiement le nom est nginx
et le type égal à
c'est  va être le port de nœud
et le port ça va être le port 80 d'
accord, c'est comme ça que nous pouvons exposer ce
déploiement d'
accord je pense qu'il y a une faute de frappe herodor donc
ça va être un
déploiement d'accord donc nous l'avons
mis ici alors mettons-le ici d'
accord  alors maintenant nous pouvons voir le service et le
gns
est exposé à droite alors essayons cube
ctl get svc maintenant vous pouvez voir
euh il y a un autre service de déploiement
appelé ngnx qui est le type de port de nœud
droit
et il est accessible en fait dans trois
zéro deux sept
zéro c'est le numéro de port huit est la carte
deux trois zéro deux  sept zéro à droite
donc je vais utiliser cette adresse IP
192.168.0 d'
accord et je vais
boucler ce commentaire cool d'
accord et ça va être le port
deux sept zéro
maintenant vous pouvez voir euh nous pouvons accéder
au ng  page Web nx c'est la page par défaut
pour nginx
si vous voyez cette page le serveur nginx est
installé avec succès et fonctionne
donc cela signifie que le ngnx fonctionne bien
maintenant
donc je pense que cela vous donne une
compréhension de base comment configurer un
cluster d'
accord donc  avec deux nœuds si vous voulez, vous
pouvez ajouter plus de nœuds
ctl obtenir des nœuds à droite
afin que nous ayons deux nœuds, nous pouvons ajouter plus de
nœud si vous le souhaitez, nous pouvons créer une
instance supplémentaire afin que nous ayons un nœud trois à droite,
alors revenons en arrière et copions la même
jointure  commande et venons ici
l  et collez ceci à la note 3,
vous pouvez voir que celui-ci a également
rejoint le cluster,
donc si je lance les nœuds get ici,
vous voyez qu'il y a deux
deux nœuds au nœud deux et au nœud trois
également, donc je pense que ce n'est pas
prêt mais maintenant il est prêt, il n'était
pas prêt auparavant maintenant il est prêt,
il y a donc trois nœuds,
un pour le maître et deux pour euh le nœud de travail,
donc c'est aussi simple que de créer un
cluster kubernetes dans ce
jeu avec l'outil kubernetes, donc
j'espère que vous le ferez  utilisez-le pour
apprendre kubernetes pour votre objectif d'apprentissage,
c'est un tutoriel assez simple, mais je
voulais juste vous montrer
cet outil qui est très utile pour les
débutants, d'accord
et j'espère que ce tutoriel informatif est
informatif pour vous
et je tiens à remercier  vous pour regarder et
je vous demande également de vous abonner à ma
chaîne
comme cette vidéo partager et commenter
[Musique]