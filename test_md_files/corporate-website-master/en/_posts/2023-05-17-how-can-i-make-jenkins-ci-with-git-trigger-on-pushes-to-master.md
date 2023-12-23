---
author: full
categories:
- jenkins
date: 2023-05-17
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
image_search_query: coordination
inspiration: null
lang: en
layout: flexstart-blog-single
post_date: 2023-05-17
pretified: true
ref: how-can-i-make-jenkins-ci-with-git-trigger-on-pushes-to-master
silot_terms: devops pipeline
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

## Automate Your Developer Workflow with Github Actions

###  What is Github Actions?


So what is Github Actions? Github Actions is a platform to automate developer workflows. So, software [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|development]] workflows. Many of the tutorials that I've seen seem to convey that Github Actions is a Ci Cd platform. But as I said, it's for automating developer workflows, and Ci Cd [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|Pipeline]] is just one of the many workflows that you can automate with Github actions.

Github Actions is a powerful tool that allows you to automate your developer workflows. In this [[2022-08-31-a-complete-tutorial-about-jenkins-file|tutorial]], we'll cover everything you need to know to get started with Github Actions.

### What is Github Actions?

Github Actions is a tool that allows you to automate your software workflows with CI/CD capabilities, code scanning, and more. It provides you with a way to customize your workflow to meet your specific needs.

### Use Cases for Github Actions

Github Actions can be used in many different [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|ways]], including automating the building and testing of your code, deploying your code to various environments, and managing your release processes. It can also be used for code scanning, security testing, and more.

### Basic Concepts of Github Actions

To understand Github Actions, it's important to understand the basic concepts of events, actions, and workflows. Events trigger actions, and actions perform specific tasks, while workflows tie everything together. With Github Actions, you can automate all of these components to create a seamless workflow.

### Benefits of Github Actions

Github Actions provides many benefits over other CI/CD tools, including the ability to customize workflows to meet your specific needs, integrate with other Github tools, and more.

### Setting up a CI/CD Pipeline with Github Actions

In this tutorial, we'll walk through setting up a CI/CD pipeline using Github Actions. We'll start with a hands-on demo where we'll explain the syntax of the Github Actions workflow file. Then, we'll go through a complete CI pipeline setup using a Java Gradle project that we'll build into a [[2022-07-21-how-to-run-jenkins-jobs-with-docker|Docker]] image and push to a private [[2022-08-24-what-is-difference-between-docker-attach-and-exec|Docker]] repository on [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|Docker]] Hub.

### Hands-On Demo

To get started with Github Actions, you'll need to create a `.github/workflows` directory in your repository. [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|Inside]] this directory, you'll create a YAML file that defines your workflow. Here's an example of what the file might look like:



```yaml
name: CI Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v2

      - name: Setup Java
        uses: actions/setup-java@v2
        with:
          java-version: '11'

      - name: Build Project
        run: ./gradlew build

      - name: Build Docker Image
        run: docker build -t my-image .

      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Push to Docker Hub
        run: |
          docker tag my-image ${{ secrets.DOCKER_USERNAME }}/my-image:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/my-image:latest
```

This workflow file defines a simple CI pipeline that runs whenever code is pushed to the `main` branch of your repository. It checks out the code, sets up Java, builds the project, and then builds a [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|Docker]] image and pushes it to a private [[2023-04-11-explore-your-container-with-docker-run|Docker]] repository on [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|Docker]] Hub.



Github Actions is a powerful tool that can help you automate your developer workflows. With its ability to customize workflows, integrate with other Github tools, and more, it's a great choice for automating your CI/CD pipeline. So why not give it a try and see how it can help you streamline your development process?





## Understanding Developer Workflows and Use Cases for GitHub Actions

As a developer, you know that managing projects can be time-consuming and tedious, and it can take away from your ability to focus on programming and developing new features. However, GitHub Actions can automate many of these tasks and streamline your workflow. In this tutorial, we'll discuss what GitHub Actions are, and explore some use cases where they can be implemented to improve developer workflows.

#### Examples of Tasks Managed by Developers on GitHub

