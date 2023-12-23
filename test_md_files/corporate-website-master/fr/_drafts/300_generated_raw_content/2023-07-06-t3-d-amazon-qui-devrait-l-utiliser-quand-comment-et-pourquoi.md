---
ToReview: true
author: full
categories:
- aws
date: 2023-07-06
description: T2 standard got vastly misunderstood due to its CPU throttling over baseline,
  to which Amazon introduced T2 unlimited – with a way to overcome the CPU throttling
  with a pay for credit mechanism for the period the EC2 ran over the baseline.
image: https://sergio.afanou.com/assets/images/image-midres-6.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-06
pretified: true
ref: aws_t3_usage
tags:
- aws
- ec2
- finops
title: T3 d'Amazon – Qui devrait l'utiliser, quand, comment et pourquoi ?
transcribed: true
youtube_video: http://www.youtube.com/watch?v=NlAauUzDmO0
youtube_video_description: 'Comment choisir ses jantes: diamètre, entraxe, alésage,
  déport, ET, offset ? Ca peut paraître compliqué de s''y retrouver dans tous ...'
youtube_video_id: NlAauUzDmO0
youtube_video_title: "\U0001F914  TOUT sur les JANTES: diamètre, entraxe, alésage,
  déport, ET, offset… \U0001F631  décodage"
---

# 

