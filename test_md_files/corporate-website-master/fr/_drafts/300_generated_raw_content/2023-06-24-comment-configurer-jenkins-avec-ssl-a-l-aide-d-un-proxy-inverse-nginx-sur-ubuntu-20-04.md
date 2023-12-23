---
ToReview: true
author: full
categories:
- docker
date: 2023-06-24
description: 'By default, Jenkins comes with its own built-in Winstone web server
  listening on port 8080, which is convenient for getting started. It’s also a good
  idea, however, to secure Jenkins with SSL to protect passwords and sensitive data
  transmitted through the web interface.

  In this tutorial, you will configure Nginx as a reverse proxy to direct client requests
  to Jenkins.'
image: https://sergio.afanou.com/assets/images/image-midres-32.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-24
pretified: true
ref: configure_jenkins_202007051235
tags: []
title: Comment configurer Jenkins avec SSL à l'aide d'un proxy inverse Nginx sur Ubuntu
  20.04
transcribed: true
youtube_video: http://www.youtube.com/watch?v=lZVAI3PqgHc
youtube_video_description: Reverse proxy is one of the most widely deployed use case
  for NGINX instance, providing an additional level of abstraction and ...
youtube_video_id: lZVAI3PqgHc
youtube_video_title: Configure NGINX as a Reverse Proxy
---

#  Configure NGINX as a Reverse Proxy Agenda Overview

hé
comment ça va, je m'appelle jay dans cette
vidéo, nous allons
jeter un coup d'œil sur la façon dont vous pouvez configurer
nginx en tant
que proxy inverse, le proxy inverse étant l'un
des
cas d'utilisation les plus largement utilisés pour l'instance nginx,
allons-y directement alors  ce que nous
allons examiner,
c'est bien sûr que nous aurons un aperçu rapide d'
une compréhension de haut niveau d'un proxy direct et d'un
proxy inverse,
nous examinerons la directive de passage de proxy
que nginx utilise pour transmettre la
demande à
un amont ou  un serveur principal, puis
nous examinerons également la redéfinition
des en-têtes de requête essentiellement pour essayer
de capturer tous les détails
du demandeur d'origine ou du
client d'origine et comment transmettre ces détails
au serveur principal réel
via le proxy donc avant de sauter  dans



#  What is NGINX and why is it lightweight? 

et parler de proxy inverse en
particulier
j'aime juste souligner le fait que
nginx euh extrêmement léger résilient
très très populaire en tant que serveur Web mais
la fonctionnalité de nginx n'agit pas
car
ne s'arrête pas à re  proxy verset ou un serveur Web
les cases vertes que vous voyez à l'écran euh en
ce moment
ce sont toutes les fonctionnalités que vous
pouvez obtenir avec une seule
instance de nginx également en plus de cela,
vous pouvez exécuter nginx où vous voulez j'ai
collé quelques logos  de quelques
fournisseurs de cloud ici, mais vous pouvez exécuter nginx
sur
n'importe quel cloud dans la mesure où vous avez un
système d'exploitation linux pris en charge
avec cela, commençons donc l'accent



#  What is a Reverse Proxy? 

sur cette vidéo
est le proxy inverse, alors allons-y
directement et alors
quoi  est exactement un proxy inverse,
il y a donc généralement deux façons de penser à un
proxy, l'
un est un proxy direct qui est
essentiellement un proxy côté client qui
cache l'identité
ou agit à la place des clients et le
second est un proxy inverse qui est un
proxy côté serveur
qui consiste à dissimuler l'
identité
du service d'application back-end réel
ou
agit parfois à la place de ces
serveurs d'applications back-end les
organisations déploient généralement nginx en tant
que proxy inverse
et  comme je l'ai mentionné plus tôt, c'est le
pire des cas d'utilisation les plus courants
pour l'instance nginx maintenant, comment
nginx fait-il que nginx fait un proxy en



#  How does NGINX work as a Proxy? 