GitHub is a platform that hosts many open-source projects, including libraries for programming languages such as Java. As a developer, you may have created a library that other developers use, and you're responsible for managing it. This can include handling issues, pull requests, and preparing releases. For instance, when a user of your library reports an issue, you need to sort and prioritize it, assign it to a contributor, review code, and merge it into the master node.

After merging the pull request, you may want to start a pipeline to test your code, build your artifact, and prepare release notes. All of these tasks can add up and become quite overwhelming, especially if your project has many contributors and users.

#### Introduction to GitHub Actions

To automate these management tasks, GitHub Actions was created. This tool allows you to streamline your workflow and concentrate on programming and developing new features. With GitHub Actions, you can automate processes such as testing, building, and deploying your code, as well as other organizational tasks.

#### Basic Concepts of GitHub Actions

To understand how GitHub Actions works, you need to understand its basic concepts. These include events, actions, and workflows. Events are triggers that start workflows, such as when a pull request is created or a commit is pushed. Actions are reusable units of code that perform a specific task, such as building a [[2020-08-04-docker-tip-inspect-and-less|Docker]] image or deploying to a cloud provider. Workflows are collections of actions that are executed when a specific event occurs.

#### CI/CD Pipeline with GitHub Actions

One of the most common workflows you can create with GitHub Actions is a CI/CD pipeline. This allows you to automate the process of testing, building, and deploying your code. GitHub Actions provides many pre-built actions that can be used to create a pipeline quickly and easily. The benefits of using GitHub Actions for a CI/CD pipeline include its seamless integration with GitHub and its ability to run workflows on multiple operating systems and platforms.

#### Hands-On Demo

To help you get started with GitHub Actions, we'll provide a hands-on demo. We'll walk you through the syntax of a GitHub Actions workflow file and demonstrate how to set up a CI pipeline for a Java Gradle project. In the demo, we'll build the project into a [[2020-08-04-docker-tip-inspect-and-grep|Docker]] image and push it to a private [[2020-08-04-docker-tip-inspect-and-jq|Docker]] repository on Docker Hub.



GitHub Actions can help you streamline your developer workflow and automate many management tasks. With its powerful features and seamless integration with GitHub, it's a valuable tool for any developer.



##  Basic Concepts of GitHub Actions: How GitHub Actions automates those workflows? GitHub Events & Actions

#### Automating GitHub Workflows with GitHub Actions

GitHub Actions is a powerful tool that automates workflows in response to events that happen within a GitHub repository. When an event occurs, such as a pull request being created or an issue being reported, GitHub Actions allows you to configure automatic actions to be executed in response. But how does it work?

#### Understanding GitHub Events

GitHub events are occurrences that happen in your repository or to your repository. Examples include a pull request being created, an issue being reported, or a contributor joining the project. In addition, other tools or applications that are integrated into your GitHub repository can also generate events that you can respond to with automatic actions.

#### Automating Workflows with Actions

The concept of automating workflows with GitHub Actions is simple. You listen for events and based on the event, you want a certain workflow to execute automatically. For example, when someone creates an issue, you might want to automatically sort, label, and assign it to the appropriate contributor. You could also write a script or a test that attempts to reproduce the issue automatically and then add a status or comment indicating whether the issue is reproducible or not.

Each small task that you automatically trigger on an event is a separate action. Examples of actions include writing a comment, putting a label on an issue, or assigning the issue to someone. The combination of these actions makes up a workflow.

Automating GitHub Workflows with GitHub Actions can save you time and energy by automating tedious, time-consuming, and [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|error]]-prone tasks. By automating these tasks, you can concentrate on programming and developing new features and functionalities in your project.

Overall, GitHub Actions provides a flexible and customizable way to automate your workflows and improve your productivity as a developer.



### A Beginner's Guide to Understanding Github Actions

#### Introduction

If you are looking for a way to automate your Github repository's workflows, Github Actions is the tool you need. In this guide, we will cover the basic concepts of Github Actions and provide an example of a common workflow.

### Github Actions and Workflows

With Github Actions, you can automatically trigger actions in response to events that occur in your repository. These events can include pull requests, issues, and more. You can even configure actions to respond to events from other tools and applications that you have integrated into your repository.

Each action represents a small task that is triggered automatically by an event. For example, you can use actions to sort and label issues, assign them to contributors, or write a script to reproduce an issue automatically. These actions can be combined into workflows, which are chains of actions that respond to a specific event.

