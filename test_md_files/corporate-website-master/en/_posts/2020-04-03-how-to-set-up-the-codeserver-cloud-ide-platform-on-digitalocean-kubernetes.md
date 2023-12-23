---
author: full
categories:
- kubernetes
comments: true
date: 2021-11-03 18:00:07.376000+00:00
description: With developer tools moving to the cloud, creation and adoption of cloud
  IDE (Integrated Development Environment) platforms is growing. Cloud IDEs allow
  for real-time collaboration between developer teams to work in a unified development
  environment that minimizes incompatibilities and enhances productivity. Accessible
  through web browsers, cloud IDEs are available from every type of modern device.
  Another advantage of a cloud IDE is the possibility to leverage the power of a cluster,
  which can greatly exceed the processing power of a single development computer.
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1668184454/blog/x1t0ot3bychbotltu3qp.jpg
lang: en
layout: flexstart-blog-single
ref: howtosetup_thecodeserver_cloudide
seo:
  links:
  - https://www.wikidata.org/wiki/Q22661306
silot_terms: container docker kubernetes
tags:
- digital ocean
- digitalocean
- kubernetes
- code-server
- cloud
- platform
title: How To Set Up the code-server Cloud IDE Platform on DigitalOcean Kubernetes
toc: true
---

With developer tools moving to the cloud, creation and adoption of cloud IDE (Integrated Development Environment) platforms is growing. Cloud IDEs allow for real-time collaboration between developer teams to [[2020-08-13-work-with-kubernetes-with-minikube|work]] in a unified development environment that minimizes incompatibilities and enhances productivity. Accessible through web browsers, cloud IDEs are available from every type of modern device. Another advantage of a cloud IDE is the possibility to leverage the power of a [[2023-08-16-argo-cd-cluster-disaster-recovery|cluster]], which can greatly exceed the processing power of a single development computer.

[[2022-01-02-how-does-code-server-works|code-server]] is Microsoft Visual Studio Code [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|running]] on a remote server and accessible directly from your browser. Visual Studio Code is a modern code editor with integrated Git support, a code debugger, smart autocompletion, and customizable and extensible features. This means that you can [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] various devices, running different operating systems, and always have a consistent development environment on hand.

In this tutorial, you will set up the [[2022-01-02-how-does-code-server-works|code-server]] cloud IDE platform on your DigitalOcean [Kubernetes cluster](2023-04-04-work-with-kubernetes-with-minikube.md) and [[2021-12-26-how-to-expose-a-port-on-minikube|expose]] it at your domain, secured with Let’s Encrypt certificates. In the end, you’ll have Microsoft Visual Studio Code running on your [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]] cluster, available via HTTPS and protected by a password.

# Prerequisites

A DigitalOcean [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]] cluster with your connection configured as the kubectl default. Instructions on how to configure kubectl are shown under the [[2022-05-08-can-docker-connect-to-database|Connect]] to your Cluster step when you create your cluster. To create a [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Kubernetes]] cluster on DigitalOcean, see [[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]] Quickstart.

The [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|Helm]] [[2023-11-01-helm-charts-the-package-manager-for-kubernetes|package]] manager installed on your [[2021-12-14-how-to-use-local-docker-images-with-minikube|local]] [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|machine]], and [[2023-12-15-release-management-with-tiller-in-helm-version-2|Tiller]] installed on your cluster. To do this, complete Steps 1 and 2 of the How To Install Software on [[2020-08-12-installing-kubernetes-with-minikube|Kubernetes]] [[2023-08-20-managing-multiple-clusters-with-argocd|Clusters]] with the [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|Helm]] Package Manager tutorial.

The Nginx Ingress Controller and Cert-Manager installed on your cluster using [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|Helm]] in order to [[2021-12-26-how-to-expose-a-port-on-minikube|expose]] code-server using Ingress Resources. To do this, follow How to Set Up an Nginx Ingress on DigitalOcean [[2022-03-25-how-to-solve-kubernetes-can-connect-with-localhost-but-not-ip|Kubernetes]] Using [[2023-10-25-using-helm-practical-use-cases|Helm]].

A fully registered domain name to [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|host]] code-server, pointed at the Load Balancer used by the Nginx Ingress. This tutorial will use code-server.your_domain throughout. You can purchase a domain name on Namecheap, get one for free on Freenom, or use the domain registrar of your choice. This domain name must differ from the one used in the How To Set Up an Nginx Ingress on DigitalOcean [[2020-08-13-work-with-kubernetes-with-minikube|Kubernetes]] prerequisite tutorial.

