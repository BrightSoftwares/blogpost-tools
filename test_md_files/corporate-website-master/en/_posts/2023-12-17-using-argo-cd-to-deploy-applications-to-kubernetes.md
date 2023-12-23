---
author: full
categories:
- kubernetes
date: 2023-12-17
description: in this blog post we're going to talk about a git ops tool that is gaining
  popularity in the devops world which is called argo cd if you don't know what git
  ops is you can check out my other blog post about git ups after which this blog
  post will make much more sense to you first i'm going to explain what argo city
  is and what are the common use cases or why we need argo cd we will then see how
  argo city actually works and how it does its job and in the final part we will do
  a hands-on demo project where we deploy argo cd and set up a fully automated cd
  pipeline for kubernetes configuration changes to get some practical experience with
  argo cd right away     argo city is as the name already tells you a continuous delivery
  tool and to understand argo cd as a cd tool or continuous
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/ecOqzrbJh1E
image_search_query: coordination
lang: en
layout: flexstart-blog-single
post_date: 2023-12-17
pretified: true
ref: introduction-to-argocd-for-devops
tags: []
title: Using Argo CD to Deploy Applications to Kubernetes
transcribed: true
youtube_blog post: https://www.youtube.com/watch?v=MeU5_k9ssrs&ab_channel=TechWorldwithNana
youtube_blog post_id: MeU5_k9ssrs
---

Are you looking for an effective way to deploy your Kubernetes applications? Then you should consider using Argo CD, a powerful and easy-to-use tool that helps you deploy your applications in a fast, reliable, and efficient way. In this article, we'll show you how to use Argo CD to deploy your applications to Kubernetes and get your applications up and running in no time.

## Setting up Argo CD

First, let's create a new Argo CD server service by running the following command:



`kubectl port-forward svc/argocd-server -n argocd 8080:443`

This will create a new service that is accessible on HTTP and HTTPS ports. To access this service, we'll use `kubectl port-forward`. Here's how to forward the service requests to the local port 8080:



`kubectl port-forward svc/argocd-server -n argocd 8080:443`

Note that we're also forwarding the service requests to the `argocd` namespace.

Now that we have access to the Argo CD UI, we'll need to log in to the service. The username is `admin`, and the password is auto-generated and saved in a secret called `argocd-initial-admin-secret`. We can get the password by running the following command:



`kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d && echo`

This will decode the base64-encoded password value and print it to the console. Once we have the password, we can log in to the Argo CD UI and start deploying our applications.

## Deploying Applications with Argo CD

To deploy our applications with Argo CD, we'll need to create a configuration file that tells Argo CD how to connect to the Git repository where the configuration files are hosted. We'll call this file `application.yaml`.

The configuration is straightforward. First, we have the `apiVersion` and `kind` fields, which are familiar fields from Kubernetes. For custom resource definitions, the `apiVersion` is from the project itself, so we'll use `argoproj.io/v1alpha1`. The `kind` is `Application`.

Next, we have the `metadata` field, which contains the name and namespace of the application. We'll call this `my-app-argocd` and put it in the `argocd` namespace.

Finally, we have the `spec` field, which is specific to this application. We'll set the `project` field to the default project and configure two things: the Git repository that Argo CD will connect to and sync, and the destination or cluster where Argo CD will apply the definitions it found in the Git repository.

Here's what the configuration file looks like:



`apiVersion: argoproj.io/v1alpha1 kind: Application metadata:   name: my-app-argocd   namespace: argocd spec:   project: default   source:     repoURL: <git-repository-url>     targetRevision: HEAD     path: dev   destination:     server: https://kubernetes.default.svc     namespace: default`

Note that we're using the `<git-repository-url>` placeholder. You'll need to replace this with the URL of your Git repository.

Once we've created this configuration file, we can apply it to Argo CD by running the following command:



`kubectl apply -f application.yaml`

Argo CD will automatically detect the new configuration file and start syncing the application. You can monitor the progress of the deployment

Once we have our configuration file set up, we can use kubectl to apply it:



`kubectl apply -f dev/application.yaml -n argocd`

This will create our application in the argocd namespace.

Now, if we go back to the Argo CD UI and refresh the page, we should see our application listed. We can click on it to see more details.

From here, we can see that Argo CD has synced our application with the Git repository and found the configuration files in the dev folder.

We can also see that Argo CD has deployed our application to the Kubernetes cluster, as evidenced by the "Sync Status" and "Health Status" sections.

At this point, we have successfully set up Argo CD to manage our application deployments. Any changes we make to our configuration files in the Git repository will automatically be synced and deployed to the Kubernetes cluster.

## Conclusion

Argo CD is a powerful tool for managing Kubernetes applications and deployments. It provides an intuitive UI and a powerful CLI, as well as integrations with Git repositories and other tools.

In this article, we walked through the process of setting up Argo CD on a Kubernetes cluster, using a sample application as an example. We covered the basic concepts of Argo CD, such as applications, repositories, and destinations, and demonstrated how to configure and deploy an application using Argo CD.

We hope that this article has been helpful in getting you started with Argo CD, and that you are now able to use it to manage your own Kubernetes deployments.