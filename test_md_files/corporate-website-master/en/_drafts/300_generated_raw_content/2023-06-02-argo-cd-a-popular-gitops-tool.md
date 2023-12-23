---
author: full
categories:
- kubernetes
- docker
date: 2023-06-02
description: In this blog post, we will discuss a popular GitOps tool called Argo
  CD that is gaining popularity in the DevOps world. If you are not familiar with
  GitOps, you can check out my other blog post about GitUps, which will make this
  blog post easier to understand. First, we will explain what Argo CD is, its common
  use cases, and why we need it. Then, we will see how Argo CD works and how it does
  its job. In the final part, we will set up a fully automated CD pipeline for Kubernetes
  configuration changes using Argo CD.   Argo CD is a continuous delivery tool. To
  understand Argo CD as a CD tool or continuous delivery tool, let's first understand
  how continuous delivery is implemented in most projects using common tools like
  Jenkins or GitLab CI/CD. Then, we will see how Argo CD compares to them. In that
  context, we will answer questions such
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/b9GvPxDpRjk
image_search_query: coordination
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-06-02
pretified: true
ref: argo-cd-a-popular-gitops-tool
silot_terms: container docker kubernetes
tags: []
title: 'Argo CD : a popular GitOps tool'
---

# TODO


In this blog post, we will discuss a popular GitOps tool called Argo CD that is gaining popularity in the DevOps world. If you are not familiar with GitOps, you can check out my other blog post about GitUps, which will make this blog post easier to understand. First, we will explain what Argo CD is, its common use cases, and why we need it. Then, we will see how Argo CD works and how it does its job. In the final part, we will set up a fully automated CD pipeline for Kubernetes configuration changes using Argo CD.

## What is Argo CD?

Argo CD is a continuous delivery tool. To understand Argo CD as a CD tool or continuous delivery tool, let's first understand how continuous delivery is implemented in most projects using common tools like Jenkins or GitLab CI/CD. Then, we will see how Argo CD compares to them. In that context, we will answer questions such as "Is Argo CD just another CD tool?" or "What is so special about it?" and "Does it replace any of these other established tools like Jenkins or GitLab CI/CD?"

## Continuous Delivery with Jenkins or GitLab CI/CD

Let's say we have a microservices application running in a Kubernetes cluster. When things change in the application code, like a new feature or a bug fix, the CI pipeline on Jenkins, for example, will be automatically triggered and will test the changes, build a new Docker image, and push it to a Docker repository. Now, how does this new image get deployed to Kubernetes? We update the application's deployment YAML file for Kubernetes with the new image tag. This YAML file should then be applied in Kubernetes. In most projects, these steps are the continuation of the CI pipeline. After the image gets pushed to the repository, Jenkins will update the deployment YAML file for the application, and using kubectl tool, for example, will apply the updated deployment file to Kubernetes. This is how many projects are set up.

## Challenges with the Common Approach

However, there are a couple of challenges with this approach. First, you need to install and set up tools like kubectl or Helm to access the Kubernetes cluster and execute changes on those build automation tools. So, you would need to install and configure them on Jenkins. You also need to configure access to Kubernetes for these tools because kubectl is just the Kubernetes client, and to connect to Kubernetes, it needs to provide some credentials. So, you will need to configure credentials for the Kubernetes cluster in Jenkins. If you're using EKS cluster, which is a Kubernetes managed cluster on AWS, for example, in addition, you would also need access to AWS. So, you'd have to add AWS credentials in addition to the Kubernetes credentials to Jenkins. This is not only a configuration effort but also a security challenge because you need to give your cluster credentials to external services and tools. Especially, we have 50 projects that deploy applications to the cluster; each project application will need its Kubernetes credentials so that it can only access that specific application's resources in the cluster. Similarly, if we have 50 clusters where things get deployed, we would have to configure it for each and every cluster.

The third challenge, and probably the most important one, is that once Jenkins deploys the application to Kubernetes or it applies any changes to Kubernetes configuration, it has no further visibility in the deployment status. So, once kubectl apply was executed, Jenkins doesn't actually know the status of that execution. Did the application actually get created? Is it in a healthy status? Or is it actually failing to start, and so on? You can only find that out by following test steps.

## Improving the CD Process with Argo CD

Now let's move on to the demo project where we will deploy Argo CD and set up a fully automated CD pipeline for Kubernetes configuration changes. For this demo, we will assume that you already have a Kubernetes cluster set up and running, and you have administrative access to the cluster.

First, we need to deploy Argo CD to the cluster. We can do this by running the following command:



`kubectl create namespace argocd kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml`

The first command creates a new namespace called `argocd`, and the second command applies the Argo CD installation manifest to the `argocd` namespace.

After deploying Argo CD, we need to configure it to connect to our Git repository and watch for changes. For this demo, we will use a simple Node.js application stored in a public Git repository on GitHub. To configure Argo CD, we need to create a new `Application` resource in Kubernetes that defines the application source and deployment target. We can do this by creating a YAML file called `node-app.yaml` with the following content:



`apiVersion: argoproj.io/v1alpha1 kind: Application metadata:   name: node-app spec:   source:     repoURL: https://github.com/your-username/node-app.git     targetRevision: HEAD     path: .   destination:     server: https://kubernetes.default.svc     namespace: default   project: default   syncPolicy:     automated:       prune: true       selfHeal: true`

In this YAML file, we define a new `Application` resource with the name `node-app`. We specify the Git repository URL, target revision (HEAD), and path to the application source code. We also specify the Kubernetes deployment target by specifying the Kubernetes server URL, namespace, and project. Finally, we specify the sync policy to use automated sync with pruning and self-healing enabled.