### Example Workflow

While Github Actions can be used for any project, a common use case is for Continuous Integration/Continuous Deployment (CI/CD) pipelines. In this example, we will walk through a CI/CD pipeline for a private Github repository.

1.  Commit Code: The pipeline is triggered when code is committed to the repository.


```bash
git commit -m "Added new feature"
```

2.  Build Code: The pipeline then builds the code and tests it.


```bash
npm run build npm run test
```

3.  Create Artifact: The pipeline creates an artifact from the built code.


```bash
npm pack
```

4.  Store Artifact: The artifact is then pushed to a storage location.


```bash
aws s3 cp ./myapp-1.0.0.tgz s3://my-bucket/
```


5.  Deploy Code: Finally, the pipeline deploys the application on a deployment server.



```bash
ssh user@deployment-server 'bash -s' < deploy.sh
```



By automating your workflows with Github Actions, you can save time and reduce the chance of errors in your code. While there are many different use cases for Github Actions, a CI/CD pipeline is a common workflow that can benefit any project. Start experimenting with Github Actions today and see how it can improve your development process.



###  Why Github Actions is a big deal for CI/CD

Github Actions is a CI/CD tool that is integrated into Github, making it easy for developers to set up and manage their pipelines without requiring a dedicated DevOps person. In this article, we'll explore the advantages of using Github Actions for CI/CD and how it compares to other tools like [[2022-09-07-overview-on-jenkins|Jenkins]].

#### Integration with different tools

One of the most critical aspects of a CI/CD pipeline is its integration with different tools. Developers often use different tools for their development process, which can make configuring a CI/CD pipeline a daunting task. With Github Actions, you can easily integrate your pipeline with the tools you use without having to install plugins and configure them manually.

#### Easy to set up and manage

The setup process of a CI/CD pipeline in Github Actions is straightforward, making it an ideal tool for developers. You can easily build your pipeline by specifying the environment you need and the tools you want to use. For instance, if you require an environment that has Node.js and Docker available, you can specify this in your pipeline without installing either of them.

#### Integration with Github

One of the significant advantages of Github Actions is that it is integrated into Github, making it easy to use. You can use Github Actions for your CI/CD pipeline without having to set up another third-party tool or manage it separately.



Github Actions is an excellent tool for developers who want an easy-to-use CI/CD pipeline that is integrated into Github. With Github Actions, you can easily integrate your pipeline with the tools you use without having to install plugins and configure them manually. The setup process is straightforward, making it an ideal tool for developers.



##  Simplify Your CI/CD Pipeline with Github Actions

Are you tired of setting up and managing multiple third-party tools for your CI/CD pipeline? Look no further than Github Actions.

### Integration and Ease of Use

Github Actions allows you to host your code and automate your workflows in one place. With its easy-to-use setup process, developers can easily create and manage their own pipelines without the need for an extra Devops person.

Github Actions also offers seamless integration with a wide variety of tools, making it easier for you to focus on developing your project without worrying about configuring your pipeline. Whether you're working on a Node.js application or a Java application with Maven, Github Actions has got you covered.

### Creating a Workflow in Github Actions

To see Github Actions in action, let's create a build workflow for a Java Gradle Project.

1.  Create a new repository in Github and call it "my project".
2.  Push your local code to the remote repository.
3.  Go to the "Actions" tab in Github.
4.  Choose a workflow template that matches the technology your project uses.
5.  Adjust the pre-configured workflow file to suit your needs.

The pre-configured workflow templates include build and test workflows, publish workflows, and deployment workflows. You can also create your own workflow by combining different tools and adjusting the configurations to suit your project's needs.

The workflow file is written in YAML format and can be found in the path `.github/workflows`. Github Actions makes it easy for you to get started with automating your workflows by providing pre-configured templates that you can easily adjust to fit your needs.



### Demo

In the next demo, we will show you how to build a Java Gradle Project into a Docker image and push it to a private Docker repository using Github Actions.

#### Execution Result


```
$ gradle build BUILD SUCCESSFUL in 5s
```



