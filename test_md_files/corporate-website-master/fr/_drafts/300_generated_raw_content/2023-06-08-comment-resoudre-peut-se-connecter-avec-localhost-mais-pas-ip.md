---
author: full
categories:
- kubernetes
date: 2023-06-08
description: 'J''ai hébergé un de mes sites web sur kubernetes et j''en suis content...
  sauf d''une chose : comment y accéder. Mon adresse IP locale est 10.0.0.21. Si j''utilise
  localhost ou 127.0.0.1, cela fonctionne. Mais si j''utilise mon adresse IP locale,
  je ne peux pas y accéder. Ca vous rappelle quelque chose? Voici comment le résoudre.'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1648310138/maria-teneva-2Wa88Py0h0A-unsplash_gwbtaf.jpg
inspiration: https://stackoverflow.com/questions/38175020/cant-access-localhost-via-ip-address
lang: fr
layout: flexstart-blog-single
post_date: 2023-06-08
pretified: true
ref: how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip
tags: []
title: Comment résoudre peut se connecter avec localhost mais pas IP?
transcribed: true
youtube_video: http://www.youtube.com/watch?v=4O-NjurMP6w
youtube_video_description: Common error faced by the most beginner VS code user. This
  can be perfect solution for those who are looking to solve localhost ...
youtube_video_id: 4O-NjurMP6w
youtube_video_title: localhost refused to connect | VS code error for HTML
---

# 

[Musique]
bonjour les gens j'espère que tout le monde va
bien
aujourd'hui je vais résoudre un
problème commun auquel chaque utilisateur de code de studio visuel
a été confronté
chaque apprenant qui fait la
programmation en html peut avoir rencontré un
problème lors de l'exécution et du débogage
j'espère que vous êtes assez familier  avec cette
image de temps en temps, vous avez peut-être rencontré
une erreur indiquant que l'hôte local a refusé de se
connecter ou une erreur d'hôte local,
ce que je voulais dire, c'est que votre fichier html ne s'ouvre peut-
être pas en
chrome.
l'un d'eux fonctionnera d'
abord, allez dans la section d'exécution et de débogage
,
vous verrez la section du bouton vert
appuyer sur cette zone et vous verrez la
section d'ajout de configuration, appuyez dessus et cela
vous amènera au lancement du fichier json
ici, vous pouvez voir un similaire  la configuration
vérifie d'abord le port de l'hôte local
pour moi, c'est 8 080. pour vérifier le
port localhost, cliquez sur ajouter la configuration
et cliquez sur lancer chrome,
puis vous pouvez voir l'adresse du port
[Musique]
enregistrer  et vérifiez puis exécutez le fichier
[Music]
si cela ne fonctionne toujours pas, copiez
tout du mien
mais n'oubliez pas de placer l'adresse du
fichier html principal que vous souhaitez exécuter
puisque mon fichier html principal est l'
index.html je mets le  adresse du
fichier index.html
puis enregistrez à nouveau et exécutez à nouveau
[Musique
] si cela ne fonctionne pas,
cette étape fonctionnera probablement,
allez dans le répertoire actuel dans lequel vous
travaillez
[Musique]
puis recherchez ce fichier puis supprimez-le
[Musique  ]
venez au code vs puis allez dans la même
section d'exécution et de débogage
[Musique]
puis cliquez dessus vous allez créer un
fichier launch.json
appuyez dessus et enregistrez-le maintenant vous êtes prêt
à partir
[Musique]
ou vous pouvez faire c'est vous  peut appuyer sur
l'option de mise en ligne dans le coin inférieur droit
merci beaucoup les gens si cela a aidé à
appuyer sur ce bouton comme
[Musique]
vous