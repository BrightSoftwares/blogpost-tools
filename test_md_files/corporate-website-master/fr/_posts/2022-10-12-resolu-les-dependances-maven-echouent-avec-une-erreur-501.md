---
author: full
categories:
- jenkins
date: 2022-10-12
description: I have a jekins installation on my infrastructure. I found that recently
  my maven jobs are failing with an exception saying that they couldn'nt pull dependencies.
  Here is how I solved it.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1648104405/arkadiusz-gasiorowski-nvYIrRZAFgg-unsplash_eycjcv.jpg
inpiration: https://stackoverflow.com/questions/59763531/maven-dependencies-are-failing-with-a-501-error
lang: fr
layout: flexstart-blog-single
post_date: 2022-10-12
pretified: true
ref: how-to-solve-maven-dependencies-are-failing-with-a-501-error
title: '[RÉSOLU] Les dépendances Maven échouent avec une erreur 501'
seo:
  links: ["https://www.wikidata.org/wiki/Q139941", "https://www.wikidata.org/wiki/Q7491312"]
---

J'ai une installation jekins sur mon infrastructure. J'ai découvert que récemment mes travaux maven échouaient avec une exception indiquant qu'ils ne pouvaient pas extraire les dépendances. Voici comment je l'ai résolu.


## TL;DR

La réponse rapide est que je n'ai pas lu [l'avertissement de l'équipe maven](https://support.sonatype.com/hc/en-us/articles/360041287334) disant que HTTPS est maintenant requis.

> À compter du **15 janvier 2020** je reçois les réponses suivantes lorsque j'envoie des demandes au référentiel central :
>
Les requêtes à **http://repo1.maven.org/maven2/** renvoyent un statut 501 HTTPS Required et un corps :
>
501 HTTPS Obligatoire.
Utilisez https://repo1.maven.org/maven2/
Plus d'informations sur https://links.sonatype.com/central/501-https-required
>
Les requêtes à **http://repo.maven.apache.org/maven2/** renvoyent un statut 501 HTTPS Required et un corps :
>
501 HTTPS Obligatoire.
Utilisez https://repo.maven.apache.org/maven2/
Plus d'informations sur https://links.sonatype.com/central/501-https-required

J'aurais dû lire cet avis :p


## Ma configuration et l'erreur que j'avais, en détails

J'utilise **maven 3.6.0** sur **Ubuntu 18.04**.

Voici l'erreur que j'obtenais.

> [ERREUR] Extension de build non résoluble :
Le plugin `org.apache.maven.wagon:wagon-ssh:2.1` ou l'une de ses dépendances n'a pas pu être résolu :
Impossible de collecter les dépendances pour `org.apache.maven.wagon:wagon-ssh:jar:2.1 ()` :
Impossible de lire le descripteur d'artefact pour `org.apache.maven.wagon:wagon-ssh:jar:2.1` :
Impossible de transférer l'artefact `org.apache.maven.wagon:wagon-ssh:pom:2.1` de/vers central ([http://repo.maven.apache.org/maven2](http://repo.maven. apache.org/maven2)):
Échec du transfert du fichier : [http://repo.maven.apache.org/maven2/org/apache/maven/wagon/wagon-ssh/2.1/wagon-ssh-2.1.pom](http://repo.maven .apache.org/maven2/org/apache/maven/wagon/wagon-ssh/2.1/wagon-ssh-2.1.pom).
Le code de retour est : `501, ReasonPhrase:HTTPS Obligatoire. -> [Aide 2]`
>
En attente que _Jenkins_ finisse de collecter `data[ERROR]`
Le plugin `org.apache.maven.plugins:maven-clean-plugin:2.4.1` ou l'une de ses dépendances n'a pas pu être résolu :
Impossible de lire le descripteur d'artefact pour `org.apache.maven.plugins:maven-clean-plugin:jar:2.4.1` :
Impossible de transférer l'artefact `org.apache.maven.plugins:maven-clean-plugin:pom:2.4.1` de/vers central ([http://repo.maven.apache.org/maven2](http:// repo.maven.apache.org/maven2)):
Échec du transfert du fichier : [http://repo.maven.apache.org/maven2/org/apache/maven/plugins/maven-clean-plugin/2.4.1/maven-clean-plugin-2.4.1.pom] (http://repo.maven.apache.org/maven2/org/apache/maven/plugins/maven-clean-plugin/2.4.1/maven-clean-plugin-2.4.1.pom).
Le code de retour est : `501 , ReasonPhrase:HTTPS Obligatoire. -> [Aide 1]`


## La solution

Pour résoudre ce problème, j'ai effectué quelques remplacements des URL maven dans ma configuration.

Remplacez *http://repo1.maven.org/maven2* par *https://repo1.maven.org/maven2* (notez les http**s**)

Remplacez *http://repo.maven.apache.org/maven2* par *https://repo.maven.apache.org/maven2*


## Si vous ne pouvez pas utiliser https

Si vous ne pouvez pas utiliser la connexion sécurisée https, il existe un endpoint non sécurisé dédié que vous pouvez utiliser :

*http://insecure.repo1.maven.org/maven2*


## Réflexions finales

J'espère que cet article a aidé à résoudre votre problème sur les dépendances Maven qui échouent avec une erreur 501.