---
categories:
- code-server
date: 2022-12-07
description: There was a network issue during the installation and it broke it. When
  the installation broke down, the dependency spdlog was not present. I am using the
  Chrome web brower on Mac Os X Big Sur. My remote OS is a Free BSD 12.2, on UNIX.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551338/pexels-brent-olson-5185026_siumaq.jpg
inspiration: https://github.com/coder/code-server/issues/3665
lang: en
layout: flexstart-blog-single
pretified: true
ref: how-to-solve-the-code-server-error-could-not-locate-the-bindings-file
seo:
  links:
  - https://www.wikidata.org/wiki/Q19841877
silot_terms: code server
tags:
- code-server
- code server
- websocket
- security
title: How to solve the code-server Error Could not locate the bindings file
toc: true
transcribed: true
youtube_video: http://www.youtube.com/watch?v=HjyBzx23h98
youtube_video_description: bindingRedirect in an application configuration file (app.config)
  instructs .NET to probe for a new version of an assembly.
youtube_video_id: HjyBzx23h98
youtube_video_title: .NET Assembly Binding Redirect
---

## TL;DR

There was a network issue during the installation and it broke it.
When the installation broke down, the dependency ```spdlog``` was not present.

Running this :

```
# cd /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog
# yarn
```

then the binding file  `build/Release/spdlog.node` appears.


## My code-server configuration

I am using the Chrome web brower on Mac Os X Big Sur. 

My remote OS is a **Free BSD 12.2**, on UNIX.

When I run ```code-server --version``` I get the following answer:

```
3.10.2
```


## How did I endup with the bindings file issue?

First, I checked my bindings file with this command:

```
# echo check for bindings available
dev@devel:~ % echo 'console.log(require("bindings"))' | node
[Function: bindings] {
  getFileName: [Function: getFileName],
  getRoot: [Function: getRoot]
}
```

Then I start the [[2022-01-02-how-to-solve-code-server-websocket-close-with-status-code-1006|code]] [[2022-01-02-how-to-solve-code-server-websocket-close-with-status-code-1006|server]]:

```
code-server
```


And last step is to load the [[2023-08-27-code-server-railway-a-comprehensive-guide-for-developers|code]] [[2023-08-22-code-server-helm-chart-simplifying-cloud-development|server]] in my chrome browser.

I expected no errors ... but actually I got a long strack trace of it.

```
[2021-06-24T17:59:57.059Z] info  code-server 3.10.2 387b12ef4ca404ffd39d84834e1f0776e9e3c005
[2021-06-24T17:59:57.064Z] info  Using user-data-dir ~/.local/share/code-server
[2021-06-24T17:59:57.107Z] info  Using config file ~/.config/code-server/config.yaml
[2021-06-24T17:59:57.108Z] info  HTTP server listening on http://xx.xx.xx.xx:8080 
[2021-06-24T17:59:57.108Z] info    - Authentication is disabled 
[2021-06-24T17:59:57.108Z] info    - Not serving HTTPS 
Error: Could not locate the bindings file. Tried:
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/build/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/build/Debug/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/build/Release/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/out/Debug/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/Debug/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/out/Release/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/Release/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/build/default/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/compiled/14.16.1/freebsd/x64/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/addon-build/release/install-root/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/addon-build/debug/install-root/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/addon-build/default/install-root/spdlog.node
 → /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/lib/binding/node-v83-freebsd-x64/spdlog.node
    at bindings (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/bindings/bindings.js:126:9)
    at Object.<anonymous> (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/index.js:3:35)
    at Module._compile (internal/modules/cjs/loader.js:1063:30)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:1092:10)
    at Module.load (internal/modules/cjs/loader.js:928:32)
    at Function.Module._load (internal/modules/cjs/loader.js:769:14)
    at Module.require (internal/modules/cjs/loader.js:952:19)
    at require (internal/modules/cjs/helpers.js:88:18)
    at t (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:5:101)
    at r.load (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:4:1719)
    at r.load (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:3:10262)
    at l (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:5:10314)
    at Object.errorback (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:5:10435)
    at r.triggerErrorback (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:3:10626)
    at /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:3:10332
    at r.load (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:4:1736)
    at r.load (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:3:10262)
    at l (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:5:10314)
    at r._loadModule (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:5:10444)
    at r._resolve (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:6:452)
    at r.defineModule (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:5:6145)
    at r._relativeRequire (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:5:6831)
    at n (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/loader.js:5:9420)
    at v (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/server/entry.js:24:4531)
    at new Promise (<anonymous>)
    at b (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/server/entry.js:24:4511)
    at C._createSpdLogLogger (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/server/entry.js:24:5444)
    at new C (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/server/entry.js:24:5260)
    at Ae.initializeServices (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/server/entry.js:36:99964)
    at async Ae.initialize (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/server/entry.js:36:96951)
    at async process.<anonymous> (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/server/entry.js:36:103671) {
  tries: [
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/build/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/build/Debug/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/build/Release/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/out/Debug/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/Debug/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/out/Release/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/Release/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/build/default/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/compiled/14.16.1/freebsd/x64/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/addon-build/release/install-root/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/addon-build/debug/install-root/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/addon-build/default/install-root/spdlog.node',
    '/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog/lib/binding/node-v83-freebsd-x64/spdlog.node'
  ],
  phase: 'loading',
  moduleId: 'spdlog',
  neededBy: [ '===anonymous3===' ]
}
```


