---
author: full
categories:
- docker
date: 2023-04-11
description: Docker is a popular tool used for containerization, allowing developers
  to package an application and its dependencies into a portable container. Once a
  Docker container is created, it can be run on any system with Docker installed,
  making it an ideal solution for building and deploying applications across different
  environments.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1651946261/philippe-oursel-R5IdSDngcv8-unsplash_hmqctw.jpg
lang: en
layout: flexstart-blog-single
post_date: 2023-01-18
post_inspiration: s
pretified: true
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- docker
- container
title: Explore your container with docker run
transcribed: true
youtube_video: https://www.youtube.com/watch?v=IEE6wwZ3_9s&ab_channel=KelvinMai
youtube_video_id: IEE6wwZ3_9s
---

## I. Introduction

[[2022-07-21-how-to-run-jenkins-jobs-with-docker|Docker]] is a popular tool used for containerization, allowing developers to package an application and its [[2022-03-23-how-to-solve-maven-dependencies-are-failing-with-a-501-error|dependencies]] into a portable [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|container]]. Once a [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|Docker]] [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|container]] is created, it can be run on any system with [[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|Docker]] installed, making it an ideal solution for building and deploying applications across different environments.

In this article, we'll cover the basics of running [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|Docker]] containers and the purpose of the `[[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|docker]] run` command. We'll also explore the `-it` flag and explain why it's commonly used with the `[[2020-08-04-docker-tip-inspect-and-grep|docker]] run` command.

Let's start by looking at how to run a [[2020-08-04-docker-tip-inspect-and-jq|Docker]] container.

**Example Code:**

To get started, make sure you have Docker installed on your system. Once Docker is installed, you can run a container using the following command:

```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

This command will download the specified image (if it's not already available on your system) and run a container using that image. The `OPTIONS` argument allows you to specify additional options for running the container, such as port mappings or volume mounts. The `IMAGE` argument specifies the name of the Docker image you want to [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] to create the container.

For example, the following command will run a container using the official `nginx` image:

```bash
docker run nginx
```


## II. Running a Docker Container

Docker containers can be run using the `docker run` command. This command has a basic syntax that looks like the following:


```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

Where:

-   `OPTIONS` are the various options that can be used with the command
-   `IMAGE` is the name of the Docker image to use
-   `COMMAND` (optional) is the command to run inside the container
-   `ARG` (optional) is any arguments to the command

Here are some commonly used options with the `docker run` command:

-   `-d`: Run the container in detached mode (i.e., in the background)
-   `-p`: Publish a container's port to the host
-   `-v`: Mount a host directory or a named volume as a data volume inside the container

To run a simple container, we can use the following command:

```bash
docker run hello-world
```


This will download and run the "hello-world" Docker image, which is a simple example image that prints a message to the console.

In the next section, we'll discuss the `-it` option, which is commonly used with the `docker run` command. I have prepared a post where you can explore the [[2022-08-24-what-is-difference-between-docker-attach-and-exec|difference between docker exec and docker attach]].

## III. Understanding the `docker run` Command

The `docker run` command is used to create and run a Docker container. It has a number of different options that allow you to customize how the container is created and how it runs. In this section, we will explore the different parts of the `docker run` command and their use cases.

### The `docker run` Command Structure

The basic syntax of the `docker run` command is as follows:

```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```


Here's a breakdown of the different parts of the command:

-   `docker run`: This is the basic command to run a Docker container.
    
-   `[OPTIONS]`: These are optional flags that can be used to customize how the container is created and how it runs.
    
-   `IMAGE`: This is the name of the Docker image that you want to run.
    
-   `[COMMAND] [ARG...]`: These are optional commands and arguments that will be executed inside the container.
    

### `docker run` Options

There are many options available with the `docker run` command. Here are some of the most commonly used ones:

-   `-d`: Run the container in the background (detached mode).
    
-   `-it`: Start an interactive shell inside the container.
    
-   `-p`: Publish a container's port(s) to the host.
    
-   `-v`: Mount a volume(s) from the host to the container.
    
-   `--name`: Assign a name to the container.
    
-   `--rm`: Automatically remove the container when it stops running.
    

### `docker run` Examples

#### Example 1: Running a Container in Detached Mode


```bash
docker run -d nginx
```


This command will start a container running the `nginx` image in the background (detached mode).

#### Example 2: Running a Container with a Specific Name

```bash
docker run --name my-nginx nginx
```

This command will start a container running the `nginx` image with the name `my-nginx`.

#### Example 3: Running a Container with Port Mapping

```bash
docker run -p 8080:80 nginx
```


