---
author: full
categories:
- jenkins
date: 2022-07-14
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551325/pexels-mododeolhar-5241772_toa7fn.jpg
inspiration: https://stackoverflow.com/questions/4764611/java-security-invalidalgorithmparameterexception-the-trustanchors-parameter-mus
lang: en
layout: flexstart-blog-single
pretified: true
ref: the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty
seo:
  links:
  - https://www.wikidata.org/wiki/Q456157
silot_terms: devops pipeline
tags:
- jekins
- hudson
- java
- jre
- jdk
- linux
- ubuntu
- aws
title: the trustAnchors parameter must be non-empty on Linux, or why is the default
  truststore empty
toc: true
transcribed: false
---

I am moving my configuration from a windows machine into an Amazon AWS EC2 instances which runs Linux.

The problem arises (in my case at least) when I try to [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] open a connection over SSL. It works fine on my windows machine, but when I deploy it to the linux machine (with sun's jre installed) it fails with the exception: 

```java.security.InvalidAlgorithmParameterException: the trustAnchors parameter must be non-empty```

The question is: why is this [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|failing]] on Linux and working on Windows?

Let's find out!

# My setup



## A windows server on which it works okay

On my windows machine, it works well. But on my linux machine, it fails with the above exception. 

## An AWS EC2 Linux instance

The linux instance is built from an Amazon AMI.
I have installed the java from Sun on it.




# What I have tried?

## Compare the truststores in Windows and Linux

The problem is that the default truststore of the JRE is empty for some reason (size of only 32 bytes, whereas it is 80kb on windows).

## Copied the cacerts from windows to Linux

When I copied my `jre/lib/security/cacerts` [[2022-08-31-a-complete-tutorial-about-jenkins-file|file]] from windows to linux, it worked fine.




# The solution

As I mentioned in a previous post about [[2022-07-07-trustanchors-parameter-must-be-non-empty#Copy the CACERTS from my windows to my Linux machine|trustanchors]], I needed in this case to update my cacerts.

I followed the steps on [this post](https://stackoverflow.com/questions/4764611/java-security-invalidalgorithmparameterexception-the-trustanchors-parameter-mus).

The idea is that the path [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|inside]] my ubuntu server ```/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/security/cacerts``` was a broken link to /etc/ssl/certs/java/cacerts. 

That lead me to this bug: [https://bugs.launchpad.net/ubuntu/+source/ca-certificates-java/+bug/983302](https://bugs.launchpad.net/ubuntu/+source/ca-certificates-java/+bug/983302) The README for ca-certificates-java eventually showed the actual fix:

[[2022-07-21-how-to-run-jenkins-jobs-with-docker|run]]

```
update-ca-certificates -f
```


Then [[2023-04-11-explore-your-container-with-docker-run|run]] this command:

```
apt-get install ca-certificates-java
```

But for my case, it didn't work. It just marked it as manually installed.




> *Note:* For those users who run `bazel` and come across this error message, just remember to set your $JAVA_HOME to the correct location. I had a previous situation with CATALINA_HOME in [[2022-07-07-trustanchors-parameter-must-be-non-empty|the post about trustanchors parameters]]. Check the solution out.