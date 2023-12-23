---
author: full
categories:
- kubernetes
- docker
date: 2023-10-23
description: ArgoCD is a powerful tool that is designed to simplify the deployment
  of applications to Kubernetes clusters. It allows you to manage your cluster configuration
  as code, which means you can store it in a Git repository and make changes in a
  declarative way. But what makes ArgoCD unique is the fact that it's deployed directly
  in the Kubernetes cluster and acts as an extension to the Kubernetes API. In this
  article, we'll explore the advantages and benefits of using ArgoCD as a Kubernetes
  extension.   When you deploy ArgoCD in your Kubernetes cluster, it becomes an extension
  to the Kubernetes API. It leverages Kubernetes resources and uses existing Kubernetes
  functionalities for doing its job. For instance, it uses the Kubernetes ID for storing
  the data and uses Kubernetes controllers for monitoring and comparing the actual
  and desired state of the application.  One of the benefits of using ArgoCD as a
  Kubernetes extension is the visibility
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/gUIJ0YszPig
image_search_query: coordination
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-10-23
pretified: true
ref: argocd-as-a-kubernetes-extension-advantages-and-benefits
silot_terms: container docker kubernetes
tags: []
title: 'ArgoCD as a Kubernetes Extension: Advantages and Benefits'
---

[[2023-08-20-managing-multiple-clusters-with-argocd|ArgoCD]] is a powerful tool that is designed to simplify the [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|deployment]] of [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|applications]] to [[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]] clusters. It allows you to manage your [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]] configuration as code, which means you can store it in a Git repository and make changes in a declarative way. But what makes [[2023-11-19-continuous-deployment-with-argocd|ArgoCD]] unique is the fact that it's deployed directly in the [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Kubernetes]] cluster and acts as an extension to the [[2023-04-04-should-a-docker-container-run-as-root-or-user|Kubernetes API]]. In this article, we'll explore the advantages and [[2023-07-30-benefits-of-using-gitops-with-argocd|benefits]] of using ArgoCD as a [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]] extension.

## ArgoCD as a Kubernetes Extension

When you deploy ArgoCD in your [[2020-08-13-work-with-kubernetes-with-minikube|Kubernetes]] cluster, it becomes an extension to the [[2022-05-08-can-docker-connect-to-database|Kubernetes API]]. It leverages [[2021-12-26-how-to-expose-a-port-on-minikube|Kubernetes resources]] and uses existing [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]] functionalities for doing its job. For instance, it uses the [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|Kubernetes]] ID for storing the data and uses [[2023-12-22-convert-docker-compose-to-kubernetes|Kubernetes]] controllers for monitoring and comparing the actual and desired state of the application.

One of the benefits of using ArgoCD as a [[2023-11-01-helm-charts-the-package-manager-for-kubernetes|Kubernetes]] extension is the visibility it provides. ArgoCD gives you real-time updates of the application state that other tools, such as Jenkins, do not have. It can monitor the deployment state after the application is deployed or after changes in the cluster configuration have been made. This means that when you deploy a new application [[2023-12-15-release-management-with-tiller-in-helm-version-2|version]], you can see in real-time in the ArgoCD UI that configuration [[2022-07-28-how-to-copy-files-from-host-to-docker-container|files]] were applied, pods were created, and the application is [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|running]] in a healthy state. In case of a failure, you can quickly detect it and initiate a rollback.

## Advantages of Using ArgoCD as a Kubernetes Extension

There are several advantages of using ArgoCD as a [[2023-05-14-understanding-kubernetes-the-container-orchestrator|Kubernetes]] extension:

### 1. Real-time monitoring and updates

As mentioned earlier, ArgoCD provides real-time updates of the application state, which allows you to detect failures and initiate rollbacks quickly.

### 2. Improved visibility

By acting as an extension to the [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|Kubernetes API]], ArgoCD provides improved visibility into the application state, which can be invaluable in troubleshooting and monitoring.

### 3. Improved security

By running inside the Kubernetes cluster, ArgoCD eliminates the need to expose cluster credentials [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|outside]] the cluster. This makes managing security in all your Kubernetes clusters much easier.

### 4. Easy cluster access management

ArgoCD allows you to configure access rules easily. You can define who can initiate or propose changes to the cluster and who can approve and merge those requests. This gives you a clean way of managing cluster permissions indirectly through Git without having to create cluster roles and users for each team member with different access permissions.

### 5. Benefit of using Git

By using Git to store your cluster configuration, you can make changes in a declarative way and store them as code. This means that you can recreate the same exact state of the cluster in case of a disaster without any intervention from your side.

## Conclusion

ArgoCD is a powerful tool that provides several benefits when used as a Kubernetes extension. By leveraging the [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|Kubernetes API]] and resources, ArgoCD provides real-time monitoring and updates, improved visibility, improved security, easy cluster access management, and the benefit of using Git to manage your cluster configuration. If you're looking for a tool to simplify your [[2021-12-14-how-to-use-local-docker-images-with-minikube|Kubernetes deployment]], ArgoCD is definitely worth considering.