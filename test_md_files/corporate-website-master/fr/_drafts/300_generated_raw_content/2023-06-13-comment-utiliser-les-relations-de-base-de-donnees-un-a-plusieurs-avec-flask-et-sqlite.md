---
ToReview: true
author: full
categories:
- database
date: 2023-06-13
description: Flask is a framework for building web applications using the Python language,
  and SQLite is a database engine that can be used with Python to store application
  data. In this tutorial, you will use Flask with SQLite to create a to-do application
  where users can create lists of to-do items. You will learn how to use SQLite with
  Flask and how one-to-many database relationships work.
image: https://sergio.afanou.com/assets/images/image-midres-48.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-13
pretified: true
ref: flask_sqlite_1239
tags: []
title: Comment utiliser les relations de base de données un à plusieurs avec Flask
  et SQLite
transcribed: true
youtube_video: http://www.youtube.com/watch?v=K0zF1GiPrxY
youtube_video_description: Séance en Python sur l'utilisation d'une base de données,
  pour vos programmes ou vos sites web.
youtube_video_id: K0zF1GiPrxY
youtube_video_title: 'Python #32 - base de données'
---

# 

[Musique]
bonjour à tous bienvenue sur la
formation au langage python on continue
avec une nouvelle séance toujours sur la
partie web et réseaux
la séance numéro 32 où je vous parle et
comme le dit l indique le titre de base
de données pour cela je vous proposer
une solution parmi beaucoup d'autres ce
qu'il existe évidemment plusieurs
manières de travailler avec des
partenaires vous explique également ce
que c'est tout ce que je pars du
principe encore une fois que vous n'avez
jamais vu d'autres langages avant
d'autres technologies que c'est la
première fois que vous découvrez sa non
je vous faire un petit peu le tour de le
torcher le mans de cet humain de ce type
de fonctionnement qui à connaître en
informatique
il faut savoir qu'à la base tout ce qui
était informations et vous l'avez vu
d'ailleurs dans les vidéos précédentes
ont stocké la plupart du temps quand on
voulait sauvegarder pour une autre
exécution du programme notamment dans un
fichier texte
vous avez d'ailleurs vu la séance sur
les fichiers nous avons pouvions stocker
des informations à l'intérieur on peut
même également sauvegarder sous forme
binaire d'accord sauvegarde est
carrément des objets et ça peut avoir
son utilité
en revanche là où ça va montrer ses
limitations c'est dans le cas où nous
allons vouloir par exemple effectuer des
recherches faire des requêtes pour
sélectionner par exemple certaines
informations parmi ce que nous avons
sauvegardé la le fichier texte n'est
évidemment pas du tout du tout prévu
pour ça et même si on s'arrangeait pour
le permettre ce serait pas optimisé
accord on aurait vraiment beaucoup de
pertes de performances puisque le
fichier texte n'est pas fait pour ça il
est fait pour être lus il est fait pour
pouvoir écrire dedans est terminée
l'accord n'est pas fait pour commencer à
faire de la recherche de la sélection du
requêtage du groupement de données selon
certains certains critères spécifiques
bref tout ce genre de petites choses
pour cela nous avons instauré donc on
appelle les bases de données en
informatique qui permettra de stocker
les informations de manière relationnel
on va pouvoir créer des relations entre
les informations stockées
on pourra par exemple avoir des
informations stockées sous forme de
table donc on appelle ça des tables dans
les bases de données dont des tables sql
puisque sql c'est le langage qui est
utilisé en base de données et je vais
revenir un petit peu dessus eos états
peuvent être va stocker tout un tas
d'informations vous pourrez par exemple
avoir une pour un site web une table qui
stocke les utilisateurs une table qui va
stocker vos ligneuse de votre site
une table qui va stocker par exemple le
les rangs pour les utilisateurs
administrateurs modérateur etc et vous
pouvez comme ça crée des relations dire
par exemple un utilisateur il a un rôle
par exemple modérateur et voyez vous
pouvez créer comme ça des relations
entre différentes tables et stocker
toutes ces informations et pouvoir faire
des recherches dessus via son appel des
requêtes sql
alors il existe sur moteur de gestion de
bases de données qu'on appelle les sgbd
notamment tous ces systèmes ont leurs
avantages et leurs inconvénients
moi mon but c'est évidemment de vous
proposer une solution qui n existe
plusieurs et de vous expliquer un petit
peu un petit peu l'ensemble des autres
commandes on lit et on entend beaucoup
de choses concernant les systèmes de
gestion de bases de données par exemple
certains qui vous diront que mysql c'est
mieux d'autres vous diront que poserait
non c'est mieux que mysql ou qui vous
diront ban en fait il ya mieux il ya
sqlite etc et on va avoir beaucoup comme
ça de deux supports qui vont vous
toujours mettre en avant la plus que
l'autre alors qu'au final n'y en a pas
un qui est mieux kloet et n'a pas un qui
est moins bien que l'autre encore une
fois et ça fonctionne pour tous vous
avez chaque système
chaque technologie chaque langage qui
est bon dans un domaine qui fonctionne
bien ce pour répondre à certains besoins
qui fonctionne bien selon un cas
spécifique une situation spécifique mais
qu'il ne fonctionnera pas du tout et pas
d'une manière optimale
dans un autre cas dans une situation
donc moi ce que je vous propose est ici
au maximum c'est de travailler comme on
fait souvent avec les choses que propose
python en natif
mon intérêt c'est toujours vous à
prendre un engagement une technologie
avec ce qu'elle propose de manière
native avant même que vous vous ayez
après la l'autonomie est là dès
l'indépendance pour pouvoir découvrir
des choses externe extérieur parce que
vous savez de python propose plein de
modules plein de bibliothèques externe
donc la première des choses à faire
c'est d'apprendre déjà ce que propose
python en standard en natif tout seul et
après de voir plus loin
pour cela je vous proposais du coup dans
cette vidéo de travailler avec sqlite
quel est l'intérêt de sql par rapport
aux autres
est-ce qu il ait en fait il vise à
remplacer l'utilisation de fichiers
textes et j'insiste bien là dessus il ne
sert vraiment qu'à ça l'intérêt c'est
banal plus avoir de fichiers texte mais
de travailler avec des bases de données
à la place qu'ils sont beaucoup plus
légers et qui vont permettre de faire
tout un tas de recherche et notamment
deux requêtes sql
alors moment j'enregistre cette vidéo je
n'ai pas encore fait la formation sql
mais sachez qu'il y en aura une pour
ceux qui se posent la question ce que
j'ai pas mal de gens mal demain il y
aura une formation à part juste sur le
langage sql vous apprendrai vraiment
tout le détail sur le langage à faire
des requêtes à connaître un petit peu
les différentes fonctions et c'est donc
on va faire un peu de sql dans d'autres
formations mais de manière très standard
très simple donc vous n'êtes pas obligés
de
la partie est ce que l on va dire je
vais vous la donner par contre si vous
voulez vraiment apprendre le langage
gestuel pour le réutiliser en php leur
utilisant python utilisé en java ou je
ne sais quoi dans n'importe quel langage
vous pouvez faire des requêtes sql et
bien n'hésitez pas quand la formation
sera bien avant de publier parce qu'elle
ne l'est pas au moment où georges et
cette vidéo a conçu par mail à consulter
le court sql sur la chaîne est comme ça
vous aurez tout le détail à ce niveau
alors grosso modo si on veut faire
simple ce que je vais pas rentrer d
itunes que oui j'ai même pas encore
commencé à programmer vous montrer quoi
que ce soit dont je veux pas trop
traîner non plus dans les explications
on a trois cas de figure et ça vous
pouvez retenir ce que c'est les trois
cas de figure qui fonctionne plutôt bien
d'accord dans là on va dire dans la
réalité ça fonctionne à 99% comme ça est
ce qu il a été fait encore une fois je
vous dis pour remplacer l'utilisation de
fichiers texte et pas autre chose
il a été conçu par exemple pour
fonctionner depuis les téléphones ça et
vos smartphones tout ça vous utilisez
des applications et ses applications
plutôt que de devoir se connecter à
distance ou à des bases de données à
avoir des choses un peu lourde parce que
ça peut être aussi compliqué les
téléphones noah n'avait pas non plus
énormément d'espacé de stockage à
l'époque n'est pas forcément beaucoup de
mémoire vive même si ça change sa
tendance à changer
donc on avait besoin de proposer un
système beaucoup plus légers parce que
les systèmes comme mysql voir au rac fin
bref des systèmes de base on est très
très lourd c'était absolument impensable
d'avoir ça sur un appareil mobile
donc on a inventé ce qu il ait pour
proposer en fait un fichier donc vous
aurez un fichier qui va représenter
votre base de données nous avons
travaillé avec ça du coup est ce que là
ils ne doivent fonctionner que pour ça
cercas qu light n'est pas utilisé ça je
lis ça fonctionne pour n'importe quel
qu'une formation n'importe quel cours
n'importe quel cas vous ne devez pas
qu'ils sqlite si vous voulez gérer
énormément de quantités de données alors
c'est un c'est une fourchette un petit
peut évidemment être revu à la hausse à
la baisse
mais moi je pars du principe qu'un parti
au moment où votre vos votes bâtonnets
ou vos bases de données arrivent à une
quantité de données qui atteint le
gigaoctet vous pouvez considérer que
sqlite n'est pas une bonne solution
le problème c'est qu'en ce moment on
démarre un projet on va pas savoir à
l'avancé combien peuvent atteindre les
données donc ça vous de l'estimé par
rapport à votre projet votre site web
votre jeu vidéo je ne sais quoi de vous
dire est ce qu'un jour je vais pas
atteindre le gigaoctet de données parce
que ça peut mine de rien il évite une
base de données qui fait un gigaoctet
c'est pas énorme
il ya plein de base de données sur des
gros projets qui dépassent largement
cette taille là
donc si vous pensez qu'un jour c'est
votre base va s'étendra au-delà du 1 du
gigaoctet éviter à ce culte c'est pas
forcément intéressant après tout dit
dans certains cas ça s'peut il ya
sûrement des projets mobiles sur
téléphone qui dépasse au giga octets qui
utilisaient ce culte mais m'a même temps
ils n'ont pas trop trop choix ça
fonctionne sur mobile c'est la solution
qui reste quand même la plus viable mais
dans l'idéal éviter si vous le pouvez
après quand on commence à voir voilà des
données assez en grosse quantité ou ça
peut aller loin et notamment quand on a
besoin de la multiples connexions cercle
problème des skull ait par exemple c'est
que vous n'allez pas pouvoir connecter
tout un tas d'utilisateurs en même temps
puisque ben ils vont devoir chacun
attendant fait d'avoir la main sur la
base de données et en plus il ya trop
trop d'utilisateurs qui se servent en
même temps de la base donnée en faisant
des requêtes
il risque d'avoir des conflits ainsi
d'avoir des problèmes puisque même si un
système de verrou pour empêcher que 2 et
à tort en même temps puisse toucher à la
même information
il est possible dans certains cas et
bassa se désynchroniser du coup ça a
créé des problèmes
donc si vous prévoyez que votre base de
données puissent être consultées par
plusieurs utilisateurs mais je parle
vraiment de quantités assez importantes
pareil à ce qu'il aille n'est pas
forcément la bonne solution d'accord on
cas dans ce genre de cas car ce qu'on va
utiliser dans matinée une solution comme
mysql mysql est la solution la plus
répandue pourquoi parce qu'elle
correspond à 80 mdsy quant à elle
correspond pratiquement à tous les
projets qui utilisent des bases de
données dans le monde pratiquement tous
or certains ont bien même il ya des
histoires comme bon oracle etc
sa cdc des solutions propriétaires donc
c'est un peu l'équivalent de mysql
d'accord c'est sur des solutions très
lourde mais on dire il ya aussi
postgressql dont on entend parler
souvent on a beaucoup de gens qui vous
disent postgressql c'est encore mieux
que mysql et ces gens ont tort tout
simplement puisque postgressql a été
conçu pour manipuler des bases donné
beaucoup beaucoup beaucoup plus grosse
que ce que l'on peut manipuler avec
mysql postgres sql et je vous dis c'est
mon concept n'en fasse que vous voulez
il est intéressant utilisé à partir -
vous travaillez sur des bases au nez de
plusieurs téraoctets de données
voilà donc déjà avant d'atteindre le
téraoctet de données
il faudra en voir par exemple un chu
tout un service médical oui ils vont
atteindre sans problème les lettres
plusieurs téraoctets de données en la
gérer tous les dossiers de patients
allaient faire basculer rob a créé des
relations entre les différents
départements régions et c'est là oui on
est vraiment dans le téraoctet de
données donc oui pour eux utiliser des
bases de données en postgressql pas de
problème ce sera largement optimisé ils
ont choisi le meilleur système de zone
et qui a pour ça
après les solutions propriétaires encore
une fois comme on raque windows server
mais je parle pas de ses souhaits sur la
sas à des solutions propriétaires
pas forcément gratuite pour la plupart
donc je les mets de côté c'est
évidemment des solutions viables pour
des gros gros gros projet également moi
je parle des solutions en tout cas
gratuite donc retenait ça si vous
travaillez sur quelque chose de léger
qui nécessite pas d'avoir trop de trop
de données donc voilà que ça dépasse
vraiment le giga par exemple de données
et qui a pas besoin de connexions
multiples vous pouvez utiliser à
sculpter c'est ce que je vais vous
montrer en cette vidéo donc on va
pouvoir y arriver enfin si vous avez
besoin de gérer un projet de plusieurs
voilà qu assez conséquent faca soit
besoin d'avoir plusieurs connexions
simultanées par exemple un forum l'accès
par exemple à des news genre de choses
ça peut inciter voire un accès par
plusieurs personnes et que ça peut du
coup éventuellement peut-être atteindre
des fois plusieurs gigas de données
mysql et mon sens la meilleure solution
et si par contre vous avez besoin de
manipuler des données qui peuvent
atteindre le téraoctet voire plus la
pause grèce qu elle est la meilleure
solution parce qu'il a été conçu avec
des fonctionnalités supplémentaires pour
gérer justement des quantités de données
comme ça très astronomique la oumma sql
lui se montrerait du coup limites
par contre utiliser postgressql sql
pardon sur une base de données qui fait
que quelques mégaoctets vous allez
complètement complètement les
performances de votre base de données
mais ça vous pourrez le vérifier pas
dans vos projets vous verrez la
différence tester du malaise créé du
post grèce créent sur des petits projets
et vous verrez que mysql dans la
majorité des cas pour pas dire tous il
est beaucoup plus performant par contre
postgressql sur des très très gros
projet c'est lui qui se montre le plus
performant donc on en revient ce que je
vous disais il n'y a pas un meilleur
système de gestion de base de données
c'est juste que chacun correspond à des
besoins d'accord s'il y en avait un
parfait il n'en existerait qu'un seul
personnes se seraient amusés
croyez le à s'embêter à créer un nouveau
système si les solutions déjà existantes
étaient parfaites
ça paraît logique par contre chaque
système a des besoins utilisé pour moi
du post crise qu elle sur une base de
données qui fait 100 mégas c'est
complètement ridicule
utiliser du mysql sur une base de
données qui fait aux cinq terrasses
c'est ridicule aussi utiliser du sql est
par exemple pour gérer 1 1 et amel
imaginons par exemple un service de
messagerie instantanée donc où il ya
plein de gens qui écrivent en même temps
pour envoyer des messages utilisés du
sql pour faire ça c'est pas forcément de
meilleurs moyens non plus sauf si bien
sûr n'est sur mobiles ou autres et qu'on
n'a pas forcément le choix encore une
fois voilà désolé d'avoir été un peu
long a pas fait grand-chose sabido j'ai
pas mal parlé il s'est pas passé
chose à l'écran mais peu importe vous
savez comment ça fonctionne vous savez
aussi que voilà je vais toujours vous
l'expliquer les choses mon but ce n'est
pas de vous balancer du code du code et
plein de choses comme ça de la
documentation je ne sais quoi
sans vous l'expliquer au moins au niveau
des bases données vous savez ce que
c'est vous savez comment ça fonctionne
et vous savez ce qu'il en est si un jour
quelqu'un vous balance soit postgressql
c'est mieux que mysql bas vous aurez les
arguments pour pouvoir justement lui
expliquer les choses comme il faut en
tout cas il me semble par rapport à la
réalité encore une fois est parce qu on
peut lire des fois sur certains forums
ou même des fois où certains vivent ce
que ça peut se trouver partout
voilà donc là on va travailler sur
sqlite parce que manipuler des données
légère ya pas beaucoup de données et en
plus ce python l'avantagent comme c'est
un langage portable est utilisable par
tous est bien moins sûr à ce qu il ait
l'avantagé c'est que vous n'avez rien à
installer pas besoin d'installer le
moteur de base au nez puisqu'il est
présent par défaut le mans très pratique
alors pareil moment je fais cette vidéo
je n'ai pas fait de tuto sur d'autres
systèmes bases sonné mais je prévois de
toute façon par exemple un tutoriel pour
faire du mysql ac python c'est prévu
d'accord donc allé voir sur la playlist
python tutoriel peut-être qu'au moment
où vous irez voir bas le tutorat été
publiés entre ton film en pot de chambre
demande en commentaire ça a été fait aux
caisses je vous répondrai bien
évidemment donc on est parti cette fois
ci donc encore une fois désolé d'avoir
pas mal pris du temps de vous faire sa
petite intro mais ça me semblait
absolument nécessaire pour la suite
que vous ayez des bonnes habitudes il
est pareil pas que vous tombiez dans les
pièges des fois que certaines personnes
peuvent tomber dans lesquelles certaines
personnes peuvent tomber nos calculettes
pour cela nous allons installer
déjà fin je vous propose est installé à
un petit logiciel qui est peu plus multi
plateforme open source donc l' avantage
c'est que c'est le même peu importe le
système d'exploitation qui vont
permettre de visualiser le contenu d'une
base de données parce que vous aurez
plus tard un fichier les fichiers pourra
pas être lu comme ça comme un fichier
texte donc c'est bien avoir un petit
logiciel qui est capable de d'aller voir
à l'intérieur pour voir par exemple vos
données ont bien été enregistré ou
éventuellement plus tard si vous voulez
créer vos tables vous savez l'étape dont
je vous ai parlé faire une table
d'utilisateurs une table d'objets une
table de 6 une table de sa de pas mal de
choses donc vous pouvez récupérer sur le
site escalettes brothers point org
ce logiciel vous voyez qu'il est
disponible pour tous pour windows on
peut la voir en version portable pour
windows version mac on peut le
télécharger pour linux et à 100 sûr si
vous êtes sur ubuntu une version cheap
debian pouvez même aller voir dans la
doc par exemple d'ogone tout pareil pour
linux mint un seul ado comme nous tous
ils devront proposer à priori même de
quoi l'installer
de commandes rapidement depuis les
dépôts parce que je pense que l'aide
dans les dépôts ce logiciel a priori on
pouvait toujours les voir il en existe
d'autres
d'accord de logiciels pour ça mais moi
je vous conseille je suis là parce que
c'est vraiment celui qui est
multiplateforme gratuit open source donc
plus pratique à gérer pour tous voilà
pour donc db du coup un browser for sql
donc c'est ce logiciel donc moi je les
videmment récupérer pour windows
convainc art besoin et on va pouvoir
comme ça travailler un petit peu avec
alors on est sur un fichier normal hein
j'ai refait voyez affiché mind point pi
comme d'habitude j'ai récupéré donc la
version portable ce que je voulais pas
installer de sql database barroso
d'accord pour ça on va pouvoir comme ça
travailler avec cette partie là alors
est ce qu il ait encore une fois on va
pouvoir faire des requêtes sql pas de
problème mais au lieu que ce soit stocké
dans pas mal d'autres choses qu'on a
installé tout un moteur il va nous avons
va avoir un fichier qui représentera la
base de données et on pourra du coup
interrogé dessus faire des requêtes
ajouter des shows supprimer modifié
créer des tables etc etc on fera pas mal
de petites choses comme ça donc nous
pour la création notamment à pas faire
d'enquêté secrète parce que encore une
fois je pars du principe que c'est votre
première formation je n'ai pas en plus
ce moment où je fais cette vidéo fait la
formation sql donc a priori vous ne
connaissez pas ce qu elle enfin je parle
de principes en tout cas vous ne le
connaissez pas donc je vais pas
commencer à faire des requêtes sql de
création de tape ça va être un peu
compliqué même si ce n'est pas non plus
un inaccessible en soi mais on va créer
du coup la table directement ou via le
logiciel donc une fois qu'il est
installé et télécharge etc vous pouvez
lancer et vous allez obtenir ce genre
d'interface tout simplement
donc là on va pouvoir se créer du coup
une nouvelle base de données
alors lui il aimait la tiens c'est
rigolo
ah oui le manant data d'accord
maintenant on va le mettre dans pitt
obama titien et je vais l'appeler du
coup une base et il va lui mettre une
extension là il peut y mettre des bsk et
des foyers mais le par m avec le numéro
de la version non comment on va
travailler avec sqlite 3 du coup il va
vous mettre à ce qu'ils aillent trop peu
3 ou des baies 3 on peut importe le le
type de d'extension on s'en fiche
ça peut y a pas vraiment d'extension à
thillois mêmes points un point data
point ce que vous voulez même d'ailleurs
pour un bd des points database vous
pouvez mettre absolument l'extension
vous voulez ça n'a aucune importance
c'est juste que par habitude on est
souvent l'une de ces voix là une de ces
deux là où éventuellement que le numéro
de version derrière donc je crée ça il
me propose donc éventuellement de créer
une table on ne voyait que les lois en
plus et vous affiche automatiquement la
requête sql correspondante
donc nous on va faire va faire une table
users d'accord je m même tes user soit
là pour changer un petit peu éviter de
mettre juste le nom comme ça donc je
pense qu'on fait cette petite astuce
quand par exemple vous gérez un site web
doit vous mettez le nom de votre site
web ou autre enfin vous mettez pas
pendant juste users d'accord mais tu es
un petit préfixe n'importe lequel
pour éviter que les gens par exemple
s'il ya des des pirates qui veulent
tenté de pirater votre ci puisse
éventuellement deviner les noms qui va y
avoir parce que si par exemple ils
veulent tenté de pirater votre base de
données
ils vont justement cherché une table
user ou une table comme ça parce que
c'est le nom utilisé le plus souvent par
les gens à tort donc essayer de mettre
par exemple petit préfixe que vous nous
donner à personne bien sûr ça peut être
n'importe quoi des chiffres au hasard
des lettres enfin ce que vous voulez
donc ça peut être par exemple voilà mon
prix fixe jeu c'est pas genre mon et
puis plus loin je mets user non plus
loin fin en deux corps aux news etc
pour éviter d'avoir un nom qui puisse
elle devine éventuellement par un peu un
les potentiels pirates qui voudrait
interroger justement votre base de
données pour récupérer par exemple des
informations d'authentification sur
votre site ou n'importe quoi donc nous
on va pas on va pas chercher un truc tu
accomplis quant à lui mais traité rende
leurs scores users
voilà donc sans la joute et là on va
créer un champ donc les champs passé
quoi passer dans la table on va pouvoir
choisir quel chant elle a par exemple -
user qu'est-ce que je quittais comme
information par défaut et je suis pas
encore une fois là pour faire un cours
de sql donc vous allez juste faire
écouter ce que je vous dis sans
forcément ou là à prendre ça parce que
vous n'êtes pas là pour apprendre et sql
on va faire un identifiant puisque c'est
bien d'avoir un identifiant surtout
surtout quand on veut faire des
sélections ou des tris donc on va faire
ça c'est moi c'est mon habitude ce que
je trouve ces mêmes noté comme ça c'est
toujours de noter pour l'identifiant
idée underscore le nom utilisé pour la
table
donc en haut d'hier au singulier donc
idéaux user on le met entre les
primaires et en notant incrémentation ce
qu'on veut que le l'identifiant soit
unique pour chaque chaque utilisateur et
en notant un crémant serre qui va se
vanter de 1 automatiquement voilà et on
va ajouter un autre champ ensuite
d'angevins je fais comme ça je prend le
nom de la table donc au singulier en
dort score je mets le nom du chant que
je donc par exemple si je veux le nom de
l'utilisateur de jamais user under score
game là c'est un texte donc hop on met
ça c'est tout apprendre à d'autres
champs pour choisir si les vases s'il
est obligatoire ou non mais sans s'en
fiche
ensuite qu'est ce que je peux mettre on
va pas sans un joueur de jeux vidéo 1 et
user level et level c'est un hit
voilà et du coup on peut faire ok c'est
tout
vous voyez qui m'a créé une table de
salle à faux pas l'enlever c'est la
table qui vous dit combien vous avez en
fait d'éléments il faut la laisser
et là on a du coup la table user avec
nos trois champs voilà on l'enregistré
jeta les modifications terminé on va
créer déjà un utilisateur donc on va
ajouter ce qu'on appelle une ligne en
fait on va ajouter d'accord un
enregistrement et une entrée à la base
de données qu'on pourra ensuite les
liens au niveau de notre code sera plus
pratique et après on verra pour en
ajouter un deuxième pour voir ça bien
fonctionné donc on va faire en fait un
une lecture de la base de données et
ensuite on a enregistré donc écrire dans
la base de kourou et que les deux
fonctionne bien donc on y va donc lors
je crois que ça fonctionne comme ça on
va faire parcourir les données va se
battre ça un nouvel enregistrement là je
pense que c'est ça un an par l'enjeu pas
la bonne base un dommage on va aller sur
tt user voilà nouvel enregistrement
voilà donc oui là ils venaient autres
par défaut l'idée 1
donc ça vous pour vous bat le faire
vous-même vous n'avez pas besoin de vous
même le spécifier identifiant jamais
c'est la base données qui va le faire
tout seul ici mais je vais lui mettre
l'info vous pouvez enregistrer là où ici
donc je met mon prénom
et puis au niveau du niveau où va mettre
par exemple niveau car sa méthode voilà
on fait ça enregistrer les modifications
et logiquement c'est bon normalement je
suis pas fait de bêtise ça devrait être
bon ok
donc là c'est bon on va fermer sa
logiquement maba zone est enregistré
alors je vais retourner sur le dossier
pitons voilà donc j'ai mon fichier mais
n'y voyez elle a regardé mais ils se
pointent des baies d'accord donc ça
c'est votre base de données d'accord
juste avec ce fichier là tout votre base
de données enregistrées l avantage c
grace et un fichier simplement texte
ainsi les seuils de l'ouvrir j'obtiens
ça d'accord le fichier temps binaire nom
qu'on peut pas le dire comme ça mais du
coup on va pouvoir mais interrogé
là-dessus faire des requêtes faire de la
recherche de la sélection de
l'enregistrement tout ça bref pas mal de
petites choses intéressantes
donc on y va on va travailler à ce
niveau-là et commencer par importer près
un mois du bac c'est parti on commence
du code
donc il fallait que vous ayez les
informations nécessaires maintenant on
peut parler de code
on va importer le module est ce qu il
ait 3 donc encore une fois un module
natif en pet ont pas besoin de
l'installer il est déjà présent vous
mettez juste cette ligne et vous l'avez
première chose à faire pour ne pas
donner il faut se connecter
là où avec un fichier on irait l'ouvrir
avec un mode une base donné on va se
connecter dessus donc en risque ul-haq
c'est très simple il suffit de se
connecter au fichier de base de données
donc soit le fichier existe déjà et il
va tout simplement être ouverts soit le
fixe le fichier sur lequel vous voulez
vous connecter n'existe pas il va du
coup être créés d'accord en fonction du
temps que vous mettez la variable de
l'appeler connexion puisque c'est une
connexion qu'on fait d'encaisser trouver
les c'est de prendre les noms pour vous
qui sont suffisamment explicites
en général mes connexions puisque ont
créé une connexion d'accord valeur
envahie qui on va avoir une instance
connexion de sql est donc on va
l'appeler connexion ne s'ajuste pas me
tromper
est-ce qu il ait trois points connaître
donc tour minuscule et là vous mettez le
nom de votre base donc c'est à dire le
nom ici d'accord avec l'extension donc
si vous avez pas vous tromper vous faire
comme ça un petit copier coller du total
comme ça vous êtes sûr de rien oublié ce
que s'ils n'ont là est différent si vous
mettez par exemple ça il va créer un
nouveau fichier une nouvelle base d'une
amy va pas ouvrir celle qui est déjà
existantes
voilà et comme toute base de données
comme pour un fichier si ça a été
connectée donc ouvert on doit fermer
donc on va faire automatiquement
connection point close mais à la fin une
fois qu'on est capable de soins donc on
va laisser ça comme ça
à partir de là nous allons pouvoir
récupérer les données pour lire les
données nous avons pas mal de petites
choses à faire nous allons avoir besoin
déjà de créer un curseur c'est à dire
qu'un curseur est tout simplement un
hors jeu par entre un détail mais c'est
un outil qui vous permettra de
travailler avec les requêtes a qu'une
fois qu'on aura le curseur il va pouvoir
effectuer une sélection donc la
sélection c'est de la recherche dans la
base de données on va pouvoir faire une
orgie streumon donc avec un insert on va
pouvoir faire une mise à jour avec un
update ou une suppression avec un deal
est et on a eu également d'autres types
de requêtes ça ce sont les principales
c'est ce qu'on appelle les fameuses
requête oncle et l'interface cloud pour
ceux qui connaissaient est rude et il
s'écrit comme ça vous avez peut-être
déjà vu on vous parle de cloud se veut
tout simplement dire que lui ait weeds
donc lire van dijk dit ça c'est le
minimum en juin quand on manipule des
bases au nez on doit faire ces quatre
choses là pouvoir créer la table et la
table enregistré la formation
puisqu'elle est déjà on parle du procès
qui a déjà créé donc on fait une certain
on enregistre une info on peut la lire
donc le select on peut la modifier
update on peut être supprimés avec diète
voilà donc saas et le cloud donc une
fois que ça c'est fait d'accord qu'on
est connecté et que normalement bon ça
fonctionnait mais tu as on verra après
comment gérer les erreurs ce que vous
doutez bien qu'en basse donné pour faire
bien les choses on doit gérer les
erreurs mais on le verra à la fin pour
faire ça de manière un peu plus propre
là on va rester sur des choses simples
pour le moment on va pouvoir créer notre
curseur en le curseur en général je lui
donne simplement le nom curseur pourquoi
parce que ben moi je suis sûr de ne pas
également me tromper dans l'eau donc on
va mettre ça au moins je sais à quoi ça
correspond et ça correspond à notre
connexion point curseur ça va créer un
objet d'accord une instance pardon de la
classe curseur qui appartient sqlite roi
donc là c'est une instance de comment
s'appelle de connexion est ce qu elle
ait trois points connexion et là c'est
une instance de cursan d'ailleurs ce
qu'on peut s'amuser à faire comme ça
print taipei 2 ça qu'on ne fait pas
souvent ça depuis
maintenant vous êtes des grands je fais
plus trop aux vérifications mais ça peut
être bien de vérifier éventuellement
voilà vous voyez le premier connection
csq les trois points connexion donc
c'est une instance de classe connexion
de cette classe qui appartient ce public
iii queen instanciés ici et là on a créé
une instance de curseur on va pouvoir
travailler du quoique ces deux objets là
tout le d'accord et on n'oublie pas
chaque fois de couper dans ce conte
ferme en fête c'est bien la connexion
d'accord donc c'est logique que je fasse
le close sur connexion n'est pas par
exemple sur curseur ou autre donc ça
c'est pour vous qu'on comprenait la
logique parce que c'est bien de vous
expliquer les choses ce que c'est bien
de balancer du code mais si on
n'explique pas un minimum
pourquoi pourquoi la logique derrière
pourquoi on ferme pour qu'on fait si
c'est un peu dommage donc au moins là
vous comprenez pourquoi on procède de
cette manière une fois que le curseur
est près d'accord on va pouvoir
travailler avec lui et avec lui avec ce
petit curseur à nous à pouvoir faire
toutes nos requêtes
nous avons plusieurs requêtes possibles
soit on va avoir par exemple une seule
requête serre qui va faire par exemple
qu'une seule information on va utiliser
la méthode execute et si on a besoin de
gérer plusieurs informations par exemple
quand on fait notamment une version une
insertion donc un insert on va utiliser
execute mini d'accord donc nous pour le
moment on va faire exécuter puisqu'on va
juste faire une sélection on va aller
lire dans la base de données les infos
que j'ai créé tout à l'heure via le
logiciel comme on l'avait vu donc
comment on va procéder à ça on va
procéder de cette manière on va faire
curseur point execute d'accord mais ça
c'est la méthode de base
ici vous allez mettre la requête à faire
donc encore une fois vous n'êtes pas là
pour trouver ce qu elle donc sachez que
la requête pour sectionner un élément
dans la base savais tu select étoiles
c'est pour dire je sélectionne tout
formant la base donc nous c'était été
users d'accord
where par exemple non je veux pas faire
ça en fait on s'en fiche
si on peut le faire si si le champ sur
lequel je veux faire éventuellement une
comment dire par exemple je veux choisir
une condition c'est à dire dans le cas
donc ou user n'est donc ça c'est le
champ de la base de n'est égale quelque
chose et nous on va faire des requêtes
sécurisé donc je vous montrais le moyen
de faire des requêtes sécurisé pour
éviter par exemple les injections sql ou
ce genre de choses parce que oui en
python il faut également sécuriser les
requêtes comme on le fait en php
vous mettez un point d'interrogation et
ici il faudra passer après la virgule
l'élément à 1 voit donc n'utilisez pas
par exemple de syntaxe comme ça qu'on
fait plus vraiment maintenant d'ailleurs
en python 3 ans je faisais beaucoup
avant et après on passe par exemple ici
notre variable avec l'usure ça c'est pas
du tout sécurisé là vous prenez beaucoup
beaucoup de risques vous mettez ceux ci
un petit joker et vous allez passer
l'info et l'info pas comment la passer
eh bien vous créer votre variable tout
simplement et c'est un tube d'accord
donc le tube même si a qu'une seule
valeur
vous mettez votre valeur tout seul
d'accord et vous mettez une virgule et
vous mettez rien sur le deuxième élément
c'est comme ça en ce moment qu'il
invente d'accord ça fait partie de la
manière dont ont été faits la gestion
pour les requêtes
donc je peux pas voilà vous à dire si
c'est bien ou pas bien c'est juste a été
décidé comme ça il faut faire un tube
les mêmes si vous n'avez qu'un seul
élément bas vous mettez le premier
élément du tube et une virgule vous
mettez rien après mais c'est tout et là
bas du corps est indéniable tout cas
passer ça est automatiquement il va
remplacer ici le point d'interrogation
le premier qui voit par le contenu de ma
news line donc part ça il qu'on va lui
dire quoi on va dire tu sélectionnes
toutes les infos depuis la base de
données tt user dans le cas où username
donc le championnat mais gala du coup de
jeune et ça tombe bien parce que c'est
ce que georges très voyez quand quand
j'ai créé l'utilisateur tout à l'heure
de paix le logiciel et l'a logiquement
on va avoir l'information il sait qu'il
va être enregistrées d'accord pour
l'affiché et bien on va utiliser comme
ici à qu'une seule information parce
qu'on a faim execute on à la méthode
fait choix dont justin print sur cure
sort l'apport point fait schwahn juste
comme ça
fait chier ça veut dire en fait de
récupérer vous voyez de liste ee en fait
sous forme d'une seule donnée encore one
d'où le fait s'appelle fait schwahn
quand tu auras plusieurs plusieurs
résultat possible ce que défend pas voir
une requête qui rend tout qui retourne
plusieurs résultats d'un coup on mettra
fait chaud le hockey mais ça on verra un
petit peu après donc nous on fait juste
fait ce choix et on va voir
l'information ici récupérer femmes ce
truc comme ça
voilà ce que nous avons donc là voyez
qui récupère les informations sous cette
forme
d'accord on voit qu'il ya l'idée il ya
eu 6 est le lieu et l'heure n'est il ya
le user level d'accord donc si je veux
par exemple que ça que l'information de
jouer ici et là ça fonctionne comme pour
un tableau d'accord ou comme pour une
liste ça c'est lundi 0 sa scène un 10-1
ça c'est l' indice de donc vous pouvez
très bien faire directement comme ceux
ci un pour avoir le nom d'utilisateur
donc vous mettez tout ça est entre
crochets lundi ce que vous voulez
récupérer et voilà et là vous avez
récupéré l'info si vous voulez faire ça
plus proprement voilà un utilisateur et
on met tout ça entre cros entre accolade
pardon pour avoir l'information
proprement et ça fonctionne
voilà comment vous pouvez faire alors si
vous préférez c'est même mieux qu'on
sait se classent souvent voyant mélange
beaucoup de choses et moi
personnellement je suis pas friand de ce
type de manière de faire je préfère
souvent que crée des variables
intermedia parce qu'on arrive mieux à
lire son code et surtout quand on veut
plus tard le maintenir ou le mettre à
jour c'est beaucoup plus simple c'est
mieux je trouve de d'enregistrer l'info
donc par exemple vous pouvez enregistrer
la requête gens vous faites ça d'accord
et après du coup vous pouvez récupérer
le résul le résultat donc mais bon ici
un nom un peu gêné rim et mettez un nom
plus explicite vous et du coup vous
pouvez faire rec points donc ce qu'on a
mis tous tout à l'heure ici en fait
ouais du coup c'est en fait non j'aime
pas besoin de faire je peux juste faire
ça comme j'utilise un curseur s'est pas
forcément inquiet du sort dans ce sens
une variable voilà c'est comme ça ici
au lieu de faire toute cette line armes
fait ça plus pratique c'est pas
obligatoire mais voilà ça fonctionne par
ineo - passe par une période
intermédiaire c'est beaucoup plus
lisible ici est beaucoup plus simple
parce qu'après du coup il y aura qu
aston droit de modifier
ce si jamais vous avez plusieurs fois
besoin d'afficher ça nous allait du coup
le répéter encore une fois comme vous
savez le dupliquer sur pas mal
d'endroits de votre code et le jour où
cette ligne a doit changer qu'au final
vous devez pas récupéré lundi saint méen
10,2 mais vous allez devoir modifier
autant de fois que vous l'avez mis alors
que la bièvre a juste cette ligne à
modifier et tous les we dolt encore une
fois seront modifiés par tous donc ça
ces révisions de variables de tout ce
qu'on a vu sur les variables depuis le
tout débute au début du coup donc
logiquement vous êtes largement à l'aise
avec tout ça je vous apprends rien du
tout voilà pour cette partie on peut
fonctionner comme ça d'accord ça
fonctionne via des indices
si on a plusieurs infos mme on le verra
après ce qu on va d'abord enregistrer un
nouvel un nouvel élément et après on
fera une lecture sur plusieurs choses
comment on va pouvoir procéder est bien
avec tout simplement eu plusieurs
plusieurs choses l'accord plusieurs jeux
donc là on a juste fait de la lecture on
n'a pas modifié comme vous savez la base
de données d'accord on a juste fait une
lecture terminée une fois qu'on a fini à
lecture offert la base de n'ai pas de
souci là on va enregistrer un élément
dans ce qu'on va faire c'est déjà passé
toutes les informations ici donc je vais
virer tout ça hop je vais créer le
nouvel utilisateur
donc nous nous user pardon vous pouvez
le passé sur plusieurs infos vous pouvez
en faire une liste d'accord on peut très
bien par exemple voire plus tard vouloir
ajouter plusieurs utilisateurs et on
peut très bien faire ça sert qu'on va
passer par exemple ici un première idée
vous sais pas quoi donc en mettre par
exemple pas moins de l'idée on va mettre
un nom encore bonjour mais un exemple
vite fait un level on ferme ici ensuite
on en est un autre
bah on aurait 2 donc en une fois les
idées c'est à nous de les remplir mais
je vous expliquerai comment faire après
laon mais voilà un autre et puis ensuite
on va mettre un autre niveau et puis
après on va mettre voyez un autre etc
et du coup on pourra les ajouter tous
ensemble comme ça vous savez comment ça
fonctionne c'est une liste à mme donc
encore une fois je reviens pas dessus
donc nous on va en avoir qu'un seul donc
voilà comment on va procéder alors pour
l'identifiant c'est pas vous de le noter
ce que j'avais dit ça à la base du nez
de le faire donc vous pouvez
automatiquement interroger la base pour
qu'automatiquement elle m l'identifiant
courant cirque là où elle a emmené au
niveau des enregistrements donc moi le
premier or justement qu'il a fait il a
mis l'idée est donc logiquement le
deuxième il devra mettre là l'idée de
lui quand je le pratique pour gérer des
tris pour faire voilà une
un ordre d'affichage ou un ordre de
récupération de données donc pour ça ce
qu'on va faire nous c'est tout
simplement utiliser le la propriété
l'astre hoa et dit d'accord sur les
éléments qu'on veut donc le mieux c'est
de faire du ressort du point
l'ast heidi hockey comme ceci pour
l'idée là on va lui passer l'information
d'accord on va lui passer un niveau et
nous avons tous d'enregistrer les trois
éléments et ensuite on fait la requête
curseur point execute et on passe la
requête
la requête mais nous n'en manquons comme
tout mais ça c'est juste de la révision
si vous voulez l'écrire sur plusieurs
lignes vous pouvez bien sûr utiliser la
syntaxe comme ça un accord peut très
bien faire simple par exemple select
avec lippi à la lime il siens d'accord
vous savez qu'en écrivant trois double
côte comme ça vous pouvez du coup mettre
les choses sur plusieurs lignes je leur
dis au cas où je fais des petits rappels
évidemment c'est rien de nouveau donc
nous on fait un insert donc ça c'est la
requête pour enregistrer un nouvel
élément
ça s'appelle insert into d'accord on met
en général au nom de la base de la table
pardon un cerf à l'intérieur de tt users
les valeurs suivantes
donc nous ça prend trois valeurs donc on
met trois points interrogations de 3
c'est tout tout simplement et petites
virgules
vous avez juste à placer votre variable
ici et là comme on a enregistré une
nouvelle chose dans la base il faut
comité c'est à dire qu'il faut valider
les changements de la base comme tout à
l'envoyer sur le logiciel j'ai cliqué
sur le bouton pour enregistrer aux
modifications bas là c'est pareil comme
on a ajouté des choses la base de
données a changé on n'a pas fait que
lire à l'intérieur ce qui avait déjà
donc on va comité tout simplement
l'enregistrement et le comité on va
évidemment le faire sur la connexion
puisque c'est la base concomitante c'est
pas le curseur donc on fait juste ceci
voilà c'est important de le faire pour
avoir l'information et là après vous
pouvez faire
nouvel utilisateur a ajouté qu il n'y a
pas de problème je veux dire qu on voit
beaucoup de chance cette vidéo à cette
vidéo sera un petit peu longue mais
voilà séquelles très important de
connaître les bases de données donc je
prends bien le temps de vous l'expliquer
j'ai pas envie de faire ça trop vite on
fait ça donc là il me met apparemment
nouvelle cette heure ajouté écouter y
accueille problème a priori après mon
n'a pas encore fait de gestion d' erreur
là mais vous en faites pas on va le
faire à la fin pour vous montrer la
bonne méthode pour gérer les bases de
données en python en tout cas non pas
aux frappes affaire comme ça on
l'augmentera la fin comme on fait ça
pour pas trop voir tout d'un coup est
bon maintenant qu'on a enregistré parce
qu'on peut faire déjà s'est vérifié au
niveau du logiciel
est-ce qu'il a bien ajouté tout cela il
nous l'a dit c'est bien mais est-ce que
c'est vrai on ne fait pas confiance
du coup on regarde ouvrir une base de
données
python base voilà un an déjà ici si on
va dans parcours est donné on voit qu'il
a mis que tu étais user il ya deux
lignes donc apparemment il ya des
enregistrements c'est plutôt bon signe
et si on va sur tt user on voit regarder
qu'il a bien ajouté un fou et voyez que
l'identifiant a bien été autant
incrémenté donc depuis il est passé à 2
alors des fois ça c'est la question que
les gens soient en se posant pas donné
il ya des gens de foi qui devrait mieux
admettons qu'un jour je supprime un
enregistrement du coup je vais avoir des
trous au niveau des antilles ans par
exemple ici je suis prêt mais celui-là
le prochain qui va être enregistrées
laura d'identifiants 3000 y aura plus de
d'enregistrement avec l'identifiant de
ça absolument pas grave d'accord cd
antichan ils servent juste pour la base
donné pour faire du tri et de la
recherche parce qu'elle va beaucoup plus
vite grâce à ça c'est pas fait pour vous
si vous voulez utiliser des identifiants
uniques en plus avec des valeurs voilà
qui se suivent de une jusqu'à chp à
combien il faudra créer un autre champ
spéciale en mettant par exemple autre
chose d'accord oui c'est lui le heidi
sert vraiment comme clé primaire et
autant incrémentation pour la base de
données parce qu'en faisant un select
étoiles elle va aller beaucoup plus vite
c'est la requête sera beaucoup plus
performante si vous travaillez sur un
select étoiles quand vous avez
d'identifiants sous forme de clé
primaire autant incrémenté c'est comme
ça qu'on fait les choses de manière plus
performantes en base de données
c'est tout c'est pas fait pour
l'utilisateur ou le développeur c'est
vraiment juste pour la base de données
pour la rendre plus performante et
faciliter les requêtes et les recherches
et tout ça voilà donc maintenant qu'on a
les infos on a vu que là physiquement
elle a effectivement bien été
enregistrée c'est vrai on va pouvoir les
récupérer donc ce qu'on va faire c'est
tout simplement
ici j'espère ça execute donc là la
requête la plus simple c'est select
étoiles donc sélectionne tout depuis la
base tu étais une others
on peut pas faire plus simple si on
prend tous les enregistrements de la la
table dti others ont fait pas de comité
à main sur ce qu'on a rien eu on n'a
rien modifié en fait je de la lecture
ok si je fais par exemple sommes donc là
ça peut être bien de faire une règle une
quête une requête par dans une quatrième
fois si je fais genre print dereck ces
histoires tout montre c'est bien d'avoir
des fois un petit faire des petits prix
comme ça pour voir un peu ce qu'on a
comme infos là vous voyez qu'on a bien
logés cure cure sorte d'accord y'a pas
de problème à ce niveau là donc ce qu'on
va faire comme on a plusieurs
enregistrements qui vont arriver ici on
fait chaud coll d'accord je ne fais pas
sur one on fait surtout et là on affiche
et vous voyez que toute l'information
ont bien été retournée sous forme de
liste d'accord on a bien une liste et
regarder comment que ça enregistré tout
ce que je vous ai montré de thaler là
vous pouvez faire une liste en mettant
les informations comme ça et du coup
avec un exécute mini vous pouvez faire
plusieurs insert d'un coup d'être obligé
de faire un insert pour enregistrer
qu'une seule personne vous pouvez
enregistrer 15 utilisateurs d'un coup si
vous voulez vous faites une liste avec
15 utilisateurs comme ça marquer sauf
qu'ici au lieu de mettre directement en
dur l'idée au fait comme tout à l'heure
vous mettez curseur point l'astro heidi
va commencer va automatiquement les
mettre en incrémenté et à la fin vous
avez juste à faire un execute min
d'accord ce cynique
vous écrivez comme tout à l'heure avec
valve use les points d'interrogation
exactement comme je lé fais un peu plus
tôt dans la vidéo et la femme avoue
passer au lieu de passer juste une
petite variable après la virgule dans la
ranquette vous passez à votre liste
et ça va ajouter tout du fait que vous
utiliser la méthode execute ming donc
c'est juste la différence pour ça je
vous la montre pas vraiment au complet
ce que je pense que la vidéo est assez
longue comme ça déjà
mais c'est exactement le même
utilisation si vous travaillez avec
execute vous passez une variable simple
si vous travaillez avec execute mini
vous pouvez passer carrément une liste
d'accords tout simplement
voilà l'information telle qu'elle est
donc après va le choix basse et de
l'enregistrer tout simplement enfin le
registre est par moment pas
l'enregistrer mais de la parcourir avec
une petite loupe d'accord on peut faire
ça si on veut
pour pouvoir lire l'information comment
le faire et bien nous on va faire juste
ça fort alors je mets tout beau pour
dire pour chaque ligne de rec
non pardon si on peut faire ça fait ch
roule alors même le maître ici vous
pouvez passer par une variable
intermédiaire du nom et du coup on peut
faire ça encore plan pour regarder ce
qu'on obtient voilà oui de cette fois ci
on a bien la formation qui est comme ça
et du coup bah là c'est facile on sait
comment faire maintenant pour récupérer
éléments on l'a fait tout à l'heure on
passe par lundi si je veux que le nom
d'utilisateur et voilà et vous avez le
nom d'utilisateur donc très pratique
dont vous pouvez comme ça par courrier
que tout ce que vous avez vu vous vous
rendez compte un petit peu tout ce que
vous avez vu les notions précédemment vu
dans le coup vous resservent tout le
temps d'accord tout ce que vous avez vu
sur les listes sur le parcours avec les
boucles etc tout est utile la boucle
fort est d'ailleurs très pratique pour
parcourir comme ça des collections
parcourir des éléments voilà enfin
plusieurs plusieurs données comme ça
d'un coup pour les faire l'une à la
suite des autres c'est plutôt bien
pensée est prévu en tout cas pour ça
donc n'hésitez pas à vous en servir de
cette manière et vous avez comme ça
toutes les informations alors si jamais
on veut revenir à l'eau dernier comic
précédent il ya la commande all back à
quoi on peut faire un connexion d'accord
point rollback c'est pour revenir au
dernier comic c'est par exemple il ya eu
un problème avec celui d'avant d'accord
pour revenir à l'avant dernier en fait
le précédent mais on va le voir parce
qu'on va mettre en place un petit
système de donc de gestion d'erreurs
donc de gestionnaire de bases de données
qui soient un peu plus optimisé un peu
plus propre ce qu'on a fait ici pour
terminer en tout cas cette vidéo
j'essaye déjà de voir si je n'ai rien
oublié par rapport à tout ce que je
voulais vous montrer à caen puisque ça
peut aller vite avec toutes les veilles
a tellement tellement d'informations à
savoir en base de données qu'il est
possible que je puisse avoir oublié
quelque chose donc je ferai le tour un
petit peu de tout ce qu'on a vu on a vu
la connexion le curseur je vous ai
montré comment lire des données
je vous ai montré comment écrire
intérieur le comité je vais montrer du
coup comment tout récupérer que ce
soient une seule un seul résultat ou
éventuellement plusieurs résultats
et puis après on a tout fait on a vu
comment récupérer bien sûr le dernier
identifiant parce qu'il faut surtout pas
le m ont dit on écrivait jamais un
identifiant durant dix ans bah voilà
il y des uns et des deux idées 3 c'est
pas vous de mettre ça à la base une et
de le faire tout seul
voilà donc on va gérer les erreurs du
coup donc les erreurs comment on va les
gérer et bien avec le fameux dry excepte
un com vous avez toujours appris à faire
donc ça devrait être tout le temps fait
comme ça d'accord gérer toujours aux
erreurs de cette manière et on va même
avoir un finally je rappelle que le
finally c'est quelque chose à faire dans
tous les cas cerqueux que les
instructions qu'on a demandé à faire et
fonctionner ou non tout ce qui se
passera dans le faille nos lits sera
fait quoi qu'il arrive crcd chose à
faire peu importe ce qui se passe au
niveau du code qui est des erreurs ou
pas faut le faire donc à ce que nous
allons faire dans le final je peux le
mettre tout de suite
eh bien nous allons fermer la base de
données ça c'est logique parce que la
base ici cette line à ce qu'elle va
faire c'est soit le fichier là existent
du coup c'est ouvert soit le fichier
n'existe pas donc elle va en créer un
nouveau
donc ça aura fonctionné donc il faut à
tout prix fermer la base donné quoi
qu'il arrive même si ici les requêtes
génère des erreurs ou des exceptions
quoi que ce soit il faut à tout prix
fermer la base donné donc il faut le
faire à cet endroit donc vous faites ça
dans le croyais pas vous mettez en fait
tout votre code en fait voilà clairement
vous mettez tout ça bon ici on n'aurait
pas grand chose que c'est que de la
lecture c'est souvent les erreurs qu'on
a c'est plus souvent quand même dans
l'écriture ou dans la mise à jour man et
on s'est quand même bien toi sont de
gérer ça comme ça voilà donc dans le
choix que vous faites tout ce que vous
avez à faire la connexion et cetera le
curseur vos petites requête vous était
d'accord et dans ce genre de cas vous
allez rencontrer des héros alors
pourquoi le accepte on peut permettre
qu'une petite exception particulier
puisqu'il y en a beaucoup
la premier souvenir on part abondé on
peut avoir des erreurs type intégrité
integrity error par rapport à
l'intégrité concernant avec les
primaires on peut avoir des erreurs sur
operational erreur par exemple quand on
fédérer des requêtes sur une table qui
n'existe pas à mes temps j'essaie de
faire ça bien là j'aurai des erreurs a
d'ailleurs on va le voir
alors on va convaincre exprès des
erreurs pour voir que notre système
fonctionne bien donc comme il ya
plusieurs types d'exception le mieux en
tout cas à mon sens en tout cas
saignante dedans que de rien faire du
tout un cm2 faire de gérer toutes les
exceptions plutôt que de rien j'irai du
tout vous faites excepte exception eux
comment connais bien et là vous gérez du
coup vos petites erreurs d'accord donc
moi en général quand je fais un truc
très simple je fais ça
un petit erreur ici
on va mettre le connection point roll
back
pourquoi parce que si jamais il ya une
erreur il faut revenir au dernier comité
d'accord il faut annuler la tentative où
la requête qu'on a fait ce calme est
temps que la requête alors j'ai des
choses à moitié bas vous allez avoir des
petits soucis d'envoi de base donc il
faut absolument annulé ce qu'il y avait
ce qu'on a tenté de faire si jamais il
ya eu des erreurs scotia des erreurs
c'est que ça n'a pas fonctionné comme ça
aurait dû donc on évite et la remettre
le indirectement large affiche veut en
fait erreur et puis j'affiche le message
tout de suite on pouvait faire un autre
chose si vous voulez mais ça c'est
vraiment la manière la plus simple et le
roll back
et voilà donc là on va retenter d'accord
du coup on voit j'ai pas changer grand
chose j'ai juste mis fin aux actes sera
excellent pour que soient propres donc
là ça fonctionne et un mets ton d'un
coup à la base en fait je mets un nom de
base qui n'existe pas d'accord
il va me retourne et je crois que c'est
opérationnel et roja qui retourne quand
ya pas de la base n'est pas trouvée il
me semble bref ça va être ça bon allez
il affiche pas parce qu'on a ça donc
nous voyez notre no such neustadt borloo
users et si j'avais pas gérer ça
maintenant je vais vitesse que sa part
est propre on va avoir des exceptions et
sera pas être profond qu'on va lui
éviter de le faire parce que là il a il
a capturé l'exception forcément donc
comme ça vous capturez tous les types
d'exception après je sais pas ce qu'il
peut y avoir d'autres éventuels m'en
trouve pas l'information en fait juste
voir par exemple user name égal alors on
va faire ça
user et puis on va créer ici une vraie
newser on va lui mettre un nom qui
n'existe pas le fameux toto est il de
retour
voilà donc si on cherche quelqu'un qui
n'existe pas là pas de problème arménien
pour que ça génère pas d'erreur parce
que ça génère pas d'ordre il ya juste
pas de résultats attendus donc le truc
c'est que à vous de vérifier
évidemment au niveau de votre quête si
l'information était retournée c'est
important dans le cas où vous n'avez
rien ou z'avez note par exemple il
faudra également gérer ça vous même
parce qu'ils considèrent ça veut pas ça
comme une barbie va pas lever
d'exception il n'y a pas de raison de
lever une exception si bas votre base on
n'y a pas de il n'a pas trouvé de
résultats parce que c'est pas faux comme
requête ça de dire voilà je cherchais un
utilisateur qui s'appelle tout haut ce
qui pourrait y en avoir un si on n'a pas
un bon rien n'a pas donc c'est à vous de
le notifier à l'utilisateur tout ça je
tenais à vous montrer ça parce que de
bien différencier une exception qui est
vraiment une erreur commise d'une 'bad
une retraite par exemple 4 simplement
pas trouvé de résultats le fait de pas
trouvé de résultats ce n'est pas une
erreur c'est juste qu'à pas de résultats
terminé voilà pour cette partie là je
pense qu'on va s'arrêter pour cette
grosse vidéo donc j'ai pas mal pas mal
fait mais j'ai fait une grosse
introduction en début de vidéo j'ai pas
mal parler pour vous présenter tout ce
qui concerne les bases une et je pense
que c'est nécessaire s'il ya des choses
qui sont entre autres est clair
évidemment vous pouvez poser des
questions demandées il n'y a pas de
souci je vous donnerai plus détails
encore si vous trouvez qu'un a pas eu
assé dans cette vidéo
dans tous les cas je pense que j'ai fait
un peu le tour de tout ce qu'il y avait
à savoir au niveau utilisation de la
skull êtes vous voyez que c'est très
simple à utiliser
si vous êtes intéressé bien sûr par le
sql comme le jeu rappelle je vais faire
en tout cas parce qu'elle n'est pas
faite au moment cette vidéo est
enregistrée une formation au langage sql
complète qui pourra vous servir dans
n'importe quelle autre formation pour
php pour python et c'est partout vous
ferez du web
donc voilà attendait cette formation là
comme ça vous pourrez vraiment apprendre
à faire des requêtes comme ça et
comprendre vraiment ces requêtes et
faire une des choses un peu plus
complexe donc on verra tout ça dans le
détail en attendant j'espère que ça vous
a plu gspc suffisamment complet on
continuera donc pour la prochaine séance
donc la 33 avec encore d'autres choses
quand on va commencer maintenant plus
rentrer ben lande je pense qu'on a fait
un peu le tour de tout ce qui était
vraiment web d'accord vraiment le web on
va plus partir sur du réseau on verra
bien un petit peu dans ce que je propose
pour la suite mais on n'a pas fini en
tout cas ce chapitre aulas concernant la
partie web réseaux dont il ya encore des
petites choses à vous présenter vous
montrer qu'ils sont très intéressantes
dans ce langage je vous dis à bientôt
pour la prochaine vidéo et n'hésitez pas
bien vous entraîner à faire du code
poser des questions si nécessaire et
bien sûr partager la vidéo chat où tout
le monde
[Musique]
[Applaudissements]
tous
[Musique]