utilisant
la directive proxy pass afin que la
directive proxy pass
déplace une demande entrante vers une
destination de remplacement à l'extrémité arrière
donc l'adresse peut être un nom de domaine
une adresse IP port unix socket
nom en amont ou même un ensemble de syntaxe de variables
pour cette directive ou le
bus proxy direct vous
est très simple c'est un pass proxy suivi
d'une destination
et il n'est généralement utilisé que dans un
serveur
et  contexte de localisation dans l'exemple que vous
voyez à l'écran en ce moment, ce que nous avons
est https.example.com
nginx correspond à cette demande spécifique
contre la barre oblique
et transmet la demande de la
destination avec laquelle dans ce cas est
10.1.1.4
donc l'adresse IP de destination  est très
probablement un serveur Web
ou un serveur d'applications assis derrière
un pare
-feu et peut-être l'adresse IP de l'
instance nginx plus ou de l'instance nginx que
vous voyez  ici ne serait que l'
adresse IP qui aurait
accès au serveur d'applications back-end
afin que les clients se connectent à ce
proxy inverse
et que le proxy inverse qui est votre
instance nginx ait accès au
serveur d'applications back-end
semble facile et il  est définitivement et
nous
verrons à quel point il est facile de configurer le
proxy inverse dans la démo après
cependant une chose que nous devons comprendre
est le comportement de



#  What is NGINX's default behavior? 

nginx et le comportement par défaut de nginx est de
fermer la connexion avant qu'elle ne disparaisse
out et
initie une nouvelle connexion au back-
end,
donc dans ce processus, certaines des
informations de la demande d'origine seront perdues, par
exemple lorsqu'une demande d'origine est faite à
partir d'
un client ou qu'un navigateur de votre ordinateur portable
atteint le proxy inverse et que les
informations vont
obtient  envoyé aux serveurs principaux nginx
met fin à cette connexion à ce
point de proxy inverse
, vous voulez donc essayer de vous assurer que vous
capturez certains des détails comme l'
adresse IP réelle o  f
le client d'origine euh l'hôte détaille ce que
vous écrivez la demande que vous voulez
essayer et la capturer et vous voulez la
transmettre au back-end ou au
serveur d'application en amont
la raison de cette tâche est que les
fichiers journaux de l'application back-end
le serveur capture la demande provenant de l'
instance nginx et maintenant,
si chaque demande provient
du
proxy inverse nginx pour essayer de donner un
sens aux données que vous avez collectées
à l'arrière-plan,
c'est une tâche impossible car chaque
demande unique de cela  la
perspective du serveur d'applications vient
du proxy inverse et vous ne
voulez pas essayer de capturer
l'
adresse IP d'origine et de la transmettre,
alors comment pouvons-nous faire cela
dans l'exemple ce que nous voyons maintenant
ce que nous pouvons utiliser est une directive  appelé
en-tête de jeu de proxy et essentiellement ce que fait
cette directive
est qu'elle permet à nginx de redéfinir
ou de réécrire l'en-tête de requête
qui vient donc essentiellement dans ce
cas ce que h  appens est nginx
remplace l'en-tête de l'hôte par la
variable qui est dollar host lorsqu'il
envoie une requête au serveur backend
dans le deuxième exemple ce que nous avons ici
est
un en-tête de jeu de proxy capture l'
adresse IP d'origine du demandeur
et la transmet au backend
le serveur d'applications indique donc essentiellement
au serveur d'applications principal
qu'il s'agit de l'adresse IP
du demandeur d'origine pour cette
demande
et de l'en-tête de l'ensemble de proxy final ce que vous
voyez ici
crée une liste de différentes adresses que
l'ip
uh et la demande ont réellement
traversé avant
il frappe le serveur d'applications principal,
donc dans certains cas, vous avez probablement
euh quelques serveurs Web quelques
proxys
avant que la demande réelle
n'atteigne le
serveur d'applications de réplique principal, donc dans un scénario comme
celui-ci, nginx sortirait et
rassemblerait tous ces ips  et envoyer ces
informations au
serveur d'application principal réel, donc
du point de vue du curseur, c'est tout
ce que j'avais, donc cela définit juste  la scène
vous donne une compréhension de haut niveau de ce que fait
un proxy inverse, alors
passons rapidement à une démo, donc je vais
vous montrer comment cela fonctionne réellement en action,



#  Configure NGINX as a Reverse Proxy Demo

