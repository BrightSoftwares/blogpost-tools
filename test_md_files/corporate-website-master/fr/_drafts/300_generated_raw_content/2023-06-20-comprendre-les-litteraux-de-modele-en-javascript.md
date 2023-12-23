---
ToReview: true
author: full
categories:
- javascript
date: 2023-06-20
description: The 2015 edition of the ECMAScript specification (ES6) added template
  literals to the JavaScript language. Template literals are a new form of making
  strings in JavaScript that add a lot of powerful new capabilities, such as creating
  multi-line strings more easily and using placeholders to embed expressions in a
  string. In addition, an advanced feature called tagged template literals allows
  you to perform operations on the expressions within a string. All of these capabilities
  increase your options for string manipulation as a developer, letting you generate
  dynamic strings that could be used for URLs or functions that customize HTML elements.
image: https://sergio.afanou.com/assets/images/image-midres-36.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-20
pretified: true
ref: javascripttemplate_1240
tags: []
title: Comprendre les littéraux de modèle en JavaScript
transcribed: true
youtube_video: http://www.youtube.com/watch?v=-7JTdtroBpI
youtube_video_description: Tour d'horizon de l'utilisation de littéraux de gabarits
  (template literals) en JavaScript.
youtube_video_id: -7JTdtroBpI
youtube_video_title: Littéraux de gabarits en JavaScript
---

# 

