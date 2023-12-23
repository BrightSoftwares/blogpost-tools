---
ToReview: true
author: full
categories:
- wordpress
date: 2023-05-16
description: How To Install WordPress with LEMP on Ubuntu 16.04
image: https://sergio.afanou.com/assets/images/image-midres-25.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-05-16
pretified: true
ref: howtoinstallwordpress_with_lemp_ubuntu
tags:
- lemp
- wordpress
- ubuntu
- linux
title: Comment installer WordPress avec LEMP sur Ubuntu 16.04
transcribed: true
youtube_video: http://www.youtube.com/watch?v=AOvh2jPEHCo
youtube_video_description: Install Wordpress on a Digital Ocean LAMP droplet.
youtube_video_id: AOvh2jPEHCo
youtube_video_title: Wordpress Install Ubuntu 16.04/LAMP
---

# 

salut, je vais faire une démonstration ici d'une
installation wordpress sur Ubuntu 1604, ce
sera une gouttelette sur laquelle le
logiciel de la lampe est installé, donc je commence
avec cette gouttelette ici celle-ci 59 89
140 204 et je vais juste travailler à
travers le  des instructions à ce sujet maintenant les
instructions que j'utilise sont sur
digitalocean c'est la façon d'installer
WordPress avec lampe sur une aubaine à 1604
et si vous regardez ces instructions
il y a quelques prérequis et les deux
prérequis que je vais utiliser sont
je  Je vais créer un utilisateur sudo sur mon
serveur afin que cet utilisateur soit le
propriétaire de WordPress, puis je
vais également créer, vous savez, j'ai déjà, comme
je l'ai dit, installé la pile de lampes,
j'ai donc le  Linux Apache mon
logiciel de pile PHP suite déjà sur cette gouttelette Je
ne vais PAS faire le site sécurisé
avec SSL qui pourrait être laissé pour un
autre projet mais pour cette vidéo je
ferai juste ces deux donc avant d'entrer
dans le premier  étape sur cet ensemble d'
instructions que je ne  ed pour créer ce
pseudo-utilisateur et je vais le faire en
utilisant cette page ici donc si vous regardez
le guide de configuration abouttwo 1604 de
digitalocean
il parle de la connexion root et c'est
ce que nous avons généralement utilisé pour nous connecter à
notre serveur donc  allons-y et voyons comment
cela fonctionne, donc si je vais à la racine SSH
à ok et que c'est la première fois que
j'entre dans cette gouttelette, je reçois juste
la question sur l'hôte connu ok
et quand je me connecte juste un  rappel pour
cette version sur l'océan numérique je suis sur l'
emplacement de l'application lampe et ça va me rappeler
que je servirai du bar
dub-dub-dub HTML quand je tape
cette URL dans mon navigateur l'installation PHP que
je peux tester  que c'est
correctement installé avec cela, je
peux utiliser les ports 22 80 et 443, puis
je peux trouver mes mots de passe digitalocean dans
cette route / dossier caché
mot de passe digitalocean afin que j'en ai besoin pour
mon installation alors disons simplement
voir ce que nous avons dans ce dossier nous avons
notre dans ce fi  le nous avons le point racine
digitalocean et vous pouvez voir que ce
fichier contient la racine mon
mot de passe de suite donc je vais avoir besoin de ce
mot de passe quand je vais installer WordPress
mais pour l'instant je suis connecté au droplet
et ce qui m'intéresse  en train de
configurer mon nouvel utilisateur et vous pouvez lire
à ce sujet et voir que vous savez que l'exécution d'
applications hors route est déconseillée
pour des raisons de sécurité, vous pouvez utiliser route
dans cette situation et l'exécuter si
vous n'êtes pas préoccupé par la sécurité la
raison  pourquoi je vous encourage à le faire,
c'est parce que si vous
suivez les instructions de l'
installation de WordPress, cela fera référence à Sammi
l'utilisateur qu'ils ont créé sur ces
instructions et cela pourrait faciliter le
suivi des instructions d'installation de wordpress
donc et c'est  bonne
pratique donc nous allons créer un nouvel
utilisateur et je vais juste utiliser leur
utilisateur ce Sammi ça pourrait être n'importe qui
Becky Jo n'importe quel nom que vous voulez mais
si vous créez un nom vous allez
vouloir vous souvenir  r ce nom d'utilisateur, donc tout
d'abord, je viens de taper ajouter l'utilisateur Sammi d'
accord et la première chose qu'il fait est de
me demander un mot de passe
quoi que j'entre ici, je dois me rappeler
de garder cela simple pour moi en ce moment
je vais juste faire le  mot de passe le
même Sammy et ensuite il me demandera de le
retaper et je le ferai
et je dirai simplement que Sammy fait le
digitalocean je ne sais même pas que ce sont
juste arbitraires tu sais je ne sais même
pas s'ils  sont en fait nécessaires, mais
je vais juste mettre quelque chose là
-dedans et les informations sont correctes, donc
j'ai créé un nouvel utilisateur
nommé Sammy maintenant, je suis toujours connecté en tant que
root, donc vous savez que je suis toujours root mais je
maintenant  avoir cet utilisateur Sammy, il dit oui,
vous pouvez simplement appuyer sur Entrée sur n'importe quel champ que vous
voulez ignorer afin que vous n'ayez rien à saisir
là-bas, la prochaine chose que
je veux faire est de donner à Sammy les privilèges root,
donc l'idée est que  Je
veux un utilisateur qui n'est pas root parce
qu'il a des qualités spécifiques qui
peuvent nuire à mon système de sécurité mais  Je veux
que cet utilisateur puisse avoir des
privilèges root et que cet utilisateur puisse
utiliser la commande sudo pour exécuter ces
privilèges afin qu'il doive préfacer la
commande qu'il fait avec sudo
afin d'obtenir les privilèges et pour ce
faire, nous  vont ajouter l'utilisateur au
pseudo-groupe, c'est donc ce que fait cette
commande ici, donc je vais juste taper cela et
maintenant cet utilisateur est capable d'exécuter des pseudo-
commandes qui sont essentiellement
des commandes d'administrateur dont il aura
besoin pour faire beaucoup  de l'installation,
vous savez que l'installation du logiciel est d'accord et
maintenant, parce que nous le voulons, nous voulons
que cet utilisateur puisse se connecter
en SSH à cet utilisateur, nous devons créer les
clés pour lui, donc nous allons exécuter
ssh-keygen bien  donc nous
travaillons toujours sur
cette configuration utilisateur, nous sommes à l'étape 4 ajouter
l'authentification par clé publique maintenant nous le
faisons afin que nous puissions nous connecter depuis notre
machine locale à Sammy vous savez que nous l'avons
déjà configuré pour que nous  peut se connecter
de la machine locale à la racine maintenant nous wa  nt
de faire la même chose pour Sammy et ces
instructions vous disent d'abord qu'il s'agit
de générer une clé sur votre
machine locale vous avez déjà fait cela
ne le refaites pas vous n'en avez pas besoin vous
ne voulez pas définitivement  ne voulez pas
remplacer cette clé, alors ne faites pas l'
étape pour générer une nouvelle clé sur le
réseau de votre machine locale, ce que vous voulez vraiment faire,
c'est copier cette clé cette clé de pub qui se trouve sur
votre machine locale dans Sammy maintenant  ils
vous donnent deux options et cela dépend
de la façon dont vous avez créé la gouttelette, je vais juste
vous dire de ne pas faire l'option un
qui ne fonctionnera pas pour vous, mais plutôt d'
aller à l'option deux et c'est quelque chose
que vous serez familier  avec l'installation manuelle de
la clé et c'est essentiellement
ce que nous allons faire est d'aller sur
notre machine locale et d'obtenir une copie dans le
tampon, puis de l'ajouter au
fichier de clés autorisées de Sammy, regardons
comment cela fonctionne donc tout d'abord  nous
allons vous demander - Sammy et ce que cela
signifie c'est une commande su super nous  euh
qui nous permet d'aller à alors je suis là je suis
connecté à mon je suis connecté en tant que root
je suis ici sur ma gouttelette et je vais
su - Sammy d'accord donc je suis là maintenant je suis qui
suis-je je suis Sammy je suis connecté en tant que Sammy
j'ai je suis assis à la racine de Sammy et
il n'y a pas de dossier SSH mais je
vais m'en créer un pour y mettre des
fichiers de clés autorisés afin qu'ils
vous donnent le  instructions ici pour créer
ce dossier SSH donc il appelle le make
der mount ici make duress SSH maintenant
disons hé j'ai ce dossier SSH et
ensuite la prochaine étape est que je vais avoir
des autorisations sur ce dossier et cela
me permet juste  pour y écrire, puis
étape, je vais créer un
fichier de clés autorisées afin que Nana
m'aide à créer ce fichier, puis je
vais revenir en arrière J'ai une
fenêtre de commande séparée ouverte ici c'est mon
lecteur local Ici  Je suis sur mon Mac et je
vais mettre la main dessus à partir de ce
SSH,
il a obtenu la clé de pub, donc vous vous souvenez probablement
que cette clé de pub, alors contentons-nous de cat qui
idrs un pub  et copiez-le depuis le SSH
RSA jusqu'à la fin de mon e-mail,
copiez-le dans le tampon, venez à
Nano, collez-le, d'accord, vous ne l'avez pas vu
coller là, essayons à nouveau.
J'ai utilisé le contrôle C, le contrôle C et  puis
contrôle V d'accord bon voilà c'est
super gros
tu sais grosse touche longue colle là
ça a l'air bien maintenant je vais juste
sortir de Nano et enregistrer ce fichier donc
je vais faire mon contrôle humide contrôle X
il va me demander si je veux le
sauvegarder, je vais dire oui, il va l'
écrire dans le fichier de clé autorisé oui
et maintenant si je le cat, alors c'est à
nouveau c'est à nouveau le
fichier de clés autorisé Sammis et j'ai
je viens de coller ma clé locale là-dedans, ce
qui signifie que je vais pouvoir me connecter
localement à Sammy mais là, je pense
qu'il y a une autre étape ici, nous voulons
changer le mode, cela change simplement les
autorisations sur cette clé autorisée, vous la
strixez un  un peu en arrière, je suis dans mon
mode de changement de connexion Sammy, puis je peux quitter maintenant quand
je quitte où suis-je  Je suis de retour en tant que root donc
je me suis déconnecté de Sammy et cela
me ramène à la racine d'où j'ai commencé d'
accord maintenant les instructions vont
vous dire stop v pour désactiver l'authentification par mot de passe
et je vais juste dire
ne '  t faire l'étape 5 Je ne veux
rien introduire qui pourrait entraver le
dépannage futur alors allez-y
et sautez l'étape
5 maintenant vous avez fini de créer
ce Sammy et nous devrions pouvoir SSH
et maintenant je suis connecté I'  Je suis de retour sur mon Mac,
je suis de retour sur une machine locale, vous savez, et
mon utilisateur mon Mac, mais je devrais pouvoir
me connecter en tant que Sammy, donc je devrais pouvoir me connecter
directement en SSH à Sammy et c'est
pratique, mais cela viendra  utile
pour qu'ils aient un utilisateur de bonne foi sur mon
droplet nommé Sammy en
plus de cela, je pense que j'ai sauté une
étape non, nous avons tout là-bas,
donc nous avons notre Sammy lui et Sammy est
capable de le pseudo  groupe donc pseudo groupe
donc il peut aussi où il peut
exécuter des commandes d'administration, alors
jetons un coup d'œil  maintenant nous sommes prêts à commencer à
installer WordPress d'accord, alors revenez
à cet onglet où oui, c'est là que j'ai
commencé où j'ai réalisé tout ce que je
veux créer un pseudo-utilisateur Je veux une lampe mais
je saute est la sécurisation avec SSL mais alors
ils  'Je vais à la première étape et la
première étape est ma suite et je veux être
connecté en tant que root alors revenons en arrière et
assurez-vous que maintenant si je dis Qui
suis-je Je suis Sammy Je ne veux pas ça  donc je
vais sortir de Sammy et revenir à la
racine donc nous n'allons pas utiliser
Sammy pour l'installer nous allons voir
comment il utilise Sammy
pour le posséder mais nous n'allons pas  utilisez
Sammy pour l'installer afin que nous soyons
connectés en tant que root et maintenant nous voulons nous
connecter à ma suite maintenant ma suite est une
base de données et donc elle nécessite un nom d'utilisateur et un
mot de passe nous avons parlé de la façon dont le
mot de passe a été rendu disponible la
première fois  connectez-vous à votre droplet donc je pense que je
devrais avoir cette commande ici
quelque part
voyons beaucoup de choses différentes
ici mais prenons juste un l  regarde l'
histoire je vais juste regarder et voir
si je peux trouver cette commande je vais utiliser grep
et voir si je peux trouver quelque chose qui s'appelle je
pense qu'il avait /root il avait ce numérique
dedans pas d'accord donc je ne peux pas  trouver cette
commande donc là c'est juste là
mot de passe digitalocean d'accord donc c'est
là que se trouve le mot de passe pour ma suite et
je veux que je vais le plafonner juste
ici avant afin que je puisse le copier dans le
tampon et l'utiliser de manière numérique  numérique voir
oh je suis toujours sur mon Mac Je suis désolé c'est
pourquoi je ne vois rien reconnectons-nous
à root donc je veux dire root ouais
parce que je me reconnecte à root chaque
fois que vous vous connectez à root vous obtenez ce
ce rappel  donc si
j'appelle ce mot de passe racine digitalocean, c'est
donc surlignez-le et copiez-le
dans le tampon parce que ce que nous
allons faire maintenant, c'est que nous allons taper ma
suite - vous et c'est ce qui sonne pour les
utilisateurs donc je  Je vais signer sur son itinéraire - P
alors voyons ce qui se passe là-bas, je
suppose - tu es root - piece et ça
dit quoi  c'est votre mot de passe et je vais juste le
coller ici
et j'espère que cela me signera oui donc je
contrôle V que ce que j'avais dans le tampon
et maintenant je suis connecté à ma suite que
vous pouvez dire parce qu'elle a ceci  mon
invite de suite ok maintenant ce que je
vais faire dans ma suite est de créer une
base de données wordpress et de créer un utilisateur
qui possédera cette base de données ou qui
appartiendra à cette base de données et et je
vais juste utiliser copier et coller pour faire
ceci donc je vais copier cette
base de données de création donc le nom de la base de données est
WordPress qui pourrait être ce que vous
voulez mais je vais utiliser WordPress parce
qu'il est facile de se souvenir que c'est ce qu'il y a dans le
Doc donc je vais juste coller  cela
là-dedans et appuyez sur Entrée et l'accord
me dit que la requête a été
exécutée sans problème, donc je peux supposer que j'ai une
base de données WordPress, puis la prochaine
chose que je vais faire est de
créer un utilisateur  donc moi et je vais aussi
leur donner des autorisations pour que vous puissiez voir que je
fais ce genre de choses  t tout en une seule étape
ici je dis accorder tout ce qui signifie
toutes les autorisations en faisant le maximum que vous
connaissez un utilisateur très puissant sur WordPress
star ce qui signifie toutes les tables tous les
objets de la base de données WordPress à un
nom d'utilisateur utilisateur WordPress qui est qui  est un
utilisateur sur localhost, ce qui signifie que cette
machine est identifiée par un mot de passe, ce qui
signifie que c'est pourquoi ce mot de passe est donc si
j'allais me connecter avec cet utilisateur
, le nom d'utilisateur serait un
utilisateur wordpress et son mot de passe serait un mot de passe,
donc je fais  beaucoup avec cette seule commande,
je vais juste la copier dans le
tampon et ensuite je vais juste appuyer sur Entrée
donc maintenant j'ai un maintenant j'ai un
utilisateur wordpress et ensuite je vais utiliser ces
privilèges de vidage qui sont  juste une
commande my sequel pour que ma suite soit au
courant de tous ces changements et c'est
tout ce que j'ai à faire là-bas, puis je
vais juste quitter pour que j'ai créé un
nom de base de données my sequel vous savez que j'ai
mon  suite comme résultat en téléchargeant la
pile de lampes que vous savez que j'ai créée  d une base de données
j'ai créé un utilisateur qui a l'autorisation
dans la base de données le nom de l'utilisateur est l'
utilisateur WordPress et le mot de passe est le mot de
passe d'accord
alors continuons et commençons à installer un
logiciel la première chose que nous allons faire est
sudo apt-get mise à jour maintenant  cela pourrait finir
par être vraiment ces installations pourraient
prendre un certain temps, donc je suis une sorte de couper
ceux de cette vidéo, mais allons-y,
donc la mise à jour qui sort
et obtient tout le dernier code Ubuntu
c'est assez courant que oui  même si
vous ne venez pas de le télécharger, il se peut
qu'il y ait des mises à jour, de nombreuses
mises à jour se produisent dans ce monde et puis
vous savez ici, je vais obtenir
des extensions spécifiques pour PHP, donc je ne fais que les
copier dans le tampon  et l'
exécuter et il me dit que cela va
prendre environ 3 Mo peut-être alors regardons simplement
les instructions d'instructions car
nous attendons que cela s'installe donc
une fois que nous aurons installé tout cela, nous
ferons un redémarrage sur Apache  pour que
tout soit disponible  le et ensuite nous allons
faire une configuration alors comment ça se passe
ouais ça prend l'air tout est bien fait
donc la prochaine étape est de redémarrer
Apache donc je suis juste en train de parcourir ces
instructions et ensuite la prochaine étape est
le htaccess  et c'est là que nous
allons obtenir WordPress et l'un de ses
plugins la possibilité de faire de la réécriture de mod la réécriture de
mod fait des choses comme la redirection vous
vous envoyez deux différents vous envoie deux
itinéraires différents dans le type de
navigation donc nous allons entrer dans
ce fichier de composition et
nous allons ajouter ce petit morceau, alors
amenons ce fichier de composition avec Nano
et donc ce que nous voulons faire est de saisir ce
morceau et il dit vers le bas
du fichier ajoutez le bloc suivant alors
allons  revenons ici, faisons défiler vers le bas
et voyons combien de temps dure ce fichier. Je parie que
vous savez comment aller jusqu'en
bas sans avoir à faire défiler comme
ça.
+ ctrl + / oh c'est une fois un
numéro de ligne disons  disons que cela ne nous mène pas
vraiment très loin c'est là que vous êtes toute la
pratique que vous avez de travailler avec ces
éditeurs va vraiment porter ses fruits
mais c'est certainement je peux voir qu'il y a
beaucoup de ces commandes de répertoire mais nous
voulons juste  pour suivre les instructions et
descendre vers le bas du fichier
, puis nous pouvons coller notre autorisation de
remplacement, puis nous ferons le contrôle X
et oui, nous voulons enregistrer les modifications
car Apache comm d'accord, donc si
j'aime un  queue sur ça je devrais voir mes
changements accrocheurs ouais donc il y a mon changement
en bas du fichier cette
commande queue montre juste ce qu'il y a au bas
d'un fichier et ensuite nous allons faire nous
allons activer ce mode lecture écriture qui
nous venons de le faire, ne vous inquiétez pas si vous ne
comprenez pas tout ce que ces
commandes vous disent de faire, c'est agréable
de regarder la description de celle
-ci, puis cela me dit que je dois redémarrer
Apache et nous avons vu ceci  avant et
installer les applications dynamiques et statiques
, puis w  Nous voulons activer les changements
que nous venons de faire, c'est tout pour
configurer l'environnement afin que WordPress
puisse faire son travail et il dit que vous
pourriez voir cela et
ne pourriez pas déterminer de manière fiable l'
appel de qualité si je nommais la syntaxe d'accord  alors oui j'ai
vu ça et ils disent que ça va ouais
vous pouvez le supprimer en faisant ça mais ne vous
inquiétez pas je pense que ça va et ensuite
nous allons faire un autre redémarrage ici maintenant
nous sommes prêts à télécharger WordPress et
la façon dont ils ont  vous faites ceci est que je
vous ai téléchargé dans un
répertoire temporaire et ensuite nous le copierons dans
son c'est le répertoire où il
vivra plus tard mais nous allons donc juste sur CD
temp et puis nous allons utiliser
cette boucle  commande et je ne sais pas si l'
un d'entre vous s'entraîne avec cela, mais cette
commande curl sort et
récupère simplement un fichier sur Internet euh donc CD
slash temp alors assurez-vous que vous êtes dans cette
température est-il quelque chose là ouais voir
peut-être  l'une des autres installations l'
utilise aussi et donc maintenant je vais juste t  o
collez cette commande curl pour qu'elle soit
envoyée au site WordPress en saisissant
ce fichier tar zip fatigué, donc c'est comme
ce fichier compressé compressé et il
va juste le faire tomber alors maintenant
j'ai ce dernier tar gzip et puis
je  Je vais exécuter la commande tar
qui va à la commande de guitare avec l'
ex EVF décompressera ce fichier et le
décompressera donc nous allons simplement le coller
là-dedans et Wow tout un tas de choses
maintenant donc si je regarde ici je peux  voyez
que j'ai maintenant un dossier wordpress si je
LS wordpress vous verrez qu'il y a tout un
tas de choses donc c'est essentiellement l'
installation de wordpress et ensuite nous
allons déplacer cela vers la racine du document
qui est notre barre dub-dub  -dub HTML
mais nous allons d'abord ajouter ce
fichier htaccess factice et définir les autorisations afin
que tout soit prêt plus tard, d'
accord, nous allons donc utiliser la commande touch the
touch crée simplement un fichier
et il va  créez-le sous le camp
WordPress afin que nous obtenions ce htaccess donc
comme si w  nous devions faire LS L un wordpress
nous devrions voir oui il y a notre accès HT
et je viens de le créer alors nous allons
définir des autorisations là-dessus que le
mode de changement va faire cela lui donner
une autorisation spécifique et ensuite nous
allons  copiez l'exemple de fichier de configuration
pour déposer un nom que WordPress lit afin
qu'ils vous fournissent l'exemple de
fichier de configuration que nous avons déjà vu auparavant où
il y a un fichier de configuration et que vous ne
voulez pas vraiment modifier le
fichier d'exemple réel que vous connaissez donc  nous allons le copier
sur celui-ci et nous allons simplement faire
tout cela dans la zone de tamponnement pour le préparer
pour sa destination finale, puis
nous exécuterons cette mise à niveau, alors configurez ce
répertoire de mise à niveau.
étapes et ensuite je
vais maintenant sudo CPI je vais copier
tout ce qui est sous WordPress dans
ma barre HTML dub-dub-dub et avant que je fasse
ça vous les gars si vous avez fait le VAR LS
disons seulement pour wwhd ml vous le ferez
voir probablement les répertoires pour les
Watts que vous avez installés, vous savez
pages dynamiques et statiques si vous utilisez
le même droplet, je ne vois pas cela
parce que j'ai créé un nouveau droplet pour
cela, mais vous pouvez l'installer directement
dedans, il va se retrouver à la racine de
ce fichier, donc en gros, courons  cette
commande sudo ici, elle va copier
oops attrapons cette
commande sudo sudo sudo Je l'ai entendu appeler les
deux donc ça nous donne juste quatre routes
donc nous n'en avons pas vraiment besoin mais ça
nous permet juste de faire des commandes d'administration donc
faisons cette grosse copie alors quelle
copie de notre HTML et maintenant quand nous faisons
notre LS pour HTML vous pouvez voir que tous
ces fichiers que nous avons téléchargés pour
WordPress sont maintenant à l'endroit où
Apache s'attend à trouver des fichiers qu'il peut
servir ok alors maintenant  c'est la cinquième étape de la
configuration du répertoire WordPress,
nous allons donc configurer et c'est là que
notre Sammie ou quel que soit l'utilisateur que nous avons
créé entre en jeu, nous allons
faire un changement de propriété pour que
Sammie soit propriétaire de ce que vous '  re
va posséder des données dub dub dub et laisser '  s il suffit de
jeter un coup d'œil si nous regardons cela, vous pouvez
voir dub dub dub data est un groupe en ce
moment si vous regardez la façon dont ces
formats de commande LSL a ce qu'il vous montre,
c'est qu'il vous montre l'utilisateur et le groupe
qui possèdent quoi que ce soit  fichiers ou dossiers vous
voyez leurs fichiers ou répertoires en ce moment
tout cela n'est pas un groupe et nous
allons changer cela alors
lançons ce sudo Chun
je vais juste vérifier voir définir
que nous voulons faire pseudo Chung d'accord maintenant
Je pense que lorsque nous faisons cela maintenant, nous voyons que tous
ces fichiers appartiennent à Sammy, l'utilisateur
qui les possède et les données dub dub dub sont
le groupe et la chose importante à propos des
données dub dub dub est qu'elles ont besoin de
cette propriété pour pouvoir
servir ces fichiers
afin que cela fasse partie de l'obtention de ceci afin que
vous sachiez comme index.html qui a été
créé s'il était déjà là,
il appartenait à dub dub dub data et
donc il pourrait être servi mais nous
devions nous assurer que tout le reste  d'entre
eux étaient aussi donc c'est ce que cette étape
fait un  Et puis c'est une étape qui
va définir un peu qui va aider
à maintenir cette propriété et
c'est une sorte de commande difficile à
lire, elle va entrer et
trouver tous ces fichiers et définir cela
va en ajouter  une autorisation qui
rendra cela disponible et ensuite nous
allons vers ce mode de changement avant
mémoire nous verrions 667 cent c'est
une autre façon et c'est juste G plus W
disant je suis tu sais ajouter une autorisation d'écriture
à ce fichier de contenu  et c'est parce
que c'est là que lorsque nous écrivons des vlogs, nous avons besoin de
WordPress pour pouvoir réellement écrire
dans ce répertoire, donc tout cela
aide simplement à se préparer pour WordPress,
puis nous allons en ajouter d'autres, voici
quelques autorisations supplémentaires sur les thèmes et
nous allons ajouter quelques autorisations sur
les plugins et je vais probablement
vous montrer d'autres autorisations que j'ai
trouvées utiles mais suivons simplement
ces instructions
maintenant la prochaine chose que nous allons faire
est de configurer ce wordpre  ss fichier de configuration et
nous utilisons que nous allons chercher ce sel
et il génère juste une sorte de
clés aléatoires et nous allons les utiliser
et elles sont utilisées pour la randomisation
et nous les fournissons à WordPress pour
son propre usage mais  suivons-les simplement
dans les directions, donc nous allons
exécuter cette instruction curl et wow, nous voyons d'
accord, nous avons tout un tas de
trucs fous, ils sont tous
associés à différentes clés nommées et nous sommes
allons l'utiliser dans nano, nous allons entrer
dans nano et nous allons
les copier dans nano, donc
nous allons ouvrir ce
fichier de configuration WP et il va dire mettez votre clé
là  et je pense que nous pouvons simplement copier et
coller cela, donc je vais essayer cela,
nous sélectionnons simplement ce ctrl C, puis
nous allons le savoir dès la sortie de la
configuration HTML WP d'accord Nano, il s'appelle WP
big P donc vous  'ai eu de l'expérience dans la modification de
fichiers de configuration PHP, vous allez descendre
et trouver ce morceau d'accord, alors
disons simplement  voyez si je peux simplement
coller ça là-dedans, collez-le là-dedans et
maintenant je peux simplement me débarrasser de tous ces
fichiers et encore une fois, plus vous en savez,
moins vous aurez à faire ce que je
fais maintenant, c'est-à-dire juste  Je suis en fait un
utilisateur VI et je ne fais même pas ça tant que ça,
mais je ne connais pas la commande
pour couper ce texte, je peux voir un ctrl K
là-bas mais je vais juste laisser cela
fonctionner et vous pouvez voir pourquoi  apprendre à
être bon dans un éditeur de ligne de commande pourrait
vous faire gagner beaucoup de temps, mais de toute façon,
le fait est que nous voulons obtenir ces clés dans
ce fichier et nous suivons les
instructions sur cette page en utilisant Jana d'
accord, alors maintenant nous pouvons faire notre  control X et
oui nous les sauvons et oui nous les
écrivons et c'est juste que je
vérifie toujours mon travail ce
n'est probablement pas nécessaire mais voyons juste
barde là-bas
WP gros d'accord donc il y a beaucoup de choses
là-dedans, mais oui, c'est
donc en gros nous avons couru le sel, nous avons eu
cette utilisation, la récupération du sel a obtenu ces
clés, puis ju  st les a collés là-dedans,
donc nous avons cela et maintenant nous
devons apporter quelques modifications supplémentaires à ce
fichier de configuration WP et vous savez que c'est
là que vous devez faire attention, vous savez de
petites petites erreurs ici de petites fautes de frappe
peuvent causer  vous problèmes et il pourrait être
difficile de résoudre les problèmes, alors
jetons un coup d'œil à ceux que nous allons
revenir dans ce fichier de configuration WP et nous
allons configurer le nom de la base de données qui
est WordPress l'utilisateur qui est l'
utilisateur WordPress et  mot de passe qui est mot de passe,
puis nous allons ajouter un tout nouveau
déclin qui va donner cette méthode FS,
alors revenons dans nano
wp-config et nous trouverons ceux qui existent,
donc nous sommes nom de la base de données et quoi
nous allons entrer ici, c'est WordPress,
donc nous partons de là
tout comme nous avons configuré notre ma
suite, nous fournissons simplement ces
informations à l'utilisateur WordPress de WordPress
, puis le mot de passe, donc oui parce que le
programme WordPress le fera  utilisez ces valeurs
pour vous aider à savoir
ow il va l'utiliser pour se connecter
à la base de données et enregistrer les choses d'accord,
donc cela continue et mettons-le simplement notre
nouvelle définition écrivez là d'accord, alors
enregistrons simplement que oui c'est
bon et vous pouvez le plafonner à nouveau et juste
voir si  nous voyons que là-dedans, c'est ce
qu'il y a ici oui, ce sont les
utilisateurs de WordPress WordPress, donc cela a l'air bien,
vous êtes à l'étape 6 et nous sommes maintenant
prêts à réellement mettre en place notre WordPress
, espérons que cela fonctionne, alors nous sommes
va saisir cette URL et qu'est-ce que cela
dit, nous allons simplement utiliser HTTP oh
super d'accord, nous allons donc faire des choses
ici sur lesquelles vous voudrez peut-être prendre des
notes, mais oui, choisissons l'anglais
pour la langue et  le titre du site, nous
pourrions le changer plus tard, mais pour le moment, je
vais juste dire d'
abord WordPress, mais si vous avez des
blogs, vous pouvez le
faire aussi maintenant, ce nom d'utilisateur et
ce mot de passe, il existe des moyens de résoudre ce problème,
mais c'est  bon de s'en souvenir pour
voir comment il dit que vous en aurez besoin  o utilisez ce
mot de passe pour vous connecter, veuillez le stocker dans un
emplacement sécurisé, donc je vais simplement
faire en sorte qu'il s'agisse maintenant d'un utilisateur de wordpress
qui va se connecter à WordPress ou ne pas se
connecter à digitalocean, ils ne se
connectent pas à l'océan numérique ou  à
votre recherche de gouttelettes, c'est une personne
qui ira sur le Web, affichera cette
image de configuration de presse de mots et voudra
ajouter des choses que vous connaissez de l'
application WordPress, donc vous voulez vous en souvenir
, faisons donc ce que je vais faire  et
ce n'est pas une bonne sécurité mais je vais le
faire maintenant et je vais probablement
détruire cette gouttelette de toute façon donc je vais juste en
faire Becky mais je recommande de
faire quelque chose de plus fort et assurez-vous
de l'écrire parce que si vous  oublie
ça et tu veux revenir et tu
vas devoir te connecter assure-toi juste de l'
écrire et je vais dire jeune
ça va parce que je fais ça juste
pour m'entraîner donc je vais utiliser ce
mot de passe faible  Je vais mettre mon mot de passe
ou mon e-mail ici d'accord un  d c'est
à vous de décider si vous essayez de faire
quelque chose de plus privé, vous voudrez peut-être le
décourager d'
accord, alors Becky Becky et c'est en fait
vous savez c'est c'est en quelque sorte c'est
un c'est un administrateur WordPress donc
il y a quelqu'un  qui peut configurer
WordPress à partir du Web, c'est pourquoi il
a un mot de passe, mais allons-
y et installons WordPress et nous nous
connecterons et
je vais me souvenir de moi juste au cas où la
connexion n'a pas besoin de l'enregistrer  alors
maintenant, ce que vous voyez ici, regardez l'
URL que vous avez votre adresse IP de droplet
et vous avez WP admin donc WP
admin est l'endroit où vous faites du
travail administratif dans WordPress et je vous encourage
à commencer à explorer cela parce que vous  vous
voudrez peut-être utiliser WordPress pour votre
projet final, mais il s'agit essentiellement de l'
installation de WordPress, donc pour revenir
aux instructions, nous avons
ici des captures d'écran de ce que nous venons de faire et
vous pouvez regarder cela, puis nous voulons
rendre notre WordPress capable  être mis à jour afin que
nous '  re allons exécuter quelques commandes supplémentaires
dans notre droplet, nous allons changer la
propriété de tout de manière récursive pour
dub dub dub data et c'est pour qu'il soit
utilisable donc nous sommes de retour ici en quelque sorte
montré et cela et ensuite nous allons
verrouiller le  autorisations pour la sécurité,
alors donnez-le à Sammi
[Music] d'
accord, puis il y a un peu d'
informations là-bas, donc cela
devrait vous aider à démarrer, il peut y avoir des
problèmes en cours de route, vous savez,
contactez-nous si vous en rencontrez et et si  vous
commencez à explorer et avez des questions,
s'il vous plaît, jetez-les sur le mou afin que nous puissions
tous en entendre parler, puis bien sûr pour
votre mission, vous saurez également que
je gère cela à partir de mon
adresse IP, vous voudrez y aller  créez un sous-
domaine pour votre nom de domaine que vous
connaissez comme un sous-domaine wordpress afin que
je tape simplement dans WordPress
point cette clé Pelt en ligne afin d'
accéder à ceci et c'est une
tâche complète, mais cela et cela vous permet de
passer à travers  installer  ling WordPress bien