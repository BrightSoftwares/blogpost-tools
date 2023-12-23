---
author: full
categories:
- jenkins
date: 2022-09-07
description: 'Today we are going to deep dive into that jenkins is and how it improves
  your devops continuous integration environments. We are going to cover what life
  is like before using jenkins and the issues that jenkins specifically addresses.
  Then we will get into what jenkins is about and how it applies to continuous integration
  and the other continuous integration tools that you need in your devops team. '
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551325/pexels-bryce-carithers-9031693_eg7h1o.jpg
lang: en
layout: flexstart-blog-single
post_date: 2022-09-07
pretified: true
ref: overview-on-jenkins
seo:
  links:
  - https://www.wikidata.org/wiki/Q7491312
silot_terms: devops pipeline
tags:
- devops
- jenkins
title: Overview on jenkins
toc: true
transcribed: true
youtube_video: https://www.youtube.com/watch?v=LFDrDnKPOTg&ab_channel=Simplilearn
youtube_video_id: LFDrDnKPOTg
---

Today we are going to deep dive into that [[2022-07-21-how-to-run-jenkins-jobs-with-docker|jenkins]] is and how it improves your devops continuous integration environments.


We are going to cover what life is like before using [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|jenkins]] and the issues that [[2022-08-31-a-complete-tutorial-about-jenkins-file|jenkins]] specifically addresses. Then we will get into what [[2023-05-17-how-can-i-make-jenkins-ci-with-git-trigger-on-pushes-to-master|jenkins]] is about and how it applies to continuous integration and the other continuous integration tools that you need in your devops team. 


Then specifically we will deep dive into features of jenkins and the jenkins architecture and we will give you a case study of a company that's using jenkins.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661895465/brightsoftwares.com.blog/jgbxwamr3xeznxs2xmdr.png)
# How thingd worked before jenkins

Today to actually transform how their it organization is operating. Let's talk a little bit about life before jenkins. Let's see this scenario I think it's something that maybe all of you can relate to. As developers we all write code and we all submit that code into a code repository and we all keep working away writing our unit tests and hopefully we are running our unit tests.

But the problem is that the actual commits that actually gets sent to the code repository aren't consistent you as a developer may be based in india. You may have another developer that's based in the philippines and you may have another team lead that's based in the UK and another [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|development]] team that's based in north america.

So you are all working at different times and you have different amounts of code going into the code repository there's issues with the integration and you are kind of running into a situation that we like to call development hell where things just aren't working out and there's just lots
of delays being added into the project and the bugs just keep mounting up.


The bottom line is the project is delayed and in the past what we would have to do is we'd have to wait until the entire software code was built and tested before we could even begin checking for errors and this just really kind of increased the amount of problems that you'd have in your project.

The actual process of delivering software was slow there was no way that you could actually iterate on your software and you just ended up with just a big headache with teams pointing fingers at each other and blaming each other.

So let's jump into jenkins and see what jenkins is and how it can address these problems.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661895773/brightsoftwares.com.blog/e1lrfqfswi43ocmpx7vz.png)



# What is jenkins?

Jenkins is a product that comes out of the concept of continuous integration that you may have heard of as [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|power]] developers where you'd have two developers sitting next to each other
coding against the same piece of information. What they were able to do is to continuously develop their code and test their code and move on to new sections of code. 

Jenkins is a product that allows you to expand on that capacity to your entire team so you are able to submit your codes consistently into a source code environment. So there are two [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|ways]] in which you can do continuous delivery.

One is through 90 builds and one is through continuous. 


So the approach that you can look at continuous delivery is modifying the legacy approach to building out solutions. So what we used to do is we would wait for nightly builds and the way that our nightly builds would work and operate is that as co-developers we would all [[2023-04-11-explore-your-container-with-docker-run|run]] and have a cut-off time at the end of the day and that was consistent around the world that we
would put our codes into a single repository and at night all of that code would be run and operated and tested to see if there were any changes and a new build would be created and that would be referred to as the nightly build.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661895978/brightsoftwares.com.blog/tlyarg93iuxcplvmkzof.png)


# What is continuous integration?

With continuous integration we are able to go one step further. We are able to not only commit our changes into our source code but we can actually do this continuously there's no need to race and have a team get all of that code in an arbitrary time you can actually do a continuous
release because what you are doing is you are putting your tests and your verification services into the build environment so you are always running cycles to test against your code.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661897032/brightsoftwares.com.blog/swr97bnvdiwo7n56d72f.png)




This is the power that jenkins provides in continuous integration. So let's dig deeper into continuous integration. 

# What is continuous integration?

So the concept of continuous integration is that as a developer you are able to pull from a repository the code that you are working on and then you will be able to then at any time submit the code that you are working on into a continuous integration server and the goal of that continuous integration server is that it actually goes ahead and validates and
passes any tests that a tester may have created.


Now if on the continuous integration server a test isn't passed then that code gets sent back to the developer and the developer can then make the changes. It allows the developer to actually do a couple of things it allows the developer not to break the build and we all don't want to break the builds that are being created but it also allows the developer not to actually have to run all the tests locally on their computer right tests particularly if you have a large number of tests can take up a lot of time. 

So if you can push that service up to another environment like a continuous integration server it really improves the productivity of your developer.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661896507/brightsoftwares.com.blog/qxnsbjrgojoytblew1kp.png)


What's also good is that if there are any code errors that have come up that may be beyond just the standard CI test so maybe there's a code the way that you write your code isn't consistent those errors can then be passed on easily from the tester back to the developer too.

The goal from doing all this testing is that you are able to release and deploy and your customer is able to get new code faster and when they get that code it simply just works.


# Continuous integration tools

So let's talk a little bit about some of the tools that you may have in your continuous integration environment

So the cool thing with working with continuous integration tools is that they are all open source at least the ones that we have listed here are open source there are some that are private
but typically you will get started with open source tools and it gives you the opportunity to understand how you can accelerate your environment quickly.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661896705/brightsoftwares.com.blog/iimfq6b9wvpkwo3mgpkh.png)


## Bamboo

Bamboo is a continuous integration tool that specifically runs multiple builds in parallel for faster compilation. 

If you have multiple versions of your software that runs on multiple platforms this is a tool that really allows you to get that up and running super fast so that your teams can actually test how those different builds would work for different environments and this has integration with and [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|maven]] and other similar tools.

So one of the tools you are going to need is a tool that allows you to automate the software build test and release process and buildbot is that open source product for you again it's
an open source tool so there's no license associated with this.

You can actually go in and you can actually get the environment up and running and you can then test for and build your environment and create your releases very quickly. 


## Buildbots

Buildbots also written in python and it does support parallel execution jobs across multiple platforms.


If you are working specifically on java projects that need to be built and test then apache gump is the tool for you it makes all of those projects really easy. It makes all the java projects easier for you to be able to test with api level and functionality level testing. 


## Github

So one of the popular places to actually store code and create a versioning of your code is github and it's a service that's available on the web just recently acquired by microsoft. If you
are storing your projects in github then you will be able to use travis continuous integration of travis ci and it's a tool designed specifically for hosted github projects.


## Jenkins

And so finally we are covering jenkins and jenkins is a central tool for automation for all of your projects.


Now when you are working with jenkins sometimes you will find there's documentation that refers to a product called hudson. Hudson is actually the original version of the product that
finally became jenkins and it was acquired by oracle when that acquisition happened the team behind um hudson was a little concerned about the direction that oracle may potentially go with
hudson. 

So they created a hard fork of hudson that they renamed jenkins and jenkins has now become that open source project it is one of the most popular and continuously contributed projects that's available as open source. 

So you are always getting new features being added to it it's a tool that really becomes the center for your CI environment.


# Jenkins features

So let's jump into some of those really great features that are available in jenkins. 
Jenkins itself is really comprised of five key areas around:
- easy installation
- easy configuration
- plugins
- extensibility and 
- distribution


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661897378/brightsoftwares.com.blog/uuu2saggeww1kzmfplaj.png)


## Jenkins Easy installation

As I mentioned for the easy installation jenkins is a self-contained java program. That allows it to run on most popular operating systems including windows mac os and unix you even run it on [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|linux]]. It really isn't too bad to set up it used to be much harder than it is today the setup process has really improved.

## Easy configuration

The web interface makes it really easy for you to check for any errors in addition you have great built-in help one of the things that makes tools like jenkins really powerful for developers and continuous integration teams and your devops teams as a whole when you have plugins that you can then add in to extend the base functionality of the product. 


## Jenkins plugins

Jenkins has hundreds of plugins and you can go and visit the update center and see which other plugins that would be good for your devops environment certainly check it out there's just lots of stuff out there.

## Jenkins extensibility

In addition to the plug-in architecture jenkins is also extremely extensible the opportunity for you to be able to configure jenkins to fit in your environment it's almost endless.

Now it's really important to remember that you are extending jenkins not creating a custom version of jenkins and that's a great differentiation because the core foundation remains as the core jenkins product the extensibility can then be continued with newer releases of jenkins. So you are always having the latest version of jenkins and your extensions mature with those core foundation.

## Distributed

The distribution and the nature of jenkins makes it really easy for you to be able to have it available across your entire network it really will become the center of your ci environment and it's certainly one of the easier tools and more effective tools for devops.

# Jenkins pipeline

Let's jump into the standard jenkins pipeline. When you are doing development you start off and you are coding away on your computer the first thing you have to do when you are working in the jenkins pipeline is to actually commit your code. 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661897833/brightsoftwares.com.blog/ywwl4juy0df3uhdzzs6r.png)


Now as a developer this is something that you are already doing at least you should be doing you are committing your code to a [[2022-09-28-what-is-git|git]] server um or to an svn server or a similar type of service. 

In this instance you will be using jenkins as the place for you to commit your code jenkins will then create a build of your code and part of that build process is actually going through and running through tests and again as a developer you are already comfortable with running
unit tests and writing those tests to validate your code 

