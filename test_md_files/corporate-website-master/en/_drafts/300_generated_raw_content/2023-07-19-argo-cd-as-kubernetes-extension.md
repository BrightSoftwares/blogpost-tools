---
author: full
categories:
- kubernetes
- docker
date: 2023-07-19
description: In modern software development, the importance of Kubernetes (K8s) is
  growing rapidly. As more and more companies adopt K8s, the need for efficient K8s
  access management has become a top priority. In this blog post, we will discuss
  how Git and ArgoCD can be used for K8s access control and disaster recovery.   Managing
  K8s access control can be a challenging task, especially in a production environment.
  However, using Git and ArgoCD can make this process easier. Git allows you to manage
  your cluster configurations as code, which means that every team member can propose
  changes to the codebase via pull requests.  With ArgoCD, you can configure access
  rules for Git repositories. This means that junior engineers can initiate or propose
  changes, but only senior engineers can approve and merge them. This gives you a
  clean way of managing cluster permissions indirectly through Git without having
  to create cluster roles and users for each team member
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/yekGLpc3vro
image_search_query: coordination security
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-07-19
pretified: true
ref: argo-cd-as-kubernetes-extension
silot_terms: container docker kubernetes
tags: []
title: Argo CD as Kubernetes extension
---

## Introduction

In modern software development, the importance of Kubernetes (K8s) is growing rapidly. As more and more companies adopt K8s, the need for efficient K8s access management has become a top priority. In this blog post, we will discuss how Git and ArgoCD can be used for K8s access control and disaster recovery.

## K8s Access Control with Git & ArgoCD

Managing K8s access control can be a challenging task, especially in a production environment. However, using Git and ArgoCD can make this process easier. Git allows you to manage your cluster configurations as code, which means that every team member can propose changes to the codebase via pull requests.

With ArgoCD, you can configure access rules for Git repositories. This means that junior engineers can initiate or propose changes, but only senior engineers can approve and merge them. This gives you a clean way of managing cluster permissions indirectly through Git without having to create cluster roles and users for each team member with different access permissions.

Furthermore, the pull model of Git and ArgoCD means that engineers only need access to the Git repository, and not the cluster directly. This way, cluster credentials don't have to be outside the cluster anymore, making managing security in all your Kubernetes clusters way easier.

## K8s Cluster Disaster Recovery with Git & ArgoCD

Disaster recovery is another important aspect of Kubernetes management. K8s cluster disaster recovery becomes super easy with Git and ArgoCD. If a cluster completely crashes, you can create a new cluster and point it to the Git repository where the complete cluster configuration is defined. This will recreate the same exact state as the previous one without any intervention from your side.

Because you've described your whole cluster in code in a declarative way, you can benefit from GitHub's principles and benefits when implementing these principles using any of GitHub's tools. While these are not specific benefits of ArgoCD itself, ArgoCD just helps implement those principles.

## Conclusion

In conclusion, K8s access control and disaster recovery are essential aspects of Kubernetes management. Git and ArgoCD can make these processes much easier, allowing you to manage your clusters efficiently and securely. With Git and ArgoCD, you can configure access rules, manage non-human user access, and recreate your K8s clusters in case of a disaster. Adopting Git and ArgoCD for K8s management is highly recommended for organizations of all sizes.