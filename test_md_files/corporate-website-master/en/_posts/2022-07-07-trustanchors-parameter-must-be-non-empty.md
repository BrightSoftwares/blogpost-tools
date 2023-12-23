---
author: full
categories:
- jenkins
date: 2022-07-07
description: I have successfully installed and made to work an Hudson installation
  on Windows machine. Now I am trying to move my installation to a Linux server. When
  I perform the installation and run it, gives me an error. Here is how I fixed it.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551331/pexels-pixabay-236164_wbyogu.jpg
inspiration: https://stackoverflow.com/questions/6784463/error-trustanchors-parameter-must-be-non-empty
lang: en
layout: flexstart-blog-single
pretified: true
ref: trustanchors-parameter-must-be-non-empty
seo:
  links:
  - https://www.wikidata.org/wiki/Q7491312
silot_terms: devops pipeline
tags:
- jenkins
- hudson
- java
- jdk
- jre
- linux
- ubuntu
title: TrustAnchors parameter must be non-empty
toc: true
transcribed: false
---

I have successfully installed and made to work an Hudson installation on Windows machine. Now I am trying to move my installation to a [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|Linux]] server.

When I perform the installation and [[2022-07-21-how-to-run-jenkins-jobs-with-docker|run]] it, gives me an [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|error]].

Here is how I fixed it.

# My setup

I have installed a Fedora Linux and a Java Sun on top of it (I am not using the Open JDK).

Then I installed [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|Jenkins]] on top of my Java Application.

But when I try it, I get this error:

```
java.security.InvalidAlgorithmParameterException: the trustAnchors parameter must be
    non-empty
```



# What I have tried to fix the issue

## Copy the CACERTS from my windows to my Linux machine

I followed the steps on [this post](https://stackoverflow.com/questions/4764611/java-security-invalidalgorithmparameterexception-the-trustanchors-parameter-mus).

The idea is that the path [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|inside]] my ubuntu server ```/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/security/cacerts``` was a broken link to /etc/ssl/certs/java/cacerts. 

That lead me to this bug: [https://bugs.launchpad.net/ubuntu/+source/ca-certificates-java/+bug/983302](https://bugs.launchpad.net/ubuntu/+source/ca-certificates-java/+bug/983302) The README for ca-certificates-java eventually showed the actual fix:

[[2023-04-11-explore-your-container-with-docker-run|run]]

```
update-ca-certificates -f
```


Then run this command:

```
apt-get install ca-certificates-java
```

But for my case, it didn't work. It just marked it as manually installed.



## Configure GMail as SMTP server

The steps for this attempt are in [this post.](http://g4j.sourceforge.net/faq.html)

My assumption was that the error was due to Java not trusting the certificate from GMail. 

**Newer version of JVM solve the problem**. Ruben Suarez provides a solution for those cannot upgrade.

To solve the problem, you must add Gmail's certificate to the default cacerts keystore.
Follow the details in the link above to implement this.


## Copy my cacerts from Windows into Java on my linux machine.

In this attempt, I downloaded the cacert files manually and move them over to my Java folder.

But that didn't solve my problem either.


# The solution

This bizarre message means that the trustStore you specified was:

1. empty,
2. not found, or
3. couldn't be opened (due to wrong/missing trustStorePassword, or [[2022-08-31-a-complete-tutorial-about-jenkins-file|file]] [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|access]] permissions, for example).

The point 2 (not found) was my problem. Let me explain.

My mistake was in the [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|environment]] variable ```CATALINA_HOME```.

In my setup, I use the ```${CATALINA_HOME}\conf```.
But in my environment variable, there was not the ```CATALINA_HOME``` so the setup ```${CATALINA_HOME}\conf``` was rendered as ```\conf``` which is not the correct path for the configuration.

# Conclusion

To fix this problem I had to create the ```${CATALINA_HOME}``` environment variable.

So one takeaway from this problem is that, when you install java, you better perform ALL the configurations **and test them** before you build on top of it.