les littoraux de gabarit ou template
littoral sont en anglais sont une
manière d'écrire des chaînes de
caractères en javascript avec quelques
super pouvoirs intéressant sache déjà
quand es 2015 on ne pouvait appeler ça
des gabarits de chaînes de caractères ou
en anglais des templates wings mais pour
le reste de cette vidéo puisse aller
template literal ce en javascript pour
créer les chaînes de caractères on
utilise les guillemets simple ou les
guides emile double de cette manière là
et on tape du texte à l'intérieur de
cette manière là pour créer un template
littoral
on va utiliser le caractère accent grave
ensuite on entre du texte à l'intérieur
et on utilise aussi l'accent grave pour
le refermer
ça nous renvoie exactement le même
résultat pour s'intéresser un peu à la
différence on est ce qu'il ya une
différence avec une chaîne de caractère
a priori non puisque si on enregistre le
résultat de chaînes de caractères avec
des accents graves qu'on appelle en
anglais des bacs tic
on va l'enregistrer dans une variable
lights littérale et du coup si on fait
par un take off l'insu de template dole
on voit qu'ils nous rendent plus qui
leur tombe bien le type string et
d'ailleurs on peut accéder aux mêmes
méthodes que sur une chaîne de
caractères classique par exemple en
ligne et du coup on se retrouve bien
avec 19 qui le nombre de caractères de
cette chaîne de caractères alors
maintenant à quoi ça sert d'écrire des
accents là parce que l'action reste
quand même un caractère qui est pas
facile à accéder sur sur un clavier
classique
la première raison est le premier un peu
super pouvoirs que va posséder une
chaîne de caractères écrite en template
eyrolles c'est le fait de pouvoir
facilement faire du multi s'étaient
associés on écrit une chaîne de
caractère multi
en javascript classique on va être
obligé de faire
par exemple si on veut l'avant sur deux
lignes en plus dans le code va devoir
faire un contre slash haine pour
signifier une new line et par exemple on
peut commencer à écrire ensuite avec un
plus ici deuxième ligne et à ce compte
là on aura bien une chaîne de caractères
qui tient sur deux lignes mais ça aura
eu deux défauts le premier défaut aussi
devoir utiliser un opérateur l'opérateur
plus et aussi de forcer un caractère new
line ce qui est assez assez moche au
maintien avec le template literal ce
qu'on va pouvoir le faire complètement
naturellement c'est à dire qu'on va
écrire notre texte
je vais écrire exactement la même chose
et je pourrais faire ici un vrai qu à
reichshoffen donc du coup et j'appuie je
serai touche entrée et je commence à
taper ma deuxième ligne je ferme tout ça
il faut ici que je ferme aussi et je me
retrouve avec exactement le même
résultat
dans les deux cas sauf que ici c'est
beaucoup plus lisible
voilà pour le premier truc un peu cool
que les templaises littérale ce nous
permettent de faire le deuxième truc
cool c'est que on va pouvoir glisser en
plein milieu d'une scène de caractère d
expression sans art au besoin d'utiliser
l'opérateur plus un exemple imaginons
que je mets dans une variable singh je
mets trois trains ont écrit les chaînes
de caractères en français si jamais je
veux dire j'aime les trains à partir de
cette variable et avec les apostrophes
double classique en basket je dois
écrire ça de cette manière j'aime les
jeux fait un plus je mets fais attention
je suis un plus que je mets trois petits
points par exemple
voici un petit peu quand même compliqué
au bon sens quand on quand on a
l'habitude ça pose pas de gros soucis
mais quand même avec les temples haters
ont écrit ça du maine beaucoup plus
naturelle puisque on peut glisser des
expressions à l'intérieur et continuer
notre chaîne de caractères tout
tranquillement et on obtient exactement
l'enlever le même résultat avec quelque
chose qui est quand même beaucoup plus
lisible et si vous avez l'habitude de
faire du rugby par exemple il me semble
que c'est très semblable à sarsan
beaucoup en fait à canton tunisie
l'opérateur diez et ensuite avec les
accolades javascript ses dollars et les
accolades
alors quand je dis qu'on peut utiliser
une expression on peut vraiment utilisé
une expression comme un calcul par
exemple un plus un égale et là je veux
et glisser un poussin et du coup je
ferme ça et je me retrouve avec bien un
plus un égale de prendre si d'une
manière un peu innocente
vous allez écrire vous voulez écrire la
même chose avec des chaînes de
caractères classique
je vais écrire un plus un égale et là si
je me mets à faire un plus un mais alors
voir une grosse surprise puisque c'est
moi écrire ça comme il faut et un plus
un plus un frein je me retrouve avec une
concaténation 2 1 qui a été transcendant
string et ensuite de 1 qui a été
transformé en string aussi et qui se
retrouvent mises placées dans cette
chaîne de caractères de manière
complètement littéral si jamais je veux
vraiment utiliser des plus et d'ailleurs
postroff double jeu de voir englober de
parenthèse qu'à ce compte là je veux
vraiment avoir en premier lieu le calcul
de cette expression qui ensuite conca
tenait dans la chaîne de caractères
l'avantagé avec les temples et little
c'est qu'on a pu associer des
parenthèses puisque ces blocs là sont
complètement évalué avant d'être ensuite
transformé en string pour être ajouté
interpol et il me semble dans la chaîne
de caractères donc ici c'est vraiment
une expression qui est évaluée quand je
dis que c'est une expression qui peut
être évaluée ça peut aller encore plus
loin puisque étant donné qu'on a tous le
pouvoir de javascript au sein de ces
accolades
on ne peut utiliser des méthodes sur des
objets peints aussi j'ai des fruits par
exemple mme hanane bon
et que j'ai par exemple une chaîne de
caractères qui est là pour définir une
liste de courses par exemple penser à
acheter deux points il a une fois que
j'ai ouvert les accolades à l'intérieur
je peux y glisser une expression et
quand je dis une expression ça fait
vraiment n'importe quoi donc par un
fouet ce point maps ou tout simplement
engine et l'on se retrouve avec qui
pensaient acheter bananes oranges lepage
voilà donc ça devient vraiment puissant
on peut faire des appels à des fonctions
qui prennent des arguments tout est
possible alors comme pour les chaînes de
caractères classique il va falloir faire
attention à celles utilisées celles
quelques quelques expressions je pense
pas d'emplois nulles en defined falls
puisque comme dans le cadre d'une chaîne
de caractère classique si je dressais de
conquête et nsa avec qui entraîne des
fign
je vais me retrouver avec je n'aime pas
les n2 fine ce qui peut parfois poser
problème
et si je fais la même chose avec les
temples returns
je vais avoir exactement
le souci c'est valable pour un defy nul
falls
donc à partir de là vous le voir comment
vous voulez gérer le cas des ânes des
fagnes où le dénouer et compagnie 1
on peut si on veut vraiment pas affiché
une des failles non on peut faire ça
pour afficher du vide voilà c'est à
peine mieux
à vous de choisir en fonction de votre
situation dans le cas le plus moche
peut-être de ce genre de choses c'est
quand on passe à autre chose qu'une
primitive par action passé un objet là
ça devient complètement la feps donc si
on fait le constat
12h égal et là on a un objet porte avec
même paul
et que ici on va vouloir commencer une
chaîne de caractères dans closer de
points et la tension mais juste user on
va surtout avec un horrible object
object de ce genre là imaginons que vous
êtes dans un template littoral et que
vous voulez vraiment écrire un accent
grave tout seul du coup c'est aussi
simple que en fait dans les autres dans
les autres cas c'est à dire qu'on va
l'échappée avec le anti slash 1
par exemple un accent de ses cris ainsi
est là du coup je vais échapper un
accent grave je peux laisser des espaces
6 janvier et ensuite je ferme la chaîne
de lérida longtemps plaie qui tarde plus
tôt on sache et que on n'est pas obligé
de faire des interpellations c'est à
dire que d'injecter des expressions 1
dans la chaîne de caractères dans le
temple haters inclus au premier niveau
c'est à dire quand on peut très bien
ouvrir du coup un template littoral
commence à écrire
m par exemple ouvrir du coup un bloc
pour faire de l'interpellation et à
l'intérieur même de ce bloc la définir
un hôte template littoral c'est qu'on le
motorisé et on peut le faire
complètement à l'infini n'ont pas
anticipé matteo +1
ici je continue ma phrase 1
et ici je passe mes tantes zéro + 10 et
je referme et ça me dis merde je sais
compter de grâce
il me semble pas qu'il y ait une limite
au nombre de profondeur ont donc c'est
quelque chose qui est extrêmement
pratique je donne un rapide exemple
concret et pas en position de générer
une classe name et que ça dépend de
certains certains éléments on va avoir
par exemple construit marie égal tout on
va avoir construit disable galles trou
et si vraiment on a besoin de gérer un
classement en fonction de ces deux états
ont peut faire pas embêtés m
si jamais il est pris mari alors à ce
compte là on peut ouvrir deuxième un
deuxième bloc de temples et littéral où
je ferme en btn primaries civet et là je
vais encore aller dans un niveau de
profondeur pour vérifier s'il a en plus
dix abris
du coup s'il est d'isabelle je vais
rajouter j'ai déjà tiré dont je fais
disait veulent et sinon je renvoie
immeubles et à la fin du coup si jamais
il est pas pris mari je peux en voir une
chaîne de caractères à vide où par
exemple btn 10 fautes
tout est possible et ensuite je peux
jouer avec ses valeurs pour vérifier que
tout ça fige les enfants ont pris marie
falls de ce coup je vais avoir btn des
foals
par contre si j'ai pris mari trop et
10h01 falls une petite hip hop
donc c'est quelque chose d'assez
puissant donc là j'ai pas mis prix
trille or donc c'est pas forcément
formaté de manière excellente mais avec
prix tueur ça reste complètement
illisible dernière chose que je peux
préciser pour l'utilisation des temples
et littoral c'est que on peut utiliser
comme dans les chaînes de caractères
classique l'école hexadécimaux de
l'unicode donc par exemple soit une
chaîne de caractères classique enverra
copyright qui est en fait un contre
slash uche 00 à 9
la seconde j'aime copyright et du coup
si je copie ça et que je mets un temple
et quitte sa place ça fonctionne oups
c'est bien du coup à faire mais ça
fonctionne exactement de la même manière
alors maintenant pourquoi à chaque fois
que je ne mets pas le point virgule sur
l'instruction précédente j'ai une erreur
tout simplement parce qu'en fait les
temples et qu'ils peuvent aussi être
utilisés en argument de fonction d'une
manière assez particulière
imaginons que j'ai une fonction tags
pour l'instant on ne fait absolument
rien je peux très bien un peu les tac
élan chaînette avec un template et rolls
et à partir de là je vais pouvoir écrire
du coup mon template liberals et avec
mes expressions
donc si on prend par exemple ça je peux
très bien faire de cette manière là donc
là j'ai une erreur tactique mais à leers
est intéressante parce que elle me dit
que l'âge et je suis censé avoir zéro
arguments et pourtant j'en passe 2 tout
simplement parce qu en fait un
quand j'utilise un temple ait quitté
runs en argument de fonction il va me
retourner deux choses un tableau des
strings d'utiliser donc là j'ai un
string et un tableau d expression et à
partir de là je pourrais les manipuler
et si on va un exemple d'utilisation de
ce genre de choses c'est pas un peu la
librairie de ces singes est ce qu'on
appelle style comme pau nantes et qui
fait un usage massif de 1
ces tags aide on appelait ça des tags et
en pleine tempe équité runs pour écrire
du css donc voilà un exemple de
d'utilisation de tagab template qualité
rolls où on a effectivement donc là on a
un objet qui renvoie ensuite points à
une méthode à qui est en fait une
fonction et qui reçoit en paramètres
tout le template littérale cette
fonction elle va pour accéder à la liste
des chaînes de caractères est ainsi que
s quand est ce qu'il y aura été passé en
interpolation par exemple y sied à ce
genre de choses c'est extrêmement
puissant c'est extrêmement malin de
faire ce genre de choses
si vous connaissez pas et que vous
faites du réactif vous invite à faire un
tour
donc je ne vais pas rentrer plus loin
dans l'utilisation des tags est empli
quitté rolls mais j'espère qu'en tout
cas la présentation que je vous aurais
fait de son utilisation classique
c'est-à-dire en mode interpolation vous
fermez créer des chaînes de caractères
vous aura été utile