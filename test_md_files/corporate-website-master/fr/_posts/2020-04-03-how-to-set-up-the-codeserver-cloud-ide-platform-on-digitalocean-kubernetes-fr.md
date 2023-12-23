---
layout: flexstart-blog-single
title: "Comment configurer la plate-forme Cloud IDE du serveur de code sur DigitalOcean Kubernetes"
author: full
lang: fr
ref: howtosetup_thecodeserver_cloudide
categories: [kubernetes]
description: "Avec la migration des outils de développement vers le cloud, la création et l'adoption de plates-formes cloud IDE (Integrated Development Environment) se développent. Les IDE cloud permettent une collaboration en temps réel entre les équipes de développeurs pour travailler dans un environnement de développement unifié qui minimise les incompatibilités et améliore la productivité. Accessibles via les navigateurs Web, les IDE cloud sont disponibles à partir de tous les types d'appareils modernes. Un autre avantage d'un IDE cloud est la possibilité d'exploiter la puissance d'un cluster, qui peut largement dépasser la puissance de traitement d'un seul ordinateur de développement."
image: "https://sergio.afanou.com/assets/images/image-midres-23.jpg"
seo:
  links: [ "https://www.wikidata.org/wiki/Q22661306" ]
---



Avec la migration des outils de développement vers le cloud, la création et l'adoption de plates-formes cloud IDE (Integrated Development Environment) se développent. Les IDE cloud permettent une collaboration en temps réel entre les équipes de développeurs pour travailler dans un environnement de développement unifié qui minimise les incompatibilités et améliore la productivité. Accessibles via les navigateurs Web, les IDE cloud sont disponibles à partir de tous les types d'appareils modernes. Un autre avantage d'un IDE cloud est la possibilité d'exploiter la puissance d'un cluster, qui peut largement dépasser la puissance de traitement d'un seul ordinateur de développement.

[[2022-01-02-how-does-code-server-works|code-server]] est Microsoft Visual Studio Code exécuté sur un serveur distant et accessible directement depuis votre navigateur. Visual Studio Code est un éditeur de code moderne avec prise en charge Git intégrée, un débogueur de code, une saisie semi-automatique intelligente et des fonctionnalités personnalisables et extensibles. Cela signifie que vous pouvez utiliser différents appareils, exécutant différents systèmes d'exploitation, et toujours disposer d'un environnement de développement cohérent.

Dans ce didacticiel, vous allez configurer la plate-forme IDE cloud [[2022-01-02-how-does-code-server-works|code-server]] sur votre cluster DigitalOcean Kubernetes et l'exposer sur votre domaine, sécurisé avec Let's Crypter les certificats. Au final, vous aurez Microsoft Visual Studio Code en cours d'exécution sur votre cluster Kubernetes, disponible via HTTPS et protégé par un mot de passe.

# Conditions préalables

Un cluster DigitalOcean Kubernetes avec votre connexion configurée comme kubectl par défaut. Les instructions de configuration de kubectl sont affichées à l'étape Se connecter à votre cluster lorsque vous créez votre cluster. Pour créer un cluster Kubernetes sur DigitalOcean, consultez Kubernetes Quickstart.

Le gestionnaire de packages Helm installé sur votre machine locale et Tiller installé sur votre cluster. Pour ce faire, suivez les étapes 1 et 2 du didacticiel How To Install Software on Kubernetes Clusters with the Helm Package Manager.

Le contrôleur d'entrée Nginx et le gestionnaire de certificats installés sur votre cluster à l'aide de Helm afin d'exposer le serveur de code à l'aide des ressources d'entrée. Pour ce faire, suivez Comment configurer une entrée Nginx sur DigitalOcean Kubernetes à l'aide de Helm.

Un nom de domaine entièrement enregistré pour héberger le serveur de code, pointé vers l'équilibreur de charge utilisé par Nginx Ingress. Ce didacticiel utilisera [[2022-01-02-how-does-code-server-works|code-server]].votre_domaine tout au long. Vous pouvez acheter un nom de domaine sur Namecheap, en obtenir un gratuitement sur Freenom ou utiliser le registraire de domaine de votre choix. Ce nom de domaine doit être différent de celui utilisé dans le didacticiel préalable How To Set Up an Nginx Ingress on DigitalOcean Kubernetes.

