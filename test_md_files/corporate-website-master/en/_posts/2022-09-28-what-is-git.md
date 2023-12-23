---
author: full
categories:
- git
date: 2022-09-28
description: Git is the most popular version control system in the world. A version
  control system records the changes made to our code over time in a special database
  called repository. We can look at our project history and see who has made what
  changes when and why. And if we screw something up we can easily revert our project
  back to an earlier state.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1661978960/pexels-christina-morillo-1181253_o4uh3s.jpg
lang: en
layout: flexstart-blog-single
post_date: 2022-09-28
pretified: true
ref: what-is-git
seo:
  links:
  - https://www.wikidata.org/wiki/Q7491312
silot_terms: devops pipeline
tags:
- git
- mercurial
- version control
- developer
- code
title: What is Git
toc: true
transcribed: true
youtube_video: https://www.youtube.com/watch?v=2ReR1YJrNOM
youtube_video_id: 2ReR1YJrNOM
---

So what is [[2023-05-17-how-can-i-make-jenkins-ci-with-git-trigger-on-pushes-to-master|git]] and why is it so popular? 

Git is the most popular version control system in the world. A version control system records the changes made to our code over time in a special [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|database]] called repository.

# What do we use git for?

We can look at our project history and see who has made what changes when and why.

And if we screw something up we can easily revert our project back to an earlier state.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661978244/brightsoftwares.com.blog/hw6aihd0khk1aluwxyew.png)

# Why do we need git?

Without a version control system we will have to constantly store copies of the entire project in various folders. This is very slow and doesn't scale at all especially if multiple people have
to work on the same project.

You would have to constantly toss around the latest code via email or some other mechanisms and then manually merge the changes.


In a nutshell, with a version control system we can track our project history and work together.


# Centralized vs distributed version control systems

Now version control systems fall into two categories:
- centralized and 
- distributed 


## Centralized version control systems

In a centralized system all team members [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|connect]] to a central server to get the latest copy of the code and to share their changes with others. Subversion and microsoft team foundation server (TFS) are examples of centralized version control systems.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661978328/brightsoftwares.com.blog/e0sfxn8vn17jtw3perjy.png)


The problem with the centralized architecture is the single point of failure. If the server goes offline we cannot collaborate or save snapshots of our project. So we have to wait until the server comes back online.


## Distributed version control systems

In distributed systems we don't have these problems every team member has a copy of the project with its history on their machine. We can save snapshots of our project locally on our machine. If the central server is offline we can synchronize our work directly with others.

Git and mercurial are examples of distributed version control systems.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661978354/brightsoftwares.com.blog/py9xnvazq8bka06yjmwv.png)

# Why is git so popular?

Out of all these git is the most popular version control system in the world because it's free open source super fast and scalable. Operations like branching and merging are slow and painful in other version control systems like subversion or TFS but they're very fast with git.


So git is almost everywhere more than 90% of software projects in the world [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] git. That's why almost every job description for a software developer mentions git.

So if you're looking for a job as a software developer git is one of the skills you must have on your resume. You should know it inside out you should know how it works and how to use it to
track your project history and collaborate with others effectively.