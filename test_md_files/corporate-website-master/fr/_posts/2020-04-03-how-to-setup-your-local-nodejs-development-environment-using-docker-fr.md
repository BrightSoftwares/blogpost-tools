---
layout: flexstart-blog-single
title: "How To Setup Your Local Node.js Development Environment Using Docker"
author: full
lang: fr
ref: howto_setuplocalnodejs_dev_docker
categories: [docker]
description: "Docker is the defacto toolset for building modern applications and setting up a CI/CD pipeline – helping you build, ship and run your applications in containers on-prem and in the cloud. Whether you’re running on simple compute instances such as AWS EC2 or Azure VMs or something a little more fancy like a hosted Kubernetes service like AWS EKS or Azure AKS, Docker’s toolset is your new BFF. "
image: "https://sergio.afanou.com/assets/images/image-midres-11.jpg"
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

<p>Docker is the defacto toolset for building modern applications and setting up a CI/CD pipeline &#8211; helping you build, ship and run your applications in containers on-prem and in the cloud.&nbsp;</p>

<p>Whether you&#8217;re running on simple compute instances such as AWS EC2 or Azure VMs or something a little more fancy like a hosted Kubernetes service like AWS EKS or Azure AKS, Docker’s toolset is your new BFF.&nbsp;</p>

<p>But what about your local development environment? Setting up local dev environments can be frustrating to say the least.</p>

<p>Remember the last time you joined a new development team?</p>

<p>You needed to configure your local machine, install development tools, pull repositories, fight through out-of-date onboarding docs and READMEs, get everything running and working locally without knowing a thing about the code and it’s architecture. Oh and don’t forget about databases, caching layers and message queues. These are notoriously hard to set up and develop on locally.</p>

<p>I’ve never worked at a place where we didn’t expect at least a week or more of on-boarding for new developers.&nbsp;</p>

<p>So what are we to do? Well, there is no silver bullet and these things are hard to do (that’s why you get paid the big bucks) but with the help of Docker and it’s toolset, we can make things a whole lot easier.</p>

<p>In Part I of this tutorial we’ll walk through setting up a local development environment for a relatively complex application that uses React for it’s front end, Node and Express for a couple of micro-services and MongoDb for our datastore. We’ll use Docker to build our images and Docker Compose to make everything a whole lot easier.</p>

<p>If you have any questions, comments or just want to connect. You can reach me in our <a href="http://dockr.ly/slack">Community Slack</a> or on twitter at <a href="https://twitter.com/pmckee">@pmckee</a>.</p>

<p>Let’s get started.</p>

<h2>Prerequisites</h2>

<p>To complete this tutorial, you will need:</p>

<ul><li>Docker installed on your development machine. You can download and install Docker Desktop from the links below:<ul><li><a href="https://download.docker.com/mac/stable/Docker.dmg">Docker Desktop for Mac</a></li><li><a href="https://download.docker.com/win/stable/Docker%20Desktop%20Installer.exe">Docker Desktop for Windows</a></li></ul></li><li><a href="https://git-scm.com/downloads">Git</a> installed on your development machine.</li><li>An IDE or text editor to use for editing files. I would recommend <a href="https://code.visualstudio.com/Download">VSCode</a></li></ul>

<h2>Fork the Code Repository</h2>

<p>The first thing we want to do is download the code to our local development machine. Let’s do this using the following git command:</p>

<p><em>git clone git@github.com:pmckeetx/memphis.git</em></p>

<p>Now that we have the code local, let’s take a look at the project structure. Open the code in your favorite IDE and expand the root level directories. You’ll see the following file structure.</p>

<p>├── docker-compose.yml<br>├── notes-service<br>│ &nbsp; ├── config<br>│ &nbsp; ├── node_modules<br>│ &nbsp; ├── nodemon.json<br>│ &nbsp; ├── package-lock.json<br>│ &nbsp; ├── package.json<br>│ &nbsp; └── server.js<br>├── reading-list-service<br>│ &nbsp; ├── config<br>│ &nbsp; ├── node_modules<br>│ &nbsp; ├── nodemon.json<br>│ &nbsp; ├── package-lock.json<br>│ &nbsp; ├── package.json<br>│ &nbsp; └── server.js<br>├── users-service<br>│ &nbsp; ├── Dockerfile<br>│ &nbsp; ├── config<br>│ &nbsp; ├── node_modules<br>│ &nbsp; ├── nodemon.json<br>│ &nbsp; ├── package-lock.json<br>│ &nbsp; ├── package.json<br>│ &nbsp; └── server.js<br>└── yoda-ui<br>&nbsp; &nbsp; ├── README.md<br>&nbsp; &nbsp; ├── node_modules<br>&nbsp; &nbsp; ├── package.json<br>&nbsp; &nbsp; ├── public<br>&nbsp; &nbsp; ├── src<br> &nbsp; └── yarn.lock</p>