To create the `Application` resource, we can run the following command:



`kubectl apply -f node-app.yaml`

After creating the `Application` resource, Argo CD will automatically start watching for changes in the Git repository and deploy the application to the Kubernetes cluster. Any changes made to the application source code will automatically trigger a new deployment to the cluster.

In conclusion, Argo CD is a powerful GitOps tool that simplifies the CD process for Kubernetes clusters. By using a pull-based workflow and integrating with Git, Argo CD makes CD more efficient and reliable. In this blog post, we discussed what Argo CD is, how it works, and why it's a good tool to use for CD in Kubernetes. We also provided a hands-on demo project to help you get started with Argo CD. Try it out and see how it can improve your CD workflow!




Introduction

In this blog post, we will discuss a popular GitOps tool called Argo CD that is gaining popularity in the DevOps world. If you are not familiar with GitOps, you can check out my other blog post about GitUps, which will make this blog post easier to understand. First, we will explain what Argo CD is, its common use cases, and why we need it. Then, we will see how Argo CD works and how it does its job. In the final part, we will set up a fully automated CD pipeline for Kubernetes configuration changes using Argo CD.

What is Argo CD?

Argo CD is a continuous delivery tool. To understand Argo CD as a CD tool or continuous delivery tool, let's first understand how continuous delivery is implemented in most projects using common tools like Jenkins or GitLab CI/CD. Then, we will see how Argo CD compares to them. In that context, we will answer questions such as "Is Argo CD just another CD tool?" or "What is so special about it?" and "Does it replace any of these other established tools like Jenkins or GitLab CI/CD?"

Continuous Delivery with Jenkins or GitLab CI/CD

Let's say we have a microservices application running in a Kubernetes cluster. When things change in the application code, like a new feature or a bug fix, the CI pipeline on Jenkins, for example, will be automatically triggered and will test the changes, build a new Docker image, and push it to a Docker repository. Now, how does this new image get deployed to Kubernetes? We update the application's deployment YAML file for Kubernetes with the new image tag. This YAML file should then be applied in Kubernetes. In most projects, these steps are the continuation of the CI pipeline. After the image gets pushed to the repository, Jenkins will update the deployment YAML file for the application, and using kubectl tool, for example, will apply the updated deployment file to Kubernetes. This is how many projects are set up.

Challenges with the Common Approach

However, there are a couple of challenges with this approach. First, you need to install and set up tools like kubectl or Helm to access the Kubernetes cluster and execute changes on those build automation tools. So, you would need to install and configure them on Jenkins. You also need to configure access to Kubernetes for these tools because kubectl is just the Kubernetes client, and to connect to Kubernetes, it needs to provide some credentials. So, you will need to configure credentials for the Kubernetes cluster in Jenkins. If you're using EKS cluster, which is a Kubernetes managed cluster on AWS, for example, in addition, you would also need access to AWS. So, you'd have to add AWS credentials in addition to the Kubernetes credentials to Jenkins. This is not only a configuration effort but also a security challenge because you need to give your cluster credentials to external services and tools. Especially, we have 50 projects that deploy applications to the cluster; each project application will need its Kubernetes credentials so that it can only access that specific application's resources in the cluster. Similarly, if we have 50 clusters where things get deployed, we would have to configure it for each and every cluster.

The third challenge, and probably the most important one, is that once Jenkins deploys the application to Kubernetes or it applies any changes to Kubernetes configuration, it has no further visibility in the deployment status. So, once kubectl apply was executed, Jenkins doesn't actually know the status of that execution. Did the application actually get created? Is it in a healthy status? Or is it actually failing to start, and so on? You can only find that out by following test steps.

Improving the CD Process with Argo CD

The CD





User
continue
ChatGPT
Now let's move on to the demo project where we will deploy Argo CD and set up a fully automated CD pipeline for Kubernetes configuration changes. For this demo, we will assume that you already have a Kubernetes cluster set up and running, and you have administrative access to the cluster.

First, we need to deploy Argo CD to the cluster. We can do this by running the following command:

shell
Copy code
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
The first command creates a new namespace called argocd, and the second command applies the Argo CD installation manifest to the argocd namespace.

After deploying Argo CD, we need to configure it to connect to our Git repository and watch for changes. For this demo, we will use a simple Node.js application stored in a public Git repository on GitHub. To configure Argo CD, we need to create a new Application resource in Kubernetes that defines the application source and deployment target. We can do this by creating a YAML file called node-app.yaml with the following content:

yaml
Copy code
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: node-app
spec:
  source:
    repoURL: https://github.com/your-username/node-app.git
    targetRevision: HEAD
    path: .
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  project: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
In this YAML file, we define a new Application resource with the name node-app. We specify the Git repository URL, target revision (HEAD), and path to the application source code. We also specify the Kubernetes deployment target by specifying the Kubernetes server URL, namespace, and project. Finally, we specify the sync policy to use automated sync with pruning and self-healing enabled.

To create the Application resource, we can run the following command:

shell
Copy code
kubectl apply -f node-app.yaml
After creating the Application resource, Argo CD will automatically start watching for changes in the Git repository and deploy the application to the Kubernetes cluster. Any changes made to the application source code will automatically trigger a new deployment to the cluster.

In conclusion, Argo CD is a powerful GitOps tool that simplifies the CD process for Kubernetes clusters. By using a pull-based workflow and integrating with Git, Argo CD makes CD more efficient and reliable. In this blog post, we discussed what Argo CD is, how it works, and why it's a good tool to use for CD in Kubernetes. We also provided a hands-on demo project to help you get started with Argo CD. Try it out and see how it can improve your CD workflow!