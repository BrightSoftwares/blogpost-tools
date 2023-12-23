---
author: full
categories:
- kubernetes
date: 2023-04-04
description: By default, Docker containers run as the root user, which can pose security
  risks and limit the portability of your applications. In this guide, we'll explore
  how to manage Docker user permissions and run containers as different users.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/_04ev82q-s0
lang: en
layout: flexstart-blog-single
pretified: true
ref: should-a-docker-container-run-as-root-or-user
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: container docker kubernetes
tags:
- docker
- containers
- root
title: Should a docker container run as root or user
toc: true
---

## I. Introduction

[[2022-05-08-can-docker-connect-to-database|Docker]] is a popular containerization technology that allows you to [[2023-11-01-helm-charts-the-package-manager-for-kubernetes|package]] and [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|run]] [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|applications]] in a portable and isolated environment. When [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|running]] [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|Docker]] containers, it's important to consider the permissions and security of the [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]]'s users. By default, [[2021-12-14-how-to-use-local-docker-images-with-minikube|Docker]] containers [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|run]] as the root user, which can pose security risks and limit the portability of your applications.

In this [[2023-05-08-restart-docker-daemon-a-comprehensive-guide|guide]], we'll explore how to manage [[2022-05-08-can-docker-connect-to-database|Docker]] user permissions and [[2023-10-29-docker-run-stopped-container|run]] containers as different users. We'll answer common questions such as "with which user your [[2022-07-28-how-to-copy-files-from-host-to-docker-container|Docker]] [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]] runs in by default?", "how do I run a [[2023-05-14-understanding-kubernetes-the-container-orchestrator|container]] as a non-root user?", and "how do I run a [[2021-12-14-how-to-use-local-docker-images-with-minikube|Docker]] [[2023-11-22-monit-docker-container-a-comprehensive-guide|container]] as a root user?".

We'll also explain what user 1000 means in [[2023-12-22-convert-docker-compose-to-kubernetes|Docker]], how to see a [[2023-05-15-understanding-container-networking|container]]'s user ID, and provide examples of working code for running containers as different users.

By the end of this guide, you'll have a better [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|understanding]] of [[2023-05-10-building-microservices-with-docker-creating-a-product-service|Docker]] user permissions and best practices for [[2023-08-20-managing-multiple-clusters-with-argocd|managing]] user permissions in your [[2023-11-17-what-is-docker-compose|Docker]] containers.


## II. With which user your docker container runs in by default

> By default, [[2023-08-25-docker-exec-bash-example|Docker]] containers run as the root user. This means that any processes running within the container have root-level permissions, which can pose security risks if the container is compromised.

To illustrate this, let's look at an example [[2023-08-30-docker-compose-vs-dockerfile|Dockerfile]]:

```bash
FROM alpine RUN touch /root/testfile
```

This Dockerfile uses the Alpine Linux base image to create a new image that creates a file named `testfile` in the root directory. When you run a container using this image, the `testfile` will be created in the root directory of the container. However, because the container is running as the root user, the `testfile` will be created with root ownership, even though the container itself may be running with limited privileges.

This can be a security risk because an attacker who gains access to the container can potentially escalate their privileges to gain root access on the host system.


> This can be a security risk because an attacker who gains access to the container can potentially escalate their privileges to gain root access on the host system.


To mitigate this risk, it's recommended to run containers as non-root users whenever possible. In the next section, we'll explore how to run containers as different users.


_***Disclaimer:***_ Please note that the code example provided in this section is not meant to be executed as it may create a file in the root directory of the container which is not a recommended practice. Instead, it is meant to illustrate the potential security risks associated with running containers as the root user.


## III. How do I run a container as a different user?

To run a container as a different user, you can [[2023-10-25-using-helm-practical-use-cases|use]] the `--user` flag when starting the container. This flag allows you to specify the username or UID/GID of the user that the container should run as.

Here's an example of running a container as a non-root user:

```bash
docker run --user 1000 nginx
```

In this example, the `nginx` container is started with the `--user` flag set to `1000`, which is the UID of a non-root user. When the container starts, any processes running within the container will have the same permissions as the `1000` user.

You can also specify the username of the user to run the container as:

```bash
docker run --user username nginx
```

Or you can specify the UID and GID of the user:

```bash
docker run --user 1001:1001 nginx
```


In this example, the `nginx` container is started with the `--user` flag set to `1001:1001`, which specifies the UID and GID of a specific user.

**Important note:** It's important to note that not all images may have the specified user or group configured. In such cases, you may need to create a custom Docker image with the desired user or group.


Here's a working example of running a container as a non-root user with a custom Docker image:

```bash
FROM nginx 
RUN adduser --disabled-password --gecos "" myuser 
USER myuser
```


In this example, we're using the official Nginx Docker image as the base image, and then creating a new image that adds a non-root user named `myuser` with no password and no additional information. Finally, the `USER` instruction is used to switch to the `myuser` user before starting any processes.

