---
author: full
categories:
- code-server
date: 2022-01-02 20:26:15.073000+00:00
description: At the end of the installation of the code server, you are ready to enjoy
  your new development workflow, and then, you see this message "WebSocket close with
  status code 1006". How to solve this websocket 1006 error? Check out these answers
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1641156621/pexels-martijn-adegeest-633565_fcr6ri.jpg
lang: en
layout: flexstart-blog-single
ref: howtosolvecodeserverWebSocketclosewithstatuscode1006
seo:
  links:
  - https://www.wikidata.org/wiki/Q19841877
silot_terms: code server
tags:
- code-server
- code server
- websocket
- security
title: '[SOLVED] code server WebSocket close with status code 1006'
toc: true
---

At the end of the installation of the [[2022-12-07-how-to-solve-the-code-server-error-could-not-locate-the-bindings-file|code]] [[2022-12-07-how-to-solve-the-code-server-error-could-not-locate-the-bindings-file|server]], you are ready to enjoy your new [[2023-08-22-code-server-helm-chart-simplifying-cloud-development|development]] [[2023-08-11-how-to-optimize-your-workflow-with-kubernetes-code-server|workflow]], and then, you see this message "WebSocket close with status [[2023-08-27-code-server-railway-a-comprehensive-guide-for-developers|code]] 1006". How to solve it? Check out these answers

> Note: If you are confused about what code [[2023-11-13-port-forwarding-for-minecraft-server|server]] is, check [[2022-01-02-how-does-code-server-works|this post]] which explains it. 


## TL;DR

Check your ```https``` connection. Your browser cannot reach your code server instance.


## What is the websocket 1006 error?

The websocket 1006 error means that the connection has been closed, locally, by your browser.

If you see a close code 1006, you have a very low level error with WebSocket itself as this error is not really meant for the user. The websocket 1006 error points to  a low level issue with your code and implementation.


##  Why do I see this error?

The main reason is that the connection was closed abnormally (locally) by the browser implementation.

It means that your browser cannot reach your remote code server.
The main issue is about your ```https``` connection to the server.


## How to fix it?

> You might not be sure about the process to follow in order to setup code server. I did a tutorial on [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|how to setup code server cloud IDE platform on digitalocean using kubernetes]]. 

> If you speak french, the french version is [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes-fr|here]].



The good news is that, there are two possible solutions :

### Use the --link parameter to get a temporary https

#### Option 1 : get the link locally

```
code-server --host 127.0.0.1 --bind-addr 0.0.0.0:9000 --auth password --link
```
 

#### Option 2 : Use ngrok

ngrok will tunnel and create an https connection to your server.

```
code-server --host 127.0.0.1 --bind-addr 0.0.0.0:9000 --auth password ngrok http 9000
```

Use wss to forward

Here is the code to perform the forwarding and solve the issue

```javascript
// forward websocket (wss -> ws)
httpsServer.on('upgrade', function (req, socket, head) {
  proxy.ws(req, socket, head, {
    target: 'ws://...',
    ws: true
  })
})
```
 

You may get into a related type of issue where [[2022-01-02-how-does-code-server-works.md|code-server c]]omplains about the bindings file. The solution is in this [[2022-12-07-how-to-solve-the-code-server-error-could-not-locate-the-bindings-file| blog post about solving binding file not found error]].

Also, [[2023-04-04-work-with-kubernetes-with-minikube|kubernetes and minikube]] are great choices to host code server.