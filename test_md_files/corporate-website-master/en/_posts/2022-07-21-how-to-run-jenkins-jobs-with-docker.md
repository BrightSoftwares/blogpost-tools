---
author: full
categories:
- jenkins
date: 2022-07-21
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551313/pexels-arina-krasnikova-7726303_dhilhm.jpg
inspiration: https://stackoverflow.com/questions/47854463/docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socke
lang: en
layout: flexstart-blog-single
pretified: true
ref: how-to-run-jenkins-jobs-with-docker
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- jenkins
- docker
- taskrunner
title: How to run jenkins jobs with docker
toc: true
transcribed: false
---

I have successfully deployed my [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|jenkins]] instance and did a good [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|setup]] in my [[2022-08-31-a-complete-tutorial-about-jenkins-file|jenkins file]]. Now I am configuring it to [[2023-04-11-explore-your-container-with-docker-run|run]] my jobs.
My target is to have some task run [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|inside]] a [[2022-08-24-what-is-difference-between-docker-attach-and-exec|docker]] [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|container]].

I did the configurations but got this [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|error]] : [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|Docker]]: Got permission denied while trying to [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|connect]] to the [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|Docker]] daemon socket at unix:///var/run/[[2020-08-04-docker-tip-inspect-and-less|docker]].sock

I finally managed to solve it, here is how.

# My setup

I have the setup my [[2022-09-07-overview-on-jenkins|jenkins]] instance.
I configured a new job with below pipeline script.

```
node {
    stage('Build') {
      docker.image('maven:3.3.3').inside {
        sh 'mvn --version'
      }
    }
}
```


# The issue I am having

When I run the task, I got this error:

```
Docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

![Picture from Promise Preston https://stackoverflow.com/users/10907864/promise-preston](https://res.cloudinary.com/brightsoftwares/image/upload/v1656262514/brightsoftwares.com.blog/ijwgcwm6rkkaf1zpigwa.png)
# The solution

To solve that issue, I had to add my jekins user into the [[2020-08-04-docker-tip-inspect-and-grep|docker]] group to give it the permission to execute the [[2020-08-04-docker-tip-inspect-and-jq|docker]] commands.

```
sudo usermod -a -G docker jenkins
```

Then restart [[2023-05-17-how-can-i-make-jenkins-ci-with-git-trigger-on-pushes-to-master|Jenkins]].