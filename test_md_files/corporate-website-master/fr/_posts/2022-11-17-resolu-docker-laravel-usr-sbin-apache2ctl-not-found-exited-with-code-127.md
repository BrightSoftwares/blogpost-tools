---
author: full
categories:
- laravel
date: 2022-11-17
description: 'J''ai récemment terminé un projet Laravel et j''ai fait un pas de plus
  pour l''empaqueter dans Docker. Dans le processus, j''ai rencontré un comportement
  étrange. L''outil docker-compose a lancé cette erreur /usr/sbin/apache2ctl,: not
  found sorti avec le code 127 sur moi. J''ai finalement réussi à le résoudre. Voici
  comment.'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1653595902/daniel-jensen-UDleHDOhBZ8-unsplash_prytio.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: solved-laravel-docker-usr-sbin-apache2ctl-not-found-exited-with-code-127
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: laravel debug
tags:
- docker
- laravel
- kubernetes
title: '[RESOLU] Docker Laravel /usr/sbin/apache2ctl,: not found exited with code
  127'
use_mermaid: true
---

J'ai récemment terminé un projet [[2022-11-10-resolu-l-image-du-docker-laravel-impossible-d-ouvrir-le-fichier-d-entree-var-www-html-artisan|Laravel]] et j'ai fait un pas de plus pour l'empaqueter dans Docker. Dans le processus, j'ai rencontré un comportement étrange. L'outil docker-compose a lancé cette erreur /usr/sbin/apache2ctl,: not found sorti avec le code 127 sur moi. J'ai finalement réussi à le résoudre. Voici comment.

Mon plan est de regrouper l'application Laravel dans une image Docker, puis de la réutiliser dans d'autres services. [[2022-05-26-7-easy-steps-to-deploy-a-laravel-application-in-a-docker-container|Je l'ai déjà fait]] et je suivais le même chemin.

Puis je suis tombé sur une erreur étrange.

Vérifions d'abord ma configuration, puis plongeons dans la solution.


## Configuration de mon application

J'ai une application simple que je souhaite regrouper dans docker. Il est utilisé sur le système d'exploitation Ubuntu.

Il a un dossier `docker/web` où le `Dockerfile` est stocké.

Le code source est dans le répertoire courant.

Voici le Dockerfile :

```
version : '3'

services:
  web: 
    container_name: laravel_web
    build:
      context: ./docker/web
    ports:
      - 9000:80
    volumes:
      - ./:/var/www/app
```


J'utilise ensuite ce Dockerfile dans mon fichier de composition.

Voici mon fichier `docker-compose.yml`.

```
FROM php:7.2.10-apache-stretch

RUN apt-get update -yqq && \
    apt-get install -y apt-utils zip unzip && \
    apt-get install -y nano && \
    apt-get install -y libzip-dev libpq-dev && \
    a2enmod rewrite && \
    docker-php-ext-install pdo_pgsql && \
    docker-php-ext-install pgsql && \
    docker-php-ext-configure zip --with-libzip && \
    docker-php-ext-install zip && \
    rm -rf /var/lib/apt/lists/*

RUN php -r "readfile('http://getcomposer.org/installer');"|php -- --install-dir=/usr/bin --filename=composer

COPY Default.conf /etc/apache2/sites-enabled/000-default.conf

WORKDIR /var/www/app

EXPOSE 80

CMD ['/usr/sbin/apache2ctl', '-D', 'FOREGROUND']
```

Ma configuration est maintenant terminée.

Voyons ce qui se passe quand je l'exécute.

## L'erreur à laquelle je suis confronté

Pour exécuter mon application, j'émets cette commande :

```
docker-compose up
```

Je m'attendais à ce que cela se passe bien mais j'obtiens cette erreur:

```
Starting laravel_web ... done
Attaching to laravel_web
laravel_web | /bin/sh: 1: [/usr/sbin/apache2ctl,: not found
laravel_web exited with code 127
```


J'ai d'abord pensé que apache2ctl n'était pas dans le système. J'ai regardé [ici](https://serverfault.com/questions/191180/what-does-apache2ctl-command-not-found-mean-if-apache-is-installed-and-runni) et [ici](https ://stackoverflow.com/questions/55108877/how-to-set-the-good-path-of-apache2ctl-in-sh-environemeent-of-docker) mais n'a pas pu trouver la cause première.

Ensuite, j'ai trouvé [ce message](https://stackoverflow.com/questions/53348044/docker-user-sbin-apache2ctl-not-found/53350884#53350884) qui m'a conduit à la solution.

## La solution

Vous devez utiliser des **guillemets doubles** au lieu de *guillemets simples* dans le `Dockerfile`.

Voici ce que vous devriez avoir :

```
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
```

## Conclusion

C'est drôle comme de petits détails peuvent casser tout un projet. J'ai été surpris par l'impact des guillemets doubles de version unique sur le projet. J'ai rencontré un autre problème venant d'un petit détail [[2022-05-31-solved-laravel-docker-image-could-not-open-input-file-var-www-html-artisan|here]] mais celui-ci est surprenant.

J'espère que cette solution a aidé.

Déposez un commentaire ci-dessous si vous avez des questions.