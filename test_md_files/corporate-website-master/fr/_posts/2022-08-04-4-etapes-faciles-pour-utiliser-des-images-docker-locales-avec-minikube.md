---
author: full
categories:
- kubernetes
date: 2022-08-04
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1656239922/pexels-oleksandr-pidvalnyi-325467_zawvug.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: howtouselocaldockerimageswithminikube
title: 4 étapes faciles pour utiliser des images docker locales avec Minikube
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

J'ai déjà partagé un court [[2020-08-13-work-with-kubernetes-with-minikube|tutoriel sur Minikube]], et pendant que je l'utilisais, j'ai pensé que je réutiliserais mes images locales directement, sans télécharger et puis les télécharger à nouveau.

## Deux choses que j'ai essayées (et qui n'ont pas fonctionné)

### Importez les images en utilisant ```kubectl```

J'ai d'abord nettoyé les instances de minikube et recommencé à zéro pour m'assurer qu'il n'y a pas de collision.


{% include codeHeader.html %}
{% raw %}
```
kubectl run hdfs --image=fluxcapacitor/hdfs:latest --port=8989
kubectl run hdfs --image=fluxcapacitor/hdfs:latest --port=8989 imagePullPolicy=Never
```
{% endraw %}

Et la sortie était :

{% include codeHeader.html %}
{% raw %}
```
NAME                    READY     STATUS              RESTARTS   AGE
hdfs-2425930030-q0sdl   0/1       ContainerCreating   0          10m
```
{% endraw %}

Comme vous le voyez, il reste bloqué sur un certain statut mais n'atteint jamais l'état prêt.


### Créer un registre local

L'idée ici est de créer un registre local et d'y mettre mes images. Avec cela, je n'ai pas besoin de télécharger puis de télécharger mes images.

Cela n'a pas fonctionné non plus.

## La solution

La solution consistait à utiliser le ```eval $(minikube docker-env)```.

Les étapes sont :

### Etape 1 : Définissez les variables d'environnement

Pour définir vos variables d'environnement, utilisez la commande :

{% include codeHeader.html %}
{% raw %}
```
eval $(minikube docker-env)
```
{% endraw %}


### Etape 2 : Construire l'image avec le démon de minikube

Pour construire l'image, utilisez cette commande :

{% include codeHeader.html %}
{% raw %}
```
docker build -t my-image
```
{% endraw %}

De la source, remplacez ```my-image``` par le nom de votre image.

### Étape 3 : Définir l'image dans le pod Kubernetes

Utilisez la balise dans le pod kubernetes.
Par exemple : ```my-image```


### Étape 4 : Dites à Kubernetes de ne plus télécharger l'image

Pour y parvenir, vous devez utiliser le ```imagePullPolicy``` à ```Never```.

Plus d'informations ici : [Comment définir imagePullPolicy sur jamais](https://kubernetes.io/docs/concepts/containers/images/#updating-images).


## Astuces et pillfalls

### Exécutez la commande env dans tous vos terminaux

Assurez-vous d'exécuter le ```eval $(minikube docker-env)``` dans tous vos terminaux. Vous aurez les variables d'environnement dans chacun d'eux.

Si ce n'est pas le cas, certaines commandes peuvent échouer en raison de l'absence de ces variables.

### Si vous fermez votre terminal, relancez eval $(minikube docker-env)

Une fois que vous fermez votre terminal, les variables d'environnement sont effacées.

Si vous construisez ensuite vos images, elles ne seront pas mises à jour dans minikube. Vous penserez que cela ne fonctionne pas, mais c'est parce que les variables d'environnement ne sont pas là.

### Quitter minikube ?

Si vous voulez quitter minikube, lancez cette commande :

{% include codeHeader.html %}
{% raw %}
```
eval $(minikube docker-env -u)
```
{% endraw %}


## Conclusion

Ce tutoriel vous montre comment vous pouvez utiliser votre image locale avec minikube sans les télécharger puis les télécharger.

Attention aux pièges.

Une fois que vous avez utilisé vos images locales, vous souhaiterez peut-être exposer les ports de services pour y accéder. [[2021-12-26-how-to-expose-a-port-on-minikube|Ce tutoriel]] vous montre comment.




## Références

[Ce fichier Lisezmoi](https://github.com/kubernetes/minikube/blob/0c616a6b42b28a1aab8397f5a9061f8ebbd9f3d9/README.md#reusing-the-docker-daemon)

[Cette publication sur stackoverflow](https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube)