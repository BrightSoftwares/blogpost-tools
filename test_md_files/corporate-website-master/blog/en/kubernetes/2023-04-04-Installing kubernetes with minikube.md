---
layout: flexstart-blog-single
title: "Installing kubernetes with minikube"
author: full
lang: en
ref: installing-kubernetes-with-minikube
categories:
  - kubernetes
tags:
  - minikube
  - security
date: 2023-04-04
description: As a software developer, I often work with Kubernetes for managing and deploying my applications. However, setting up a Kubernetes cluster can be a daunting task, especially if you don't have access to a dedicated infrastructure or cloud platform.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1641156621/pexels-martijn-adegeest-633565_fcr6ri.jpg
seo:
  links: [ "https://www.wikidata.org/wiki/Q19841877" ]
toc: true
---

As a software developer, I often work with Kubernetes for managing and deploying my applications. However, setting up a Kubernetes cluster can be a daunting task, especially if you don't have access to a dedicated infrastructure or cloud platform. That's why I started exploring Minikube, a tool that allows you to run a local Kubernetes cluster on your laptop or desktop machine. In this guide, I will share the steps that I follow to install Kubernetes and Minikube on a Linux machine. By the end of this guide, you should have a working Kubernetes cluster that you can use for testing and development purposes. Whether you're new to Kubernetes or an experienced user, I hope you will find this guide helpful in setting up a local Kubernetes environment with Minikube. So let's get started!


## Step 1: Install a virtualization softwares to host kubernetes

Install a virtualization software, such as VirtualBox or KVM. For example, to install VirtualBox on Ubuntu, run:

```bash
sudo apt-get update 
sudo apt-get install virtualbox
```


## Step 2: Install kubectl to be able to interact with kubernetes

Install kubectl, the command-line tool for interacting with Kubernetes clusters. For example, to install kubectl on Ubuntu, run:

```bash
sudo apt-get update sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release 
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - 
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list 
sudo apt-get update 
sudo apt-get install -y kubectl
```


## Step 3: Install minikube to run kubernetes locally

Install Minikube, the tool for running Kubernetes clusters locally. For example, to install Minikube on Ubuntu, run:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

## Step 4: Start minikube and start enjoying

Start Minikube with the desired configuration. For example, to start Minikube with 2 CPUs and 4 GB of RAM, run:

```bash
minikube start --cpus=2 --memory=4096
```

This will download the required Docker images and start a local Kubernetes cluster using Minikube.

## Step 5: Verify that Minikube and Kubernetes are running

For example, to check the status of the Minikube cluster, run:

```bash
minikube status
```

This should show the status of the Minikube cluster, including the IP address and port of the Kubernetes API server.

That's it! You should now have a working Kubernetes cluster running locally with Minikube. You can use kubectl to interact with the cluster and deploy your applications.

Note: The configuration files for Minikube and Kubernetes are managed by the tools themselves, and you usually don't need to modify them manually. However, if you need to customize the configuration, you can find the relevant files in the Minikube and Kubernetes documentation.

## Conclusion

Congratulations! You have successfully installed Kubernetes and Minikube on your Linux machine. With this local Kubernetes cluster, you can now test, develop, and deploy your applications in a self-contained environment, without the need for a dedicated infrastructure or cloud platform. Minikube provides a user-friendly interface for managing your Kubernetes cluster, and you can use kubectl to interact with the cluster and deploy your applications. Whether you're a developer, a system administrator, or just curious about Kubernetes, this local setup is a great way to get started with the technology. Happy coding!