ce que j'ai ici sur mon ordinateur local est
une machine virtuelle et dans ce  les
écrans de machine virtuelle qui ont le
pire mot de passe le plus sécurisé et
j'ai une machine virtuelle en cours d'exécution, donc j'ai
installé nginx dessus, nous allons donc faire moteur x
v et vous verrez que j'ai installé nginx r24
dessus
, sautons  ici
et jetez un œil à la configuration, donc
si nous faisons cat nginx.conf
c'est une configuration standard de stock, c'est
ce que je n'ai euh
rien d'extraordinaire ici
si je cd dans le répertoire de configuration qui
m'excuse,
c'est là que mes
fichiers de configuration font un  ls dessus
vous voyez que j'ai un default.conf
qui
agit essentiellement comme un proxy inverse dans mon cas mon
application back-end fonctionne toujours
sur le même hôte dans votre cas cette
application serait peut-être
quelque part dans le back-end  ou il pourrait s'agir d'
une adresse IP différente
dans mon scénario, cette application
s'exécute sur l'hôte local
par le catweb.conf c'est l'
application réelle que nous essayons d'exécuter,
donc dans ce scénario, comme vous pouvez le voir,
nginx agit comme un serveur Web qui publie



#  NGINX acting as a web server

l'application et
agit également  en tant que proxy inverse pour
ce cas,
aussi simple que cela, je peux sortir et faire
curl
localhost, vous pouvez voir qu'il enveloppe
cette demande à l'application un
à l'arrière, donc si je fais curl
localhost 9001 c'est l'
application réelle c'est
d'une certaine manière, l'application back-end par laquelle
nginx est acheminée,
donc nginx agit comme un proxy inverse
écoutant le port 80
et chaque fois que cette demande y parvient,
le proxy transmet cette demande
à l'arrière-plan du serveur
en amont dans notre cas qui est  le port 9001.
donc dans un scénario comme celui-ci, si j'essaie toujours
d'accéder à cette boîte depuis mon
ordinateur local,
sautons
ici et ce que j'ai, c'est ouvrir une
fenêtre de terminal
et donc ce que je fais, c'est accéder à ma vm à
partir de  ma  machine locale,
je vais juste passer un appel et l'
adresse IP de cette machine virtuelle est
192.168.153.187
et appuyez sur Entrée, vous obtiendrez la
réponse que c'est ce
qu'elle fait réellement, voyons si je peux
réellement accéder au
réel  application sur le port 9001 aussi,
j'espère que je devrais pouvoir y accéder, mais
si je ne peux rien
m'inquiéter, mais testons-le
et oui, les ports s'ouvrent dans mon cas, donc si
vous faites cela et que vous appuyez sur 9001,
vous pouvez toujours accéder  l'
application backend dans vos
environnements de production, cela devrait être arrêté
car
seul l'hôte local du
proxy inverse ou l'
adresse IP du proxy inverse serait
autorisé à accéder à l'
application backend mais un test simple
cependant le point que j'essaie de faire
voici pour essayer
de vous montrer quelles informations sont capturées
dans les journaux,
alors allons-y et jetons un coup d'œil
aux journaux,
donc si vous accédez aux journaux ici, vous
pouvez voir que ces journaux
ne vous donnent pas vraiment beaucoup d'
informations s  o vous pouvez voir que la commande passée
est en fait une demande curl en fait
chaque demande est une demande d'appel alors
allons simplement faire
une demande basée sur le navigateur
et appuyez sur rafraîchir plusieurs fois
désolé j'accède juste à un navigateur ici dans
en fait, permettez-moi de le faire ici aussi,
exemple.com, cliquez sur rafraîchir plusieurs
fois et
regardons le journal de chat en ce moment et
voyons
ce que nous allons faire, nous avons capturé des
informations, mais vous pouvez voir que
ce ne sont pas des informations pertinentes que nous
pouvez utiliser
et vous voulez essayer de capturer le
demandeur réel
l'uri qui a été demandé et vous
voulez le transmettre au
serveur d'application back-end donc pour cela
sortons et éditons notre fichier de configuration
pour essayer de capturer ces détails spécifiques en
utilisant euh en utilisant  la variable
utilisant le répertoire dont nous avons parlé
plus tôt, alors sautons simplement dans le
type de mots de passe le plus sécurisé
et ce que j'ai, c'est que j'ai configuré
quelques
fichiers ici qui viennent de sortir ici,
appuyez sur Entrée
essentiellement juste pour  assurez-vous que mes gros
doigts ne volent pas la vedette et que je
tape correctement,
j'ai ce pré-préparé, alors laissez-le
là, donc essentiellement
ce que nous faisons est de
définir l'en-tête de l'ensemble de proxy et de saisir l'hôte et
nous remplaçons la valeur par
une variable afin que la liste complète des
variables nginx soit disponible sur nginx.org
où vous pouvez capturer ces valeurs à partir de
euh
en définissant une variable elle-même et j'ai
été un peu effronté et je viens d'ajouter
un  exemple d'en-tête donc quand nous sortons pour
accéder au navigateur, nous voulons juste essayer
de voir que nous avons injecté un en-
tête de réponse
que nous devrions être en mesure de voir parfait
je vais juste enregistrer
ceci ici
fermer ceci et aller
accès au moteur sudo
donc nous avons rechargé la configuration,
tout fonctionne bien
et si je devais essayer de faire une boucle sur
localhost
et maintenant c'est le port 9000 et je
vais essayer de faire
un v pour essayer d'obtenir plus d'informations
, appuyez sur Entrée et hé là  nous allons donc
le petit en-tête effronté que
j'ai inséré en-tête de test a m  ade it true
dans
l'en-tête de réponse, donc
cela montre essentiellement que
toutes les informations que nous avons
fournies sortent et capturent cela,
mais
pour essayer de le tester, essayons simplement d'
écrire un fichier journal personnalisé afin que nous puissions
réellement
voir le  des valeurs d'en-tête de jeu de proxy uh spécifiques
que nous avons
définies, nous devons donc créer un nouveau
format de journal pour essayer de capturer les valeurs spécifiques
que nous avons
insérées.  la vie est un
peu plus facile
et ce que je vais faire
une fois de plus, c'est pour me sauver de l'
embarras,
je vais juste copier et coller le texte avant
ici
et aussi ici ce dont nous avons besoin est le
journal d'accès
donc essentiellement pour ce serveur spécifique
nous sommes  écrire cela dans un
fichier journal séparé et c'est également une
très bonne pratique, donc si vous avez
quelques serveurs différents en cours d'exécution,
vous voulez essayer de créer des
fichiers d'accès séparés pour
capturer des verrous pour chaque serveur séparé,
donc e  essentiellement, c'est juste très bien
si quelque chose devait mal tourner si vous
vouliez essayer de creuser des données
très très facilement si vous écrivez un
fichier séparé
et ici je viens d'écrire un
format de journal personnalisé je l'ai appelé
personnalisé  log et c'est ce que
j'utilise ici
et je viens de sortir et de taper quelques
demandes que je capture
, gardons ça euh aussi je partagerai le
lien
vers tous ces détails dans mon dépôt github
que vous pouvez regarder à partir de  les
liens ci-dessous sont parfaits
maintenant que nous avons rechargé, allons-y
et faisons cd
ng-max et voyons quel fichier et nous avons
les fichiers journaux d'accès personnalisés, mettons simplement à l'
échelle ce
fichier et
voyons ce que nous obtenons alors maintenant que nous  'ai fait
cela
à ce stade, j'y accède simplement à partir de
la boîte elle-même, vous verrez donc que les
adresses IP et l'adresse IP de l'hôte se
ressembleraient toutes,
car tout fonctionne à partir de mon
ordinateur local,
alors sortons et appuyez sur Entrée  ici,
appuyez sur rafraîchir et
c'est parti, tous les détails sont capturés ou  t ici
comme vous pouvez voir qu'il s'agit d'un navigateur firefox
donc le client utilisateur a capturé tous les
détails du client utilisateur
le nom d'hôte du proxy euh il est acheminé donc
cette demande est acheminée vers
ce backend spécifique l'adresse IP du proxy
est ce que nous '  j'ai demandé que l'adresse IP du client
soit exactement la même parce que
j'essaie d'y accéder à
partir de la même boîte elle-même afin que vous puissiez
voir
qu'elle a capturé toutes les informations pour
nous et euh
elle est remplie ici donc
en bref c'est tout ce que je voulais  pour
vous montrer en termes de configuration de moteur
nginx en tant que proxy inverse euh
définir des valeurs d'en-tête de proxy pour vous assurer que
vous capturez toutes les valeurs
et les transmettez au
serveur d'application principal réel et vous pouvez sortir
et apporter des modifications de configuration
dans vos fichiers journaux pour essayer  et capturez
des informations pertinentes les
gars parfaits alors merci d'avoir regardé cette
vidéo je vous verrai très bientôt les gars
merci beaucoup au revoir