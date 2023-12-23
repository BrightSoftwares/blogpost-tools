---
author: full
categories:
- jenkins
description: I have a jekins installation on my infrastructure. I found that recently
  my maven jobs are failing with an exception saying that they couldn'nt pull dependencies.
  Here is how I solved it.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1648104405/arkadiusz-gasiorowski-nvYIrRZAFgg-unsplash_eycjcv.jpg
inpiration: https://stackoverflow.com/questions/59763531/maven-dependencies-are-failing-with-a-501-error
lang: en
layout: flexstart-blog-single
ref: how-to-solve-maven-dependencies-are-failing-with-a-501-error
seo:
  links:
  - https://www.wikidata.org/wiki/Q7491312
silot_terms: devops pipeline
title: '[SOLVED] Maven dependencies are failing with a 501 error'
toc: true
---

I have a jekins installation on my infrastructure. I found that recently my maven [[2022-07-21-how-to-run-jenkins-jobs-with-docker|jobs]] are failing with an exception saying that they couldn'nt pull dependencies. Here is how I solved it.


## TL;DR

The quick answer is that I didn't read [the warning from maven team](https://support.sonatype.com/hc/en-us/articles/360041287334) saying that HTTPS is now required.

> As of **January 15, [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|2020]]** I am receiving the following responses upon making requests to The Central Repository:
>
Requests to **http://repo1.maven.org/maven2/** return a 501 HTTPS Required status and a body:
>
501 HTTPS Required. 
[[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|Use]] https://repo1.maven.org/maven2/
More information at https://links.sonatype.com/central/501-https-required
>
Requests to **http://repo.maven.apache.org/maven2/** return a 501 HTTPS Required status and a body:
>
501 HTTPS Required. 
Use https://repo.maven.apache.org/maven2/
More information at https://links.sonatype.com/central/501-https-required

I should have read that notice :p


## My configuration and the error I was having, in details

I am using **maven 3.6.0** on **Ubuntu 18.04**.

Here is the error I was getting.

> [ERROR] Unresolveable build extension:  
Plugin `org.apache.maven.wagon:wagon-ssh:2.1` or one of its dependencies could not be resolved:  
Failed to collect dependencies for `org.apache.maven.wagon:wagon-ssh:jar:2.1 ()`:  
Failed to read artifact descriptor for `org.apache.maven.wagon:wagon-ssh:jar:2.1`:  
Could not transfer artifact `org.apache.maven.wagon:wagon-ssh:pom:2.1` from/to central ([http://repo.maven.apache.org/maven2](http://repo.maven.apache.org/maven2)):  
Failed to transfer [[2022-08-31-a-complete-tutorial-about-jenkins-file|file]]: [http://repo.maven.apache.org/maven2/org/apache/maven/wagon/wagon-ssh/2.1/wagon-ssh-2.1.pom](http://repo.maven.apache.org/maven2/org/apache/maven/wagon/wagon-ssh/2.1/wagon-ssh-2.1.pom).  
Return code is: `501, ReasonPhrase:HTTPS Required. -> [Help 2]`
>
Waiting for _Jenkins_ to finish collecting `data[ERROR]`  
Plugin `org.apache.maven.plugins:maven-clean-plugin:2.4.1` or one of its dependencies could not be resolved:  
Failed to read artifact descriptor for `org.apache.maven.plugins:maven-clean-plugin:jar:2.4.1`:  
Could not transfer artifact `org.apache.maven.plugins:maven-clean-plugin:pom:2.4.1` from/to central ([http://repo.maven.apache.org/maven2](http://repo.maven.apache.org/maven2)):  
Failed to transfer file: [http://repo.maven.apache.org/maven2/org/apache/maven/plugins/maven-clean-plugin/2.4.1/maven-clean-plugin-2.4.1.pom](http://repo.maven.apache.org/maven2/org/apache/maven/plugins/maven-clean-plugin/2.4.1/maven-clean-plugin-2.4.1.pom).  
Return code is: `501 , ReasonPhrase:HTTPS Required. -> [Help 1]`


## The solution

To solve this problem, I did some replacements of the maven urls in my configuration.

Replace *http://repo1.maven.org/maven2* with *https://repo1.maven.org/maven2* (notice the http**s**)

Replace *http://repo.maven.apache.org/maven2* with *https://repo.maven.apache.org/maven2*


## In case you cannot use https

In case you cannot use the secure connection https, there is a dedicated insecure endpoint you can use :

*http://insecure.repo1.maven.org/maven2*


## Final thoughs

I hope this article helped solving your issue on Maven dependencies are failing with a 501 error.