---
author: full
categories:
- kubernetes
- docker
date: 2023-07-03
description: Helm is more than just a package manager for Kubernetes; it's also a
  powerful templating engine. But what exactly does that mean? Let's say you have
  an application with multiple microservices, and you want to deploy them all on your
  Kubernetes cluster. Each microservice has its own deployment and service configuration,
  with only minor differences like the application name or version number. Without
  Helm, you would need to create separate YAML files for each microservice. But with
  Helm, you can define a common blueprint for all microservices and replace dynamic
  values with placeholders, creating a template file.   A template file is a standard
  YAML file that includes placeholders for values that will change. You can define
  these dynamic values in an additional YAML file called Values.yaml. Here, you can
  define all the values that you will use in your template file. For instance, if
  you have four values to define, you can add them to your Values.yaml
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/fN603qcEA7g
image_search_query: container rules
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q22661306
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-07-03
pretified: true
ref: using-helm-as-a-templating-engine
silot_terms: container docker kubernetes
tags: []
title: Using Helm as a Templating Engine
---

Helm is more than just a package manager for Kubernetes; it's also a powerful templating engine. But what exactly does that mean? Let's say you have an application with multiple microservices, and you want to deploy them all on your Kubernetes cluster. Each microservice has its own deployment and service configuration, with only minor differences like the application name or version number. Without Helm, you would need to create separate YAML files for each microservice. But with Helm, you can define a common blueprint for all microservices and replace dynamic values with placeholders, creating a template file.

## Using a Template File

A template file is a standard YAML file that includes placeholders for values that will change. You can define these dynamic values in an additional YAML file called Values.yaml. Here, you can define all the values that you will use in your template file. For instance, if you have four values to define, you can add them to your Values.yaml file as shown:



```
service:
  name: my-microservice
  port: 8080
  type: ClusterIP
  selector:
    app: my-microservice

```

## Using the Values Object

In your template file, you can use placeholders for values by using the syntax `{{ .Values.valueName }}`. This syntax tells Helm to take a value from the external configuration file, which in this case is the Values.yaml file. The `.Values` object is created based on the values supplied via the Values.yaml file and the `--set` flag in the command line. All additional values are combined and put together in the `.Values` object, which you can use in your template files to get the values out.

For example, suppose you have a template file with the following contents:



```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.service.name }}-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{ .Values.service.name }}
```

In this file, the placeholders `{{ .Values.service.name }}` and `{{ .Values.service.port }}` will be replaced with the corresponding values from your Values.yaml file at runtime. This way, instead of having a YAML file for each microservice, you just have one template file that you can reuse by dynamically replacing the values.

## Benefits of Using Helm as a Templating Engine

Using Helm as a templating engine offers several benefits. First, it simplifies the configuration process by reducing the number of configuration files you need to manage. Instead of writing a separate YAML file for each microservice, you can use a single template file and replace the dynamic values. Additionally, it makes it easier to manage changes across multiple microservices. When you need to make a change, you only need to modify the template file and Helm will propagate the changes across all microservices that use that template.

Furthermore, Helm can manage dependencies between microservices, making it easier to deploy and manage complex applications. By using Helm charts, you can package multiple microservices together, along with their dependencies, and distribute them as a single unit. Finally, Helm offers the ability to create and manage your own Helm charts or use charts that others have created and shared, making it easier to reuse configuration across different projects.

## Conclusion

In conclusion, Helm is a powerful tool that simplifies the deployment and configuration of Kubernetes applications. By using Helm as a templating engine, you can reduce the number of configuration files you need to manage and simplify the deployment process for complex applications.