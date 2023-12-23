---
author: full
categories:
- kubernetes
description: Minikube is a tool that makes it easy to run Kubernetes locally. Minikube
  runs a single-node Kubernetes cluster inside a Virtual Machine (VM) on your laptop
  for users looking to try out Kubernetes or develop with it day-to-day.
image: https://sergio.afanou.com/assets/images/image-midres-38.jpg
lang: en
layout: flexstart-blog-single
ref: playingkubernetes_1246
seo:
  links:
  - https://www.wikidata.org/wiki/Q22661306
silot_terms: database cli ubuntu
title: Playing Kubernetes with Minikube
toc: true
---

# Installing Kubernetes with Minikube

Minikube is a tool that makes it easy to run Kubernetes locally. Minikube runs a single-node Kubernetes cluster inside a Virtual Machine (VM) on your laptop for users looking to try out Kubernetes or develop with it day-to-day.


## Minikube Features[ ](#minikube-features)

Minikube supports the following Kubernetes features:

- DNS
- NodePorts
- ConfigMaps and Secrets
- Dashboards
- Container Runtime: [Docker](https://www.docker.com/), [CRI-O](https://cri-o.io/), and [containerd](https://github.com/containerd/containerd)
- Enabling CNI (Container [[2023-02-24-how-to-optimize-network-traffic-for-a-database|Network]] Interface)
- Ingress
  Installation[ ](#installation)

---

See [[2020-08-12-installing-kubernetes-with-minikube|Installing Minikube]].


## Quickstart[ ](#quickstart)

This brief demo guides you on how to start, use, and delete Minikube locally. Follow the steps given below to start and explore Minikube.


1. Start Minikube and create a cluster:

```
minikube start 
```

The output is similar to this:

```
Starting local Kubernetes cluster... 
Running pre-create checks... 
Creating machine... 
Starting local Kubernetes cluster... 
```

For more information on starting your cluster on a specific Kubernetes version, VM, or container runtime, see [Starting a Cluster](#starting-a-cluster).



2. Now, you can interact with your cluster using kubectl. For more information, see [Interacting with Your Cluster](#interacting-with-your-cluster).

Let’s create a Kubernetes Deployment using an existing image named echoserver, which is a simple HTTP server and expose it on port 8080 using --port.


{% include codeHeader.html %}
{% raw %}
```
kubectl create deployment hello-minikube --image=k8s.gcr.io/echoserver:1.10
```
{% endraw %}


The output is similar to this:

{% include codeHeader.html %}
{% raw %}
```
deployment.apps/hello-minikube created 
```
{% endraw %}



3. To [[2023-03-21-how-to-secure-a-remote-database-from-unauthorized-access|access]] the hello-minikube Deployment, expose it as a Service:

{% include codeHeader.html %}
{% raw %}
```
kubectl expose deployment hello-minikube --type=NodePort --port=8080
```
{% endraw %}


The option `--type=NodePort` specifies the type of the Service.

The output is similar to this:

{% include codeHeader.html %}
{% raw %}
```
service/hello-minikube exposed
```
{% endraw %}



4. The hello-minikube Pod is now launched but you have to wait until the Pod is up before accessing it via the exposed Service.

Check if the Pod is up and running:


{% include codeHeader.html %}
{% raw %}
```
kubectl get pod 
```
{% endraw %}


If the output shows the STATUS as ContainerCreating, the Pod is still being created:

{% include codeHeader.html %}
{% raw %}
```
NAME READY STATUS RESTARTS AGE hello-minikube-3383150820-vctvh 0/1 ContainerCreating 0 3s
```
{% endraw %}

If the output shows the STATUS as Running, the Pod is now up and running:

{% include codeHeader.html %}
{% raw %}
```
NAME READY STATUS RESTARTS AGE hello-minikube-3383150820-vctvh 1/1 Running 0 13s 5.
```
{% endraw %}


Get the URL of the exposed Service to view the Service details:

{% include codeHeader.html %}
{% raw %}
```
minikube service hello-minikube --url 6. 
```
{% endraw %}


To view the details of your local cluster, copy and paste the URL you got as the output, on your browser.

The output is similar to this:

{% include codeHeader.html %}
{% raw %}
```
Hostname: hello-minikube-7c77b68cff-8wdzq 
Pod Information: -no pod information available
- Server values: server_version=nginx: 1.13.3 
- lua: 10008 Request Information: client_address=172.17.0.1 method=GET real path=/ query= request_version=1.1 request_scheme=http request_uri=http://192.168.99.100:8080/ 
Request Headers: accept=_/_ 
host=192.168.99.100:30674 user-agent=curl/7.47.0 
Request Body: -no body in request- 
```
{% endraw %}


If you no longer want the Service and cluster to run, you can delete them.



7. Delete the hello-minikube Service:


{% include codeHeader.html %}
{% raw %}
```
kubectl delete services hello-minikube 
```
{% endraw %}


The output is similar to this:

{% include codeHeader.html %}
{% raw %}
```
service "hello-minikube" deleted 
```
{% endraw %}


8. Delete the hello-minikube Deployment:

{% include codeHeader.html %}
{% raw %}
```
kubectl delete deployment hello-minikube 
```
{% endraw %}


The output is similar to this:

{% include codeHeader.html %}
{% raw %}
```
deployment.extensions "hello-minikube" deleted 
```
{% endraw %}


9. Stop the local Minikube cluster:


{% include codeHeader.html %}
{% raw %}
```
minikube stop 
```
{% endraw %}


The output is similar to this:


{% include codeHeader.html %}
{% raw %}
```
Stopping "minikube"... "minikube" stopped. 
```
{% endraw %}


For more information, see [Stopping a Cluster](#stopping-a-cluster).



10. Delete the local Minikube cluster:


{% include codeHeader.html %}
{% raw %}
```
minikube delete 
```
{% endraw %}



The output is similar to this:


{% include codeHeader.html %}
{% raw %}
```
Deleting "minikube" ... The "minikube" cluster has been deleted. 
```
{% endraw %}



For more information, see [Deleting a cluster](#deleting-a-cluster).


## Managing your Cluster[ ](#managing-your-cluster)

### Starting a Cluster[ ](#starting-a-cluster)

The minikube start [[2023-03-28-create-and-audit-mysql-db-command-line|command]] can be used to start your cluster. This command creates and configures a Virtual Machine that runs a single-node Kubernetes cluster. This command also configures your [kubectl](/docs/reference/kubectl/overview/) installation to communicate with this cluster.

> **Note:**If you are behind a web proxy, you need to pass this information to the minikube start command:
>
> ```
> https_proxy=<my proxy> minikube start --docker-env http_proxy=<my proxy> --docker-env https_proxy=<my proxy> --docker-env no_proxy=192.168.99.0/24 
> ```
>
> Unfortunately, setting the environment variables alone does not work.
>
> Minikube also creates a "minikube" context, and sets it to default in kubectl. To switch back to this context, run this command: ```kubectl config use-context minikube```.
>
> #### Specifying the Kubernetes version[ ](#specifying-the-kubernetes-version)

You can specify the version of Kubernetes for Minikube to use by adding the ```--kubernetes-version``` string to the minikube start command. For example, to run version v1.18.0, you would run the following:


{% include codeHeader.html %}
{% raw %}
```
minikube start --kubernetes-version v1.18.0
```
{% endraw %}
  

#### Specifying the VM driver[ ](#specifying-the-vm-driver)

You can change the VM driver by adding the ```--driver=<enter_driver_name>``` flag to minikube start. For example the command would be.



{% include codeHeader.html %}
{% raw %}
```
minikube start --driver=<driver_name> 
```
{% endraw %}  


Minikube supports the following drivers:

> **Note:** See [DRIVERS](https://minikube.sigs.k8s.io/docs/reference/drivers/) for details on supported drivers and how to install plugins.\* docker ([driver installation](https://minikube.sigs.k8s.io/docs/drivers/docker/))

- virtualbox ([driver installation](https://minikube.sigs.k8s.io/docs/drivers/virtualbox/))
- podman ([driver installation](https://minikube.sigs.k8s.io/docs/drivers/podman/)) (EXPERIMENTAL)
- vmwarefusion
- kvm2 ([driver installation](https://minikube.sigs.k8s.io/docs/reference/drivers/kvm2/))
- hyperkit ([driver installation](https://minikube.sigs.k8s.io/docs/reference/drivers/hyperkit/))
- hyperv ([driver installation](https://minikube.sigs.k8s.io/docs/reference/drivers/hyperv/)) Note that the IP below is dynamic and can change. It can be retrieved with minikube ip.
- vmware ([driver installation](https://minikube.sigs.k8s.io/docs/reference/drivers/vmware/)) (VMware unified driver)
- parallels ([driver installation](https://minikube.sigs.k8s.io/docs/reference/drivers/parallels/))
- none (Runs the Kubernetes components on the host and not in a virtual machine. You need to be running Linux and to have [DockerDocker is a software technology providing operating-system-level virtualization also known as containers.](https://docs.docker.com/engine/) installed.)

> **Caution:** If you use the none driver, some Kubernetes components run as privileged containers that have side effects outside of the Minikube environment. Those side effects mean that the none driver is not recommended for personal workstations.#### Starting a cluster on alternative container runtimes[ ](#starting-a-cluster-on-alternative-container-runtimes)

You can start Minikube on the following container runtimes.

- [containerd](#container-runtimes-0)
- [CRI-O](#container-runtimes-1)
  To use [containerd](https://github.com/containerd/containerd) as the container runtime, run:


minikube start \ --network-plugin=cni \ --enable-default-cni \ --container-runtime=containerd \ --bootstrapper=kubeadm 
  

Or you can use the extended version:

minikube start \ --network-plugin=cni \ --enable-default-cni \ --extra-config=kubelet.container-runtime=[[2023-02-28-how-do-i-setup-a-remote-database-to-optimize-site-performance-with-MySQL|remote]] \ --extra-config=kubelet.container-runtime-endpoint=unix:///run/containerd/containerd.sock \ --extra-config=kubelet.image-service-endpoint=unix:///run/containerd/containerd.sock \ --bootstrapper=kubeadm 
  

To use [CRI-O](https://cri-o.io/) as the container runtime, run:

minikube start \ --network-plugin=cni \ --enable-default-cni \ --container-runtime=cri-o \ --bootstrapper=kubeadm 
  
Or you can use the extended version:

minikube start \ --network-plugin=cni \ --enable-default-cni \ --extra-config=kubelet.container-runtime=[[2020-04-04-how-to-set-up-a-remote-database-to-optimize-site-performance-with-mysql-on-ubuntu-1604|remote]] \ --extra-config=kubelet.container-runtime-endpoint=/var/run/crio.sock \ --extra-config=kubelet.image-service-endpoint=/var/run/crio.sock \ --bootstrapper=kubeadm $(function(){$("#container-runtimes").tabs();});
  
  
#### Use local images by re-using the Docker daemon[ ](#use-local-images-by-re-using-the-docker-daemon)

  
When using a single VM for Kubernetes, it's useful to reuse Minikube's built-in Docker daemon. Reusing the built-in daemon means you don't have to build a Docker registry on your host machine and push the image into it. Instead, you can build inside the same Docker daemon as Minikube, which speeds up local experiments.

> **Note:** Be sure to tag your Docker image with something other than latest and use that tag to pull the image. Because :latest is the default value, with a corresponding default image pull policy of Always, an image pull error (ErrImagePull) eventually results if you do not have the Docker image in the default Docker registry (usually DockerHub).To work with the Docker daemon on your Mac/Linux host, run the last line from minikube docker-env.

You can now use Docker at the command line of your host Mac/Linux machine to communicate with the Docker daemon inside the Minikube VM:

  
docker ps
  

> **Note:**On Centos 7, Docker may report the following error:
>
> Could not read CA certificate "/etc/docker/ca.pem": open /etc/docker/ca.pem: no such file or directory You can fix this by updating /etc/sysconfig/docker to ensure that Minikube's environment changes are respected:
>
> < DOCKER_CERT_PATH=/etc/docker --- > if [ -z "${DOCKER\_CERT\_PATH}" ]; then > DOCKER_CERT_PATH=/etc/docker > fi ### Configuring Kubernetes[ ](#configuring-kubernetes)

Minikube has a "configurator" feature that allows users to configure the Kubernetes components with arbitrary values. To use this feature, you can use the --extra-config flag on the minikube start command.

This flag is repeated, so you can pass it several times with several different values to set multiple options.

This flag takes a string of the form component.key=value, where component is one of the strings from the below list, key is a value on the configuration struct and value is the value to set.

Valid keys can be found by examining the documentation for the Kubernetes componentconfigs for each component. Here is the documentation for each supported configuration:

- [kubelet](https://godoc.org/k8s.io/kubernetes/pkg/kubelet/apis/config#KubeletConfiguration)
- [apiserver](https://godoc.org/k8s.io/kubernetes/cmd/kube-apiserver/app/options#ServerRunOptions)
- [proxy](https://godoc.org/k8s.io/kubernetes/pkg/proxy/apis/config#KubeProxyConfiguration)
- [controller-manager](https://godoc.org/k8s.io/kubernetes/pkg/controller/apis/config#KubeControllerManagerConfiguration)
- [etcd](https://godoc.org/github.com/coreos/etcd/etcdserver#ServerConfig)
- [scheduler](https://godoc.org/k8s.io/kubernetes/pkg/scheduler/apis/config#KubeSchedulerConfiguration)


#### Examples[ ](#examples)

To change the MaxPods setting to 5 on the Kubelet, pass this flag: --extra-config=kubelet.MaxPods=5.

This feature also supports nested structs. To change the LeaderElection.LeaderElect setting to true on the scheduler, pass this flag: --extra-config=scheduler.LeaderElection.LeaderElect=true.

To set the AuthorizationMode on the apiserver to RBAC, you can use: --extra-config=apiserver.authorization-mode=RBAC.


### Stopping a Cluster[ ](#stopping-a-cluster)

The minikube stop command can be used to stop your cluster. This command shuts down the Minikube Virtual Machine, but preserves all cluster state and data. Starting the cluster again will restore it to its previous state.

  
### Deleting a Cluster[ ](#deleting-a-cluster)

The minikube delete command can be used to delete your cluster. This command shuts down and deletes the Minikube Virtual Machine. No data or state is preserved.

  
### Upgrading Minikube[ ](#upgrading-minikube)

If you are using macOS and [Brew Package Manager](https://brew.sh/) is installed run:

  
## brew update brew upgrade minikube Interacting with Your Cluster[ ](#interacting-with-your-cluster)

  
### Kubectl[ ](#kubectl)

The minikube start command creates a [kubectl context](/docs/reference/generated/kubectl/kubectl-commands#-em-set-context-em-) called "minikube". This context contains the configuration to communicate with your Minikube cluster.

Minikube sets this context to default automatically, but if you need to switch back to it in the future, run:



{% include codeHeader.html %}
{% raw %}
```
kubectl config use-context minikube
```
{% endraw %}

  
Or pass the context on each command like this:



{% include codeHeader.html %}
{% raw %}
```
kubectl get pods --context=minikube
```
{% endraw %}
  

### Dashboard[ ](#dashboard)

To access the [[2020-08-04-playing-kubernetes-with-minikube#Dashboard dashboard|Kubernetes Dashboard]], run this command in a shell after starting Minikube to get the address:



{% include codeHeader.html %}
{% raw %}
```
minikube dashboard
```
{% endraw %}

### Services[ ](#services)

To access a Service exposed via a node port, run this command in a shell after starting Minikube to get the address:



{% include codeHeader.html %}
{% raw %}
```
minikube service [-n NAMESPACE] [--url] NAME 
```
{% endraw %}
  
Networking[ ](#networking)
  

The Minikube VM is exposed to the host system via a host-only IP address, that can be obtained with the minikube ip command. Any services of type NodePort can be accessed over that IP address, on the NodePort.

To determine the NodePort for your service, you can use a kubectl command like this:



{% include codeHeader.html %}
{% raw %}
```
kubectl get service $SERVICE --output='jsonpath="{.spec.ports[0].nodePort}"'
```
{% endraw %}
  
## Persistent Volumes[ ](#persistent-volumes)

Minikube supports [PersistentVolumes](/docs/concepts/storage/persistent-volumes/) of type hostPath. These PersistentVolumes are mapped to a directory inside the Minikube VM.

The Minikube VM boots into a tmpfs, so most directories will not be persisted across reboots (minikube stop). However, Minikube is configured to persist files stored under the following host directories:

- /data
- /var/lib/minikube
- /var/lib/docker
  
Here is an example PersistentVolume config to persist data in the /data directory:



{% include codeHeader.html %}
{% raw %}
```
## apiVersion: v1 kind: PersistentVolume metadata: name: pv0001 spec: accessModes: - ReadWriteOnce capacity: storage: 5Gi hostPath: path: /data/pv0001/ Mounted Host Folders[ ](#mounted-host-folders)
```
{% endraw %}

Some drivers will mount a host folder within the VM so that you can easily share files between the VM and host. These are not configurable at the moment and different for the driver and OS you are using.

> **Note:** Host folder sharing is not implemented in the KVM driver yet.DriverOSHostFolderVMVirtualBoxLinux/home/hosthomeVirtualBoxmacOS/Users/UsersVirtualBoxWindowsC://Users/c/UsersVMware FusionmacOS/Users/mnt/hgfs/UsersXhyvemacOS/Users/UsersPrivate Container Registries[ ](#private-container-registries)

---

To access a private container registry, follow the steps on [this page](/docs/concepts/containers/images/).

We recommend you use ImagePullSecrets, but if you would like to configure access on the Minikube VM you can place the .dockercfg in the /home/docker directory or the config.json in the /home/docker/.docker directory.

## Add-ons[ ](#add-ons)

In order to have Minikube properly start or restart custom addons, place the addons you wish to be launched with Minikube in the ~/.minikube/addons directory. Addons in this folder will be moved to the Minikube VM and launched each time Minikube is started or restarted.

## Using Minikube with an HTTP Proxy[ ](#using-minikube-with-an-http-proxy)

Minikube creates a Virtual Machine that includes Kubernetes and a Docker daemon. When Kubernetes attempts to schedule containers using Docker, the Docker daemon may require external network access to pull containers.

If you are behind an HTTP proxy, you may need to supply Docker with the proxy settings. To do this, pass the required environment variables as flags during minikube start.

For example:



{% include codeHeader.html %}
{% raw %}
```
minikube start --docker-env http_proxy=http://$YOURPROXY:PORT \  --docker-env https\_proxy=https://$YOURPROXY:PORT
```
{% endraw %}
  
If your Virtual Machine address is 192.168.99.100, then chances are your proxy settings will prevent kubectl from directly reaching it. To by-pass proxy configuration for this IP address, you should modify your no_proxy settings. You can do so with:



{% include codeHeader.html %}
{% raw %}
```
## export no_proxy=$no\_proxy,$(minikube ip) Known Issues[ ](#known-issues)
```
{% endraw %}

Features that require multiple nodes will not work in Minikube.

## Design[ ](#design)

Minikube uses [libmachine](https://github.com/docker/machine/tree/master/libmachine) for provisioning VMs, and [kubeadm](https://github.com/kubernetes/kubeadm) to provision a Kubernetes cluster.

For more information about Minikube, see the [proposal](https://git.k8s.io/community/contributors/design-proposals/cluster-lifecycle/local-cluster-ux.md).