But there may be additional tests that jenkins is running so for instance as a team you may have a standard set of tests for how you actually write out your code so that each team member can understand the code that's been written and those tests can also be included in the testing process within the jenkins environment.

Assuming everything passed the the tests you can then get everything placed in a stage
and release ready environment within jenkins and finally again ready to deploy or deliver your code to a production environment.

Jenkins is going to be the tool that helps you with your server environment to be able to deploy your code to the production environment and the result is that you are able to move from a developer to production code really quickly. This whole process can be automated rather than having to wait for people to actually test your codes or go through a nightly build you are looking at being able to commit your code and go through this testing process and release
process continuously.

As an example  companies Etsy will release up to 50 different versions of their website every single day.


# Jenkins architecture

Let's talk about the architecture within jenkins that allows you to be so effective at applying a continuous delivery devops environment.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661898125/brightsoftwares.com.blog/smyxdygtepjt9sxky6zd.png)


So the server architecture really is broken up into two sections on the left hand side of section you have the code the developers are doing and submitting that code to a source code repository. Then from there jenkins is your continuous integration server and it will then pull any code that's been sent to the source code repository and will run tests against it it will use a build
server such as maven to actually then build the code and every single stage that we have that jenkins manages there are constant tests. 

So for instance if a build fails that feedback is sent right back to the developers so that they can
then change their code so that the build environment can run effectively.

The final stage is to actually execute specific test scripts and these test groups can be written in selenium.

It's probably good to mention here that both mavin and selenium are plugins that run in the jenkins environment. Before we were talking about how jenkins can be extended with plug-ins mavin and selenium are just two very popular examples of how you can extend the jenkins environment. 

The goal to go through this whole process again is an automated process is to get your code from the developer to the production server as quickly as possible have it fully tested and have no errors.

It's probably important at this point to mention one piece of information around the jenkins environment that if you have different code builds that need to be managed and distributed. This will require that you need to have multiple builds being managed. Jenkins itself doesn't allow for multiple files and builds to be executed on a single server you need to have a multiple server environment with running different versions of jenkins for that to be able to happen.


# Jenkins master-slave architecture

Let's talk a little bit about the master slave architecture within jenkins. 

What we have here is an overview of the master slave architecture within jenkins. On the left-hand side is the remote source code repository. And that remote source code repository could be github or it could be team foundation services or the new azure devops code repository or it could be your own git repository.

The jenkins server acts as the master environment on the left hand side and that master
environment can then push out to multiple other jenkins slave environments to distribute the workload.

It allows you to run multiple builds and tests and production environments simultaneously across your entire architecture. So jenkins slaves can be running the different build versions of the code for different operating systems and the server master is controlling how each of those builds operate.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1661898376/brightsoftwares.com.blog/dj0cjfbpna2hdsrvn9fb.png)


# A jenkins case study

Let's step into a quick story of a company that has used jenkins very successfully.

Here's a use case scenario. over the last 10 or 15 years there has been a significant shift within the automotive industry where manufacturers have shifted from creating complex hardware to actually creating software. We have seen that with companies such as tesla where they are creating uh software to manage their cars. We see the same thing with companies such as general motors with their onstar program and Ford just recently have rebranded themselves as a
technology company rather than just a automotive company what this means though is that the software within these cars is becoming more complex and requires more testing to allow more capabilities enhancements to be added to the core software.

Bosch is a company that specifically ran into this problem and their challenge was that they wanted to be able to streamline the increasingly complex automotive software by adopting continuous integration and continuous delivery best practices with the goal of being able to delight and exceed the customer expectations of the end user.


So bosch has actually used cloudbees which is the enterprise jenkins environment so to be able to reduce them the number of manual steps such as building deploying and testing Bosch has introduced the use of cloudbees from jenkins and this is part of the enterprise jenkins platform has significantly helped improve the efficiencies throughout the whole software development cycle from automation stability and transparency because jenkins becomes a self-auditing
environment.

The results have been tangible previously it took three days before a build process could be done. 

It's taken that same three-day process and reduced it to less than three hours that is significant.  Large-scale deployments are now kept on track and have expert support and there is clear visibility and transparency across the whole operations through using the jenkins tools.


# Conclusion

First of all we describe the developer hell that you may be in before the use of jenkins. And then we talked about what the [[2022-08-24-what-is-difference-between-docker-attach-and-exec|difference]] is between a nightly build and a continuous delivery continuous integration environment can look like.

We step through how a continuous integration environment should be set up so it's constantly providing feedback to the developer or to the tester to improve and speed up the efficiency of delivering code that gets delivered out to the end user. 

We went specifically through the process that jenkins uses and the jenkins pipeline and then stepped through the architecture that jenkins employs to be successful in enabling you as a developer to build not just one but maybe multiple platform solutions at once.

And then finally we step through a use case study around the work that bosch is doing to be  able to significantly improve the efficiency of the software that they are delivering into the automotive industry.