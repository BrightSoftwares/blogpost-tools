---
author: full
categories:
- jenkins
date: 2023-03-01
description: In this Github Actions tutorial, we'll go through the following topics.
  First, I'm going to explain what Github actions actually is, and we're going to
  look at specific developer workflow use cases that you can automate with Github
  actions. After that, I will explain the basic concepts of Github actions, including
  the events and actions and workflow, and how Github actions actually automates these
  workflows using these components. Having understood what Github actions solves and
  how it makes it possible, I will go through the most common workflow, which is Cicd
  Pipeline. I will explain shortly why it's not just another Ci Cd tool, or what are
  the benefits of Github actions Cicd Pipeline. Finally, we will go through a hands-on
  demo where I explain the syntax of Github Actions workflow file, and then we will
  go through a complete Ci Pipeline setup with my example Java Gradle project which
  we will build into a docker image and
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551341/pexels-mike-b-4168038_q4w0p1.jpg
inspiration: null
lang: en
layout: flexstart-blog-single
post_date: 2023-03-01
pretified: true
tags:
- git
- cicd
title: How can I make Jenkins CI with Git trigger on pushes to master
transcribed: true
youtube_video: http://www.youtube.com/watch?v=R8_veQiYBjI
youtube_video_description: Complete Github Actions Tutorial | GitHub Actions CI/CD
  | GitHub Actions Docker Build and Push | GitHub Actions Demo ...
youtube_video_id: R8_veQiYBjI
youtube_video_title: GitHub Actions Tutorial - Basic Concepts and CI/CD Pipeline with
  Docker
---

In this Github Actions tutorial, we'll go through the following topics. First, I'm going to explain what Github actions actually is, and we're going to look at specific developer workflow use cases that you can automate with Github actions. 

After that, I will explain the basic concepts of Github actions, including the events and actions and workflow, and how Github actions actually automates these workflows using these components. Having understood what Github actions solves and how it makes it possible, I will go through the most common workflow, which is Cicd Pipeline. I will explain shortly why it's not just another Ci Cd tool, or what are the benefits of Github actions Cicd Pipeline. 

Finally, we will go through a hands-on demo where I explain the syntax of Github Actions workflow file, and then we will go through a complete Ci Pipeline setup with my example Java Gradle project which we will build into a docker image and push to a private docker repository on Docker Hub.



##  What is Github Actions?


So what is Github Actions? Github Actions is a platform to automate developer workflows. So, software development workflows. Many of the tutorials that I've seen seem to convey that Github Actions is a Ci Cd platform. 

But as I said, it's for automating developer workflows, and Ci Cd Pipeline is just one of the many workflows that you can automate with Github actions.



##  What are developer workflows? Use Cases for GitHub Actions

So now we need to understand what are those developer workflows. In other words, what is that the developers typically do that is so time consuming or error prone, or just tedious that it needs automation. 

So let's go through a couple of specific examples. Now, as you probably already know, Github is a platform for a lot of open source projects. So a lot of developers who have developed their own libraries for Java or some other programming language, they can host their projects on Github and make them publicly available as open source projects so that the community can use those projects, but also to contribute to those projects. 

So when a team or individual developers who manage those projects get new contributors or things happen inside the repository, people creating pull requests, people joining in as contributors, and so on. They have a lot of organizational tasks to manage. Let's see examples of such tasks. Let's say, you have created a library that makes it easier to work with datetime in Java. So it's a Java library that you created and you have some contributors and users of that library. And whenever a user of the library sees that a new release of the library has a bug or something isn't working, they can create an issue. 