## Étape 1 - Installer et exposer le serveur de code

Dans cette section, vous allez installer code-server sur votre cluster DigitalOcean Kubernetes et l'exposer sur votre domaine, à l'aide du contrôleur Nginx Ingress. Vous devrez également configurer un mot de passe pour l'admission.
Vous stockerez la configuration de déploiement sur votre ordinateur local, dans un fichier nommé code-server.yaml. Créez-le à l'aide de la commande suivante :
nano code-server.yaml

Ajoutez les lignes suivantes au fichier :

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

Cette configuration définit un espace de noms, un déploiement, un service et une entrée. L'espace de noms est appelé code-server et sépare l'installation de code-server du reste de votre cluster. Le déploiement se compose d'une réplique de l'image Docker codercom/code-server et d'une variable d'environnement nommée PASSWORD qui spécifie le mot de passe d'accès.

Le service code-server expose en interne le pod (créé dans le cadre du déploiement) au port 80. L'entrée définie dans le fichier spécifie que le contrôleur d'entrée est nginx et que le domaine code-server.your_domain sera servi à partir du Un service.

N'oubliez pas de remplacer your_password par le mot de passe souhaité et code-server.your_domain par le domaine souhaité, pointé vers l'équilibreur de charge du contrôleur d'entrée Nginx.

Créez ensuite la configuration dans Kubernetes en exécutant la commande suivante :

```
kubectl create -f code-server.yaml
```

Vous verrez la sortie suivante :


```
namespace/code-server created
ingress.extensions/code-server created
service/code-server created
deployment.extensions/code-server created
```

Vous pouvez regarder le pod code-server devenir disponible en exécutant :

```
kubectl get pods -w -n code-server
```

La sortie ressemblera à :


```
NAME                          READY   STATUS              RESTARTS   AGE
code-server-f85d9bfc9-j7hq6   0/1     ContainerCreating   0          1m
```

Dès que l'état devient En cours d'exécution, code-server a terminé l'installation sur votre cluster.
Accédez à votre domaine dans votre navigateur. Vous verrez l'invite de connexion pour code-server.

Entrez le mot de passe que vous avez défini dans code-server.yaml et appuyez sur Enter IDE. Vous entrerez dans code-server et verrez immédiatement l'interface graphique de son éditeur.

Vous avez installé code-server sur votre cluster Kubernetes et l'avez rendu disponible sur votre domaine. Vous avez également vérifié qu'il vous oblige à vous connecter avec un mot de passe. Maintenant, vous allez le sécuriser avec des certificats Let's Encrypt gratuits à l'aide de Cert-Manager.

## Étape 2 — Sécurisation du déploiement du serveur de code

Dans cette section, vous allez sécuriser l'installation de votre serveur de code en appliquant des certificats Let's Encrypt à votre Ingress, que Cert-Manager créera automatiquement. Après avoir terminé cette étape, votre installation de serveur de code sera accessible via HTTPS.
Ouvrez code-server.yaml pour le modifier :

```
nano code-server.yaml
```

Ajoutez les lignes en surbrillance à votre fichier, en veillant à remplacer l'exemple de domaine par le vôtre :

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

Tout d'abord, vous spécifiez que l'émetteur de cluster que cet Ingress utilisera pour provisionner les certificats sera Letsencrypt-prod, créé dans le cadre des prérequis. Ensuite, vous spécifiez les domaines qui seront sécurisés sous la section tls, ainsi que votre nom pour le secret qui les détient.

Appliquez les modifications à votre cluster Kubernetes en exécutant la commande suivante :

```
kubectl apply -f code-server.yaml
```

Vous devrez attendre quelques minutes pour que Let's Encrypt provisionne votre certificat. En attendant, vous pouvez suivre sa progression en consultant le résultat de la commande suivante :
kubectl describe certificate codeserver-prod -n code-server

Une fois terminé, la fin de la sortie ressemblera à ceci :


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

