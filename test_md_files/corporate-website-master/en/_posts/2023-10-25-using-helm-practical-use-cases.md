---
author: full
categories:
- kubernetes
- docker
date: 2023-10-25
description: 'Helm is a versatile tool that offers many benefits for developers using
  continuous delivery and continuous integration for their applications. Here are
  two practical use cases where Helm''s features can help streamline your workflow:   Helm''s
  templating engine allows you to template ML files and replace their values on-the-fly
  before deploying them. This is particularly useful when deploying microservices
  that share a lot of common configuration but have small differences in application
  name, version, or image tags. Instead of writing separate ML files for each microservice,
  you can define a common blueprint and use placeholders for dynamic values. You can
  then use an additional YAML file to define the values that will replace these placeholders.  For
  example, you can define values for your microservice in a `values.yaml` file and
  use the `{{ .Values }}` syntax in your template file to reference them. You can
  also define values through the command line using the `--set` flag. All these'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/9c6j-akotJQ
image_search_query: container rules
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-10-25
pretified: true
ref: using-helm-practical-use-cases
silot_terms: container docker kubernetes
tags: []
title: 'Using Helm: Practical Use Cases'
---

[[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Helm]] is a versatile tool that offers many [[2023-10-23-argocd-as-a-kubernetes-extension-advantages-and-benefits|benefits]] for developers using [[2023-11-19-continuous-deployment-with-argocd|continuous]] delivery and continuous integration for their [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|applications]]. Here are two practical [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] cases where [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|Helm]]'s features can help streamline your workflow:

### 1. Dynamic Configuration

[[2023-11-01-helm-charts-the-package-manager-for-kubernetes|Helm]]'s templating engine allows you to template ML [[2022-07-28-how-to-copy-files-from-host-to-docker-container|files]] and replace their values on-the-fly before deploying them. This is particularly useful when deploying [[2023-05-10-building-microservices-with-docker-creating-a-product-service|microservices]] that share a lot of common configuration but have small differences in application name, [[2023-12-15-release-management-with-tiller-in-helm-version-2|version]], or image tags. Instead of writing separate ML files for each microservice, you can define a common blueprint and use placeholders for dynamic values. You can then use an additional YAML file to define the values that will replace these placeholders.

For [[2023-08-25-docker-exec-bash-example|example]], you can define values for your microservice in a `values.yaml` file and use the `{{ .Values }}` syntax in your template file to reference them. You can also define values through the command line using the `--set` flag. All these values are combined and put together in a `.Values` object that you can use in your template files to get the values out.

### 2. Deploying to Multiple Clusters

Another use case for Helm is deploying the same set of applications across different [[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]] [[2023-08-20-managing-multiple-clusters-with-argocd|clusters]]. Consider a scenario where you want to deploy your microservice application on development, staging, and production clusters. Instead of deploying individual ML files separately in each [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]], you can package them up into an application chart that includes all the necessary ML files for that particular deployment. You can then use this chart to redeploy the same application in each cluster.

## Example Code

Here's an example of how you can use Helm to deploy an application chart:



```bash
$ helm install myapp ./mychart
```

This command installs an application chart named `mychart` and gives it the release name `myapp`. You can also use the `--set` flag to specify values for the chart:



```bash
$ helm install myapp ./mychart --set app.name=myapp --set app.version=1.0
```

This command installs the same chart but sets values for the `app.name` and `app.version` placeholders in the template file.


## Benefits of using Helm

1.  Standardization Using Helm, you can standardize the deployment process for your microservices, making it easier to deploy and manage them across different environments. By creating a chart for each microservice, you can define the desired state of your deployment, including the number of replicas, resource requirements, and other configuration options.
    
2.  Flexibility Helm allows you to define your own custom templates for your deployment files, making it easy to configure your microservices with different values depending on the environment. This means that you can deploy the same application to different environments, such as development, staging, and production, with different configurations.
    
3.  Reusability Using Helm, you can create reusable charts that can be shared across your organization. By defining charts for your microservices, you can easily deploy them to different environments without having to rewrite deployment files for each environment.
    
4.  Versioning Helm provides versioning for your charts, which allows you to track changes to your deployments over time. This makes it easier to roll back to a previous version of a deployment if there are issues with the current version.
    

## Conclusion

Helm is a powerful tool for deploying and managing microservices on [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]]. By using Helm, you can standardize your deployment process, make your deployments more flexible and reusable, and track changes to your deployments over time. If you're using [[2020-08-13-work-with-kubernetes-with-minikube|Kubernetes]] to manage your microservices, Helm is definitely worth considering.