```
$ docker build -t my-docker-repo/my-project:latest .
...
Successfully built a5b5ef56b5e2
Successfully tagged my-docker-repo/my-project:latest
```



```bash
$ docker push my-docker-repo/my-project:latest
...
latest: digest: sha256:2fb5c130cc51f2cccb07b9773b1cc3e58020f72f0a2151d2450e05d8b6a47f6c size: 739
```

With just a few simple steps, Github Actions makes it easy for you to automate your CI/CD pipeline and simplify your development process.



# # Understanding the Syntax of a Workflow File

If you're interested in learning how to write your own GitHub workflows, it's important to understand the syntax of the workflow file. In this post, we'll go through the syntax of the workflow file in detail and discuss how to write workflows.

### Defining Workflow Events

At the beginning of the workflow file, you'll need to define the events that should trigger the following workflow. For example, every time someone pushes to the Master branch or creates a pull request with Master as the target, the workflow should execute. A list of events can be found on the [GitHub documentation page](https://docs.github.com/en/actions/reference/events-that-trigger-workflows).

### Defining Workflow Jobs

After defining the workflow events, you'll need to define the jobs that will be executed when those events occur. Each job can have a set of actions that will be executed. These actions can be pre-created or predefined actions that are hosted on GitHub's Actions Path. For example, if you need to check out the repository or code before building or running tests, you can use the "checkout" action.

To use an action, you can add the "Uses" attribute to the workflow file. GitHub Actions provides a list of official actions, but you can also use any other action created by a community or team. You can also run commands just like a [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|Linux]] command using the "run" attribute.

### Example Workflow File

Let's take a look at an example workflow file for a Java application:



```yaml
name: Java CI

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Set up JDK 1.8
      uses: actions/setup-java@v1
      with:
        java-version: 1.8
    - name: Grant execute permission for gradlew
      run: chmod +x gradlew
    - name: Build with Gradle
      run: ./gradlew build
```

In this example, the workflow file is triggered every time someone pushes to the Master branch or creates a pull request with Master as the target. The workflow has one job called "build" that runs on the "ubuntu-latest" environment. The steps of the job include checking out the code, setting up JDK 1.8, granting execute permission for "gradlew", and building the application using Gradle.

### Execution Results

When the workflow is executed, you can view the progress and results in the GitHub Actions tab of your repository. The output will show each step of the job and whether it succeeded or failed.

Below is an image placeholder showing the output of the executed workflow:

Overall, GitHub workflows can be a powerful tool for automating your software development workflows. By understanding the syntax of the workflow file, you can write your own custom workflows to fit the needs of your project



## Where does the Workflow Code Run in GitHub Actions?

GitHub Actions has become a popular platform for running workflows that automate tasks in software development. With its ease of use and flexibility, GitHub Actions has made it easier for developers to create, test, and deploy code. However, one question that often arises is where do all the workflows run? In this post, we will explore where GitHub Actions workflows get executed.

### GitHub Action Runner

GitHub Actions workflows get executed on GitHub servers, which are managed by GitHub. This means that developers do not need to set up their own servers, configure build tools, install plugins, or prepare for building their applications. Instead, GitHub manages all of these tasks for the developers. The servers are configured and ready to execute the jobs in the workflows.

### Job Execution

When a workflow is executed, each job in the workflow runs on a single server at a time. For example, if you have a list of jobs that build the application and then publish Java artifacts to a repository, each job will run on a different server. By default, these jobs will run in parallel, but developers can override this behavior using `needs` and referencing the previous job that needs to complete before the current job can start.

### Operating Systems

GitHub provides three categories of servers that developers can choose from to run their workflows: Ubuntu, Windows, or MacOS. This means that developers can test their application on all three operating systems by using the `runs-on` attribute in the workflow. By using the `strategy` attribute, developers can define different operating systems or versions of Java that their application needs to be tested on.



```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    
```

### Conclusion

In conclusion, GitHub Actions workflows get executed on GitHub servers that are managed by GitHub. Developers do not need to set up their own servers, configure build tools, or install plugins. Each job in a workflow runs on a single server at a time, and developers can choose which operating system to run their workflows on. Overall, GitHub Actions makes it easier for developers to create, test, and deploy code by providing an all-in-one platform for managing workflows.