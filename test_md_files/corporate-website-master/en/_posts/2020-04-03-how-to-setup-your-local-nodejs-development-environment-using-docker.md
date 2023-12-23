---
ToReview: true
author: full
categories:
- docker
description: 'Docker is the defacto toolset for building modern applications and setting
  up a CI/CD pipeline – helping you build, ship and run your applications in containers
  on-prem and in the cloud. Whether you’re running on simple compute instances such
  as AWS EC2 or Azure VMs or something a little more fancy like a hosted Kubernetes
  service like AWS EKS or Azure AKS, Docker’s toolset is your new BFF. '
image: https://sergio.afanou.com/assets/images/image-midres-11.jpg
lang: en
layout: flexstart-blog-single
ref: howto_setuplocalnodejs_dev_docker
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- docker
- cicd
- container
- aws
- azure
title: How To Setup Your Local Node.js Development Environment Using Docker
toc: true
---

[[2022-07-21-how-to-run-jenkins-jobs-with-docker|Docker]] is the defacto toolset for building modern applications and setting up a CI/CD [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|pipeline]] – helping you build, ship and [[2023-04-11-explore-your-container-with-docker-run|run]] your applications in containers on-prem and in the cloud. 

Whether you’re running on simple compute instances such as AWS EC2 or Azure VMs or something a little more fancy like a hosted Kubernetes service like AWS EKS or Azure AKS, [[2022-08-24-what-is-difference-between-docker-attach-and-exec|Docker]]’s toolset is your new BFF. 

But what about your [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|local]] development environment? Setting up local dev environments can be frustrating to say the least.

Remember the last time you joined a new development team?

You needed to configure your local machine, install development tools, pull repositories, fight through out-of-date onboarding docs and READMEs, get everything running and working locally without knowing a thing about the code and it’s architecture. Oh and don’t forget about databases, caching layers and message queues. These are notoriously hard to set up and develop on locally.

I’ve never worked at a place where we didn’t expect at least a week or more of on-boarding for new developers. 

So what are we to do? Well, there is no silver bullet and these things are hard to do (that’s why you get paid the big bucks) but with the help of [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|Docker]] and it’s toolset, we can make things a whole lot easier.

In Part I of this [[2022-08-31-a-complete-tutorial-about-jenkins-file|tutorial]] we’ll walk through setting up a local development environment for a relatively complex application that uses React for it’s front end, Node and Express for a couple of micro-services and MongoDb for our datastore. We’ll use [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|Docker]] to build our images and [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|Docker]] Compose to make everything a whole lot easier.

