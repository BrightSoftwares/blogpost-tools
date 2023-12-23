---
author: full
categories:
- database
date: 2023-07-20
description: 'On my website installation, I need a mysql database to store my posts
  and configuration. During the configuration, I suddently run into a strange error:
  mysql server is complaining about authentication issues. Here is how I solved it.'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1646322256/kyle-glenn-dGk-qYBk4OA-unsplash_irufoi.jpg
inspiration: https://stackoverflow.com/questions/2995054/access-denied-for-user-rootlocalhost-using-passwordno?noredirect=1&lq=1
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-20
pretified: true
ref: 2022-03-03-how-to-solve-access-denied-for-user-root-localhost-using-password-no-unable-to-authenticate-php-mysql
tags:
- mysql
- windows
title: 'Comment résoudre l''accès refusé pour l''utilisateur ''root''@''localhost''
  (en utilisant le mot de passe : NO) ? Impossible d''authentifier php/Mysql'
transcribed: true
youtube_video: http://www.youtube.com/watch?v=cmRg4qCSU9g
youtube_video_description: Bonjour et bienvenue dans cette nouvelle vidéo ! Aujourd'hui
  je vais vous montrer comment créer un système de connexion pour ...
youtube_video_id: cmRg4qCSU9g
youtube_video_title: TUTO PHP - Système de Connexion pour vos Utilisateurs
---

# 

