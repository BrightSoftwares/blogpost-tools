---
author: full
categories:
- jenkins
date: 2022-07-27
description: Apache groovy is an object-oriented programming language used for the
  jvm platform. This  dynamic language has a lot of features drawing inspiration from
  python small talk and ruby. It can be used to orchestrate your pipeline in jenkins
  and it can glue different languages together, meaning that teams in your project
  can be contributing in different languages.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551341/pexels-mike-b-4168038_q4w0p1.jpg
inspiration: https://stackoverflow.com/questions/38276341/jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject
lang: en
layout: flexstart-blog-single
post_date: 2022-07-27
pretified: true
ref: jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject
seo:
  links:
  - https://www.wikidata.org/wiki/Q7491312
silot_terms: devops pipeline
tags:
- pipeline
- plugins
- groovy
title: Jenkins CI Pipeline Scripts not permitted to use method groovy.lang.GroovyObject
toc: true
transcribed: true
youtube_video: http://www.youtube.com/watch?v=3g1DX_0VXyw
youtube_video_description: 'Edureka DevOps Training: https://www.edureka.co/devops-certification-training/
  This Edureka "Jenkins Groovy Tutorial" gives you ...'
youtube_video_id: 3g1DX_0VXyw
youtube_video_title: Jenkins Groovy Tutorial For Beginners | Jenkins Pipeline Tutorial
  | DevOps Training | Edureka
---

Apache groovy is an object-oriented programming language used for the jvm platform. This  dynamic language has a lot of features drawing inspiration from python small talk and ruby.

It can be used to orchestrate your pipeline in [[2022-07-21-how-to-run-jenkins-jobs-with-docker|jenkins]] and it can glue different languages together, meaning that teams in your project can be contributing in different languages.


Before we begin I would like to address the agenda firstly we will understand what is a [[2022-09-07-overview-on-jenkins|jenkins]] pipeline and then we'll discuss the various methods to create a pipeline.

Then we'll understand why we need to use the [[2022-08-31-a-complete-tutorial-about-jenkins-file|jenkins]] pipeline plug-in.

Then we will also talk about the types, of [[2023-05-17-how-can-i-make-jenkins-ci-with-git-trigger-on-pushes-to-master|jenkins]] pipeline that are available and then we'll compare declarative pipeline versus scripted pipeline.

And finally we will understand how to create pipeline using groovy scripts.

So without much ado let's get started !



# What is a Jenkins Pipeline?

In jenkins a jenkins pipeline (or you can simply refer it to as pipeline) is a collection of events or jobs which are basically interlinked with one another in a sequence. It is a combination of plugins that support the integration and implementation of continuous delivery pipelines using jenkins.


The events and jobs that I am talking about is the sequence of events that can happen or occur in a software organization to deliver a particular application. In other words, a jenkins pipeline is a collection of jobs that brings the software from version control into the hands of the end users by using automation tools.


It is used to incorporate continuous delivery in our software [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|development]] workflow.


Now in a jenkins pipeline every job has some sort of dependency on at least one or more jobs or events.


So basically, in a continuous delivery pipeline in jenkins it contains a collection of various states such as build deploy test release etc. These jobs that I am talking about are interlinked with each other.

Every state has its jobs which work in a sequence called a continuous delivery pipeline.


For all of you all who don't know what a continuous delivery pipeline is it is basically an automated expression to show your process for getting software for version control. Thus every change made in your software goes to a number of complex processes in its manner to be released.

It also involves developing the software in a repeatable and reliable manner and progression of
the build software through multiple stages of testing and deployment.


That we know what is a jenkins pipeline let us understand the methods to create a pipeline.


# Methods to create a Pipeline


There are two methods :
- the first method is using the build pipeline plugin
- okay so now


## Create a jenkins pipeline using a plugin

There are various plugins that jenkins offers. The hundreds of plugins that jenkins offers and one of the plug-in that we can use to create a pipeline is the build pipeline plugin.


Continuous integration can become the center piece of your deployment pipeline orchestrating the promotion of a version of software to quality gates and into production.
By extending the concepts of continuous integration you can create a chain of jobs each one
subjecting your build to quality assurance steps.


You can see that you have job one is version control job tools build job three as unit tests so the various jobs that you build to create your pipeline.


These quality assurance steps may be a combination of manual and automated steps. Once a bill is passed all of these it can be automatically deployed into production that is your final step. In order to better support this process you can use the build pipeline plugin.


This basically gives you the ability to form a chain of jobs based on their upstream or downstream [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|dependencies]].


Downstream jobs may as per the [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|default]] behaviors be triggered automatically or by a suitable authorized [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|user]] manually triggering it. The next way to create your pipeline is by using pipeline plugin. This plugin is extremely important. The jenkins pipeline can be defined by a text file which is called as jenkins file.


So what really happens here is you just create one job with all of these stages together. All of these stages interlink together so the stages are version control build unit test deploy autotest etc.


What really happens is you can implement this entire pipeline as code okay so that's the [[2022-08-24-what-is-difference-between-docker-attach-and-exec|difference]] between the build pipeline plugin and the pipeline plugin.

Here you can implement this pipeline as code and this happens with the help of the
jenkins file. Also this is defined by using a DSL (**Domain Specific Language**). With the help of jenkins files you can write the steps required for running this entire jenkins pipeline.