That something is not working. So you have to check that issue. You have to sort it. Is it minor? Is it major? Is it something urgent? Is it something that others may have also reported? Is it reproducible? For example, Maybe you assign it to one of the contributors or to yourself, and so on. Let's say one of the contributors fixes the issue and creates a pull request so that you can merge it into the next release of that library. So you look at the pull request, you review the code, you make sure that the issue is not reproducible anymore with the fix, and you merge it into the master node. So this is going to be part of the next release. So to say? so you want to release the next version so the people who use the library can upgrade the version where the issue is fixed. So after the pull request is merged into the master branch, you want to start a pipeline, a build pipeline that will test your code, build your artifact, and so on. You also want to maybe prepare some release notes where you document what got edit in the new version and maybe also adjust the version tag or the version number. So all these things are workflow examples of what you have to do as a maintainer of such repository. So you can imagine the bigger the project gets and the more contributors you get and the more features and issues they fix and more pull requests they create and the more people use your project, the more organizational effort it is going to be. So obviously, as a developer, you don't want to be sitting there doing all these tedious organizational stuff. You want to automate as much as possible of those management tasks so that you can also concentrate on programming and developing new features and new functionalities in the project. And for that purpose, Github actions was created.



##  Basic Concepts of GitHub Actions: How GitHub Actions automates those workflows? GitHub Events & Actions

So with Github actions, every time something happens in your repository or to your repository, you can configure automatic actions to get executed in response. And these things that are happening in your repository or to your repository are events in the Github space. 

So someone creating a pull request is an event. Someone creating an issue is an event. Someone joining as a contributor is an event where you merging that pull request into the master branch is an event. Also note that other applications or tools that you may have integrated into your Github can also produce such events that you can respond to with automatic actions. So when you automate these flows, Basically, the concept is pretty simple. You listen to any such events, and depending on what event happens, you want a certain workflow to execute automatically. 

So every time someone creates an issue, that's an event. Maybe you want to automatically sort that issue, maybe label it, assign it to respective contributor, or maybe assign it to you per default. Maybe categorize it, and also maybe write a script or a test that will try to automatically reproduce the issue, and then add some status or comment or something that says reproducible or non-reproducible So all these things can be automated with actions. So each small task that you automatically trigger on an event is going to be a separate action. 

So writing a comment, putting a label on an issue, assigning it to someone, etcetera. those are actions, and this chain of actions or these combination of actions actually make up workflow. So now that we.



##  GitHub Actions CI/CD

Understand the basic concepts of Github actions. Let's look at a specific workflow example. So obviously not everybody has an open source project. On Github, you can have your own private projects of Github for the application that you're developing. 

So the most common workflow you will think of for your repository would be a Cicd pipeline. You commit your code, the build starts. it tests your code, builds it into an artifact, then pushes the artifact and some storage, and then deploys the application on a deployment server.



##  Why another CI/CD Tool - Benefits of Github Actions

Now why is it a big deal to have just another Ci Cd tool? Well, the first and obvious advantage is that if you're already hosting your code on Github now, you can use the same tool for Ci Cd Pipeline as well. 

You don't have to set up another third-party tool and manage it separately. You have that integrated into your code repository. Another advantage of Github actions that I see is that it makes it really easy to build your pipeline. So the setup process of the Cicd pipeline is really easy. It is actually meant to be a tool for developers. so they made it so that if you have a developer's team, you don't need an extra Devops person who is dedicated to setting up and maintaining that Ci Cd pipeline in your project. 

So now the question is, how do they make it easy? Or how does it compare to other Ci Cd tools like Jenkins for example. And why is it much easier to set up and manage? So you know that when you think about Ci Cd Pipeline, one of the most important things is it's integration with different tools. So what do I mean by that? Whether you are developing a Node.js application which will be built into a docker image and then pushed into a Nexus repository and deployed on Digitalocean Server, or you're developing a java application with Maven, You have integration tests to test your application on Linux and Windows servers, then build it into a docker image and push it to Aws container registry and deploy it on Aws Eks. 

So basically you can have many different combinations of tools that you're using in your development process, so you don't want to be sitting there trying to configure your Ci Cd pipeline with all these tools like installing java and Maven and Docker and all these integrations with Nexus and Aws and so on, installing plugins and configuring them Instead, You want a simpler way of saying hey, I need an environment which has node and docker both available without me installing any of it with a version that I want and the same way. I wanted to do the deployment part easily by simply connecting to the target environment and deploying the application there. And that's exactly the advantage that you have when you're using Ci Cd Pipeline in Github Actions.



##  DEMO - Create CI Workflow or Pipeline

And of course I will show you and explain how this works in the next demo part with my example Java Gradle Project which we will build into a docker image and push to our private docker repository. 

