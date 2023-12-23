---
author: full
categories:
- security
date: 2022-10-26
description: Une faille dans Log4j, une bibliothèque Java développée par l'Apache
  Software Foundation open source pour la journalisation des messages d'erreur dans
  les applications, est la vulnérabilité de sécurité la plus médiatisée sur Internet
  à l'heure actuelle et est associée à un score de gravité de 10 sur 10.
image: https://res.cloudinary.com/brightsoftwares/image/upload/v1639575508/photo-1639140651961-41392a332bfc_njfgu8.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2022-10-26
pretified: true
ref: log4jflow<zeroday_impacted_and_protection
title: 'Faille Log4j : Suis-je impacté et comment puis-je me protéger'
---

Une faille dans Log4j, une bibliothèque Java développée par l'Apache Software Foundation open source pour la journalisation des messages d'erreur dans les applications, est la vulnérabilité de sécurité la plus médiatisée sur Internet à l'heure actuelle et est associée à un score de gravité de 10 sur 10.


La bibliothèque est développée par Apache Software Foundation open-source et est un framework de journalisation Java clé. Le [CERT Nouvelle-Zélande a déclenché une alerte la semaine dernière](https://www.zdnet.com/article/security-warning-new-zero-day-in-the-log4j-java-library-is-already-being- exploité/) que [CVE-2021-44228](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-44228), une faille d'exécution de code à distance dans Log4j, était déjà exploités par des attaquants. Plusieurs agences nationales de cybersécurité ont également lancé l'alerte, notamment la Cybersecurity and Infrastructure Security Agency (CISA) et le National Cyber ​​Security Center (NCSC) du Royaume-Uni.

En savoir plus sur [le fournisseur d'infrastructure Internet Cloudflare a déclaré que les exploits Log4j ont commencé le 1er décembre](https://www.zdnet.com/article/log4j-rce-activity-began-on-december-1-as-botnets-start-using -vulnérabilité/).

# Quels appareils et applications sont à risque ?

![Mes appareils sont-ils impactés par la faille Log4j](https://res.cloudinary.com/brightsoftwares/image/upload/v1639579714/log4j_detection_nkqvl4.png)

Voici les critères :

1. Votre appareil doit être exposé à Internet.
2. Votre appareil doit exécuter Apache Log4j
3. La version d'Apache Log4j doit être comprise entre 2.0 et 2.14.1

Si vous avez des **appareils IOT** connectés à Internet, avec les conditions ci-dessus, vous êtes à risque. Mirai, un botnet qui cible toutes sortes d'appareils connectés à Internet (IoT), pourrait probablement essayer de localiser votre appareil.

# Où Log4j est-il le plus utilisé ?

NCSC [notes](https://www.ncsc.gov.uk/news/apache-log4j-vulnerability) que Log4j version 2 (Log4j2), la version concernée, est incluse dans :

* Cadre Apache Struts2
* Cadre Solr
* Cadre druidique
* Cadre Flink
* Cadre rapide.

Pour les produits IBM, il existe Websphere 8.5 et 9.0.

# Réponse des gros joueurs

##AWS

AWS [travaille sur la correction de ses services](https://aws.amazon.com/security/security-bulletins/AWS-2021-005/) qui utilisent Log4j et a publié des mesures d'atténuation pour des services comme CloudFront. Il a également détaillé l'impact de la faille sur ses services.


AWS a mis à jour son **ensemble de règles WAF** – AWSManagedRulesKnownBadInputsRuleSet AMR – pour détecter et atténuer les tentatives d'attaque et l'analyse Log4j. Il dispose également d'options d'atténuation qui peuvent être activées pour **CloudFront**, **Application Load Balancer (ALB)**, **API Gateway** et **AppSync**. Il met également actuellement à jour tous ** Amazon OpenSearch Service ** vers la version corrigée de Log4j.


##IBM

Idem pour IBM [partagé](https://www.ibm.com/blogs/psirt/an-update-on-the-apache-log4j-cve-2021-44228-vulnerability/) que c'est ****" répondant activement "**** à la vulnérabilité Log4j dans l'infrastructure d'IBM et ses produits. IBM a confirmé **Websphere [8.5 et 9.0 sont vulnérables](https://www.ibm.com/support/pages/node/6525706/)**.

Oracle a [également publié un correctif pour la faille](https://www.oracle.com/security-alerts/alert-cve-2021-44228.html).

> "En raison de la gravité de cette vulnérabilité et de la publication de code d'exploitation sur divers sites, Oracle recommande fortement aux clients d'appliquer les mises à jour fournies par cette alerte de sécurité dès que possible", a-t-il déclaré.

# Autres joueurs


Les fournisseurs de produits populaires connus pour être encore vulnérables comprennent

- Atlassien,
- Amazone,
-Microsoft Azure,
- Cisco,
- Commvault,
-ESRI,
- Exact,
-Fortinet,
- JetBrains,
- Nelson,
-Nutanix,
- OpenMRS,
-Oracle,
- Chapeau rouge,
- Splunk,
-Doux, et
- VMware.

La liste est encore plus longue lors de l'ajout de produits pour lesquels un correctif a été publié.


# Ce que vous devez faire : Découvrez vos appareils et corrigez-les

![Étapes vers la solution](https://res.cloudinary.com/brightsoftwares/image/upload/v1639579711/log4j_solution_zbuf59.png)


Une partie du défi consistera à **identifier les logiciels hébergeant la vulnérabilité Log4j**.

Le Nationaal Cyber ​​Security Centrum (NCSC) des Pays-Bas a publié une [liste complète et sourcée de A à Z sur GitHub] (https://github.com/NCSC-NL/log4shell/tree/main/software) de tous les produits concernés dont il sait qu'ils sont vulnérables, non vulnérables, font l'objet d'une enquête ou lorsqu'un correctif est disponible.

La liste des produits illustre l'étendue de la vulnérabilité, couvrant les services cloud, les services de développement, les dispositifs de sécurité, les services de cartographie, etc.


Le principal conseil de CISA est d'identifier les appareils connectés à Internet exécutant Log4j et de les mettre à niveau vers la version 2.15.0, ou d'appliquer "immédiatement" les mesures d'atténuation fournies par les fournisseurs. Mais il recommande également de configurer des alertes pour les sondes ou les attaques sur les appareils exécutant Log4j.

> "Pour être clair, cette vulnérabilité présente un risque grave", [a déclaré dimanche la directrice de la CISA, Jen Easterly](https://www.cisa.gov/news/2021/12/11/statement-cisa-director-easterly-log4j -vulnérabilité).
> "Nous ne minimiserons les impacts potentiels que grâce à des efforts de collaboration entre le gouvernement et le secteur privé.
> Nous exhortons toutes les organisations à se joindre à nous dans cet effort essentiel et à agir."

Les étapes supplémentaires recommandées par CISA incluent : **énumérer tous les périphériques externes avec Log4j installé** ; assurer les **actions du centre des opérations de sécurité** à chaque alerte avec Log4j installé ; et **l'installation d'un pare-feu d'application Web (WAF)** avec des règles pour se concentrer sur Log4j.


# Que se passe-t-il si je ne peux pas patcher ou mettre à jour ?

Il est recommandé de mettre à niveau vers la version 2.15.0 de Log4j. Il peut y avoir des situations où la mise à niveau n'est pas immédiatement possible.

## Mettre à jour la configuration de Log4j

NCSC [recommande](https://www.ncsc.gov.uk/news/apache-log4j-vulnerability) la mise à jour vers la version 2.15.0 ou ultérieure, et - lorsque cela n'est pas possible - l'atténuation de la faille dans Log4j 2.10 et versions ultérieures en définissant propriété système **```"log4j2.formatMsgNoLookups"``` à ```"true"```** ou en supprimant la classe **```JndiLookup```** du classpath.
 

## Configurer des règles réseau pour détecter les tentatives d'exploitation

NCCGroup a publié [plusieurs règles de détection de réseau](https://research.nccgroup.com/2021/12/12/log4shell-reconnaissance-and-post-exploitation-network-detection/) pour détecter les tentatives d'exploitation et les indicateurs de réussite exploitation.

# Mon système est-il compromis ?

Enfin, Microsoft a publié son ensemble d'indicateurs de compromission et [conseils pour prévenir les attaques contre la vulnérabilité Log4j](https://www.microsoft.com/security/blog/2021/12/11/guidance-for-preventing-detecting- et-chasse-pour-cve-2021-44228-log4j-2-exploitation/). Les exemples de post-exploitation de la faille que Microsoft a constatés incluent l'installation de **mineurs de pièces**, **Cobalt Strike** pour permettre le vol d'informations d'identification et les mouvements latéraux, et l'exfiltration de données à partir de systèmes compromis.

Qu'est-ce que Log4j ?
--------------

Log4J est une bibliothèque Java largement utilisée pour consigner les messages d'erreur dans les applications. Il est utilisé dans les applications logicielles d'entreprise, y compris les applications personnalisées développées en interne par les entreprises, et fait partie de nombreux services de cloud computing.

Où Log4j est-il utilisé ?
--------------------

La bibliothèque Log4j 2 est utilisée dans les logiciels Java d'entreprise et, selon le NCSC du Royaume-Uni, est incluse dans les frameworks Apache tels que Apache Struts2, Apache Solr, Apache Druid, Apache Flink et Apache Swift.

Quelles applications sont concernées par la faille Log4j ?
--------------------------------------------------

Parce que Log4j est si largement utilisé, la vulnérabilité peut affecter une très large gamme de logiciels et de services de nombreux grands fournisseurs. Selon le NCSC, une application est vulnérable "si elle consomme une entrée utilisateur non fiable et la transmet à une version vulnérable de la bibliothèque de journalisation Log4j".

Dans quelle mesure la faille Log4j est-elle exploitée ?
---------------------------------------------

Les experts en sécurité ont averti qu'il y a des centaines de milliers de tentatives de pirates informatiques pour trouver des appareils vulnérables ; plus de 40 % des réseaux d'entreprise ont été ciblés selon une société de sécurité.

# Conclusion

L'objectif principal que vous devez avoir est d'abord l'évaluation de vos appareils.
Divisez votre équipe en 3 groupes :

1. **Groupe d'évaluation** : listera tous les appareils de votre infrastructure et vérifiera s'ils sont impactés. S'ils trouvent des appareils corrompus, mettez-les hors ligne. Pour les autres, dirigez-les vers les deux équipes restantes.
2. **Groupe de mise à niveau** : Ils effectuent la mise à niveau des appareils.
3. **Groupe de reconfiguration** : ils traitent les appareils qui ne peuvent pas être mis à niveau immédiatement.