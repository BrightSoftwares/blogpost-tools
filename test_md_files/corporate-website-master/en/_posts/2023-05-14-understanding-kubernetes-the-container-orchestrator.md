---
author: full
categories:
- kubernetes
date: 2023-05-14
description: Ovehttps://www.digitalocean.com/community/cheatsheets/getting-started-with-kubernetes-a-kubectl-cheat-sheet
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551333/pexels-martin-dalsgaard-11279594_p4iavf.jpg
image_search_query: container transportation
lang: en
layout: flexstart-blog-single
post_date: 2023-05-14
pretified: true
ref: understanding-kubernetes-the-container-orchestrator
silot_terms: container docker kubernetes
tags: []
title: 'Understanding Kubernetes: The Container Orchestrator'
transcribed: true
youtube_video: https://www.youtube.com/watch?v=cC46cg5FFAM&ab_channel=GoogleCloudTech
youtube_video_id: cC46cg5FFAM
---

If you've been hearing a lot about [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]] lately, you're not alone. This open source [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|platform]] for [[2023-08-20-managing-multiple-clusters-with-argocd|managing]] containerized workloads and services has gained widespread popularity, and it's time to understand why. In this article, we'll go over the concepts that make [[2020-08-13-work-with-kubernetes-with-minikube|Kubernetes]] so powerful, scalable, and useful.

## What is Kubernetes?

At its core, [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]] is a [[2023-04-04-should-a-docker-container-run-as-root-or-user|container]] orchestrator. It ensures that each [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]] is [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|running]] where it's supposed to be and that all containers can [[2020-08-13-work-with-kubernetes-with-minikube|work]] together. Think of it like a conductor managing an orchestra: just as a conductor ensures that each instrument is playing at the right time, [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Kubernetes]] ensures that services are running smoothly the way an app developer wants.

## Why was Kubernetes created?

To understand why [[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]] was created, we need to first understand the challenges of monolithic [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|applications]]. These applications put all functionality, like transactions and third-party integrations, into a single deployable artifact. While monoliths are still a common way to build applications, they have their downfalls. Deployments can take a long time, and if different parts of the monolith are managed by different teams, there could be a lot of additional complexity when preparing for a rollout. Scaling has the same problem: teams have to throw resources at the entire application, even if the bottleneck is only in a single area.

This is where [[2023-05-10-building-microservices-with-docker-creating-a-product-service|microservices]] come in. Each piece of functionality is split into smaller, individual artifacts, making it [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|easier]] to update and scale. However, having one [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|machine]] for each [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|service]] would require a lot of resources and machines. This is where containers come in. With containers, teams can [[2023-11-01-helm-charts-the-package-manager-for-kubernetes|package]] their services neatly, along with all necessary dependencies and configuration.

## How does Kubernetes help?

[[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]] manages containers on [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|virtual]] machines or nodes, grouping them together as a [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]]. Each [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]] has endpoints for DNS, storage, and scalability, automating most of the repetition and inefficiencies of doing everything by hand. The app developer tells [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Kubernetes]] what it wants the cluster to look like, and [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]] makes it happen.

## Is Kubernetes right for your application?

While [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]] may sound amazing, microservices still have their own unique challenges, and sometimes a monolith can be the right solution based on the application itself. However, monoliths can still [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] on [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|Kubernetes]], though they won't be able to [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] all the same [[2023-10-23-argocd-as-a-kubernetes-extension-advantages-and-benefits|benefits]].


## Benefits of Kubernetes

[[2023-12-22-convert-docker-compose-to-kubernetes|Kubernetes]] makes it easy to manage containers, and provides a [[2022-07-28-how-to-copy-files-from-host-to-docker-container|host]] of [[2023-07-30-benefits-of-using-gitops-with-argocd|benefits]] to app developers, including:

-   Automation: Kubernetes automates most of the repetition and inefficiencies of managing containers, making it easier for developers to focus on writing code.
    
-   Scalability: Kubernetes can scale up and down containers based on demand, making it easy to avoid bottlenecks without overprovisioning.
    
-   Resilience: Kubernetes ensures that containers are always running and can recover from failures without manual intervention.
    
-   Portability: Kubernetes makes it easy to move containers between environments, making it easier to develop and deploy applications across multiple environments.
    
-   Declarative configuration: [[2022-05-08-can-docker-connect-to-database|Kubernetes uses]] declarative configuration, which means that developers can describe the desired state of the system, and Kubernetes will make it happen.
    

## Getting Started with Kubernetes

If you're interested in getting started with Kubernetes, the first step is to start using containers. We'll cover more about containers in our next article.


Kubernetes is a powerful platform for managing containerized workloads and services. It provides automation, scalability, resilience, portability, and declarative configuration, making it easy for developers to manage containers and focus on writing code. While Kubernetes is not the right solution for every application, it is a powerful tool that every developer should have in their toolkit. If you're interested in getting started with Kubernetes, the first step is to start using containers. That's easier said than done, but it's a critical first step towards building scalable, resilient applications.


Thanks for reading, and stay tuned for more! If you want to get hands-on, check out the link in the description, and if you enjoyed this article, subscribe for more.