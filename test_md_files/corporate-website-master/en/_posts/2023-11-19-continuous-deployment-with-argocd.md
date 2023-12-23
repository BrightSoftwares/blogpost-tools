---
author: full
categories:
- kubernetes
- docker
date: 2023-11-19
description: As discussed in the previous section, setting up a continuous deployment
  workflow with Kubernetes can be challenging, especially when dealing with multiple
  projects and clusters. This is where ArgoCD comes into the picture. ArgoCD is a
  GitOps tool that provides a streamlined and automated way of deploying and managing
  applications in a Kubernetes cluster.   ArgoCD is a declarative, GitOps continuous
  delivery tool for Kubernetes. It automates the deployment of applications and provides
  a real-time view of the deployment status, which eliminates the need for manual
  updates and configuration changes. It allows users to define the desired state of
  their Kubernetes applications in a Git repository, and automatically monitors and
  updates the cluster to match that state.   ArgoCD simplifies the process of deploying
  and managing applications in a Kubernetes cluster, by automating the deployment
  process and providing real-time feedback. It allows for declarative, version-controlled
  application deployments, which eliminates the need for manual configuration changes.
  ArgoCD
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/Kygy3Xbbp-g
image_search_query: coordination
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-11-19
pretified: true
ref: continuous-deployment-with-argocd
silot_terms: container docker kubernetes
tags: []
title: Continuous Deployment with ArgoCD
---

As discussed in the previous section, setting up a continuous [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|deployment]] workflow with [[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]] can be challenging, especially when dealing with [[2023-08-20-managing-multiple-clusters-with-argocd|multiple]] projects and clusters. This is where [[2023-10-23-argocd-as-a-kubernetes-extension-advantages-and-benefits|ArgoCD]] comes into the picture. [[2023-07-30-benefits-of-using-gitops-with-argocd|ArgoCD]] is a GitOps tool that provides a streamlined and automated way of deploying and managing [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|applications]] in a [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Kubernetes]] [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]].

## What is ArgoCD?

ArgoCD is a declarative, GitOps continuous delivery tool for [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]]. It automates the deployment of applications and provides a real-time view of the deployment status, which eliminates the need for manual updates and configuration changes. It allows users to define the desired state of their [[2020-08-13-work-with-kubernetes-with-minikube|Kubernetes]] applications in a Git repository, and automatically monitors and updates the cluster to match that state.

## Why Use ArgoCD?

ArgoCD simplifies the process of deploying and managing applications in a [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]] cluster, by automating the deployment process and providing real-time feedback. It allows for declarative, [[2023-12-15-release-management-with-tiller-in-helm-version-2|version]]-controlled application deployments, which eliminates the need for manual configuration changes. ArgoCD also provides visibility into the deployment status, which enables users to quickly detect and resolve issues.

## How ArgoCD Works

ArgoCD works by continuously monitoring a Git repository for changes to the desired state of the [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|Kubernetes]] application. Once a change is detected, ArgoCD will automatically update the [[2023-12-22-convert-docker-compose-to-kubernetes|Kubernetes]] cluster to match the new desired state. This eliminates the need for manual updates and configuration changes. ArgoCD also provides a real-time view of the deployment status, which allows users to quickly detect and resolve any issues that may arise.

## Hands-On Demo

Let's set up a simple demo project using ArgoCD to deploy an application in a [[2023-11-01-helm-charts-the-package-manager-for-kubernetes|Kubernetes]] cluster.

### Prerequisites

-   A [[2023-05-14-understanding-kubernetes-the-container-orchestrator|Kubernetes]] cluster
-   ArgoCD installed and configured in the cluster
-   Access to the Git repository containing the desired state configuration [[2022-07-28-how-to-copy-files-from-host-to-docker-container|files]]

### Steps

1.  Create a new Git repository and add the application's desired state configuration files. This includes the deployment and [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|service]] YAML files.
    
2.  Configure ArgoCD to monitor the Git repository for changes to the desired state configuration files. This can be done using the ArgoCD CLI or the ArgoCD UI.
    

    
    `argocd app create my-app \ --repo https://github.com/my-org/my-repo.git \ --path ./ \ --dest-[[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|server]] https://kubernetes.default.svc \ --dest-namespace default`
    
3.  Once ArgoCD is configured, it will automatically monitor the Git repository for changes to the desired state configuration files. When a change is detected, ArgoCD will automatically update the Kubernetes cluster to match the new desired state.
    
4.  [[2021-12-14-how-to-use-local-docker-images-with-minikube|Use]] the ArgoCD UI to monitor the deployment status and detect any issues that may arise.
    

## Conclusion

In conclusion, ArgoCD is a powerful tool for streamlining the deployment process and managing applications in a Kubernetes cluster. It eliminates the need for manual updates and configuration changes, and provides real-time feedback on the deployment status. By using ArgoCD, organizations can simplify their deployment workflow, reduce manual errors, and increase the efficiency of their DevOps process.