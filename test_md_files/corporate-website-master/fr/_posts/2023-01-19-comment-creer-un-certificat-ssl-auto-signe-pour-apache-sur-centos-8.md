---
ToReview: true
author: full
categories:
- ubuntu
date: 2023-01-19
description: "Le protocole TLS et son prédécesseur SSL sont des protocoles utilisés pour envelopper le trafic normal dans un wrapper protégé et chiffré. Grâce à cette technologie, les serveurs peuvent envoyer en toute sécurité des informations à leurs clients sans que leurs messages soient interceptés ou lus par une partie extérieure. Dans ce guide, nous allons vous montrer comment créer et utiliser un certificat SSL auto-signé avec le serveur Web Apache sur une machine CentOS 8."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1656243521/pexels-antoni-shkraba-5475754_ffi8va.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: selfsigned_ssl_1237
title: Comment créer un certificat SSL auto-signé pour Apache sur CentOS 8
---

Le protocole **TLS**, ou "sécurité de la couche de transport" - et son prédécesseur **SSL** - sont des protocoles utilisés pour envelopper le trafic normal dans un wrapper protégé et chiffré. Grâce à cette technologie, les serveurs peuvent envoyer en toute sécurité des informations à leurs clients sans que leurs messages soient interceptés ou lus par une partie extérieure.

Dans ce guide, nous allons vous montrer comment créer et utiliser un certificat SSL auto-signé avec le serveur Web Apache sur une machine CentOS 8.

**Remarque :** Un certificat auto-signé cryptera la communication entre votre serveur et ses clients. Cependant, comme il n'est signé par aucune des autorités de certification approuvées incluses avec les navigateurs Web et les systèmes d'exploitation, les utilisateurs ne peuvent pas utiliser le certificat pour valider automatiquement l'identité de votre serveur. Par conséquent, vos utilisateurs verront une erreur de sécurité lorsqu'ils visiteront votre site.

En raison de cette limitation, les certificats auto-signés ne sont pas appropriés pour un environnement de production au service du public. Ils sont généralement utilisés pour tester ou pour sécuriser des services non critiques utilisés par un seul utilisateur ou un petit groupe d'utilisateurs qui peuvent établir la confiance dans la validité du certificat via des canaux de communication alternatifs.