This command will start a container running the `nginx` image and map port `80` in the container to port `8080` on the host.

#### Example 4: Running a Container with Volume Mounting


```bash
docker run -v /host/path:/container/path nginx
```


This command will start a container running the `nginx` image and mount the `/host/path` directory on the host to the `/container/path` directory in the container.

#### Example 5: Running a Container in Interactive Mode


```bash
docker run -it ubuntu bash
```

This command will start an interactive shell inside a new container running the `ubuntu` image with the `bash` command.

### Conclusion

The `docker run` command is a fundamental part of using Docker. Understanding the different options available with this command will help you customize your Docker containers to meet your needs. In the next section, we will explore the `-it` option in more detail.

Once the container is running, you can [[2020-08-04-docker-tip-inspect-and-less|get more information on it by inspecting it]].

## IV. Using the `-it` Flag with `docker run`

The `-it` flag is a commonly used option with the `docker run` command. It allows users to run a container in an interactive mode with a terminal.


### Purpose of the `-it` flag:

-   `-i`: This option stands for "interactive" and tells Docker to keep STDIN open even if not attached. It allows you to interact with the container's command prompt.

-   `-t`: This option stands for "terminal" and tells Docker to allocate a pseudo-TTY. It provides a terminal or console to the container.


### Difference between running a container with and without the `-it` flag:

-   Without `-it` flag: When a container is run without the `-it` flag, it runs in the background or detached mode. The user can view container logs but cannot interact with it.
-   With `-it` flag: When a container is run with the `-it` flag, it runs in interactive mode, and the user can interact with it as if it were a local terminal.


### Examples of using the `-it` flag with different types of containers:

-   Running a bash shell inside an Ubuntu container interactively with `-it` flag:

```bash
docker run -it ubuntu:latest /bin/bash
```

-   Running a container for an interactive Python session:

```bash
docker run -it python:3.9-slim
```


-   Running an interactive MongoDB shell with the latest image:

```bash
docker run -it mongo:latest mongo
```


Using the `-it` flag with the `docker run` command is useful when you want to interact with a container's command prompt or run a container in interactive mode.


## V. Why Use the `-it` Flag with `docker run`


The `-it` flag is a commonly used option with the `docker run` command. It stands for "interactive" and "tty," and when used, it enables an interactive session with the container. Here are some of the benefits of using the `-it` flag with `docker run`:

### Enable interactive sessions

The `-it` flag allows you to interact with the container and run commands inside the container. This is useful for debugging, testing, or running an application interactively.


### Allocate a pseudo-TTY

The `-it` flag allocates a pseudo-TTY, which simulates a real terminal device. This makes it possible to use tools like `bash` or `sh` to run commands inside the container.


### Keep STDIN open

The `-it` flag keeps STDIN open, which allows you to send input to the container. This is useful for providing input to interactive applications or scripts.


### Start a shell session

The `-it` flag can be used to start a shell session inside the container. This allows you to explore the container's [[2022-08-31-a-complete-tutorial-about-jenkins-file|file]] system, install packages, or configure the container.


Here is an example of how to use the `-it` flag with the `docker run` command:


```bash
$ docker run -it ubuntu /bin/bash
```

In this example, we are running an interactive session with an Ubuntu container and starting a shell session inside the container using the `/bin/bash` command.

### Running the python interactive inside a container

Another example is running an interactive Python script inside a container:


```bash
$ docker run -it python:3.9-slim python -i
```


This command starts an interactive Python interpreter inside the container, allowing you to run Python code and test different Python libraries.

Overall, using the `-it` flag with the `docker run` command can greatly enhance your experience with Docker containers by enabling interactive sessions, allocating a pseudo-TTY, keeping STDIN open, and starting a shell session.

## VI. Conclusion

In conclusion, running Docker containers is an essential part of modern software development and deployment. The `docker run` command is a powerful tool that allows you to create and run containers quickly and easily. Using the `-it` flag with the `docker run` command enhances the usability of containers, providing an interactive session with the container.

To summarize, in this article, we have covered the basics of running a Docker container, the `docker run` command, and the `-it` flag. We have explained how the `-it` flag works and its benefits. We hope this article has been informative and helpful in understanding the basics of running Docker containers.

If you're interested in learning more about Docker and containerization, check out these additional resources:

-   Docker documentation: [https://docs.docker.com/](https://docs.docker.com/)
-   Docker tutorial for beginners: [https://www.docker.com/101-tutorial](https://www.docker.com/101-tutorial)
-   Docker Compose documentation: [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
-   Docker Hub: [https://hub.docker.com/](https://hub.docker.com/)