If you have any [[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|questions]], comments or just want to connect. You can reach me in our [Community Slack](http://dockr.ly/slack) or on twitter at [@pmckee](https://twitter.com/pmckee).

Let’s get started.

Prerequisites
-------------

To complete this tutorial, you will need:

*   [[2020-08-04-docker-tip-inspect-and-less|Docker]] installed on your development machine. You can download and install [[2020-08-04-docker-tip-inspect-and-grep|Docker]] Desktop from the links below:
    *   [Docker Desktop for Mac](https://download.docker.com/mac/stable/Docker.dmg)
    *   [Docker Desktop for Windows](https://download.docker.com/win/stable/Docker%20Desktop%20Installer.exe)
*   [Git](https://git-scm.com/downloads) installed on your development machine.
*   An IDE or text editor to use for editing files. I would recommend [VSCode](https://code.visualstudio.com/Download)

Fork the Code Repository
------------------------

The first thing we want to do is download the code to our local development machine. Let’s do this using the following [[2022-09-28-what-is-git|git]] command:

_git clone [[2023-05-17-how-can-i-make-jenkins-ci-with-git-trigger-on-pushes-to-master|git]]@github.com:pmckeetx/memphis.git_

Now that we have the code local, let’s take a look at the project structure. Open the code in your favorite IDE and expand the root level directories. You’ll see the following file structure.

├── [[2020-08-04-docker-tip-inspect-and-jq|docker]]-compose.yml  
├── notes-service  
│   ├── config  
│   ├── node\_modules  
│   ├── nodemon.json  
│   ├── package-lock.json  
│   ├── package.json  
│   └── server.js  
├── reading-list-service  
│   ├── config  
│   ├── node\_modules  
│   ├── nodemon.json  
│   ├── package-lock.json  
│   ├── package.json  
│   └── server.js  
├── users-service  
│   ├── Dockerfile  
│   ├── config  
│   ├── node\_modules  
│   ├── nodemon.json  
│   ├── package-lock.json  
│   ├── package.json  
│   └── server.js  
└── yoda-ui  
    ├── README.md  
    ├── node\_modules  
    ├── package.json  
    ├── public  
    ├── src  
  └── yarn.lock

The application is made up of a couple simple microservices and a front-end written in React.js. It uses MongoDB as it’s datastore.

Typically at this point, we would start a local version of MongoDB or start looking through the project to find out where our applications will be looking for MongoDB.

Then we would start each of our microservices independently and then finally start the UI and hope that the [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|default]] configuration just works.

This can be very complicated and frustrating. Especially if our micro-services are using different versions of node.js and are configured differently.

So let’s walk through making this process easier by dockerizing our application and putting our database into a container. 

Dockerizing Applications
------------------------

Docker is a great way to provide consistent development environments. It will allow us to run each of our services and UI in a container. We’ll also set up things so that we can develop locally and start our [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|dependencies]] with one docker command.

The first thing we want to do is dockerize each of our applications. Let’s start with the microservices because they are all written in node.js and we’ll be able to use the same Dockerfile.

Create Dockerfiles
------------------

Create a Dockerfile in the notes-services directory and add the following commands.

![](https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.12.36-PM.jpeg?resize=576%2C260&ssl=1)

This is a very basic Dockerfile to use with node.js. If you are not familiar with the commands, you can start with our [getting started guide](https://docs.docker.com/get-started/). Also take a look at our reference [documentation](https://docs.docker.com/engine/reference/builder/).

Building Docker Images
----------------------

Now that we’ve created our Dockerfile, let’s build our image. Make sure you’re still located in the notes-services directory and run the following command:

_docker build -t notes-service._

![](https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.38.21-PM.jpeg?ssl=1)

Now that we have our image built,  let’s run it as a container and test that it’s working.

_docker run –rm -p 8081:8081 –name notes notes-service_

![](https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.11.54-PM.jpeg?resize=568%2C239&ssl=1)

Looks like we have an issue connecting to the mongodb. Two things are broken at this point. We didn’t provide a connection string to the application. The second is that we do not have MongoDB running locally.

At this point we could provide a connection string to a shared instance of our database but we want to be able to manage our database locally and not have to worry about messing up our colleagues’ data they might be using to develop. 

Local Database and Containers
-----------------------------

Instead of downloading MongoDB, installing, configuring and then running the Mongo database service. We can use the [Docker Official Image](https://hub.docker.com/_/mongo/) for MongoDB and run it in a container.

Before we run MongoDB in a container, we want to create a couple of volumes that Docker can manage to store our persistent data and configuration. I like to use the managed volumes that docker provides instead of using bind mounts. You can read all about [volumes in our documentation](https://docs.docker.com/storage/).

Let’s create our volumes now. We’ll create one for the data and one for configuration of MongoDB.

_docker volume create mongodb  
docker volume create mongodb\_config_

Now we’ll create a network that our application and database will use to talk with each other. The network is called a user defined bridge network and gives us a nice DNS lookup service which we can use when creating our connection string.

_docker network create mongodb_

Now we can run MongoDB in a container and attach to the volumes and network we created above. Docker will pull the image from Hub and run it for you locally.

_docker run -it –rm -d -v mongodb:/data/db -v mongodb\_config:/data/configdb -p 27017:27017 –network mongodb –name mongodb mongo_

Okay, now that we have a  running mongodb, we also need to set a couple of environment variables so our application knows what port to listen on and what connection string to use to access the database. We’ll do this right in the docker run command.

_docker run \\_  
_\-it –rm -d \\  
–network mongodb \\  
–name notes \\  
\-p 8081:8081 \\  
\-e SERVER\_PORT=8081 \\  
\-e SERVER\_PORT=8081 \\  
\-e DATABASE\_CONNECTIONSTRING=mongodb://mongodb:27017/yoda\_notes \\ notes-service_

Let’s test that our application is connected to the database and is able to add a note.

_curl –request POST \\  
–url http://localhost:8081/services/m/notes \\  
  –header ‘content-type: application/json’ \\  
  –data ‘{  
“name”: “this is a note”,  
“text”: “this is a note that I wanted to take while I was working on writing a blog post.”,  
“owner”: “peter”  
}_

You should receive the following json back from our service.

_{“code”:”success”,”payload”:{“\_id”:”5efd0a1552cd422b59d4f994″,”name”:”this is a note”,”text”:”this is a note that I wanted to take while I was working on writing a blog post.”,”owner”:”peter”,”createDate”:”2020-07-01T22:11:33.256Z”}}_

Conclusion
----------

Awesome! We’ve completed the first steps in Dockerizing our local development environment for Node.js.

In Part II of the series, we’ll take a look at how we can use Docker Compose to simplify the process we just went through.

In the meantime, you can read more about networking, volumes and Dockerfile best practices with the below links:

*   [Docker Networking](https://docs.docker.com/network/)
*   [Volumes](https://docs.docker.com/storage/)
*   [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

The post [How To Setup Your Local Node.js Development Environment Using Docker](https://www.docker.com/blog/how-to-setup-your-local-node-js-development-environment-using-docker/) appeared first on [Docker Blog](https://www.docker.com/blog).