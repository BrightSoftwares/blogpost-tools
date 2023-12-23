---
author: full
categories:
- code-server
date: 2023-07-29
description: A la fin de l'installation du serveur de code, vous êtes prêt à profiter
  de votre nouveau workflow de développement, puis, vous voyez ce message WebSocket
  close with status code 1006. Comment le résoudre? Découvrez ces réponses
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1641156621/pexels-martijn-adegeest-633565_fcr6ri.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-29
pretified: true
ref: howtosolvecodeserverWebSocketclosewithstatuscode1006
tags:
- code-server
- code server
- websocket
- security
title: '[RESOLU] Le serveur de code WebSocket se ferme avec le code d''état 1006'
---

A la fin de l'installation du serveur de code, vous êtes prêt à profiter de votre nouveau workflow de développement, puis, vous voyez ce message "WebSocket close with status code 1006". Comment le résoudre? Découvrez ces réponses

> Remarque : Si vous ne savez pas ce qu'est le serveur de code, consultez [[2022-01-02-how-does-code-server-works|this post]] qui l'explique.


## TL;DR

Vérifiez votre connexion ```https```. Votre navigateur ne parvient pas à accéder à votre instance de serveur de code.


## Pourquoi cette erreur s'affiche-t-elle ?

La raison principale est que la connexion a été fermée anormalement (localement) par l'implémentation du navigateur.

Cela signifie que votre navigateur ne peut pas atteindre votre serveur de code distant.
Le principal problème concerne votre connexion ```https``` au serveur.


## Comment le réparer?

> Vous n'êtes peut-être pas sûr du processus à suivre pour configurer le serveur de code. J'ai fait un tutoriel sur [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|how to setup code server cloud IDE platform on digitalocean using kubernetes] ].

> Si vous parlez français, la version française est [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes-fr|ici]].



La bonne nouvelle, c'est qu'il y a deux solutions possibles :

### Utilisez le paramètre --link pour obtenir un https temporaire

#### Option 1 : obtenir le lien localement

```
code-server --host 127.0.0.1 --bind-addr 0.0.0.0:9000 --auth password --link
```
 

#### Option 2 : Utiliser ngrok

ngrok créera un tunnel et créera une connexion https à votre serveur.

```
code-server --host 127.0.0.1 --bind-addr 0.0.0.0:9000 --auth password ngrok http 9000
```

Utiliser wss pour transférer

Voici le code pour effectuer le transfert et résoudre le problème

```javascript
// forward websocket (wss -> ws)
httpsServer.on('upgrade', function (req, socket, head) {
  proxy.ws(req, socket, head, {
    target: 'ws://...',
    ws: true
  })
})
```