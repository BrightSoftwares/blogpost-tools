---
author: full
categories:
- kubernetes
date: 2023-12-15
description: 'In this blog post I''m gonna explain all the main concepts of Helm so
  that you''re able to use it in your own projects. Also, Helm changes a lot from
  version to version, so understanding the basic common principles and more importantly
  its use cases to when and why we use Helm will make it easier for you to use it
  in practice no matter which version you choose. So the topics I''m gonna go through
  in this blog post are: Helm and Helm Charts what they are, how to use them, and
  in which scenarios they''re used, and also what is Tiller and what part it plays
  in the Helm architecture. So what is Helm? Helm has a.     Couple of main features
  that it''s useful. The first one is as a package manager for Kubernetes, so you
  can think of it as apt yum or home Brewer for Kubernetes. So it''s a convenient
  way for'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/851_Smpkk-U
image_search_query: container transportation
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-12-15
pretified: true
ref: release-management-with-tiller-in-helm-version-2
silot_terms: container docker kubernetes
tags: []
title: Release Management with Tiller in Helm Version 2
transcribed: true
youtube_blog post: https://youtu.be/-ykwb1d0DXU
youtube_blog post_id: -ykwb1d0DXU
---

[[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|Helm]], the popular [[2023-12-22-convert-docker-compose-to-kubernetes|Kubernetes]] [[2023-11-01-helm-charts-the-package-manager-for-kubernetes|package]] manager, comes in two versions: version 2 and version 3. While version 3 introduced several changes and improvements over version 2, it's important to understand the differences between the two versions.

One of the key differences between [[2023-10-25-using-helm-practical-use-cases|Helm]] version 2 and version 3 is in the way release management is handled. In version 2, the [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Helm]] installation comes in two parts: the Helm client and the [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|server]], also known as Tiller.

## Helm Version 2 Architecture

In version 2 of Helm, whenever you deploy a Helm chart using the command `helm install my-chart`, the Helm client sends the values file to Tiller. Tiller runs in a [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|Kubernetes]] [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]] and creates components from the values file inside the cluster.

The architecture of Helm version 2 offers an additional valuable feature, which is Release Management. Whenever you create or change a [[2023-11-19-continuous-deployment-with-argocd|deployment]], Tiller stores a [[2022-07-28-how-to-copy-files-from-host-to-docker-container|copy]] of each configuration client for future reference. This creates a history of chart executions, allowing you to roll back changes in case an upgrade goes wrong.

## Helm Upgrade and Helm Rollback

With Release Management in Helm version 2, when you execute the command `helm upgrade chart-name`, the changes will be applied to the existing deployment instead of removing it and [[2023-05-10-building-microservices-with-docker-creating-a-product-service|creating]] a new one. This is possible because of the chart execution history that Tiller keeps whenever you send requests from the Helm client to Tiller.

In case an upgrade goes wrong, for [[2023-08-25-docker-exec-bash-example|example]], if some values files are faulty or if some configurations are incorrect, you can roll back the upgrade using the command `helm rollback chart-name`. This will revert the deployment to the previous version.

## Drawbacks of the Tiller Setup

However, there are some drawbacks to the Tiller setup in Helm version 2. One of the biggest issues is security. Tiller runs as a privileged [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|service]] account, which means it has full access to the [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|Kubernetes API]]. This can be a security risk in certain environments.

Additionally, the Tiller service is not supported in [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]] [[2023-08-20-managing-multiple-clusters-with-argocd|clusters]] with Role-Based Access Control (RBAC) enabled by default, which is an important security feature. In such environments, users have to manually set up RBAC for Tiller, which can be complex and error-prone.

## Conclusion

Release Management is a crucial aspect of Helm, and Tiller in Helm version 2 offers a robust solution for managing releases. However, the security concerns associated with Tiller make it less than ideal for certain environments.

In version 3 of Helm, Tiller has been removed, and release management is handled differently, addressing many of the security concerns. However, for those still using Helm version 2, it's important to understand the architecture of Tiller and how it handles release management.