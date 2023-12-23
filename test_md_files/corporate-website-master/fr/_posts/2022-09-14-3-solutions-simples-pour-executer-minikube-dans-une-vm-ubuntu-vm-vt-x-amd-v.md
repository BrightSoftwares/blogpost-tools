---
author: full
categories:
- kubernetes
date: 2022-09-14
description: Comment exécuter minikube dans une machine virtuelle Ubuntu vm_VT-X/AMD-v.
  En tant que développeur, j'aime avoir un environnement reproductible. Mes clients
  fournissent souvent les spécifications techniques de leur environnement et j'aime
  les reproduire localement pour être au plus proche de leur environnement. Pour pouvoir
  installer minikube sur une machine virtuelle, exécutant virtualbox, vous devez utiliser
  le bon pilote (aucun).
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1640818246/samuele-errico-piccarini-MyjVReZ5GLQ-unsplash_bm7ufa.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2022-09-14
pretified: true
ref: howtorunminikubeinavirtualmachineubuntuvm_vtxamdx
tags:
- minikube
- kubernetes
- ubuntu
- virtual-machine
- virtualbox
- driver
title: 3 solutions simples pour exécuter minikube dans une VM Ubuntu vm_VT-X/AMD-v
seo:
  links: [ "https://www.wikidata.org/wiki/Q381" ]
---

Comment exécuter minikube dans une machine virtuelle Ubuntu vm_VT-X/AMD-v


En tant que développeur, j'aime avoir un environnement reproductible. Mes clients fournissent souvent les spécifications techniques de leur environnement et j'aime les reproduire localement pour être au plus proche de leur environnement.

Pour pouvoir installer minikube sur une machine virtuelle, exécutant virtualbox, vous devez utiliser le bon pilote (aucun).

Dans ce tutoriel, je vais vous montrer comment installer et configurer minikube sur la machine virtuelle. Le système d'exploitation sera Ubuntu.

# TL;DR

Pour installer minikube sur une machine virtuelle exécutant virtualbox, suivez ces étapes :

1. Installez minikube comme vous le feriez normalement. Consultez mon tutoriel [[2020-08-13-work-with-kubernetes-with-minikube|ici]]

2. Configurez minikube pour qu'il n'utilise aucun pilote. Le pilote none ne nécessite aucune virtualisation imbriquée.
3. Installez docker-ce en suivant les instructions de votre système d'exploitation. (le mien est ubuntu)
4. Activez docker et démarrez-le
5. Démarrez minikube


# Le problème auquel je faisais face

J'étais en train d'installer minikube dans une machine virtuelle virtualbox exécutant le système d'exploitation Ubuntu. J'ai activé VT-X/AMD-v pour la machine virtuelle.

Mais j'obtiens l'erreur suivante lorsque j'essaie de démarrer mon minikube.

{% include codeHeader.html %}
{% raw %}
```
# minikube start
````
{% endraw %}

Vous obtenez cette sortie :

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

## Ce qui se passe?

**VirtualBox ne prend pas en charge VT-X/AMD-v dans la virtualisation imbriquée**. Vous pouvez [en savoir plus ici](https://www.virtualbox.org/ticket/4032) [^2]

Il existe donc peu d'approches pour résoudre ce problème :

1. Exécutez directement minilube sur ma machine, pas de VM virtualbox.
2. **Utilisez un hyperviseur différent** prenant en charge VT-X/AMD-v dans la virtualisation imbriquée (comme Xen, KVM ou VMware).
3. Exécutez Minikube directement à l'aide de Docker et de l'option de pilote "none"



# Les solutions

Il y a peu de solutions que je pourrais mettre en œuvre.

## Installer directement minikube sur ma machine

Il existe des binaires compilés pour Windows, MacOs et Linux, donc j'aurais pu installer directement minikube sur mon hôte.

### Avantages

- Facile à installer

### Les inconvénients

- Aimé à mon ordinateur
- Besoin de réinstaller et de configurer si je change d'ordinateur ou si j'ai besoin de réinstaller le système d'exploitation.
- Je ne peux pas disposer d'un environnement de test comparable avant de déployer ma solution dans l'environnement du client.

## Exécutez minikube avec le pilote none

La [documentation de kubernetes indique](https://kubernetes.io/docs/tasks/tools/install-minikube/) :

> Minikube prend également en charge une option --vm-driver=none qui exécute les composants Kubernetes sur l'hôte et non sur une VM. L'utilisation de ce pilote nécessite Docker et un environnement Linux, mais pas un hyperviseur [^1].


1. Installez docker sur la machine virtuelle VirtualBox
2. Configurez minikube pour utiliser le pilote ```none```.

{% include codeHeader.html %}
{% raw %}
```
minikube config set vm-driver none
```
{% endraw %}

3. Activer Docker sur la machine virtuelle


{% include codeHeader.html %}
{% raw %}
```
systemctl enable docker
```
{% endraw %}

Vous obtiendrez cette sortie.

{% raw %}
```
Created symlink from /etc/systemd/system/multi-user.target.wants/docker.service to /usr/lib/systemd/system/docker.service.
```
{% endraw %}

4. Exécutez le menu fixe

{% include codeHeader.html %}
{% raw %}
```
systemctl start docker
```
{% endraw %}

6. Démarrer minikube

{% include codeHeader.html %}
{% raw %}
```
minikube start
```
{% endraw %}


Vous obtiendrez cette sortie.


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


## Utiliser un autre hyperviseur

VirtualBox est un hyperviseur que vous installez sur votre machine pour héberger les machines virtuelles. Comme il ne supporte pas VT-X/AMD-v en virtualisation imbriquée, vous pouvez utiliser les alternatives :

-Xen
-KVM
-VMware
- etc.


# Conclusion

Vous pouvez installer minikube dans une VM. Mais pour le faire fonctionner, vous devez faire quelques ajustements. Mais il est possible de le réaliser.

L'exécuter à l'intérieur d'une VM vous permet d'automatiser votre workflow de développement.
Vous pouvez même penser à des outils comme vagrant pour provisionner automatiquement votre machine virtuelle afin que vous disposiez d'un environnement reproductible.


# Références

[Début de la virtualisation](https://github.com/docker/machine/issues/2256)

[^1]https://stackoverflow.com/a/52635546/5730444

[^2]https://www.virtualbox.org/ticket/4032