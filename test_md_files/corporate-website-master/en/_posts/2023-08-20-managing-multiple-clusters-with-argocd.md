---
author: full
categories:
- kubernetes
- docker
date: 2023-08-20
description: ArgoCD is a popular continuous delivery tool for Kubernetes, allowing
  users to deploy and manage their applications in a Kubernetes environment with ease.
  However, as organizations scale and start to work with multiple clusters, managing
  ArgoCD configuration can become more complicated. In this blog post, we will discuss
  how to work with multiple clusters using ArgoCD.   When working with multiple clusters,
  one approach is to deploy ArgoCD in each cluster separately. This way, each ArgoCD
  instance can manage the resources of its own cluster, and changes can be tested
  and rolled out independently in each environment. However, this approach can result
  in managing multiple ArgoCD instances, which can be time-consuming and require additional
  maintenance.  Another approach is to deploy ArgoCD in one cluster and configure
  it to deploy changes to multiple clusters at the same time. This way, Kubernetes
  administrators can configure and manage one ArgoCD instance, which can configure
  a fleet of clusters. This
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/mTjjFvlSLp0
image_search_query: coordination container
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-08-20
pretified: true
ref: managing-multiple-clusters-with-argocd
silot_terms: container docker kubernetes
tags: []
title: Managing Multiple Clusters with ArgoCD
---

## Managing Multiple Clusters with ArgoCD

[[2023-10-23-argocd-as-a-kubernetes-extension-advantages-and-benefits|ArgoCD]] is a popular [[2023-11-19-continuous-deployment-with-argocd|continuous]] delivery tool for [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]], allowing users to deploy and manage their [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|applications]] in a [[2020-08-13-work-with-kubernetes-with-minikube|Kubernetes]] environment with ease. However, as organizations scale and start to [[2020-08-13-work-with-kubernetes-with-minikube|work]] with multiple clusters, managing [[2023-07-30-benefits-of-using-gitops-with-argocd|ArgoCD]] configuration can become more complicated. In this blog post, we will discuss how to work with multiple clusters using ArgoCD.

### Deploying ArgoCD in Multiple Clusters

When working with multiple clusters, one approach is to deploy ArgoCD in each [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]] separately. This way, each ArgoCD instance can manage the resources of its own cluster, and changes can be tested and rolled out independently in each environment. However, this approach can result in managing multiple ArgoCD instances, which can be time-consuming and require additional maintenance.

Another approach is to deploy ArgoCD in one cluster and configure it to deploy changes to multiple clusters at the same time. This way, [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]] administrators can configure and manage one ArgoCD instance, which can configure a fleet of clusters. This approach can save time and simplify maintenance, as changes can be rolled out to multiple clusters at the same time.

### Applying Changes to Multiple Clusters

When working with multiple clusters, it is common to have different environments, such as development, staging, and production, each with their own cluster replicas. In this scenario, changes need to be tested and promoted through each environment before being rolled out to production.

One approach is to [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] multiple branches in a Git repository for each environment. For [[2023-08-25-docker-exec-bash-example|example]], development, staging, and production branches can be created, each with its own cluster configuration. However, this approach can result in maintenance overhead and require manual testing before promoting changes to the next environment.

Another approach is to [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] overlays with Customize. Overlays allow you to reuse the same base YAML [[2022-07-28-how-to-copy-files-from-host-to-docker-container|files]] and selectively change specific parts for different environments. For example, the development CI pipeline can update the template in the development overlay, the staging CI pipeline can update the template in a staging overlay, and so on. This approach allows for more automation and streamlines the process of applying changes to different environments.

### Conclusion

ArgoCD is a powerful tool for continuous delivery in [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Kubernetes]] environments, and managing multiple clusters with ArgoCD can be challenging. However, by deploying ArgoCD in multiple clusters or a single instance and using overlays, organizations can simplify the process of deploying and managing applications in their [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|Kubernetes]] environments.

Before we wrap up, we want to give a shout-out to Kasten by Veeam, who made this video possible. Kasten K10 is the data [[2023-12-15-release-management-with-tiller-in-helm-version-2|management]] [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|platform]] for [[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]], making it easy to do backup and restore operations in a [[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]] environment. With K10, you can streamline the process of managing data in [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Kubernetes]], making it [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|easier]] for cluster administrators to focus on their core tasks. [[2023-10-25-using-helm-practical-use-cases|Use]] our link to download K10 for free and get 10 nodes free forever to do your [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]] backups. Check out the link in the video description to learn more!