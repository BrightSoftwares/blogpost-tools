---
author: full
categories:
- database
date: 2023-02-16
description: 'Lors de l''installation de mon site Web, j''ai besoin d''une base de
  données mysql pour stocker mes publications et ma configuration. Lors de la configuration,
  je rencontre soudainement une erreur étrange : le serveur mysql se plaint de problèmes
  d''authentification. Voici comment je l''ai résolu.'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1646322256/kyle-glenn-dGk-qYBk4OA-unsplash_irufoi.jpg
inspiration: https://stackoverflow.com/questions/2995054/access-denied-for-user-rootlocalhost-using-passwordno?noredirect=1&lq=1
lang: fr
layout: flexstart-blog-single
pretified: true
ref: 2022-03-03-how-to-solve-access-denied-for-user-root-localhost-using-password-no-unable-to-authenticate-php-mysql
tags:
- mysql
- windows
title: 'Comment résoudre Access denied for user root localhost using password : access
  denied for user root localhost using password'
---

Lors de l'installation de mon site Web, j'ai besoin d'une base de données mysql pour stocker mes publications et ma configuration. Lors de la configuration, je rencontre soudainement une erreur étrange : le serveur mysql se plaint de problèmes d'authentification. Voici comment je l'ai résolu.

# La réponse TL;DR

Exécutez cette commande :

```
mysql -u root -p
```

Lorsque vous êtes invité à saisir le mot de passe, **appuyez sur la touche Entrée** (laissez le mot de passe vide).


# Ma configuration

Je travaille sur une machine Windows. J'ai utilisé le `Web Platform Installer` pour avoir une pile de développement sur ma machine.
J'ai l'intention d'utiliser [[2020-04-04-how-to-install-wordpress-with-lamp-on-ubuntu-1604|Wordpress]] pour mon site Web.

***Remarque importante*** : Je n'ai jamais défini de mot de passe pour MySQL pendant le processus d'installation.

## Tentative de connexion sans mot de passe

Pour me connecter à la base de données, j'ai utilisé la commande suivante :

```
mysql -u root -p
```

Ensuite, il me demande un mot de passe que je n'ai pas. :(


## Tentative de connexion avec un mot de passe

J'ai essayé de me connecter en utilisant cette commande.

```
mysql -u root password '123'
```


Ensuite, il renvoie ceci:

```
Access denied for user 'root@localhost' (using password:NO)
```


# La solution

## Premièrement, j'ai fait une erreur

Il y a une erreur dans la commande que j'ai exécutée. Pour le mot de passe, vous devez utiliser `-p` ou `--password`.

Donc cette commande est fausse.

```
mysql -u root password '123'
```

La bonne commande est :

```
mysql -u root --password '123'
```


## Le mot de passe par défaut

Le mot de passe par défaut pour `root` pour l'installation est **`blank`**. Pas le mot littéral, mais "rien".


## Les étapes à résoudre

Connectez-vous au serveur MySQL avec un mot de passe vide.

Exécutez cette commande :

```
mysql -u root -p
```

Lorsque vous êtes invité à saisir le mot de passe, **appuyez sur la touche Entrée** (laissez le mot de passe vide).

Après cela, vous pouvez définir un mot de passe pour l'utilisateur "root".


# Conclusion

Pour résoudre le problème que vous rencontrez, vous devez d'abord :

 - vérifiez que votre commande est correcte.
 - connectez-vous au serveur MySQL avec un compte root et un mot de passe vide.
 - définir un mot de passe pour l'utilisateur root.