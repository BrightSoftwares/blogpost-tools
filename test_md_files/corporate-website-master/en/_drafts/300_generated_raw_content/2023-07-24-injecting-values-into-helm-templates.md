---
author: full
categories:
- kubernetes
- docker
date: 2023-07-24
description: Helm, a popular package manager for Kubernetes, is widely used in the
  DevOps community to automate application deployment and management. One of the key
  features of Helm is its ability to inject values into templates, allowing for flexible
  and customizable deployments.   To understand how values are injected into Helm
  templates, let's take a closer look at the `values.yaml` file. This file contains
  default values for various parameters such as `Image`, `Name`, `Port`, and `Version`.
  These default values can be overridden in a few different ways.  One way is to provide
  an alternative values file using the `--values` flag when executing the `helm install`
  command. For example, if the `values.yaml` file has the aforementioned parameters,
  you can create your own values file called `my-values.yaml` and override one or
  more of those values. These values will then be merged into a `.Values` object that
  can be used in your templates.  Alternatively, you can provide individual values
  using
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/uBe2mknURG4
image_search_query: container rules
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-07-24
pretified: true
ref: injecting-values-into-helm-templates
silot_terms: container docker kubernetes
tags: []
title: Injecting Values into Helm Templates
---

Helm, a popular package manager for Kubernetes, is widely used in the DevOps community to automate application deployment and management. One of the key features of Helm is its ability to inject values into templates, allowing for flexible and customizable deployments.

## Understanding Values Injection

To understand how values are injected into Helm templates, let's take a closer look at the `values.yaml` file. This file contains default values for various parameters such as `Image`, `Name`, `Port`, and `Version`. These default values can be overridden in a few different ways.

One way is to provide an alternative values file using the `--values` flag when executing the `helm install` command. For example, if the `values.yaml` file has the aforementioned parameters, you can create your own values file called `my-values.yaml` and override one or more of those values. These values will then be merged into a `.Values` object that can be used in your templates.

Alternatively, you can provide individual values using the `--set` flag. This allows you to define values directly on the command line, but it's generally better to store them in a separate file for better organization and manageability.

## The Helm Chart Structure

Before we dive deeper into how values are injected, let's take a quick look at the structure of a Helm chart. A chart is typically made up of the following directories:

-   **Chart.yaml**: This file contains metadata about the chart such as its name, version, and dependencies.
    
-   **values.yaml**: This file contains default values for the chart's parameters.
    
-   **charts**: This directory contains dependencies for the chart, such as other charts that it depends on.
    
-   **templates**: This directory contains the template files that are used to generate the Kubernetes manifests.
    

## Injecting Values into Templates

When Helm deploys a chart, it fills in the template files in the `templates` directory with the values from the `values.yaml` file. This produces valid Kubernetes manifests that can be deployed into Kubernetes.

For example, suppose you have a `deployment.yaml` template file that looks like this:



```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.Name }}-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{ .Values.Name }}
  template:
    metadata:
      labels:
        app: {{ .Values.Name }}
    spec:
      containers:
        - name: {{ .Values.Name }}-container
          image: {{ .Values.Image }}:{{ .Values.Version }}
          ports:
            - containerPort: {{ .Values.Port }}
```

In this example, we're using the `.Values` object to inject values from the `values.yaml` file into the template. For instance, the `Name` parameter is injected into the `metadata.name` field, and the `Image`, `Version`, and `Port` parameters are injected into the `image`, `ports`, and `containerPort` fields, respectively.

By overriding the default values in the `values.yaml` file, you can customize the values that are injected into the templates. This allows you to deploy the same chart with different parameter values, which is useful when deploying applications across different environments such as development, staging, and production.

## Conclusion

Values injection is a powerful feature of Helm that allows for flexible and customizable deployments. By providing alternative values files or individual values using flags, you can easily customize the parameters of your chart. When deploying a chart, Helm fills in the templates with the values from the `values.yaml` file, producing valid Kubernetes manifests that can be deployed into Kubernetes.