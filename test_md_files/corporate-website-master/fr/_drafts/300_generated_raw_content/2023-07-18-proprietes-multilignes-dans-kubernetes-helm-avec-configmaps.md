---
author: full
categories:
- kubernetes
date: 2023-07-18
description: Il existe plusieurs API dans Kubernetes. Un ConfigMap est l'un d'entre
  eux. C'est un objet qui permet de stocker certaines données non confidentielles.
  Les données se présentent sous la forme de paires clé-valeur. Certains utilisent
  des variables d'environnement. Dans cet article de blog, nous verrons comment vous
  pouvez afficher des lignes à valeurs multiples.
image: https://sergio.afanou.com/assets/images/image-midres-25.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-18
pretified: true
ref: KubernetesHelmhowtoshowMultilineProperties
tags:
- helm
- automation
- docker
- container
title: Propriétés multilignes dans kubernetes Helm avec ConfigMaps
transcribed: true
youtube_video: http://www.youtube.com/watch?v=1uFVr15xDGg
youtube_video_description: 'YAML Tutorial for DevOps engineers | YAML Syntax explained
  with real examples ▻ Subscribe To Me On Youtube: ...'
youtube_video_id: 1uFVr15xDGg
youtube_video_title: Yaml Tutorial | Learn YAML in 18 mins
---

#  Intro

dans cette vidéo, je vais vous expliquer tout sur la
démo, nous verrons à quoi sert ml et
nous passerons en revue la syntaxe de la façon d'
écrire un fichier ml valide comme vous l'avez vu dans



# YAML is popular

mes vidéos de tutoriel sur docker
kubernetes dans Siebel
Prometheus etc I  ont montré des exemples de
fichiers de configuration tous écrits en mo
car il est devenu un format assez largement
utilisé pour écrire des configurations
pour de nombreux outils et applications DevOps différents
, c'est pourquoi lors de l'utilisation de ces
outils, il est important de comprendre les
détails de la syntaxe jaune et ses principaux
concepts en général ouais  mo est un



#  What is YAML?

langage de sérialisation tout comme le langage de
sérialisation XML et JSON
signifie essentiellement que les applications écrites avec
différents langages de technologies, etc.,
qui ont des structures de données différentes peuvent se
transférer des données en utilisant un
format commun convenu ou standard
et les formats les plus populaires sont
llamo jason et xml et le nom
llamo signifie en fait y mo n'est pas un langage de balisage
et vous pouvez créer llamo f  ile
avec l'une de ces deux extensions, elles



#  Why learn YAML? YAML Format compared to XML and JSON

sont identiques l'une des principales raisons pour lesquelles la
popularité d'hemos a tellement augmenté au
cours des dernières années est qu'il est super
lisible et intuitif, ce qui en
fait un excellent choix pour écrire des
fichiers de configuration pour tous ceux  des outils DevOps récents
comme j'ai mentionné docker kubernetes, etc.,
donc pour vous montrer un exemple et aussi une
comparaison entre les formats llamo XML et JSON
, considérons cet exemple,
voici à quoi ressemblerait le fichier y mo,
c'est très simple, c'est assez
propre, ce sont les mêmes données dans
Format XML où vous avez ce soi-disant
texte, puis vous avez le format JSON
et comme vous le voyez dans XML et les
structures de données JSON sont définies à l'aide de
caractères spéciaux en XML, vous avez un soi-disant
texte avec des crochets angulaires dans Jason, vous
avez des accolades et  en jaune, vous
n'avez pas ces caractères spéciaux, donc
la façon dont la structure de données est définie
dans le mo se fait par des séparations de lignes
et des espaces avec des indentations, c'est pourquoi
vous pouvez indenter  l'espace en XML et JSON
comme vous le souhaitez, mais dans le ml, vous obtenez une
erreur de validation si vous avez un seul
espace et une mauvaise structure de données, ce qui peut
être un peu ennuyeux, mais cela fait
du format llamó le format le plus propre et le plus
lisible par l'homme des trois, alors quels sont



#  YAML Use Cases

certains de vos cas d'utilisation les plus courants pour compter peu de
format yema sont utilisés pour les fichiers composés de canard
pour la balle néo-zélandaise prometheus kubernetes
et bien d'autres outils, alors maintenant que vous
savez ce qu'est llamo et où il est utilisé



#  YAML Syntax

, plongeons-nous dans sa syntaxe, donc ça a commencé



#  key-value pairs

