---
author: full
categories:
- kubernetes
date: 2021-12-14 13:42:20.890000+00:00
image: https://sergio.afanou.com/assets/images/image-midres-5.jpg
lang: en
layout: flexstart-blog-single
ref: howtouselocaldockerimageswithminikube
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: container docker kubernetes
title: 4 easy steps to use local docker images with Minikube
toc: true
---

I have previously shared a short [[2020-08-13-work-with-kubernetes-with-minikube|tutorial on Minikube]], and while I was using it, I thought I would reuse my local images directly, without uploading and then downloading them again.

## Two things I have tried (and didn't work)

### Import the images using ##@@10000@@##

I first cleaned the instances of [[2020-08-12-play-with-kubernetes-with-minikube|minikube]] and start fresh to make sure that the is no collision.


{% include codeHeader.html %}
{% raw %}
```
kubectl run hdfs --image=fluxcapacitor/hdfs:latest --port=8989
kubectl run hdfs --image=fluxcapacitor/hdfs:latest --port=8989 imagePullPolicy=Never
```
{% endraw %}

And the output was :

{% include codeHeader.html %}
{% raw %}
```
NAME                    READY     STATUS              RESTARTS   AGE
hdfs-2425930030-q0sdl   0/1       ContainerCreating   0          10m
```
{% endraw %}

As you see, it get stuck on some status but it never reach the ready state.


### Create a local registery

The idea here is to create a local registry and put my images into it. With that, I don't need to upload then download my images.

That didn't [[2020-08-13-work-with-kubernetes-with-minikube|work]] either.

## The solution

The solution was to [[2023-10-25-using-helm-practical-use-cases|use]] the ```eval $(minikube docker-env)```.

The steps are:

### Step 1 : Set the environment variables

To set your environment variables, use the command :

{% include codeHeader.html %}
{% raw %}
```
eval $(minikube docker-env)
```
{% endraw %}


### Step 2: Build the image with the daemon of minikube

To build the image use this command :

{% include codeHeader.html %}
{% raw %}
```
docker build -t my-image
```
{% endraw %}

Of source, replace ```my-image``` with your image name.

### Step 3: Set the image in the kubernetes pod

Use the tag in the [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|kubernetes]] pod.
Eg: ```my-image```


### Step 4: Tell kubernetes not to download the image anymore

To achieve that, you need to use the ```imagePullPolicy``` to ```Never```.

More information here: [How to set imagePullPolicy to never](https://kubernetes.io/docs/concepts/containers/images/#updating-images).


## Tips and pilfalls

### Run the env command in all your terminals

Make sure you [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] the ```eval $(minikube docker-env)``` in all your terminal. You will have the environment variables in all of them. 

If not, some of the commands my fail because of the lack of these variables.

### If you close your terminal, rerun eval $(minikube docker-env)

Once you close your terminal, the environment variables are cleared.

If you then build your images, they won't update in [[2021-12-26-how-to-expose-a-port-on-minikube|minikube]]. You will think that it is not working, but it is because the environment variables are not there.

### Exit from minikube?

If you want to exit from [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|minikube]], [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] this command :

{% include codeHeader.html %}
{% raw %}
```
eval $(minikube docker-env -u)
```
{% endraw %}


## Conclusion

This tutorial shows you how you can use your local image with [[2020-08-12-installing-kubernetes-with-minikube|minikube]] without uploading then downloading them.

Watchout for the pitfalls.

Once you have use your local images, you may want to [[2021-12-26-how-to-expose-a-port-on-minikube|expose]] the services ports to access them. [[2021-12-26-how-to-expose-a-port-on-minikube|This tutorial]] shows you how.

There are also a very interesting post on [[2020-07-05-how-to-configure-jenkins-with-ssl-using-an-nginx-reverse-proxy-on-ubuntu-2004|using a nice url for your application using a reverse proxy and nginx]].




## References

[This readme](https://github.com/kubernetes/minikube/blob/0c616a6b42b28a1aab8397f5a9061f8ebbd9f3d9/README.md#reusing-the-docker-daemon)

[This stackoverflow post](https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube)