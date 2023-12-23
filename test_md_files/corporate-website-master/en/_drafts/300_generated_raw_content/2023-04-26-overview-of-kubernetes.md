---
categories:
- kubernetes
date: 2023-04-26
description: 'In this video I''m gonna explain all the main concepts of Helm so that
  you''re able to use it in your own projects. Also, Helm changes a lot from version
  to version, so understanding the basic common principles and more importantly its
  use cases to when and why we use Helm will make it easier for you to use it in practice
  no matter which version you choose. So the topics I''m gonna go through in this
  video are: Helm and Helm Charts what they are, how to use them, and in which scenarios
  they''re used, and also what is Tiller and what part it plays in the Helm architecture.
  So what is Helm? Helm has a.     Couple of main features that it''s useful. The
  first one is as a package manager for Kubernetes, so you can think of it as apt
  yum or home Brewer for Kubernetes. So it''s a convenient way for'
image: null
lang: en
post_date: 2023-04-26
pretified: true
tags: []
title: Overview of kubernetes
transcribed: true
youtube_video: https://youtu.be/-ykwb1d0DXU
youtube_video_id: -ykwb1d0DXU
---

#  Intro

In this video I'm gonna explain all the main concepts of Helm so that you're able to use it in your own projects. Also, Helm changes a lot from version to version, so understanding the basic common principles and more importantly its use cases to when and why we use Helm will make it easier for you to use it in practice no matter which version you choose. So the topics I'm gonna go through in this video are: Helm and Helm Charts what they are, how to use them, and in which scenarios they're used, and also what is Tiller and what part it plays in the Helm architecture. So what is Helm? Helm has a.



#  Package Manager and Helm Charts

Couple of main features that it's useful. The first one is as a package manager for Kubernetes, so you can think of it as apt yum or home Brewer for Kubernetes. So it's a convenient way for packaging collections of Kubernetes DML files and distributing them in public and private registry. Now, these definitions may sound a bit abstract, so let's break them down with specific examples. So let's say you have deployed your application in Kubernetes cluster and you want to deploy Elasticsearch. Additionally, a new cluster that your application will use to collect its logs. In order to deploy Elastic, Stick in your Kubernetes cluster, you will need a couple of commands components, so you would need a stateful set which is for stateful applications like databases. You will need a config map with external configuration. You would need a secret where some credentials and secret data are stored. You will need to create the current it's user with its respective permissions and also create a couple of services. Now, if you were to create all of these files manually by searching for each one of them separately on Internet, be a tedious job. And until you have all these yellow files collected and tested and try it out, it might take some time. and since Elastic stack deployment is pretty much the standard across all clusters, other people will probably have to go through the same. So it made perfect sense that someone created this yellow files once and packaged them up and made it available somewhere so that other people who also use the same kind of deployment could use them in their communities cluster. And that bundle of yellow files is called Helm Chart. So using Helm you can create your own helmet, arts, or bundles of those yellow files and push them to some Helm repository to make it available for others or you can consume. So you can use download and use existing Helm charts that other people pushed and made available in different repositories so commonly use deployments like database applications Elasticsearch MongoDB my sequel, or monitoring applications like Prometheus that all have this kind of complex set up. all have charts available in some Helm repository, So using a simple Helm installed chart name command, you can reuse the configuration that someone else has already made without additional effort and sometimes that someone is even the company that created the application. And this functionality of sharing charts that became pretty widely used actually was one of the contributors to why Helm became so popular compared to its alternative tools. So now if you're if you have a cluster and you need some kind of deployment that you think should be available out there, you can actually look it up either using command line so you can do helm search with a keyword or you can go to either Helms on public repository Helm Hub or on Helm Charts pages or other repositories that are available and I will put all the relevant links for this video in the description so you can check them out. Now apart from those public registries for helm charts, there are also private registries because when companies start creating those charts, they also started distributing them monk or internally in the organization. So it made perfect sense to create registries to share those charts within the organization and not publicly. So they're a couple of tools out there. they're used as Hell Charts private repositories as well. Another.



#  Templating Engine