avec la base  syntaxe qui est de simples
paires clé-valeur, alors prenons un exemple
que je viens de vous montrer et écrivons
des paires clé-valeur comme AB et
appelons-le authentification de l'utilisateur et nous avons un
port, mettons-le à 9000 et la version de
l'application et 1.7 juste un  par exemple, ce
sont donc de simples paires clé-valeur, tout ce
fichier jaune est écrit et vous avez
différents types de données ici, nous avons une
chaîne qui note que nous n'avons pas à l'
entourer de guillemets, vous pouvez si vous le
souhaitez afin que vous puissiez  utilisez soit des guillemets doubles, soit des
guillemets simples, soit aucun guillemet du
tout et vous avez également le nombre de
représentations si vous devez
utiliser un caractère spécial comme le
chariot de ligne par exemple, vous devez le
mettre dans des chaînes sinon le Yémen
ne peut pas le reconnaître mais autre que  que
vous n'avez pas besoin de guillemets donc je vais



#  comments

mentionner ici qu'en jaune vous avez aussi
des commentaires donc tout ce qui commence
par ce signe ou par ce caractère
fondamentalement jaune s'interprète comme un commentaire
donc je peux écrire un commentaire ici et
fondamentalement je peux utiliser ceci  commentez entre
les attributs n'importe où dans le fichier mo
où je veux rendre mon fichier encore plus
lisible et compréhensible donc c'est une



#  objects

simple liste de paires de valeurs clés ce que vous
pouvez faire est que vous pouvez les regrouper à l'intérieur d'
un objet afin que vous puissiez créer un objet  en
jaune et vous pouvez le faire en in
dans ces paires de valeurs clés individuelles et en les
enfermant dans un objet appelons-le
un micro service comme celui-ci et cela
devient un objet avec un micro service
avec i  ts attributs et notez que l'
espace doit être exactement le même pour chaque
attribut dans l'objet et
notez également que parce que Jemil est si
sensible aux espaces et à l'indentation, c'est
toujours une bonne idée d'utiliser un
validateur llamo avant par exemple d'exécuter
un fichier de configuration  dans kubernetes ou
vous appliquez cela ou utilisez ce fichier pour vous
assurer que vos invitations sont correctes et
qu'il existe des outils en ligne pour
celui que j'utilise est celui-ci ici, mais
il existe également d'autres outils en ligne,
je peux les lier dans la description
donc ce que vous pouvez faire, c'est que vous pouvez simplement copier
cela et il vous dit que c'est valide si
je par exemple cela va crier
cette indentation afin que vous puissiez vérifier votre
validité et ici alors revenons en jaune



#  lists

vous pouvez aussi avoir des listes par exemple
si vous avez plusieurs micro-services comme
celui-ci, je peux créer une liste de ces micro-
services simplement en utilisant - donc comme ceci
et encore une chose importante que ces
attributs restent au même niveau et
le - est correct  ici, vous pouvez également avoir



#  boolean

des valeurs booléennes, par exemple si nous avons
déployé des attributs, vous pouvez dire vrai ou
faux et au Yémen, vous pouvez également exprimer
des expressions booléennes avec oui ou non,
disons donc déployé oui et aussi avec on
et off donc toutes ces 3 paires  des valeurs
sont des expressions de valeurs booléennes et
vous voyez également que la coloration syntaxique est



#  more about lists

différente, il s'agit donc d'une liste et ce
sont les éléments de la liste et je peux ajouter une
deuxième application d'élément, disons des cartes d'achat
et disons que le port est neuf mille deux
alors  nous avons la version 1.9 et de
cette façon, vous pouvez définir des listes d'objets
mais vous pouvez également définir des listes de
valeurs simples, par exemple si vous aviez une liste
de noms de micro-services, vous
pourriez faire comme ça et ce serait
bien comme  bien et vous pouvez également utiliser des listes à l'
intérieur d'un élément de liste, par exemple si vous
avez plusieurs versions d'un panier d'achat,
par exemple, que vous souhaitez répertorier
ici pour une raison quelconque, je ne sais pas si vous
pouvez les répertorier ici pour que je puisse faire
versions disons que vous avez 2.0 et ensuite
vous avez 2.1 etc et je vais copier cela
aussi dans le validateur et ici vous voyez
que la position - vous pouvez en fait utiliser
différentes annotations pour cela donc j'ai
une indentation ici mais je n'en ai pas  avoir
ici donc c'est bien aussi je pourrais faire
comme ça ou je peux l'aligner sur le
parent de l'attribut donc ne soyez pas confus
si vous voyez différents alignements des
listes fonctionnent car llamo reconnaît
que c'est un élément de liste ce qui ne fonctionnera pas
est si vous n'alignez pas les éléments de la liste en
utilisant l'indentation, par exemple, il y avait
un espace, le validateur sera
rouge, donc quelques petits détails là-bas
sachez également que si vous avez des éléments primitifs dans
la liste comme celui-ci par exemple certains
pas le  les éléments d'objet, mais les
primitifs, vous pouvez également l'exprimer de
manière différente et c'est ainsi qu'avec la
syntaxe différente, vous avez des
crochets et vous pouvez mettre ces valeurs à l'
intérieur comme une liste, ce qui la rend en
fait plus lisible si vous avez
simplement d  les atatypes et non les objets
validons cela également pour nous assurer que vous
pouvez également avoir des chaînes ici ou les
mélanger n'a pas d'importance maintenant c'est vraiment
quelques-unes des bases de la syntaxe llamo donc pour la
rendre plus pratique et réaliste
regardons réellement



