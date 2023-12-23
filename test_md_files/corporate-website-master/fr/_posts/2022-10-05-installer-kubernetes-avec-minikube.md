---
author: full
categories:
- kubernetes
date: 2022-10-05
description: 'Installing Kubernetes with Minikube
  Minikube is a tool that makes it easy to run Kubernetes locally. Minikube runs a
  singlenode Kubernetes cluster inside a Virtual Machine VM on your laptop for users
  looking to try out Kubernetes or develop with it daytoday.
  Minikube Features minikubefeatures
  Minikube supports the following Kubernetes features:
  DNS NodePorts ConfigMaps and Secrets Dashboards Container Runtime: Dockerhttps://www.docker.com/,
  CRIOhttps'
image: https://sergio.afanou.com/assets/images/image-midres-38.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2022-10-05
pretified: true
ref: installingkubernetes_1251
title: Installer Kubernetes avec Minikube
seo:
  links: [ "https://www.wikidata.org/wiki/Q22661306" ]
---

# Installer Kubernetes avec Minikube

Minikube est un outil qui facilite l'exécution locale de Kubernetes. Minikube exécute un cluster Kubernetes à nœud unique à l'intérieur d'une machine virtuelle (VM) sur votre ordinateur portable pour les utilisateurs qui souhaitent essayer Kubernetes ou développer avec lui au jour le jour.

## Fonctionnalités Minikube[ ](#minikube-features)

Minikube prend en charge les fonctionnalités Kubernetes suivantes :