<p>The application is made up of a couple simple microservices and a front-end written in React.js. It uses MongoDB as it’s datastore.</p>

<p>Typically at this point, we would start a local version of MongoDB or start looking through the project to find out where our applications will be looking for MongoDB.</p>

<p>Then we would start each of our microservices independently and then finally start the UI and hope that the default configuration just works.</p>

<p>This can be very complicated and frustrating. Especially if our micro-services are using different versions of node.js and are configured differently.</p>

<p>So let&#8217;s walk through making this process easier by dockerizing our application and putting our database into a container.&nbsp;</p>

<h2>Dockerizing Applications</h2>

<p>Docker is a great way to provide consistent development environments. It will allow us to run each of our services and UI in a container. We’ll also set up things so that we can develop locally and start our dependencies with one docker command.</p>

<p>The first thing we want to do is dockerize each of our applications. Let’s start with the microservices because they are all written in node.js and we’ll be able to use the same Dockerfile.</p>

<h2>Create Dockerfiles</h2>

<p>Create a Dockerfile in the notes-services directory and add the following commands.</p>

<figure class="wp-block-image size-large is-resized"><img data-attachment-id="26571" data-permalink="https://www.docker.com/blog/how-to-setup-your-local-node-js-development-environment-using-docker/screen-shot-2020-07-01-at-5-12-36-pm/" data-orig-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.12.36-PM.jpeg?fit=713%2C321&amp;ssl=1" data-orig-size="713,321" data-comments-opened="0" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;,&quot;orientation&quot;:&quot;0&quot;}" data-image-title="Screen-Shot-2020-07-01-at-5.12.36-PM" data-image-description="" data-medium-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.12.36-PM.jpeg?fit=666%2C300&amp;ssl=1" data-large-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.12.36-PM.jpeg?fit=713%2C321&amp;ssl=1" src="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.12.36-PM.jpeg?resize=576%2C260&#038;ssl=1" alt="" class="wp-image-26571" width="576" height="260" srcset="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.12.36-PM.jpeg?w=713&amp;ssl=1 713w, https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.12.36-PM.jpeg?resize=666%2C300&amp;ssl=1 666w" sizes="(max-width: 576px) 100vw, 576px" data-recalc-dims="1" /></figure>

<p>This is a very basic Dockerfile to use with node.js. If you are not familiar with the commands, you can start with our <a href="https://docs.docker.com/get-started/">getting started guide</a>. Also take a look at our reference <a href="https://docs.docker.com/engine/reference/builder/">documentation</a>.</p>

<h2>Building Docker Images</h2>

<p>Now that we’ve created our Dockerfile, let’s build our image. Make sure you’re still located in the notes-services directory and run the following command:</p>

<p><em>docker build -t notes-service.</em></p>

<figure class="wp-block-image size-large"><img data-attachment-id="26576" data-permalink="https://www.docker.com/blog/how-to-setup-your-local-node-js-development-environment-using-docker/screen-shot-2020-07-01-at-5-38-21-pm/" data-orig-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.38.21-PM.jpeg?fit=720%2C202&amp;ssl=1" data-orig-size="720,202" data-comments-opened="0" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;,&quot;orientation&quot;:&quot;0&quot;}" data-image-title="Screen Shot 2020-07-01 at 5.38.21 PM" data-image-description="" data-medium-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.38.21-PM.jpeg?fit=720%2C202&amp;ssl=1" data-large-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.38.21-PM.jpeg?fit=720%2C202&amp;ssl=1" src="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.38.21-PM.jpeg?ssl=1" alt="" class="wp-image-26576" data-recalc-dims="1"/></figure>

<p>Now that we have our image built,&nbsp; let’s run it as a container and test that it’s working.</p>

<p><em>docker run &#8211;rm -p 8081:8081 &#8211;name notes notes-service</em></p>

<figure class="wp-block-image size-large is-resized"><img data-attachment-id="26572" data-permalink="https://www.docker.com/blog/how-to-setup-your-local-node-js-development-environment-using-docker/screen-shot-2020-07-01-at-5-11-54-pm/" data-orig-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.11.54-PM.jpeg?fit=710%2C299&amp;ssl=1" data-orig-size="710,299" data-comments-opened="0" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;,&quot;orientation&quot;:&quot;0&quot;}" data-image-title="Screen-Shot-2020-07-01-at-5.11.54-PM" data-image-description="" data-medium-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.11.54-PM.jpeg?fit=710%2C299&amp;ssl=1" data-large-file="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.11.54-PM.jpeg?fit=710%2C299&amp;ssl=1" src="https://i1.wp.com/www.docker.com/blog/wp-content/uploads/2020/07/Screen-Shot-2020-07-01-at-5.11.54-PM.jpeg?resize=568%2C239&#038;ssl=1" alt="" class="wp-image-26572" width="568" height="239" data-recalc-dims="1" /></figure>

