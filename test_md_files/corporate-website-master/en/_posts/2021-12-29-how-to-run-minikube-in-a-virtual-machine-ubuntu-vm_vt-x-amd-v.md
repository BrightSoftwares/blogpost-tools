---
author: full
categories:
- kubernetes
date: 2021-12-29 22:16:25.280000+00:00
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1640818246/samuele-errico-piccarini-MyjVReZ5GLQ-unsplash_bm7ufa.jpg
lang: en
layout: flexstart-blog-single
ref: howtorunminikubeinavirtualmachineubuntuvm_vtxamdx
seo:
  links:
  - https://www.wikidata.org/wiki/Q22661306
silot_terms: container docker kubernetes
tags:
- minikube
- kubernetes
- ubuntu
- virtual-machine
- virtualbox
- driver
title: 3 easy solutions to run minikube in an Ubuntu VM vm_VT-X/AMD-v
toc: true
---

How to [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] [[2020-08-12-play-with-kubernetes-with-minikube|minikube]] in a [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|Virtual]] [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|Machine]] Ubuntu vm_VT-X/AMD-v


As a developer, I like to have a reproducable environment. My customers often provide the technical specifications of their environment and I like to reproduce them locally so I can be the closest to their environment.

To be able to install [[2021-12-26-how-to-expose-a-port-on-minikube|minikube]] on a virtual [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|machine]], running virtualbox, you need to [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] the correct driver (none).

In this tutorial, I will [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|show]] you how to install and setup [[2020-08-13-work-with-kubernetes-with-minikube|minikube]] on the virtual machine. The operating system will be Ubuntu.

# TL;DR

To install [[2020-08-12-installing-kubernetes-with-minikube|minikube]] on a virtual machine, running virtualbox, follow these steps:

1. Install [[2021-12-26-how-to-expose-a-port-on-minikube|minikube]] as you would normally do. Check my tutorial [[2020-08-13-work-with-kubernetes-with-minikube|here]]

2. Configure [[2020-08-12-installing-kubernetes-with-minikube|minikube]] not to [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] any driver. The none driver does not require any nested virtualization.
3. Install [[2022-05-08-can-docker-connect-to-database|docker]]-ce following the instructions of your operating system. (Mine is ubuntu)
4. Enable [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|docker]] and start it 
5. Start [[2020-08-13-work-with-kubernetes-with-minikube|minikube]]


# The problem I was facing

I was tring to install [[2020-08-12-play-with-kubernetes-with-minikube|minikube]] in a virtualbox VM running Ubuntu OS. I have enabled VT-X/AMD-v for the vm. 

But i'm getting following error when I try to start my minikube.

{% include codeHeader.html %}
{% raw %}
```
# minikube start
````
{% endraw %}

You get this output :

{% raw %}
```
Starting local Kubernetes cluster...
E0217 15:00:35.395801    3869 start.go:107] Error starting host: Error creating host: Error with pre-create check: "This computer doesn't have VT-X/AMD-v enabled. Enabling it in the BIOS is mandatory".

 Retrying.
E0217 15:00:35.396019    3869 start.go:113] Error starting host:  Error creating host: Error with pre-create check: "This computer doesn't have VT-X/AMD-v enabled. Enabling it in the BIOS is mandatory"
================================================================================
An error has occurred. Would you like to opt in to sending anonymized crash
information to minikube to help prevent future errors?
To opt out of these messages, run the command:
    minikube config set WantReportErrorPrompt false