Pour une solution de certificat plus prête pour la production, consultez [Let's Encrypt](https://letsencrypt.org/), une autorité de certification gratuite. Vous pouvez apprendre à télécharger et à configurer un certificat Let's Encrypt dans notre [Comment sécuriser Apache avec Let's Encrypt sur CentOS 8](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with -let-s-encrypt-on-centos-8) tutoriel.

## Conditions préalables


Avant de commencer ce didacticiel, vous aurez besoin des éléments suivants :

* Accès à un serveur CentOS 8 avec un utilisateur non ** root **, sudo activé. Notre guide [Configuration initiale du serveur avec CentOS 8](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-centos-8) peut vous montrer comment créer ce compte.
* Vous aurez également besoin d'avoir installé Apache. Vous pouvez installer Apache en utilisant `dnf` :

```
sudo dnf install httpd
```
        

Activez Apache et démarrez-le en utilisant `systemctl` :
    
```
sudo systemctl enable httpd
sudo systemctl start httpd
```


Et enfin, si vous avez configuré un pare-feu `firewalld`, ouvrez les ports `http` et `https` :

```
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```
        
    

Une fois ces étapes terminées, assurez-vous que vous êtes connecté en tant qu'utilisateur non ** root ** et continuez avec le didacticiel.

## Étape 1 - Installation de `mod_ssl`


Nous devons d'abord installer `mod_ssl`, un module Apache qui prend en charge le cryptage SSL.

Installez `mod_ssl` avec la commande `dnf` :

```
sudo dnf install mod_ssl
```
    

En raison d'un bogue d'empaquetage, nous devons redémarrer Apache une fois pour générer correctement le certificat et la clé SSL par défaut, sinon nous obtiendrons une erreur indiquant que `'/etc/pki/tls/certs/localhost.crt' n'existe pas ou est vide'.

```
sudo systemctl restart httpd
```
    

Le module `mod_ssl` est maintenant activé et prêt à être utilisé.


## Étape 2 - Création du certificat SSL


Maintenant qu'Apache est prêt à utiliser le chiffrement, nous pouvons passer à la génération d'un nouveau certificat SSL. Le certificat stockera certaines informations de base sur votre site et sera accompagné d'un fichier clé qui permet au serveur de gérer en toute sécurité les données cryptées.

Nous pouvons créer la clé SSL et les fichiers de certificat avec la commande `openssl` :

```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/pki/tls/private/apache-selfsigned.key -out /etc/pki/tls/certs/apache-selfsigned.crt
```


Après avoir entré la commande, vous serez redirigé vers une invite où vous pourrez entrer des informations sur votre site Web. Avant d'aborder cela, examinons ce qui se passe dans la commande que nous lançons :

* `openssl` : il s'agit de l'outil de ligne de commande permettant de créer et de gérer des certificats, des clés et d'autres fichiers OpenSSL.
* `req -x509` : Ceci spécifie que nous voulons utiliser la gestion des demandes de signature de certificat (CSR) X.509. X.509 est une norme d'infrastructure à clé publique à laquelle SSL et TLS adhèrent pour la gestion des clés et des certificats.
* `-nodes` : cela indique à OpenSSL de ne pas sélectionner l'option de sécurisation de notre certificat avec une phrase de passe. Nous avons besoin d'Apache pour pouvoir lire le fichier, sans intervention de l'utilisateur, au démarrage du serveur. Une phrase de passe empêcherait que cela se produise, car nous devions la saisir après chaque redémarrage.
* `-days 365` : cette option définit la durée pendant laquelle le certificat sera considéré comme valide. Nous l'avons fixé pour un an ici. De nombreux navigateurs modernes rejetteront tous les certificats valides pendant plus d'un an.
* `-newkey rsa:2048` : Ceci spécifie que nous voulons générer un nouveau certificat et une nouvelle clé en même temps. Nous n'avons pas créé la clé requise pour signer le certificat lors d'une étape précédente, nous devons donc la créer avec le certificat. La partie `rsa:2048` lui dit de créer une clé RSA d'une longueur de 2048 bits.
* `-keyout` : cette ligne indique à OpenSSL où placer le fichier de clé privée généré que nous créons.
* `-out` : cela indique à OpenSSL où placer le certificat que nous créons.

Remplissez les invites de manière appropriée. La ligne la plus importante est celle qui demande le `Common Name`. Vous devez entrer soit le nom d'hôte que vous utiliserez pour accéder au serveur, soit l'adresse IP publique du serveur. Il est important que ce champ corresponde à ce que vous mettrez dans la barre d'adresse de votre navigateur pour accéder au site, car une incompatibilité entraînera davantage d'erreurs de sécurité.

La liste complète des invites ressemblera à ceci :

```
Country Name (2 letter code) [XX]:US
State or Province Name (full name) []:Example
Locality Name (eg, city) [Default City]:Example 
Organization Name (eg, company) [Default Company Ltd]:Example Inc
Organizational Unit Name (eg, section) []:Example Dept
Common Name (eg, your name or your server's hostname) []:your_domain_or_ip
Email Address []:webmaster@example.com
```

    

Les deux fichiers que vous avez créés seront placés dans les sous-répertoires appropriés du répertoire `/etc/pki/tls`. Il s'agit d'un répertoire standard fourni par CentOS à cet effet.

Ensuite, nous mettrons à jour notre configuration Apache pour utiliser le nouveau certificat et la nouvelle clé.


## Étape 3 - Configuration d'Apache pour utiliser SSL

Maintenant que nous avons notre certificat auto-signé et notre clé disponibles, nous devons mettre à jour notre configuration Apache pour les utiliser. Sur CentOS, vous pouvez placer de nouveaux fichiers de configuration Apache (ils doivent se terminer par `.conf`) dans `/etc/httpd/conf.d` et ils seront chargés la prochaine fois que le processus Apache sera rechargé ou redémarré.

Pour ce tutoriel, nous allons créer un nouveau fichier de configuration minimal. Si vous avez déjà configuré un Apache `<Virtualhost>` et que vous avez juste besoin d'y ajouter SSL, vous devrez probablement copier les lignes de configuration commençant par `SSL` et changer le port `VirtualHost` de `80` à '443'. Nous nous occuperons du port '80' dans la prochaine étape.

Ouvrez un nouveau fichier dans le répertoire `/etc/httpd/conf.d` :

```
sudo vi /etc/httpd/conf.d/your_domain_or_ip.conf
```

    

Collez la configuration minimale suivante de VirtualHost :

/etc/httpd/conf.d/votre\_domaine\_ou\_ip.conf

```
<VirtualHost *:443>
        ServerName your_domain_or_ip
        DocumentRoot /var/www/ssl-test
        SSLEngine on
        SSLCertificateFile /etc/pki/tls/certs/apache-selfsigned.crt
        SSLCertificateKeyFile /etc/pki/tls/private/apache-selfsigned.key
</VirtualHost>
```
    

Assurez-vous de mettre à jour la ligne `ServerName` selon la façon dont vous avez l'intention d'adresser votre serveur. Il peut s'agir d'un nom d'hôte, d'un nom de domaine complet ou d'une adresse IP. Assurez-vous que tout ce que vous choisissez correspond au "nom commun" que vous avez choisi lors de la création du certificat.

Les lignes restantes spécifient un répertoire `DocumentRoot` à partir duquel servir les fichiers, et les options SSL nécessaires pour pointer Apache vers notre certificat et notre clé nouvellement créés.

Créons maintenant notre `DocumentRoot` et insérons-y un fichier HTML uniquement à des fins de test :

```
sudo mkdir /var/www/ssl-test
```

    

Ouvrez un nouveau fichier "index.html" avec votre éditeur de texte :

```
sudo vi /var/www/ssl-test/index.html
```

    

Collez ce qui suit dans le fichier vierge :

/var/www/ssl-test/index.html

```
<h1>it worked!</h1>
```
    

Ce n'est pas un fichier HTML complet, bien sûr, mais les navigateurs sont indulgents et il suffira de vérifier notre configuration.

Enregistrez et fermez le fichier, puis vérifiez votre configuration Apache pour les erreurs de syntaxe en tapant :

```
sudo apachectl configtest
```
    

Vous pouvez voir des avertissements, mais tant que la sortie se termine par "Syntaxe OK", vous pouvez continuer en toute sécurité. Si cela ne fait pas partie de votre sortie, vérifiez la syntaxe de vos fichiers et réessayez.

Lorsque tout va bien, rechargez Apache pour récupérer les modifications de configuration :

```
sudo systemctl reload httpd
```

    

Chargez maintenant votre site dans un navigateur, en vous assurant d'utiliser `https://` au début.

Vous devriez voir une erreur. C'est normal pour un certificat auto-signé ! Le navigateur vous avertit qu'il ne peut pas vérifier l'identité du serveur, car notre certificat n'est signé par aucune des autorités de certification connues du navigateur. À des fins de test et pour un usage personnel, cela peut convenir. Vous devriez pouvoir cliquer sur **avancé** ou **plus d'informations** et choisir de continuer.

Après cela, votre navigateur chargera le message "Ça a marché!".

**Remarque :** si votre navigateur ne se connecte pas du tout au serveur, assurez-vous que votre connexion n'est pas bloquée par un pare-feu. Si vous utilisez `firewalld`, les commandes suivantes ouvriront les ports `80` et `443` :

```
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload 
```


Ensuite, nous ajouterons une autre section "VirtualHost" à notre configuration pour servir les requêtes HTTP simples et les rediriger vers HTTPS.

## Étape 4 - Redirection HTTP vers HTTPS

Actuellement, notre configuration ne répondra qu'aux requêtes HTTPS sur le port `443`. Il est recommandé de répondre également sur le port "80", même si vous souhaitez forcer le chiffrement de tout le trafic. Configurons un `VirtualHost` pour répondre à ces requêtes non chiffrées et les rediriger vers HTTPS.

Ouvrez le même fichier de configuration Apache que celui que nous avons lancé aux étapes précédentes :

```
sudo vi /etc/httpd/conf.d/your_domain_or_ip.conf
```
    

En bas, créez un autre bloc "VirtualHost" pour faire correspondre les requêtes sur le port "80". Utilisez la directive `ServerName` pour faire à nouveau correspondre votre nom de domaine ou votre adresse IP. Ensuite, utilisez `Redirect` pour faire correspondre toutes les demandes et les envoyer au SSL `VirtualHost`. Assurez-vous d'inclure la barre oblique finale :

/etc/httpd/conf.d/votre\_domaine\_ou\_ip.conf

```
<VirtualHost *:80>
        ServerName your_domain_or_ip
        Redirect / https://your_domain_or_ip/
</VirtualHost>
```

    

Enregistrez et fermez ce fichier lorsque vous avez terminé, puis testez à nouveau votre syntaxe de configuration et rechargez Apache :

```
sudo apachectl configtest
sudo systemctl reload httpd
```
    

Vous pouvez tester la nouvelle fonctionnalité de redirection en visitant votre site avec "http://" devant l'adresse. Vous devriez être automatiquement redirigé vers `https://`.

# Conclusion

Vous avez maintenant configuré Apache pour traiter les requêtes chiffrées à l'aide d'un certificat SSL auto-signé et pour rediriger les requêtes HTTP non chiffrées vers HTTPS.

Si vous envisagez d'utiliser SSL pour un site Web public, vous devriez envisager d'acheter un nom de domaine et d'utiliser une autorité de certification largement prise en charge telle que [Let's Encrypt](https://letsencrypt.org/).

Pour plus d'informations sur l'utilisation de Let's Encrypt avec Apache, veuillez lire notre [Comment sécuriser Apache avec Let's Encrypt sur CentOS8] (https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-centos-8) tutoriel.