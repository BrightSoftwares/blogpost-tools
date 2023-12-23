---
ToReview: true
author: full
categories:
- docker
date: 2022-12-29
description: "Par défaut, Jenkins est livré avec son propre serveur Web Winstone intégré écoutant sur le port `8080`, ce qui est pratique pour démarrer. C'est aussi une bonne idée, cependant, de sécuriser Jenkins avec SSL pour protéger les mots de passe et les données sensibles transmises via l'interface Web. Dans ce didacticiel, vous allez configurer Nginx en tant que proxy inverse pour diriger les demandes des clients vers Jenkins."
image: https://sergio.afanou.com/assets/images/image-midres-32.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: configure_jenkins_202007051235
title: "Comment configurer Jenkins avec SSL à l'aide d'un proxy inverse Nginx sur Ubuntu 20.04"
seo:
  links: [ "https://www.wikidata.org/wiki/Q381", "https://www.wikidata.org/wiki/Q7491312" ]
---

Par défaut, [Jenkins](https://jenkins.io/) est livré avec son propre serveur Web Winstone intégré écoutant sur le port `8080`, ce qui est pratique pour démarrer. C'est aussi une bonne idée, cependant, de sécuriser Jenkins avec SSL pour protéger les mots de passe et les données sensibles transmises via l'interface Web.

Dans ce didacticiel, vous allez configurer Nginx en tant que proxy inverse pour diriger les demandes des clients vers Jenkins.


## Conditions préalables


Pour commencer, vous aurez besoin des éléments suivants :

* Un serveur Ubuntu 20.04 configuré avec un utilisateur et un pare-feu sudo non root, conformément au [guide de configuration initiale du serveur Ubuntu 20.04] (https://www.digitalocean.com/community/tutorials/initial-server-setup-with -ubuntu-20-04).
* Jenkins installé, en suivant les étapes de [Comment installer Jenkins sur Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-jenkins-on-ubuntu-20-04)
* Nginx installé, en suivant les étapes de [Comment installer Nginx sur Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04)
* Un certificat SSL pour un domaine fourni par [Let's Encrypt](https://letsencrypt.org/). Suivez [[2020-07-05-how-to-create-a-selfsigned-ssl-certificate-for-apache-on-centos-8|How to create a self-signed certificate]] pour obtenir ce certificat. Notez que vous aurez besoin d'un [nom de domaine enregistré](https://www.digitalocean.com/docs/networking/dns/) que vous possédez ou contrôlez. Ce didacticiel utilisera le nom de domaine **example.com** tout au long.


## Étape 1 - Configuration de Nginx


Dans le tutoriel prérequis [Comment sécuriser Nginx avec Let's Encrypt sur Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu -20-04), vous avez configuré Nginx pour utiliser SSL dans le fichier `/etc/nginx/sites-available/example.com`. Ouvrez ce fichier pour ajouter vos paramètres de proxy inverse :

```
    sudo nano /etc/nginx/sites-available/example.com
    
```

Dans le bloc `server` avec les paramètres de configuration SSL, ajoutez les journaux d'accès et d'erreurs spécifiques à Jenkins :

/etc/nginx/sites-available/example.com

```
    . . .
    serveur {
            . . .
            #Configuration SSL
            #
            écouter [::]:443 ssl ipv6only=on ; # géré par Certbot
            écouter 443 ssl; # géré par Certbot
            access_log /var/log/nginx/jenkins.access.log ;
            error_log /var/log/nginx/jenkins.error.log;
            . . .
            }
    
```

Ensuite, configurons les paramètres du proxy. Puisque nous envoyons toutes les requêtes à Jenkins, nous allons commenter la ligne par défaut `try_files`, qui renverrait sinon une erreur 404 avant que la requête n'atteigne Jenkins :

/etc/nginx/sites-available/example.com

```
    . . .
               emplacement / {
                    # Première tentative de servir la requête en tant que fichier, puis
                    # comme répertoire, puis revient à l'affichage d'un 404.
                    # try_files $uri $uri/ =404; }
    . . .
    
```

Ajoutons maintenant les paramètres de proxy, qui incluent :

* `proxy_params` : le fichier `/etc/nginx/proxy_params` est fourni par Nginx et garantit que les informations importantes, y compris le nom d'hôte, le protocole de la demande du client et l'adresse IP du client, sont conservées et disponibles dans les fichiers journaux .
* `proxy_pass` : Ceci définit le protocole et l'adresse du serveur mandaté, qui dans ce cas sera le serveur Jenkins accessible via `localhost` sur le port `8080`.
* `proxy_read_timeout` : cela permet une augmentation de la valeur par défaut de 60 secondes de Nginx à la valeur de 90 secondes recommandée par Jenkins.
* `proxy_redirect` : cela garantit que [les réponses sont correctement réécrites](https://wiki.jenkins-ci.org/display/JENKINS/Jenkins+says+my+reverse+proxy+setup+is+broken) pour inclure le nom d'hôte approprié.

Assurez-vous de remplacer votre nom de domaine sécurisé par SSL par `example.com` dans la ligne `proxy_redirect` ci-dessous :

/etc/nginx/sites-available/example.com

```
    Emplacement /
    . . .
               emplacement / {
                    # Première tentative de servir la requête en tant que fichier, puis
                    # comme répertoire, puis revient à l'affichage d'un 404.
                    # try_files $uri $uri/ =404;
                    inclure /etc/nginx/proxy_params ;
                    proxy_pass http://localhost:8080;
                    proxy_read_timeout 90s ;
                    # Corrigez l'erreur potentielle "Il semble que votre configuration de proxy inverse est cassée".
                    proxy_redirect http://localhost:8080 https://example.com ;
    
```

Une fois ces modifications effectuées, enregistrez le fichier et quittez l'éditeur. Nous attendrons le redémarrage de Nginx jusqu'à ce que nous ayons configuré Jenkins, mais nous pouvons tester notre configuration maintenant :

```
    sudo nginx-t
    
```

Si tout va bien, la commande retournera :

```
    Outputnginx : la syntaxe du fichier de configuration /etc/nginx/nginx.conf est correcte
    nginx : le test du fichier de configuration /etc/nginx/nginx.conf est réussi
    
```

Si ce n'est pas le cas, corrigez les erreurs signalées jusqu'à ce que le test réussisse.

**Note:**
Si vous configurez mal le `proxy_pass` (en ajoutant une barre oblique à la fin, par exemple), vous obtiendrez quelque chose de similaire à ce qui suit dans votre page Jenkins **Configuration**.

![Erreur Jenkins : la configuration du proxy inverse est interrompue](https://assets.digitalocean.com/articles/nginx_jenkins/1.jpg)

Si vous voyez cette erreur, revérifiez vos paramètres `proxy_pass` et `proxy_redirect` dans la configuration Nginx.


## Étape 2 - Configuration de Jenkins

Pour que Jenkins fonctionne avec Nginx, vous devrez mettre à jour la configuration de Jenkins afin que le serveur Jenkins n'écoute que sur l'interface `localhost` plutôt que sur toutes les interfaces (`0.0.0.0`). Si Jenkins écoute sur toutes les interfaces, il est potentiellement accessible sur son port d'origine non chiffré (`8080`).

Modifions le fichier de configuration `/etc/default/jenkins` pour effectuer ces ajustements :

```
    sudo nano /etc/default/jenkins
    
```

Localisez la ligne `JENKINS_ARGS` et ajoutez `--httpListenAddress=127.0.0.1` aux arguments existants :

/etc/default/jenkins

```
    . . .
    JENKINS_ARGS="--webroot=/var/cache/$NAME/war --httpPort=$HTTP_PORT --httpListenAddress=127.0.0.1"
    
```

Enregistrez et quittez le fichier.

Pour utiliser les nouveaux paramètres de configuration, redémarrez Jenkins :

```
    sudo systemctl redémarrer jenkins
```

Étant donné que `systemctl` n'affiche pas de sortie, vérifiez l'état :

```
    statut sudo systemctl jenkins
    
```

Vous devriez voir le statut `active (exited)` dans la ligne `Active` :

```
    Sortie● jenkins.service - LSB : démarrer Jenkins au démarrage
       Chargé : chargé (/etc/init.d/jenkins ; généré)
       Actif : actif (sorti) depuis le lundi 2018-07-09 20:26:25 UTC ; il y a 11 s
         Documents : man:systemd-sysv-generator(8)
      Processus : 29766 ExecStop=/etc/init.d/jenkins stop (code=exited, status=0/SUCCESS)
      Processus : 29812 ExecStart=/etc/init.d/jenkins start (code=exited, status=0/SUCCESS)
    
```

Redémarrez Nginx :

    sudo systemctl redémarrer nginx
    

Vérifiez l'état :

```
    statut sudo systemctl nginx
```


```
    Sortie● nginx.service - Un serveur Web hautes performances et un serveur proxy inverse
       Chargé : chargé (/lib/systemd/system/nginx.service ; activé ; préréglage du fournisseur : activé)
       Actif : actif (en cours d'exécution) depuis le lundi 2018-07-09 20:27:23 UTC ; il y a 31 s
         Documents : man:nginx(8)
      Processus : 29951 ExecStop=/sbin/start-stop-daemon --quiet --stop --retry QUIT/5 --pidfile /run/nginx.pid (code=exited, status=0/SUCCESS)
      Processus : 29963 ExecStart=/usr/sbin/nginx -g démon activé ; master_process activé ; (code=sorti, statut=0/SUCCESS)
      Processus : 29952 ExecStartPre=/usr/sbin/nginx -t -q -g démon activé ; master_process activé ; (code=sorti, statut=0/SUCCESS)
     PID principal : 29967 (nginx)
    
```


Avec les deux serveurs redémarrés, vous devriez pouvoir visiter le domaine en utilisant HTTP ou HTTPS. Les requêtes HTTP seront automatiquement redirigées vers HTTPS et le site Jenkins sera servi en toute sécurité.


## Étape 3 - Test de la configuration

Maintenant que vous avez activé le chiffrement, vous pouvez tester la configuration en réinitialisant le mot de passe administrateur. Commençons par visiter le site via HTTP pour vérifier que vous pouvez joindre Jenkins et que vous êtes redirigé vers HTTPS.

Dans votre navigateur Web, saisissez `http://example.com`, en remplaçant votre domaine par `example.com`. Après avoir appuyé sur `ENTER`, l'URL doit commencer par `https` et la barre d'adresse doit indiquer que la connexion est sécurisée.

Vous pouvez entrer le nom d'utilisateur administratif que vous avez créé dans [Comment installer Jenkins sur Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-jenkins-on-ubuntu-20-04) dans le champ **Utilisateur** et le mot de passe que vous avez sélectionné dans le champ **Mot de passe**.

Une fois connecté, vous pouvez modifier le mot de passe pour vous assurer qu'il est sécurisé.

Cliquez sur votre nom d'utilisateur dans le coin supérieur droit de l'écran. Sur la page principale du profil, sélectionnez **Configurer** dans la liste sur le côté gauche de la page :

![Naviguer vers la page de mot de passe Jenkins](https://assets.digitalocean.com/articles/jenkins-nginx-ubuntu-1804/configure_password.png)

Cela vous amènera à une nouvelle page, où vous pourrez saisir et confirmer un nouveau mot de passe :

![Jenkins crée une page de mot de passe](https://assets.digitalocean.com/articles/jenkins-nginx-ubuntu-1804/password_page.png)

Confirmez le nouveau mot de passe en cliquant sur **Enregistrer**. Vous pouvez maintenant utiliser l'interface Web Jenkins en toute sécurité.

# Conclusion

Dans ce didacticiel, vous avez configuré Nginx en tant que proxy inverse du serveur Web intégré de Jenkins pour sécuriser vos informations d'identification et autres informations transmises via l'interface Web. Maintenant que Jenkins est sécurisé, vous pouvez apprendre [comment mettre en place un pipeline d'intégration continue](https://www.digitalocean.com/community/tutorials/how-to-set-up-continuous-integration-pipelines-in- jenkins-on-ubuntu-16-04) pour tester automatiquement les changements de code. D'autres ressources à considérer si vous débutez avec Jenkins sont [le tutoriel "Créer votre premier pipeline" du projet Jenkins](https://jenkins.io/doc/pipeline/tour/hello-world/) ou [la bibliothèque de la communauté- plugins contribués] (https://plugins.jenkins.io/).