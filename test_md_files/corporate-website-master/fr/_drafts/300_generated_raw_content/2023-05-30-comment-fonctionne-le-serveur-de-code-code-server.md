---
Aliases:
- code-server
- code server
author: full
categories:
- code-server
date: 2023-05-30
description: Imaginez que Visual Studio Code s'exécute dans un navigateur Web. C'est
  le serveur de code. Il vous permet de coder dès que vous disposez d'une connexion
  internet et d'un navigateur. Vous pouvez travailler sur n'importe quel appareil
  tel qu'une tablette ou un ordinateur portable avec un environnement de développement
  intégré (IDE) cohérent. Configurez une machine de développement Linux sécurisée
  et codez sur n'importe quel appareil doté d'un navigateur Web.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1641154407/pexels-mateusz-dach-914929_sopots.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-05-30
pretified: true
ref: howdoescodeserverworks
tags:
- code-server
- visual-studio-code
- installation
- linux
- nginx
- coder
- devops
- ci-cd
title: Comment fonctionne le serveur de code code-server?
transcribed: true
use_mermaid: true
youtube_video: http://www.youtube.com/watch?v=oXvNYHgsX0g
youtube_video_description: 7 astuces pour finir plus vite sa journée ...
youtube_video_id: oXvNYHgsX0g
youtube_video_title: Comment gagner en productivité avec l&#39;extension Live Server
  sur VSCode ?
---

# 

salut à tous dans cette vidéo on va voir
une extension visual studio code qui va
vous permettre de générer un petit
serveur sur votre machine et du coup
vous allez pouvoir dupliquer ou voire
quadrupler votre productivité
quand vous développez en javascript
alors comme je voulais dit on va
télécharger aujourd'hui donc une
extension sur visual studio code
donc si vous ne connaissez pas ce
logiciel ou que vous ne l'utilisez pas
vous passer vraiment à côté de quelque
chose
c'est un petit éditeur de texte un petit
c'est s'est très rapidement dit bref
c'est un éditeur de texte qui est assez
puissant puisque il vous fournit en fait
vous allez avoir une très grosse
communauté qui va être derrière ce
logiciel et en plus de ça vous allez
avoir beaucoup beaucoup de plugins qui
sont super intéressant et surtout qu'ils
sont très bien adaptés pour ce type de
logiciel ils sont faciles à installer
c'est facile d'utilisation la plupart du
temps et on va voir donc dans cette
extension là une extension en
particulier qui s'appelle live serveur
qui va vous permettre de générer des
petits serveurs sur votre machine et du
coup vous allez pouvoir donc développé
en java script plus rapidement donc ce
que je veux faire c'est que moi dans
visual studio code sur le panneau de
gauche vous allez avoir un petit bouton
extension vous cliquez dessus et alors
moi j'ai déjà plusieurs extensions qui
sont déjà installés et vous allez
rechercher live serveurs on recherche
lac serveurs et vous allez donc cliquer
sur la première extension qui vient donc
c'est une extension avec cette petite
icône la de diffusion d'onde et vous
allez cliquer sur installer une fois que
vous avez installé live serveur il
faudra recharger votre configuration de
visual studio code donc vous cliquez sur
recharge est donc là ça va relancer le
logiciel et une fois que s'installer ben
vous avez tout simplement visual studio
code d'installer sur votre logiciel
donc maintenant on peut quitter les
extensions et allez dans votre
arborescence de fichiers est ce qu'il
faut savoir c'est qu'il faut donc ouvrir
un dossier avant enfin pour que live
serveurs puisse fonctionner donc il faut
bien ouvrir un fichier pour ça vous
allez un dossier pardon vous allez faire
ficher ouvrir un dossier
et là vous allez sexuée sélectionner le
dossier qui corresponde à votre projet
est ce qu'on va faire donc c'est qu'on
va créer donc de fichier un fichier
index point html et un fixé à un fichier
apb point j s évidemment on pourrait
créer plusieurs fichiers point js
compris inclure dans notre index
fra.html mais pour le moment nous va
utiliser qu'un seul fichier js donc je
crée un nouveau fichier qui va s'appeler
index
point html html hockey et je vais en
créer un autre il y as ap ap pointe js
dans mon fichier index e.html j'ai créé
un petit à petit comment dire un bel
scott de 2 html je vais écrire et si mon
application tac je vais enlever la
feuille de style qui ne met pas utile et
je vais changer le script qui n'est plus
mais le point g a semé à pépé pour 1 js
j'enregistre et là tout simplement donc
je vais avoir donc mon fichier index
point html et mon fichier apb point j s
à partir de là normalement vous devriez
avoir une petite comment dire une un
petit bouton qui s'appelle open with
love serveurs alors là il n'apparaît pas
c'est parce que très probablement sa du
mal recharger mon extension alors je
vais regarder si elle est bien installé
live serveurs tac
alors est ce que c'est bien d'installer
ouais c'est bien installés alors je
crois que ma configuration n'a pas été
bien relancé
ou sinon en faisant alors voilà
simplement en fermant et en réouvrant
votre logiciel normalement vous devriez
voir en bas à droite ici un petit bouton
qui s'appelle go live il est marqué go
live donc en gros c'est quand vous êtes
dans un projet vous allez pouvoir faire
go live dans un projet en général mais
la plupart du temps ce que je fais
personnellement c'est que si j'ai
plusieurs fichiers pour html par exemple
mais je vais sélectionner un fichier
pour html je faire clic droit et je vais
avoir le bouton open with life serveurs
je clique dessus
là ça va lancer justement live serveur
est tout simplement ça lance mon live
serveurs alors là on le voit que ça ne
démarre donc sur ma propre ip sur le
port 5500 et maintenant si je vais dans
mon à pépé point g est ce que je mets un
petit con seul point log de hello world
et que je vais dans ma console ici dans
mon navigateur j'ai bien hello world et
ce qui est assez intéressant c'est que
sans même enregistré un fichier ça va
automatiquement recharger ma page
donc là ici si par exemple je mets un
petit achat avec un petit coucou tac
j'enregistre donc là ça me relance ma
page ici je vais non non à pépé point g
est par exemple éclats je rajoute un
petit con seulement log et que je mets
et le world deux là je n'ai pas
enregistré est automatiquement ça va le
relancer donc là ça a détecté un
changement ça va relancer votre page
et là c'est très pratique puisque
lorsque vous développez en général avec
javascript c'est assez rapide le
développement parce qu'on fait de
l'algorithme et où des petites thèse des
conditions etc
c'est super pratique puisque vous pouvez
voir en temps réel le résultat que vous
allez avoir donc quand je développe la
plupart de mes petits projets avec
canvas
ou alors que j'ai un petit peu
d'algorithmes et bref des petits codes
des petits bouts de code comme ça que je
veux tester quelque chose
liles et rvr c'est vraiment l'extension
qui est belle la plus excellentes qui va
vous permettre vraiment de gagner en
productivité
donc si ce genre de vidéos sur des
extensions particulière sur ce visage
qui de code vous plaît n'hésitez pas à
me le faire savoir donc en commentaire
si vous êtes intéressé par javascript et
la technologie bien sûr de javascript en
général vous pouvez rejoindre le club
d'uzès master qui est en lien en
descriptions et on se retrouve dans une
prochaine vidéo très bientôt à la
prochaine