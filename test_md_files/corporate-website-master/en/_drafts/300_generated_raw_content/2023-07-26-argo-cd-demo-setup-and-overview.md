---
author: full
categories:
- kubernetes
- docker
date: 2023-07-26
description: In today's fast-paced software development world, continuous integration
  and continuous delivery (CI/CD) pipelines have become essential. Kubernetes has
  also gained a lot of popularity as the preferred container orchestration platform,
  and it has its own specific requirements for CI/CD pipelines. This is where Argo
  CD comes in, as a tool designed specifically for Kubernetes deployments.  In this
  blog post, we will walk through a demo of setting up a fully automated CD pipeline
  for Kubernetes configuration changes using Argo CD. We will use a simple example
  with deployment and service YAML files, and show how we can update these files in
  a Git repository and have Argo CD automatically deploy the changes to a Kubernetes
  cluster.   We start with an empty MiniKube cluster, which we will use to demonstrate
  the functionality of Argo CD. We have a Git repository with deployment and service
  YAML files that we will use to deploy an application on
image: null
image_search_query: coordination
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-07-26
pretified: true
ref: argo-cd-demo-setup-and-overview
silot_terms: container docker kubernetes
tags: []
title: 'Argo CD : Demo setup and overview'
---

# TODO

## Introduction

In today's fast-paced software development world, continuous integration and continuous delivery (CI/CD) pipelines have become essential. Kubernetes has also gained a lot of popularity as the preferred container orchestration platform, and it has its own specific requirements for CI/CD pipelines. This is where Argo CD comes in, as a tool designed specifically for Kubernetes deployments.

In this blog post, we will walk through a demo of setting up a fully automated CD pipeline for Kubernetes configuration changes using Argo CD. We will use a simple example with deployment and service YAML files, and show how we can update these files in a Git repository and have Argo CD automatically deploy the changes to a Kubernetes cluster.

## Demo Setup

We start with an empty MiniKube cluster, which we will use to demonstrate the functionality of Argo CD. We have a Git repository with deployment and service YAML files that we will use to deploy an application on Kubernetes. The application's image version 1.0 is hosted on Docker Hub, and we have three image versions available for this app.

## Argo CD Installation and Configuration

We will first install Argo CD on the Kubernetes cluster. You can use the following command to install Argo CD:



`kubectl create namespace argocd kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml`

Once installed, we need to configure Argo CD to track and sync with our Git repository. We do this by creating an application Custom Resource Definition (CRD) component in Argo CD. We can do this using the following command:



`kubectl create namespace my-app kubectl apply -f app-crd.yaml -n my-app`

Here, we have created a new namespace called `my-app` and applied the `app-crd.yaml` file to it. This file defines the Argo CD application CRD that tells Argo CD which Git repository to track and sync with, and how to deploy changes.

## Git Repository Configuration

We then need to configure our Git repository to allow Argo CD to access it. We do this by adding a deploy key to our Git repository. The steps to do this vary depending on your Git repository provider, but you can find instructions for GitHub [here](https://developer.github.com/v3/guides/managing-deploy-keys/#deploy-keys).

## Argo CD Configuration Continued

We can now configure the Argo CD application CRD to point to our Git repository. We do this by updating the `argocd-application.yaml` file with our Git repository information and applying it to the `my-app` namespace:



`kubectl apply -f argocd-application.yaml -n my-app`

This file specifies the source repository, target Kubernetes cluster, and the deployment strategy to use for the application.

## Application Deployment

Now that everything is set up, we can start making changes to our Git repository and see how Argo CD automatically deploys these changes to the Kubernetes cluster. For example, let's say we want to update the application's image version to `2.0`. We can simply update the deployment YAML file in our Git repository and push the changes.

Argo CD will detect the changes in the Git repository and automatically apply the changes to the Kubernetes cluster. We can verify that the application has been updated by running the following command:



`kubectl get deployments -n my-app`

This should show the updated deployment with two replicas and the new image version.

## Conclusion

In conclusion, Argo CD is a powerful tool for automating CD pipelines for Kubernetes deployments. It allows developers to focus on writing code, while Argo CD takes care of deploying and updating the code


Introduction
In today's fast-paced software development world, continuous integration and continuous delivery (CI/CD) pipelines have become essential. Kubernetes has also gained a lot of popularity as the preferred container orchestration platform, and it has its own specific requirements for CI/CD pipelines. This is where Argo CD comes in, as a tool designed specifically for Kubernetes deployments.

In this blog post, we will walk through a demo of setting up a fully automated CD pipeline for Kubernetes configuration changes using Argo CD. We will use a simple example with deployment and service YAML files, and show how we can update these files in a Git repository and have Argo CD automatically deploy the changes to a Kubernetes cluster.

Demo Setup
We start with an empty MiniKube cluster, which we will use to demonstrate the functionality of Argo CD. We have a Git repository with deployment and service YAML files that we will use to deploy an application on Kubernetes. The application's image version 1.0 is hosted on Docker Hub, and we have three image versions available for this app.

Argo CD Installation and Configuration
We will first install Argo CD on the Kubernetes cluster. You can use the following command to install Argo CD:

ruby
Copy code
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
Once installed, we need to configure Argo CD to track and sync with our Git repository. We do this by creating an application Custom Resource Definition (CRD) component in Argo CD. We can do this using the following command:

perl
Copy code
kubectl create namespace my-app
kubectl apply -f app-crd.yaml -n my-app
Here, we have created a new namespace called my-app and applied the app-crd.yaml file to it. This file defines the Argo CD application CRD that tells Argo CD which Git repository to track and sync with, and how to deploy changes.

Git Repository Configuration
We then need to configure our Git repository to allow Argo CD to access it. We do this by adding a deploy key to our Git repository. The steps to do this vary depending on your Git repository provider, but you can find instructions for GitHub here.

Argo CD Configuration Continued
We can now configure the Argo CD application CRD to point to our Git repository. We do this by updating the argocd-application.yaml file with our Git repository information and applying it to the my-app namespace:

perl
Copy code
kubectl apply -f argocd-application.yaml -n my-app
This file specifies the source repository, target Kubernetes cluster, and the deployment strategy to use for the application.

Application Deployment
Now that everything is set up, we can start making changes to our Git repository and see how Argo CD automatically deploys these changes to the Kubernetes cluster. For example, let's say we want to update the application's image version to 2.0. We can simply update the deployment YAML file in our Git repository and push the changes.

Argo CD will detect the changes in the Git repository and automatically apply the changes to the Kubernetes cluster. We can verify that the application has been updated by running the following command:

arduino
Copy code
kubectl get deployments -n my-app
This should show the updated deployment with two replicas and the new image version.

Conclusion
In conclusion, Argo CD is a powerful tool for automating CD pipelines for Kubernetes deployments. It allows developers to focus on writing code, while Argo CD takes care of deploying and updating the code