<p>Looks like we have an issue connecting to the mongodb. Two things are broken at this point. We didn’t provide a connection string to the application. The second is that we do not have MongoDB running locally.</p>

<p>At this point we could provide a connection string to a shared instance of our database but we want to be able to manage our database locally and not have to worry about messing up our colleagues&#8217; data they might be using to develop.&nbsp;</p>

<h2>Local Database and Containers</h2>

<p>Instead of downloading MongoDB, installing, configuring and then running the Mongo database service. We can use the <a href="https://hub.docker.com/_/mongo/">Docker Official Image</a> for MongoDB and run it in a container.</p>

<p>Before we run MongoDB in a container, we want to create a couple of volumes that Docker can manage to store our persistent data and configuration. I like to use the managed volumes that docker provides instead of using bind mounts. You can read all about <a href="https://docs.docker.com/storage/">volumes in our documentation</a>.</p>

<p>Let’s create our volumes now. We’ll create one for the data and one for configuration of MongoDB.</p>

<p><em>docker volume create mongodb<br>docker volume create mongodb_config</em></p>

<p>Now we’ll create a network that our application and database will use to talk with each other. The network is called a user defined bridge network and gives us a nice DNS lookup service which we can use when creating our connection string.</p>

<p><em>docker network create mongodb</em></p>

<p>Now we can run MongoDB in a container and attach to the volumes and network we created above. Docker will pull the image from Hub and run it for you locally.</p>

<p><em>docker run -it &#8211;rm -d -v mongodb:/data/db -v mongodb_config:/data/configdb -p 27017:27017 &#8211;network mongodb &#8211;name mongodb mongo</em></p>

<p>Okay, now that we have a&nbsp; running mongodb, we also need to set a couple of environment variables so our application knows what port to listen on and what connection string to use to access the database. We’ll do this right in the docker run command.</p>

<p><em>docker run \</em><br><em>-it &#8211;rm -d \<br>&#8211;network mongodb \<br>&#8211;name notes \<br>-p 8081:8081 \<br>-e SERVER_PORT=8081 \<br>-e SERVER_PORT=8081 \<br>-e DATABASE_CONNECTIONSTRING=mongodb://mongodb:27017/yoda_notes  \ notes-service</em></p>

<p>Let’s test that our application is connected to the database and is able to add a note.</p>

<p><em>curl &#8211;request POST \<br>&#8211;url http://localhost:8081/services/m/notes \<br>&nbsp;&nbsp;&#8211;header &#8216;content-type: application/json&#8217; \<br>&nbsp;&nbsp;&#8211;data &#8216;{<br>           &#8220;name&#8221;: &#8220;this is a note&#8221;,<br>            &#8220;text&#8221;: &#8220;this is a note that I wanted to take while I was working on writing a blog post.&#8221;,<br> &#8220;owner&#8221;: &#8220;peter&#8221;<br>}</em></p>

<p>You should receive the following json back from our service.</p>

<p><em>{&#8220;code&#8221;:&#8221;success&#8221;,&#8221;payload&#8221;:{&#8220;_id&#8221;:&#8221;5efd0a1552cd422b59d4f994&#8243;,&#8221;name&#8221;:&#8221;this is a note&#8221;,&#8221;text&#8221;:&#8221;this is a note that I wanted to take while I was working on writing a blog post.&#8221;,&#8221;owner&#8221;:&#8221;peter&#8221;,&#8221;createDate&#8221;:&#8221;2020-07-01T22:11:33.256Z&#8221;}}</em></p>

<h2>Conclusion</h2>

<p>Awesome! We’ve completed the first steps in Dockerizing our local development environment for Node.js.</p>

<p>In Part II of the series, we’ll take a look at how we can use Docker Compose to simplify the process we just went through.</p>

<p>In the meantime, you can read more about networking, volumes and Dockerfile best practices with the below links:</p>

<ul><li><a href="https://docs.docker.com/network/">Docker Networking</a></li><li><a href="https://docs.docker.com/storage/">Volumes</a></li><li><a href="https://docs.docker.com/develop/develop-images/dockerfile_best-practices/">Best practices for writing Dockerfiles</a></li></ul>
<p>The post <a rel="nofollow" href="https://www.docker.com/blog/how-to-setup-your-local-node-js-development-environment-using-docker/">How To Setup Your Local Node.js Development Environment Using Docker</a> appeared first on <a rel="nofollow" href="https://www.docker.com/blog">Docker Blog</a>.</p>