Vous pouvez maintenant actualiser votre domaine dans votre navigateur. Vous verrez le cadenas à gauche de la barre d'adresse de votre navigateur signifiant que la connexion est sécurisée.
Dans cette étape, vous avez configuré Ingress pour sécuriser le déploiement de votre serveur de code. Maintenant, vous pouvez revoir l'interface utilisateur du serveur de code.

## Étape 3 - Explorer l'interface du serveur de code

Dans cette section, vous allez explorer certaines des fonctionnalités de l'interface du serveur de code. Étant donné que code-server est Visual Studio Code exécuté dans le cloud, il a la même interface que l'édition de bureau autonome.

Sur le côté gauche de l'IDE, il y a une rangée verticale de six boutons ouvrant les fonctionnalités les plus couramment utilisées dans un panneau latéral appelé barre d'activité.

Cette barre est personnalisable, vous pouvez donc déplacer ces vues vers un ordre différent ou les supprimer de la barre. Par défaut, la première vue ouvre le panneau Explorateur qui fournit une navigation arborescente de la structure du projet. Vous pouvez gérer vos dossiers et fichiers ici, en les créant, en les supprimant, en les déplaçant et en les renommant si nécessaire. La vue suivante donne accès à une fonctionnalité de recherche et de remplacement.

Ensuite, dans l'ordre par défaut, se trouve votre vue des systèmes de contrôle de code source, comme Git. Le code Visual Studio prend également en charge d'autres fournisseurs de contrôle de source et vous pouvez trouver des instructions supplémentaires pour les workflows de contrôle de source avec l'éditeur dans cette documentation.

L'option de débogage de la barre d'activité fournit toutes les actions courantes de débogage dans le panneau. Visual Studio Code est livré avec une prise en charge intégrée du débogueur d'exécution Node.js et de tout langage qui se transpile en Javascript. Pour les autres langages, vous pouvez installer des extensions pour le débogueur requis. Vous pouvez enregistrer les configurations de débogage dans le fichier launch.json.

La vue finale dans la barre d'activité fournit un menu pour accéder aux extensions disponibles sur la place de marché.

La partie centrale de l'interface graphique est votre éditeur, que vous pouvez séparer par des onglets pour l'édition de votre code. Vous pouvez changer votre vue d'édition en un système de grille ou en fichiers côte à côte.

Après avoir créé un nouveau fichier via le menu Fichier, un fichier vide s'ouvrira dans un nouvel onglet, et une fois enregistré, le nom du fichier sera visible dans le panneau latéral de l'Explorateur. La création de dossiers peut être effectuée en cliquant avec le bouton droit de la souris sur la barre latérale de l'explorateur et en appuyant sur Nouveau dossier. Vous pouvez développer un dossier en cliquant sur son nom ainsi qu'en faisant glisser et déposer des fichiers et des dossiers vers les parties supérieures de la hiérarchie pour les déplacer vers un nouvel emplacement.

Vous pouvez accéder à un terminal en appuyant sur CTRL+SHIFT+\, ou en appuyant sur Terminal dans le menu supérieur, et en sélectionnant Nouveau terminal. Le terminal s'ouvrira dans un panneau inférieur et son répertoire de travail sera défini sur l'espace de travail du projet, qui contient les fichiers et dossiers affichés dans le panneau latéral de l'explorateur.
Vous avez exploré un aperçu de haut niveau de l'interface [[2022-01-02-how-does-code-server-works|code-server]] et passé en revue certaines des fonctionnalités les plus couramment utilisées.

# Conclusion

Vous avez maintenant code-server, un IDE cloud polyvalent, installé sur votre cluster DigitalOcean Kubernetes. Vous pouvez travailler sur votre code source et vos documents avec celui-ci individuellement ou collaborer avec votre équipe. L'exécution d'un IDE cloud sur votre cluster offre plus de puissance pour les tests, le téléchargement et un calcul plus approfondi ou rigoureux. Pour plus d'informations, consultez la documentation de Visual Studio Code sur les fonctionnalités supplémentaires et les instructions détaillées sur les autres composants de code-server.

[[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|Lire en Anglais]]