You must be wondering what are the benefits of using this jenkins files.


So the first biggest benefit is that you can make pipelines automatically for all branches
and then execute pull requests with just one jenkins file.

You don't really have to treat all of these jobs separately so you can review your jenkins pipeline and the code that is present.


This is the singular source for your pipeline and can be customized by multiple users.


Jenkins file can be defined by using either : 
- web user interface or 
- a jenkins file


As we've already discussed jenkins is a continuous integration server which has the ability to support the automation of software development processes.


You can create several automation jobs with the help of use cases and [[2023-04-11-explore-your-container-with-docker-run|run]] them as a jenkins
pipeline we know this already. So i wrote about some of the benefits of using jenkins file.


# Jenkins pipeline can resume from checkpoints after reboot


Jenkins pipeline is implemented as a code which allows several users to edit and execute the pipeline process and the pipelines are very robust.

If your server undergoes and very unpredicted restart the pipeline will be automatically resumed from where you left off. You can also pause the pipeline process and make it wait to continue 
 until there is an input from the particular user.


Also jenkins pipelines support big projects you can also run many jobs and even use pipelines in a loop. 


Now that we've learned the different methods to create a pipeline let's talk about as to why we can use jenkins pipeline.


# Why use Jenkins Pipeline?


The highlight of jenkins pipeline is that it offers the feature to define the complete deployment flow through configuration and code.


It states that all the standard jenkins jobs can be written manually as an entire script and can also be managed with the version control system. This is a great advantage for people on the developer side.


Now it's essentially following the discipline of pipeline as code.


Hence instead of creating multiple jobs for each process it allows us to code the entire workflow and place it simply in a jenkins file. Some of the reasons that one might consider before using the jenkin pipelines for jenkins test automation with selenium is because it allows you to use groovy DSL (Domain Specific Language) and it helps model easy to complex pipelines is code.


As I have already mentioned the code is stored in the form of a text file which is called jenkins files that can be scanned into source code management.


It also supports complex pipelines by adding conditional loops forks or joining operations and allowing parallel execution tasks. It also improves user experience by integrating user feedback into the pipeline.


It's resilient in terms of jenkins master unplanned restart and as already mentioned it can resume from checkpoints saved. Also as we already know as to why jenkins is famous that is because of its plugins it can incorporate multiple additional plugins and add-ins.


Now that we know as to why we should use jenkins pipeline let's move on and check out the  types of jenkins pipeline that are available.


# Types of Jenkins Pipeline


There are two different types in which jenkins pipeline can be constructed : 
- the declarative pipeline
- the scripted pipeline 


## The jenkins declarative pipeline

The declarative pipeline is relatively a very new feature that supports the concept of code pipeline. It basically enables the reading and writing of the pipeline code.


This code is written within a jenkins file which can be tested into a tool such as get for source control. 


## The scriped pipeline

The scripted pipeline on the other hand is a typical method of code writing now the jenkins file is written on the jenkins user interface instance in this particular pipeline. 


While both of these pipelines are groovy based the scripted pipeline uses more strict groovy base syntaxes  and this is because it was the first groovy foundation pipeline that was created for use.


As this groovy script was not usually suitable to all the users it introduced the declarative pipeline to provide a much more simpler and flexible groovy syntax.


The declarative pipeline is defined within a pipeline block while the scripted pipeline is defined within a node block.  The declarative pipeline is defined in a pipeline block while the scripted one is defined within a node block.

As I have already mentioned before the scripted pipeline is a groovy based DSL and it provides greater flexibility and scalability for jenkins users than the declarative one. 

So groovy script are not necessarily suitable for all their users so the declarative pipeline syntax is much more stringent. It needs to use jenkins predefined DSL structure which provides a much more simpler and much more assertive syntax for writing jenkins pipeline.


Now that we've discussed the types of jenkins pipeline let's move ahead and check out the differences between declarative and scripted pipeline.


# Declarative vs Scripted


The difference between declarative pipeline and scripted pipeline would definitely be with respect to their syntaxes and their flexibility.


The declarative pipeline is relatively a new feature that supports the pipeline is code concept.


as I have already mentioned before it makes the pipeline code easier to read and write, whereas the scripted one is a traditional way of writing the code in this pipeline the jenkins file is written on the jenkins UI instance. 

Let's move ahead and check out the first difference between them that is the syntax.


## The syntax difference between declarative and scripted pipeline

The declarative one offers a much more simpler and much more optioned groovy syntax while the script pipeline uses a much stricter groovy based syntax.


## The flexibility difference between declarative and scripted pipeline


The next difference is based on the flexibility. The declarative pipeline is much more easier to read and write whereas the scripted one has a traditional way of writing the code.

In terms of programming model declarative pipeline encourages a declarative programming model whereas scripted pipelines follows a more imperative programming model.


## The structure of the declarative vs scripted pipeline

Moving on to the structure the declarative type imposes limitations to the user with a much 
more strict and predefined structure which would be very ideal for simpler continuous delivery pipelines. On the other hand the scripted type has very few limitations that too with respect to structure and syntax that tend to be defined by groovy.


Thus making it ideal for users with more complex requirements now that we've discussed the differences between declarative and scripted pipelines.


# Conclusion

Which method do you use to create the pipeline in jenkins? Scripted? Declarative? What are your tips? Let us know in the comments section.