So to see all this in action, let's go to Github. In here, we can create a test repository, call it my project, let's make it public and that's it. So this is my empty project, so to say. So whenever you create a new project, you have this actions tab integrated into the project that lets you get started with automating one of your workflows. So now I can push my local code to the remote repository. So let's go back and refresh it. And here I have my Java application which uses Gradle project. 

So let's go to Actions. So here if we scroll down, we see a big list of workflow templates, which means you don't have to start writing your workflow file from scratch. You can use one of the templates that matches technology your project uses and these are actually grouped in three main categories. Here we see the deployment workflows to deploy your code to cloud services or using some automation tools, And here we have big section of continuous integration workflows. 

And here if you look at the list, a lot of options based on what programming language you're using, what tools you're using, and also combinations of such tools. So for example, you have Java with Gradle and you also have Java with Maven and so on. So you have the build and test workflows as well as publish workflows where you publish your artifact to some repository. And that's where I was talking about when I mentioned that different applications use different combination of tools and it's important for a Ci Cd tool to have an easy integration with many different tools so that it works for different projects all the way down. These are the workflow examples that I mentioned at the beginning like greeting someone. For example, if a contributor joins your project, you might want to send an automated greeting message to welcome or labeling your issues and so on. And obviously you can make your own workflow with different combinations and adjust it. So let's create a build workflow for our Java Gradle application. And obviously, I will choose the Java Gradle workflow template and let's see what the workflow file looks like and see what happens. It automatically creates this configuration view in my project or my repository. It creates this path dot, Github slash workflows and this is the file that basically holds my workflow logic. It is written in Yaml. it's a Yaml format and what's great with this list of workflow suggestions is that you get a pre-configured workflow that you may need to adjust just a little bit, but most of the stuff is already here so you don't have to start from blank file So.



##  Syntax of Workflow File


Let's go through the syntax of this workflow file in detail so that we understand how to write our own workflows. So I'm gonna copy this in my editor so we can see better. So first of all, we have the name of the workflow. 

This is basically for you to describe what the workflow is doing. These are the events that I mentioned. So every time an event happens or events happen, we can trigger a certain workflow. So this is a section where we define events that should trigger the following workflow. and I think it's pretty intuitive. Every time someone pushes to Master branch, we want to trigger this workflow. or every time a pull request gets created with Master branch as a target, this workflow will get executed. 

Which in this case makes sense because every time something gets pushed into a master or you want to merge something into master, it makes sense to run tests or to test our application to make sure that it's mergeable. So to say or that we didn't break something in the master branch. So that's pretty straightforward. Other examples that I mentioned could be creating an issue or a contributor Joining this will be all events listed Here You have a complete list of such events documented on this page, So here you see the list and here you see some more detailed explanation and also the usage. 