Salut à tous !
Bienvenue sur Garage Bagnoles et Rock’n Roll
Aujourd’hui on parle de jantes !
Une roue est composée d’une jante sur laquelle est monté un pneu.
On a déjà vu quelles étaient les caractéristiques des pneus
je vous met le lien vers la vidéo dans la description et en haut à droite ici.
Maintenant regardons de plus près ce qui caractérise une jante.
Tout d’abord c’est son diamètre: il est exprimé en pouces
et on retrouve cette indication sur le pneu après la lettre R
La largeur de la jante est aussi exprimée en pouces. En général entre 5 et 7 pouces.
En France on est sensé utiliser le système métrique, mais je ne sais pas pourquoi là on utilise les pouces
J’imagine que c’est comme pour les diagonales d’écrans: ça fait plus cool.
Ensuite ça va être le nombre de trous pour la fixer au moyeu: ici c’est 4 trous.
Les trous sont placés en cercle et le diamètre de ce cercle c’est l’entraxe.
Cet entraxe est exprimé en millimètres ou en pouces. En général en millimètres.
C’est un paramètre important quand vous achetez des nouvelles jantes.
Si ce n’est pas le bon entraxe vous ne pourrez pas monter vos roues sur la voiture.
Sur la spécification de votre jante sera noté le nombre de trous fois l’entraxe.
Par exemple sur les Renault c’est souvent 4 trous avec un entraxe de 100mm donc 4x100
Ensuite il y a l’alésage central: c’est le diamètre en millimètres du trou au centre de la jante.
Donc ces paramètres sont assez simple et avec juste un mètre vous pouvez les mesurer.
Maintenant il reste le dernier paramètre, le plus difficile à comprendre et à mesurer: le déport.
Et pour ça je vais avoir besoin d’un tableau blanc
et de mes cheveux.
Voici une roue vue en coupe
Ici la partie hachurée en rouge c’est la jante, en haut et en bas le pneu.
Ce côté ci est tourné vers l’extérieur et celui ci vers l’intérieur de la voiture.
Ici en vert c’est le moyeu de roue, là l’étrier de frein et en haut c’est le bord de l’aile.
Comment est mesuré le déport ?
C’est la distance entre la face intérieure de la jante là et l’axe qui passe par le milieu de sa largeur que je suis en train de dessiner ici.
et voilà notre déport
quand le déport est de ce côté-ci de l’axe vers l’extérieur
alors c’est une valeur positive
il y a des jantes avec des déports négatifs comme sur les roues jumelées des camions par exemple
Le déport est très important et lorsque vous achetez une nouvelle jante vous devez vous assurer que son déport correspond à celui des roues d’origine.
Si le déport est trop grand alors vous aurez la roue qui sera trop à l’intérieur
et elle risque de toucher la suspension ou l’étrier de frein.
Si le déport est trop petit la roue sera trop à l’extérieur et risque de toucher l’aile.
En plus elle ne sera plus dans l’axe du roulement et ça va user prématurément le roulement de roue.
Je vous rajoute le roulement de roue sur le schéma.
il se trouve ici
Dans l’idéal l’axe central de la roue doit passer par le centre du roulement pour bien répartir les forces.
Une tolérance de 5mm est admise et je vous conseille de privilégier 5mm en moins plutôt que 5mm en plus
Pourquoi ? Et bien tout simplement parce qu’il vaut mieux avoir une roue un petit peu plus à l’extérieur qu’à l’intérieur.
Par exemple si vos roues d’origine ont un déport de 55mm 
vous pourrez prendre des jantes avec un déport de 50mm
Ca élargira vos essieux et vous donnera un look « badass »
et ça ne risque pas de toucher vos suspensions ou vos étriers de frein.
il faut juste vérifier que ça passe bien sous l’aile
Alors comment trouver le déport sur vos roues ?
Je vous montre deux méthodes:
La première est très simple, il suffit de la lire directement sur la roue.
Et pour ça il faut démonter la roue !
alors je vais passer un coup de brosse sur tout ça
et là on a nos informations
ici on peut lire le diamètre
fois la largeur en pouces donc 15x
5 et demi
il y a une lettre après: « J » c’est la forme de la jante
et là c’est marqué offset 50
donc là c’est ce qui nous intéresse: c’est le déport
50mm
alors ici c’est marqué offset en anglais mais en général c’est marqué ET
attention à ne pas confondre avec l’entraxe
et pour vous souvenir c’est très simple ça vient de l’allemand:
EinpressTiefe
La deuxième méthode c’est au cas où vous ne trouvez aucune inscription dans votre jante
vous pouvez mesurer le déport
avec un bout de ficelle et un mètre
donc vous mesurez la largeur de la jante
prenez la moitié, vous y mettez
un fil à plomb
et ensuite vous mesurez
la distance entre la face intérieure et la ficelle
et là je trouve 50mm
je mesure l’alésage et j’ai à peu près 50mm
pour une mesure plus précise
je sors le centre
et comme ça de l’autre côté avec mon pied à coulisse
je peux mesurer l’alésage
et là j’ai 51mm
voilà. Si vous ne vous sentez pas de démonter votre roue
vous pouvez aussi trouver les spécifications de votre jante sur Internet
en donnant la marque, le modèle et l’année précise de votre voiture
je vous met un lien vers un site dans la description pour ça
Une fois qu’on a toutes ces mesures, on peut écrire précisément les spécifications de la jante
et pour celle-ci c’est:
15 pouces
4 fois 100
ET 50 50
donc diamètre de 15 pouces
4 trous avec un entraxe de 100mm
déport de 50mm
alésage de 50mm
pour le montage de vos pneus sur vos jantes
demandez à faire équilibrer les roues
ça consiste à ajouter des petites masses
à l’intérieur de la jante comme ici
et ça répartit la masse de la roue et du pneu de manière uniforme
pour éviter les vibrations
Dernier point: vos jantes doivent être homologuées pour votre véhicule.
En général il y a un document qui est livré avec les jantes neuves et il doit être conservé avec les papiers de la voiture
Voilà c’est tout pour aujourd’hui,
je vais pouvoir commander des jantes neuves pour l’Agila et y monter des pneus été.
[00:06:11.09]Je vais stocker ces roues
avec jantes d’origine montées avec des pneus neige et je les sortirai l’hiver prochain.
Si vous avez des questions mettez les dans les commentaires je m’efforcerai d’y répondre.
A la prochaine sur Garage, Bagnoles et Rock’n Roll !