#  Real Kubernetes YAML Configuration Example

vrai exemple jaune kubernetes pour voir
comment cette syntaxe de base est exprimée
là-bas, donc je vais nettoyer cela et
examinons une configuration de pot,
donc c'est essentiellement la partie principale où
les métadonnées et le genre, etc. sont
définis comme vous le voyez, ils sont super
simples  paires de valeurs clés et ensuite vous avez
ces objets que nous venons de voir avec
Hiroki ou les indentations pour avoir un
objet de métadonnées et à l'intérieur que vous avez
un autre objet d'étiquettes et ici vous avez
la spécification et les conteneurs peut-être que
vous êtes déjà familier avec cela et
dans les conteneurs est  une liste de sorte que chaque
élément de conteneur doit en quelque sorte commencer
par
- et l'indentation, puis nous avons le
nom du conteneur, avons l'image
, utilisons nginx, puis vous avez des ports
qui  est une autre liste, donc encore une fois, nous commençons
par - pour répertorier les ports, puis vous avez
l'attribut qui est la valeur du port du conteneur à l'
intérieur du conteneur, vous
pouvez également avoir des montages de volume qui est une autre
liste, donc ici, vous listez tous vos volumes
et c'est une liste d'objets  encore une fois,
nous avons des paires de valeurs clés, utilisons Je ne connais pas le
volume nginx et le chemin de montage
un exemple et voici à quoi
ressemblera une configuration de pod afin que vous ayez à
nouveau des blocs de construction de base
paires de valeurs clés objets et listes, puis des listes à l'
intérieur de cette liste  article et puisque les
conteneurs sont également au moins vous pouvez avoir
plusieurs conteneurs à l'intérieur et par
exemple si je devais définir un conteneur side-car
, j'aurais une autre
expression d'élément - et ici, je dirais que
c'est mon conteneur side-car et encore image
une image etc aussi un autre  exemple que
j'ai également montré dans l'une de mes vidéos est l'
endroit où nous avons déployé une image curl en tant que
side-car et à l'intérieur de cette
configuration de conteneur, les roues avaient ces deux lignes,
je vais en fait copier le  m et ici
vous voyez qu'il s'agit de cette
syntaxe alternative de définition des listes, donc les arguments sont
une liste et nous l'utilisons comme ceci, puis
nous avons les deux éléments ici un et deux,
donc savoir comment fonctionne la syntaxe jaune
devrait faciliter la compréhension du
kubernetes  structure du fichier de configuration
mieux un autre concept important de la
syntaxe Gemmell est lorsque vous avez



#  Multi-line strings