## Things I have tried to solve the bindlings file issue


### Check the node version and rebuild the project

I thought that my node version was not right. Then I went and check it.

My node version is ```14.16.1```.

Then I went ahead and delete the node_modules folder and reinstall everything.

```
rm -r node_modules
npm install
```

After some waiting, I stumbled upon this error.

```
/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/playwright/lib/utils/browserPaths.js:133
    throw new Error('Unsupported platform: ' + process.platform);
    ^

Error: Unsupported platform: freebsd
    at cacheDirectory (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/playwright/lib/utils/browserPaths.js:133:11)
    at /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/playwright/lib/utils/browserPaths.js:139:36
    at Object.<anonymous> (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/playwright/lib/utils/browserPaths.js:140:3)
    at Module._compile (internal/modules/cjs/loader.js:1063:30)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:1092:10)
    at Module.load (internal/modules/cjs/loader.js:928:32)
    at Function.Module._load (internal/modules/cjs/loader.js:769:14)
    at Module.require (internal/modules/cjs/loader.js:952:19)
    at require (internal/modules/cjs/helpers.js:88:18)
    at Object.<anonymous> (/stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/playwright/lib/install/installer.js:25:22)
```


Although I had that error, I started the [[2023-08-11-how-to-optimize-your-workflow-with-kubernetes-code-server|server]] again and tried to load the code-[[2023-11-13-port-forwarding-for-minecraft-server|server]].

```
code-server
```

I realized that some worker was consuming the whole CPU.

```
root@devel:~ # ps aux | grep node
user    31675 98.9  6.1 255768 61400  1  R+J  19:39   1:12.18 /stor/usr-local/bin/node /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/bootstrap-fork --type=extensionHost
root    31681  0.0  0.2  11332  2236  0  S+J  19:41   0:00.00 grep node
user    31666  0.0  4.4 248664 44848  1  S+J  19:39   0:01.16 node /usr/local/bin/code-server --auth none
user    31667  0.0  4.6 250300 46424  1  S+J  19:39   0:01.38 /stor/usr-local/bin/node /usr/local/bin/code-server --auth none
user    31672  0.0  6.2 267560 62708  1  S+J  19:39   0:03.52 /stor/usr-local/bin/node /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/vs/server/fork
user    31673  0.0  3.1 231204 31248  1  S+J  19:39   0:00.34 /stor/usr-local/bin/node /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/bootstrap-fork --type=ptyHost
user    31674  0.0  5.0 254472 50612  1  S+J  19:39   0:01.79 /stor/usr-local/bin/node /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/out/bootstrap-fork --type=watcherService
```


## Uninstall code-server and start from scratch

Before we get there, you may want to learn in details [[2022-01-02-how-does-code-server-works|how code-server works]].

At this step, I thought I could just erase everything and start over again. I thought there were one of two dependencies missing in my environment so I though reinstalling will solve them.

So I went ahead that remove code-server:

```
rm -rf ~/.local/share/code-server ~/.config/code-server
```

Then install everything using ```yarn```:

```
curl -fsSL https://code-server.dev/install.sh | sh -s -- --dry-run
```

After a few minutes of installation, I tried to load the code-server and it worked! ha!

I might admit I was a bit suprised.

So I tried to understand what happened in the previous installation.

It turned out that the dependency library `spdlog` was somehow not built. I go to `spdlog` and install (build):

```
# cd /stor/usr-local/share/.config/yarn/global/node_modules/code-server/lib/vscode/node_modules/spdlog
# yarn
```

and bindings file `build/Release/spdlog.node` appears

I suppose the reason was network error (or some else) that caused installation break. May be I did not notice and just run again setup. But why it does not rebuilt? - possible `yarn` algorithm consider `spdlog` as installed and does not check target files that must be built.

## Conclusion

This was a very instructive experience. I don't think I have seen that before: a network error that generate an installation and compilation issue, hence the failure of the application. Nice catch!

There is another tricky issue that you may encounter on the road to code-server. Explore [[2022-01-02-how-to-solve-code-server-websocket-close-with-status-code-1006| how to solve code-server websocket close with status code 1006]].

Also, to get a better understanding of [[2022-01-02-how-does-code-server-works.md|code-server install]]ation process, visit this blog post on [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|how to install code-server on digitalocean cloud]].