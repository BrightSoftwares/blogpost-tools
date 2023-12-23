---
author: full
categories:
- kubernetes
date: 2022-11-24
description: "Jetons un coup d'œil au réseau de pont intégré que vous obtenez sur tous les hôtes Docker basés sur Linux. Maintenant, ce réseau est à peu près équivalent au réseau NAT par défaut que vous obtenez avec docker sous Windows."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655109789/jerry-zhang-zemLpQqvJ-0-unsplash_bobi86.jpg
inspiration: https://stackoverflow.com/questions/33814696/how-to-connect-to-a-docker-container-from-outside-the-host-same-network-windo
lang: fr
layout: flexstart-blog-single
pretified: true
ref: how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host
title: "Comment connecter un conteneur Docker à l'extérieur de l'hôte ?"
transcribed: true
youtube_video: http://www.youtube.com/watch?v=Js_140tDlVI
youtube_video_description: This video demonstrates how to network containers on the
  same host using the bridge driver provided in Docker -- Docker is an ...
youtube_video_id: Js_140tDlVI
youtube_video_title: Bridge Networking for Single Host Container Networking
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

Jetons un coup d'œil au réseau de pont intégré que vous obtenez sur tous les hôtes Docker basés sur Linux. Maintenant, ce réseau est à peu près équivalent au réseau NAT par défaut que vous obtenez avec docker sous Windows.

## Ma configuration : Nouvelle installation sous Linux
Je suis connecté ici à un hôte docker fraîchement installé et à mon installation basée sur Linux. Ce sont les trois réseaux que j'obtiens par défaut.


### Réseaux par défaut


![Les réseaux par défaut sur une nouvelle installation de docker](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110158/brightsoftwares.com.blog/akmy5xdtqxb6ya9bm4d6.png)Celui-ci ici appelé pont en utilisant le pilote de pont ce est celui qui nous intéresse en ce moment : le réseau de ponts.



### Inspecter pour plus de détails

Maintenant, si nous voulons obtenir plus d'informations à ce sujet, nous pouvons lancer une commande d'inspection ici et nous lui donnons le nom du réseau et nous obtenons à peu près les mêmes informations qu'avant, avec un tas de plus également.

```
docker network inspect bridge
```


![Détails du réseau Docker sans conteneurs et passerelle par défaut](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110268/brightsoftwares.com.blog/iqgc7hho1xbrmimneqpd.png)

D'une part, nous pouvons voir le sous-réseau et la passerelle ici et nous pouvons voir où il
dit conteneurs nous n'en avons pas.


À l'heure actuelle, aucun conteneur n'est attaché à ce réseau, mais qu'est-ce qui sous-tend tout cela, comment tout cela fonctionne-t-il bien si nous lançons cela ici, nous pouvons le voir sur notre hôte docker.


## Comment fonctionne le réseau de ponts ?


Nous avons un commutateur virtuel ou un pont appelé ```docker0```. C'est ce qui constitue vraiment ce réseau appelé pont. Tout ce que nous avons à faire est d'y placer des conteneurs d'aplomb et, comme n'importe quelle couche pour changer de type, tous les conteneurs qui y sont branchés pourront
parler les uns aux autres maintenant parce que ces réseaux créés par le conducteur du pont.

![le réseau de pont docker0](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110392/brightsoftwares.com.blog/iawmrpbr0mimdpwkth3n.png)
Il est confiné à cet hôte docker ici sur lequel ont été connectés, car le pilote de pont concerne uniquement ```single host networking```, il crée donc des réseaux et des commutateurs isolés qui n'existent que dans un seul hôte docker.



### Comment voir le pont docker0

Pour voir réellement ce dock comme un pont zéro, nous devons installer le package d'utilitaires de pont Linux.

 ```
 sudo apt-get install bridge-utils
 ```


Maintenant, si nous allons ```brctl show``` il y a notre commutateur virtuel ```docker0```.


```
brctl show
```

Dans le langage natif de l'outillage, cela s'appelle un pont, mais ** un pont dans un commutateur est identique **.

Ici, nous pouvons voir qu'il n'y a pas d'interfaces qui s'y rattachent, c'est la cause
nous n'avons pas de conteneur.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110524/brightsoftwares.com.blog/bnbb58dqwfjvp6x10qf1.png)


### Ajouter un conteneur au réseau

Ajoutons-en une et juste une simple commande docker run :


```
docker run -it --rm alpine sh
```


Cette commande dit démarrer en tant que nouveau conteneur, basez-le sur l'image Alpine et déposez-nous dans un shell.

Remarquez ici que nous ne spécifions pas le réseau à rejoindre, donc par défaut. ** Si nous ne disons pas à un conteneur quel réseau rejoindre, il rejoindra ce réseau de pont **.
![Adresse IP du conteneur ponté](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110637/brightsoftwares.com.blog/gr5euqyql5izpsgeuzwd.png)
Nous sommes dans notre conteneur et voici l'IP de nos conteneurs. Nous n'avons rien à faire maintenant, alors laissons tomber ici, mais continuons à fonctionner.

Pour abandonner mais continuer à fonctionner, appuyez sur ```Ctrl P+Q```.


### Vérifiez maintenant que le docker0 ponté a un conteneur qui lui est attaché

Voyons s'il a fait ce que nous avions dit qu'il ferait, nous verrons pour rejoindre ce réseau de ponts. Exécutons à nouveau la commande inspect.

Nous avons un conteneur qui lui est attaché et il y a aussi son adresse IP.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110791/brightsoftwares.com.blog/i3u1qwaxpsqdurout5lw.png)


Si nous regardons à nouveau ce commutateur virtuel docker0, nous voyons comment une interface y est attachée maintenant que cette interface est intégrée dans notre conteneur.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1655110817/brightsoftwares.com.blog/dmhobxbz6iyvxm0ae2ak.png)



## Conclusion

Revenons en arrière et récapitulons. :)
Nous sommes sur une installation docker propre sur Linux, tous les réseaux que nous avons vus faisaient partie de cette installation par défaut, donc ce réseau de pont a été créé pour nous.

Il contient un seul commutateur virtuel appelé docker0.
Nous avons dit qu'il s'agit du réseau et du commutateur par défaut, ce qui signifie que si nous créons de nouveaux conteneurs et ne spécifions pas de réseau pour qu'ils se joignent, ils vont se connecter à ce commutateur docker0, faire partie de ce réseau de pont et parce que le réseau de pont est créé avec le pilote de pont, il s'agit d'un réseau hôte unique.