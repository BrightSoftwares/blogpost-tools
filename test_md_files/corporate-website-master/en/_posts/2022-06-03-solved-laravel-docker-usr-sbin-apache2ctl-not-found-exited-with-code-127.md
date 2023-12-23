---
author: full
categories:
- laravel
date: 2022-06-03
description: 'I recently finished a Laravel project and I steped one more step to
  package it in docker. In the process I encountered a strange behaviour. The docker-compose
  tool threw this error /usr/sbin/apache2ctl,: not found exited with code 127 at me.
  I finally managed to solve it. Here is how.'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1653595902/daniel-jensen-UDleHDOhBZ8-unsplash_prytio.jpg
lang: en
layout: flexstart-blog-single
pretified: true
ref: solved-laravel-docker-usr-sbin-apache2ctl-not-found-exited-with-code-127
seo:
  links:
  - https://www.wikidata.org/wiki/Q15206305
  - https://www.wikidata.org/wiki/Q13634357
silot_terms: laravel debug
tags:
- docker
- laravel
- kubernetes
title: '[SOLVED] Laravel docker /usr/sbin/apache2ctl,: not found exited with code
  127'
toc: true
use_mermaid: true
---

I recently finished a [[2023-12-01-demystifying-the-pdoexception-sqlstate-hy000-2002-no-such-file-or-directory-in-laravel-development|Laravel]] project and I steped one more step to package it in docker. In the process I encountered a strange behaviour. The docker-compose tool threw this [[2023-11-15-error-target-class-controller-does-not-exist-when-using-laravel-8|error]] /usr/sbin/apache2ctl,: not found exited with code 127 at me. I finally managed to [[2023-09-05-how-to-solve-property-title-does-not-exist-on-this-collection-instance|solve]] it. Here is how.

My plan is to bundle the [[2023-08-23-how-to-solve-laravel-pdoexception-sqlstate-hy000-2002-no-such-file-or-directory|Laravel]] application into a docker image then resuse it in other services. [[2022-05-26-7-easy-steps-to-deploy-a-laravel-application-in-a-docker-container|I have done it before]] and I was following the same path.

Then I stumbled upon a strange error. 

Let's check my setup first and then dive into the solution.


## My application setup

I have a simple application that I want to bundle in docker. It is used on Ubuntu operating system.

It has a folder `docker/web` where the `Dockerfile` is stored.

The source code is in the current directory.

Here is the Dockerfile:

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


I then use this Dockerfile in my compose file.

Here is my `docker-compose.yml` file.

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

My setup is now complete.

Let's see what happens when I run it.

## The error I am facing

To run my application I issue this command:

```
docker-compose up
```

I was expecting this to run smoothly but I get this error:

```
Starting laravel_web ... done
Attaching to laravel_web
laravel_web | /bin/sh: 1: [/usr/sbin/apache2ctl,: not found
laravel_web exited with code 127
```


I first thought that the apache2ctl was not in the system. I looked [here](https://serverfault.com/questions/191180/what-does-apache2ctl-command-not-found-mean-if-apache-is-installed-and-runni) and [here](https://stackoverflow.com/questions/55108877/how-to-set-the-good-path-of-apache2ctl-in-sh-environemeent-of-docker) but couldn't [[2023-11-20-laravel-could-not-find-driver-reasons-and-solutions|find]] the root cause.

Then I found [this post](https://stackoverflow.com/questions/53348044/docker-user-sbin-apache2ctl-not-found/53350884#53350884) that led me to the solution.

## The solution

You must use **double quotes** instead of *single quotes* in the `Dockerfile`.

This is what you should have:

```
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
```

## Conclusion

It is funny how little details can break a whole project. I was surprised by the impact of single version double quotes on the project. I have encountered another issue coming from a little detail [[2022-05-31-solved-laravel-docker-image-could-not-open-input-file-var-www-html-artisan|here]] but this one is surprising.


If you're interested in learning how to solve the could not open input file issue in [[2023-10-30-laravel-migration-cannot-add-foreign-key-constraint|Laravel]] using docker image, our blog post on [[2022-05-31-solved-laravel-docker-image-could-not-open-input-file-var-www-html-artisan.md|could not open input file: artisan]] has everything you need to know.


I hope this solution helped. 

Drop a comment below if you have questions.