Functionality of Helm is that it's a templating engine, so what does that actually mean? Imagine you have an application that is made up of multiple micro services and you're deploying all of them in your convenience cluster and deployment and service of each of those micro services are pretty much the same with the only difference that the application name and version are different or the docker, image, name and version tags are different. So without Helm, you would write separate EML files configuration files for each of those micro services. So you would have multiple deployment service files where each one has its own application name and version defined. But since the only difference between those Llamo files are just couple of lines or a couple of values. Using Helm, what you can do is that you can define a common blueprint for all the micro services and the values that are dynamic or the values that are going to change. replace by placeholders and that would be a template file. So the template file would look something like this. You would have a template file which is standard EML but instead of values in some places you would have the syntax which means that you're taking a value from external configuration and that external configuration. If you see the syntax here, dot values That external configuration comes from an additional llamó file which is called Values Dot Yemen And here you can define all those values that you are going to use in that template file. So for example, here those 4 values are defined in an Values Yamo file and what dot Values is? It's an object that is being created it based on the values that are supplied via Values EML file and also through command line using - - set flag. So whichever way you define those additional values that are combined and put together in odd values object that you can then use in those template files to get the values out. So now instead of having yellow files for each micro-service you just have one and you can simply replace those values dynamically. And this is especially.



#  Use Cases for Helm

Practical when you're using continuous delivery, continuous integration for application because what you can do is that in your built pipeline, you can use those, template the Ml files and replace the values on the fly before deploying them. Another use case where you can use the helm features of package manager and templating engine is when you deploy the same set of applications across different Kubernetes clusters. So consider use case where you have your micro service application that you want to deploy on development, staging, and production clusters. So instead of deploying the individual DML files separately in each cluster, you can package them up to make your own application chart that will have all the necessary Ml files that that particular deployment needs and then you can use them to redeploy the same application in.



#  Helm Chart Structure

Different communities cluster environments using one comment which can also make the whole deployment process easier. So now that you know what helm charts are used for it, let's actually look at an example helm chart structure to have a better understanding. So typically chart is made up of such a directory structure so it have the top level will be the name of the chart and inside the director you would have following so Chart That Yamo is basically a file that contains all the meta information about the chart could be named and version may be list of dependencies etc. values. The Demo that I mentioned before is place where all the values are configured for the template files and this will actually be the default values that you can override later. The Charts directory will have char dependencies inside meaning that if this chart depends on other charts then those chart dependencies will be stored here. and Templates folder is basically where the template files are stored. so when you execute, he'll install command to actually deploy those yellow files into Kubernetes. The template files from here will be filled with the values from value store demo producing valid Kubernetes manifests that can then be deployed into Kubernetes and optionally you can have some other files in this folder like readme or license file etc. So to have a better.



#  Values injection into template files

Understanding of how values are injected into Helm templates, consider that in values the Demo which is a default value configuration you have following three values: Image, Name, Port, and Version And as I mentioned, the default values that are defined here can be overridden in a couple of different ways. One way is that when executing Helm Install Command, you can provide an alternative values Yellow File using Values Flag So for example, if values, the Mo file will have following three values which are Image, Name, Port, and Version you can define your own values Yellow File called My Value Study Mo and you can override one of those values or you can even add some new attributes there and those two will be merged which will result into a dot values object that will look like this so would have Image, name and port from values or Demo and the one that you overrode with your own values File: Alternatively, you can also provide additional individual values using Set flag where you can define the values directly on the command line, but of course it's more organized and better manageable to have files where you store all those values instead of just providing them on a command line. Another feature of Helm is.



#  Release Management / Tiller (Helm Version 2!)

Release Management which is provided based on its setup. But it's important to note here the difference between Helm versions 2 & 3. In version 2 of Helm, The Helm installation comes in two parts. You have Helm client and the server and the server part is called Tiller. So whenever you deploy Helm Chart using Helm install my chart. Helm client will send the yellow files to Tiller that actually runs or has to run in a Kubernetes cluster and Tiller then will execute this request and create components from this yellow files inside the Currents cluster and exactly. This architecture offers additional valuable feature of Helm, which is Release Management. So the way Helm Clients server setup works is that whenever you create or change Deployment Pillar will store a copy of each configuration clients and for future reference, thus creating a history of chart executions. So when you execute Helm Upgrade chart name the changes will be applied to the existing deployment instead of removing it and creating a new one and also in case the upgrades goes wrong. For example, some yellow files where falls or some configuration was wrong, you can roll back that upgrade using Helm Robic chart name comment and all. This is possible because of that chart execution history that Tiller keeps whenever you send those requests from Helm client to tiller. However, this setup has a big.