================================================================================
Please enter your response [Y/n]:
```
{% endraw %}

## What is happening?

**VirtualBox does not support VT-X/AMD-v in nested virtualisation**. You can [read more here](https://www.virtualbox.org/ticket/4032) [^2]

So there are few approaches to [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|solve]] this:

1. [[2023-04-04-should-a-docker-container-run-as-root-or-user|Run]] minilube on my machine directly, no virtualbox VM.
2. **[[2023-10-25-using-helm-practical-use-cases|Use]] a different hypervisor** that does support VT-X/AMD-v in nested virtualisation (like Xen, KVM or VMware).
3. [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|Run]] Minikube directly using [[2022-07-28-how-to-copy-files-from-host-to-docker-container|Docker]] and the "none" driver option



# The solutions

There are few solutions I could implement.

## Install minikube on my machine directly

There are compiled binaries for Windows, MacOs and Linux so I could have just installed minikube on my [[2022-07-28-how-to-copy-files-from-host-to-docker-container|host]] directly.

### Pros

- Easy to install

### Cons

- Liked to my computer
- Need to reinstall and setup if I change my computer or need to reinstall the OS.
- I can't have a comparable test environment before deploying my solution to the customer's environment.

## Run minikube with driver none

The [kubernetes documentation says](https://kubernetes.io/docs/tasks/tools/install-minikube/) :

> Minikube also supports a --vm-driver=none option that runs the [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|Kubernetes]] components on the [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|host]] and not in a VM. Using this driver requires [[2022-05-08-can-docker-connect-to-database|Docker]] and a linux environment, but not a hypervisor [^1].


1. Install [[2023-12-22-convert-docker-compose-to-kubernetes|docker]] on the VirtualBox VM
2. Configure minikube to use the ```none``` driver.

{% include codeHeader.html %}
{% raw %}
```
minikube config set vm-driver none
```
{% endraw %}

3. Enable [[2023-05-10-building-microservices-with-docker-creating-a-product-service|docker]] on the VM machine


{% include codeHeader.html %}
{% raw %}
```
systemctl enable docker
```
{% endraw %}

You will get this output.

{% raw %}
```
Created symlink from /etc/systemd/system/multi-user.target.wants/docker.service to /usr/lib/systemd/system/docker.service.
```
{% endraw %}

4. [[2023-10-29-docker-run-stopped-container|Run]] [[2023-11-17-what-is-docker-compose|docker]]

{% include codeHeader.html %}
{% raw %}
```
systemctl start docker
```
{% endraw %}

6. Start minikube

{% include codeHeader.html %}
{% raw %}
```
minikube start
```
{% endraw %}


You will get this output.


{% raw %}
```
Starting local Kubernetes v1.10.0 cluster...
Starting VM...
Getting VM IP address...
Moving files into cluster...
Downloading kubeadm v1.10.0
Downloading kubelet v1.10.0
Finished Downloading kubelet v1.10.0
Finished Downloading kubeadm v1.10.0
Setting up certs...
Connecting to cluster...
Setting up kubeconfig...
Starting cluster components...
Kubectl is now configured to use the cluster.
===================
WARNING: IT IS RECOMMENDED NOT TO RUN THE NONE DRIVER ON PERSONAL WORKSTATIONS
        The 'none' driver will run an insecure kubernetes apiserver as root that may leave the host vulnerable to CSRF attacks

When using the none driver, the kubectl config and credentials generated will be root owned and will appear in the root home directory.
You will need to move the files to the appropriate location and then set the correct permissions.  An example of this is below:

        sudo mv /root/.kube $HOME/.kube # this will write over any previous configuration
        sudo chown -R $USER $HOME/.kube
        sudo chgrp -R $USER $HOME/.kube

        sudo mv /root/.minikube $HOME/.minikube # this will write over any previous configuration
        sudo chown -R $USER $HOME/.minikube
        sudo chgrp -R $USER $HOME/.minikube

This can also be done automatically by setting the env var CHANGE_MINIKUBE_NONE_USER=true
Loading cached images from config file.
```
{% endraw %}


## Use another hypervisor

VirtualBox is an hypervisor that you install on your machine to host the virtual machines. Since it does not support VT-X/AMD-v in nested virtualisation, you can use the alternatives : 

- Xen
- KVM
- VMware
- etc.


# Conclusion

You can install minikube inside a VM. But to make it run, you need to make some adjustments. But it is possible to make it happen.

Running it inside a VM allows you to automate your development worklow.
You ca even think of tools like vagrant to provision your VM automatically to that you have a reproducable environment.


# References

[Inception of virtualization](https://github.com/docker/machine/issues/2256)

[^1]https://stackoverflow.com/a/52635546/5730444

[^2]https://www.virtualbox.org/ticket/4032