-DNS
- NodePorts
- ConfigMaps et Secrets
- Tableaux de bord
- Exécution du conteneur : [Docker](https://www.docker.com/), [CRI-O](https://cri-o.io/) et [containerd](https://github.com /conteneur/conteneur)
- Activation de CNI (Container Network Interface)
- Entrée
  Installation[ ](#installation)

---

Voir [[2020-08-12-installing-kubernetes-with-minikube|Installation de Minikube]].

## Démarrage rapide[ ](#démarrage rapide)

Cette brève démo vous explique comment démarrer, utiliser et supprimer Minikube localement. Suivez les étapes ci-dessous pour démarrer et explorer Minikube.

1. Démarrez Minikube et créez un cluster :

minikube start La sortie ressemble à ceci :

Démarrage du cluster Kubernetes local... Exécution des vérifications préalables à la création... Création de la machine... Démarrage du cluster Kubernetes local... Pour plus d'informations sur le démarrage de votre cluster sur une version spécifique de Kubernetes, une machine virtuelle ou un environnement d'exécution de conteneur, consultez [Démarrage d'un Cluster](#starting-a-cluster).

2. Vous pouvez maintenant interagir avec votre cluster à l'aide de kubectl. Pour plus d'informations, consultez [Interacting with Your Cluster](#interacting-with-your-cluster).

Créons un déploiement Kubernetes à l'aide d'une image existante nommée echoserver, qui est un simple serveur HTTP et exposons-le sur le port 8080 en utilisant --port.

kubectl create deployment hello-minikube --image=k8s.gcr.io/echoserver:1.10 Le résultat ressemble à ceci :

deployment.apps/hello-minikube créé 3. Pour accéder au déploiement hello-minikube, exposez-le en tant que service :

kubectl expose déploiement hello-minikube --type=NodePort --port=8080 L'option --type=NodePort spécifie le type du service.

La sortie est similaire à ceci :

service/hello-minikube expose 4. Le pod hello-minikube est maintenant lancé mais vous devez attendre que le pod soit opérationnel avant d'y accéder via le service exposé.

Vérifiez si le pod est opérationnel :

kubectl get pod Si la sortie affiche le STATUS comme ContainerCreating, le Pod est toujours en cours de création :

NOM READY STATUS RESTARTS AGE hello-minikube-3383150820-vctvh 0/1 ContainerCreating 0 3s Si la sortie indique STATUS Running, le pod est maintenant opérationnel :

NOM READY STATUS RESTARTS AGE hello-minikube-3383150820-vctvh 1/1 Running 0 13s 5. Obtenez l'URL du service exposé pour afficher les détails du service :

service minikube hello-minikube --url 6. Pour afficher les détails de votre cluster local, copiez et collez l'URL que vous avez obtenue en sortie, sur votre navigateur.

La sortie est similaire à ceci :

Nom d'hôte : hello-minikube-7c77b68cff-8wdzq Informations sur le pod : -aucune information sur le pod disponible- Valeurs du serveur : server_version=nginx : 1.13.3 - lua : 10008 Informations sur la requête : client_address=172.17.0.1 method=GET real path=/ query= request_version =1.1 request_scheme=http request_uri=http://192.168.99.100:8080/ En-têtes de requête : accept=_/_ host=192.168.99.100:30674 user-agent=curl/7.47.0 Corps de la requête : -aucun corps dans la requête- Si vous ne souhaitez plus que le service et le cluster s'exécutent, vous pouvez les supprimer.

7. Supprimez le service hello-minikube :

kubectl delete services hello-minikube Le résultat ressemble à ceci :

service "hello-minikube" supprimé 8. Supprimez le déploiement hello-minikube :

kubectl delete deployment hello-minikube Le résultat ressemble à ceci :

deployment.extensions "hello-minikube" supprimé 9. Arrêtez le cluster Minikube local :

minikube stop La sortie ressemble à ceci :

Arrêt de "minikube"... "minikube" s'est arrêté. Pour plus d'informations, consultez [Arrêter un cluster](#stopping-a-cluster).

10. Supprimez le cluster Minikube local :

minikube delete La sortie ressemble à ceci :

Suppression de "minikube" ... Le cluster "minikube" a été supprimé. Pour plus d'informations, consultez [Supprimer un cluster](#deleting-a-cluster).

## Gérer votre cluster[ ](#managing-your-cluster)

### Démarrage d'un cluster[ ](#starting-a-cluster)

La commande minikube start peut être utilisée pour démarrer votre cluster. Cette commande crée et configure une machine virtuelle qui exécute un cluster Kubernetes à nœud unique. Cette commande configure également votre installation [kubectl](/docs/reference/kubectl/overview/) pour communiquer avec ce cluster.

> **Remarque :**Si vous êtes derrière un proxy Web, vous devez transmettre ces informations à la commande minikube start :
>
> https_proxy=<mon proxy> minikube start --docker-env http_proxy=<mon proxy> --docker-env https_proxy=<mon proxy> --docker-env no_proxy=192.168.99.0/24 Malheureusement, définir les variables d'environnement seules ne marche pas.
>
> Minikube crée également un contexte "minikube" et le définit par défaut dans kubectl. Pour revenir à ce contexte, exécutez cette commande : kubectl config use-context minikube.
>
> #### Spécifier la version de Kubernetes[ ](#specifying-the-kubernetes-version)

Vous pouvez spécifier la version de Kubernetes pour Minikube à utiliser en ajoutant la chaîne --kubernetes-version à la commande minikube start. Par exemple, pour exécuter la version v1.18.0, vous devez exécuter ce qui suit :

minikube start --kubernetes-version v1.18.0 #### Spécification du pilote VM[ ](#specifying-the-vm-driver)

Vous pouvez modifier le pilote VM en ajoutant l'indicateur --driver=<enter_driver_name> au démarrage de minikube. Par exemple, la commande serait.

minikube start --driver=<driver_name> Minikube prend en charge les pilotes suivants :

> **Remarque :** Voir [DRIVERS](https://minikube.sigs.k8s.io/docs/reference/drivers/) pour plus de détails sur les pilotes pris en charge et comment installer les plugins.\* docker ([installation du pilote] (https://minikube.sigs.k8s.io/docs/drivers/docker/))

- virtualbox ([installation du pilote](https://minikube.sigs.k8s.io/docs/drivers/virtualbox/))
- podman ([installation du pilote](https://minikube.sigs.k8s.io/docs/drivers/podman/)) (EXPÉRIMENTAL)
- vmware fusion
- kvm2 ([installation du pilote](https://minikube.sigs.k8s.io/docs/reference/drivers/kvm2/))
- hyperkit ([installation du pilote](https://minikube.sigs.k8s.io/docs/reference/drivers/hyperkit/))
- hyperv ([installation du pilote](https://minikube.sigs.k8s.io/docs/reference/drivers/hyperv/)) Notez que l'IP ci-dessous est dynamique et peut changer. Il peut être récupéré avec minikube ip.
- vmware ([installation du pilote](https://minikube.sigs.k8s.io/docs/reference/drivers/vmware/)) (pilote unifié VMware)
- parallèles ([installation du pilote](https://minikube.sigs.k8s.io/docs/reference/drivers/parallels/))
- aucun (Exécute les composants Kubernetes sur l'hôte et non sur une machine virtuelle. Vous devez exécuter Linux et disposer de [DockerDocker est une technologie logicielle fournissant une virtualisation au niveau du système d'exploitation également connue sous le nom de conteneurs.](https:// docs.docker.com/engine/) installé.)

> **Attention :** Si vous utilisez le pilote none, certains composants Kubernetes s'exécutent en tant que conteneurs privilégiés qui ont des effets secondaires en dehors de l'environnement Minikube. Ces effets secondaires signifient que le pilote none n'est pas recommandé pour les postes de travail personnels.

Vous pouvez démarrer Minikube sur les environnements d'exécution de conteneur suivants.

- [containerd](#container-runtimes-0)
- [CRI-O](#container-runtimes-1)
  Pour utiliser [containerd](https://github.com/containerd/containerd) comme environnement d'exécution du conteneur, exécutez :

minikube start \ --network-plugin=cni \ --enable-default-cni \ --container-runtime=containerd \ --bootstrapper=kubeadm Ou vous pouvez utiliser la version étendue :

minikube start \ --network-plugin=cni \ --enable-default-cni \ --extra-config=kubelet.container-runtime=remote \ --extra-config=kubelet.container-runtime-endpoint=unix:/ //run/containerd/containerd.sock \ --extra-config=kubelet.image-service-endpoint=unix:///run/containerd/containerd.sock \ --bootstrapper=kubeadm Pour utiliser [CRI-O]( https://cri-o.io/) en tant qu'environnement d'exécution du conteneur, exécutez :

minikube start \ --network-plugin=cni \ --enable-default-cni \ --container-runtime=cri-o \ --bootstrapper=kubeadm Ou vous pouvez utiliser la version étendue :

minikube start \ --network-plugin=cni \ --enable-default-cni \ --extra-config=kubelet.container-runtime=remote \ --extra-config=kubelet.container-runtime-endpoint=/var/ run/crio.sock \ --extra-config=kubelet.image-service-endpoint=/var/run/crio.sock \ --bootstrapper=kubeadm $(function(){$("#container-runtimes"). tabs();});#### Utiliser des images locales en réutilisant le démon Docker[ ](#use-local-images-by-re-using-the-docker-daemon)

Lorsque vous utilisez une seule machine virtuelle pour Kubernetes, il est utile de réutiliser le démon Docker intégré de Minikube. La réutilisation du démon intégré signifie que vous n'avez pas besoin de créer un registre Docker sur votre machine hôte et d'y insérer l'image. Au lieu de cela, vous pouvez construire à l'intérieur du même démon Docker que Minikube, ce qui accélère les expériences locales.

> **Remarque :** Assurez-vous de baliser votre image Docker avec autre chose que la plus récente et utilisez cette balise pour extraire l'image. Étant donné que :latest est la valeur par défaut, avec une stratégie d'extraction d'image par défaut correspondante de Toujours, une erreur d'extraction d'image (ErrImagePull) se produit éventuellement si vous n'avez pas l'image Docker dans le registre Docker par défaut (généralement DockerHub). Pour travailler avec le Docker démon sur votre hôte Mac/Linux, exécutez la dernière ligne de minikube docker-env.

Vous pouvez maintenant utiliser Docker sur la ligne de commande de votre machine Mac/Linux hôte pour communiquer avec le démon Docker à l'intérieur de la VM Minikube :

docker ps

> **Remarque :**Sur Centos 7, Docker peut signaler l'erreur suivante :
>
> Impossible de lire le certificat CA "/etc/docker/ca.pem": ouvrez /etc/docker/ca.pem : aucun fichier ou répertoire de ce type Vous pouvez résoudre ce problème en mettant à jour /etc/sysconfig/docker pour vous assurer que l'environnement de Minikube change sont respectés :
>
> < DOCKER_CERT_PATH=/etc/docker --- > if [ -z "${DOCKER\_CERT\_PATH}" ] ; then > DOCKER_CERT_PATH=/etc/docker > fi ### Configuration de Kubernetes[ ](#configuring-kubernetes)

Minikube dispose d'une fonction "configurateur" qui permet aux utilisateurs de configurer les composants Kubernetes avec des valeurs arbitraires. Pour utiliser cette fonctionnalité, vous pouvez utiliser le --extra-drapeau de configuration sur la commande minikube start.

Cet indicateur est répété, vous pouvez donc le passer plusieurs fois avec plusieurs valeurs différentes pour définir plusieurs options.

Cet indicateur prend une chaîne de la forme component.key=value, où component est l'une des chaînes de la liste ci-dessous, key est une valeur sur la structure de configuration et value est la valeur à définir.

Des clés valides peuvent être trouvées en examinant la documentation des configurations de composants Kubernetes pour chaque composant. Voici la documentation de chaque configuration prise en charge :

- [kubelet](https://godoc.org/k8s.io/kubernetes/pkg/kubelet/apis/config#KubeletConfiguration)
- [apiserver](https://godoc.org/k8s.io/kubernetes/cmd/kube-apiserver/app/options#ServerRunOptions)
- [proxy](https://godoc.org/k8s.io/kubernetes/pkg/proxy/apis/config#KubeProxyConfiguration)
- [controller-manager](https://godoc.org/k8s.io/kubernetes/pkg/controller/apis/config#KubeControllerManagerConfiguration)
- [etcd](https://godoc.org/github.com/coreos/etcd/etcdserver#ServerConfig)
- [planificateur](https://godoc.org/k8s.io/kubernetes/pkg/scheduler/apis/config#KubeSchedulerConfiguration)

#### Exemples[ ](#exemples)

Pour modifier le paramètre MaxPods sur 5 sur le Kubelet, transmettez cet indicateur : --extra-config=kubelet.MaxPods=5.

Cette fonctionnalité prend également en charge les structures imbriquées. Pour modifier le paramètre LeaderElection.LeaderElect sur true sur le planificateur, transmettez cet indicateur : --extra-config=scheduler.LeaderElection.LeaderElect=true.

Pour définir AuthorizationMode sur l'apiserver sur RBAC, vous pouvez utiliser : --extra-config=apiserver.authorization-mode=RBAC.

### Arrêt d'un cluster[ ](#stopping-a-cluster)

La commande minikube stop peut être utilisée pour arrêter votre cluster. Cette commande arrête la machine virtuelle Minikube, mais préserve tout l'état et les données du cluster. Redémarrer le cluster le restaurera à son état précédent.

### Suppression d'un cluster[ ](#deleting-a-cluster)

La commande minikube delete peut être utilisée pour supprimer votre cluster. Cette commande arrête et supprime la machine virtuelle Minikube. Aucune donnée ou état n'est conservé.

### Mise à niveau de Minikube[ ](#upgrading-minikube)

Si vous utilisez macOS et que [Brew Package Manager](https://brew.sh/) est installé, exécutez :

## brew update brew upgrade minikube Interacting with Your Cluster[ ](#interacting-with-your-cluster)

### Kubectl[ ](#kubectl)

La commande minikube start crée un [contexte kubectl](/docs/reference/generated/kubectl/kubectl-commands#-em-set-context-em-) appelé "minikube". Ce contexte contient la configuration pour communiquer avec votre cluster Minikube.

Minikube définit automatiquement ce contexte par défaut, mais si vous devez y revenir ultérieurement, exécutez :

kubectl config use-context minikube

Ou passez le contexte sur chaque commande comme ceci :

kubectl get pods --context=minikube

### Tableau de bord[ ](#tableau de bord)

Pour accéder au [[2020-08-04-playing-kubernetes-with-minikube#Dashboard dashboard|Kubernetes Dashboard]], exécutez cette commande dans un shell après avoir démarré Minikube pour obtenir l'adresse :

tableau de bord minikube ### Services[ ](#services)

Pour accéder à un service exposé via un port de nœud, exécutez cette commande dans un shell après avoir démarré Minikube pour obtenir l'adresse :

## service minikube [-n NAMESPACE] [--url] NOM Networking[ ](#networking)

La machine virtuelle Minikube est exposée au système hôte via une adresse IP réservée à l'hôte, qui peut être obtenue avec la commande minikube ip. Tous les services de type NodePort sont accessibles via cette adresse IP, sur le NodePort.

Pour déterminer le NodePort de votre service, vous pouvez utiliser une commande kubectl comme celle-ci :

kubectl get service $SERVICE --output='jsonpath="{.spec.ports[0].nodePort}"'

## Volumes persistants[ ](#volumes-persistants)

Minikube prend en charge les [PersistentVolumes](/docs/concepts/storage/persistent-volumes/) de type hostPath. Ces PersistentVolumes sont mappés à un répertoire à l'intérieur de la machine virtuelle Minikube.

La machine virtuelle Minikube démarre dans un tmpfs, de sorte que la plupart des répertoires ne seront pas conservés lors des redémarrages (arrêt minikube). Cependant, Minikube est configuré pour conserver les fichiers stockés sous les répertoires hôtes suivants :

- /Les données
- /var/lib/minikube
- /var/lib/docker
  Voici un exemple de configuration PersistentVolume pour conserver les données dans le répertoire /data :

## apiVersion : v1 kind : PersistentVolume metadata : name : pv0001 spec : accessModes : - ReadWriteOnce capacity : stockage : 5Gi hostPath : chemin : /data/pv0001/ Mounted Host Folders[ ](#mounted-host-folders)

Certains pilotes monteront un dossier hôte dans la VM afin que vous puissiez facilement partager des fichiers entre la VM et l'hôte. Ceux-ci ne sont pas configurables pour le moment et différents pour le pilote et le système d'exploitation que vous utilisez.

> **Remarque :** Le partage de dossier hôte n'est pas encore implémenté dans le pilote KVM. Registres[ ](#private-container-registries)

---

Pour accéder à un registre de conteneurs privé, suivez les étapes sur [cette page](/docs/concepts/containers/images/).

Nous vous recommandons d'utiliser ImagePullSecrets, mais si vous souhaitez configurer l'accès sur la VM Minikube, vous pouvez placer le .dockercfg dans le répertoire /home/docker ou le config.json dans le répertoire /home/docker/.docker.

## Modules complémentaires[ ](#modules complémentaires)

Afin que Minikube démarre ou redémarre correctement les addons personnalisés, placez les addons que vous souhaitez lancer avec Minikube dans le répertoire ~/.minikube/addons. Les modules complémentaires de ce dossier seront déplacés vers la machine virtuelle Minikube et lancés à chaque démarrage ou redémarrage de Minikube.

## Utilisation de Minikube avec un proxy HTTP[ ](#using-minikube-with-an-http-proxy)

Minikube crée une machine virtuelle qui inclut Kubernetes et un démon Docker. Lorsque Kubernetes tente de planifier des conteneurs à l'aide de Docker, le démon Docker peut nécessiter un accès réseau externe pour extraire les conteneurs.

Si vous êtes derrière un proxy HTTP, vous devrez peut-être fournir à Docker les paramètres de proxy. Pour ce faire, transmettez les variables d'environnement requises en tant qu'indicateurs lors du démarrage de minikube.

Par exemple:

minikube start --docker-env http_proxy=http://$YOURPROXY:PORT \ --docker-env https\_proxy=https://$YOURPROXY:PORT Si l'adresse de votre machine virtuelle est 192.168.99.100, il y a de fortes chances que votre proxy les paramètres empêcheront kubectl de l'atteindre directement. Pour contourner la configuration du proxy pour cette adresse IP, vous devez modifier vos paramètres no_proxy. Vous pouvez le faire avec :

## export no_proxy=$no\_proxy,$(minikube ip) Problèmes connus[ ](#known-issues)

Les fonctionnalités qui nécessitent plusieurs nœuds ne fonctionneront pas dans Minikube.

## Conception[ ](#conception)

Minikube utilise [libmachine](https://github.com/docker/machine/tree/master/libmachine) pour provisionner les machines virtuelles et [kubeadm](https://github.com/kubernetes/kubeadm) pour provisionner un cluster Kubernetes .

Pour plus d'informations sur Minikube, consultez la [proposition](https://git.k8s.io/community/contributors/design-proposals/cluster-lifecycle/local-cluster-ux.md).

## Liens supplémentaires[ ](#liens-supplémentaires)

- **Objectifs et non-objectifs** : pour les objectifs et les non-objectifs du projet Minikube, veuillez consulter notre [feuille de route](https://minikube.sigs.k8s.io/docs/contrib/roadmap/).
- **Guide de développement** : voir [Contribuer](https://minikube.sigs.k8s.io/docs/contrib/) pour un aperçu de la façon d'envoyer des pull requests.
- **Construire Minikube** : pour obtenir des instructions sur la façon de construire/tester Minikube à partir de la source, consultez le [guide de construction](https://minikube.sigs.k8s.io/docs/contrib/building/).
- **Ajout d'une nouvelle dépendance** : pour savoir comment ajouter une nouvelle dépendance à Minikube, consultez le [guide d'ajout de dépendances](https://minikube.sigs.k8s.io/docs/contrib/drivers/).
- **Ajout d'un nouvel addon** : pour savoir comment ajouter un nouvel addon pour Minikube, consultez le [guide d'ajout d'un addon](https://minikube.sigs.k8s.io/docs/contrib/addons/) .
- **MicroK8s** : les utilisateurs de Linux qui souhaitent éviter d'exécuter une machine virtuelle peuvent envisager [MicroK8s](https://microk8s.io/) comme alternative.
  Communauté[ ](#communauté)

---

Les contributions, questions et commentaires sont les bienvenus et encouragés ! Les développeurs de Minikube traînent sur [Slack](https://kubernetes.slack.com) dans le canal #minikube (obtenez une invitation [ici](https://slack.kubernetes.io/)). Nous avons également la [liste de diffusion Google Groups kubernetes-dev](https://groups.google.com/forum/#!forum/kubernetes-dev). Si vous postez sur la liste, préfixez votre sujet avec "minikube : ".

## Retour d'information

Cette page vous a été utile?

Oui NonMerci pour les commentaires. Si vous avez une question précise sur l'utilisation de Kubernetes, posez-la sur [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes). Ouvrez un problème dans le référentiel GitHub si vous souhaitez [signaler un problème](https://github.com/kubernetes/website/issues/new?title=Issue%20with%20k8s.io/docs/setup/learning-environment /minikube/) ou [suggérer une amélioration](https://github.com/kubernetes/website/issues/new?title=Improvement%20for%20k8s.io/docs/setup/learning-environment/minikube/).