When you run a container using this custom image, it will be run as the `myuser` user instead of the default root user. This can help mitigate potential security risks associated with running containers as the root user.


## IV. How do I run a container as a non-root user?

Running containers as a non-root user can help mitigate potential security risks associated with running containers as the root user. When a container is run as a non-root user, any processes running within the container have reduced permissions and [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|cannot]] perform actions [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|outside]] of the container's scope.

To run a container as a non-root user, you can create a new user in a Dockerfile and then use the `USER` instruction to switch to that user before starting any processes.

> To run a container as a non-root user, you can create a new user in a Dockerfile and then use the `USER` instruction to switch to that user before starting any processes.

Here's an example Dockerfile that creates a new user named `myuser` with no password and no additional information:

```bash 
FROM nginx 
RUN adduser --disabled-password --gecos "" myuser 
USER myuser
```


In this Dockerfile, we're using the official Nginx Docker image as the base image, and then creating a new image that adds a non-root user named `myuser` with no password and no additional information. Finally, the `USER` instruction is used to switch to the `myuser` user before starting any processes.

To build the image, you can use the following command:

```bash
docker build -t mynginx .
```


This will build a new Docker image named `mynginx` that includes the `myuser` user.

To run a container using this custom image, you can use the `docker run` command with the `--user` flag to specify the UID of the `myuser` user:

```bash
docker run --user 1000 mynginx
```

In this example, the `mynginx` container is started with the `--user` flag set to `1000`, which is the UID of the `myuser` user we created in the Dockerfile.


By default, Docker containers run as the root user, which can potentially pose security risks. Running containers as a non-root user can help mitigate these risks by limiting the permissions of any processes running within the container. Creating a new user in a Dockerfile and running containers as that user is a simple way to achieve this.



## V. Running Containers as the privileged User

By default, Docker containers run as the root user, which can potentially pose security risks. Running containers as the root user can allow processes running within the container to perform actions outside of the container's scope and potentially compromise the host system.

However, there may be certain scenarios where running a container as the root user is necessary. In such cases, Docker provides the `--privileged` flag to run a container as the root user with full capabilities.

To run a container as the root user using the `--privileged` flag, you can use the following command:

```bash
docker run --privileged myimage
```


In this example, the `myimage` container is started with the `--privileged` flag, which gives the container full access to the host system and runs as the root user.

It's important to exercise caution when running containers as the root user, as this can potentially compromise the host system. Only use the `--privileged` flag when absolutely necessary.


While it's generally not recommended to run containers as the root user, there may be certain scenarios where this is necessary. In such cases, Docker provides the `--privileged` flag to run a container with full capabilities and as the root user. However, it's important to exercise caution when using this flag, as it can potentially compromise the host system.


## VI. Understanding User IDs in Docker

In Docker, user IDs are assigned to users and groups within a container, and can be used to manage permissions and access control.

By default, the first user in a Docker container is assigned user ID 1000. This user is created when the container is built and is often used as the default user for running processes within the container.

In addition to user 1000, Docker also assigns other user IDs for specific purposes. For example, user ID 1001 is typically used for the `nobody` user, which is a special user account that has no privileges and is used for security purposes.

To see the user ID of a running container, you can use the `docker exec` command with the `id` command:

```bash
docker exec mycontainer id
```

In this example, the `id` command is run within the `mycontainer` container using the `docker exec` command, which displays the user ID of the container.

Understanding user IDs in Docker is important for managing permissions and access control within containers. By default, the first user in a container is assigned user ID 1000, and Docker also assigns other user IDs for specific purposes such as the `nobody` user. You can use the `docker exec` command with the `id` command to see the user ID of a running container.


## VII. Conclusion

In this article, we've explored various aspects of Docker user permissions and how to manage them. We've learned that by default, Docker containers run as the first user with ID 1000, which can pose security risks. We've also learned how to run containers as different users using the `--user` flag, and how to create and run containers as non-root users.

In addition, we've discussed the risks of running containers as the root user, and how to run containers with elevated privileges using the `--privileged` flag.

Finally, we've explored the significance of user IDs in Docker and how to see the user ID of a running container using the `docker exec` command.

By following best practices for Docker user permissions, you can ensure that your containers are secure and run with appropriate access controls.

For further learning about Docker user permissions, here are some additional resources:

-   Docker documentation on security: [https://docs.docker.com/engine/security/](https://docs.docker.com/engine/security/)
-   Docker best practices for security: [https://www.docker.com/blog/security-best-practices-for-building-a-container-image/](https://www.docker.com/blog/security-best-practices-for-building-a-container-image/)
-   Docker tutorial on user namespaces: [https://docs.docker.com/engine/security/userns-remap/](https://docs.docker.com/engine/security/userns-remap/)
-   Blog post on securing Docker containers with user namespaces: [https://www.redhat.com/sysadmin/user-namespaces-docker](https://www.redhat.com/sysadmin/user-namespaces-docker)

We hope this article has been helpful in understanding Docker user permissions and how to manage them.