jours à toutes et à tous et bienvenue
sur french codeurs alors bienvenue dans
ce nouveau tutoriel où je vais vous
apprendre à créer un système de
connexion en php et mysql
alors avant de commencer le tutoriel je
vous invite à avoir les bases on php et
mysql pour pouvoir mieux suivre et mieux
comprendre les concepts que je vais
aborder dans ce tutoriel
alors avant de commencer le tutoriel
également je vous invite à vous abonner
à mon compte instagram french codeurs où
je publie régulièrement des tutoriels
des astuces et des conseils à propos du
développement web et/ou également je
vous invite à aller voir mes story
quotidienne où je publie des contenus de
qualité et des quizz pour vous aider à
progresser en fait dans le domaine
alors on va tout de suite commencer le
tutoriel donc ce que vous allez faire
c'est déjà bas pourquoi pas de créer
votre projet si vous en avez pas encore
créé vous créez votre projet à
l'intérieur de votre dossier acheter
ducks encore une fois 2 1 même si vous
êtes sur mac ou bien d'exemple si on
vous êtes sur linux ou windows
et pourquoi pas de honte si vous êtes
également sur windows
donc vous allez sur votre serveur mon
exemple ou en poudre ou lampe bien
évidemment et vous allez sur http avez
créé votre projet donc moi j'ai déjà
donc raymond nouveaux dossiers que j'ai
appelé espace membre et à l'intérieur
j'ai créer un ficher inscriptions pour
le tutoriel précédons et le fichier
connexion pour le tutoriel actuelle
donc ce que vous allez faire aussi donc
n'oubliez surtout pas donc de lancer de
votre serveur local host pour que votre
serveur apache et mysql server puisse
tourner en fait sur votre ordinateur en
local sinon ça ne fonctionnera pas donc
sur votre navigateur bien sûr vous allez
donc accéder à votre look alost moi
c'est le cas elle est sur le port 8 8 8
donc je vais sur youtube espace membre
connexion pour un ph b donc voilà la
page est vide alors ce qu'on va
commencer par faire c'est déjà de créer
donc notre top late html donc ici on a
bien notre top late normal de base avec
notre nos balises en fait html est en
fait ici donc j'ai juste mais un
encodage et un titre alors au niveau de
votre corps de pages donc au niveau de
votre balise body donc ce qu'on va venir
faire c'est comme dans le tutoriel
précédent au niveau du système
d'inscription
et bien en fait juste créer un
formulaire donc pour cela et bien je
vais créer un formulaire beau de
méthodes poste comme ceci est donc pour
l'action comme d'habitude
eh bien je ne vais pas changer de
fichiers donc je vais rester dans le
fichier connexion pour un php donc bien
évidemment si vous avez un fichier
externe ou vous souhaitez donc exécuter
le code php et bien vous avez donc dont
action vous pourrez spécifié en fait
votre fiche est alors on fit ensuite
donc ce qu'on va pouvoir faire c'est de
mettre à nîmes foot donc un limp août
qui correspond à un champ de texte au
niveau de ce champ de texte bas par
exemple je vais mettre du texte donc le
type ça sera du texte et comme non bah
je vais mettre le pseudo donc je demande
à l'utilisateur de choisir un pseudo
alors ensuite bas je mets un assaut de
mines et donc je vais créer un autre
hymne poutre que je vais appeler
password voilà que le nom ce sera donc
mdp alors password s'en est sinon ça ne
fonctionnera pas et ensuite bas ce qui
nous reste à faire c'est donner de
maître par notre bouton notre bouton qui
sera de type subite et le nombre a par
exemple on voit des données donc moi je
vais juste écrit renvoie donc voilà donc
pour ceux qui ont suivi le tutoriel sur
le système d'inscription j'ai fait
exactement la même chose au niveau du
formulaire donc comme vous pouvez le
voir c'est la même chose lorsque je vais
faire aussi c'est d'aligner en fait
notre formulaire au milieu de notre page
pour cela je mets la tribu lane à center
donc maintenant si j'ai actuellement ma
page alors ici je suis toujours dans le
système d'inscription
je vais me rendre dons
connexion point php comme ceux ci et là
on a bien notre formulaire donc si
j'envoie des données rien ne se passe
tout simplement parce qu'on n'a pas
encore de code php au niveau du code php
donc je vais me mettre tout en haut de
ma page html
est ce que je vais faire c'est tout
simplement de déclarer notre balises phb
alors comme d'habitude on va déclarer
notre base de données
alors notre base de données qu'est ce
que c'est bas c'est tout simplement la
base de données qui se trouve au niveau
de phpmyadmin donc phpmyadmin c'est tout
simplement donc la base de données en
local si vous voulez de de notre projet
en localhost donc de demande ou de web
ou de lampes ou deux exemples donc ici
en fait
en fait je vous invite à regarder le
tutoriel précédent pour voir à peu près
ce qu'on a fait en fait ce qu'on a fait
c'est jose explique vite fait en fait
j'ai crée donc une base de données
espace membre donc vous allez sur une
nouvelle base de données vous tapez
espace membre vous crée ensuite vous
créez votre table à l'intérieur donc de
cette base de données espace membre
et bien tout simplement j'ai créé une
table usa donc au niveau de cette table
hüther j'ai créé donc à champ idée un
champ pseudo et un chant mot de passe
donc le champ idées et temps est un
entier
donc je les autos incrémenté pour que
lorsqu'on crée en fait un nouvel objet
donc que c'est à dire lorsqu'il ya un
nouvel utilisateur dont notre table eh
bien il louera en fait un identifiant
unique qui est un entier donc en
incrémente à chaque fois qu'il ya un
nouvel utilisateur si vous voulez alors
ensuite bas on a un champ pseudo et un
chant mot de passe qui sont de type
texte
alors si je parcours ma table et bien
ici on regarde et en fait on a déjà
quelques utilisateurs que j'ai créée
dans le tutoriel pressé non
d'inscription en fait ici j'avais créé
un
trois utilisateurs un frenchie codeurs 1
2 et 1 avec du texte n'importe quoi
alors au niveau du mot de passe comme
vous pouvez le constater on à crypter
nos mots de passe avec le système
chahains donc la méthode chat un
justicier qui nous a permis en fait de
crypter notre autre passe alors pareil
pour le pseudo en fait on a mis de
l'acheter mais les spéciales charge
spéciale charles j'arrive pas à
prononcer pour en fait pouvoir éviter du
code html à l'intérieur donc voilà donc
la juste j'ai juste intégré quelques
utilisateurs
alors ici bien évidemment ça fait 1 2 et
4 pour l'identifiant tout simplement
parce que j'ai supprimé l'identifiant
numéro 3 ça c'est pas trop grave
alors du coup bah justement pour pouvoir
se connecter à cette base de données
parce qu'on va pouvoir faire c'est déjà
de déclarer notre bouffe variable bdd on
va en fait pouvoir créer un nouvel objet
pdo puisqu'on va utiliser l'objet pdo
pour pouvoir exécuter nos roquettes
est ce qu'on va pouvoir faire c'est de
déclarer mysql host est tout simplement
je vais le mettre à locale est donc ce
maïs clause devait en fait tout
simplement spécifié votre hébergeur donc
par exemple si vous êtes sur un
hébergeur en ligne comme ovh infiniti
free etc
est-ce que ce que vous pourrez faire en
fait c'est d'aller dans phpmyadmin de
créer une base de données est en fait il
va vous générez en fait un hébergeur par
exemple ça peut être une ip ça peut être
une adresse comme par exemple je sais
pas sql points 1 2 3 etc
votre nom d'utilisateur blabla donc ici
si vous êtes en local pardon comme moi
localhost avec mon exemple lampe est
bien ce que vous pouvez faire c'est de
mettre localhost voilà ensuite parce que
vous allez faire c'est de déclarer en
fait dit by name qui le nom de votre was
the dawn est donc ici comme je vous l'aï
dit j'ai créé une nouvelle base de
données dont phpmyadmin que j'ai appelé
espace membre donc je j'ai créé un
espace membre donc voila vous faites
très attention à ne pas mettre de fautes
et ensuite je vais mettre un encodage
pour encoder en fait nos données en
utf-8 donc ça vous n'êtes pas obligé
mais pour être sûr vous mettez utf-8
alors ensuite vous mettez une virgule
est donc en second paramètre au niveau
de notre objet pdo donc ce qu'on va
venir faire c'est pourquoi pas de mettre
le nom d'utilisateur
alors le nom de l'utilisateur ça va être
route par défaut normalement sur
localhost sur votre serveur en local ça
va être dur hoult et comme mot de passe
donc le troisième paramètre ça va être
aussi dur août
alors faites très attention avec ça pas
sûr parce que en fait ça va changer d'un
serveur à l'autre
donc je m'explique au niveau d'un
serveur en ligne ça peut très bien
changer votre nantes 8 d'utilisateurs
sera sécurisé dont vous aurez un mot de
passe ici à saisir qui sera fourni par
votre hébergeur et un mot de passe
un an d'utilisateurs par nom qui est
également fourni avec ici si vous êtes
en local ça peut être route au niveau de
l'utilisateur et ça peut être route au
niveau du mot de passe mais attention si
vous êtes par exemple sur web
je sais pas si si pour vous ça fait ça
mais moi par exemple quand j'étais sur
windows
et bien comme je vous l'expliquais déjà
dans le tutoriel précédent au niveau de
l'inscription pour l'ap-hp
et bien en fait bah quand j'étais sur
windows
il n'y avait pas de mot de passe du coup
ici fallait rien m et du coup j'ai passé
beaucoup beaucoup d'heures à essayer de
résoudre le problème
alors qu'ici le problème était que baye
est tout simplement il n'y avait pas de
mot de passe à rentrer au niveau du
serveur est en fait ici vous faites très
attention à vérifier
au préalablement au niveau de votre
local os si il ya bien c'est un mot de
passe en fait au niveau 2 du paramètre
de mot de passe
alors ici par défaut normalement ces
routes pareil pour le nom d'utilisateur
vérifiez bien à ce que tout soit correct
alors maintenant donc trêve de bavardage
si j'actualise voilà donc si j'actualise
normalement ça devrait fonctionner rien
ne se passe c'est parfait alors une fois
qu'on a terminé avec ce système peu de
deux requêtes au niveau de notre base de
données si vous voulez ce qu'on va
pouvoir faire c'est déjà de d'effectuer
toutes les opérations
donc lorsque l'utilisateur va cliquer
sur le bouton d'envoi on va exécuter des
opérations
donc pour cela j'utilise une condition
ifs donc si l'utilisateur clique sur le
bouton d'envoi donc if i 7 var poste
encore une fois rappelez vous on utilise
la méthode poste pour envoyer des
données vers le serveur et pour
récupérer bien sûr donc vous mettez
poste on voit donc qui est qui et le nom
du bouton en fait et ensuite vous ouvrez
les accolades et à l'intérieur en fait
on va venir exécuter nos différents
codes alors déjà on va venir vérifier si
l'utilisateur rentre bien tous les
champs ou pour cela on vérifie que les
gens ne sont pas vides donc qu'on écrit
if he's not un petit is not
c'est le point d'exclamation donc si
c'est pas vide
donc si la variable pseudo n'est pas
vide est également donc en fait la même
chose pour la variable mot de passe
comme ceci donc si le 2 si les deux
champs pardon ne sont pas vides ce qu'on
va pouvoir faire ces d'exécuter le code
sinon bah si sont vides on n'écrit pas
qu'ils sont vides donc veuillez
compléter tous les chante
voilà comme celle ci donc si j'actualise
mon code pardon donc si je gens voient
les données du formulaire sans donner
donc sans sans rien à l'intérieur des
champs il nous dit bien failli compléter
tous les champs pareil si je remplis un
seul champ j'en vois hélas on a bien le
même message alors je vais juste mettre
un autocollant l'it as of pour éviter
l'auto complétion
alors voilà donc si j'ai actuellement
code maintenant donc si j'ai créé du
code
ok donc là il n'ya plus nos propositions
qui s'affiche lorsque je place mon
curseur sur les champs alors maintenant
parce qu'on va pouvoir faire ces
d'exécuter d'autres codes donc à
l'intérieur du même bloc ce qu'on va
pouvoir faire c'est déjà donc de de
déclarer le pseudo de l'utilisateur donc
le pseudo de l'ue theater pareil comme
dans le tutoriel précédent mais de
l'acheter mais les spéciales cars pour
encoder pour crypter on va dire on va
pas vraiment cryptée mais pour sécuriser
notre champ de notre champ de texte donc
notre no strings pour en fait éviter le
l'insertion de code html et surtout de
code javascript pour pouvoir en fait
accéder à différentes données si on a un
utilisateur malveillant donc vous
encoder avec de l'html spécial cars
voilà comme ceux ci est ensuite bas pour
le mot de passe on va faire la même
chose
alors ici c'est très important au niveau
du système d'inscription en avait mis un
encodage achats
donc on fait cet encodage achats comme
je voulais dit dans le tutoriel
précédent permet de décrypter notre mot
de passe pour éviter en fait
que lorsque je rentre dans ma base de
données eh bien on est notre mot de
passe en clair donc ici on a bien notre
mot de passe qui est crypté donc en fait
pour pouvoir a décrypté le mot de passe
ensuite dans notre fichier connexion
poids phb et bien ce qu'on va pouvoir
faire c'est de recruter on va dire notre
mot de passe mais cette fois ci en fait
ce qui va faire c'est de décrypter le
mot de passe donc voilà au lieu de le
rue
alors excusez moi donc au lieu de le
recruter il va le décrypter voilà vous
allez voir ensuite à quoi ça va servir
donc maintenant ce qui va venir faire
c'est ensuite de sélectionner en fait de
récupérer tous les utilisateurs qui se
retrouvent dans ma base de données donc
je fais une requête qui va récupérer
tous les utilisateurs
donc voilà bd des prix perd donc une
requête préparer et en fait je vais
venir sélectionnés tous les utilisateurs
donc la petite étoile qui va qui va
signifier hall tous donc select hall
from earth donc sélectionner tous les
dictateurs de la table heather ce qui se
trouve dans notre base de données
est-ce qu'on va venir faire c'est de les
sélectionner en fonction en fait donc
courir ou r
pseudo est égal à point d'interrogation
et mot de passe est égal à point
d'interrogation
ça veut dire qu'ici en fait on va venir
sélectionnés tous les utilisateurs qui
possèdent le pseudo il le mot de passe
saisie par l'utilisateur
donc je jeu donc re déclare cette
variable mais cette fois ci je vais
faire knicks une requête exécuté voilà
et ensuite je vais mettre un oreilles
est ce que je vais faire c'est de
spécifier le pseudo rentrait pas
l'utilisateur et le mot de passe ici
donc on ce qu'on veut faire c'est tout
simplement de récupérer l'utilisateur
qui correspond aux pseudo rentrée par le
pseudo de l'utilisateur dans le
formulaire et le mot de passe rentré
dans le mot de passe dans le formulaire
voilà alors maintenant donc si j'ai
actuellement un code et que je tape
n'importe quoi rien ne se passe bien sûr
parce que on a juste effectué une
requête qui venu en qui va nous renvoyer
truau folz et ensuite on va venir en
fait gérer tout ça donc ce qu'on va
venir faire alors je sais pas du tout si
ça nous renvoie truau force
non je pense que ça nous renvoie ici ah
oui donc ici en fait ça nous renvoie un
tableau qui va en fait contenir tous nos
éléments
alors parce qu'on va pouvoir faire c'est
ensuite le dire ap hp que si au niveau
de ses talents de ce tableau est bien on
a récupéré au moins un élément
eh bien on va pouvoir connecter
l'utilisateur pourquoi parce que en fait
pas tout simplement on vérifie si le
pseudo et le mot de passe de
l'utilisateur se trouve bien dans la
table ça veut dire qu'on verra fils et
lui theater se trouve bien dans notre
table est en fait si l'utilisateur se
trouve dans notre table ça veut dire que
l'autre à aurait donc notre tableau ne
sera pas vide et du cou pour voir si
l'ue theater correspond bien à un
un champ dans notre table qu'il suffit
de faire c'est tout simplement de mettre
une condition est de dire que si notre
arrêt donc notre tableau n'est pas vide
et bien tout simplement c'est que
l'utilisateur est connecté parce que ici
on a bien récupéré l'utilisateur en
question donc pour cela on va y créant
une condition yves récup
voilà donc y ferez cupe hüther recompte
du coup donc vous mettez bien une petite
flèche comme ceci est donc if récup isr
roquentin dont croquante qui est une
méthode je pense je sais plus recompte
supérieur à zéro donc ça veut dire que
si on a au moins un élément est bien ce
qu'on va pouvoir faire c'est donc de
connecter l'utilisateur
par contre si bas tout simplement
c'est inférieur à zéro donc ça veut dire
que si on a récupéré aucun utilisateur
et bien ce qu'on va pouvoir faire c'est
de dire à votre mot de passe
mot de passe ou pseudo est incorrect
comme ceux ci en copie un peu les sites
assez connu voilà donc on met le même
message d'erreur alors ici on a un
problème
http pourquoi alors oui ça vient du code
convient d'écrire qui n'est absolument
pas correct alors je vais essayer de le
rectifier donc
alors ce qu'on va faire c'est tout
simplement de remettre un récup
plusieurs comme ceci je lui dis donc six
ans le compte et qu'il est supérieur à 0
alors on exécute du code puis si
j'actualise ce code tout se passe
correctement sinon et bien donc je vais
mettre un écho je vais écrire erreur
voilà comme ceci donc si j'ai actualisé
mon code tout se passe correctement
également alors je sais pas qu'est ce
qui a foiré mais bon c'est peut-être mon
serveur qui a crash
mais bon c'est pas très grave donc ici
on va réécrire donc votre mot de passe
ou pseudo est incorrect voilà tout se
passe correctement en fait c'était juste
mon serveur qui a crash
donc si vous avez remarqué une erreur
n'hésitez pas à me signaler dans le
commandant les commentaires donc
normalement si je saisis n'importe quoi
et que j'en vois ici on a bien notre
message d'erreur tout simplement parce
que on a aucune entrée dans notre table
qui correspond aux pseudos et aux mots
de passes saisies par l'utilisateur et
bien et si en fait rappelez-vous en a en
fait cryptée le mot de passe de
l'utilisateur on en fait décrypté par
non le mot de passe de litas temps bon
on a on l'a pas vraiment décrypter mais
c'est juste que pour que vous compreniez
la chose en fait on l'a pas décrypté
mais c'est juste que on à crypter le mot
de passe rentrée par l'utilisateur au
moment de la connexion et en a juste
match et en fait on a juste au regard
des 6 e cryptage correspond au cryptage
qui se trouve dans une des tables dans
la table isr sedan une deux dans un
champ en fait dans un label de notre
table users donc c'est à ça que ça sert
on l'a pas vraiment décrypter en fait
mais bon donc maintenant ce qu'on va
pouvoir faire c'est tout simplement donc
que lorsque si on trouve donc un
utilisateur dont
la table est bien ce qu on va pourra
faire c'est de déclarer nos sessions
alors rappelez vous une session veut
enfin en fait nous permettre de laisser
un utilisateur connecté sur le site qui
va nous permettre de récupérer des
informations liées à l'utilisateur qui
vont en fait pouvoir circuler sur toutes
les pages alors pour ceux là bas on veut
en fait on va venir déclarer une
sécheuse start comme ceux-ci tac est ce
qu'on va pouvoir faire c'est en fait de
déclarer des cessions comme au niveau de
l'inscription
on avait en fait ici déclarait des
sessions propre à l'utilisateur donc
l'utilisateur connecté aura un pseudo un
mot de passe et un identifiant donc ici
est ce qu'on va pouvoir faire c'est de
mettre pareil un pseudonyme
comme ceci donc un pseudo à
l'utilisateur donc ce pseudo va être
simplement en fait correspondre aux
pseudo rentrée par l'utilisateur
voilà que la cession pseudo correspond
aux pseudo ensuite bas on va faire la
même chose pour la session mdp
voilà donc pareil mdp et enfin pour la
session idée c'est un peu plus compliqué
parce qu'on fait ici on va venir
récupérer l'identifiant qui a été
récupérée sur le sur la requête en fait
lorsqu'on a sélectionné l'utilisateur
dont la table donc pour cela est bien ce
que je vais faire c'est tout simplement
de re déclaré notre récup une heure
comme ceci mais cette fois-ci de
récupérer absolument toutes les données
voilà comme ceci dans un tableau fâchent
comme ceci mais ce qu'on va venir faire
c'est en fait de mettre des crochets
pour lui dire de rock de récupérer
uniquement l'identifiant comme ceci donc
nous ce qui nous intéresse c'est
l'identifiant alors rappelez vous de
cette syntaxe on l'a en fait utilisé
dans le système d'inscription donc
maintenant ce qu'on va pouvoir faire
aussi c'est pourquoi pas donc affiché
pour être sûr et certain de la session
de l'utilisateur donc j'affiche la
session de l'utilisateur alors ici vous
vous allez d'effacer donc si vous mettez
votre projet en ligne assurez-vous de
bien l'effacer voilà donc qui sait c'est
juste pour essayer quelque chose donc
maintenant
ici donc si je prends le compte par
exemple de french codeurs alors pourquoi
pas ici déjà créé un nouveau compte
donc voilà je vais dont l'inscription
est ce que je vais faire pourquoi pas de
créer donc bottes
voilà bottes et comme tu passes jeu à
écrire bottes
j'envoie donc là on a bien notre
utilisateur qui est connecté avec son
identifiant numéro 5 est ce que je vais
faire c'est qu'au niveau de la connexion
et ben je vais déclarer bottes et bottes
donc je vais essayer de connecter bottes
avec le mot de passe bottes
si j'envoie regarder en appuyant en fait
pu récupérer cet identifiant cette
session en fait qui a été bien créé
alors maintenant ce que vous pouvez
faire c'est pourquoi pas on fait
rediriger l'utilisateur vers une page
donc en fait par exemple votre page
indyk ce point php comme ceci en fait ce
que vous pouvez faire c'est pas pourquoi
pas dans cette page index point php
comme je voulais dire en fait la cession
va en fait nous permet d'échanger des
données sur toutes vos pages et je
déclare en fait si sean start comme ceci
et pourquoi pas en fait je déclare
j'affiche tout simplement la session
d'utilisateur
comme je voulais dit on peut directement
accéder à la session juste ici en
faisant un session pourquoi pas afficher
sans pseudo
voilà comme ceci donc si j'ai tu as
lease et que maintenant ici donc
j'enlève le écossais sean est en fait je
leur ai dit et je le redis dirige pardon
en faisant un leader location et je le
redis riches dans le fichier index.ph
paie donc maintenant si j'ai actualise
ma page comme ceux ci et que je rentre
donc une fausse adresse qu'une faut un
faux pseudos pardon et infos mot de
passe donc ici me dis bien votre mot de
passe ou pseudo est incorrect et
maintenant si je rentre le pseudo de
bottes et le mot de passe de bottes
donc j'en vois hélas on est bien
redirigée vers index.ph paix et regardez
on a bien accéder à la session ce dos de
l'utilisateur donc comme vous pouvez le
voir on a bien notre donné ce dos qui a
été échangé dans
une autre page même sans avoir à
effectuer du code de connexion de
l'utilisateur donc c'est à ça que ça
sert à les sessions c'est super
important
c'est pour pouvoir authentifier si vous
voulez vos utilisateurs sur votre site