And as always, I will put all the relevant links for this tutorial in the video description and this is a part that gets executed whenever these events happen. So I have jobs. these are the names of the job. This could be arbitrary, just like the name of the workflow. so you can name it yourself. And Job basically groups a set of actions that will be executed right. So as I mentioned, events trigger a chain of actions or combination of actions and these are defined here. so let's look at the first one. Pretty logical. Whenever we want to build application or run tests, we need to check out the repository or the code first. So how does this get executed or what is behind these syntax? So Actions Path in Github is where pre-created or predefined actions are hosted. So basically you can assume that everybody who uses a Ci Cd pipeline in Github actions will need to use checkout command, right? So instead of letting everybody do that on their own, they creating an action called checkout that people can use. So if I go to Github slash actions, I will see list of repositories that contain all those actions. So let's look for our checkout action. So these are all these actions are basically repositories. Let's go inside and here you have Action Yemo! So this is a normal repository with some code in it and we have Action Yaml file here. This is basically what checkout action does in the background or the logic that people already wrote so you don't have to write it in your workflow and just reuse it. and each action in the repository will have some sort of documentation where you see if you can configure some additional parameters for this checkout action. and this here is version of that action. So to say Because as I said, these are simple repositories that are built and released and have versioning. So this is our checkout step. and whenever you are using an action that is already available either at Slash Actions or maybe some other community or team has created one, you can basically use any such action using the Uses attribute. so these are the official ones. But whenever someone creates an action basically a repository with action Yaml file, you can use it here using the Uses attribute. So the second one second step is action called Setup Java which is another repository in this actions list. and what it does is basically prepares your environment with Java with a version that you defined here. And this is the part where I mentioned that you don't have to install or configure anything like in Jenkins. For example, you would go and configure Java version Here you just define that you want to use an environment with Java on it. so Java version 1.8 will be installed and available there. the next one is a command. So here you see the difference. Whenever we are referring to action in repository, we use this attribute whenever we're running a command just like a Linux command. For example, command Line command, we are using run attribute So this basically just changes the permissions of Gradle file and the next step just calls Gradle Build and all this is done in the same environment so your code gets checked out, Java version gets installed and then you call Gradle Build in the same environment. So obviously for this to work you have to have a Java application that is built with cradle and now let's actually go ahead and execute this workflow for our Java project. The name of the Yaml file is also something that you can decide for yourself. We can actually call it Ci and start commit. Let's create a new branch and create a pull request that will be merged into master branch and here you see that the workflow got triggered because our event matched to what just happened. So we created a pull request against must branch and that triggered the workflow. This is in progress and if I go into details we're gonna see what is actually happening. So the bill completed. So let's actually look at the steps that got executed. Set up job which basically prepares the job environment for executing the workflow. Here you see for example, these action repositories got downloaded so that it can be used. Here you see the checkout action and you actually see pretty helpful information in all these steps. and they also highlight the comment that gets executed so that you can easily see first of all the command and differentiate it from the logs and also see how they can interpret your comment for example, with options and flags and environmental variables and so on. Then we have the setup Jdk again. these are the commands that got executed and some log files. This is where the build, the actual build happened, build successful, and then we have some post build actions which we didn't define. These are out of the box things get cleaned up. So in my opinion, for an initial setup of a workflow or such a workflow, it's actually pretty straightforward and easy to set up, and it's pretty difficult to mess this up.



##  Where does this Workflow Code run? GitHub Action Runner

So now you may be asking, where do all these things get actually executed because you see that the code got checked out, then you see some commands got executed, Java version got installed, and the gradle build actually happened. 

So where do all these things happen and how do they get executed? So the way it works is that workflows on Github actions get executed on Github servers, so it's managed by Github. 

You don't need to set up some servers and configure your build tool, install some plugins or whatever, and prepare it for building the application. So Github will manage all of these for you. The servers will be configured and ready to execute your jobs. 

And important to note here is that whenever you create a new job, or whenever you create a new workflow with a set of jobs for every single job, a fresh new Github server will be prepared or used to execute all those steps inside the job. So one job will run on a single server at a time. 

So for example, if you have a list of jobs here, maybe you have a job that builds the application and then you have another job that publishes Java artifacts. Let's say to a repository. So one job will run on one server, another job will run on another server. By default, these jobs will run in parallel. 

but of course, in such a case, you would want to wait until the first job was accessible to execute the publish. So here I could have a publish job. Of course, in this case, we want to wait for the build job to successfully execute before we publish the artifact so we can override this default parallel execution using needs and we can reference the bill that it depends on. and then we'll have a set of steps and actions here. 

And another thing that should be noted here as well is this line here runs on. So the servers that I mentioned that Github makes available for the workflows to run come in three categories, so you can choose either Ubuntu, Windows, or Mac Os. So for example, if you have an application that you are shipping out to customers that have all three operating systems, you can test each release for example, or each commit to master. 

You can test that on all three operating systems and the way we do that is using those attributes. So we have a strategy. A Metrics Metrics is used basically whenever you want to use multiple operating systems or maybe multiple versions of Java or whatever technology you're using for your application. And here I'm gonna define Os options as an array. So we have the Ubuntu latest, we have Windows latest, and we have Mac Os latest and here on runs on. and we're going to reference that list using Metrics.os And let's actually try to apply this change. So I have merged my pull request. 

So here you see in the master branch we have this dot Github slash workflows path with the Ci Yml file inside. So now this has become part of the application code so I can adjust it here. and let's actually commit straight to master branch and let's see our workflow. And here you see three builds are getting executed in parallel on all three operating systems.