## Step 1 — Installing And Exposing code-server

In this section, you’ll install code-server to your DigitalOcean [Kubernetes cluster](2023-04-04-Installing%20kubernetes%20with%20minikube.md) and expose it at your domain, using the Nginx Ingress controller. You will also set up a password for admittance.
You’ll store the [[2023-11-19-continuous-deployment-with-argocd|deployment]] configuration on your local [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|machine]], in a file named code-server.yaml.

Create it using the following command:

```
nano code-server.yaml
```

Add the following lines to the file:

code-server.yaml

```
apiVersion: v1
kind: Namespace
metadata:
  name: code-server
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: code-server
  namespace: code-server
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: code-server.your_domain
    http:
      paths:
      - backend:
          serviceName: code-server
          servicePort: 80
---
apiVersion: v1
kind: Service
metadata:
 name: code-server
 namespace: code-server
spec:
 ports:
 - port: 80
   targetPort: 8443
 selector:
   app: code-server
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  labels:
    app: code-server
  name: code-server
  namespace: code-server
spec:
  selector:
    matchLabels:
      app: code-server
  replicas: 1
  template:
    metadata:
      labels:
        app: code-server
    spec:
      containers:
      - image: codercom/code-server
        imagePullPolicy: Always
        name: code-server
        args: ["--allow-http"]
        ports:
        - containerPort: 8443
        env:
        - name: PASSWORD
          value: "your_password"
```

This configuration defines a Namespace, a Deployment, a [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|Service]], and an Ingress. The Namespace is called code-server and separates the code-server installation from the rest of your cluster. The Deployment consists of one replica of the codercom/code-server [[2023-04-04-should-a-docker-container-run-as-root-or-user|Docker]] image, and an environment variable named PASSWORD that specifies the password for access.

The code-server [[2023-05-10-building-microservices-with-docker-creating-a-product-service|Service]] internally exposes the pod (created as a part of the Deployment) at port 80. The Ingress defined in the file specifies that the Ingress Controller is nginx, and that the code-server.your_domain domain will be served from the Service.

Remember to replace your_password with your desired password, and code-server.your_domain with your desired domain, pointed to the Load Balancer of the Nginx Ingress Controller.
Then, create the configuration in [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]] by running the following command:

```
kubectl create -f code-server.yaml
```

You’ll see the following output:
Output

```
namespace/code-server created
ingress.extensions/code-server created
service/code-server created
deployment.extensions/code-server created
```

You can watch the code-server pod become available by running:

```
kubectl get pods -w -n code-server
```

The output will look like:
Output

```
NAME                          READY   STATUS              RESTARTS   AGE
code-server-f85d9bfc9-j7hq6   0/1     ContainerCreating   0          1m
```

As soon as the status becomes Running, code-server has finished installing to your cluster.
Navigate to your domain in your browser. You’ll see the login prompt for code-server.

Enter the password you set in code-server.yaml and press Enter IDE. You’ll enter code-server and immediately see its editor [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|GUI]].

You’ve installed code-server to your [[2023-12-22-convert-docker-compose-to-kubernetes|Kubernetes]] cluster and made it available at your domain. You have also verified that it requires you to log in with a password. Now, you’ll move on to secure it with free Let’s Encrypt certificates using Cert-Manager.

## Step 2 — Securing the code-server Deployment

In this section, you will secure your code-server installation by applying Let’s Encrypt certificates to your Ingress, which Cert-Manager will automatically create. After completing this step, your code-server installation will be accessible via HTTPS.
Open code-server.yaml for editing:

```
nano code-server.yaml
```

Add the highlighted lines to your file, making sure to replace the [[2023-08-25-docker-exec-bash-example|example]] domain with your own:
code-server.yaml

```
apiVersion: v1
kind: Namespace
metadata:
  name: code-server
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: code-server
  namespace: code-server
  annotations:
    kubernetes.io/ingress.class: nginx
    certmanager.k8s.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - code-server.your_domain
    secretName: codeserver-prod
  rules:
  - host: code-server.your_domain
    http:
      paths:
      - backend:
          serviceName: code-server
          servicePort: 80
...
```