des chaînes multilignes, par exemple le
contenu du fichier chaîne multiligne appelons-le
l'attribut et au lieu d'écrire
cette chaîne multiligne ici avec le
chariot je peux l'écrire en fait  sur
plusieurs lignes comme celle-ci, donc je n'ai plus besoin de
cette chose, donc c'est une
chaîne multiligne et c'est la
ligne suivante, etc.
interprétez
tout ici
comme un texte multiligne afin que ces sauts de ligne
restent en fait un autre cas pourrait être
si vous avez cette chaîne super longue qui
doit être sur une seule ligne donc par
exemple c'est une seule ligne  e chaîne
qui devrait être sur une seule ligne et d'
autres choses
, mettons des points ici et dans ce cas,
évidemment, vous voulez les chariots de ligne
ici, mais vous ne voulez pas non plus écrire
tout cela sur une seule ligne car ce n'est
tout simplement pas très lisible et  c'est pourquoi
vous voulez pour la lisibilité que vous
voulez toujours afficher cela ici dans mon
fichier de démonstration lui-même, mais vous voulez que le jaune soit
interprété comme une seule ligne dans ce
cas au lieu d'un tuyau, vous le
remplacez par un signe supérieur à ou
par ce support angulaire et  cela
sera interprété comme une seule ligne maintenant, ce
n'est qu'un exemple aléatoire, alors voyons en
fait quelques cas d'utilisation réels.
ici vous avez le nom
de l'attribut et appelez-le comme
vous voulez
et ici nous utilisons ce tuyau et ce sont en
fait le contenu du fichier qui
va être affiché exactement comme
ceci avec des chariots de ligne beca  utilisez ceci
doit être chacun sur sa propre ligne et de
cette façon vous pouvez réellement écrire
des fichiers de configuration pour différentes
applications comme celle-ci est pour les
moustiques vous avez aussi peut-être la grippe en D
et ils ont leurs propres
formats différents et vous pouvez écrire le
tout  en tant que fichier représenté par une
chaîne multiligne en jaune
un autre exemple d'utilisation de cette
chaîne multiligne que vous pouvez réellement rencontrer
dans les fichiers de configuration des communautés est
celui-ci ici donc cela fait partie de la
configuration d'un pod donc vous avez cet
attribut de commande et  ici vous voyez la
liste familière et ici encore vous avez
ce tube qui est suivi d'une
chaîne multiligne et c'est un exemple
de
bhana que j'ai trouvé donc fondamentalement ce qu'il
fait est qu'il exécute la commande shell
et c'est un script shell donc  vous pouvez en
fait mettre tout le contenu d'un
script shell comme vous l'auriez sous forme de
fichier de script shell après ce symbole de tuyau
sous forme de texte multiligne et cela
s'exécutera comme un script shell essentiellement o  une



#  environment variables

chose que j'ai également eu besoin d'utiliser dans
les variables d'environnement ml Wars, par
exemple, si une partie contenant des
variables d'environnement est définie et que vous devez en
utiliser une dans la configuration du pod
, vous pouvez y
accéder en utilisant un signe dollar à l'intérieur de votre
configuration jaune donc ceci est un
exemple d'un module de ma suite et ici la
même chose que je vous ai montrée avant voir
comment ils commentent et ici dans cette ligne
nous exécutons ma commande de suite
et j'accède à la
variable d'environnement qui est disponible à l'intérieur  le
pod utilisant le nom de la
variable environnementale et le signe dollar avant celui
qui, si vous en avez besoin, pourrait être
utile car je pense que ce
concept spécifique d'utilisation de variables environnementales
dans llamó n'est pas très bien documenté



#  placeholders

Gemmell a également un concept d'
espaces réservés un  de ses cas d'utilisation est dans l'
aide par exemple et voici à quoi cela
ressemble donc fondamentalement au lieu d'
écrire directement les valeurs à l'intérieur, vous
définissez des espaces réservés et th  La syntaxe pour l'
utilisation des espaces réservés est des accolades doubles
autour de cet espace réservé et cette
valeur est remplacée à l'aide du
générateur de modèles et je pense que le même concept
est également utilisé dans instable, donc encore une fois si
vous utilisez helm ou dans zville par exemple
et que vous voyez la syntaxe que vous devriez  sachez
ce que cela signifie



#  multiple yaml documents

et enfin à l'intérieur d'un fichier llamó, vous pouvez en
fait définir plusieurs composants et
vous pouvez séparer ces composants en utilisant
trois plats comme celui-ci, par exemple si
j'ai un fichier jaune où je veux mettre
toutes mes configurations, je peux les
séparer en utilisant  ces trois tirets et ce
sera un EML valide et cela peut être
très pratique dans le cas où vous avez
plusieurs composants peut-être pour un
service et que vous voulez les regrouper dans un
seul fichier jaune donc pour ce cas d'utilisation
c'est la voie à suivre



#  YAML and JSON in Kubernetes

peut-être que la remarque intéressante ici est que
dans toutes mes vidéos kubernetes, j'ai utilisé
le format jaune pour écrire
des fichiers de configuration kubernetes, mais vous pouvez également
écrire des commandes confi  fichiers de
guration au format JSON exemple si je me dirige vers mon
tableau de bord et que je clique pour modifier l'un de mes
composants je vois que j'ai à la fois les
formats llamo et Jason disponibles que je peux
modifier directement ou si je veux créer un
nouvel élément nouveau composant je  peut fournir du
jaune ou Jason, mais j'utilise personnellement le
jaune car, comme je l'ai mentionné, il est
plus propre et plus lisible, mais vous pouvez en
fait utiliser les deux, donc c'était tout pour la
vidéo du didacticiel Gemmell, merci d'avoir
regardé et à la prochaine vidéo