First, you specify that the cluster-issuer that this Ingress will use to provision certificates will be letsencrypt-prod, created as a part of the prerequisites. Then, you specify the domains that will be secured under the tls section, as well as your name for the Secret holding them.

Apply the changes to your [[2023-10-23-argocd-as-a-kubernetes-extension-advantages-and-benefits|Kubernetes]] cluster by running the following command:

```
kubectl apply -f code-server.yaml
```

You’ll need to wait a few minutes for Let’s Encrypt to provision your certificate. In the meantime, you can track its progress by looking at the output of the following command:
kubectl describe certificate codeserver-prod -n code-server

When it finishes, the end of the output will look similar to this:
Output

```
Events:
  Type    Reason              Age    From          Message
  ----    ------              ----   ----          -------
  Normal  Generated           2m49s  cert-manager  Generated new private key
  Normal  GenerateSelfSigned  2m49s  cert-manager  Generated temporary self signed certificate
  Normal  OrderCreated        2m49s  cert-manager  Created Order resource "codeserver-prod-4279678953"
  Normal  OrderComplete       2m14s  cert-manager  Order "codeserver-prod-4279678953" completed successfully
  Normal  CertIssued          2m14s  cert-manager  Certificate issued successfully
```

You can now refresh your domain in your browser. You’ll see the padlock to the left of the address bar in your browser signifying that the connection is secure.
In this step, you have configured the Ingress to secure your code-server deployment. Now, you can review the code-server [[2023-04-04-should-a-docker-container-run-as-root-or-user|user]] interface.

## Step 3 — Exploring the code-server Interface

In this section, you’ll explore some of the features of the code-server interface. Since code-server is Visual Studio Code running in the cloud, it has the same interface as the standalone desktop edition.

On the left-hand side of the IDE, there is a vertical row of six buttons opening the most commonly used features in a side panel known as the Activity Bar.

This bar is customizable so you can move these views to a different order or remove them from the bar. By default, the first view opens the Explorer panel that provides tree-like navigation of the project’s structure. You can manage your folders and [[2022-07-28-how-to-copy-files-from-host-to-docker-container|files]] here—creating, deleting, moving, and renaming them as necessary. The next view provides access to a search and replace functionality.

Following this, in the default order, is your view of the source control systems, like Git. Visual Studio code also supports other source control providers and you can find further instructions for source control workflows with the editor in this documentation.

The debugger option on the Activity Bar provides all the common actions for debugging in the panel. Visual Studio Code comes with built-in support for the Node.js runtime debugger and any language that transpiles to Javascript. For other languages you can install extensions for the required debugger. You can save debugging configurations in the launch.json file.

The final view in the Activity Bar provides a menu to access available extensions on the Marketplace.

The central part of the GUI is your editor, which you can separate by tabs for your code editing. You can change your editing view to a grid system or to side-by-side [[2022-07-28-how-to-copy-files-from-host-to-docker-container|files]].

After creating a new file through the File menu, an empty file will open in a new tab, and once saved, the file’s name will be viewable in the Explorer side panel. Creating folders can be done by right clicking on the Explorer sidebar and pressing on New Folder. You can expand a folder by clicking on its name as well as dragging and dropping files and folders to upper parts of the hierarchy to move them to a new location.

You can gain access to a terminal by pressing CTRL+SHIFT+, or by pressing on Terminal in the upper menu, and selecting New Terminal. The terminal will open in a lower panel and its working directory will be set to the project’s workspace, which contains the files and folders shown in the Explorer side panel.
You’ve explored a high-level overview of the code-server interface and reviewed some of the most commonly used features.

At this stage, you may get errors. I have prepared for you a solution whe you get [[2022-01-02-how-to-solve-code-server-websocket-close-with-status-code-1006|a websocket close with code 1006 error]] or the issue with [[2022-12-07-how-to-solve-the-code-server-error-could-not-locate-the-bindings-file|your bindings file]].

# Conclusion

You now have code-server, a versatile cloud IDE, installed on your DigitalOcean [[2023-05-14-understanding-kubernetes-the-container-orchestrator|Kubernetes]] cluster. You can work on your source code and documents with it individually or collaborate with your team. Running a cloud IDE on your cluster provides more power for testing, downloading, and more thorough or rigorous computing. For further information see the Visual Studio Code documentation on additional features and detailed instructions on other components of code-server.

[[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes-fr|Read in french]]